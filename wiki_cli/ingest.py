"""Ingestion: original sources -> local Gemma -> linked wiki notes + index.

Pipeline for `wiki ingest vault/raw`:
  1. Read each source in raw/ into located sections (sources.py). raw/ is never written.
  2. Plan: send the source text + prompts/ingest-source.md to Gemma -> source title,
     summary, and 2–4 topics. A source whose hash is unchanged reuses its saved plan,
     so re-ingesting cannot invent new note names or duplicates.
  3. Chunk + embed every source (retrieval.py) so each topic can pull its best passages.
  4. Write each topic note from its evidence passages (prompts/ingest-topic.md).
     Notes marked `reviewed: true` are never overwritten; the new draft goes to
     data/drafts/ so it can be compared by hand.
  5. Write one note per source in wiki/Sources/ that links to the original file.
  6. Rebuild vault/index.md and the retrieval index (source passages + wiki notes).
"""
import datetime
import json
import re
import time
from pathlib import Path

import numpy as np

from . import config, llm, retrieval
from .sources import file_sha256, is_source_file, markdown_sections, read_sections

CATEGORIES = ("Projects", "Concepts")
SOURCE_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "topics": {"type": "array", "items": {
            "type": "object",
            "properties": {"title": {"type": "string"},
                           "category": {"type": "string", "enum": list(CATEGORIES)},
                           "description": {"type": "string"}},
            "required": ["title", "category", "description"]}},
    },
    "required": ["title", "summary", "topics"],
}
TOPIC_NOTE_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "points": {"type": "array", "items": {
            "type": "object",
            "properties": {"text": {"type": "string"}, "evidence": {"type": "string"}},
            "required": ["text", "evidence"]}},
        "related": {"type": "array", "items": {
            "type": "object",
            "properties": {"title": {"type": "string"}, "reason": {"type": "string"}},
            "required": ["title", "reason"]}},
    },
    "required": ["summary", "points", "related"],
}
MAX_EVIDENCE_PASSAGES = 6


# ---------------------------------------------------------------- catalog + titles

def load_catalog() -> dict:
    if config.CATALOG.exists():
        return json.loads(config.CATALOG.read_text(encoding="utf-8"))
    return {"sources": {}, "pages": {}}


def save_catalog(catalog: dict) -> None:
    config.CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")


def new_source_id(path: Path, catalog: dict) -> str:
    words = re.findall(r"[A-Za-z]+", path.stem)
    base = "src-" + ("-".join(w.lower() for w in words[:3]) or file_sha256(path)[:8])
    taken = {s.get("source_id") for s in catalog["sources"].values()}
    candidate, n = base, 2
    while candidate in taken:
        candidate, n = f"{base}-{n}", n + 1
    return candidate


def clean_title(title: str) -> str:
    """Make a model-proposed title safe and readable as a filename and graph label."""
    title = re.sub(r'[\\/:*?"<>|#^\[\]]', " ", title)
    words = title.split()[:6]
    words = [w[0].upper() + w[1:] if w.islower() and w not in {"and", "in", "of", "for", "the", "to", "vs"}
             else w for w in words]
    return " ".join(words).strip(" .-–—") or "Untitled"


def title_key(title: str) -> str:
    """Comparison key so 'Pilot Project' and 'pilot projects' map to the same note."""
    words = re.findall(r"[a-z0-9]+", title.lower())
    return " ".join(w[:-1] if len(w) > 3 and w.endswith("s") else w for w in words)


def resolve_title(proposed: str, known_titles: list[str]) -> str:
    cleaned = clean_title(proposed)
    for title in known_titles:
        if title_key(title) == title_key(cleaned):
            return title
    return cleaned


# ---------------------------------------------------------------- note files

def note_path(title: str, category: str) -> Path:
    return config.WIKI / category / f"{title}.md"


def read_note(path: Path) -> tuple[dict, str]:
    """Split a note into (frontmatter dict, body). Only handles our own simple format."""
    text = path.read_text(encoding="utf-8")
    meta = {}
    if text.startswith("---\n"):
        header, _, text = text[4:].partition("\n---\n")
        for line in header.splitlines():
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta, text


def write_note(path: Path, content: str, say) -> bool:
    """Write a note unless a human marked it reviewed. Returns True if written."""
    if path.exists() and read_note(path)[0].get("reviewed") == "true":
        drafts = config.DATA / "drafts"
        drafts.mkdir(parents=True, exist_ok=True)
        (drafts / path.name).write_text(content, encoding="utf-8")
        say(f"    kept reviewed note {path.relative_to(config.VAULT)} (new draft in data/drafts/)")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def frontmatter(fields: dict) -> str:
    lines = []
    for key, value in fields.items():
        if isinstance(value, list):
            value = "[" + ", ".join(value) + "]"
        lines.append(f"{key}: {value}")
    return "---\n" + "\n".join(lines) + "\n---\n"


# ---------------------------------------------------------------- step 2: plan a source

def load_prompt(name: str, **values) -> str:
    text = (config.PROMPTS / name).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def plan_source(path: Path, sections, catalog: dict) -> tuple[dict, dict]:
    known = sorted(catalog["pages"])
    prompt = load_prompt(
        "ingest-source.md",
        existing_titles="\n".join(f"- {t}" for t in known) or "(none yet)",
        filename=path.name,
        source_text="\n\n".join(f"[{s.location}]\n{s.text}" for s in sections),
    )
    plan, stats = llm.chat_json([{"role": "user", "content": prompt}], SOURCE_PLAN_SCHEMA,
                                temperature=0.2)
    topics, seen = [], set()
    for topic in plan["topics"][:4]:
        title = resolve_title(topic["title"], known)
        if title_key(title) in seen:
            continue
        seen.add(title_key(title))
        topics.append({"title": title, "category": topic["category"],
                       "description": topic["description"].strip()})
    source_title = resolve_title(plan["title"], [])
    if title_key(source_title) in seen or title_key(source_title) in map(title_key, known):
        source_title = clean_title(source_title + " Notes")
    return {"title": source_title, "summary": plan["summary"].strip(), "topics": topics}, stats


# ---------------------------------------------------------------- step 4: write a topic note

def select_evidence(topic: dict, candidates: list[int], chunks, vectors) -> list[int]:
    """Best-matching passages for a topic, at least one from each of its sources."""
    query = retrieval.embed_query(f"{topic['title']}: {topic['description']}")
    ranked = sorted(candidates, key=lambda i: -float(vectors[i] @ query))
    chosen = []
    for source_id in dict.fromkeys(chunks[i].source_id for i in ranked):
        chosen.append(next(i for i in ranked if chunks[i].source_id == source_id))
    for i in ranked:
        if len(chosen) >= MAX_EVIDENCE_PASSAGES:
            break
        if i not in chosen:
            chosen.append(i)
    return chosen


def check_points(raw_points: list[dict], labelled: dict, vectors: dict, say) -> list:
    """Harness checks on the model's points before anything is written:
    - the evidence label must name a passage we actually sent (else drop the point);
    - no repeated points (first ingest repeated one sentence with 4 different citations);
    - English only (first ingest pasted Chinese sentences instead of translating);
    - citation check: if another passage matches the point clearly better by embedding
      similarity, the citation is FLAGGED for human review (not changed). In the second
      ingest this check moved citations automatically and 5 of 6 moves were wrong, because
      slides in one deck share vocabulary — so a human now decides."""
    kept, seen = [], set()
    candidates = [p for p in raw_points if p["evidence"].strip().strip("[]") in labelled]
    if len(candidates) < len(raw_points):
        say(f"    dropped {len(raw_points) - len(candidates)} point(s) citing no real passage")
    for point in candidates:
        text = point["text"].strip()
        key = re.sub(r"\W+", " ", text.lower()).strip()
        if key in seen:
            say(f"    dropped a repeated point: {text[:60]}")
            continue
        seen.add(key)
        if len(re.findall(r"[一-鿿]", text)) > len(text) * 0.3:
            say(f"    dropped an untranslated point: {text[:40]}")
            continue
        kept.append([text, point["evidence"].strip().strip("[]")])
    if not kept:
        return []
    point_vectors = [retrieval.embed_query(text) for text, _ in kept]
    for (text, label), vector in zip(kept, point_vectors):
        scores = {lab: float(vectors[lab] @ vector) for lab in labelled}
        best = max(scores, key=scores.get)
        if best != label and scores[best] - scores[label] > 0.08:
            say(f"    CHECK citation {label} ({labelled[label].location}); closest passage is "
                f"{best} ({labelled[best].location}): {text[:60]}")
    return [(text, labelled[label]) for text, label in kept]


def write_topic_note(title: str, info: dict, evidence, evidence_vectors, topic_titles,
                     source_titles, say):
    labelled = {f"S{n}": chunk for n, chunk in enumerate(evidence, start=1)}
    vectors = {f"S{n}": v for n, v in enumerate(evidence_vectors, start=1)}
    prompt = load_prompt(
        "ingest-topic.md",
        title=title,
        description=" ".join(info["descriptions"]),
        other_titles="\n".join(f"- {t}" for t in topic_titles if t != title),
        evidence="\n\n".join(f"[{label}] {c.doc_title} — {c.location}\n{c.text}"
                             for label, c in labelled.items()),
    )
    note, stats = llm.chat_json([{"role": "user", "content": prompt}], TOPIC_NOTE_SCHEMA,
                                temperature=0.2)

    # Harness checks: points must cite real passages; links must point to real topic notes.
    points = check_points(note["points"], labelled, vectors, say)
    related = [(r["title"], r["reason"].strip()) for r in note["related"]
               if r["title"] in topic_titles and r["title"] != title]

    cited_ids = list(dict.fromkeys(c.source_id for _, c in points))
    body = [f"# {title}", "", note["summary"].strip(), "", "## Key points"]
    for text, chunk in points:
        body.append(f"- {text} — *[[{source_titles[chunk.source_id]}]], {chunk.location}*")
    if related:
        body += ["", "## Related notes"]
        body += [f"- [[{t}]] — {reason}" for t, reason in related]
    body += ["", "## Sources"]
    for source_id in cited_ids:
        raw_path = next(c.path for _, c in points if c.source_id == source_id)
        body.append(f"- [[{source_titles[source_id]}]] (original file: [[{raw_path}]])")

    content = frontmatter({
        "title": title, "category": info["category"], "source_ids": cited_ids,
        "generated_by": config.CHAT_MODEL, "reviewed": "false",
        "updated": datetime.date.today().isoformat(),
    }) + "\n".join(body) + "\n"
    written = write_note(note_path(title, info["category"]), content, say)
    return note["summary"].strip(), cited_ids, written, stats


# ---------------------------------------------------------------- step 5: source notes

def write_source_note(entry: dict, raw_name: str, sections, say) -> bool:
    body = [
        f"# {entry['title']}", "", entry["summary"], "",
        f"**Original file:** [[raw/{raw_name}]]", "",
        "## Notes built from this source",
        *[f"- [[{t['title']}]] — {t['description']}" for t in entry["topics"]],
        "", "## Sections in the original",
        *[f"- {s.location}" for s in sections],
    ]
    content = frontmatter({
        "title": entry["title"], "category": "Sources", "source_id": entry["source_id"],
        "original_file": f"raw/{raw_name}", "sha256": entry["sha256"],
        "generated_by": config.CHAT_MODEL, "reviewed": "false",
        "updated": datetime.date.today().isoformat(),
    }) + "\n".join(body) + "\n"
    return write_note(note_path(entry["title"], "Sources"), content, say)


# ---------------------------------------------------------------- step 6: index.md

def write_index(catalog: dict) -> None:
    lines = [f"# {config.WIKI_TITLE}", "", config.WIKI_PURPOSE, "",
             "Start here: pick a project or concept, follow its related-note links, and use each "
             "note's *Sources* section to open the original evidence in `raw/`.", ""]
    groups = {"Projects": "Named projects and startups",
              "Concepts": "Ideas, methods, and market topics",
              "Sources": "One note per original document, linking to the file in raw/"}
    for category, blurb in groups.items():
        pages = sorted((t, p) for t, p in catalog["pages"].items() if p["category"] == category)
        if not pages:
            continue
        lines += [f"## {category}", f"*{blurb}*", ""]
        for title, page in pages:
            first_sentence = re.split(r"(?<=[.!?])\s", page.get("summary", ""))[0]
            lines.append(f"- [[{title}]] — {first_sentence}")
        lines.append("")
    config.INDEX_MD.write_text("\n".join(lines), encoding="utf-8")


def check_vault() -> list[str]:
    """Find broken or ambiguous [[links]], missing headings, and duplicate note names."""
    problems = []
    notes = list(config.WIKI.rglob("*.md")) + [config.INDEX_MD]
    by_name: dict[str, list[Path]] = {}
    for path in config.WIKI.rglob("*.md"):
        by_name.setdefault(path.stem, []).append(path)
    for name, paths in by_name.items():
        if len(paths) > 1:
            problems.append(f"duplicate note name '{name}': {[str(p) for p in paths]}")
    for path in notes:
        meta, body = read_note(path)
        rel = path.relative_to(config.VAULT)
        if path != config.INDEX_MD and not body.lstrip().startswith(f"# {path.stem}\n"):
            problems.append(f"{rel}: first heading does not match the filename")
        for target in re.findall(r"\[\[([^\]|#]+)", body):
            if "/" in target:  # path link, e.g. [[raw/file.docx]]
                if not (config.VAULT / target).exists():
                    problems.append(f"{rel}: link to missing file [[{target}]]")
            elif target not in by_name:
                problems.append(f"{rel}: link to missing note [[{target}]]")
    return problems


def wiki_chunks() -> list[retrieval.Chunk]:
    chunks = []
    for path in sorted(config.WIKI.rglob("*.md")):
        meta, body = read_note(path)
        title = meta.get("title", path.stem)
        chunks += retrieval.chunk_sections(
            markdown_sections(body, title), kind="wiki",
            path=str(path.relative_to(config.VAULT)), doc_title=title,
            source_id=meta.get("source_id", ""))
    return chunks


# ---------------------------------------------------------------- the whole pipeline

def ingest(target: Path, force: bool = False, say=print) -> dict:
    target, raw_dir = target.resolve(), config.RAW.resolve()
    if not target.exists():
        raise FileNotFoundError(f"{target} does not exist.")
    if target != raw_dir and raw_dir not in target.parents:
        raise ValueError(f"Sources must live in {config.RAW}. Copy the file there first, then ingest it.")
    files = [target] if target.is_file() else sorted(p for p in target.iterdir() if is_source_file(p))
    if not files:
        raise FileNotFoundError(f"No supported source files in {target}.")
    llm.ensure_model(config.CHAT_MODEL)
    llm.ensure_model(config.EMBED_MODEL)

    started = time.perf_counter()
    catalog = load_catalog()
    calls, touched_topics, touched_sources = [], set(), []

    # Steps 1–2: plan each source (or reuse the saved plan).
    for path in files:
        entry = catalog["sources"].setdefault(path.name, {})
        entry.setdefault("source_id", new_source_id(path, catalog))
        sha = file_sha256(path)
        unchanged = entry.get("sha256") == sha and "topics" in entry
        notes_exist = unchanged and note_path(entry["title"], "Sources").exists() and all(
            note_path(t["title"], t["category"]).exists() for t in entry["topics"])
        if notes_exist and not force:
            say(f"= {path.name}: unchanged and notes exist, skipping (use --force to regenerate)")
            continue
        if unchanged:
            say(f"~ {path.name}: unchanged, regenerating its notes with the saved titles")
        else:
            say(f"+ {path.name}: asking {config.CHAT_MODEL} for a title, summary, and topics ...")
            plan, stats = plan_source(path, read_sections(path), catalog)
            calls.append({"step": "plan", "file": path.name, **stats})
            entry.update(plan)
            for topic in plan["topics"]:  # register titles so the next source can reuse them
                catalog["pages"].setdefault(topic["title"], {"category": topic["category"]})
            say(f"    source note: {plan['title']}")
            say("    topics: " + ", ".join(t["title"] for t in plan["topics"]))
        entry["sha256"] = sha
        entry["ingested"] = datetime.date.today().isoformat()
        touched_sources.append(path.name)
        touched_topics.update(t["title"] for t in entry["topics"])

    # Step 3: chunk + embed all original sources.
    source_files = {name: config.RAW / name for name in catalog["sources"]
                    if (config.RAW / name).exists() and "title" in catalog["sources"][name]}
    sections_by_file = {name: read_sections(p) for name, p in source_files.items()}
    source_chunks = []
    for name, sections in sections_by_file.items():
        entry = catalog["sources"][name]
        source_chunks += retrieval.chunk_sections(
            sections, kind="source", path=f"raw/{name}", doc_title=entry["title"],
            source_id=entry["source_id"])
    say(f"Embedding {len(source_chunks)} source passages with {config.EMBED_MODEL} ...")
    source_vectors = retrieval.embed_chunks(source_chunks)

    # Step 4: topic notes (a topic can draw on several sources).
    topics: dict[str, dict] = {}
    for name, entry in catalog["sources"].items():
        for t in entry.get("topics", []):
            info = topics.setdefault(t["title"], {"category": t["category"],
                                                  "descriptions": [], "source_ids": []})
            info["descriptions"].append(t["description"])
            info["source_ids"].append(entry["source_id"])
    source_titles = {e["source_id"]: e["title"] for e in catalog["sources"].values() if "title" in e}
    topic_titles = sorted(topics)  # "Related notes" link topics; sources get their own section
    written = kept = 0
    for title in sorted(touched_topics):
        info = topics[title]
        candidates = [i for i, c in enumerate(source_chunks) if c.source_id in info["source_ids"]]
        evidence_ids = select_evidence({"title": title, "description": info["descriptions"][0]},
                                       candidates, source_chunks, source_vectors)
        say(f"  writing [[{title}]] from {len(evidence_ids)} passages ...")
        summary, cited, was_written, stats = write_topic_note(
            title, info, [source_chunks[i] for i in evidence_ids],
            [source_vectors[i] for i in evidence_ids], topic_titles, source_titles, say)
        calls.append({"step": "note", "title": title, **stats})
        written, kept = written + was_written, kept + (not was_written)
        page = catalog["pages"].setdefault(title, {})
        if was_written or "summary" not in page:
            page.update({"category": info["category"], "summary": summary, "source_ids": cited,
                         "path": str(note_path(title, info["category"]).relative_to(config.VAULT))})

    # Step 5: source notes.
    for name in touched_sources:
        entry = catalog["sources"][name]
        was_written = write_source_note(entry, name, sections_by_file[name], say)
        written, kept = written + was_written, kept + (not was_written)
        catalog["pages"][entry["title"]] = {
            "category": "Sources", "summary": entry["summary"], "source_ids": [entry["source_id"]],
            "path": str(note_path(entry["title"], "Sources").relative_to(config.VAULT))}

    # Step 6: index.md + retrieval index over sources and wiki notes.
    save_catalog(catalog)
    write_index(catalog)
    notes = wiki_chunks()
    say(f"Embedding {len(notes)} wiki passages and saving the search index ...")
    retrieval.save_index(source_chunks + notes,
                         np.vstack([source_vectors, retrieval.embed_chunks(notes)]))

    report = {
        "date": datetime.datetime.now().isoformat(timespec="seconds"),
        "model": config.CHAT_MODEL, "embed_model": config.EMBED_MODEL, "mode": "local",
        "files": [p.name for p in files], "regenerated_sources": touched_sources,
        "notes_written": written, "notes_kept_reviewed": kept,
        "passages_indexed": len(source_chunks) + len(notes),
        "seconds_total": round(time.perf_counter() - started, 1), "model_calls": calls,
    }
    config.DATA.mkdir(exist_ok=True)
    (config.DATA / "last-ingest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                                  encoding="utf-8")
    return report
