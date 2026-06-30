# Synthetic Coordinate-Method Benchmark

> This is a controlled Python/NumPy microbenchmark, not a comparison with Geant4, ACTS,
> CMSSW, Athena, production detector tracking, or validated HEP reconstruction software.

Events: `10,000,000`; boundary/edge events: `3,500,000`; seed: `1729`.

| Kernel | Median latency (s) | Events/s | Peak RSS (MiB) | Branch misses |
| --- | ---: | ---: | ---: | --- |
| `branchy_cylindrical_scalar` | 11.022200 | 907,260 | 1159.0 | not available |
| `cylindrical_vectorized_control` | 0.893868 | 11,187,328 | 1931.5 | not available |
| `bhsm_boundary_vectorized` | 0.281142 | 35,569,214 | 1617.0 | not available |

## Deltas

- Scalar branch-heavy baseline / BHSM-inspired direct map: `39.205x`.
- Vectorized cylindrical control / BHSM-inspired direct map: `3.179x`.
- Peak RSS reduction versus scalar baseline: `-39.5%` (negative means higher memory).
- Peak RSS reduction versus vectorized control: `16.3%`.

## Correctness

Maximum absolute delta versus scalar baseline: `1.066e-14`.
All kernels agree at `rtol=atol=1e-12`: `True`.

## Branch-counter status

`HARDWARE_COUNTERS_UNAVAILABLE_ON_WINDOWS`. Hardware branch-misprediction values are not inferred from timing.

## Interpretation boundary

- `SYNTHETIC_MICROBENCHMARK_NOT_PRODUCTION_HEP_VALIDATION`.
- `BHSM_INSPIRED_BOUNDARY_MAP_NOT_OFFICIAL_TRACKING_ENGINE`.
- The scalar speedup includes Python-loop versus NumPy-vectorization effects.
- The vectorized-control delta is the more relevant coordinate-formula comparison.
- No physics accuracy, detector efficiency, tracking quality, or production HEP speedup is claimed.
- Frozen BHSM predictions and official model logic are unchanged.
