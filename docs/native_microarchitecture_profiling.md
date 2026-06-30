# Native Microarchitecture Profiling

Status: `PROFILING_HARNESS_READY_COUNTERS_NOT_COLLECTED`.

The native C++ harness isolates two coordinate kernels over the checksum-gated
CMS dimuon four-vectors:

- `angular`: cylindrical/spherical reconstruction with transcendental functions;
- `direct`: Cartesian radius and unit-direction mapping.

Run on Linux:

```bash
./scripts/run_native_perf_profile.sh
```

The orchestrator requests cycles, instructions, IPC inputs, branch misses,
cache misses, L1 data-cache load misses, and LLC load misses. It records
`PERF_COUNTERS_UNAVAILABLE_OR_PERMISSION_DENIED` when PMU access is unavailable.
No cache, IPC, branch-prediction, or stall explanation is claimed until counters
are collected on identified hardware. Python/NumPy benchmark timings are not a
substitute for native hardware counters.
