# Gauge Fixing And Production Coupling Scheme

Phase Three-E exports
`artifacts/BHSM_gauge_fixing_production_coupling_scheme_v0_7.json`.

## Target Interface

```text
target_gauge_group = SU(3)c x SU(2)L x U(1)Y
canonical_vector_kinetic_terms = true
canonical_vector_kinetic_terms_status = STANDARD_HEP_TARGET_CONVENTION
gauge_fixing_status = OPEN_OR_TARGET_CONVENTION_ONLY
production_coupling_status = SCHEME_CONDITIONAL
```

The candidate couplings `g1_BH_candidate`, `g2_BH_candidate`, and
`g3_BH_candidate` are read from existing BHSM parameter-card artifacts and
remain scheme-conditional. They require a reference scale, normalization
convention, threshold/running scheme, renormalization scheme, gauge fixing
convention, and validated production parameter card before production use.

No final UFO production coupling scheme is claimed.

## Phase Three-F Follow-On

Phase Three-F adds a production coupling map using
`G_prod = G_raw / product_a sqrt(Z_a)`. In the canonical production basis
`Z_a = 1`, so `G_prod = G_raw` only where Lorentz attachment, gauge
representation, coupling scheme, mass-width requirements, and renormalization
requirements are satisfied.
