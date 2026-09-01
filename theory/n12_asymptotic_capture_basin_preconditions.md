# N=12 asymptotic capture-basin preconditions

Status: `LINEAR_DESCRIPTOR_AND_ONE_ANALYTIC_BRANCH_DO_NOT_PROVE_AN_OPEN_CAPTURE_BASIN`.

The certified weight-seven descriptor is the exact action **two-jet** at the
round expanding balance.  It proves 25 physical center roots, 25 stable roots
at `-7 H0`, no unstable finite root, and 24 algebraic modes.  The source
helper explicitly says that this two-jet is not a nonlinear truncation of the
retained action away from the background.

The full retained asymptotic theorem proves one analytic invariant graph

`Z(epsilon)=epsilon X5+epsilon^2 R(epsilon)`

with `epsilon=R4^-2` and `H4 -> H0>0`.  This is an existence theorem for one
local mathematical exterior branch.  It is not a neighborhood theorem and
does not show that nearby initial data, much less any AE2 reset data, approach
that graph.

After constraint and gauge reduction, the information presently certified
only fixes the linear part of the leading-weight center equations:

`a'=v`,

`v'=-7 H0 v + N7(a,v) + epsilon F(a,v,epsilon)`,

where `N7(0,0)=0` and `D N7(0,0)=0`.  The two-jet does not prove
`N7(a,v)=0`, does not prove `N7(a,0)=0`, and does not supply a trapping
estimate.  A cubic leading-weight action term is invisible to the action
two-jet while contributing a quadratic term to `N7`; therefore analyticity,
the nonresonant Briot--Bouquet recurrence, and absence of linear unstable
roots cannot remove this logical gap.

An open finite-N12 capture basin requires one of the following equivalent
forms of new action-owned control:

1. extract the exact constraint-reduced nonlinear weight-seven vector field
   and prove that its center set is an invariant normally attracting
   manifold with `H4` uniformly positive nearby; or
2. derive a Lyapunov/trapping inequality controlling the complete
   leading-weight nonlinear remainder and then absorb the positive powers of
   `epsilon`.

At minimum the proof must certify the constraint implicit-function domain,
the identity or bound replacing `N7(a,0)=0`, a uniform stable-normal estimate,
and a positive expansion/domain margin.  Only after that may quantitative
majorants define a capture surface for a reset-to-exterior connection proof.

This audit preserves the existing analytic branch and its branchwise
`H4 -> H0>0` result.  It withdraws no certified eigenvalue and adds no action
term, selector, endpoint, recurrence assumption, scale, fit, or chord.  It
prevents the branch theorem from being promoted to an open basin.  Gate 7
remains active at the nonlinear leading-weight basin-or-direct-connection
owner; Gate 8 remains locked.
