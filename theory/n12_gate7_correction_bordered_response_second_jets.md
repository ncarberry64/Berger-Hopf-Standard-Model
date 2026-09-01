# Gate-7 correction bordered-response second jets

Along the normalized signed ambient Green correction, the selected-line and
bordered systems are differentiated twice without forming an inverse:

`K x'' = rhs'' - K'' x - 2 K' x'`.

The center Hessian and directional third-action matrix come from the retained
96-point action.  The directional fourth-action matrix is analytic automatic
differentiation of the same action formula.  The complete selected-line,
bordered-response, and normalization second identities are checked by their
direct residuals on the selected quarter-step center.  No predictor
calibration from a different center participates in those proof checks.

This closes the second-derivative identity and its center composition.  It
does not promote JAX to retained interval authority.  The existing retained
`D4`--`D5` correction majorants have one free output leg; they are not silently
treated as the two-free-leg matrix bounds required here.  The outward theorem
must first certify those two-free-leg bounds and then compose them with the
branchwise selected-line and bordered-response radii.
