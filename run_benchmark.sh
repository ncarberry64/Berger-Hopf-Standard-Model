#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python3}"
EVENTS="${BHSM_BENCHMARK_EVENTS:-1000000}"
REPEATS="${BHSM_BENCHMARK_REPEATS:-3}"

cd "$ROOT_DIR"
if ! "$PYTHON_BIN" -c "import numpy, matplotlib" >/dev/null 2>&1; then
  "$PYTHON_BIN" -m pip install -e ".[benchmark]"
fi

exec "$PYTHON_BIN" -m bhsm.interface.benchmarks.coordinate_benchmark \
  --events "$EVENTS" \
  --boundary-fraction 0.35 \
  --repeats "$REPEATS" \
  --output tmp/coordinate_benchmark/results.json \
  --markdown tmp/coordinate_benchmark/results.md \
  --plot tmp/coordinate_benchmark/latency.png \
  --summary
