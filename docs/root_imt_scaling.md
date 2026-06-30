# ROOT Implicit-Multithreading Scaling

Status: `ROOT_IMT_HARNESS_READY_CI_SCAN_PENDING`.

The harness calls `ROOT::EnableImplicitMT(N)` before constructing each
`RDataFrame`. Every thread count runs in a separate process, preventing ROOT
thread-pool state from leaking between measurements. Pure column definitions
map exact Pythagorean vectors, and every row must reproduce the expected radius
checksum.

The CI scan covers one and two threads because GitHub-hosted runners expose a
small shared VM. Use the same orchestrator on allocated hardware for:

```text
1, 2, 4, 8, 16, 32, 64 threads
```

Reported metrics are throughput, speedup versus one thread, parallel
efficiency, latency, and checksum status. A two-core hosted result is not a
claim of linear cluster scaling, absence of all races, or production detector
readiness.
