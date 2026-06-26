# Mass-Width Scheme Candidate

Phase Three-E exports
`artifacts/BHSM_mass_width_scheme_candidate_v0_7.json`.

## Current Status

```text
mass_scheme_status = STRUCTURAL_CANDIDATE
width_scheme_status = BLOCKED_BY_MISSING_THEOREM
fermion_mass_status = BLOCKED_BY_MISSING_THEOREM
gauge_boson_mass_status = BLOCKED_BY_MISSING_THEOREM
neutrino_mass_status = BLOCKED_BY_MISSING_THEOREM
decay_width_status = BLOCKED_BY_MISSING_THEOREM
feynrules_ready = false
ufo_ready = false
```

The ledger preserves the internal BHSM profile curvature source
`kappa_H = 64*pi^5`. This is a BHSM profile Hessian curvature, not
automatically a collider Higgs mass.

No PDG masses and no fake decay widths are inserted.

## Phase Three-F Follow-On

Phase Three-F defines a runtime mass-width policy. `BHSM_PURE_NOFIT` still does
not import external masses or widths. `BHSM_COLLIDER_INTERFACE` may accept
runtime mass/width cards for simulation and comparison only, and those runtime
inputs do not modify BHSM constants, boundary coefficients, mixing matrices, or
frozen predictions.
