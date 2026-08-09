# BHSM v14.49 — Zeta-Spectral Ray and Input-Compression Theorem

## Primary verdict

`BHSM_A_CURVATURE_INDEPENDENT_DIRAC_TYPE_A4_OR_ZETA_LOCAL_ACTION_COLLAPSES_THE_R2_RICCI2_AND_GAUGE_DIMENSION_FOUR_COEFFICIENTS_TO_ONE_SPECTRAL_RAY_BUT_THIS_IS_FOUNDATIONAL_DATA_NOT_DERIVED_FROM_PATH_B`

## Secondary verdict

`THE_PURE_DIRAC_GRAVITATIONAL_A4_VARIATION_OBEYS_3_C_R2_PLUS_C_RICCI2_EQUALS_ZERO_MODULO_GAUSS_BONNET_AND_ONE_NONDEGENERATE_BERGER_MODULUS_EQUATION_CAN_THEN_FIX_THE_REMAINING_RAY_AMPLITUDE`

## 1. Question

v14.48 proved that the current local effective action cannot determine, from cap
regularity and one Berger-modulus condition alone, the four independent inputs

\[
\{c_{R^2}^{\rm ren},c_{R_{\mu\nu}^2}^{\rm ren},c_{\rm YM},L_*\}.
\]

This sprint tests the strongest internal input-compression mechanism still
compatible with the foundational Dirac sector adopted in v14.45: use the local
heat-kernel coefficient of one fully specified BHSM Dirac-type operator as the
common source of all dimension-four bosonic terms.

This is a **conditional foundational branch**.  The current Path-B bosonic
action does not derive the spectral functional.

## 2. Generic cutoff spectral action

For a positive Laplace-type operator \(P=D^2\) in four dimensions,

\[
\operatorname{Tr}f(P/\Lambda^2)
\sim
f_4\Lambda^4 a_0(P)
+f_2\Lambda^2a_2(P)
+f_0a_4(P)
+\cdots.
\]

A generic cutoff function therefore introduces independent moments
\(f_4,f_2,f_0\).  Naming a spectral action does not select these moments or the
matching scale.  Nevertheless, every dimension-four term in \(a_4\), including
gauge kinetic and curvature-squared terms, carries the same overall moment
\(f_0\).  Once the Dirac bundle and representation trace are fixed, their
relative coefficients lie on one spectral ray.

## 3. Pure Dirac gravitational ray

For a minimal Dirac-type operator whose response endomorphism does not itself
contain curvature, the pure spin-connection part of \(a_4\) has a dynamical
curvature-squared contribution proportional to Weyl curvature squared plus an
Euler-density term.

In four dimensions,

\[
C_{\mu\nu\rho\sigma}C^{\mu\nu\rho\sigma}
=
E_4
+2R_{\mu\nu}R^{\mu\nu}
-\frac23R^2.
\]

The Euler density has no local bulk field equation on a closed smooth
four-manifold.  Modulo this topological term, a representative coefficient ray
is

\[
(c_{R^2},c_{R_{\mu\nu}^2})
=s\left(-\frac23,2\right).
\]

Therefore

\[
\boxed{3c_{R^2}+c_{R_{\mu\nu}^2}=0.}
\]

This is not the result of cap regularity.  It is the local coefficient relation
selected by the minimal Dirac \(a_4\) structure.

The relation can be modified if the complete BHSM response endomorphism contains
explicit curvature dependence.  That audit remains mandatory.

## 4. Compact-cap projection

v14.47 established the structural projections

\[
\mathcal H_L[R^2]=Aq_L,
\]

\[
\mathcal H_L[R_{\mu\nu}R^{\mu\nu}]
=Bq_L+Cq_L^2,
\qquad
q_L=(L-1)(L+3).
\]

On the spectral ray,

\[
\mathcal H_L^{\rm spectral}
=s\left[
-\frac23Aq_L
+2Bq_L
+2Cq_L^2
\right].
\]

The \(L=2,3\) local channel pair is now a one-parameter vector rather than a
rank-two plane.  Its amplitude is still unknown until a normalization principle
or a nondegenerate stationarity equation is supplied.

## 5. Berger-modulus closure condition

If the Berger anisotropy is promoted to a genuine action variable and all terms
are evaluated on one common domain, its Euler equation becomes

\[
0
=
s\frac{d\mathcal A_{\rm spectral}}{d\log a}
+\frac{d\Pi_{\rm nonlocal}}{d\log a}.
\]

When

\[
\frac{d\mathcal A_{\rm spectral}}{d\log a}\ne0,
\]

this fixes the remaining dimensionless amplitude:

\[
\boxed{
 s
 =
-\frac{\Pi_{\rm nonlocal}'(a)}
       {\mathcal A_{\rm spectral}'(a)}.
}
\]

This is an exact closure formula, not a numerical result.  Neither derivative
has yet been evaluated for the complete BHSM Dirac bundle and full-preimage
background.

## 6. Gauge normalization

The gauge kinetic terms also arise in \(a_4(D^2)\).  Their ratios are determined
by the internal representation trace.  On this branch the common gauge
normalization and the curvature-squared amplitude are not independent: they
share the same spectral normalization.

Thus the spectral-ray branch can compress

\[
\{c_{R^2},c_{R_{\mu\nu}^2},c_{\rm YM}\}
\]

to one dimensionless amplitude, provided the complete Dirac operator and trace
are specified.

## 7. Zeta-local declaration

A cutoff-moment-free foundational option is to declare

\[
S_{\zeta,\rm local}:=a_4(D_{\rm BHSM}^2)
\]

after the collective zero-mode quotient and parent-relative subtraction.
Choosing this action with unit coefficient removes the continuous \(f_0\)
input by definition.  It is a model postulate, not a theorem derived from Path
B.  The Euclidean sign must be chosen so that the gauge kinetic form is
positive.

Even this strongest branch does not determine the absolute physical scale.
It also does not bypass the required calculation of the full internal trace,
Kosmann spectral sums, nonlocal determinant, nonlinear branch, confinement or
neutral scale.

## 8. Input count

### Generic effective branch

Four continuous foundational inputs remain:

1. \(c_{R^2}^{\rm ren}(\mu_*)\),
2. \(c_{R_{\mu\nu}^2}^{\rm ren}(\mu_*)\),
3. \(c_{\rm YM}(\mu_*)\),
4. \(L_*\) or \(E_*\).

### Generic cutoff-spectral branch

The dimension-four coefficients share \(f_0\), but the cutoff action retains
independent moments and scale data.

### Canonical zeta-local declaration

The dimensionless local ray is fixed by the fully specified operator and unit
spectral normalization.  The absolute scale remains open.

## 9. Hindsight 20/20

### Validated

- A minimal Dirac \(a_4\) coefficient selects the relation
  \(3c_{R^2}+c_{R_{\mu\nu}^2}=0\) modulo the Euler density.
- Gauge and curvature-squared coefficients share one dimension-four spectral
  normalization.
- One nondegenerate Berger-modulus equation can fix that one remaining
  dimensionless amplitude.
- A zeta-local action avoids arbitrary cutoff moments if adopted as foundational
  data.

### Invalidated

- Claiming that merely naming a spectral action fixes its cutoff moments.
- Claiming that the current Path-B action derives the zeta-local functional.
- Claiming that the pure Dirac coefficient relation survives an arbitrary
  curvature-dependent response endomorphism without audit.
- Claiming that dimensionless spectral closure fixes the absolute physical
  scale.

### Open

- the complete BHSM Dirac bundle and species trace;
- curvature dependence of the response endomorphism;
- exact gauge/gravity coefficient ratios;
- Berger-modulus local and nonlocal derivatives;
- normalized \(L=2,3\) Kosmann sums and zero crossing;
- nonlinear flavor branch, CKM and CP;
- nonperturbative Wilson sector;
- neutral scale and absolute physical scale.

## 10. Completion status

BHSM remains physically incomplete.  The zeta-local branch is a precise
foundational candidate that reduces the remaining dimensionless input rank; it
has not been adopted into the official action or evaluated numerically.  Frozen
predictions are unchanged and the USB remains untouched.

## Exact next object

`FULL_BHSM_DIRAC_BUNDLE_A4_TRACE_WITH_CURVATURE_RESPONSE_AUDIT_GAUGE_AND_GRAVITY_COEFFICIENT_RATIOS_BERGER_MODULUS_STATIONARITY_AND_ABSOLUTE_SCALE_SELECTION`
