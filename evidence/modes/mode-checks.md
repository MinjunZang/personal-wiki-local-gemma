# Chat / Search Mode Checks (offline run)

Run on 2026-09-29 09:39–09:43 PDT with **Wi-Fi off** (`networksetup` reported `Off`, `curl google.com`
failed), right after `brew services restart ollama`. Model `gemma4:e4b` (Q4_K_M), local.
Full output: [`../offline-run/terminal-log.txt`](../offline-run/terminal-log.txt) ·
chat transcript: [`../chat/chat-20260929-094147.md`](../chat/chat-20260929-094147.md) ·
screen recording: [`../offline-run/`](../offline-run/)

| # | Check | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | chat: "what can we do?" | Accurate capabilities, no notes search, no citations, no refusal | Lists brainstorm / draft / rewrite / recall-from-notes; `(no notes lookup: not needed for this message)`; no citation markers | ✅ |
| 2 | chat: "what can you help me with?" | Same | Same capabilities, suggests a starting point; no lookup; no citation markers (this failed in development — see below) | ✅ |
| 3 | chat: "Draft a short plan for my next week of General Alpha customer interviews." | A draft labelled as a suggestion; notes looked up because it is about a project; any facts from notes cited | Starts with "Suggestion:"; lookup `auto` → 3 passages; cites [S2] (Commercialization) for the third-party-verification point — checked, supported | ✅ (see issues) |
| 4 | chat: "make that shorter" | Uses the conversation, no new lookup | Shortened the same 3-day plan; `6 earlier messages sent as context`; no lookup | ✅ |
| 5 | chat: "By the way, General Alpha quoted its pilot customers $0.08 per kWh." | Chat may accept it as conversation context; it must NOT become evidence for ask | Scout accepted it as a user-provided data point (no notes support it: lookup found nothing relevant) | ✅ (context only) |
| 6 | ask Test 4 afterwards: "What price per kWh did General Alpha quote to its pilot customers?" | Insufficient evidence — chat claim ignored | "Insufficient evidence in the wiki to answer this question." | ✅ |
| 7 | search: `./wiki search "pilot projects that reduce adoption risk" --kind source -k 3` | Original passages + file + location, **no generated answer**, no LLM call | 3 raw passages from `General Alpha 0928.docx` (Commercialization ¶23–29, Key Risks ¶35–42, Product / Market ¶1–13), header `no language model used` | ✅ |
| 8 | search with Ollama stopped | Still works | Falls back to BM25 keywords with a clear note ([`error-handling.txt`](error-handling.txt)) | ✅ |

## Issues seen in these offline chat replies (honest notes)

- The plan draft says it is "based on your existing notes" but cites only one passage; its focus on
  "Remote Power Supply" comes from [S1] (Product / Market) without a citation marker. The fact is correct,
  but the citation is missing.
- The model printed LaTeX arrows (`$\rightarrow$`) instead of "→" in two replies, and one line of the
  3-day plan ends with an unclosed "(" — small formatting glitches from the 4B model.
- Scout calls the $0.08/kWh claim "a key data point" — acceptable in chat (the user said it), but it shows
  why chat history must never be used as evidence in ask mode.

## Failure found and fixed earlier (development run, internet on)

In the first development run, reply 2 contained "[S1], [S2], etc." even though no notes were given —
invented citation markers copied from an example in `prompts/persona.md`. The persona was reworded and the
CLI now warns when markers appear without passages. Before/after transcripts: `../dev-runs/`.
