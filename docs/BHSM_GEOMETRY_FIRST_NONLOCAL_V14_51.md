# BHSM v14.51 — Geometry-First Internal Trace, Relative Determinant, and Berger-Scale Gate

## Primary verdict

`BHSM_V14_51_EXACT_BUNDLE_TRACE_RECONSTRUCTION_DOES_NOT_DERIVE_THE_HISTORICAL_1_2_7_GAUGE_PATTERN`

## Scale verdict

`BHSM_PARENT_RELATIVE_NONLOCAL_DETERMINANT_CAN_SUPPLY_LOGARITHMIC_SCALE_DEPENDENCE_ONLY_THROUGH_A_NONZERO_RELATIVE_ZETA_ANOMALY_AND_REQUIRES_A_SECOND_SCALE_DEPENDENT_TERM_FOR_A_FINITE_STABLE_SCALE`

## Curvature-response verdict

`BHSM_MINIMAL_CONNECTION_AND_DOCUMENTED_ETA_HIGGS_RESPONSE_LOCK_THE_ADDITIONAL_SCALAR_CURVATURE_ENDOMORPHISM_TO_XI_ZERO`

## Exact next object

`FULL_CHILD_PARENT_DIRAC_AND_BOSONIC_RELATIVE_HEAT_KERNEL_WITH_TRACE_CLASS_SEAM_DOMAIN_RELATIVE_ZETA_ANOMALY_BERGER_DERIVATIVE_AND_NONDEGENERATE_LOG_SCALE_BERGER_STATIONARITY_SYSTEM`

---

## 1. Purpose

v14.50 showed that the unweighted canonical Standard Model fermion trace gives

\[
K_Y:K_2:K_3=\frac53:1:1,
\]

rather than the historical BHSM registry pattern `1:2:7`.  It also proved that
the local four-dimensional `a4` functional is scale invariant and that the
local Weyl term alone does not select the frozen nonround Berger anisotropy.

This sprint tests the requested BHSM-native continuation:

1. reconstruct the internal trace from the actual Hopf, `C3`, collar, FR, and
   `G2 -> SU(3)` bundle data;
2. test whether winding or fiber multiplicity can produce `1:2:7`;
3. formulate absolute-scale generation using a parent-relative nonlocal
   determinant;
4. formulate the full coupled Berger and scale stationarity system;
5. select the allowed curvature-response branch from the retained connection.

No external gauge ratio, particle mass, or absolute scale is inserted.

---

## 2. Exact canonical trace and common bundle factors

For one all-left-Weyl Standard Model generation in ordinary-hypercharge
normalization,

\[
K_Y=\frac{10}{3},\qquad K_2=2,\qquad K_3=2.
\]

The currently owned BHSM structures include common replication factors:

- exact `C3` family replication;
- the two oriented collar sheets;
- conjugate or particle/antiparticle doubling when the chosen spectral Hilbert
  space includes it;
- the rank-one FR sign line.

If a gauge generator acts trivially on an auxiliary factor `F`, then

\[
\operatorname{Tr}_{\mathcal H_{\rm gauge}\otimes F}
(T_aT_b)
=
\dim(F)\operatorname{Tr}_{\mathcal H_{\rm gauge}}(T_aT_b).
\]

Every gauge coefficient is multiplied by the same number.  The ratios are
unchanged.  Therefore family replication, collar orientation, conjugation, and
the FR line cannot convert `5/3:1:1` into `1:2:7`.

The same theorem applies to a factorized gauge-blind Hopf-fiber multiplicity.
An infinite fiber tower requires a regulator, but a common regulator still
multiplies every gauge trace by the same regularized fiber dimension.  A
sector-dependent fiber cutoff or weight would be a new gauge-dependent
selector and must be derived from the action rather than inferred from the
desired ratio.

---

## 3. Peter–Weyl multiplicity is not representation dimension

For the normalized Peter–Weyl decomposition

\[
L^2(SU(2))
\cong
\bigoplus_j V_j\otimes V_j^*,
\]

the left `SU(2)` action sees `V_j` with multiplicity

\[
\dim V_j=2j+1.
\]

With the standard index

\[
T(j)=\frac13j(j+1)(2j+1),
\]

the complete level contributes

\[
K_2^{(j)}=(2j+1)T(j).
\]

For the lowest nontrivial block,

\[
j=\frac12,
\qquad
K_2^{(1/2)}=2\left(\frac12\right)=1.
\]

Thus the dimension-two Hopf doublet does **not** automatically contribute a
kinetic weight two.  Fiber dimension, representation dimension, multiplicity,
and quadratic index are distinct quantities.

---

## 4. The `G2` seven-module contributes color index one, not seven

The complexified seven-dimensional carrier restricts as

\[
\mathbf 7_{\mathbb C}\big|_{SU(3)}
\cong
\mathbf 1\oplus\mathbf 3\oplus\bar{\mathbf 3}.
\]

The singlet has zero color index, while

\[
T(\mathbf3)=T(\bar{\mathbf3})=\frac12.
\]

Therefore

\[
\boxed{
T(\mathbf 7_{\mathbb C}|_{SU(3)})=1,
}
\]

not seven.

Moreover, the current BHSM seven-module is the bosonic eta/triality carrier.
It is not automatically an additional fermion species in the local Dirac
Hilbert trace.  Counting it as one vectorlike `3 + bar3` pair is therefore a
counterfactual upper-bound diagnostic, not an action-owned state insertion.

If ordinary hypercharge is rescaled only to present the canonical trace as

\[
1:2:2,
\]

then adding one counterfactual complexified `G2` seven gives

\[
1:2:3.
\]

A literal kinetic-trace target

\[
1:2:7
\]

would require four additional vectorlike `3 + bar3` index units beyond that
single seven-module diagnostic.  No such action-owned state content exists in
the current BHSM ledger.

This diagnostic does not assert that the historical registry was originally a
kinetic-trace convention.  If `1:2:7` is interpreted instead as a coupling or
`alpha_i` ratio, an explicit inverse kinetic-normalization map is required.
The current action does not supply that map either.  Under either convention,
the exact owned bundle data do not generate the registry pattern.

---

## 5. Topological winding does not become an ordinary kinetic weight

Winding and bundle topology can determine:

- the FR sign or spin-statistics parity;
- the instanton or Chern class;
- the integrated topological density `tr(F wedge F)`;
- spectral asymmetry and determinant phases;
- which twisted sectors are admitted.

They do not by themselves determine the positive multiplier of

\[
\operatorname{tr}(F\wedge\star F).
\]

The local gauge kinetic coefficient is controlled by the representation index
and the normalized trace.  A winding number can affect that coefficient only
indirectly by changing the actual Hilbert space, spectrum, or action-selected
measure.  None of those changes has been derived in a way that yields
`1:2:7`.

Consequently:

\[
\boxed{
\text{rank seven, winding seven, or seven tangent directions}
\not\Rightarrow K_3=7.
}
\]

---

## 6. Parent-relative determinant and logarithmic scale law

Let the positive child and parent operators share a common principal symbol and
compatible self-adjoint seam domain.  After the collective zero-mode quotient,
define

\[
\zeta_{\rm rel}(s;L,a)
=
\zeta_{\rm child}(s;L,a)
-
\zeta_{\rm parent}(s;L,a).
\]

For a covariantly scaling second-order operator,

\[
P_{c,p}(L,a)=L^{-2}\widehat P_{c,p}(a),
\]

one obtains

\[
\zeta_{\rm rel}(s;L,a)
=
L^{2s}\widehat\zeta_{\rm rel}(s;a).
\]

Using the fermion convention

\[
\Gamma_F^{\rm rel}
=-\log\det_{\rm rel}D
=\frac12\zeta_{\rm rel}'(0;P/\mu^2),
\]

the scale dependence is

\[
\boxed{
\Gamma_F^{\rm rel}(L,a;\mu)
=
\widehat\Gamma_F^{\rm rel}(a)
+
\widehat\zeta_{\rm rel}(0;a)\log(\mu L).
}
\]

Therefore

\[
\boxed{
\frac{\partial\Gamma_F^{\rm rel}}
{\partial\log L}
=
\widehat\zeta_{\rm rel}(0;a).
}
\]

This gives three exact cases.

### Case A: relative anomaly vanishes

\[
\widehat\zeta_{\rm rel}(0;a)=0.
\]

The parent-relative determinant is scale invariant and cannot select `L`.

### Case B: relative anomaly is nonzero, with no other scale term

The determinant contains a lone logarithm.  Its slope is constant, so it has no
finite stable minimum.

### Case C: relative anomaly plus a second scale-dependent term

A finite stationary scale may occur only if the eta, collar, gravitational,
interface, running-coupling, or parent-response sector contributes a different
`L` dependence.  The second derivative must be positive after all constrained
fields are integrated out.

Parent-relative subtraction does not guarantee Case C.  It can cancel the
local relative anomaly entirely when child and parent ultraviolet data match.
The relative heat-kernel coefficient must be calculated.

---

## 7. Trace-class and renormalization requirements

A physical relative determinant requires:

1. one declared child and parent operator family;
2. a common principal symbol and matched Clifford/gauge seam data;
3. a self-adjoint common domain;
4. a trace-class heat-kernel difference, or a specified relative determinant
   extension;
5. identical ultraviolet subtraction conventions;
6. explicit treatment of zero and negative modes;
7. the collective-mode no-double-counting projector;
8. local counterterm running that cancels residual `mu` dependence.

Until those conditions are supplied, `Pi_nonlocal(a)` is a symbolic response,
not a numerical scale generator.

---

## 8. Full coupled Berger and scale stationarity

The correct relative effective action is

\[
\Gamma_{\rm rel}
=
S_{\eta}^{\rm rel}
+S_{\rm grav}^{\rm rel}
+S_{\rm collar/lapse}^{\rm rel}
+S_{\zeta,\rm local}^{\rm rel}
+\Gamma_{\rm nonlocal}^{\rm rel}.
\]

The background must solve the quantum-corrected equations

\[
\frac{\delta\Gamma_{\rm rel}}{\delta f_\eta}=0,
\qquad
\frac{\delta\Gamma_{\rm rel}}{\delta N}=0,
\qquad
\frac{\delta\Gamma_{\rm rel}}{\delta J}=0.
\]

The remaining global conditions are

\[
\boxed{
F_a:=
\frac{d\Gamma_{\rm rel}^{\rm on-shell}}{da}=0,
}
\]

\[
\boxed{
F_L:=
\frac{d\Gamma_{\rm rel}^{\rm on-shell}}{d\log L}=0.
}
\]

For the fermion determinant,

\[
\frac{d\Gamma_F^{\rm rel}}{da}
=
-\operatorname{Tr}_{\rm rel}
\left(D^{-1}\frac{\partial D}{\partial a}\right)
\]

in the declared relative-zeta convention.  The eta-derived mass contributes

\[
m_\eta=-\partial_s\log\sin f_\eta,
\]

\[
\frac{\partial m_\eta}{\partial a}
=
-\partial_s
\left(
\cot f_\eta\frac{\partial f_\eta}{\partial a}
\right).
\]

However, implicit profile derivatives cancel from the derivative of the total
on-shell action only when the **same quantum-corrected functional** supplies the
eta, lapse, collar, Berger, and scale equations.  Reusing the classical eta
profile while adding a determinant derivative is not self-consistent.

A discrete local solution requires

\[
\boxed{
\det
\frac{\partial(F_L,F_a)}
{\partial(\log L,a)}
\ne0.
}
\]

Stability requires the constrained Schur-reduced Hessian in `(log L,a)` to be
positive definite.

These equations implement the directive exactly.  They cannot yet be evaluated
because the full child/parent operators and relative spectrum are absent.

---

## 9. Curvature-response lock

The retained BHSM Dirac connection already contains the usual spin-curvature
Lichnerowicz term

\[
E_{\rm spin}=-\frac14R
\]

in the adopted convention.  This is not the optional scalar-curvature response
parameter.

The documented additional endomorphisms are:

- the eta-derived odd mass;
- the seam Higgs response;
- finite family operators;
- gauge, projector, Berry, and spin connections.

None contains a separately owned term

\[
\xi R I.
\]

Therefore the BHSM-native branch is

\[
\boxed{\xi=0.}
\]

The algebraic value `xi=1/6` preserves the pure gravitational `a4` ray, but
adopting it would add a curvature-response endomorphism not derived by the
current BHSM connection.  It remains available only if a later parent action
explicitly generates that term and the full `a4` trace is recomputed.

---

## 10. Hindsight 20/20

### Validated

- Common `C3`, collar, conjugate, FR, and gauge-blind fiber multiplicities do
  not alter gauge-trace ratios.
- The complete lowest Hopf Peter–Weyl doublet block has quadratic index one,
  not two.
- The complexified `G2` seven-module has `SU(3)` index one, not seven.
- Winding and Chern data do not become ordinary `F wedge star F` coefficients.
- Parent-relative zeta scaling is governed by the relative anomaly
  `zeta_rel(0)`.
- A lone determinant logarithm does not possess a finite stable scale minimum.
- Berger and scale selection form a coupled two-equation problem.
- The documented BHSM connection selects the additional curvature response
  `xi=0`.

### Invalidated

- Recovering `1:2:7` by counting fiber, quaternionic, octonionic, or tangent
  dimensions as quadratic trace indices.
- Recovering `1:2:7` from common family or collar multiplicities.
- Recovering an ordinary gauge kinetic coefficient directly from winding.
- Assuming parent subtraction automatically creates dimensional transmutation.
- Solving the Berger equation with a classical eta profile while adding quantum
  determinant backreaction afterward.
- Adopting `xi=1/6` without a new action term.

### Open

- the full child and parent Dirac operators, bosonic Hessians, and matched seam
  domain;
- the complete relative heat-kernel difference and `zeta_rel(0)`;
- the finite nonlocal Berger derivative;
- a second physical scale-dependent term or running boundary condition;
- a nondegenerate stable solution of `(F_L,F_a)=0`;
- any action-owned internal state/weight mechanism replacing the failed
  `1:2:7` trace reconstruction;
- the downstream `L=2,3` crossing, nonlinear branch, CKM, CP, confinement,
  neutrino scale, and absolute masses.

---

## 11. Completion status

BHSM remains physically incomplete.  v14.51 closes the requested geometry-first
reconstruction as a negative trace result, fixes `xi=0`, and replaces the
informal nonlocal-scale proposal with an exact relative-zeta and two-variable
stationarity contract.

Frozen predictions are unchanged.  No physical coupling, scale, mass, CKM
matrix, or CP phase is emitted.  The USB remains untouched.
