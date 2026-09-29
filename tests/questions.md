# Ask-Mode Test Set (written before building retrieval)

This file is the answer key. It lives in `tests/`, **outside** `vault/`, so the retriever can never find it.

Sources (in `vault/raw/`, unchanged; SHA-256 recorded in `docs/source-catalog`):

| ID | File | Type | Language |
|---|---|---|---|
| src-ga | `General Alpha 0928.docx` | Word doc — General Alpha customer interview findings + interview question drafts | English (+ a few Chinese lines) |
| src-dtcs | `DTCS_Lean_Transfer_Customer_Discovery.pptx` | 5-slide deck — DTCS customer discovery hypotheses and interview plan | English |
| src-dt | `数字孪生在制造业中的应用与访谈安排_Summary_202609150939_LectMate.doc` | Meeting summary (Markdown saved as HTML `.doc`) — digital twins in manufacturing | Chinese |

---

## Test 1 — Direct question, one source

**Question:** What kind of pilot projects would reduce customer adoption risk for General Alpha?

**Expected source:** src-ga, section "1. Interview Findings → Commercialization"

**Expected passage:**
> Small-scale pilot projects partnered with state governments, universities, public entities, or corporate R&D/innovation teams.

**Expected behavior:** Answer names small-scale pilots with state governments, universities, public entities, corporate R&D/innovation teams; cites src-ga.

---

## Test 2 — Paraphrased question (wording differs from the source)

**Question:** Why shouldn't General Alpha go after hospitals and data centers as its first customers?

**Expected source:** src-ga, "Best Fit / Defer for Later" and "2. Key Risks Identified"

**Expected passages:**
> Defer for Later: Space, data centers, hospitals, and critical infrastructure. These require an established track record and proven reliability before adoption.

> Space & High-Risk Markets: High adoption barriers in mission-critical areas without an established track record.

**Expected behavior:** Explains these markets need an established track record / proven reliability first; early adopters are remote/transportable power and industrial users instead. Cites src-ga.
**What this tests:** the source says "defer for later", not "shouldn't go after first" — does retrieval still match?

---

## Test 3 — Connects two sources

**Question:** Which customer segments does the DTCS project plan to interview, and does the digital twin meeting agree with that plan?

**Expected sources:** src-dtcs (slides 2, 3, 5) **and** src-dt (section 时间线与实践安排)

**Expected passages:**
- src-dtcs: "01 Established / Big Tech R&D … 02 Resource-constrained startups … 03 Raw-material vendors"; slide 5: "Six interviews intentionally span the 3 segments (2 each)"
- src-dt: "访谈对象的筛选方向已初步明确，分为三类：1. 大厂/技术公司工程师 … 2. 初创公司或中小企业 … 3. 原材料供应商"

**Expected behavior:** Names the same three segments (big tech / established R&D engineers, startups/SMEs, raw-material vendors) and says both sources agree; cites both.
**Known risk:** src-dt is in Chinese and the question is in English — pure keyword (BM25) search will likely miss it. This is a deliberate test of cross-language retrieval.

---

## Test 4 — Unanswerable (answer is NOT in the sources)

**Question:** What price per kWh did General Alpha quote to its pilot customers?

**Why it's unanswerable:** src-ga mentions "$ per kWh" only as a *metric customers want to see*. No actual price or number appears anywhere.

**Expected behavior:** An explicit "insufficient evidence" response. Retrieval will probably return the "$ per kWh" passage (keyword overlap) — the model must NOT invent a number from it.
