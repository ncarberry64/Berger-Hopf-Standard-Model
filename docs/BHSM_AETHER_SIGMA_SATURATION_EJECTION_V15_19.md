# BHSM transient sigma activation, saturation and ejection audit

## Exact conservative formation trajectory

For (m>0), the reduced v15.9 equation

\[
 \ddot q-aq+bq^3=0,
 \qquad
 a=\frac{5m}{6a_c^2},
 \quad b=\frac{23}{54a_c^2},
\]

has the exact zero-energy homoclinic solution

\[
 q(\tau)=\sqrt{\frac{90m}{23}}
 \operatorname{sech}\!\left(\sqrt{\frac{5m}{6a_c^2}}\tau\right).
\]

Its velocity vanishes at both asymptotic ends and at the central turning
point. The two velocity maxima satisfy

\[
 q^2=\frac{45m}{23},\qquad
 \max\dot q^2=\frac{75m^2}{92a_c^2}.
\]

With (M_q=3a_c^2/2),

\[
 \boxed{M_q\max\dot q^2=\frac{225}{184}m^2.}
\]

For a constant-curvature control, the exact activation condition is

\[
 g\frac{225}{184}m^2>K_{\sigma,\rm static}.
\]

When it holds, there are two finite intervals in which the sigma tangent
curvature is negative. This is a transient tachyonic/spinodal instability,
not Floquet instability: the conservative homoclinic coefficient is a pulse,
not periodic. A physical periodic formation orbit could reopen Floquet
analysis, but none is presently action-selected.

The actual v15.9 sigma curvature also changes with the eta profile:

\[
 K_{\sigma,\rm static}(t)=A_0+g\left[
 \kappa_1X_\eta(q(t))+\frac14X_\eta(q(t))^4\right].
\]

Consequently the displayed window endpoints are not physical predictions.
They require the full Lorentzian profile (X_\eta(q(t))) and the still-open
alpha/r response. What is robust is the classification: composing any local
curvature with the conservative homoclinic trajectory remains nonperiodic,
so a crossing is transient rather than Floquet.

## Stable backreaction cannot manufacture positive saturation

Let a stable response block (y) couple through

\[
 V=\frac14G_{\rm dir}\sigma^4
 +\sigma^2B^Ty+\frac12y^THy,
 \qquad H\succ0.
\]

Eliminating (y) gives

\[
 \boxed{G_{\rm eff}=G_{\rm dir}-2B^TH^{-1}B\le G_{\rm dir}.}
\]

Thus positive-block metric/localization backreaction softens the quartic. If
the direct quartic is zero and (B\ne0), the induced quartic is negative;
it cannot stabilize the new sigma branch.

Likewise, if

\[
 I_{qq}=M_q(1+g\sigma^2+h\sigma^4+\cdots),
\]

then the Lorentzian dynamic contribution is

\[
 \Delta G=-2hM_q\dot q^2.
\]

A positive (h) softens further. A negative (h) could stabilize, but no
such action-derived fourth inertia variation exists in the retained kernel.
At finite frequency (H-\omega^2M) need not be positive, but then local
stable Schur elimination fails near dynamical poles and the full nonlocal
system must be solved.

## Contact cross inertia

For an already-derived positive kinetic metric on physical coordinates
((q,d)),

\[
 P_d=I_{dd}\dot d+I_{dq}\dot q,
 \qquad I_{dq}^2<I_{qq}I_{dd}.
\]

This confirms that cross inertia could redirect formation momentum without
a kick coefficient.

It is not present on the retained round seam. The exact moving-trace law is

\[
 \delta h=\operatorname{Tr}(\delta g)+2dK.
\]

At the round equator (K=0), so pure normal displacement is an exact
first-order metric-trace kernel. Independent work also proves that pure cap
repartition has zero total-action inertia. Hence the round first-order
(I_{dq}) is zero. A physical coupling requires a nonround stationary
(K_{ab}\ne0) background or second shape variation, followed by constraint
and symplectic reduction that turns (d) into a genuine canonical mode.

## Completion boundary

The retained dynamics can open a finite sigma instability window, but it
does not supply the positive nonlinearity that stops the instability or the
canonical separation mode that receives formation momentum.

The exact next object is:

`ACTION_OWNED_NONROUND_OR_SECOND_SHAPE_M5_M4_LOCALIZATION_INERTIA_KERNEL_WITH_DIRECT_POSITIVE_SIGMA_QUARTIC_CANONICAL_SEPARATION_MODE_AND_NONZERO_Q_TO_D_SYMPLECTIC_TRANSFER_ON_THE_V15_9_FORMATION_TRAJECTORY`

`FULL_BHSM_COMPLETE = FALSE`.
