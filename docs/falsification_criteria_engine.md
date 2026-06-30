# Engine Falsification Criteria

| claim_id | claim | current_status | what_would_falsify_it |
| --- | --- | --- | --- |
| ENG-01 | CERN open-data four-vector accuracy | ARTIFACT_BACKED | scale-aware error exceeds declared bound |
| ENG-02 | SIMD/control speedup | ENVIRONMENT_SPECIFIC | independent matched implementation is not faster |
| ENG-03 | ROOT implicit multithreading scaling | NEGATIVE_HOSTED_RESULT | no scaling or regression; current 2-thread run is 0.940x |
| ENG-04 | Native PMU explanation | RUNTIME_GATED | PMU counters contradict proposed mechanism |
| ENG-05 | Lorentz invariant preservation | ARTIFACT_BACKED | declared backward-error gate fails |
| ENG-06 | Round-trip coordinate transformation | ARTIFACT_BACKED | inverse fails scale-aware tolerance |
