# Containerized Benchmark

```bash
docker build -f integrations/benchmark/Dockerfile -t bhsm-benchmark .
docker run --rm bhsm-benchmark
```

This executes the same synthetic microbenchmark as `run_benchmark.sh`. It does
not provide ROOT, Geant4, detector simulation, or production tracking.
