# N=12 compactified asymptotic common chart

Status: `COMMON_PHYSICAL_PRODUCT_NORM_AND_FIRST_LIFT_SCALE_DERIVED_CAPTURE_RADIUS_OPEN`.

The asymptotic and reset-side certificates must meet in one declared chart.
Use the retained pole-regular coefficient ordering and the existing
seven-dimensional `C2` phase topology:

`H6_coordinates x H5_velocities x H6_multipliers`.

For a coefficient of frequency `omega`, the squared weights are respectively
`(1+omega^2)^6`, `(1+omega^2)^5`, and `(1+omega^2)^6`.  The physical
weight-seven coordinate quotient is ordered as

`(q0_tilde,w_0,...,w_11,b_0,...,b_11)`,

where `q0_tilde` is the common-scale modulation after subtracting the round
expanding scale represented by `epsilon=R4^-2`.  This is a recentering, not a
gauge quotient; the common-scale modulation remains physical in the full
action.  Velocities use the same 25-component ordering, and the 24 retained
lapse/shift coefficients keep their existing ordering.

The directed Arb certificate supplies the complete first lower-weight lift
`X5` in these 74 variables.  Applying the exact squared Sobolev weights to
its component balls gives a rigorous product-norm interval

`C_X5_lower <= ||X5||_prod <= C_X5_upper`.

The value is of order `5.68e13`, dominated by high-frequency shape
coefficients.  Therefore even the certified first-order displacement
`epsilon X5` cannot be called small in this topology merely because
`epsilon<1`.

For any future action-owned admissible chart radius `rho_star`, the exact
first-lift necessary bound is

`epsilon <= rho_star/C_X5_upper`,

or equivalently

`R4 >= sqrt(C_X5_upper/rho_star)`.

This is a symbolic conversion law, not a fitted capture threshold.  No value
of `rho_star` is selected here.  A quantitative capture theorem must derive
`rho_star` from uniform lower bounds for the reduced kinetic/constraint
blocks and all physical domain margins, together with a remainder bound that
fits inside the unused part of that same product ball.

The tiny reset Calderon radius cannot be inserted for `rho_star`: it is
centered at the reset root in a different chart.  Gate 7 remains active.
