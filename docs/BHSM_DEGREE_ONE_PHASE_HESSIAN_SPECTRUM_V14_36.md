# BHSM v14.36 degree-one phase-Hessian spectrum

## Question

Does the Path B `p=2+p=8` eta action turn on the nonaxisymmetric Hopf-phase bifurcation required by the v14.35 flavor texture?

The tested channels are

\[
(\ell,p)=(2,2),(4,4),(6,6),(8,8),(10,8).
\]

## 1. Exact phase-Hessian theorem

Let the physical eta action density be

\[
F(X)=\frac{\kappa_1}{2}X+\frac18X^4,
\qquad X=|D\eta|^2,
\]

and let `T` generate a target-space isometry.  A local phase deformation is

\[
\eta_\epsilon=\exp(\epsilon\phi T)\eta.
\]

Writing

\[
j_\mu=\langle D_\mu\eta,T\eta\rangle,
\]

the kinetic scalar changes as

\[
X_\epsilon
=X+2\epsilon j^\mu\partial_\mu\phi
+\epsilon^2|T\eta|^2|d\phi|^2.
\]

On a stationary background with admissible boundary flux, the linear term vanishes by the Noether equation. The exact second variation is

\[
\delta^2S_{\rm phase}
=\int d\mu\,w\left[
2F'(X)|T\eta|^2|d\phi|^2
+4F''(X)(j\cdot d\phi)^2
\right].
\]

For the Path B density,

\[
F'(X)=\frac12(\kappa_1+X^3)>0,
\qquad
F''(X)=\frac32X^2\ge0.
\]

Therefore

\[
\boxed{\delta^2S_{\rm phase}\ge0.}
\]

A globally constant phase is an exact collective symmetry mode. Every nonconstant harmonic phase has positive quadratic cost. The pure Path B action cannot create a negative phase mode.

## 2. Round-smash degree-one surrogate

The only currently constructed degree-one stationary profile is the v13.1 flat-\(\mathbb R^7\) hedgehog. It can be used conditionally as the round base-fiber smash surrogate, but it does not constitute the still-missing physical compact-cap full-preimage solution.

For the lower-bound phase operator, the nonnegative `F''` current-square term is omitted. In `x=log r`, the quadratic form is

\[
Q_{\ell,p}[\psi]
=\int dx\,A(x)
\left[(\partial_x\psi)^2+\lambda_{\ell,p}\psi^2\right],
\]

with kinetic norm

\[
\|\psi\|^2=\int dx\,C(x)\psi^2,
\]

where

\[
A=e^{5x}(\kappa_1+X^3)\sin^2f,
\qquad
C=e^{7x}(\kappa_1+X^3)\sin^2f,
\]

and

\[
\lambda_{\ell,p}
=\ell(\ell+2)+(a^2-1)p^2.
\]

At the frozen anisotropy, the five angular costs are approximately

| Channel | `lambda_(ell,p)` |
|---|---:|
| `(2,2)` | 9.355097092071 |
| `(4,4)` | 29.420388368285 |
| `(6,6)` | 60.195873828642 |
| `(8,8)` | 101.681553473142 |
| `(10,8)` | 141.681553473142 |

The lowest finite-box generalized eigenvalues are:

| Channel | `[-6,4]` | `[-7,5]` | `[-8,6]` |
|---|---:|---:|---:|
| `(2,2)` | 0.023452431438 | 0.003174940235 | 0.000438734552 |
| `(4,4)` | 0.036753443604 | 0.004976219888 | 0.000688114499 |
| `(6,6)` | 0.055035130021 | 0.007450461099 | 0.001031578446 |
| `(8,8)` | 0.077784318345 | 0.010526914900 | 0.001458653450 |
| `(10,8)` | 0.098572857683 | 0.013336096820 | 0.001846964412 |

Every value is positive. The lowest values move toward zero as the noncompact box expands. This is consistent with essential spectrum beginning at zero, not with a negative normalizable mode and not with a positive physical mass gap.

## 3. Bifurcation verdict

The requested flavor-phase bifurcation does **not** turn on from the pure Path B `p=2+p=8` action:

```text
BHSM_PATH_B_DEGREE_ONE_PHASE_HESSIAN_IS_NONNEGATIVE_AND_THE_REQUESTED_HOPF_FLAVOR_CHANNELS_HAVE_NO_NEGATIVE_MODE_ON_THE_ROUND_SMASH_SURROGATE
```

This result is narrower than full stability. It does not evaluate:

- non-isometric shape modes of the eta map;
- the complete compact-cap self-adjoint Hessian;
- gauge, Wilson, metric or scalar mixing blocks;
- the v12 relative-holonomy contribution;
- the nonlinear bifurcated branch after a source is attached.

## 4. What can still turn on the branch

The most economical candidate is the already identified v12 relative holonomy. It must be attached to the same action and background so that it contributes a signed phase potential

\[
\delta^2S_{\rm hol}
=\sum_{\ell,p}\int dx\,V^{\rm hol}_{\ell,p}(x)|\psi_{\ell,p}|^2.
\]

A bifurcation can occur only if the complete lowest eigenvalue crosses zero:

\[
\lambda_{0,\ell,p}
\left(H_{\rm PathB}+H_{\rm hol}+H_{\rm other}\right)=0.
\]

The next exact object is

```text
ACTION_ATTACHMENT_OF_THE_V12_RELATIVE_HOLONOMY_OR_OTHER_SIGNED_PHASE_POTENTIAL_TO_THE_DEGREE_ONE_FULL_PREIMAGE_HESSIAN_WITH_SELF_ADJOINT_CAP_DOMAIN_AND_FULL_NONISOMETRIC_SHAPE_SPECTRUM
```

## Claim boundary

No physical CKM matrix, CP phase, Jarlskog invariant, quark mass, absolute scale or confinement result is emitted. Frozen predictions are unchanged.
