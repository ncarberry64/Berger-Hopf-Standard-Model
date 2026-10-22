# Independent product contract test receipt

**Result: 36 tests passed** in the final replay (0.89 seconds). Tests exercise the public `load_dataset`, `predict`, and `fit` interface without editing the root implementation.

The baseline fixture is a synthetic 10-solar-mass Galactic lens with z_l=z_s=0, seven irregular epochs, nonzero observer proper motion, free source positions and a supplied dense covariance. Its physical angular/time predictions are constructed independently from the nominal solar mass parameter, exact c and the parsec conversion; implementation lens helpers and unit constants are not imported.

Validated contracts: independent six-observable point-lens physics; angular translation and reference-epoch invariance; joint epoch/observation/source/covariance permutation; dense full-covariance whitening; file/dict equivalence and input immutability; dataset/forward-domain/family rejection; and reported fit chi2 against an independent full covariance solve. Negative controls first establish that their unmodified fixture is admitted, preventing an unrelated failure from masking every admission check.

Three additional frozen regressions pass: noiseless stellar-mass inference when the numerical reference mass is omitted; the same inference when it is deliberately set to 10^5 solar masses; and downgrade from an unqualified TRACKED status at an active, explicitly declared physical mass bound. The exact baseline recovery criteria were fixed before evaluating the correction: relative mass error <=10^(-5), chi2<10^(-6). They are numerical regression criteria, not uncertainty calibration.

The first replay preserved a real loader failure: equal zero Galactic redshifts were rejected (five positive tests failed; the initial 28 negative passes were masked). The loader was corrected and the baseline-validity controls strengthened. A development diagnostic also exposed a normalization-dependent mass lower bound: deleting the reference-mass field forced the 10-solar-mass fixture to 1831.56 solar masses and rejected the fit. The corrected implementation uses explicit physical mass bounds and no longer mistakes numerical normalization for a hidden mass prior. No physical R1 amplitude or preexisting tolerance was changed.

This receipt establishes interface, ordinary-lens, noise-objective and specific inference-regression behavior. It does not certify repeated-noise interval coverage, global nonlinear uniqueness, optional R1 inference, horizon identification, a real object, or observing capability. The wider preregistered matrix remains in `product_validation_protocol.md`.

## Replay metadata

Python 3.14.3; NumPy 2.4.6; SciPy 1.17.1; pytest 9.0.3.

Run from the worktree product directory: `python -m pytest tests/test_inference_contract.py -q --tb=short`.

| File | SHA-256 at replay |
|---|---|
| `product/tests/test_inference_contract.py` | `82fb1914151351df49abdbbe73aaee2e126f76ff4fed2875bedb72a4b5a7e4d4` |
| `product/bhtracker/data.py` | `832b6c210cf4eb4f18383ff7a3f47a12e6e7d9c87a767488e5db31affd633d04` |
| `product/bhtracker/forward.py` | `1360f559dea673b4557e6f0eac444a4e7ef0c1738fa4f2796da8b4ae8ffe1d98` |
| `product/bhtracker/inference.py` | `e231c91a95a82a469e57c22f3670eabfb8b0840321cc7196182d2cfe867101f0` |

A replay after public physical-admission enforcement also passed all 36 tests (0.96 seconds). Its code hashes are retained separately in the JSON receipt under `latest_replay_after_public_physics_admission`; the original replay metadata above remains preserved.
