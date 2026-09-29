# Ask-mode evidence card: test1-direct

- **Question:** What kind of pilot projects would reduce customer adoption risk for General Alpha?
- **Mode:** ask (standalone) · **Execution:** local (offline-capable)
- **Model:** `gemma4:e4b` via Ollama · **Embeddings:** `embeddinggemma`
- **Run at:** 2026-09-29T09:42:59
- **Status:** answered

## Terminal output

```text
[ask | model: gemma4:e4b | local | standalone: no chat history, no persona]
Question: What kind of pilot projects would reduce customer adoption risk for General Alpha?

Answer:
Small-scale pilot projects are recommended, specifically those partnered with state
governments, universities, public entities, or corporate R&D/innovation teams [S1].

Citations (open these to check the claims):
  [S1] raw/General Alpha 0928.docx — Commercialization (¶23–29)

Retrieved but not cited:
  [S2] raw/General Alpha 0928.docx — Product / Market (¶1–13)
  [S3] raw/General Alpha 0928.docx — 2. Key Risks Identified (¶35–42)
  [S4] raw/General Alpha 0928.docx — SpaceCo Founder — 20-min Version (¶80–100)
  [S5] raw/General Alpha 0928.docx — Space (¶77–78)
  [S6] raw/General Alpha 0928.docx — Finance Advisor — Finance 版 (¶51–62)
  [S7] raw/General Alpha 0928.docx — Potential Market (¶14–22)
  [S8] raw/General Alpha 0928.docx — Commercialization Advisor — Commercialization 版 (¶64–73)

(11.26 s, 1923 prompt tokens, 49 output tokens, 8376 prompt chars)
```

## Retrieved passages (exactly what Gemma was given)

### [S1] `raw/General Alpha 0928.docx` — Commercialization (¶23–29) — **cited**
bm25 12.25, cosine 0.608

```text
## Commercialization
- What would make customers switch from an existing solution?
  - Clear, quantified advantages in cost, construction timelines, operational reliability, and future predictability.
- How can the technology prove its value in a real operating environment?
  - Following the solar and battery industry precedent: rely on third-party independent laboratory and engineer verification reports (covering reliability, temperature, and lifespan tests) to build trust.
- What type of pilot would reduce customer adoption risk?
  - Small-scale pilot projects partnered with state governments, universities, public entities, or corporate R&D/innovation teams.
```

### [S2] `raw/General Alpha 0928.docx` — Product / Market (¶1–13)
bm25 7.685, cosine 0.497

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

### [S3] `raw/General Alpha 0928.docx` — 2. Key Risks Identified (¶35–42)
bm25 7.295, cosine 0.534

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

### [S4] `raw/General Alpha 0928.docx` — SpaceCo Founder — 20-min Version (¶80–100)
bm25 3.641, cosine 0.408

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

### [S5] `raw/General Alpha 0928.docx` — Space (¶77–78)
bm25 4.083, cosine 0.376

```text
## Space
Thanks again for taking the time. I’m really interested in learning from your experience building SpaceCo. I’m working on another cleantech project this semester, but rather than pitching anything, I’d mainly love to understand how you think about the space market, customer needs, and commercialization challenges.
```

### [S6] `raw/General Alpha 0928.docx` — Finance Advisor — Finance 版 (¶51–62)
bm25 2.074, cosine 0.413

```text
## 我建议你实际 Interview 不要问17个
20–30分钟的话，我建议你准备 8个核心问题 + follow-up。
## Finance Advisor — Finance 版
- Tell me about your role and the types of energy projects you typically evaluate.
- What are the biggest barriers preventing new nuclear / clean-energy technologies from reaching commercial scale?
- Which challenge is most underestimated by technology developers?
- What makes an energy technology “financeable”?
- What assumptions would you want validated before taking a technology seriously?
- What would make you skeptical of a startup claiming a significant reduction in capital cost?
- What evidence would investors or financiers need before committing capital?
- If you were advising GenAlpha, what would you tell us to learn from the market next?
- Who else should we talk to?
```

### [S7] `raw/General Alpha 0928.docx` — Potential Market (¶14–22)
bm25 2.675, cosine 0.393

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

### [S8] `raw/General Alpha 0928.docx` — Commercialization Advisor — Commercialization 版 (¶64–73)
bm25 1.549, cosine 0.468

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

| Check | Expected (from `tests/questions.md`, written before building) | Actual |
|---|---|---|
| Retrieval | `General Alpha 0928.docx` → Commercialization: "Small-scale pilot projects partnered with state governments, universities, public entities, or corporate R&D/innovation teams." | Retrieved as **[S1], rank 1** ✔ |
| Answer | Small-scale pilots with state governments, universities, public entities, corporate R&D/innovation teams | Same content ✔ |
| Citation | src-ga | [S1] = `raw/General Alpha 0928.docx` — Commercialization (¶23–29) ✔ |

Claim-by-claim: *"Small-scale pilot projects are recommended, specifically those partnered with state governments,
universities, public entities, or corporate R&D/innovation teams [S1]"* — stated almost word for word in [S1]
under "What type of pilot would reduce customer adoption risk?". Supported.

No invented details. The other 7 passages (all from the same interview doc) were retrieved but correctly not cited.
Ran offline (Wi-Fi off, see `evidence/offline-run/terminal-log.txt`), 11.6 s.
