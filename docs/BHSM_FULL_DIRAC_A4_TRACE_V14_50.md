# BHSM v14.50 — Full Dirac `a4` Trace, Curvature-Response, Gauge-Ratio, and Scale Audit

## Primary verdict

`BHSM_V14_50_THE_DOCUMENTED_ETA_HIGGS_AND_FAMILY_RESPONSES_ARE_CURVATURE_INDEPENDENT_AND_PRESERVE_THE_MINIMAL_DIRAC_A4_GRAVITATIONAL_RAY_BUT_THE_UNDEFINED_PHI_RESPONSE_CAN_REOPEN_THE_R2_DIRECTION`

## Gauge verdict

`THE_CANONICAL_THREE_GENERATION_STANDARD_MODEL_FERMION_TRACE_GIVES_K_Y_K_2_K_3_EQUALS_5_OVER_3_1_1_AFTER_NORMALIZATION_AND_DOES_NOT_GENERATE_THE_HISTORICAL_BHSM_1_2_7_PATTERN`

## Scale verdict

`THE_FOUR_DIMENSIONAL_ZETA_LOCAL_A4_FUNCTIONAL_IS_GLOBALLY_SCALE_INVARIANT_AND_CANNOT_SELECT_THE_ABSOLUTE_BHSM_LENGTH_OR_ENERGY_SCALE`

---

## 1. Heat-kernel contract

For a Laplace-type operator

\[
P=-(\nabla^2+E),
\]

the local four-dimensional coefficient contains

\[
a_4(P)\supset
\frac{1}{360(4\pi)^2}
\int\sqrt g\,\operatorname{tr}
\left[
60RE+180E^2+30\Omega_{\mu\nu}\Omega^{\mu\nu}
+5R^2-2R_{\mu\nu}^2+2R_{\mu\nu\rho\sigma}^2
\right].
\]

The v14.49 one-ray result is valid only when the extra BHSM response does not
introduce an independent curvature endomorphism.

## 2. Curvature-response theorem

Use the minimal Dirac convention

\[
E_0=-\frac14R\,I+E_{\rm gauge}+E_{\rm scalar}.
\]

Add the most general scalar linear-curvature response

\[
E_{\rm curv}=\xi R I.
\]

The additional pure `R^2` numerator from `60RE+180E^2` is

\[
\Delta c_{R^2}^{(\rm numerator)}
=
30\,\operatorname{rank}(E)\,\xi(6\xi-1).
\]

Therefore the minimal gravitational ray is unchanged only for

\[
\boxed{\xi=0\quad\text{or}\quad\xi=\frac16.}
\]

The second value is an algebraic heat-kernel cancellation point. It is not an
automatic BHSM prediction.

The documented eta odd mass

\[
m_\eta(s)=-\partial_s\log\sin f_\eta(s)
\]

and the finite family/Higgs operators have no explicit four-dimensional
curvature dependence. They therefore do not themselves reopen the pure
curvature-squared plane before scalar fields are integrated out.

However, the retained symbol `Phi_response` has never been given a complete
action-owned formula. The complete spectral ray is consequently conditional on
one of the following explicit declarations:

1. `Phi_response` is curvature independent;
2. its only scalar-curvature term has `xi=1/6` in the stated convention;
3. the full response is supplied and its trace is recomputed.

## 3. Canonical gauge trace

For one canonical Standard Model generation, including an optional sterile
right-handed neutrino, use

\[
T(\mathbf N)=\frac12
\]

for the non-Abelian fundamental generators and ordinary hypercharge `Y`.
The traces are

\[
K_Y
=
6\left(\frac16\right)^2
+3\left(\frac23\right)^2
+3\left(\frac13\right)^2
+2\left(\frac12\right)^2
+1
=
\frac{10}{3},
\]

\[
K_2=3\left(\frac12\right)+\frac12=2,
\]

\[
K_3=2\left(\frac12\right)+\frac12+\frac12=2.
\]

Three families, particle/antiparticle doubling, and a neutral right-handed
neutrino multiply all rows by common factors or zero and do not change the
ratios. Thus

\[
\boxed{K_Y:K_2:K_3=\frac53:1:1.}
\]

Equivalently,

\[
g_2^2=g_3^2=\frac53g_Y^2
\]

at the spectral matching scale, before RG transport.

This canonical trace does **not** generate the historical BHSM `1:2:7` coupling
pattern. In particular, equality of the `SU(2)` and `SU(3)` trace coefficients
cannot be changed into `2:7` by a hypercharge normalization convention.

Recovering a different ratio requires at least one of:

- action-owned nonuniform internal spectral weights;
- additional nonuniversal states;
- inequivalent gauge-factor kinetic normalizations outside the single spectral
  trace.

The repository has previously rejected `1:2:7` as an already-derived
representation trace. v14.50 preserves that negative result.

## 4. Berger-cylinder diagnostic

For the product diagnostic `R x S^3_a` with

\[
h_a=R^2(\sigma_1^2+\sigma_2^2+a^2\sigma_3^2),
\]

the four-dimensional Weyl invariant is

\[
\boxed{
C^2
=
\frac{64}{3R^4}(a^2-1)^2.
}
\]

After the Berger volume is included, the dimensionless shape factor is

\[
F(a)=a(a^2-1)^2,
\]

with

\[
F'(a)=(a^2-1)(5a^2-1).
\]

The nondegenerate round point `a=1` is stationary. The frozen nonround BHSM
value is not selected by this local Weyl term alone. This product calculation is
a diagnostic only; the physical compact cap includes the collar, lapse,
parent-relative subtraction, eta profile, and nonlocal determinant.

## 5. Absolute-scale theorem

In four dimensions,

\[
\int\sqrt g\,C^2,
\qquad
\int\sqrt g\,F^2,
\qquad
a_4(D^2)
\]

have global metric scaling weight zero. Under

\[
g_{\mu\nu}\mapsto L^2g_{\mu\nu},
\]

the local zeta action is unchanged.

Therefore

\[
\boxed{
S_{\zeta,\rm local}=a_4(D_{\rm BHSM}^2)
\quad\text{cannot select }L_*\text{ or }E_*.
}
\]

An absolute scale requires an additional dimensionful mechanism:

- an `a2` or `a0` spectral moment and cutoff scale;
- the eta parameter `kappa_1` fixed by a parent equation;
- dimensional transmutation with a declared reference condition;
- a nondegenerate parent-child quasilocal or DtN eigenvalue.

## 6. Completion consequence

The v14.49 zeta-local branch survives only as the following conditional model:

1. adopt the local Dirac action and zeta-local `a4` action as foundational data;
2. declare or derive the complete curvature response;
3. either accept the canonical `5/3:1:1` trace or derive a new action-owned
   internal weight/state content;
4. derive the nonlocal Berger response and `L=2,3` Kosmann sums;
5. provide a separate absolute-scale mechanism.

It cannot simultaneously preserve the historical `1:2:7` gauge pattern and
claim that all gauge kinetic terms arise from the unweighted canonical fermion
trace.

## Hindsight 20/20

### Validated

- The documented eta mass and finite family/Higgs terms are explicitly
  curvature independent.
- An explicit `xi R` response changes only the `R^2` direction by
  `30 xi (6 xi - 1)` per internal rank in the stated convention.
- `xi=0` and `xi=1/6` are the only ray-preserving scalar-curvature values.
- The canonical fermion trace is `5/3:1:1`.
- The local `a4` functional cannot select an absolute scale.
- The local Berger-cylinder Weyl term does not select the frozen nonround
  anisotropy.

### Invalidated

- Treating undefined `Phi_response` as automatically curvature independent.
- Deriving `1:2:7` from the canonical Standard Model species trace.
- Using local `a4` scale invariance as dimensional-scale generation.
- Claiming the local Weyl term alone selects the frozen Berger value.

### Open

- complete action-owned `Phi_response`;
- internal spectral weights or additional state content;
- exact gauge/gravity coefficient ratios on that completed bundle;
- nonlocal Berger derivative;
- normalized `L=2,3` Kosmann determinant;
- absolute scale, confinement, neutral scale, CKM and CP.

## Exact next object

`ACTION_SELECTED_INTERNAL_SPECTRAL_WEIGHT_OR_EXTENDED_STATE_CONTENT_WITH_COMPLETE_CURVATURE_RESPONSE_ENDOMORPHISM_AND_A_SEPARATE_DIMENSIONAL_TRANSMUTATION_OR_PARENT_CHILD_SCALE_EIGENVALUE`

BHSM remains incomplete. Frozen predictions are unchanged. No physical coupling,
scale, mass, CKM matrix, or CP phase is emitted.
