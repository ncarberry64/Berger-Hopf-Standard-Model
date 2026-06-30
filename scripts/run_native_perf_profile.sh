#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python -m bhsm.interface.benchmarks.cern_open_data_benchmark \
  --download --repeats 1 --replication-factor 1 \
  --output tmp/native-profile/source-check.json \
  --markdown tmp/native-profile/source-check.md

cmake -S . -B build/native-profile \
  -DBUILD_NATIVE_BENCHMARK=ON \
  -DBUILD_ROOT_INTEGRATION=OFF \
  -DENABLE_AVX2="${ENABLE_AVX2:-OFF}" \
  -DENABLE_AVX512="${ENABLE_AVX512:-OFF}" \
  -DCMAKE_BUILD_TYPE=Release
cmake --build build/native-profile --config Release --parallel

python tools/run_linux_perf_profile.py \
  --executable build/native-profile/bhsm_native_coordinate_benchmark \
  --data data/external/cern_open_data/dimuon.csv \
  --output artifacts/runtime/native_microarchitecture_profile.json
