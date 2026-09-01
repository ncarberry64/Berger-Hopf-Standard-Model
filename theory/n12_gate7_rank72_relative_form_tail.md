# Gate-7 rank-72 source-contracted relative-form tail

Status: `RANK72_SOURCE_CONTRACTED_RELATIVE_FORM_CRITERION_SHARP_ACTUAL_TAIL_OPEN`.

Let `B : R^72 -> R^98` be the certified outgoing C2 seed-image basis and
let `U(t,0)` be the constraint-reduced Jacobi evolution on the unique
action-owned maximal child history.  For a finite Friedrichs core ending at
`T`, write the complete closed-system replacement covector as

`g_T = B^dagger p_T(0) + d_T`,

where

`p_T(0) = integral_0^T U(t,0)^dagger q_rep(t) dt`

and `d_T` is the already-owned direct replacement increment.  The exact
tail identity is

`g_T-g_S = integral_S^T (U(t,0)B)^dagger q_rep(t) dt + d_T-d_S`.

Thus Gate 7 does not require convergence of the ambient 98-state adjoint, an
ambient operator norm for `U`, or 72 separately promoted forward histories.
It requires exactly this 72-vector net to be Cauchy.  This statement is
necessary and sufficient because the target is finite dimensional.

There is an equivalent heat-smoothed relative-form statement.  For every
retained positive joint channel operator `P_ck`, put

`Q_ck^+ = (1/2) exp(-ell_kappa^2 P_ck) P_ck^-1`.

If `b_j` is a column of `B`, the heat part of the source-contracted density is

`rho_j^heat(t) = sum_(c,k) w_ck Re Tr[(Q_ck^+)^dagger`
`                                  D P_ck(t)[U(t,0)b_j]]`.

The zeta part is the direct action derivative of
`(59/30) integral d_tau/R4`, evaluated on the same propagated seed, and all
incoming/interface terms are included once in `d_T`.  A sufficient projected
trace-ideal estimate is

`integral ||rho^heat(t)-rho^zeta(t)||_2 dt < infinity`

together with Cauchy convergence of `d_T`.  Equivalently, the integrand may
be majorized by the sum over channels of the Euclidean norm, in `j`, of the
trace norms

`||(Q_ck^+)^(1/2) D P_ck[U b_j] (Q_ck^+)^(1/2)||_1`.

This is strictly weaker than the old ambient estimate
`integral ||U|| ||q_rep||`: it tests only reset-generated directions after
heat smoothing and retains signed action cancellations until the final
72-vector is formed.  It is also stronger than fixed-channel source-Dini or
finite-core trace class, neither of which controls the temporal Jacobi tail.

The later moving-duration Ward theorem supersedes one stale obligation in
the earlier infinite-route ledger.  On the genuine simultaneous
common-scale variation, `d_tau/R4` is invariant on every core, so the zeta
component is identically zero and is automatically Cauchy.  A separate
common-scale optical integral is therefore not required.  This does not
remove a seed-image dimension: the pure common-scale generator has not been
proved to be a member of `range(B)`, and the common-scale heat contraction is
the generally nonzero graded heat trace.  Every non-scale zeta component and
the full graded heat relative-form tail remain in the joint covector.

The tracked 1,222-core data provide only a finite prefix.  The Ward/BRST
ledger leaves a nonzero physical heat coefficient, the principal gauge slice
is not a global state quotient, and the certified `E0 -> C1 ->[T>0] E1 -> C2`
interface does not terminate the outgoing C2 arm.  No tracked theorem bounds
the displayed rank-72 relative-form density on the maximal tail.  The valid
completion alternatives are therefore an action-owned estimate of this
specific density or a genuine finite later event/canonical stop for C2.

Only the external Cauchy/birth datum is zero.  No internal response is
zeroed, no determinant is counted twice, and no selector, endpoint,
recurrence condition, scale, fit, gate, or chord is introduced.
