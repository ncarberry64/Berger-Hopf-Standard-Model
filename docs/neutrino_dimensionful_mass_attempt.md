# BHSM Neutrino Dimensionful Mass Attempt

The v1.0 attempt applies the audited neutral scale law to each existing
dimensionless propagation-response channel. Because no valid unit source is
available, `effective_mass_eV` and `effective_mass_GeV` remain `null` for every
channel.

This is a deliberate fail-closed result, not a zero-mass prediction. The
dimensionless channel responses from v0.9 remain unchanged and conditional.

Status: `OPEN_MISSING_NEUTRAL_SCALE`.

The legacy extension records
`m_nu=(c^2/(2G))r_prop^2 k_neutral,eff` as a candidate bridge. The attempt still
returns null eV/GeV fields because `r_prop` and physical `k_neutral,eff` are
absent. Legacy particle tables are excluded from scale derivation.

The v1.2 candidate adds a mass-dimension gate and continues to emit null kg,
eV, and GeV fields. Numeric radius and curvature inputs would be necessary but
not sufficient until the legacy functional is corrected or derived with the
missing length normalization.
