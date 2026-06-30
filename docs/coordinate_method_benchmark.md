# Synthetic Coordinate-Method Benchmark

This benchmark compares three implementations of the same Cartesian-state
normalization task over a deterministic, boundary-heavy synthetic dataset:

1. scalar cylindrical/spherical mapping with explicit pole and seam branches;
2. a vectorized cylindrical/spherical control;
3. a BHSM-inspired direct vectorized boundary normalization.

Run one million events with:

```bash
python -m bhsm.interface.benchmarks.coordinate_benchmark --events 1000000 --repeats 3
```

The isolated workers regenerate the exact same dataset from a fixed seed.
Dataset generation and output hashing are outside the timed region. Each result
records median wall time, throughput, process peak RSS, output digest, and the
hardware-counter availability status.

## Interpretation

This is a Python/NumPy algorithmic microbenchmark. It is not a comparison with
Geant4, ACTS, CMSSW, Athena, detector simulation, magnetic-field propagation,
Kalman tracking, material interactions, or production HEP software. The scalar
comparison includes Python-loop versus vectorization effects. The vectorized
cylindrical control is the more relevant estimate of coordinate-formula cost.

The direct kernel is BHSM-inspired and is not the official frozen BHSM
prediction engine. A measured speedup does not establish physics accuracy or a
production HEP performance advantage.

Externally supplied benchmark numbers are not copied into the measured-results
artifact unless this deterministic runner reproduces them on the stated
platform and configuration.

On Linux, hardware branch counts should be collected independently with
`perf stat -e branches,branch-misses` around an isolated worker. On platforms
without those counters, the report leaves branch values null rather than
inferring them from latency.
