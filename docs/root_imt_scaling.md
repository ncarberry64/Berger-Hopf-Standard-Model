# ROOT Implicit-Multithreading Scaling

Status: `ROOT_IMT_SCALING_MEASURED_ENVIRONMENT_SPECIFIC`.

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

## Hosted-runner result

| Threads | Median seconds | Entries/s | Speedup | Efficiency | Checksum |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 0.021603 | 23,145,121 | 1.000x | 100.0% | pass |
| 2 | 0.022977 | 21,761,003 | 0.940x | 47.0% | pass |

Two threads did not improve this 500,000-entry pure-map workload on the shared
Azure runner. The result indicates that scheduling overhead dominates at this
scale; it is not evidence for favorable scaling on larger nodes.
