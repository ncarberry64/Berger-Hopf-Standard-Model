# N12 C2 reset-launch adjoint interface

Status: `C2_RESET_LAUNCH_ADJOINT_AND_FIXED_SEED_SEAM_SPLIT_DERIVED`.

Let `Z : R^139 -> ker J_R` be the action-normalized reset-tangent basis and
let `B=P_C2 Z : R^139 -> R^98` be its projection to the outgoing C2 seed after
the certified forward swap.  The launch theorem gives

`rank B=72`, `dim ker B=67`.

For any downstream C2 state covector `p_0`, its reset-tangent pullback is

`g_C2=B^dagger p_0`.

Consequently `K^dagger g_C2=0` for every coordinate basis
`K : R^67 -> ker B`.  No amount of later C2 propagation can generate or
cancel force on those fixed-C2-seed lift directions.

Let `d_upstream_interface` be all force dependence not propagated through the
outgoing C2 seed.  The fixed-seed ownership audit identifies it as the
complete upstream-history plus retained-interface covector on the
196-dimensional event-child product.  The full restricted force is

`g_total=Z^dagger d_upstream_interface+B^dagger p_0`,

and its exact fixed-seed-kernel condition is therefore

`K^dagger g_total=(ZK)^dagger d_upstream_interface=0`.

This is a compatibility equation for the already-retained full upstream
history and interface data.  It does not assert that it vanishes, reduce to a
new local seam action, or replace the missing action evaluation.

On the outgoing image, choose an orthonormal basis `Q` and write the exact
fixed-`s` field as `F_0=Q a+beta n`, with `n` the unit transverse direction
and `beta>0`.  The natural launch map and its force pullback are

`B_launch=[Q,F_0]`,

`g_launch=B_launch^dagger p_0=(Q^dagger p_0,<F_0,p_0>)`.

The coordinate change from `(xi,delta s)` to the orthonormal chart is
triangular with final diagonal entry `beta`, hence invertible.  This proves
that a scalar Gate-7 force requires one downstream adjoint covector, not 73
forward Jacobi columns.  The actual maximal/finite-endpoint adjoint `p_0` and
the actual upstream/interface covector remain the two unevaluated algebraic
blocks of one action-owned joint-history adjoint.

No reset member, endpoint, force value, scale, recurrence, gate, or chord is
introduced.
