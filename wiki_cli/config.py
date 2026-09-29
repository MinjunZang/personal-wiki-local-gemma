"""Paths and model settings for the personal wiki harness.

Everything the harness reads or writes is defined here, so it is easy to see
which folders are evidence (vault/raw), curated notes (vault/wiki),
and machine files (data/).
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The Obsidian vault: open this folder (not the repo root) in Obsidian.
VAULT = ROOT / "vault"
RAW = VAULT / "raw"            # original sources — never modified by the harness
WIKI = VAULT / "wiki"          # generated + reviewed notes
INDEX_MD = VAULT / "index.md"  # human landing page

# Outside the vault
PROMPTS = ROOT / "prompts"          # instructions loaded per mode
DATA = ROOT / "data"                # retrieval chunks + embeddings (rebuilt by ingest)
CATALOG = ROOT / "catalog.json"     # source_id <-> file, hash, note titles (tracked in git)
EVIDENCE = ROOT / "evidence"        # saved ask/chat/search outputs

WIKI_TITLE = "Deep-Tech Customer Discovery Wiki"
WIKI_PURPOSE = (
    "My notes from customer-discovery work for two deep-tech startup projects: "
    "General Alpha (compact energy technology) and DTCS (digital twins for chemistry "
    "and manufacturing)."
)

# Local model runtime (Ollama). Override with environment variables if needed.
OLLAMA_URL = os.environ.get("WIKI_OLLAMA_URL", "http://localhost:11434")
CHAT_MODEL = os.environ.get("WIKI_MODEL", "gemma4:e4b")
EMBED_MODEL = os.environ.get("WIKI_EMBED_MODEL", "embeddinggemma")
NUM_CTX = int(os.environ.get("WIKI_NUM_CTX", "8192"))  # tokens of context per model call

# Passage size for retrieval chunks (characters). ~1200 chars ≈ 250–300 English tokens.
CHUNK_MAX_CHARS = 1200
CHUNK_MIN_CHARS = 200
