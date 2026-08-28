# Gate-7 correction bordered-response second jets

Along the normalized signed ambient Green correction, the selected-line and
bordered systems are differentiated twice without forming an inverse:

`K x'' = rhs'' - K'' x - 2 K' x'`.

The center Hessian and directional third-action matrix come from the retained
96-point action.  The directional fourth-action matrix is analytic automatic
differentiation of the same action formula, and the completely assembled
normalized field second derivative is cross-checked against an independent
twice-differentiated calibrated field evaluation.

The comparison is between the retained center jet and the separately
center-calibrated JAX realization.  Relative first- and second-jet residuals
are therefore reported in addition to the differentiated identity residuals;
they are cross-realization checks, not interval error bounds.

This closes the second-derivative identity and its center composition.  It
does not promote JAX to retained interval authority.  The existing retained
`D4`--`D5` correction majorants have one free output leg; they are not silently
treated as the two-free-leg matrix bounds required here.  The outward theorem
must first certify those two-free-leg bounds and then compose them with the
branchwise selected-line and bordered-response radii.
