#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/.."
DEST="data/loghub2k"
mkdir -p "$DEST"

SYSTEMS=(Android Apache BGL Hadoop HDFS HPC HealthApp Linux Mac OpenSSH OpenStack Proxifier Spark Thunderbird Windows Zookeeper)
BASE="https://raw.githubusercontent.com/logpai/loghub/master"

for S in "${SYSTEMS[@]}"; do
  for F in "${S}_2k.log" "${S}_2k.log_structured.csv" "${S}_2k.log_templates.csv"; do
    if [ -f "$DEST/$F" ]; then continue; fi
    url="$BASE/$S/$F"
    if curl -fsSL --max-time 60 -o "$DEST/$F" "$url"; then
      echo "ok   $F"
    else
      echo "miss $F (skipped)"
    fi
  done
done
echo "Loghub-2k in $DEST/"