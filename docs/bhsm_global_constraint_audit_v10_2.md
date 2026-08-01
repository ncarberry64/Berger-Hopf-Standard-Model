# BHSM v10.2 Global Constraint Audit

## Result

`BHSM_NO_ACTION_DERIVED_GLOBAL_BUOYANCY_RESTORING_CONSTRAINT`

The lapse variation supplies the parent constraint

\[
\mathcal C_H
=\frac12\{\kappa_1(R_7-H^TGH)-\kappa_0\}-\rho=0,
\]

with propagation `D_t C_H = -Theta C_H`. This is an action-derived local
constraint, not a positive scalar total energy and not a law relating local
compactness to normal depth.

The audited candidates are:

- fixed eta degree: covariant and topological, but scale free;
- Hamiltonian constraint: derived and propagating, but not a restoring modulus;
- fixed total volume: covariant but absent and introduces `V_star`;
- fixed curvature integral: absent or redundant and introduces a target value;
- Brown--York closure: quasilocal and ensemble/reference dependent;
- normalized boundary measure: useful for finite operators, not a global
  geometry constraint.

No candidate is selected. In particular, fixed topology does not fix a radial
energy scale, and no coordinate-dependent integral of `T00` is introduced.
