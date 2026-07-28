# BHSM v6.25.0 fixed support versus dynamical B1 embedding

## Primary result

The homogeneous cap-length modulus has a regular fixed-manifold
localization.  Let

\[
 \ell(q)=\ell _0+\tau\ell _1q+O(q^2),\qquad
 \ell _0=N_0={\pi\over4},\qquad
 \ell _1=-{\chi _1\over4}.
\]

The change of radial coordinate

\[
 \rho=\ell(q(x))t,\qquad 0\leq t\leq1
\]

maps the \(q\)-dependent proper-radial cap to
\([0,1]_t\times M_4\), with B1 fixed at \(t=1\).  It uses the existing ADM
lapse, shift, induced metric, scalar, intrinsic B1 metric, and matcher
variables.  Its linear shift agrees exactly with the v6.18 threading
response.

This proves kinematic representability, but it does not yet prove dynamical
compatibility of fixed support.  The first unresolved contribution to the
normal-support residual is the time-dependent spatially homogeneous
Lorentzian threading and endpoint response at \(O(D^2q)\).  The v6.18
theorem covers the spatial round-\(S^3\) projected response, not the
\(D_0D_0q\) sector.  Hence neither a vanishing nor a nonvanishing
\(R_\perp\) has been established.

The primary verdict is

```text
BHSM_SUPPORT_DOMAIN_DECISION_BLOCKED_BY_UNDERIVED_TIME_DEPENDENT_HOMOGENEOUS_THREADING_JUNCTION_RESPONSE
```

Neither fixed-support success nor dynamical-embedding necessity is emitted.
The dynamic domain, its Z2 glue rule, action differentiability, and an
embedding Euler--Lagrange equation are not constructed.

## Fixed-manifold pullback

In proper radial coordinates take

\[
 ds^2=d\rho^2+
 \widetilde\gamma_{\mu\nu}(\rho,q(x))dx^\mu dx^\nu .
\]

Because

\[
 d\rho=\ell\,dt+t\ell_qD_\mu q\,dx^\mu ,
\]

the exact coordinate components relevant through two derivatives are

\[
 g_{tt}=\ell^2,\qquad
 g_{t\mu}=t\ell\ell_qD_\mu q,
\]

\[
 \gamma_{\mu\nu}
 =\widetilde\gamma_{\mu\nu}(\ell t,q)
 +t^2\ell_q^2D_\mu qD_\nu q.
\]

Thus, in fixed-\(t\) radial ADM form,

\[
 N_\mu=t\ell\ell_qD_\mu q=D_\mu B,\qquad
 B={t\over2}\left[\ell(q)^2-\ell_0^2\right],
\]

and

\[
 N^2=\ell^2\left[1-t^2\ell_q^2(Dq)^2\right]+O(D^4).
\]

At linear order,

\[
 B^{(1)}
 =\tau\ell_0\ell_1tq
 =-\tau{\pi\chi_1\over16}tq.
\]

This is precisely

\[
 \Pi_\perp B
 =-\tau{\pi\chi_1\over16}t\,\Pi_\perp q
\]

from v6.18.  No new shift field is required.

The derivative part of the extrinsic curvature contains

\[
 \delta K_{\mu\nu}\supset
 -t\ell_qD_\mu D_\nu q
 =\tau{\chi_1\over4}tD_\mu D_\nu q
\]

at the fold.  The induced metric and lapse also contain the displayed
\((Dq)^2\) terms.  Their complete quadratic coefficients require the
unstored second homogeneous responses
\(\ell_2,a_2,N_2\), but those responses are not needed to identify the
linear \(O(D^2q)\) support test.

The scalar is pulled back as
\(\sigma_{\rm fixed}(t,x)=\widetilde\sigma(\ell(q)t,q)\).
Its stored odd homogeneous tangent obeys \(u_1(1)=0\).  The matcher imposes
the complete fixed-\(t\) pullback at B1, including the rank-one
\((Dq)^2\) metric term.

## Homogeneous tangent and affine convention

The retained fixed-domain profiles are

\[
 a_0(t)=\sqrt2\sin{\pi t\over4},
\]

\[
 a_1(t)=\chi_1\left[
 {a_0(t)\over4}
 -{\sqrt2\,t\cos(\pi t/4)\over4}\right],
\qquad N_1=\ell_1=-{\chi_1\over4},
\]

before multiplication by \(\tau\).  They satisfy \(a_1(1)=0\).  The stored
homogeneous junction tangent remains
\(\delta a'_J=\delta X/2\) after the domain correction, with
\(dX_{\rm FRW}/dq=\tau\chi_1\).

One affine convention is used: these \(q\)-dependent homogeneous profiles
are included in the fixed-domain fields and are not duplicated in a direct
mixed source.  The scalar Schur combination is invariant under an affine
change \(Y=Z+vq\):

\[
 K'-{J'^2\over L}=K-{J^2\over L}.
\]

## Gauge quotient

The endpoint threading invariant is

\[
 {\cal S}_\Sigma
 =B+N_0^2\zeta-a_0^2\partial_tE .
\]

For the scalar radial and M4-longitudinal gauge parameters
\((\xi^t,L)\),

\[
 B\mapsto B-N_0^2\xi^t-a_0^2\partial_tL,\quad
 \zeta\mapsto\zeta+\xi^t|_{\rm B1},\quad
 E\mapsto E-L,
\]

so \({\cal S}_\Sigma\) is invariant.  The gauge conditions
\((\zeta,E)=(0,0)\) have Faddeev--Popov matrix

\[
 \begin{pmatrix}1&0\\0&-1\end{pmatrix},
\]

with determinant \(-1\) and rank two.  A moving graph
\(\zeta=\tau\ell_1q/\ell_0\) is brought to fixed support by
\(\xi^t=-t\zeta\).  It is smooth at the pole, has the required B1 value,
and generates the same \(B^{(1)}\) above.  It changes no pullback datum and
adds no physical embedding scalar.

## Boundary-equation dependency ledger

The tensor junction equation is

\[
 {\cal J}_{\mu\nu}
 =\kappa_1[Q_{\mu\nu}]
 +2C_\partial G_{\mu\nu}^{(4)}
 -T_{\partial,\mu\nu}=0.
\]

Its closed-FRW scalar decomposition has four projections: Hamiltonian,
scalar momentum, spatial trace, and traceless-longitudinal.  The intrinsic
Bianchi identity and bulk momentum constraint give two scalar Ward
dependencies.  Therefore there are two independent scalar junction
combinations, not four.  The two scalar matcher equations remain algebraic
and eliminate the matcher variables without producing a propagating mode.

The available equations do not close the full local scalar B1 system,
because the time-dependent spatially homogeneous junction threading and
endpoint trace have not been derived from the quadratic frozen action.
This is the earliest stop.

## Normal-support residual

The primary diagnostic definition is

\[
 R_\perp[q]
 ={1\over\sqrt{|h|}}\,
 \left.\delta_{\zeta}^{\rm diag}S_{\rm total}\right|_{\zeta=0}.
\]

Here \(\delta_\zeta^{\rm diag}\) simultaneously displaces the integration
domain normally and pulls back the fields.  It is a diagnostic shape
variation, not an enlargement of the frozen configuration space.
Equivalently it is the boundary coefficient in the five-dimensional
diffeomorphism identity with normal boundary value, or the corresponding
combination of cap normal Einstein constraints, the tensor junction
equation contracted with the background extrinsic curvature, and the
scalar and matcher boundary equations.

Structurally, at linear order,

\[
 R_\perp^{(1)}
 =\sum_{\rm caps}c_H\,\delta E_{nn}
 +\bar K^{\mu\nu}\delta{\cal J}_{\mu\nu}
 +(\hbox{scalar and matcher boundary equations}).
\]

The action-normalized coefficient and complete endpoint terms cannot be
assigned until the missing fixed-support quadratic response is derived.
No arbitrary normalization is introduced.

The \(O(q)\) homogeneous residual vanishes on the stored bulk and junction
tangent.  An \(O(Dq)\) shift exists but cannot by itself form a covariant
scalar residual.  The first unresolved order is \(O(D^2q)\), through the
\(D_0D_0q\) part of \(\delta K_{\mu\nu}\).  The later
\(O((Dq)^2)\) order also depends on second homogeneous responses.

The residual is a scalar on the common B1, cap-exchange even in the stored
common-normal convention, and independent of fixed versus moving
coordinates and affine bookkeeping.  The sheet label \(\tau\) changes the
linear source sign but not the dependency rank.  The scalar sign \(s\) is
absent at this order because \(\sigma_0=0\).

The Noether identity does not set \(R_\perp\) to zero before all independent
boundary equations are known.  A normal diffeomorphism with nonzero B1
value is not a gauge transformation within the fixed-support variational
domain; it instead supplies the diagnostic identity relating the residual
to the bulk and boundary equations.

## Decision and next target

The exact supporting results are

```text
BHSM_FIXED_MANIFOLD_LOCALIZATION_MAP_DERIVED
BHSM_NORMAL_SUPPORT_RESIDUAL_BLOCKED_BY_UNDERIVED_TIME_DEPENDENT_HOMOGENEOUS_THREADING_JUNCTION_RESPONSE
BHSM_DYNAMICAL_EMBEDDING_DOMAIN_NOT_REACHED_BECAUSE_NECESSITY_NOT_PROVEN
BHSM_FOLD_LOCAL_SCALAR_OPERATOR_REOPENING_BLOCKED_BY_UNDECIDED_SUPPORT_DOMAIN
BHSM_FOLD_SCHUR_REDUCTION_BLOCKED_BY_UNDECIDED_SUPPORT_DOMAIN
BHSM_FOLD_KINETIC_SIGN_REMAINS_UNRESOLVED_BY_UNDECIDED_SUPPORT_DOMAIN
```

The next construction target is the action-normalized time-dependent
spatially homogeneous threading and endpoint response.  It must be inserted
into the two independent scalar B1 junction projections before evaluating
\(R_\perp\) at \(O(D^2q)\).

No measured input, fitted coefficient, new primitive, new action, new scale,
corner term, arbitrary boundary condition, local \(X_{\rm FRW}(x)\) field,
scalar-curvature inverse, chat-only kinetic candidate, physical mass, or
stability claim is introduced.  Frozen predictions and official prediction
logic are unchanged.
