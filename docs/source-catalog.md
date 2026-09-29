# Source Catalog

Originals in `vault/raw/` are **never modified by the harness**. The harness identifies each source by `source_id`;
readable wiki page names are mapped to these IDs in page frontmatter (`source_ids:`).

| source_id | File in `vault/raw/` | Format | Language | SHA-256 (frozen shareable version) |
|---|---|---|---|---|
| src-ga | `General Alpha 0928.docx` | Word (.docx) — customer interview findings, GTM strategy, interview question drafts | English (+ some Chinese notes) | `18cc9024a3d314fc1fb35309152a90f741e985e31818d05d4c55e19c2cdd9df0` |
| src-dtcs | `DTCS_Lean_Transfer_Customer_Discovery.pptx` | PowerPoint, 5 slides — customer discovery hypotheses & interview plan | English | `966f24f3a6d46ebb14355ce1ecb3e86cc160610d59c757d6d48e274b780d5d24` |
| src-dt | `数字孪生在制造业中的应用与访谈安排_Summary_202609150939_LectMate.doc` | Markdown text wrapped in Word-HTML, saved as `.doc` (exported meeting summary) | Chinese | `f93290bf434208c565d966e4019d69713def5c6891d54bf7dff6980d19970171` |

## Privacy redaction (done once, before freezing)

This repository is public, so before the sources were frozen, personal names were replaced with roles
in the copies placed in `vault/raw/` (the author's private originals are kept locally and are git-ignored):

- Interviewee names → roles ("Finance Advisor", "Commercialization Advisor")
- A named startup being interviewed → "SpaceCo"
- A named project founder → "the founder"
- A meeting participant's employer and product → "某消费电子大厂" / "某第一代头显产品" (a large consumer-electronics company / a first-generation headset product)

Only text content was changed; document structure and all other wording are untouched.
The hashes above are of the redacted versions; they are the evidence the wiki cites.
