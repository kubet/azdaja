#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 bench/fixtures/generate.py
mkdir -p bench/results
BIN=${BIN:-target/release/azdaja}
QUERY="The file contains exactly six incident blocks headed === INC-N ===; only each block's FINDING line carries diagnostic evidence and all other lines are filler. Using at least one and at most two llm() calls total, classify each of INC-101 through INC-106 as exactly credential expiry, network saturation, or storage exhaustion. Return the exact mapping ID -> category and the three counts."
NATIVE_QUERY="Read $PWD/bench/fixtures/semantic-incidents.txt. It contains exactly six blocks headed === INC-N ===; only FINDING lines matter. Classify INC-101 through INC-106 as credential expiry, network saturation, or storage exhaustion. Return exact mapping and counts."
{
  "$BIN" --version
  jcode --version
  prime-agent --version 2>&1 | tail -1
  sw_vers 2>/dev/null || uname -a
} > bench/results/e2e-versions.txt
/usr/bin/time -l jcode run --no-update --quiet --model claude-haiku-4-5 "$NATIVE_QUERY" >bench/results/jcode-native-semantic.txt 2>bench/results/jcode-native-semantic.time
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
/usr/bin/time -l env -u RLM_DEPTH AZDAJA_HOME="$T/state" "$BIN" solo "$QUERY" -f bench/fixtures/semantic-incidents.txt >bench/results/jcode-solo-semantic.txt 2>bench/results/jcode-solo-semantic.time
/usr/bin/time -l prime-agent --offline -p --mode json --cwd "$PWD" --no-session --provider openai-codex --model openai-codex/gpt-5.4 <<EOF >bench/results/prime-agent-semantic.jsonl 2>bench/results/prime-agent-semantic.time
$NATIVE_QUERY
EOF
python3 bench/score.py bench/results/jcode-native-semantic.txt
python3 bench/score.py bench/results/jcode-solo-semantic.txt
python3 bench/score.py --prime-jsonl bench/results/prime-agent-semantic.jsonl
