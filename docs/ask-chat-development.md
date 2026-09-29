# Ask / Chat / Search — Development Log

Runs during development (internet still on, same local model). All raw records are in
[`evidence/dev-runs/runs-online-dev.jsonl`](../evidence/dev-runs/runs-online-dev.jsonl).
The graded runs are the offline ones in `evidence/offline-run/` and `evidence/ask/`.

## 1. Retrieval checked first (before any model answer)

Test 3 asks in English about a Chinese source. With the first fusion rule, the Chinese
meeting passage (`时间线与实践安排`) was **#1 by embedding similarity (cosine 0.599)** but
**did not appear in the top 10** after fusion. Cause: BM25 gives 0 to text in another language,
so Reciprocal Rank Fusion penalised it.

| Attempt | Change | Test 3 top 6 |
|---|---|---|
| A | plain RRF (BM25 + embeddings) | 6 × DTCS slides / General Alpha, **no Chinese passage** |
| B | cross-language passages: embedding rank counted twice | **6 × Chinese passages**, no DTCS slides (overcorrected) |
| C | B + ignore BM25 for cross-language passages (their only BM25 match was the English note title "Digital Twin Meeting Notes") | Chinese `时间线与实践安排` #1, DTCS slides #2–5 ✔ |

Tests 1, 2, 4 retrieval was unchanged by this fix (checked).

## 2. Ask-mode answers

| Run | Setting | Test 3 result |
|---|---|---|
| 1 | 6 passages | Found both sources, but **attributed the meeting's three categories to "the DTCS project"** (cited the Chinese meeting notes, which never mention DTCS), and never said whether they agree |
| 2 | + research rule 8 ("say what each source states, then compare") | Same misattribution — the prompt change alone did not help |
| 3 | 8 passages (`ASK_PASSAGES = 8`) | Slide 2 (DTCS segments) now retrieved; **attribution correct** (DTCS → Slide 2, meeting → Chinese notes); the agreement is implied but still not stated in one sentence → partial pass |

Root cause of run 1–2: the slides that name DTCS's segments (2 and 3) were not retrieved, so the
small model filled the gap with the only passage that listed three categories. More passages
fixed the evidence gap; the 4B model still compares sources implicitly rather than explicitly.
Tests 1, 2, 4 were rerun with 8 passages: still correct.

Also changed: research rule 5 now says "missing" must be empty when the question is fully
answered — the model was adding a caveat to every answer.

## 3. Chat mode

- "what can we do?" / "what can you help me with?" → accurate capability list, **no notes
  lookup**, no refusal.
- **Failure found:** the second reply contained "[S1], [S2], etc." although no passages were given
  (the persona text showed those labels as an example and the model copied them).
  Fix: persona no longer shows literal labels and says "if no passages were given, write no
  citation markers"; the CLI now prints a warning if markers appear without passages. Rerun: clean.
- Draft plan for General Alpha interviews → notes looked up automatically (message mentions
  "General Alpha"); both citations checked against `Product / Market` and `Commercialization`;
  ideas labelled "Suggestion".
- "make that shorter" → used the previous turn (6 earlier messages sent), no lookup.
- A claim made only in chat ("General Alpha quoted $0.08 per kWh") is accepted as conversation
  context by Scout, but `ask` never reads chat history, so Test 4 still returns insufficient evidence.

## 4. Error handling

[`evidence/modes/error-handling.txt`](../evidence/modes/error-handling.txt). **Bug found:** with
Ollama stopped, `ask` printed "insufficient evidence" (retrieval silently fell back to keywords and
found nothing) instead of reporting that the model was down. Fix: `ask` checks the model before
retrieving. `search` still works with Ollama stopped (keyword-only fallback, clearly labelled).
