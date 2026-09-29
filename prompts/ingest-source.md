You are helping build a personal wiki (read in Obsidian) from ONE original source document.
Read the source below and return JSON with these fields:

- "title": a short, natural note name for this SOURCE, 2–6 words, Title Case,
  e.g. "General Alpha Interview Notes". No dates, file extensions, IDs, or full sentences.
- "summary": 2–3 neutral English sentences describing what the source contains.
  Only state what the source itself says.
- "topics": 2–4 subjects from this source that deserve their own wiki note. For each:
  - "title": 2–5 words, Title Case, naming the subject (e.g. "Pilot Projects",
    "Digital Twins in Manufacturing"). Not a sentence, not a question.
  - "category": "Projects" for a named project, company, or startup;
    "Concepts" for an idea, method, market, or practice.
  - "description": one sentence on what that note will cover, based on this source.

Rules:
- If the source is mainly about one named project, product, or startup, one topic must be
  that project, titled with its name (e.g. "General Alpha") and category "Projects".
- Topics from the same source must not overlap; merge closely related subjects into one.
- If an existing note title (listed below) is about the same subject, reuse that exact title.
- Write in English even when the source is in another language.
- Prefer subjects that other notes could link to; do not make a topic for a single question.

Existing note titles:
{{existing_titles}}

Source file: {{filename}}
--- SOURCE TEXT ---
{{source_text}}
