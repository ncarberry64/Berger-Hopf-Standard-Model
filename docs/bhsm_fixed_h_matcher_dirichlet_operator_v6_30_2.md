# BHSM v6.30.2 fixed-h matcher Dirichlet operator

The five Phase-A results are

- `BHSM_FIXED_H_UNELIMINATED_MATCHER_OPERATOR_DERIVED`;
- `BHSM_FIXED_H_DIRICHLET_GREEN_CURRENT_AND_ADJOINT_DOMAIN_DERIVED`;
- `BHSM_FIXED_H_MATCHER_KERNEL_AND_CLOSED_RANGE_DERIVED`;
- `BHSM_FIXED_H_MATCHER_COMPLEMENT_INVERSE_DERIVED`;
- `BHSM_FIXED_H_NONLINEAR_BOUNDARY_MAP_DERIVED`.

They are derived from the frozen two-cap
P1+GHY+scalar+B1+matcher action. No matcher elimination, Robin inverse,
generic pseudoinverse, new action term, or empirical datum is used.

## Fixed-h variation

The exact matcher is

\[
S_{\rm match}=\int_{\rm B1}\sqrt{|h|}\,
\Lambda^{\mu\nu}(h_{\mu\nu}-\iota^*\gamma_{\mu\nu}).
\]

For the effective action \(\Gamma[h,q]\), \(\delta h_{\mu\nu}=0\), while
the bulk boundary metric and \(\Lambda^{\mu\nu}\) are varied. Thus

\[
\delta_\Lambda S=0
\quad\Longrightarrow\quad
h_{\mu\nu}=\iota^*\gamma_{\mu\nu},
\]

and the bulk boundary variation gives

\[
\Pi_{\mu\nu}-\Lambda_{\mu\nu}=0.
\]

The intrinsic B1 action is a functional of the independent fixed metric
\(h\). Consequently it contributes to the value of \(\Gamma[h,q]\), but
not to the bulk fixed-\(h\) KKT Hessian. GHY cancels normal derivatives of
\(\delta\gamma\) cap by cap. The reflected canonical momenta add in the
stored common-normal convention.

## Complete scalar trace

Before scalar gauge fixing, use

\[
{\delta\gamma_{\mu\nu}\over2a_J^2}
=\psi\,\bar h_{\mu\nu}+D_\mu D_\nu E .
\]

The two independent scalar matcher traces are

\[
\Theta=\psi(1)+{1\over4}\Box_4E(1),\qquad
\mathcal E=E(1)
\]

on nonzero scalar harmonics. The constant \(E\) representative is a
coordinate null direction. Neither the radial lapse \(A\) nor the
normal-tangential shift \(B\) belongs to the induced metric trace.

After deriving the momentum equation and choosing \(E=0\), the homogeneous
trace is

\[
B_DY=\psi(1)=0.
\]

The multiplier reactions are the trace and scalar-longitudinal projections
\(\eta_{\rm tr},\eta_L\). The longitudinal row is Ward dependent after the
\(E\) gauge reduction; the homogeneous radial saddle retains
\(\eta_{\rm tr}\).

## KKT operator

On \(\mathbb Y=(A,\psi,\delta\sigma,\eta_{\rm tr})\), the strong block form
is

\[
\mathbb L_D=
\begin{pmatrix}
L_{AA}&L_{A\psi}&0&0\\
L_{\psi A}&L_{\psi\psi}&0&-B_D^\dagger\\
0&0&L_\sigma&0\\
0&-B_D&0&0
\end{pmatrix}.
\]

The matcher sign follows from \(S_{\rm match}=\Lambda(h-\gamma)\).
The endpoint equations are

\[
\psi(1)=0,\qquad
P_\psi(1)-\eta_{\rm tr}=0,\qquad
\delta\sigma(1)=0.
\]

This is an indefinite symmetric saddle operator, not the v6.28 Robin
realization.

## Green identity and adjoint

The bulk current is

\[
\begin{split}
\mathcal G_{12}={}&
d(A_1\psi_2-A_2\psi_1)
-2c_{\psi\psi}(\psi_1\psi_{2,t}-\psi_{1,t}\psi_2)\\
&+{2Z_5a_0^4\over N_0}
(s_1s_{2,t}-s_{1,t}s_2).
\end{split}
\]

The saddle current adds the finite matcher pairing

\[
\mathcal G^D_{12}
=\mathcal G_{12}
+\psi_1\eta_2-\psi_2\eta_1.
\]

At B1, \(P_{\psi,i}=\eta_i\), so the canonical-momentum current cancels
the matcher pairing. At the regular pole the coefficientwise current
vanishes. The extended KKT domain and its formal adjoint domain are equal.
After solving the lower KKT row, both constrained realizations have
\(\psi(1)=s(1)=0\).

## Kernel and range

Endpoint-preserving radial diffeomorphisms remain gauge. The v6.28 metric
modulus has \(\psi_z(1)=1\) and is excluded. A matcher-only vector is not a
zero mode because \(P_\psi-\eta=0\) forces \(\eta=0\).

Since the scalar background is zero, metric-scalar Hessian blocks vanish.
The fixed-\(h\) quotient kernel is therefore exactly

\[
\ker\mathbb L_D
=\operatorname{span}\{(0,0,u_1,0)\}.
\]

The adjoint kernel is the same. The regular singular scalar
Sturm--Liouville block, finite-rank matcher extension, compact radial
interval, and removal of the only metric modulus give closed range and
Fredholm index zero.

## Complement inverse

The exact projector is

\[
Q_Df=f-u_1\langle u_1,f_\sigma\rangle_w.
\]

Fixed-\(h\) Dirichlet data allow endpoint-preserving areal gauge
\(\psi=0\). On Noether-compatible metric sources,

\[
A={f_A\over L_{AA}},\qquad
\eta_{\rm tr}=P_\psi[A,0](1),
\]

and the remaining metric row is the radial Noether identity. The scalar
inverse is

\[
G_\sigma^Df
=\sum_{n\ge2}{\langle u_n,f\rangle_w\over\mu_n-\mu_1}u_n .
\]

Adaptive collocation and an independent hypergeometric spectral inversion
agree on the first complementary eigenmode within a certified
\(10^{-10}\) weighted-\(L^2\) bound. The positive complement gap is
\(64.0147366689857\).

## Nonlinear boundary map

Let the exact fixed-h warp trace be

\[
\alpha(q)=\sum_{n\ge1}{q^n\over n!}\alpha_n,\qquad
(1+\alpha(q,1))^2=1.
\]

Then

\[
\alpha_n(1)=
-{1\over2}\sum_{k=1}^{n-1}
{n\choose k}\alpha_k(1)\alpha_{n-k}(1).
\]

Hence \(\alpha_1(1)=0\) implies \(\alpha_n(1)=0\) recursively. The first
three sources are \(0\), \(-\alpha_1^2\), and
\(-3\alpha_1\alpha_2\). A reusable arbitrary-order routine implements this
factorial convention.

The multiplier reaction at every order is generated by differentiating the
exact P1+GHY canonical momentum. The reaction generator uses the
repository's additive induced-metric Weyl variable
\(\gamma=a_0^2(1+2\psi)\bar h\), related to the warp response by

\[
\psi=\alpha+{\alpha^2\over2}.
\]

It therefore evaluates

\[
a=a_0\sqrt{1+2\psi},\qquad N=N_0(1+A).
\]

Its linear coefficient reproduces the v6.28 action-derived
\(P_\psi\) exactly. This nonlinear trace-and-reaction map supplies the
boundary input required for v6.30.3.

No measured input, fit, empirical inverse, q-dependent action control,
q-dependent regulator, new primitive, physical mass, stability claim, or
frozen prediction change is introduced.
