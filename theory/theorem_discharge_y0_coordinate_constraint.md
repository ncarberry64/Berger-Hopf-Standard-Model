# PO-BH-32 — y0 Coordinate Constraint Theorem

## Mission

This theorem-discharge layer continues the Berger–Hopf Standard Model derivation program toward a complete derivation of Standard Model structure from Berger–Hopf boundary geometry.

The immediate target is the universal internal sampling point

\[
y_0=(\alpha_0,\beta_0,\gamma_0)
\]

that enters the generic Wigner/Hopf harmonic evaluation layer.

## Previous theorem layers achieved

Earlier theorem-discharge layers established:

\[
q=k-2j,\qquad k=q+2j
\]

\[
\ell=\frac{k}{2},\qquad n=\frac{q}{2},\qquad j=\ell-n
\]

and the full admissible multiplet scaffold

\[
\left\{D^{k/2}_{m,q/2}(y)\right\}_{m=-\ell}^{+\ell}.
\]

The previous generic-y0 layer then defined

\[
D^{k/2}_{m,q/2}(y_0)
=
e^{-im\alpha_0}
d^{k/2}_{m,q/2}(\beta_0)
e^{-i(q/2)\gamma_0}.
\]

## Why y0 coordinates are the next blocker

The current Yukawa/harmonic pipeline no longer depends on choosing a single m-weight. The remaining structural question is whether the universal coordinate triple

\[
(\alpha_0,\beta_0,\gamma_0)
\]

is fixed, constrained, gauge-removable, or still open.

This theorem layer does not attempt to fit these values to observed fermion masses or mixing. It only audits what follows from the BHSM geometry and existing repo theorem machinery.

## Generic Wigner evaluation at y0

Using the PO-BH-27 and PO-BH-31 conventions,

\[
D^\ell_{m,n}(\alpha,\beta,\gamma)
=
e^{-im\alpha}
d^\ell_{m,n}(\beta)
e^{-in\gamma}.
\]

With

\[
\ell=\frac{k}{2},\qquad n=\frac{q}{2},
\]

this becomes

\[
D^{k/2}_{m,q/2}(y_0)
=
e^{-im\alpha_0}
d^{k/2}_{m,q/2}(\beta_0)
e^{-i(q/2)\gamma_0}.
\]

## Coordinate scaffold alpha0, beta0, gamma0

The symbolic scaffold is:

\[
y_0=(\alpha_0,\beta_0,\gamma_0).
\]

Here:
- \(\alpha_0\) enters through \(e^{-im\alpha_0}\);
- \(\gamma_0\) enters through \(e^{-i(q/2)\gamma_0}\);
- \(\beta_0\) enters through \(d^{k/2}_{m,q/2}(\beta_0)\).

## Alpha/gamma phase structure

The \(\alpha_0\) and \(\gamma_0\) coordinates appear as Wigner phase coordinates. Their role is therefore phase-like at this layer. They may become relevant for future complex mixing phases, but this theorem layer does not derive CKM or PMNS phases.

## Alpha/gamma gauge-fixing audit

This layer does not assume that \(\alpha_0\) or \(\gamma_0\) are removable by gauge or coordinate choice. A future theorem may promote gauge-fixing if the repo explicitly proves a residual symmetry or coordinate convention allowing one or both phases to be set without physical loss.

Default status:

\[
\text{alpha/gamma gauge-fixing remains open}.
\]

## Beta0 as reduced-Wigner magnitude selector

The coordinate \(\beta_0\) controls the reduced Wigner factor:

\[
d^{k/2}_{m,q/2}(\beta_0).
\]

This makes \(\beta_0\) the main magnitude selector in the generic-y0 harmonic feature scaffold. This is structural from Wigner factorization, not a numerical fit.

## Beta0 geometry constraint audit

This theorem layer searches for, but does not assume, a derivation of \(\beta_0\) from Berger squashing, scalar/topographic localization, Hopf-axis selection, focal-point geometry, or a repo-defined internal coordinate convention.

Unless such a derivation exists, \(\beta_0\) remains an open universal geometric selector.

## Axis-collapse beta0 audit

The axis-collapse limit is:

\[
\beta_0=0
\]

or an equivalent Hopf-axis/pole/identity-point condition. Then:

\[
d^\ell_{m,n}(0)=\delta_{mn},
\]

and the multiplet collapses to the leading component

\[
m=n=\frac{q}{2}.
\]

This branch does not promote that case unless axis status is derived elsewhere in the repo.

## Generic beta0 selector status

If no axis-collapse or geometry-fixed value is derived, BHSM retains the generic symbolic selector

\[
0\leq\beta_0\leq\pi
\]

with \(\beta_0\) treated as open and universal, not fit to data.

## Bridge to feature-rank independence

The y0-coordinate scaffold feeds the feature multiplets:

\[
F_{k,q}(y_0)=
\left\{
D^{k/2}_{m,q/2}(y_0),
\partial_aD^{k/2}_{m,q/2}(y_0),
\partial_a\partial_bD^{k/2}_{m,q/2}(y_0)
\right\}_{m=-\ell}^{+\ell}.
\]

Rank-three support requires that three generation-mode feature multiplets remain independent under universal finite-width moment contractions. That theorem is not discharged here.

## Numerical Yukawa status

No numerical Yukawa values are derived in this layer.

## CKM/PMNS status

No CKM or PMNS values are derived in this layer.

## Non-tautology audit

This layer does not choose \(\beta_0\) to match masses, set \(\beta_0=0\) by convenience, force \(m=q/2\), use observed CKM or PMNS values, or alter frozen predictions.

## What this achieves

This branch isolates the next precise bottleneck:

\[
\text{derive or constrain }y_0=(\alpha_0,\beta_0,\gamma_0).
\]

It conditionally derives the phase/magnitude role of the coordinates and preserves the open status of coordinate fixing unless repo proof exists.

## What remains before full BHSM replacement claim

Remaining downstream obligations include deriving or constraining \(\beta_0\) from geometry, deciding whether \(\alpha_0,\gamma_0\) are gauge-removable or physical phases, evaluating reduced Wigner feature multiplets, proving finite-width rank-three independence, deriving numerical Yukawa values, and deriving CKM and PMNS.

## Conclusion

This branch derives the y0 coordinate-constraint scaffold. In the generic Wigner evaluation, alpha0 and gamma0 enter as phase coordinates while beta0 controls the reduced-Wigner magnitude selector. The branch does not fit these coordinates to fermion masses or mixing data. Unless repo geometry fixes beta0 or derives an axis-collapse case, beta0 remains an open universal geometric selector. Finite-width rank-three support, numerical Yukawa values, CKM, PMNS, and replacement readiness remain open.

Follow-up: `theory/theorem_discharge_generic_finite_width_feature_rank.md` turns the symbolic y0 feature data into a finite-width Gram/minor rank-support problem while keeping nonzero determinant and rank-three claims open.

Follow-up: `theory/theorem_discharge_explicit_symbolic_gram_minor.md` enumerates explicit symbolic minor candidates for that rank-support problem without promoting a nonzero determinant.
