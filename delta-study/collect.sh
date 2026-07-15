#!/bin/bash
# Stage 1 — collect paired outputs from both models.
# For each prompt x model x replicate, save outputs/raw/<id>__<model>__<rep>.txt
# Idempotent: skips files that already exist and are non-empty and non-error.
#
# Env:
#   N        replicates per (prompt,model)   default 3
#   PAR      parallel jobs                    default 4
#   MODELS   space-separated model ids        default the two under study
#   IDS      space-separated prompt ids       default: all in manifest
set -u
cd "$(dirname "$0")"

N="${N:-3}"
PAR="${PAR:-4}"
MODELS="${MODELS:-claude-opus-4-8 claude-fable-5}"
DISALLOW="Bash,Write,Edit,NotebookEdit,WebFetch,WebSearch,Task,Glob,Grep,Read"
mkdir -p outputs/raw

if [ -z "${IDS:-}" ]; then
  IDS="$(cut -f1 manifest.tsv)"
fi

is_bad() {  # true if file missing/empty/known-null
  local f="$1"
  [ ! -s "$f" ] && return 0
  grep -qE "session limit|Self-signed certificate|Unable to connect to API" "$f" && return 0
  return 1
}

run_one() {
  local id="$1" model="$2" rep="$3"
  local out="outputs/raw/${id}__${model}__${rep}.txt"
  is_bad "$out" || return 0
  local prompt; prompt="$(cat "prompts/${id}.txt")"
  timeout 300 claude --model "$model" -p "$prompt" --disallowedTools "$DISALLOW" \
    > "$out" 2> "${out}.err"
  if is_bad "$out"; then echo "NULL ${id}__${model}__${rep}"; else echo "ok   ${id}__${model}__${rep}"; fi
}
export -f run_one is_bad
export DISALLOW

# Build the job list, then run in parallel.
for id in $IDS; do
  for model in $MODELS; do
    for rep in $(seq 1 "$N"); do
      echo "$id $model $rep"
    done
  done
done | xargs -P "$PAR" -n 3 bash -c 'run_one "$0" "$1" "$2"'

echo "COLLECT DONE"
nulls=$(grep -rlE "session limit|Self-signed|Unable to connect" outputs/raw/*.txt 2>/dev/null | wc -l)
echo "remaining null/error files: $nulls (rerun collect.sh to retry just those)"
