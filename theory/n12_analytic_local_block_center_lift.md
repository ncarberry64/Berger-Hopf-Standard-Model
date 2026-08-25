# N12 analytic local-block center lift

Status: `GENUINE_70_DIGIT_ANALYTIC_LOCAL_BLOCK_LIFT_CONVERGED_DIRECTED_INTERVAL_AND_UNIFORM_REMAINDER_OPEN`.

The generic precision audit is corrected: it used high-precision nodes and a
70-digit final solve, but its action-jet arithmetic ran at the then-default
15 digits. Its conservative nonpromotion decision was sound, but its rows are
superseded.

The replacement assembly differentiates the exact ten-variable local
weight-seven integrand and exact eight-variable local weight-five integrand,
then maps those small blocks to `q0+12w+12b` and the 24 lapse/shift
multipliers. All quadrature, trigonometry, block accumulation, and bordered
solving run inside one 70-digit context. No combined Euler--Dirac inverse is
formed.

An independent full 98-variable object-jet assembly now cross-checks the
analytic map at 48 Gauss nodes with the entire action integration and solve
inside an 80-digit context. Two binary64 leaks in the generic realization
were removed: coefficient vectors were being allocated as float arrays, and
the scalar subtraction in `a'=...-tan(chi)` passed through the legacy Jet's
`float()` coercion. After correcting those numerical-realization defects,
the generic and analytic matrices agree within `1.35e-79`, their sources
within `1.69e-80`, and their `X5_q0` values within `1.64e-69`. The generic
relative solve residual is `8.59e-81`. The earlier generic 48-node number is
therefore superseded as float-cast contaminated; no action term or physical
claim changed.

The 64-, 80-, 96-, and 128-node rows agree below `1e-40`:

`X5_q0=66.494327736840793193242388023117925357510087982407...`,

`(D_tau q0)_5=-51.963761962903932051564000772817373661146975456095...`.

This converges the represented coefficient reproducibly and establishes a
robust negative observed common-scale rate correction. A directed-rounding
interval wrapper is still required before promoting the sign as a rigorous
action theorem. A uniform nonlinear remainder theorem or existing
event/canonical-stop theorem is still required before selecting among the
full-history `H4` outcomes.

The infinite nonencapsulating branch remains mathematical and nonrealized;
the physical finite-history Calderon force remains a separate Gate-7 owner.

`FULL_BHSM_COMPLETE=false`.
