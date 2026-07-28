# BHSM v6.28.0: reduced fold operator and radial domain

## Result and scope

This phase derives the local two-\(M_4\)-derivative quadratic operator pencil
on

\[
Y=(A,\psi,\delta\sigma_\perp)^T
\]

from the frozen P1+GHY+bulk-scalar+B1+matcher action. The v6.27 full momentum
constraint has already fixed the shift and endpoint response:

\[
W=0,\qquad B_q(t)=-\tau{\pi\chi_1\over16}t,\qquad
\mathcal S_{\Sigma,q}=-\tau{\pi\chi_1\over16}.
\]

No global Lorentzian propagator, measured input, fitted parameter, new action,
primitive, scale, boundary parameter, or pseudoinverse is introduced.

The four phase results are

- `BHSM_REDUCED_FOLD_OPERATOR_L0_L1_DERIVED`;
- `BHSM_REDUCED_FOLD_SOURCE_J0_J1_DERIVED`;
- `BHSM_REDUCED_FOLD_ADJOINT_DOMAIN_DERIVED`;
- `BHSM_REDUCED_FOLD_KERNEL_AND_COMPATIBILITY_DERIVED`.

The phase verdict is
`BHSM_REDUCED_FOLD_OPERATOR_AND_DOMAIN_CLOSED_CONDITIONALLY`.

## Frozen action and background

The relevant action is

\[
S_{\rm P1}={1\over2}\int_{M_5}\sqrt{|g|}
(\kappa_1R_5-\kappa_0),
\]

with one \(\kappa_1\int\sqrt{|h|}K\) GHY term on each reflected cap,

\[
S_\sigma=\int_{M_5}\sqrt{|g|}
\left[-{Z_5\over2}(\nabla\sigma)^2-U_5(\sigma)\right],
\]

one common intrinsic term

\[
S_{B1}=C_\partial\int_{B1}\sqrt{|h|}R_4,
\]

and the exact metric matcher. At the critical representative,

\[
N_0={\pi\over4},\qquad
a_0(t)=\sqrt2\sin{\pi t\over4},\qquad
X_c=2,\qquad \sigma_0=0,
\]
\[
\kappa_0=12\kappa_1.
\]

The exact identities

\[
H_\rho^2-{X_c\over a_0^2}=-1,\qquad
{a_{0,tt}\over N_0^2a_0}=-1,\qquad H_\rho(1)=1
\]

are verified symbolically. The two-cap radial weight is expressed using the
common per-cap pairing

\[
w(t)\,dt=N_0a_0^4dt
=\pi\sin^4{\pi t\over4}\,dt.
\]

The factor two from the reflected caps appears in every bulk quadratic
coefficient below.

## Complete quadratic density

Use

\[
N=N_0(1+A),\qquad
\gamma_{\mu\nu}=a_0^2(1+2\psi)\bar h_{\mu\nu},
\]

after deriving the momentum equation and setting \(E=0\). Let
\(-\bar\Box_4\phi=\lambda\phi\). The metric zero-derivative and radial part is
obtained by expanding the repository-native reduced P1+GHY density

\[
6\kappa_1\left({a^2a_t^2\over N}+NXa^2\right)
-{1\over2}N a^4\kappa_0
\]

on both caps. Write

\[
Q_0^{g}
=c_{AA}A^2+dA\psi_t+eA\psi
+c_{\psi\psi}\psi_t^2+f\psi\psi_t+g\psi^2,
\]

where

\[
c_{AA}={12\kappa_1a_0^2a_{0,t}^2\over N_0},
\qquad
d=-{24\kappa_1a_0^3a_{0,t}\over N_0},
\]

\[
e=24X_c\kappa_1N_0a_0^2
-{48\kappa_1a_0^2a_{0,t}^2\over N_0}
-4\kappa_0N_0a_0^4,
\]

\[
c_{\psi\psi}={12\kappa_1a_0^4\over N_0},
\qquad
f={48\kappa_1a_0^3a_{0,t}\over N_0},
\]

\[
g={48\kappa_1a_0^2a_{0,t}^2\over N_0}
-4\kappa_0N_0a_0^4.
\]

The complete bulk metric term at first order in the derivative pencil is

\[
Q_1^g
=w\lambda\left(
{6\kappa_1\over a_0^2}A\psi
+{6\kappa_1\over a_0^2}\psi^2
\right).
\]

The scalar density is

\[
Q^\sigma
=-{Z_5a_0^4\over N_0}(\delta\sigma_t)^2
-N_0a_0^4A_5(\delta\sigma)^2
-Z_5N_0a_0^2\lambda(\delta\sigma)^2.
\]

Because \(\sigma_0=0\) and \(D\sigma_0=0\), all
\(A\)-\(\delta\sigma\) and \(\psi\)-\(\delta\sigma\) Hessian blocks vanish.
This is an action result, not a diagonalization assumption.

The common intrinsic B1 action adds

\[
Q_{B1}=6C_\partial\lambda\,\psi(1)^2.
\]

The matcher is eliminated algebraically after
\(h=\iota^*\gamma\); it supplies no independent propagating block.

## Operator pencil

In the weighted pairing, the zero-order blocks are

\[
L_{AA}^{(0)}={2c_{AA}\over w},
\]

\[
L_{A\psi}^{(0)}={d\over w}\partial_t+{e\over w},
\qquad
L_{\psi A}^{(0)}
=-{1\over w}\partial_t(d\,\cdot)+{e\over w},
\]

\[
L_{\psi\psi}^{(0)}
=-{2\over w}\partial_t(c_{\psi\psi}\partial_t)
+{2g-f_t\over w},
\]

\[
L_{\sigma\sigma}^{(0)}
={2Z_5\over w}\partial_t
\left({a_0^4\over N_0}\partial_t\right)-2A_5.
\]

The mixed scalar blocks are zero. The bulk first-order matrix is

\[
L_1^{\rm bulk}=
\begin{pmatrix}
0 & 6\kappa_1/a_0^2 & 0\\
6\kappa_1/a_0^2 & 12\kappa_1/a_0^2 & 0\\
0&0&-2Z_5/a_0^2
\end{pmatrix},
\]

and its B1 \(\psi\psi\) Hessian is \(12C_\partial\).
Thus the inherited principal lapse--Weyl block is recovered exactly:

\[
L_{A\psi}^{\rm crit}
={6\kappa_1\over a_0^2}
\begin{pmatrix}0&1\\1&2\end{pmatrix}.
\]

The complete action is therefore

\[
S^{(2)}
={1\over2}\int_{M_4}\sqrt{|\bar h|}
\left[
\langle Y,(L_0+\lambda L_1)Y\rangle
+2q\langle J_0+\lambda J_1,Y\rangle
+q(K_0+\lambda K_1)q
\right]+O(\lambda^2).
\]

The variable \(A\) is algebraic: the quadratic density contains no \(A_t\).
At \(\lambda=0\) its equation gives

\[
A={H_\rho\,\psi_t/N_0+(X_c/a_0^2)\psi\over H_\rho^2}.
\]

It is therefore a radial Hamiltonian constraint variable inside a
differential-algebraic system. It has not been eliminated before its action
normalization and B1 role are established.

## Scalar orthogonality

The critical Jacobi function obeys

\[
\left[
{1\over a_0^4}\partial_\rho(a_0^4\partial_\rho)
-{A_5\over Z_5}
\right]u_1=0,
\]

with regular pole condition, \(u_1(1)=0\), and per-cap normalization

\[
\int_0^1N_0a_0^4u_1^2dt=1.
\]

The reduced scalar field is

\[
\delta\sigma_\perp=P_\perp\delta\sigma,\qquad
P_\perp f=f-u_1\int_0^1N_0a_0^4u_1f\,dt.
\]

Consequently the scalar source is also projected with \(P_\perp\), and the
simple Jacobi kernel is absent from the response field.

## Affine convention and complete source

Exactly one affine convention is used:

\[
Y_{\rm total}=Y_{\rm response}+qv,
\]

\[
v_A={N_1\over N_0}=-\tau{\chi_1\over\pi},
\qquad
v_\psi=\tau{a_1\over a_0},
\]

\[
a_1=\chi_1\left[
{a_0\over4}-{\sqrt2\,t\cos(\pi t/4)\over4}
\right],
\qquad v_\sigma=s u_1.
\]

The independent M4 metric is varied directly; a separate
\(X\)-metric tangent is not added. This is the v6.23 no-double-counting
convention.

Let \(B_0\) and \(B_1\) be the polarized bilinear forms of the displayed
quadratic densities, including their B1 terms. Then the source is

\[
J_0[Y]=B_0^g(v_g,Y_g)+B_0^\sigma(su_1,\delta\sigma_\perp).
\]

The scalar term vanishes by the Jacobi equation and orthogonality, but it is
retained in the derivation. At first derivative order,

\[
\begin{split}
J_1[Y]={}&B_1^g(v_g,Y_g)
-2Z_5\int_0^1N_0a_0^2(su_1)\delta\sigma_\perp\,dt\\
&+\int_0^1w\left[
J_A^{(B)}A+J_{\psi,t}^{(B)}\psi_t
\right]dt ,
\end{split}
\]

where

\[
J_A^{(B)}
={6\kappa_1B_q(a_{0,t}/a_0)\over N_0^2a_0^2},
\qquad
J_{\psi,t}^{(B)}
=-{6\kappa_1B_q\over N_0^2a_0^2}.
\]

If the \(\psi_t\) term is integrated radially, its endpoint
\([wJ_{\psi,t}^{(B)}\psi]_0^1\) is retained with the inhomogeneous B1
source. Dropping it would change compatibility.

In the same convention,

\[
K_0=B_0^g(v_g,v_g)+B_0^\sigma(su_1,su_1),
\]

and

\[
\begin{split}
K_1={}&B_1^g(v_g,v_g)
-2Z_5\int_0^1N_0a_0^2u_1^2dt\\
&+2\int_0^1w\left[
J_A^{(B)}v_A+J_{\psi,t}^{(B)}v_{\psi,t}
\right]dt .
\end{split}
\]

There is no separate \(B_q^2\) term: the complete pure-shift Hessian is a
quadratic form in
\(W=B+\tau(\pi\chi_1/16)tq\), and the parent constraint gives \(W=0\).
The displayed threading terms are its mixed lapse/Weyl response and are not
an additional pure-shift square. The Einstein-frame Weyl term is not
included here; it remains a separate, exactly-once contribution for v6.29.

## Green current and domains

For two fields \(Y_1,Y_2\), the radial Green current is

\[
\begin{split}
\mathcal G_{12}={}&
d(A_1\psi_2-A_2\psi_1)
-2c_{\psi\psi}
(\psi_1\psi_{2,t}-\psi_{1,t}\psi_2)\\
&+{2Z_5a_0^4\over N_0}
(s_1s_{2,t}-s_{1,t}s_2).
\end{split}
\]

Coefficientwise in the derivative expansion, regular pole fields have

\[
A=A_0+O(t^2),\qquad
\psi=\psi_0+O(t^2),\qquad
\delta\sigma=s_0+O(t^2),
\]

so the pole current vanishes.

Define the metric endpoint momentum

\[
P_\psi=dA+2c_{\psi\psi}\psi_t+f\psi.
\]

The homogeneous B1 domain is

\[
P_\psi(1)+12C_\partial\lambda\psi(1)=0,
\qquad
\delta\sigma_\perp(1)=0.
\]

The first condition is the independent B1 trace equation; the algebraic
\(A\) equation evaluated at B1 is the Hamiltonian projection. The other two
scalar junction rows are the inherited Ward-dependent equations.

At B1 the metric Green current becomes
\(\psi_2P_{\psi,1}-\psi_1P_{\psi,2}\), and the Robin terms cancel. The scalar
current vanishes by Dirichlet data. Thus the formal adjoint has the same
radial domain:

\[
\operatorname{Dom}L=\operatorname{Dom}L^\dagger.
\]

This equality is derived from the current; it is not inferred from matrix
symmetry.

## Kernels and compatibility

Before quotienting, \(L_0\) has the endpoint-preserving radial
diffeomorphism kernel

\[
(A,\psi)=
\left(-\xi_t,-{a_{0,t}\over a_0}\xi\right),
\qquad \xi(0)=\xi(1)=0.
\]

It is gauge. The scalar kernel \(\operatorname{span}\{u_1\}\) is the physical
fold collective direction and is removed from
\(\delta\sigma_\perp\). The v6.27 \(C_1\) shift mode is forbidden by the
parent momentum constraint.

After the radial gauge quotient, one metric background conformal modulus
remains. A representative is

\[
z_A=\sec^2{\pi t\over4},\qquad z_\psi=1.
\]

It obeys the \(L_0\) equations and the \(\lambda=0\) B1 condition. Since the
operator is self-adjoint, the quotient kernel and adjoint kernel both have
dimension one.

The affine \(J_0\), including its boundary distribution, is orthogonal to
this adjoint kernel by the exact \(B_0\) Green identity. Gauge directions
are annihilated by the radial Noether identity. The scalar source is
orthogonal to \(u_1\) by \(P_\perp\).

At first derivative order the metric kernel is lifted by

\[
M_z=\langle z,L_1z\rangle
=12C_\partial+3\kappa_1(6-\pi)>0.
\]

The Lyapunov--Schmidt kernel equation fixes its amplitude:

\[
c_z=-{\langle z,J_1\rangle\over\langle z,L_1z\rangle}.
\]

No inverse on the unprojected \(L_0\) and no generic pseudoinverse is used.
The complementary scalar and metric source is compatible with the projected
operator. This supplies the operator/domain data needed to begin v6.29.

## Phase boundary

The present phase derives the operator, source, adjoint domain, kernels, and
compatibility. It does not evaluate

\[
-\langle J,L^{-1}J\rangle,
\]

does not emit a fold kinetic sign, and does not derive an Einstein-frame
potential, scale, or mass. Phase v6.29 is permitted only with the projected
pencil, explicit modulus equation, scalar projector, and inhomogeneous B1
source retained.
