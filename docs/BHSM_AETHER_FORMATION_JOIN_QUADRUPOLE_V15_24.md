# BHSM v15.24: formation-to-Hopf-join quadrupole bridge

## The two nonlinear reductions are distinct

The v15.9 formation solution has radial \(S^6\) level sets. The Hopf join
reduction has \(S^3\times S^3\) orbits. Their identity maps describe the same
round degree-one state, but their nonlinear one-variable profiles cannot be
substituted for one another. The physical continuation must pass through the
full \(S^7\) field equation or an action-derived common representation.

## Exact common representation

Let \(n\in S^7\) be the spontaneously selected v15.9 formation axis and
\(\phi_n=n\cdot x\) its \(l=1\) harmonic. Its square contains

\[
Q_n=(n\cdot x)^2-\frac18,
\]

an exact trace-free \(l=2\) component. The retained Hopf splitting
\(\mathbb R^8=\mathbb R^4_u\oplus\mathbb R^4_v\) supplies

\[
J=\operatorname{diag}(I_4,-I_4),\qquad
Q_J=x^TJx=\cos(2\chi).
\]

Uniform \(S^7\) fourth moments give

\[
\langle Q_n^2\rangle=\frac7{320},\qquad
\langle Q_J^2\rangle=\frac15,\qquad
\langle Q_nQ_J\rangle=\frac{n^TJn}{40}.
\]

Therefore

\[
\boxed{\operatorname{Proj}_{J}Q_n=\frac{\zeta}{8}Q_J},
\qquad \zeta=n^TJn\in[-1,1].
\]

This is the first coefficient-free formation-to-join source permitted by the
existing geometry. The relative orientation \(\zeta\) is internal to the
formation axis and Hopf splitting; it is not an external frame parameter.
Its physical branch still has to be selected by the coupled action.

## Exact invariant scalar join spectrum

For \(w=\sin^3\chi\cos^3\chi\), the invariant scalar operator is

\[
\mathcal L_J=-\frac1w\partial_\chi(w\partial_\chi).
\]

Smooth extension across both collapse poles selects the Friedrichs domain.
The Green boundary form

\[
[w(\bar u v'-\bar u'v)]_0^{\pi/2}
\]

vanishes on its bounded even Frobenius branches. The complete invariant
spectrum is

\[
\psi_n=P_n^{(1,1)}(\cos2\chi),\qquad
\boxed{\lambda_n=4n(n+3)}.
\]

The first nonconstant mode is exactly the join quadrupole:

\[
\mathcal L_J\cos2\chi=16\cos2\chi.
\]

This is a geometric scalar spectrum, not yet the Hamiltonian-reduced coupled
metric--eta--sigma spectrum.

## Critical Hamiltonian-constraint response

The v15.9 profile gives, with \(t=n\cdot x\),

\[
\bar X_\eta
=7+14qt+q^2\left(\frac{427}{27}t^2-\frac{343}{54}\right)+O(q^3).
\]

Use the smooth scalar metric family

\[
g_{ij}=R^2e^{2aQ_J}\bar g_{ij}.
\]

Its curvature variation is

\[
\delta R_7=\frac{108}{R^2}aQ_J.
\]

Projecting the eta energy onto \(Q_J\), including its metric susceptibility,
and imposing the time-symmetric Hamiltonian constraint at
\(R_c^6=343/(5\kappa_1)\) yields

\[
\boxed{\frac{a}{q^2}=\frac{343}{1728}\,\zeta}.
\]

The corresponding mixed static-action derivative per unit round \(S^7\)
volume is

\[
\boxed{\frac{\partial^3 S}{\partial a\,\partial q^2}
=-\frac{7203}{20R_c}\,\zeta}.
\]

Thus an aligned formation axis forces a smooth nonround metric response at
order \(q^2\). A zero eigenvalue is not required. The balanced branch
\(\zeta=0\) has no projection into this particular join channel. The result
is an exact time-symmetric constraint slice; the momentum constraint and
time-dependent physical kinetic form remain to be reduced.

## Momentum constraint and onset Legendre degeneracy

The round scalar sector can be reduced further in eta-unitary gauge. Set

\[
h_{ij}=2aYg_{ij},\qquad \beta^i=b\nabla^iY,qquad
-\Delta Y=\frac{16}{R^2}Y.
\]

After including both Einstein and p2+p8 eta kinetic terms, the quadratic
kinetic form per \(\langle Y^2\rangle\) is

\[
L_{\rm kin}=A\dot a^2+B\dot a b+Cb^2,
\]

with

\[
A=-21\kappa_1,\quad B=-6\kappa_1\lambda,
\quad C=\frac{\lambda}{R^2}[F'(X_0)-3\kappa_1].
\]

At the exact formation crossing, \(X_0^3=5\kappa_1\) and therefore
\(F'(X_0)=3\kappa_1\). Hence

\[
\boxed{C=0},\qquad \boxed{\delta_bL=0\Longrightarrow\dot a=0}.
\]

The forced \(a=(343/1728)\zeta q^2\) is consequently a nonpropagating
constraint response at the exact onset slice, not yet a canonical shape
coordinate. On the round-radius formed side \(R>R_c\), the shift coefficient
is nonzero and its Schur reduction has positive kinetic sign. The decisive
calculation must now use the actual nonidentity eta pullback and dynamical
sigma response, rather than replacing them by the round-radius control.

That first replacement has now been performed on instantaneous
\(\dot q=0\), \(\sigma=0\) formed slices. For an aligned formation axis, the
radial and tangential eta stretches are projected into the join quadrupole
using exact conditional \(S^7\) moments. The v15.9 and join orbit spaces are
never identified. At \(R^6/R_c^6=1.01\), the actual 12-mode v15.9 profile
makes the total shift-square coefficient nonzero, and shift elimination gives
a strictly positive reduced \(\dot a^2\) coefficient. Thus the Legendre
degeneracy is confined to the exact identity crossing in this sector; the
formed nonidentity pullback lifts it.

The next calculation must retain \(\dot q\), \(\dot\sigma\), their cross
kinetic terms, and the time-dependent sigma transfer before the covariant
symplectic pullback can certify the canonical shape momentum.

## Exact sigma pulse transfer

The homoclinic tangent equation can be written in its reconstructed affine
clock variable as

\[
s''+[\omega_0^2-D\,\operatorname{sech}^2x\tanh^2x]s=0.
\]

v15.24 integrates its complete fundamental matrix and removes the free
oscillator rotation. The resulting symplectic transfer has reciprocal
singular values, and its largest logarithm is the net pulse squeezing. This
replaces an instantaneous or WKB-only diagnosis. Its physical value and
whether nonlinear saturation is reached remain conditional on the unselected
global sigma response operator.

## Consequence for the nonround branch

A positive round \(l=2\) Hessian does not imply zero nonround response. The
order-\(q^2\) quadrupole can force a unique response through the invertible
operator before any eigenvalue crosses zero. The required next calculation is
the mixed eta-stress/metric source vertex and its Hamiltonian-constraint Schur
complement.

## Status

`FULL_BHSM_COMPLETE = FALSE`.

Exact next object:

`ACTION_OWNED_MOVING_FORMED_BRANCH_QDOT_SIGMADOT_L2_CROSS_KINETIC_AND_COVARIANT_SYMPLECTIC_PULLBACK_WITH_DYNAMIC_SIGMA_TRANSFER_BACKREACTION_AND_NONLINEAR_FORCED_JOIN_CONTINUATION`

No Aether metric or primitive time, empirical input, fitted coefficient,
external frame, frozen prediction, Git operation, or removable medium was
used.
