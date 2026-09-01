# N12 C2 full-action eigenline ball at the tracked 1,221 edge

The cancelled flow requires simplicity of the retained branch-24 selected
line, but it does not require positivity of the old fixed-descriptor cubic or
of `Delta`.  A new ambient retained-action ball is therefore centered at the
fully tracked 1,221 endpoint and evaluated with the full-local-action Hessian.

On the action-coordinate ball of radius `1e-8`:

- the hard-complement relative perturbation is below `0.120`;
- the selected-line gap remains above `2.057e-7`;
- the fixed Schur implicit denominator remains positive;
- the eigenvector graph norm is below `3.28e-6`;
- the selected-line first and second variation bounds are finite.

The signed descriptor remains an independent interval coordinate.  The
binary64 selected eigenvalue is retained only as a line-identification
diagnostic and is not substituted into the near-birth flow.

This enlarges the rigorously available simple-line neighborhood by roughly
two orders of magnitude relative to the inherited endpoint tube.  It is not
yet a propagated history segment: the complete bordered response and
cancelled-field Lohner enclosure must be solved inside this larger ball.

