# Setup Notes (Step 1) — 2026-09-28

## Device
- Chip: Apple M4
- Memory: 24 GB unified memory
- OS: macOS 15.7.3
- Free disk: ~380 GB
- Python 3.13.5 (Anaconda), Homebrew 6.0.22

## Runtime & Model
- Runtime: Ollama 0.34.4 (installed via `brew install ollama`, running as `brew services start ollama`)
- Model: `gemma4:e4b` (Ollama ID `c6eb396dbd59`), official source: https://ollama.com/library/gemma4
- Quantization: Q4_K_M
- Download size on disk: 9.6 GB (includes vision/audio components)
- Parameters reported by Ollama: 8.0B total (E4B = ~4B effective)
- Context length supported: 131072 (Ollama default loaded context: 4096)
- License: Apache 2.0
- Obsidian 1.13.7 (installed via `brew install --cask obsidian`)

## First measurements (online, before building the harness)
- Cold start + thinking ON (`ollama run`): 19.2 s for a one-sentence reply
- Warm, thinking OFF (`/api/chat`, `"think": false`): 2.3 s total, ~26 tokens/s
- Loaded model memory (`ollama ps`): 3.2 GB, 100% GPU
- System memory free while loaded: ~30%

## Observations
- Thinking mode is ON by default → much slower. Plan: set `"think": false` in the harness.
- Hallucination example: asked "are you running locally?", the model answered "I operate on the cloud"
  even though it runs locally. Good reminder that the model has no knowledge of its own setup —
  the harness/persona must state capabilities explicitly.

## Why E4B
24 GB unified memory leaves plenty of headroom for E4B (~3–5 GB loaded) plus OS, Obsidian, and retrieval.
26B A4B MoE (~14.4 GB) would fit but be tight and slower; not needed for a small personal wiki.

## Embedding model (added in Step 2)
- `embeddinggemma:latest` (Ollama ID `85462619ee72`), 621 MB, BF16, 307.58M parameters, 768-dim, context 2048
- Official source: https://ollama.com/library/embeddinggemma
- Why: multilingual. Test on 2026-09-28: English query "Which customer segments does the DTCS project plan
  to interview?" → Chinese segment passage cosine 0.544 vs unrelated Chinese 0.287 / unrelated English 0.240.
  BM25 alone cannot match English words to Chinese text.

## Python environment
- `.venv` (Python 3.14.7): python-docx 1.2.0, python-pptx 1.0.2, rank-bm25 0.2.2, numpy 2.5.3
- Note: `pip install -e .` did not work reliably here — macOS kept setting the "hidden" flag on the editable
  `.pth` file and Python 3.14 skips hidden `.pth` files. The repo uses the `./wiki` launcher script instead.
