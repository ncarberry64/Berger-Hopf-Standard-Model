# BHSM coherent inertia and fixed-momentum saturation theorem

## The ensemble correction

The v15.19 fixed-velocity calculation and stable-response Schur theorem are
correct, but they do not exhaust inertia physics. With

\[
 I_{qq}(\sigma)=M_q(1+g\sigma^2),
\]

the Legendre transform at fixed canonical momentum gives

\[
 H_{\rm kin}=\frac{p_q^2}{2M_q(1+g\sigma^2)}.
\]

Its expansion is

\[
 H_{\rm kin}=\frac{p_q^2}{2M_q}
 \left(1-g\sigma^2+g^2\sigma^4+O(\sigma^6)\right).
\]

Thus the action already generates the positive Hamiltonian quartic

\[
 \boxed{G_{\rm inertia}=\frac{2p_q^2g^2}{M_q}>0.}
\]

This does not integrate out a stable response field and therefore does not
contradict
(G_{\rm eff}=G_{\rm dir}-2B^TH^{-1}B).

## Exact inertial saturation

With no direct quartic, the instantaneous sigma Hamiltonian is

\[
 H_\sigma(\sigma;p_q)=
 \frac{p_q^2}{2M_q(1+g\sigma^2)}
 +\frac12K_{\rm static}\sigma^2.
\]

It is bounded for (K_{\rm static}>0). When

\[
 \frac{p_q^2g}{M_q}>K_{\rm static},
\]

the exact stable extrema are

\[
 \boxed{
 \sigma_\pm^2=
 \frac{\sqrt{p_q^2g/(M_qK_{\rm static})}-1}{g}.}
\]

This is genuine finite saturation from inverse inertia, not a bare sigma
self-quartic. Since the v15.9 coordinate is not cyclic, (p_q) is a
canonical state variable rather than a conserved constant. The formula is an
instantaneous Hamiltonian or adiabatic branch until the full coupled
((q,p_q,\sigma,p_\sigma)) flow is solved.

## Multi-channel interference identity

Let

\[
 I(\sigma)=I_0+\sigma^2I_2,
 \quad
 z=I_0^{-1/2}p,
 \quad
 B=I_0^{-1/2}I_2I_0^{-1/2}.
\]

Then

\[
 \frac12p^TI(\sigma)^{-1}p
 =\frac12\|z\|^2
 -\frac12\langle z,Bz\rangle\sigma^2
 +\frac12\|Bz\|^2\sigma^4+cdots.
\]

Therefore

\[
 \boxed{G_{\rm inertia}=2\|Bz\|^2\ge0.}
\]

The cross terms inside (|Bz|^2) are precisely inertial interference.
Relative phases can enhance, suppress, or cancel particular components, but
phase locking is not needed to prove the nonnegative total sign. It is
needed—together with the physical incidence map—to fix the magnitude and
prove it is nonzero on the selected state.

A second positive construction is possible if a fixed nonlinear incidence
has

\[
 \mathcal A(\sigma)=c\sigma^2+O(\sigma^4),
 \qquad E=\frac12\|\mathcal A\|_G^2.
\]

Then (G_{\rm int}=2c^*Gc>0) for nonzero (c). This is distinct from a
relaxable response variable, whose elimination invokes the v15.19 softening
theorem.

## What the attachment geometry supplies

The recovered attachment tangent kinetic Gram is

\[
 K_\parallel=\begin{pmatrix}2&1\\1&2\end{pmatrix}.
\]

Its positive off-diagonal overlap comes from the two constraint-tangent
directions sharing the core coordinate (q_C). The matcher signs are real
and fixed. Nevertheless, canonical incidence whitening produces orthonormal
tangent channels, showing that an off-diagonal coordinate Gram entry is not
alone an invariant interference prediction.

The missing physical maps are now exact:

- the second-sigma nonlinear incidence (c_{\sigma^2}) into the attachment
  tangent space;
- the differential incidence of formation (q);
- the differential incidence of physical separation (d);
- global selection of the attachment curvatures and nonround/second-shape
  background.

The global spin lift fixes fermion transmission, not phases between
independent bosonic inertia channels. The Hopf connection can transport a
declared representation along declared paths, but those physical channel
paths are not selected.

Finally, the retained action still contains independent (G_0). The
inertial identity cannot silently delete it. Replacing (G_0) requires an
upstream parent-action or uniqueness theorem establishing that sigma's
nonlinearity is entirely inertial.

The exact next object is:

`ACTION_OWNED_SECOND_SIGMA_AND_Q_D_DIFFERENTIAL_INCIDENCE_MAP_INTO_THE_GLOBALLY_SELECTED_COMMON_ATTACHMENT_GRAM_HESSIAN_ON_A_NONROUND_OR_SECOND_SHAPE_M5_M4_STATE_WITH_CANONICAL_FORMATION_AND_SEPARATION_MOMENTA`

`FULL_BHSM_COMPLETE = FALSE`.
