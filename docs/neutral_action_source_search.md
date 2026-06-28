# Neutral Action Source Search

The repository contains a partial neutral action chain:

```text
S_neutral_prop[Psi_nu,U_nu,R_curv] over dmu_boundary dt,
S_partial^(nu)=int [1/2 chi_nu^{AB}D_A Phi D_B Phi
                    +lambda_nu Phi n.grad Phi] dA,
dV_collar=J(Y,rho)dA d rho.
```

The boundary variation and standard collar-Jacobian formula are conditionally
derived. The complete normalized neutral action is not present: `chi_nu`,
`lambda_nu`, the support metric and measure, collar orientation/edge data,
profile/embedding, and physical units remain open. Status:
`OPEN_MISSING_NEUTRAL_ACTION_NORMALIZATION`.

BHSM does not use neutrino limits, PDG values, W calibration, empirical fitting, or legacy particle threshold tables to set the neutral action scale.

