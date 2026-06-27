# Neutral Curvature Mapping

The current BHSM kernel provides the dimensionless response

```text
R_nu_dimless(psi,p)
  = max(0, p g_nu ||K_nu psi||/||psi|| - kappa_nu).
```

This establishes a positive-threshold response, not a curvature in `m^-2`.
No local artifact fixes the conversion from one dimensionless response unit to
`k_neutral,eff`. The physical mapping therefore remains
`OPEN_MISSING_NEUTRAL_CURVATURE_MAPPING`.

A physical BHSM neutrino mass requires both a propagation/localization scale and a neutral curvature mapping with physical units.

