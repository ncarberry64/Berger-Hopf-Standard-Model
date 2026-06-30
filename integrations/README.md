# BHSM Integrations

| Integration | Purpose | Status |
| --- | --- | --- |
| [CERN ROOT](cern-root/README.md) | Header-only coordinate utility and PyROOT `RDataFrame` wrapper | `OPTIONAL_ROOT_ADAPTER_NOT_RUNTIME_VALIDATED_IN_REPOSITORY_CI` |
| [Benchmark container](benchmark/README.md) | Reproducible containerized synthetic coordinate microbenchmark | `AVAILABLE` |

These adapters do not change frozen predictions or official BHSM model logic.
ROOT, Geant4, detector tracking, and institutional experiment validation remain
external runtime concerns.
