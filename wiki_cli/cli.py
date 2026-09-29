"""`wiki` command-line interface: parses the command and hands it to the harness."""
import argparse
import datetime
import re
import sys
import textwrap
from pathlib import Path

from . import config, llm

DESCRIPTION = f"""\
Personal wiki CLI — local Gemma + retrieval over your own notes (works offline).

commands:
  ingest [PATH]   read sources in vault/raw/, write linked notes to vault/wiki/,
                  update vault/index.md and the search index in data/
  search QUERY    show matching ORIGINAL passages + locations (no model answer)
  ask QUESTION    standalone factual answer from retrieved passages, with citations,
                  or "insufficient evidence" (no chat history, no personality)
  chat            talk with Scout, your personal assistant (drafts, plans, ideas);
                  looks up notes only when a message needs them
  check           verify wiki links, source references, headings, duplicate names

examples:
  ./wiki ingest vault/raw
  ./wiki search "pilot projects"
  ./wiki ask "What kind of pilot projects would reduce customer adoption risk?"
  ./wiki chat

configuration (environment variables):
  WIKI_MODEL        chat model        (default: {config.CHAT_MODEL})
  WIKI_EMBED_MODEL  embedding model   (default: {config.EMBED_MODEL})
  WIKI_OLLAMA_URL   local runtime     (default: {config.OLLAMA_URL})

required inputs: sources in vault/raw/ (.docx .pptx .doc .md .txt .html);
the Ollama runtime running locally with both models pulled
(ollama pull {config.CHAT_MODEL} && ollama pull {config.EMBED_MODEL}).
"""


def require_local(mode: str) -> None:
    if mode != "local":
        raise ValueError("Only --mode local is implemented. Online mode is an optional "
                         "extension that this project does not include.")


# ---------------------------------------------------------------- ingest / check

def cmd_ingest(args) -> int:
    from .ingest import ingest
    print(f"[ingest | model: {config.CHAT_MODEL} | local]")
    report = ingest(Path(args.path), force=args.force)
    print(f"\nDone in {report['seconds_total']} s: {report['notes_written']} note(s) written, "
          f"{report['notes_kept_reviewed']} reviewed note(s) kept, "
          f"{report['passages_indexed']} passages indexed.")
    print(f"Open {config.VAULT} in Obsidian and start at index.md.")
    return 0


def cmd_check(args) -> int:
    from .ingest import check_vault
    problems = check_vault()
    for problem in problems:
        print("problem:", problem)
    print(f"[check] {len(problems)} problem(s) found in {config.VAULT}")
    return 1 if problems else 0


# ---------------------------------------------------------------- search

def format_hit(n: int, hit, label: str = "") -> str:
    c = hit.chunk
    cosine = "" if hit.cosine is None else f", cosine {hit.cosine}"
    head = f"[{label or n}] {c.path} — {c.location}\n    ({c.kind} passage, bm25 {hit.bm25}{cosine})"
    return head + "\n" + textwrap.indent(c.text, "    │ ")


def cmd_search(args) -> int:
    from .retrieval import Retriever
    retriever = Retriever()
    kinds = ("source", "wiki") if args.kind == "all" else (args.kind,)
    hits = retriever.search(args.query, k=args.k, kinds=kinds, use_embeddings=not args.keywords)
    method = "keywords only (BM25)" if args.keywords or retriever.notice else "hybrid: BM25 + embeddings"
    print(f"[search | {method} | no language model used]")
    if retriever.notice:
        print(f"note: {retriever.notice}")
    if not hits:
        print("No matching passages.")
    for n, hit in enumerate(hits, start=1):
        print("\n" + format_hit(n, hit))
    return 0


# ---------------------------------------------------------------- ask

def render_ask(result) -> str:
    lines = [f"[ask | model: {config.CHAT_MODEL} | local | standalone: no chat history, no persona]",
             f"Question: {result.question}", ""]
    if result.status == "answered":
        lines += ["Answer:", textwrap.fill(result.answer, 92), ""]
        if result.missing:
            lines += ["Not supported by the sources:", textwrap.fill(result.missing, 92), ""]
        lines.append("Citations (open these to check the claims):")
        for n in result.cited:
            c = result.hits[n - 1].chunk
            lines.append(f"  [S{n}] {c.path} — {c.location}")
    else:
        lines += [result.answer]
        if result.missing:
            lines += ["", "What is missing:", textwrap.fill(result.missing, 92)]
    if result.invalid_citations:
        lines.append(f"  warning: answer cited passages that were not retrieved: "
                     f"{', '.join(f'S{n}' for n in result.invalid_citations)}")
    if result.harness_note:
        lines.append(f"  harness: {result.harness_note}")
    uncited = [n for n in range(1, len(result.hits) + 1) if n not in result.cited]
    if uncited:
        lines += ["", "Retrieved but not cited:"]
        lines += [f"  [S{n}] {result.hits[n - 1].chunk.path} — {result.hits[n - 1].chunk.location}"
                  for n in uncited]
    if result.stats:
        lines += ["", f"({result.stats['seconds']} s, {result.stats['prompt_tokens']} prompt tokens, "
                      f"{result.stats['output_tokens']} output tokens, {result.prompt_chars} prompt chars)"]
    return "\n".join(lines)


def write_ask_card(result, path: Path, terminal_text: str) -> None:
    """Evidence card: question, identity, retrieved passages (full text), answer, citations."""
    lines = [
        f"# Ask-mode evidence card: {path.stem}", "",
        f"- **Question:** {result.question}",
        f"- **Mode:** ask (standalone) · **Execution:** local (offline-capable)",
        f"- **Model:** `{config.CHAT_MODEL}` via Ollama · **Embeddings:** `{config.EMBED_MODEL}`",
        f"- **Run at:** {datetime.datetime.now().isoformat(timespec='seconds')}",
        f"- **Status:** {result.status}", "",
        "## Terminal output", "", "```text", terminal_text, "```", "",
        "## Retrieved passages (exactly what Gemma was given)", "",
    ]
    for n, hit in enumerate(result.hits, start=1):
        cited = " — **cited**" if n in result.cited else ""
        lines += [f"### [S{n}] `{hit.chunk.path}` — {hit.chunk.location}{cited}",
                  f"bm25 {hit.bm25}, cosine {hit.cosine}", "", "```text", hit.chunk.text, "```", ""]
    lines += ["## Assessment (human review)", "", "_To be filled in after checking each claim "
              "against the cited passages._", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def cmd_ask(args) -> int:
    from .harness import ask
    require_local(args.mode)
    result = ask(args.question)
    text = render_ask(result)
    print(text)
    if args.save:
        path = config.EVIDENCE / "ask" / f"{args.save}.md"
        write_ask_card(result, path, text)
        print(f"\nsaved evidence card: {path.relative_to(config.ROOT)}")
    return 0


# ---------------------------------------------------------------- chat

CHAT_HELP = """commands: /notes <topic>  look up your notes · /reset  clear conversation ·
          /save <name>  save last reply to drafts/ · /help · /exit"""


def cmd_chat(args) -> int:
    from .harness import ChatSession
    require_local(args.mode)
    llm.ensure_model(config.CHAT_MODEL)
    session = ChatSession()
    started = datetime.datetime.now()
    transcript_path = config.EVIDENCE / "chat" / f"chat-{started:%Y%m%d-%H%M%S}.md"
    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    transcript = [f"# Chat transcript — {started:%Y-%m-%d %H:%M}", "",
                  f"Mode: chat · Execution: local · Model: `{config.CHAT_MODEL}`", ""]
    piped = not sys.stdin.isatty()

    def show(text: str = "") -> None:
        print(text)
        transcript.append(text)
        transcript_path.write_text("\n".join(transcript) + "\n", encoding="utf-8")

    show(f"[chat | Scout | model: {config.CHAT_MODEL} | local]")
    show(CHAT_HELP)
    while True:
        try:
            line = input("\nyou> ").strip()
        except EOFError:
            break
        if piped:
            print(line)
        transcript.append(f"\n**you>** {line}")
        if not line:
            continue
        if line in ("/exit", "/quit"):
            break
        if line == "/help":
            show(CHAT_HELP)
            continue
        if line == "/reset":
            session.reset()
            show("(conversation cleared)")
            continue
        if line.startswith("/save"):
            name = re.sub(r"[^\w\- ]", "", line[5:].strip()) or f"draft-{datetime.datetime.now():%H%M%S}"
            if not session.last_reply:
                show("(nothing to save yet)")
                continue
            drafts = config.ROOT / "drafts"
            drafts.mkdir(exist_ok=True)
            (drafts / f"{name}.md").write_text(
                f"<!-- Generated by Scout ({config.CHAT_MODEL}) in chat on {datetime.date.today()}. "
                f"A draft, NOT source evidence. -->\n\n{session.last_reply}\n", encoding="utf-8")
            show(f"(saved last reply to drafts/{name}.md — kept outside the wiki)")
            continue
        force = line[len("/notes"):].strip() if line.startswith("/notes") else None
        message = f"What do my notes say about {force}?" if force else line
        turn = session.reply(message, force_query=force)
        show(f"\nscout> {turn['reply'].strip()}")
        if turn["hits"]:
            footer = [f"  (notes looked up — {turn['retrieval']}; passages given to Scout:)"]
            footer += [f"  [S{n}] {h.chunk.path} — {h.chunk.location}"
                       for n, h in enumerate(turn["hits"], 1)]
            if turn["invalid_citations"]:
                footer.append(f"  warning: cited passages that were not provided: {turn['invalid_citations']}")
        elif turn["retrieval"] == "skipped":
            footer = ["  (no notes lookup: not needed for this message)"]
        else:
            footer = ["  (notes looked up — nothing clearly relevant found)"]
        if turn["invalid_citations"] and not turn["hits"]:
            footer.append("  warning: reply contains citation markers but no notes were provided "
                          "— they are not real citations")
        show("\n".join(footer) + f"\n  ({turn['stats']['seconds']} s, "
             f"{turn['history_messages_sent']} earlier messages sent as context)")
    show("\n(chat ended)")
    print(f"transcript saved: {transcript_path.relative_to(config.ROOT)}")
    return 0


# ---------------------------------------------------------------- parser

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wiki", description=DESCRIPTION, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    p = sub.add_parser("ingest", help="build or update wiki notes from vault/raw/")
    p.add_argument("path", nargs="?", default=str(config.RAW),
                   help="vault/raw/ or one file inside it (default: vault/raw)")
    p.add_argument("--force", action="store_true",
                   help="regenerate notes even if the source is unchanged (keeps note names)")
    p.set_defaults(func=cmd_ingest)

    p = sub.add_parser("search", help="show original matching passages, no generated answer")
    p.add_argument("query")
    p.add_argument("-k", type=int, default=5, help="number of passages (default 5)")
    p.add_argument("--kind", choices=["source", "wiki", "all"], default="all",
                   help="search original sources, wiki notes, or both (default all)")
    p.add_argument("--keywords", action="store_true",
                   help="BM25 keywords only (needs no model running at all)")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("ask", help="standalone cited answer, or insufficient evidence")
    p.add_argument("question")
    p.add_argument("--mode", choices=["local", "online"], default="local",
                   help="where the model runs (default local; online is not implemented)")
    p.add_argument("--save", metavar="NAME", help="also write evidence/ask/NAME.md")
    p.set_defaults(func=cmd_ask)

    p = sub.add_parser("chat", help="personal assistant with conversation context")
    p.add_argument("--mode", choices=["local", "online"], default="local",
                   help="where the model runs (default local; online is not implemented)")
    p.set_defaults(func=cmd_chat)

    p = sub.add_parser("check", help="verify links, source references, and note names")
    p.set_defaults(func=cmd_check)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    try:
        return args.func(args)
    except (llm.LocalModelError, FileNotFoundError, ValueError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print()
        return 130


if __name__ == "__main__":
    sys.exit(main())
