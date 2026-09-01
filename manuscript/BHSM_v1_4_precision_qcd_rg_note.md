# BHSM v1.4 Precision-Oriented QCD/RG Matching Note

BHSM v1.4 upgrades the quark-mass comparison architecture without changing
the frozen BHSM predictions.

The framework includes:

- `MIXED_DEFAULT`: current mixed scheme/scale reference baseline;
- `COMMON_SCALE_APPROX`: one-loop-inspired common-scale scaffold;
- `THRESHOLD_AWARE_APPROX`: piecewise-threshold approximate scaffold;
- `PDG_STYLE_REFERENCE_PLACEHOLDER`: metadata shell for future verified inputs;
- `PRECISION_QCD_PLACEHOLDER`: metadata shell for future two-/three-loop
  threshold-matched QCD inputs.

The compared BHSM quantities are:

```text
c/t, u/t, s/b, d/b
```

plus the dressed-candidate branch value for:

```text
Z_virt^{u,2}=1/2 applied only to c/t.
```

The approximate scheme-consistent rows can identify scaffold-level tensions,
but they are not final precision QCD verdicts. A real BHSM tension is declared
only for a final scheme-consistent reference set with implemented uncertainties
and fixed tolerance scoring. No such final precision reference set is supplied
in this phase.

This phase does not tune `a`, `S`, the mode ledger, tolerances, or virtual
dressing. It does not adopt new dressing factors and does not claim precision
quark matching is solved.
