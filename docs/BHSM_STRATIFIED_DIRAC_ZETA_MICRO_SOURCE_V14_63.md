# BHSM v14.63 — Full Stratified Dirac/Zeta Microscopic-Source Exhaustion

## Status

**Primary verdict**

`BHSM_V14_63_THE_FULL_STRATIFIED_DIRAC_ZETA_CANDIDATE_DOES_NOT_YET_CLOSE_ZERO_INPUT_BHSM_BECAUSE_A_PURE_ZETA_DETERMINANT_FIXES_THE_NONLOCAL_AND_LOG_ANOMALY_PART_BUT_REQUIRES_LOCAL_RENORMALIZED_COUNTERTERMS_THE_LOCAL_ZETA_A_D_ACTION_OMITS_THE_RELEVANT_LOWER_HEAT_COEFFICIENTS_NEEDED_FOR_M8_AND_M5_VOLUME_EINSTEIN_TERMS_AND_A_CUTOFF_SPECTRAL_ACTION_CAN_GENERATE_THEM_ONLY_AFTER_A_CUTOFF_PROFILE_GLOBAL_CROSS_STRATUM_TRACE_AND_FINITE_DIRAC_DATA_ARE_DEFINED_SO_THE_CURRENT_ARCHIVE_CONTAINS_NO_DERIVED_SINGLE_MICROSCOPIC_FUNCTIONAL_THAT_FIXES_ALL_M8_M5_AND_M4_WILSON_FAMILIES`

**BHSM physical completion:** `FALSE`
**Mark III:** `NOT_REACHED`
**Frozen predictions changed:** `NO`
**Official prediction logic changed:** `NO`
**Physical prediction emitted:** `NO`
**USB touched:** `NO`

---

## 1. Question tested

v14.62 reduced the apparent coefficient problem to four genuinely independent action-data families in the current stratified action:

1. M8 parent volume/potential data;
2. M8 two-derivative geometry/eta data;
3. M5 cap Einstein/scalar data, with GHY fixed relative to Einstein-Hilbert;
4. intrinsic M4 gauge/Dirac-Yukawa/Higgs/current data.

The strongest internal zero-input candidate was then explicit:

> Can one globally defined Dirac/zeta microscopic functional generate the relative coefficients of all three strata so that these cease to be independent Wilson inputs?

v14.63 tests that candidate in its three mathematically distinct forms rather than calling all of them “the spectral action.”

---

## 2. Candidate A — pure zeta-induced determinant

For a complete gauge-fixed positive operator bundle `P`, the induced one-loop term is schematically

\[
\Gamma_{\rm ind}
=\frac12\,\mathrm{STr}\,\log\det_{\zeta}(P/\mu^2),
\]

with the boson, fermion and ghost weights fixed by statistics.

For a positive rescaling `alpha P`,

\[
\zeta_{\alpha P}(s)=\alpha^{-s}\zeta_P(s),
\]

and therefore

\[
\log\det_{\zeta}(\alpha P)
=\log\det_{\zeta}P+\zeta_P(0)\log\alpha.
\]

This is valuable: once the physical operator exists, the determinant fixes a nonlocal spectral contribution and its logarithmic scale response.

But a renormalized field theory has the form

\[
\Gamma_{\rm ren}
=\Gamma_{\rm nonlocal}[P]
+\sum_i c_i^{\rm ren}(\mu)\int {\cal O}_i.
\]

The determinant identifies divergences/running and the nonlocal part. It does not, by itself, determine the finite renormalized values of every relevant local Wilson coefficient. Those finite parts require renormalization conditions or a more microscopic UV definition.

So a pure induced determinant cannot presently replace the independently owned M8/M5/M4 local action data.

**Verdict:** `PURE_ZETA_INDUCED_DETERMINANT_ZERO_INPUT_CLOSURE = FALSE`.

---

## 3. Candidate B — local zeta action

For a Laplace-type operator on a `d`-dimensional closed stratum, modulo kernel and boundary qualifications,

\[
\zeta_P(0)\sim a_d(P).
\]

This is precisely why the previously tested `a4(D^2)` branch is useful in four dimensions. It can compress dimension-four curvature/gauge terms and, on the canonical three-generation Standard-Model trace, retains

\[
K_Y:K_2:K_3=\frac53:1:1,
\]

not the historical `1:2:7` rule.

However, the parent and cap relevant operators occur in lower heat coefficients. A cutoff expansion would contain, schematically,

\[
M_8:\quad \Lambda^8F_8a_0+\Lambda^6F_6a_2+\cdots,
\]

and

\[
M_5:\quad \Lambda^5F_5a_0+\Lambda^3F_3a_2+\cdots.
\]

The dimension-matched local zeta coefficient `a8` or `a5` is not `a0` or `a2`. Therefore `zeta_P(0)` alone cannot generate the M8/M5 volume and Einstein/two-derivative terms needed by the global envelopment equations.

**Verdict:** `LOCAL_ZETA_A_D_ZERO_INPUT_CLOSURE = FALSE`.

---

## 4. Candidate C — cutoff spectral action

The only tested spectral construction broad enough to generate all relevant local terms is

\[
S_f(P,\Lambda)
=\mathrm{STr}\,f(P/\Lambda^2).
\]

Its asymptotic expansion has the mixed-dimensional structure

\[
S_f\sim
\sum_s\sum_k
F_{d_s-k}\,\Lambda^{d_s-k}a_k(P_s),
\]

plus the appropriate boundary terms on strata with boundary.

Representative moments are

\[
\begin{aligned}
M_8:&\quad F_8,F_6,F_4,F_2,F_0,\\
M_5:&\quad F_5,F_3,F_1,\ldots,\\
M_4:&\quad F_4,F_2,F_0.
\end{aligned}
\]

Thus a **specific** cutoff profile `f` can relate those coefficients. The question is whether the current BHSM axioms already select that profile.

They do not.

---

## 5. Executable heat-moment independence witness

To avoid treating this as a verbal objection, v14.63 implements a constructive functional-rank witness using positive mixtures

\[
f(u)=\sum_{j=1}^{7}w_j e^{-a_ju},\qquad w_j>0.
\]

For the normalized exponential moment,

\[
F_p(e^{-au})=a^{-p/2},\qquad p>0,
\]

and `F0=f(0)`.

Using the moment set

\[
\{F_8,F_6,F_5,F_4,F_3,F_2,F_0\},
\]

the deterministic seven-rate moment matrix has full rank seven.

More strongly, v14.63 constructs a small perturbation of a strictly positive cutoff mixture that preserves both `F0` and `F4` to numerical precision while changing `F8`. Therefore fixing a common normalization and a dimension-four normalization still does not force the eight-dimensional volume moment.

This does **not** mean a spectral profile can never relate the moments. It means the relation appears only after the profile is specified. Choosing that profile is a microscopic theory-definition step, not a result of global minimization.

**Verdict:** `GENERIC_CUTOFF_HEAT_MOMENTS_ARE_NOT_FIXED_BY_ONE_COMMON_NORMALIZATION`.

---

## 6. Cross-stratum trace is itself part of the missing microscopic object

A true “single spectral action” requires more than writing `Tr f(D^2)`.

For a stratified system containing M8, M5 and M4, the microscopic object must define before comparison:

- the Hilbert/bundle space of every stratum;
- the global self-adjoint operator and compatibility/off-diagonal domain;
- how the cross-stratum trace is normalized;
- field multiplicities, grading and statistics;
- the complete ghost complex;
- the cutoff profile and scale rule, or equivalent renormalization conditions;
- the zero-mode quotient and determinant phase/eta convention.

The authoritative BHSM v7.1 correspondence action deliberately does not identify all of those independently owned strata as one spectral triple. v14.63 therefore refuses to silently manufacture such a triple after seeing physical targets.

---

## 7. Finite Dirac data remain a separate zero-input gate

Even a fully specified cutoff profile would not automatically solve flavor.

The dimension-four heat coefficients depend on the representation trace and on the finite/internal Dirac data. Representation multiplicities can generate gauge trace ratios; that is the source of the canonical

\[
K_Y:K_2:K_3=\frac53:1:1.
\]

But Higgs/Yukawa invariants contain quantities such as

\[
\operatorname{Tr}(Y^\dagger Y),
\qquad
\operatorname{Tr}\big[(Y^\dagger Y)^2\big],
\]

and mixing information depends on the relative finite-Dirac structures of sectors.

A spectral trace propagates those operator entries into coefficients. It does not derive their numerical values merely by taking the trace.

Therefore a zero-input spectral completion must either derive the finite Dirac/internal operator from BHSM geometry or declare it as new microscopic data before comparison.

---

## 8. What remains valid from the previous campaign

Nothing in this result reopens the solved architectural points:

- the v14.59 local cap inverse problem remains bypassed by global envelopment;
- v14.60 remains a valid reduced proof that globally integrated action can distinguish seam-equivalent cap profiles;
- v14.61's full-field global Euler-Lagrange/Hessian architecture remains the right solver;
- v14.62's GHY relative coefficient and common-normalization quotient remain closed;
- the determinant statistics prefactors remain fixed rather than tunable;
- `R_H`, nesting ratios and moving-seam amplitudes remain dynamical variables, not Wilson coefficients;
- `xi=0` remains locked.

The obstruction has moved upstream to the definition of the microscopic action itself.

---

## 9. Validated / invalidated / reclassified / open

### Validated

- A pure zeta determinant has a fixed operator rescaling law and gives a legitimate nonlocal/log-anomaly response once the operator is supplied.
- A local zeta `a_d` action is dimension-matched and cannot substitute for the lower `a0/a2` relevant operators in M8/M5.
- A cutoff spectral action is broad enough in principle to generate relevant local terms across mixed dimensions.
- Generic cutoff moments needed by the 8D/5D/4D strata have independent functional freedom; the deterministic seven-moment witness has full rank.
- One can preserve `F0` and `F4` while changing `F8` inside a strictly positive cutoff-mixture neighborhood.
- Finite Dirac/Yukawa data are not numerically derived merely by evaluating a spectral trace.

### Invalidated

- “The zeta determinant alone fixes all local M8/M5/M4 Wilson coefficients.”
- “The local `a_d` zeta action generates the M8/M5 cosmological and Einstein terms.”
- “One common spectral-action normalization automatically fixes all mixed-dimensional coefficient ratios.”
- “The historical gauge ratio `1:2:7` follows from the canonical three-generation spectral trace.”

### Reclassified

- The cutoff spectral action is **not disproven**. It is reclassified as a possible new microscopic foundation whose profile/trace/operator data must be declared independently of physical targets.
- The zero-input obstruction is no longer cap reconstruction. It is **microscopic action definition and finite-Dirac provenance**.

### Open

- a BHSM-derived global stratified spectral triple or equivalent microscopic principle;
- selection of the cutoff profile `f` or a UV renormalization rule that fixes the local finite parts;
- a canonical cross-stratum trace normalization;
- derivation of finite Dirac/Yukawa data from the BHSM geometry;
- action-derived physical parent/child background;
- branch exhaustion and gauge-reduced Hessian on that physical background;
- physical DtN and relative heat kernel;
- the frozen no-retuning neutrino kill screen.

---

## 10. Completion gate

`FULL_BHSM_COMPLETE = FALSE`.

The exact next object is

`GLOBAL_STRATIFIED_SPECTRAL_TRIPLE_OR_EQUIVALENT_MICROSCOPIC_PRINCIPLE_THAT_PREDECLARES_THE_CROSS_STRATUM_HILBERT_TRACE_NORMALIZATION_CUTOFF_PROFILE_OR_RENORMALIZATION_CONDITIONS_AND_FINITE_DIRAC_DATA_BEFORE_ANY_PHYSICAL_COMPARISON_THEN_REDERIVE_THE_M8_M5_M4_COEFFICIENT_RATIOS_RUN_THE_GLOBAL_ENVELOPMENT_BVP_BRANCH_EXHAUSTION_GAUGE_REDUCED_HESSIAN_DTN_RELATIVE_HEAT_KERNEL_AND_ZERO_RETUNING_NEUTRINO_KILL_SCREEN`

v14.63 makes **no automatic foundational choice**. A new microscopic action cannot be selected because it produces desired masses, couplings or mixing and still qualify as a zero-retuning derivation.
