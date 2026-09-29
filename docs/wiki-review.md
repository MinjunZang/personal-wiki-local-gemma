# Wiki Generation & Review Log

How the wiki in `vault/wiki/` was produced by local Gemma (`gemma4:e4b`, Q4_K_M, via Ollama)
and then reviewed against the originals in `vault/raw/`. Earlier outputs are kept as evidence.

## Run 1 — first automatic ingest (2026-09-28)

Evidence: [`evidence/ingest-v1/`](../evidence/ingest-v1/) (notes, index, catalog, terminal output)

- Before it: one failed attempt — Ollama returned `timed out waiting for llama-server to start`
  after ~10 minutes. A plain retry loaded the model in 6.6 s. `llm.chat()` now retries that
  specific error once.
- Result: 15 notes (12 topics + 3 source notes), 362 s total, 16 model calls.

Problems found when reading every note against the sources:

| # | Problem | Example |
|---|---|---|
| 1 | Points copied in Chinese instead of translated | `Chemical Process Simulation`, `New Product Development` |
| 2 | Same point repeated with wrong citations | `Customer Discovery Process`: one sentence × 4, citing slides 1, 2, 4, 5 — only slide 2 says it |
| 3 | Unreadable locations after merging tiny sections | `Interviewer / Project… + Topic… + 1. Interview Findings… + Product / Market (¶1–13)` |
| 4 | Poor structure | No `Projects/` notes for General Alpha or DTCS; four overlapping digital-twin notes (`Virtual To Physical Connection`, `Chemical Process Simulation`, `Manufacturing Case Studies`, `New Product Development`) |
| 5 | Links based on a shared word, not a real connection | `Early Adopter Markets` → `Digital Twin Manufacturing Applications` ("industrial" appears in both) |
| 6 | Vague source-note titles | `Digital Twin Chemical Science` (for a slide deck), `General Alpha Finance Advisor Interview` (doc also has other advisors' questions) |

## Changes after run 1

- **Code** (`wiki_cli/`): passage label = the section holding most of the text (fixes #3);
  harness drops repeated points and untranslated points (#1, #2); "Related notes" may only link
  topic notes (#5); embedding-based citation check added (see run 2).
- **Prompts** (`prompts/`): translate Chinese facts into English; each point different and cited
  to the passage that contains it; a named project must become a `Projects` note; topics from one
  source must not overlap; sharing one word is not a connection.
- **Reviewed note plan** (`catalog.json`, edited by hand): source titles `General Alpha Interview Notes`,
  `DTCS Customer Discovery Deck`, `Digital Twin Meeting Notes`; topics merged to 9 (2 projects,
  7 concepts); four digital-twin notes merged into `Digital Twins in Manufacturing`;
  `Portable Power Solutions` merged into `General Alpha` / `Early Adopter Markets`;
  `Third-Party Validation` widened to `Real-World Validation` (it draws on two sources).

## Run 2 — regenerate with the reviewed plan (`wiki ingest vault/raw --force`)

Evidence: [`evidence/ingest-v2-terminal-output.txt`](../evidence/ingest-v2-terminal-output.txt)
— 12 notes, 248.5 s, 9 model calls (plans were reused, so no planning calls).

**New failure: the automatic citation check made citations worse.** The check moved a point's
citation when another passage had a higher embedding similarity. Checked by hand, **5 of its 6 moves
were wrong** — e.g. "hospitals and data centers should be deferred…" was moved from
`Product / Market (¶1–13)` (correct) to `2. Key Risks Identified (¶35–42)`; "raw-material vendors …
support material adoption" was moved to slide 5 although the wording is on slide 3. Slides in one
deck and sections of one interview share vocabulary, so similarity cannot tell them apart.
**Fix:** the check now only prints `CHECK citation …` for a human to review; it never changes a citation.

## Human review corrections (then every note marked `reviewed: true`)

| Note | Correction |
|---|---|
| Target Customer Segments | 2 citations corrected to Slide 3; added the matching Chinese meeting passage (the three interviewee categories), so the note now connects two sources; replaced an off-topic point with the "2 interviews per segment" plan |
| Customer Discovery Interviews | "not pitching, understanding the most painful process issues" re-cited to the meeting notes (it is not on slide 2); off-topic pain-point points replaced with General Alpha interview-design facts (8 core questions; each list ends with "who else should we talk to?") |
| Early Adopter Markets | "defer hospitals/data centers" re-cited to `Product / Market`; wrong link to `Target Customer Segments` (a DTCS note) replaced by `General Alpha` |
| Real-World Validation | "reliability … pilot operating data" re-cited to `Key Risks` (¶35–42); added the injection-molding example; weak link replaced |
| Financeable Energy Technology | A draft *interview question* had been written as a fact ("investors need to know…") — rewritten as a question; off-topic point removed |
| Digital Twins in Manufacturing | Added the semiconductor case; wrong link to `Early Adopter Markets` replaced by `Real-World Validation`, `DTCS`, `Target Customer Segments` |
| Chemical R&D Pain Points, DTCS | Clarified that pain points are **hypotheses** (slide 4: "No customer interviews yet"); LaTeX `$\leftrightarrow$` → `↔`; links fixed |
| General Alpha | Link to `Customer Discovery Interviews` added |

`./wiki check` after review: 0 problems, 137 links checked (including 16 links to the original files).

## Re-ingestion without duplicates

Reviewed notes are never overwritten: a forced re-ingest writes its new draft to `data/drafts/`
for comparison. Known sources reuse their saved note titles from `catalog.json`, so re-ingesting
cannot bring back old or machine-style names. See
[`evidence/reingest-duplicate-test.txt`](../evidence/reingest-duplicate-test.txt).
