# N12 maximal forward-adjoint exhaustion

Status: `INFINITE_MAXIMAL_ADJOINT_EXHAUSTION_CRITERION_DERIVED_ACTUAL_WEIGHTED_LOAD_OPEN`.

Let `Y_xi(tau)` be one action-owned maximal child history and let
`U_xi(t,s)` be the evolution family of the constraint-reduced first Jacobi
equation along it.  After pulling the heat-minus-zeta operator cotangent
through the fixed-channel coefficient assembly, write the state-covector
density as `q_xi(t)`.  On a finite Dirichlet form-core exhaustion ending at
`T`, the zero-terminal adjoint gives

`p_T(0)=integral_0^T U_xi(t,0)^dagger q_xi(t) dt`.

This is exactly the same contraction as propagating every reset Jacobi
column, but it requires only one covector solve.  If

`integral_0^Tmax ||U_xi(t,0)|| ||q_xi(t)|| dt < infinity`,

then `p_T(0)` is Cauchy in the finite physical state dual and converges as the
form core exhausts the maximal Friedrichs interval.  For a reset tangent
`h`, with initial reset jet `B_reset h`, the infinite-route force is

`F(h)=<B_reset^dagger p(0)+q_direct,h>`.

Exact time invariance makes this covector basic on the retained whole-system
time orbit, so the existing intrinsic quotient theorem applies after the
limit.  No explicit noncompact matrix `D_xi M_C` and no collection of all
reset-Jacobi columns is required.

The weighted integral is a sufficient absolute-convergence criterion, not an
assumption now inserted into BHSM.  It must be proved from the retained
history, the constraint-reduced Jacobi propagator, and the complete
heat-minus-zeta load.  The negative-resolvent Weyl exhaustion alone does not
imply it.  In the scalar example `U(t,0)=1` and `q(t)=1`, every finite adjoint
exists but `p_T(0)=T` diverges.  Conversely, for
`U(t,0)=exp(-alpha t)` and `q(t)=exp(-beta t)` with
`alpha+beta>0`,

`p_T(0)=(1-exp(-(alpha+beta)T))/(alpha+beta)`

converges to `1/(alpha+beta)`.

On a finite later-event or canonical-stop stratum, the interval is finite and
the already-derived moving-endpoint adjoint theorem applies directly, so no
infinite-horizon condition is needed.  On an infinite route, the remaining
action theorem is precisely a weighted bound for the full state propagator
against the source-measure operator cotangent and the direct zeta load.  The
existing finite-N12 NHIM theorem could supply its asymptotic half only after
a reset-to-basin connection and quantitative tangent bounds; neither is
promoted here.

No selector, endpoint, terminal return, contour, scale, fit, recurrence,
gate, or chord is added.  Gate 7 remains active and Gate 8 remains locked.
