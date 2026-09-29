#!/usr/bin/env bash
# Offline demonstration: run AFTER turning Wi-Fi off.
#   bash tests/run_offline_demo.sh
# Saves everything to evidence/offline-run/ (terminal log, memory samples) and
# evidence/ask/ (four ask-mode evidence cards). Uses only the local CLI and Ollama.
set -u
cd "$(dirname "$0")/.."
OUT=evidence/offline-run
mkdir -p "$OUT" evidence/ask
LOG="$OUT/terminal-log.txt"
: > "$LOG"

run() {  # print a command like a terminal would, run it, keep the output
  echo "" | tee -a "$LOG"
  echo "\$ $*" | tee -a "$LOG"
  "$@" 2>&1 | tee -a "$LOG"
}

echo "# Offline demonstration — $(date '+%Y-%m-%d %H:%M:%S %Z')" | tee -a "$LOG"

# 1. Prove the machine is offline (read-only checks).
run networksetup -getairportpower en0
echo "" | tee -a "$LOG"
echo '$ curl -sS -m 5 https://www.google.com -o /dev/null   # must FAIL when offline' | tee -a "$LOG"
if curl -sS -m 5 https://www.google.com -o /dev/null 2>>"$LOG"; then
  echo "!! Internet is reachable — turn Wi-Fi off and run again." | tee -a "$LOG"; exit 1
fi
echo "OK: internet not reachable" | tee -a "$LOG"

# 2. Restart the local runtime and the CLI (no warm caches from an online session).
run brew services restart ollama
sleep 3
run ollama list
run ./wiki --help

# Memory sampler for the rest of the run.
( while true; do { date +%T; ollama ps | tail -n +2; memory_pressure | tail -1; } >> "$OUT/memory-samples.txt"; sleep 3; done ) &
SAMPLER=$!
trap 'kill $SAMPLER 2>/dev/null' EXIT

# 3. Ingestion offline: re-generate the notes of one source with local Gemma.
#    Reviewed notes are kept (drafts go to data/drafts/), so this also re-checks "no duplicates".
run find vault/wiki -name "*.md"
run /usr/bin/time -p ./wiki ingest "vault/raw/General Alpha 0928.docx" --force
run find vault/wiki -name "*.md"
run ./wiki check

# 4. Search mode: original passages, no generated answer.
run ./wiki search "pilot projects that reduce adoption risk" --kind source -k 3

# 5. Chat mode checks (capabilities, a draft, a follow-up, and a claim made only in chat).
echo "" | tee -a "$LOG"
echo '$ ./wiki chat   (messages typed below)' | tee -a "$LOG"
printf '%s\n' \
  "what can we do?" \
  "what can you help me with?" \
  "Draft a short plan for my next week of General Alpha customer interviews." \
  "make that shorter" \
  "By the way, General Alpha quoted its pilot customers \$0.08 per kWh." \
  "/exit" | ./wiki chat 2>&1 | tee -a "$LOG"

# 6. The four ask-mode tests (standalone; Test 4 also checks that the chat-only claim
#    above is NOT used as evidence).
run /usr/bin/time -p ./wiki ask "What kind of pilot projects would reduce customer adoption risk for General Alpha?" --save test1-direct
run /usr/bin/time -p ./wiki ask "Why shouldn't General Alpha go after hospitals and data centers as its first customers?" --save test2-paraphrased
run /usr/bin/time -p ./wiki ask "Which customer segments does the DTCS project plan to interview, and does the digital twin meeting agree with that plan?" --save test3-two-sources
run /usr/bin/time -p ./wiki ask "What price per kWh did General Alpha quote to its pilot customers?" --save test4-unanswerable

run ollama ps
echo "" | tee -a "$LOG"
echo "# Finished — $(date '+%Y-%m-%d %H:%M:%S %Z')" | tee -a "$LOG"
