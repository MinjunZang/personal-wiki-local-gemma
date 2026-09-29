# Ask-mode evidence card: test2-paraphrased

- **Question:** Why shouldn't General Alpha go after hospitals and data centers as its first customers?
- **Mode:** ask (standalone) · **Execution:** local (offline-capable)
- **Model:** `gemma4:e4b` via Ollama · **Embeddings:** `embeddinggemma`
- **Run at:** 2026-09-29T09:43:13
- **Status:** answered

## Terminal output

```text
[ask | model: gemma4:e4b | local | standalone: no chat history, no persona]
Question: Why shouldn't General Alpha go after hospitals and data centers as its first customers?

Answer:
General Alpha should defer targeting hospitals, data centers, and space applications because
these areas require an established track record and proven reliability before adoption [S1].
These are categorized as long-term or high-barrier markets [S2].

Citations (open these to check the claims):
  [S1] raw/General Alpha 0928.docx — Product / Market (¶1–13)
  [S2] raw/General Alpha 0928.docx — Potential Market (¶14–22)

Retrieved but not cited:
  [S3] raw/General Alpha 0928.docx — 2. Key Risks Identified (¶35–42)
  [S4] raw/General Alpha 0928.docx — SpaceCo Founder — 20-min Version (¶80–100)
  [S5] raw/General Alpha 0928.docx — Commercialization (¶23–29)
  [S6] raw/DTCS_Lean_Transfer_Customer_Discovery.pptx — Slide 4: Iteration Reflection
  [S7] raw/DTCS_Lean_Transfer_Customer_Discovery.pptx — Slide 3: Skinny Business Model Canvas — Initial Hypothesis
  [S8] raw/DTCS_Lean_Transfer_Customer_Discovery.pptx — Slide 2: Expanded Business Focus

(13.85 s, 2193 prompt tokens, 63 output tokens, 9739 prompt chars)
```

## Retrieved passages (exactly what Gemma was given)

### [S1] `raw/General Alpha 0928.docx` — Product / Market (¶1–13) — **cited**
bm25 9.163, cosine 0.511

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

### [S2] `raw/General Alpha 0928.docx` — Potential Market (¶14–22) — **cited**
bm25 8.866, cosine 0.46

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

### [S3] `raw/General Alpha 0928.docx` — 2. Key Risks Identified (¶35–42)
bm25 2.476, cosine 0.478

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
bm25 4.269, cosine 0.418

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

### [S5] `raw/General Alpha 0928.docx` — Commercialization (¶23–29)
bm25 1.939, cosine 0.456

```text
## Commercialization
- What would make customers switch from an existing solution?
  - Clear, quantified advantages in cost, construction timelines, operational reliability, and future predictability.
- How can the technology prove its value in a real operating environment?
  - Following the solar and battery industry precedent: rely on third-party independent laboratory and engineer verification reports (covering reliability, temperature, and lifespan tests) to build trust.
- What type of pilot would reduce customer adoption risk?
  - Small-scale pilot projects partnered with state governments, universities, public entities, or corporate R&D/innovation teams.
```

### [S6] `raw/DTCS_Lean_Transfer_Customer_Discovery.pptx` — Slide 4: Iteration Reflection
bm25 4.326, cosine 0.216

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

### [S7] `raw/DTCS_Lean_Transfer_Customer_Discovery.pptx` — Slide 3: Skinny Business Model Canvas — Initial Hypothesis
bm25 4.262, cosine 0.275

```text
Skinny Business Model Canvas — Initial Hypothesis
Only the two blocks required for this first presentation
03
VALUE PROPOSITION
Turn experimental spectra into
faster chemical understanding.
• Connect computational chemistry with real-time experimental data
• Simulate / predict spectra and infer reaction mechanisms
• Use AI optimization to guide the next experiment
• Potential outcome: less trial-and-error and better use of characterization resources
CUSTOMER SEGMENTS
01
Established / Big Tech R&D
Materials & design engineers; chemistry-heavy workflows
02
Resource-constrained startups
Small teams with limited people, budget, and characterization access
03
Raw-material vendors
Technical / application / R&D teams supporting material adoption
Early-adopter hypothesis: teams with high experiment cost + limited interpretation bandwidth.
DTCS • Lean Transfer • Customer Discovery
3/5
```

### [S8] `raw/DTCS_Lean_Transfer_Customer_Discovery.pptx` — Slide 2: Expanded Business Focus
bm25 3.852, cosine 0.304

```text
Expanded Business Focus
Three customer hypotheses to test first
02
01
Big Tech / Established R&D
Materials & design engineers
Plastic • coatings • adhesives • other reaction-driven materials
Pain-point hypothesis
• Long experiment / characterization cycles
• High cost of lab time & instrumentation
• Need stronger theory ↔ experiment feedback
Interview goal: validate pain severity + workflow + willingness to pay.
02
Resource-Constrained Startups
Small chemistry/materials teams
Limited people, budget, and characterization capacity
Pain-point hypothesis
• Too few specialists to interpret every dataset
• Expensive external characterization
• Need to move from data → decision faster
Interview goal: validate pain severity + workflow + willingness to pay.
03
Raw-Material Vendors
Technical / application / R&D teams
Suppliers of specialty chemical or material inputs
Pain-point hypothesis
• Need evidence behind material performance
• Customer-specific development can be slow
• Potential to differentiate with mechanistic insight
Interview goal: validate pain severity + workflow + willingness to pay.
Key discovery question
```

## Assessment (human review)

**Verdict: PASS**

| Check | Expected | Actual |
|---|---|---|
| Retrieval | Product / Market: "Defer for Later: Space, data centers, hospitals, and critical infrastructure. These require an established track record and proven reliability before adoption." + Key Risks: "High adoption barriers in mission-critical areas without an established track record." | Product / Market = **[S1], rank 1** ✔; Key Risks = [S3] ✔ (retrieved, not cited) |
| Wording test | The source says "defer for later", the question says "shouldn't go after … first" | Retrieval matched the paraphrase at rank 1 ✔ |
| Answer | Needs an established track record / proven reliability first | ✔ |

Claim-by-claim:
1. *"defer targeting hospitals, data centers, and space applications because these areas require an established
   track record and proven reliability before adoption [S1]"* — [S1] "Defer for Later: Space, data centers, hospitals,
   and critical infrastructure. These require an established track record and proven reliability before adoption."
   Supported (adding "space" is correct — it is in the same list).
2. *"These are categorized as long-term or high-barrier markets [S2]"* — [S2] Potential Market: "Long-Term /
   High-Barrier Markets: Space applications; Hospitals, remote communities, and data centers." Supported.

Not included (acceptable, not required): the alternative early markets (remote/transportable power).
Ran offline, 14.2 s.
