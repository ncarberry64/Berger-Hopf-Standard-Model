# BHSM v6.30.3 fixed-action fold tangent and surface test

## Scope

This phase compares the merged fixed-\(h\) KKT kernel with the first
derivative used by the inherited Jordan-frame fold coefficient. All action
controls, the \([0,1]_t\times M_4\) domain, the \(M_4\) regulator, and the
independent curvature probe are fixed:

\[
{d\mu\over dq}=0,\qquad {dr\over dq}=0.
\]

No measured input, fit, neighboring-action potential, new source, or vacuum
subtraction is used.

## Exact first-tangent contradiction

The v6.30.2 fixed-\(h\) quotient kernel is

\[
\ker\mathbb L_D=\operatorname{span}\{(0,0,u_1,0)\}.
\]

Thus the normalized scalar amplitude has

\[
\Phi_1=(A_1,\psi_1,\sigma_1,\eta_1)=(0,0,u_1,0).
\]

For the common reduced density, the gravitational coefficient is

\[
F(q)=2\kappa_1\int_0^1N(q,t)a(q,t)^2dt+2C_\partial .
\]

Consequently,

\[
F_1=2\kappa_1\int_0^1
\left(N_1a_0^2+2N_0a_0a_1\right)dt=0
\]

on the fixed-action Jacobi tangent.

The historical nonzero result

\[
F_{1,\tau}=\tau{\chi_1(\pi-4)\over4}
\]

was evaluated on

\[
N_1=-\tau{\chi_1\over4},\qquad
a_1=\tau\chi_1\left({a_0\over4}
-{\sqrt2\,t\cos(\pi t/4)\over4}\right),
\qquad {dX\over dq}=\tau\chi_1 .
\]

It is therefore a curvature-varying affine tangent. It cannot be the
derivative of the fixed-\(h\), \(dr/dq=0\) family whose first vector is the
pure scalar kernel. The failed equation is already the order-one equation
\(\mathbb L_D\Phi_1=0\): one vector cannot simultaneously be the homogeneous
fixed-\(h\) kernel and the \(dX/dq\ne0\) sourced response.

This is not a contradiction in the frozen action. It is a contradiction in
identifying derivatives taken on two different variational domains.

## Radial Noether identity

Direct variation of the lapse-retained one-cap density gives the exact
identity

\[
a' E_a+\sigma' E_\sigma-N(E_N)'=0.
\]

It supplies a second implementation constraint. If both local metric and
lapse equations are imposed, a scalar-only reduced residual
\(E_\sigma=g(q)u_1\) is not admissible by itself: the identity gives
\(\sigma'g(q)u_1=0\). A constrained-amplitude construction must include the
metric and lapse variations of a covariant amplitude constraint. Dropping
those variations would violate the full constraint required by the
campaign.

## Surface-existence verdict

At \(q=0\), \(a_0(1)=1\). Hence the induced four-metric has rank four, its
determinant and volume measure are nonzero, and the matcher trace and KKT
boundary ranks do not change. The one-cap proper length is \(\pi/4\),
\(F_0=\pi/2>0\), \(k_E(0)=6.935084858283065>0\), and the boundary normal
curvature is finite with \(H_J=1\). The canonical distance behaves as
\(\sqrt{k_E(0)}|q|+O(q^2)\) and is finite.

Scalar reflection acts as \((q,\tau)\mapsto(-q,\tau)\). The label \(\tau\)
belongs to the historical curvature/orientation tangent and is not the sign
of the scalar Jacobi amplitude. The unoriented metric data coincide at
\(q=0\), while oriented labels remain distinct until a cap-exchange quotient
is chosen.

The unique surface verdict is

`BHSM_CRITICAL_FOLD_IS_REGULAR_SPACETIME_CONFIGURATION`.

Quadratic flatness is not used to reach this verdict.

## Gate decision

The fixed-action coefficient \(F_1=0\) and the historical
\(F_{1,\tau}\ne0\) cannot be inserted into one Taylor family. Therefore
\(\Phi_2\), separate \(F_2,V_2\), the common-family Hessian identity, and the
first nonzero Einstein interaction are not promoted here.

The primary result is

`BHSM_FIXED_ACTION_NONLINEAR_FOLD_FAMILY_BLOCKED_BY_INCOMPATIBLE_FIXED_H_AND_CURVATURE_VARYING_FIRST_TANGENTS`.

The local-stability result is

`BHSM_FOLD_LOCAL_STABILITY_BLOCKED_BY_INCOMPATIBLE_FIXED_H_AND_CURVATURE_VARYING_FIRST_TANGENTS`.

The v6.31 scale phase is not permitted. The smallest repair is not a new
coefficient: the campaign must choose one domain and rederive all
first-order frame and kinetic data on it.
