# BHSM N=3 second direct-residual JFNK v18.39

This calculation applies the measured `1e-6` direct exact-residual response
and the existing action-owned right-coordinate map to the square 376-variable
KKT proposal problem. It adds no equation, row scaling, or acceptance rule.

The resulting Krylov direction is invalidated as a Newton model: its response
scale inconsistency is `0.39322559803476`, GMRES does not converge in the
bounded cycle, and the relative linear residual is `0.87244719657199`.
Nevertheless, independent evaluation of its line states identifies an
eta-admissible physical candidate with exact norm `0.824262386198657`, a
reduction of `0.001688628048434`. That candidate is not promoted here; it
still requires a fresh complete-child and persistence evaluation.
