# BHSM Dimensionful Neutrino Mass Candidate

The preferred route is `m_nu=(hbar/c)sqrt(A_nu/Z_nu)K_neutral,eff`. The
historical gravitational expression is not used as a particle-mass formula.

Status: `DIMENSIONFUL_MASS_NOT_AVAILABLE`.

The evaluator requires all of the following before it can produce a mass:

1. numerical `r_prop` in metres;
2. numerical `k_neutral,eff` in `m^-2`;
3. physical stiffness and transport normalization;
4. a mass functional whose dimensions reduce to mass.

Current BHSM artifacts satisfy none of the numerical gates, and the legacy
`r^2 k` formula fails the fourth gate under its own definition of curvature.
Consequently all kg, eV, and GeV fields remain null. This is an obstruction
report, not a zero-neutrino-mass prediction.
