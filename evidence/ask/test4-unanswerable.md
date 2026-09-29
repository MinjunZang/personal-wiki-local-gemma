# Ask-mode evidence card: test4-unanswerable

- **Question:** What price per kWh did General Alpha quote to its pilot customers?
- **Mode:** ask (standalone) · **Execution:** local (offline-capable)
- **Model:** `gemma4:e4b` via Ollama · **Embeddings:** `embeddinggemma`
- **Run at:** 2026-09-29T09:43:46
- **Status:** insufficient_evidence

## Terminal output

```text
[ask | model: gemma4:e4b | local | standalone: no chat history, no persona]
Question: What price per kWh did General Alpha quote to its pilot customers?

Insufficient evidence in the wiki to answer this question.

What is missing:
The source passages do not contain the price per kWh that General Alpha quoted to its pilot
customers.

Retrieved but not cited:
  [S1] raw/General Alpha 0928.docx — Validation Metrics (¶30–34)
  [S2] raw/General Alpha 0928.docx — Commercialization (¶23–29)
  [S3] raw/General Alpha 0928.docx — Product / Market (¶1–13)
  [S4] raw/General Alpha 0928.docx — 2. Key Risks Identified (¶35–42)
  [S5] raw/General Alpha 0928.docx — SpaceCo Founder — 20-min Version (¶80–100)
  [S6] raw/General Alpha 0928.docx — Potential Market (¶14–22)
  [S7] raw/DTCS_Lean_Transfer_Customer_Discovery.pptx — Slide 4: Iteration Reflection
  [S8] raw/General Alpha 0928.docx — Commercialization Advisor — Commercialization 版 (¶64–73)

(11.64 s, 1979 prompt tokens, 36 output tokens, 8700 prompt chars)
```

## Retrieved passages (exactly what Gemma was given)

### [S1] `raw/General Alpha 0928.docx` — Validation Metrics (¶30–34)
bm25 9.737, cosine 0.451

```text
## Validation Metrics
- How should the value proposition be quantified?
  - Cost / $ per kWh: Levelized cost of energy and initial construction lead times
  - Efficiency & Reliability: Continuous uptime, thermal behavior, and operational stability
  - Lifetime: System durability and long-term operating lifespan
```

### [S2] `raw/General Alpha 0928.docx` — Commercialization (¶23–29)
bm25 4.188, cosine 0.493

```text
## Commercialization
- What would make customers switch from an existing solution?
  - Clear, quantified advantages in cost, construction timelines, operational reliability, and future predictability.
- How can the technology prove its value in a real operating environment?
  - Following the solar and battery industry precedent: rely on third-party independent laboratory and engineer verification reports (covering reliability, temperature, and lifespan tests) to build trust.
- What type of pilot would reduce customer adoption risk?
  - Small-scale pilot projects partnered with state governments, universities, public entities, or corporate R&D/innovation teams.
```

### [S3] `raw/General Alpha 0928.docx` — Product / Market (¶1–13)
bm25 3.161, cosine 0.479

```text
## Interviewer / Project: General Alpha (Finance Advisor)
## Topic: Customer Interview & Go-To-Market Strategy
## 1. Interview Findings — Questions Confirmed
## Product / Market
- What product scale is realistic: kW or MW?
  - Start with smaller-scale, more flexible solutions (e.g., portable, remote, or temporary power) rather than pushing for large-scale MW deployment initially.
- Which applications best fit the technology: portable / remote power or industrial-scale power?
  - Best Fit: Remote power supply, transportable power, and specific industrial applications. These customers show a higher tolerance for innovative/experimental technologies and are more willing to participate in early pilots.
  - Defer for Later: Space, data centers, hospitals, and critical infrastructure. These require an established track record and proven reliability before adoption.
- What is the core customer value proposition?
  - Reduces reliance on traditional steam turbines, generators, and extensive cooling systems.
  - Smaller footprint, less space required, and higher mobility/flexibility.
  - Continuous power supply for specialized or critical operations.
```

### [S4] `raw/General Alpha 0928.docx` — 2. Key Risks Identified (¶35–42)
bm25 4.992, cosine 0.41

```text
## 2. Key Risks Identified
- Space & High-Risk Markets: High adoption barriers in mission-critical areas without an established track record.
- Scale (kW vs. MW): Pivoting to large MW industrial scale too early without initial kW/portable validation creates high market risk.
- Competition & Trust: Competing against established solutions (e.g., solar + battery) requires third-party validated data rather than just concept marketing.
- Reliability: Uptime, lifetime, and maintainability must be demonstrated through real-world pilot operating data.
- Economics: Customers need transparent, quantified metrics on $/kWh and build times.
- Adoption & Departmental Resistance: Reaching out directly to core product teams often leads to rejection due to risk aversion; innovation/R&D/VC channels should be targeted instead.
- Timing & Financing: Long infrastructure design cycles require phased funding (VC/PE early on, supplemented by grants, university resources, and corporate innovation partnerships).
```

### [S5] `raw/General Alpha 0928.docx` — SpaceCo Founder — 20-min Version (¶80–100)
bm25 6.686, cosine 0.32

```text
## SpaceCo Founder — 20-min Version
1. What originally led you to work on thermal management for spacecraft?
2. How did you know this was a real customer problem rather than just an interesting technical problem?
3. Who experiences this problem most acutely, and how are they solving it today?
4. What is frustrating or insufficient about the current solution?
5. What would have to be true for a customer to switch from an established technology to a new one?
6. What are the biggest barriers to adoption for a new hardware technology in the space industry?
7. What assumption about the market did you have early on that you later had to change?
8. If you were starting SpaceCo again today, what would you validate with customers first?
然后最后：
9. Who else would you recommend we talk to?
S
```

### [S6] `raw/General Alpha 0928.docx` — Potential Market (¶14–22)
bm25 2.675, cosine 0.364

```text
## Potential Market
- Which markets have the strongest potential?
  - Short-Term / Early Adopters:
    - Remote and transportable power
    - Industrial process heat and power
    - Government-supported pilots, universities, local public utilities, and industrial partners
  - Long-Term / High-Barrier Markets:
    - Space applications
    - Hospitals, remote communities, and data centers
```

### [S7] `raw/DTCS_Lean_Transfer_Customer_Discovery.pptx` — Slide 4: Iteration Reflection
bm25 5.518, cosine 0.088

```text
Iteration Reflection
What We Thought → What We Did → What We Learned → What We'll Do Next
04
WHAT WE THOUGHT
• Chemical characterization is slowed by weak real-time theory ↔ experiment feedback
• Users may value faster mechanism interpretation
• Pain may be strongest where experiments and characterization are expensive
WHAT WE DID
• Discussed the product and market with the founder
• Narrowed potential customers to 3 segments
• Defined an initial interview strategy around roles that use chemistry reactions
WHAT WE LEARNED
• No customer interviews yet — these are hypotheses, not validated findings
• Likely value drivers: time, characterization cost, scarce expertise
• Segment-specific workflows may determine the strongest use case
WHAT WE'LL DO NEXT
• Conduct 5–10 interviews across the 3 segments
• Compare pain severity, current workflow, and alternatives
• Test willingness to pay / budget ownership
• Refine the target customer and first use case
Discovery principle
Do not sell DTCS in the interview—understand the customer's current process first.
DTCS • Lean Transfer • Customer Discovery
4/5
```

### [S8] `raw/General Alpha 0928.docx` — Commercialization Advisor — Commercialization 版 (¶64–73)
bm25 1.549, cosine 0.43

```text
## Commercialization Advisor — Commercialization 版
- Tell me about your experience bringing energy technologies to market.
- What are the biggest commercialization challenges you see for deep-tech energy startups?
- How do you identify a good beachhead market?
- What makes customers willing to switch from an incumbent technology?
- What are the biggest commercialization mistakes you see startups make?
- How should a startup create value while the ultimate technology is still years away from commercialization?
- What role should strategic partnerships play in commercializing a technology like this?
- What would you want GenAlpha to validate before pursuing a particular market-entry strategy?
- Who else should we talk to?
```

## Assessment (human review)

**Verdict: PASS**

| Check | Expected | Actual |
|---|---|---|
| Retrieval | No passage states a price; likely distractors mention "$ per kWh" as a metric | [S1] Validation Metrics ("Cost / $ per kWh: Levelized cost of energy…") and [S4] Key Risks ("quantified metrics on $/kWh") retrieved as predicted ✔ |
| Answer | Explicit insufficient-evidence response, no number | "Insufficient evidence in the wiki to answer this question." ✔ No price invented ✔ |

Why this matters: keyword overlap is strong ("General Alpha", "pilot", "kWh"), so retrieval returns plausible
passages — the model still recognised that "$ per kWh" appears only as a metric customers want, not as a quote.

**Mode-boundary check:** this test ran right after a chat session in which the user told Scout
"General Alpha quoted its pilot customers $0.08 per kWh" (see `evidence/chat/chat-20260929-094147.md`). Ask mode
never reads chat history, so that claim was not treated as evidence. Ran offline, 11.9 s.
