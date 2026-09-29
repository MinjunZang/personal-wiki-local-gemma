"""The retrieval tool: split text into passages, index them, and search.

Hybrid search = BM25 keywords + local embeddings, merged with Reciprocal Rank Fusion.
- BM25 needs no model at all, so `wiki search` still works if Ollama is down.
- Embeddings (embeddinggemma, multilingual) let an English question find the
  Chinese meeting notes, which keyword matching alone cannot do.

Machine files live in data/ (outside the vault): chunks.json + embeddings.npy.
"""
import json
import re
from dataclasses import asdict, dataclass

import numpy as np
from rank_bm25 import BM25Okapi

from . import config, llm
from .sources import Section, format_location


@dataclass
class Chunk:
    chunk_id: str
    kind: str          # "source" (original evidence in raw/) or "wiki" (generated note)
    path: str          # relative to the vault, e.g. "raw/General Alpha 0928.docx"
    doc_title: str     # readable title of the source or note
    location: str      # e.g. "Commercialization (¶23–29)" or "Slide 3: ..."
    text: str
    source_id: str = ""


@dataclass
class Hit:
    chunk: Chunk
    score: float       # fused rank score (higher is better)
    bm25: float
    cosine: float | None


# ---------------------------------------------------------------- chunking

def chunk_sections(sections: list[Section], *, kind: str, path: str, doc_title: str,
                   source_id: str = "") -> list[Chunk]:
    """Merge tiny neighbouring sections and split long ones, keeping locations."""
    groups: list[list[Section]] = []
    for section in sections:
        if groups and sum(len(s.text) for s in groups[-1]) < config.CHUNK_MIN_CHARS \
                and groups[-1][-1].unit != "slide":
            groups[-1].append(section)
        else:
            groups.append([section])

    chunks = []
    for group in groups:
        # Tiny heading-only sections get merged into their neighbour; label the passage
        # with the section that holds most of the text so locations stay readable.
        label = max(group, key=lambda s: len(s.text)).label
        unit = group[0].unit
        lines = [line for s in group for line in s.lines]
        parts, current = [], []
        for line in lines:
            if current and sum(len(t) + 1 for _, t in current) + len(line[1]) > config.CHUNK_MAX_CHARS:
                parts.append(current)
                current = []
            current.append(line)
        if current:
            parts.append(current)
        for n, part in enumerate(parts, start=1):
            location = format_location(label, unit, part)
            if len(parts) > 1 and unit is None:
                location += f" (part {n}/{len(parts)})"
            chunks.append(Chunk(
                chunk_id=f"{source_id or path}#{len(chunks) + 1}", kind=kind, path=path,
                doc_title=doc_title, location=location,
                text="\n".join(t for _, t in part), source_id=source_id,
            ))
    return chunks


# ---------------------------------------------------------------- BM25 tokens

_STOP = set("""a an and are as at be by can do does for from has have how i in is it its of on or
that the their them they this to was were what when where which who why will with would you your
should shouldn t s""".split())
_WORD = re.compile(r"[a-z0-9$]+")
_CJK = re.compile(r"[一-鿿]+")


def tokenize(text: str) -> list[str]:
    """English words (lightly stemmed) + Chinese character bigrams."""
    text = text.lower()
    tokens = []
    for word in _WORD.findall(text):
        if word in _STOP:
            continue
        if len(word) > 4 and word.endswith("s") and not word.endswith("ss"):
            word = word[:-1]  # hospitals -> hospital, centers -> center
        tokens.append(word)
    for run in _CJK.findall(text):
        tokens += [run[i:i + 2] for i in range(len(run) - 1)] or [run]
    return tokens


def is_cjk(text: str) -> bool:
    """True if the text is mostly Chinese (used to spot cross-language query/passage pairs)."""
    letters = re.findall(r"[a-zA-Z]|[\u4e00-\u9fff]", text)
    return bool(letters) and sum(ch >= "\u4e00" for ch in letters) > len(letters) * 0.3


# ---------------------------------------------------------------- embeddings

def _doc_prompt(chunk: Chunk) -> str:
    # embeddinggemma's recommended document format
    return f"title: {chunk.doc_title} — {chunk.location} | text: {chunk.text}"


def _query_prompt(query: str) -> str:
    return f"task: search result | query: {query}"


def embed_chunks(chunks: list[Chunk]) -> np.ndarray:
    vectors = np.array(llm.embed([_doc_prompt(c) for c in chunks]), dtype=np.float32)
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def embed_query(query: str) -> np.ndarray:
    vector = np.array(llm.embed([_query_prompt(query)])[0], dtype=np.float32)
    return vector / np.linalg.norm(vector)


# ---------------------------------------------------------------- index files

def save_index(chunks: list[Chunk], vectors: np.ndarray) -> None:
    config.DATA.mkdir(exist_ok=True)
    (config.DATA / "chunks.json").write_text(
        json.dumps({"embed_model": config.EMBED_MODEL, "chunks": [asdict(c) for c in chunks]},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    np.save(config.DATA / "embeddings.npy", vectors)


class Retriever:
    """Loads the saved index and answers search queries."""

    def __init__(self):
        chunks_file = config.DATA / "chunks.json"
        if not chunks_file.exists():
            raise FileNotFoundError(
                "No search index yet. Build it first with:  wiki ingest vault/raw")
        data = json.loads(chunks_file.read_text(encoding="utf-8"))
        self.chunks = [Chunk(**c) for c in data["chunks"]]
        self.vectors = np.load(config.DATA / "embeddings.npy")
        self.bm25 = BM25Okapi([tokenize(c.doc_title + " " + c.text) for c in self.chunks])
        self.cjk = [is_cjk(c.text) for c in self.chunks]
        self.notice = ""  # set when search falls back to keywords only

    def search(self, query: str, k: int = 5, kinds: tuple[str, ...] = ("source", "wiki"),
               use_embeddings: bool = True) -> list[Hit]:
        allowed = [i for i, c in enumerate(self.chunks) if c.kind in kinds]
        bm25_all = self.bm25.get_scores(tokenize(query))

        cosines = None
        if use_embeddings:
            try:
                cosines = self.vectors @ embed_query(query)
            except llm.LocalModelError as err:
                self.notice = f"Embedding model unavailable, using keyword search only. ({err})"

        # Reciprocal Rank Fusion: sum of 1/(60 + rank) across the two rankings.
        # A passage in another language than the query (Chinese notes, English question)
        # is invisible to BM25 (only its English title can match), so it is scored by its
        # embedding rank alone, counted twice, instead of being penalised. Without this, the
        # Chinese meeting passage for Test 3 was #1 by embeddings but fell out of the top 10.
        query_is_cjk = is_cjk(query)
        fused = {i: 0.0 for i in allowed}
        by_bm25 = sorted((i for i in allowed if bm25_all[i] > 0
                          and (cosines is None or self.cjk[i] == query_is_cjk)),
                         key=lambda i: -bm25_all[i])
        for rank, i in enumerate(by_bm25):
            fused[i] += 1 / (60 + rank)
        if cosines is not None:
            for rank, i in enumerate(sorted(allowed, key=lambda i: -cosines[i])):
                cross_language = self.cjk[i] != query_is_cjk
                fused[i] += (2 if cross_language else 1) / (60 + rank)

        best = sorted((i for i in allowed if fused[i] > 0), key=lambda i: -fused[i])[:k]
        return [Hit(self.chunks[i], round(fused[i], 5), round(float(bm25_all[i]), 3),
                    None if cosines is None else round(float(cosines[i]), 3)) for i in best]
