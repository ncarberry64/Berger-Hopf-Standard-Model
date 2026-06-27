# BHSM Neutral Threshold-to-Energy Map

The guarded target is

```text
m_eff[eV] = neutral_scale[eV] * dimensionless_response.
```

The dimensionless response and curvature threshold are executable. The local
artifacts do not supply `neutral_scale[eV]`, a normalized neutral background
energy density, or a transport normalization connecting the boundary action
to physical energy. The map therefore has status
`OPEN_MISSING_THRESHOLD_TO_ENERGY_MAP`.

No arbitrary conversion constant is inserted.

