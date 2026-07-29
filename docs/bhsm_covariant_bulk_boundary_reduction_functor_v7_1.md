# BHSM v7.1 covariant bulk--boundary reduction functor

## Result

BHSM v7.1 replaces the unsourced arrows of the v7.0 action complex by a
covariant correspondence construction. The authoritative architecture is
not a claim that every four-dimensional field descends from the
eight-dimensional metric. It combines:

1. an oriented fiber-pushforward functor on retained
   invariant/equivariant \(S^3\) modes;
2. the independently owned two-cap \(M_5\) relative action;
3. an intrinsic \(M_4\) action for boundary-localized Standard Model fields;
4. covariant compatibility multipliers linking the strata.

The result is
`BHSM_STRATIFIED_MASTER_ACTION_CLOSED_WITH_COVARIANT_COMPATIBILITY_MAPS`.
It closes RB-01 while preserving the firewall that the intrinsic Standard
Model action is not derived from pure eight-dimensional geometry.

## Authoritative geometry

The selected source and target are

\[
M_8=I_t\times S^7,\qquad M_5=I_t\times S^4,
\]

with the quaternionic Hopf map

\[
\pi_{85}=\operatorname{id}_{I_t}\times p_H:
I_t\times S^7\longrightarrow I_t\times S^4,
\qquad
S^3=\operatorname{Sp}(1)\longrightarrow S^7
\overset{p_H}{\longrightarrow}S^4.
\]

The bundle has \(c_2=+1\) in the stored base-before-fiber orientation. The
vertical metric is bundle-natural on the round
\(\operatorname{Ad}(\operatorname{Sp}(1))\)-invariant branch. No preferred
global \(U(1)\) anisotropy axis is introduced.

The two \(M_5\) caps use

\[
ds_5^2=-dt^2+a(t)^2
\left[d\chi^2+\sin^2\chi\,ds_{S^3}^2\right]
\]

and share the equator

\[
\iota_{54,\epsilon}:M_4=I_t\times S^3\hookrightarrow M_{5,\epsilon},
\qquad
\iota_{54,\epsilon}(t,x)=(t,\pi/2,x).
\]

The outward normals are

\[
n_+=a^{-1}\partial_\chi,\qquad
n_-=-a^{-1}\partial_\chi.
\]

The cap reflection \(J(t,\chi,x)=(t,\pi-\chi,x)\) exchanges the caps and
their normals. A dimensionless collar is

\[
c_\epsilon(t,x,\rho)=(t,\pi/2-\epsilon\rho,x),
\qquad 0\leq\rho<\epsilon_\chi .
\]

At fixed \(t\), the physical normal element is \(ds=a(t)d\rho\). No
absolute length is inferred from the coordinate range.

## Measures and orientations

The orientation and fiber measure are

\[
\operatorname{or}(M_8)
=\operatorname{or}(M_5)\wedge\operatorname{or}(S^3),
\]

\[
d\mu_F=a_F^3\,\eta_1\wedge\eta_2\wedge\eta_3,\qquad
V_F=16\pi^2a_F^3,\qquad
d\nu_F=\frac{d\mu_F}{V_F}.
\]

The normalized pairing satisfies \(\int_Fd\nu_F=1\), while physical action
pushforward retains the fiber volume:

\[
\pi_{85!}(\mathcal L_8\,d\mu_8)
=
\left(\int_F\mathcal L_8\,d\mu_F\right)d\mu_5.
\]

On the hyperspherical branch,

\[
d\mu_5
=Na^4\sin^3\chi\,dt\,d\chi\,d\mu_{S^3},\qquad
d\mu_4=Na^3\,dt\,d\mu_{S^3}.
\]

In collar coordinates,

\[
d\mu_5
=Na^4\cos^3\rho\,dt\,d\rho\,d\mu_{S^3}.
\]

Because the \(S^3\) fiber is closed,

\[
d\,\pi_{85!}\omega=\pi_{85!}d\omega.
\]

## The \(8\to5\) functor

For a retained finite spectral subspace,

\[
\Phi_8(x,y)
=\sum_{\alpha\in\mathcal I_{\rm ret}}
\phi_\alpha(x)u_\alpha(y)+\Phi_\perp(x,y),
\]

with

\[
N_{\alpha\beta}
=\int_Fu_\alpha^\dagger u_\beta\,d\mu_F,\qquad
\phi_\alpha
=N_\alpha^{-1}\int_Fu_\alpha^\dagger\Phi_8\,d\mu_F.
\]

The basic mode is a scalar on \(M_5\). A nontrivial
\(\operatorname{Sp}(1)\) representation produces a section of

\[
E_R=P\times_RV_R\longrightarrow M_5
\]

with the connection induced by the quaternionic Hopf connection. On
invariant or equivariant retained modes,

\[
D_5P_\alpha=P_\alpha D_8.
\]

The coefficient map is

\[
c_{5,\alpha\beta}
=c_8\int_Fu_\alpha^\dagger u_\beta\,d\mu_F.
\]

For an unnormalized fiber-constant field \(c_5=V_Fc_8\), whereas an
orthonormal mode absorbs that volume into its field normalization. In
particular,

\[
\kappa_5(x)=V_F(x)\kappa_8.
\]

If \(a_F\) varies, \(\pi_{85!}S_8\) is scalar--tensor gravity containing a
radion, connection curvature, and fiber-potential terms. It is not equal to
the historical constant-\(\kappa_5\) cap action. V7.1 records that action as
an independent target-stratum Wilson action instead of normalizing away the
mismatch.

## The \(5\to4\) functor

Bulk-derived response is defined on a local stationary branch by

\[
S_{4,\mathrm{response}}[\varphi,k]
=
\operatorname*{Crit}_{\substack{
\Phi_5:\operatorname{Tr}_{B_1}\Phi_5=\varphi\\
\mathcal C(\Phi_5)=0,\;k\ {\rm retained}
}}
S_{5|4}[\Phi_5,\eta].
\]

Here \(\mathcal C\) includes cap equations, ADM constraints, GHY completion,
the matcher, gauge quotient conditions where applicable, and the \(D_0\)
scalar Dirichlet condition. Lyapunov--Schmidt kernel variables \(k\) remain
explicit.

The Standard Model connections, fermions, Higgs field, and optional neutral
auxiliary field are intrinsic \(M_4\) data. They are varied on \(M_4\); no
bulk extension is invented to claim an \(S_8\) provenance.

## Stratified correspondence action

The authoritative action is

\[
\begin{aligned}
S_{\rm BHSM}^{\rm strat}
={}&S_8[G,\chi,\sigma]
+\sum_{\epsilon=\pm}
\left(S_{5,\epsilon}[g_\epsilon,\sigma_5]
+S_{\rm GHY,\epsilon}\right)\\
&+S_{4,\mathrm{localized}}[h,A,\Psi,H;\mathcal I_4]
+S_{\rm compatibility},
\end{aligned}
\]

where

\[
\begin{aligned}
S_{\rm compatibility}
={}&\int_{M_5}
\left\langle\Lambda_{85},g_5-Q_H(G_8)\right\rangle
+\left\langle\lambda_\sigma,\sigma_5-P_0\sigma_8\right\rangle\\
&+\sum_{\epsilon=\pm}\int_{M_4}
\Lambda_{54,\epsilon}^{ab}
\left(h_{ab}-\iota_\epsilon^*g_{\epsilon,ab}\right).
\end{aligned}
\]

The source and target fields are distinct off shell. Their kinetic terms
belong to different strata and have independently typed Wilson
coefficients. Compatibility multipliers have no kinetic term, and their
normalization is redundant.

## Variational intertwiner

The constrained Euler--Lagrange system is

\[
\begin{aligned}
E_8+C_{85,8}^*\Lambda_{85}&=0,\\
E_5-C_{85,5}^*\Lambda_{85}+C_{54,5}^*\Lambda_{54}&=0,\\
E_4-C_{54,4}^*\Lambda_{54}&=0,\\
C_{85}&=0,\qquad C_{54}=0.
\end{aligned}
\]

For the genuinely pushed-forward part,

\[
D(\pi_{85!}S_8)\circ D\mathcal R_{85}
=\mathcal R_{85*}\circ DS_8
\]

on the retained invariant/equivariant subspace. GHY cancels normal metric
derivatives, matcher multipliers supply seam reactions, and lapse and shift
retain the ADM constraints.

## Domains and Hessians

The master domain contains the \(M_8\) diffeomorphism quotient, cap/ADM
domain, \(M_4\) gauge quotient, maximal-isotropic Dirac domains, scalar
trace domains, optional neutral cone, and multiplier duals.

The fixed-\(h\) domain is unchanged:

\[
\mathcal D_0
=\{\text{regular pole},\ h\ \text{fixed},\
\sigma|_{B_1}=0,\ \text{exact matcher reaction}\}.
\]

The KKT Hessian is

\[
\begin{pmatrix}
H_8&0&0&C_{85,8}^*&0\\
0&H_5&0&-C_{85,5}^*&C_{54,5}^*\\
0&0&H_4&0&-C_{54,4}^*\\
C_{85,8}&-C_{85,5}&0&0&0\\
0&C_{54,5}&-C_{54,4}&0&0
\end{pmatrix}.
\]

Eliminating an interior complement gives only

\[
H_{\rm eff}=H_{bb}-H_{bi}H_{ii,\perp}^{-1}H_{ib}.
\]

The inverse acts on the closed-range complement. Gauge, constraint, and
Lyapunov--Schmidt kernels remain explicit. No generic pseudoinverse, kernel
inverse, empirical inverse, or unlicensed Robin domain is used.

## Projectors and action ownership

- Spin(8) triality projectors are representation-derived and transported
  equivariantly.
- Standard Model representation and sector projectors are finite
  independent \(M_4\) inputs.
- Chirality is intrinsic to the four-dimensional spin bundle.
- Generation/mode projectors remain conditional finite spectral data;
  measured masses do not select them.
- Charged channels are owned by the \(SU(2)\) covariant derivative and
  Yukawa basis.
- Neutral auxiliary projectors belong only to the conditional extension.

| Term | Ownership/result |
| --- | --- |
| \(M_8\) Einstein/carrier/scalar | independent parent-theory inputs |
| capwise Einstein--scalar | independent target-stratum inputs |
| GHY | transported boundary trace/variational completion |
| intrinsic \(B_1\) gravity/matter | boundary-localized fundamental |
| compatibility matchers | transported trace constraints |
| Yang--Mills | boundary-localized fundamental |
| Dirac/Yukawa | boundary-localized fundamental |
| Higgs/scalar | boundary-localized fundamental |
| neutral auxiliary response | conditional extension |

No four-dimensional action term is relabeled as an eight-dimensional
prediction.

## Completion DAG

RB-01 is closed by the covariant correspondence architecture. Its Tier-A
descendants close as follows:

- RB-03: domains, projectors, and boundary operators are finitely typed.
- RB-04 and RB-05: charged stiffness and \(\eta_\ell\) remain historical
  screens, not official action outputs.
- RB-06: CKM is \(U_u^\dagger U_d\) from independent Yukawa matrices; the
  \(1/16\) rule remains screen-only.
- RB-07: PMNS and neutrino mass operators are conditional extensions.
- RB-08: \(g_1,g_2,g_3\) are finite independent inputs.
- RB-09: fiber, cap, seam, and collar measures are explicit.
- RB-10: the neutral cone is typed only within the optional extension.
- RB-11: the retained scalar action closes with \(\lambda_5\) independent.

This yields `BHSM_CORE_COMPLETE`.

## One-scale bridge and next obstruction

One common positive length \(\ell_\star\) is admitted as the sole
dimensionful calibration:

\[
Q_{\rm phys}=\ell_\star^{-d_L}\widehat Q,\qquad
m_{\rm phys}=\widehat m/\ell_\star.
\]

No value is selected, it is not called a prediction, and no dimensionless
parameter or sector is retuned.

The next independent Tier-B object is
`COMMON_SCHEME_OBSERVABLE_TRANSPORT_FUNCTOR`. It must map action parameters
and spectral quantities into one declared renormalization scheme, scale,
threshold prescription, and observable definition without hidden retuning.
The classical stratified action does not supply that quantum transport.

## Claim boundary

V7.1 proves internal closure of the finite-input dimensionless core. It
does not prove that the Standard Model is derived from pure geometry, select
numerical gauge or Yukawa inputs, predict \(\lambda_5\), derive PMNS or
neutrino masses, or claim physical/release completion.
