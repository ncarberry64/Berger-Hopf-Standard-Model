# Neutral Action Stiffness

The normalized spectral action requires distinct coefficients

```text
Z_nu               neutral kinetic stiffness,
A_nu_gap           neutral curvature-penalty stiffness,
ell_nu=sqrt(A_nu_gap/Z_nu).
```

`A_nu_gap` is not the open Robin coefficient historically denoted `A_nu`.
Scalar `lambda` supplies an action analogue, not the neutral coefficient.
Both coefficients are symbolic and open; no numeric ratio with dimension
`L^2` and no stiffness length in metres is derived. Status:
`OPEN_MISSING_NUMERIC_STIFFNESS_LENGTH`.

Physical eV/GeV neutrino mass closure requires a numeric neutral stiffness length sqrt(A_nu/Z_nu) and a physical K_neutral,eff map in m^-2.

