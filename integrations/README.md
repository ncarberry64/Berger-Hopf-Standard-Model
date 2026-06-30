# BHSM Integrations

| Integration | Purpose | Status |
| --- | --- | --- |
| [CERN ROOT](cern-root/README.md) | Header-only utility, PyROOT wrapper, and pinned-container C++ smoke test | `ROOT_ADAPTER_LIVE_COMPILED_IN_CI_NOT_PRODUCTION_VALIDATED` |
| [Benchmark container](benchmark/README.md) | Reproducible containerized synthetic coordinate microbenchmark | `AVAILABLE` |

These adapters do not change frozen predictions or official BHSM model logic.
ROOT, Geant4, detector tracking, and institutional experiment validation remain
external runtime concerns.
