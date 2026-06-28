# Neutral Stiffness Ratio

The normalized neutral action defines the stiffness length

```text
ell_nu = sqrt(A_nu/Z_nu).
```

The repository supports this object symbolically as
`CONDITIONAL_NEUTRAL_STIFFNESS_RATIO_CANDIDATE`. It does not contain a numeric,
action-derived value in metres. Scalar `lambda` is action-shape support, not a
silent substitution for the neutral ratio. Existing Robin-coefficient uses of
`A_nu` are not identified with the curvature-penalty coefficient.

A physical eV/GeV neutrino mass requires a numeric neutral stiffness length and a physical neutral curvature map.

