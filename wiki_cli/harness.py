"""The harness: decides what each mode sends to Gemma and checks what comes back.

  search  retrieval only — no model call (see cli.cmd_search)
  ask     standalone RAG: retrieve source passages -> research rules + passages ->
          Gemma -> citation check -> answer or "insufficient evidence"
  chat    persona + recent conversation; retrieves notes only when the message needs them

Every ask and chat turn is appended to evidence/runs.jsonl so results can be inspected
without rerunning the model.
"""
import datetime
import json
import re
from dataclasses import dataclass, field

from . import config, llm
from .ingest import load_catalog
from .retrieval import Hit, Retriever

ASK_PASSAGES = 8            # passages given to Gemma per question (~8 × 1200 chars max)
MIN_RELEVANCE = 0.30        # below this cosine, no passage is about the question at all
CHAT_NOTES_RELEVANCE = 0.45 # chat only uses passages that are clearly on topic
CHAT_HISTORY_MESSAGES = 10  # recent messages (5 turns) kept as conversation context

ASK_SCHEMA = {
    "type": "object",
    "properties": {"answer_found": {"type": "boolean"}, "answer": {"type": "string"},
                   "missing": {"type": "string"}},
    "required": ["answer_found", "answer", "missing"],
}
CITATION = re.compile(r"\[S(\d+)\]")


def load_instructions(name: str) -> str:
    return (config.PROMPTS / name).read_text(encoding="utf-8")


def format_passages(hits: list[Hit]) -> str:
    return "\n\n".join(
        f"[S{n}] {h.chunk.doc_title} — {h.chunk.location} (file: {h.chunk.path})\n{h.chunk.text}"
        for n, h in enumerate(hits, start=1))


def check_citations(text: str, n_passages: int) -> tuple[list[int], list[int]]:
    """Return (valid, invalid) citation numbers found in the text."""
    cited = sorted({int(n) for n in CITATION.findall(text)})
    return [n for n in cited if 1 <= n <= n_passages], [n for n in cited if not 1 <= n <= n_passages]


def log_run(record: dict) -> None:
    config.EVIDENCE.mkdir(exist_ok=True)
    with open(config.EVIDENCE / "runs.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- ask

@dataclass
class AskResult:
    question: str
    hits: list[Hit]
    status: str                 # "answered" | "insufficient_evidence"
    answer: str
    missing: str = ""
    cited: list[int] = field(default_factory=list)
    invalid_citations: list[int] = field(default_factory=list)
    harness_note: str = ""
    stats: dict = field(default_factory=dict)
    prompt_chars: int = 0


def ask(question: str, retriever: Retriever | None = None) -> AskResult:
    """Standalone factual answer. No chat history and no persona are ever included."""
    # Check the model first: otherwise a stopped runtime would look like "no evidence".
    llm.ensure_model(config.CHAT_MODEL)
    retriever = retriever or Retriever()
    hits = retriever.search(question, k=ASK_PASSAGES, kinds=("source",))
    best = max((h.cosine or 0 for h in hits), default=0)

    # Gate 1: nothing relevant was retrieved -> do not even ask the model.
    if not hits or (retriever.notice == "" and best < MIN_RELEVANCE):
        result = AskResult(question, hits, "insufficient_evidence",
                           "Insufficient evidence: no passage in the wiki is about this question.",
                           harness_note=f"retrieval gate: best cosine {best:.3f} < {MIN_RELEVANCE}")
        _log_ask(result)
        return result

    prompt = (f"Question: {question}\n\nSource passages:\n\n{format_passages(hits)}")
    messages = [{"role": "system", "content": load_instructions("wiki-instructions.md")},
                {"role": "user", "content": prompt}]
    reply, stats = llm.chat_json(messages, ASK_SCHEMA, temperature=0.1)
    answer, missing = reply["answer"].strip(), reply["missing"].strip()
    valid, invalid = check_citations(answer, len(hits))

    # Gate 2: an "answer" without a single valid citation is not grounded -> refuse.
    if reply["answer_found"] and not valid:
        result = AskResult(question, hits, "insufficient_evidence",
                           "Insufficient evidence: the model's answer cited no retrieved passage, "
                           "so it is not shown as a grounded answer.", missing=missing,
                           invalid_citations=invalid, stats=stats,
                           harness_note=f"citation gate: rejected uncited answer: {answer!r}")
    elif not reply["answer_found"]:
        result = AskResult(question, hits, "insufficient_evidence",
                           "Insufficient evidence in the wiki to answer this question.",
                           missing=missing or answer, cited=valid, stats=stats)
    else:
        result = AskResult(question, hits, "answered", answer, missing=missing, cited=valid,
                           invalid_citations=invalid, stats=stats)
    result.prompt_chars = sum(len(m["content"]) for m in messages)
    _log_ask(result)
    return result


def _log_ask(r: AskResult) -> None:
    log_run({
        "time": datetime.datetime.now().isoformat(timespec="seconds"), "mode": "ask",
        "execution": "local", "model": config.CHAT_MODEL, "embed_model": config.EMBED_MODEL,
        "question": r.question, "status": r.status, "answer": r.answer, "missing": r.missing,
        "cited": r.cited, "invalid_citations": r.invalid_citations, "harness_note": r.harness_note,
        "retrieved": [{"label": f"S{n}", "path": h.chunk.path, "location": h.chunk.location,
                       "cosine": h.cosine, "bm25": h.bm25} for n, h in enumerate(r.hits, 1)],
        "prompt_chars": r.prompt_chars, "stats": r.stats,
    })


# ---------------------------------------------------------------- chat

NOTE_PHRASES = ("my notes", "our notes", "the notes", "my wiki", "the wiki", "according to",
                "what did i", "what did we", "remind me", "did we learn", "interview findings")


class ChatSession:
    """Personal-assistant conversation. History is conversation context, not evidence:
    only passages retrieved for the current turn may be cited."""

    def __init__(self, retriever: Retriever | None = None):
        self.retriever = retriever
        self.history: list[dict] = []
        self.persona = load_instructions("persona.md")
        titles = load_catalog().get("pages", {})
        # Subjects that mean "this message is about the user's notes".
        self.topic_terms = sorted({t.lower() for t in titles} |
                                  {"general alpha", "genalpha", "dtcs", "digital twin", "数字孪生"})
        self.last_reply = ""

    def needs_notes(self, message: str) -> bool:
        text = message.lower()
        return any(term in text for term in self.topic_terms) or any(p in text for p in NOTE_PHRASES)

    def lookup(self, query: str) -> list[Hit]:
        self.retriever = self.retriever or Retriever()
        hits = self.retriever.search(query, k=4, kinds=("source",))
        return [h for h in hits if (h.cosine or 0) >= CHAT_NOTES_RELEVANCE]

    def reply(self, message: str, force_query: str | None = None) -> dict:
        wants_notes = force_query is not None or self.needs_notes(message)
        hits = self.lookup(force_query or message) if wants_notes else []

        system = self.persona
        if hits:
            system += ("\n\n## Notes retrieved for this message (cite as [S1], [S2]…)\n\n"
                       + format_passages(hits))
        elif wants_notes:
            system += ("\n\n## Notes lookup\nThe harness searched the user's notes for this "
                       "message and found nothing clearly relevant. Say so if the user asked "
                       "about their notes; do not invent facts.")
        messages = [{"role": "system", "content": system},
                    *self.history[-CHAT_HISTORY_MESSAGES:],
                    {"role": "user", "content": message}]
        text, stats = llm.chat(messages, temperature=0.6)
        valid, invalid = check_citations(text, len(hits))

        # History keeps plain text only; passages are re-retrieved per turn when needed.
        self.history += [{"role": "user", "content": message},
                         {"role": "assistant", "content": text}]
        self.last_reply = text
        turn = {"time": datetime.datetime.now().isoformat(timespec="seconds"), "mode": "chat",
                "execution": "local", "model": config.CHAT_MODEL, "message": message,
                "retrieval": "forced" if force_query else ("auto" if wants_notes else "skipped"),
                "passages": [{"label": f"S{n}", "path": h.chunk.path, "location": h.chunk.location,
                              "cosine": h.cosine} for n, h in enumerate(hits, 1)],
                "reply": text, "cited": valid, "invalid_citations": invalid,
                "history_messages_sent": len(messages) - 2, "stats": stats}
        log_run(turn)
        return {**turn, "hits": hits}

    def reset(self) -> None:
        self.history.clear()
        self.last_reply = ""
