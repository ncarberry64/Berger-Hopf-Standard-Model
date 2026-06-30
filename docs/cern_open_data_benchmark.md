# CERN Open Data Coordinate Benchmark

Status: `CERN_OPEN_DATA_FOUR_VECTOR_BENCHMARK_NOT_TRACK_RECONSTRUCTION`.

Source: [Events with two muons from 2010](https://opendata.cern.ch/record/303), DOI `10.7483/OPENDATA.CMS.4M97.3SQ9`.

Unique four-vectors: `200,000`; timed four-vectors per pass: `2,000,000`; replication factor: `10`.

> This benchmark uses published CMS collision-derived muon four-vectors. It tests coordinate
> transformation throughput, not track fitting, detector propagation, or reconstruction.

| Kernel | Median seconds | Four-vectors/s |
| --- | ---: | ---: |
| `branchy_cylindrical_scalar` | 2.307091 | 866,893 |
| `cylindrical_vectorized_control` | 0.181168 | 11,039,508 |
| `bhsm_boundary_vectorized` | 0.056168 | 35,607,463 |

## Measured deltas

- Direct map versus scalar control: `41.075x`.
- Direct map versus vectorized control: `3.225x`.
- Maximum absolute numerical delta: `5.821e-11`.
- Strict synthetic `rtol=atol=1e-12` check: `False`.
- Scale-aware 128-epsilon backward-error check: `True`.

## Scope

The source is a CC0 derived education dataset and is not suitable for a full physics analysis.
Neither CMS nor CERN endorses this benchmark. Frozen BHSM predictions are unchanged.
