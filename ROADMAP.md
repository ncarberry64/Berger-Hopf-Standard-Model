# BHSM Roadmap

Current neutral-sector boundary: conditional dimensionless propagation closure,
a conditional neutral spectral-mass theorem, and conditional
measurement-supported admissible positivity. Physical eV/GeV mass closure
remains open pending numeric `sqrt(A_nu/Z_nu)` in metres, physical
`K_neutral,eff` in `m^-2`, and complete-action derivation of the response cone.

## Neutral spectral stiffness v1.3

- Derive `Z_nu` and `A_nu` from the neutral action rather than importing the
  scalar analogue's coefficient.
- Derive `sqrt(A_nu/Z_nu)` in metres.
- Derive the physical `K_neutral,eff` map in `m^-2`.
- Prove positivity on the admissible/projected neutral space.
- Derive the measurement-supported response cone uniquely from the complete
  neutral action; the current exact copositivity result is ontology conditional.
- Derive `chi_nu`, `lambda_nu`, normalized `dmu_boundary dt`, support metric,
  collar orientation/edge data, and the neutral profile/embedding.
- Identify neutral `Z_nu` and `A_nu_gap` from that normalized action and derive
  their ratio in physical units before any mass comparison.
- Retain the legacy gravitational expression only as a dimensionally gated
  stiffness functional.

## Done

- Frozen internal prediction package and integrity guards.
- Offline Python interface, prediction registry, and reviewer reports.
- Prediction gallery, notebooks, and provenance-tracked artifact adapters.
- Executable theorem-blocker and proof-gate machinery.
- Source-traced symbolic CP `O_int` field/action candidate.
- Machine-readable author ontology integrated into the minimal-action evaluator.
- Artifact-backed CP/Z6 holonomy target separated from the retired standalone
  production-vertex target.
- Conditional `X_ch` boundary-response and neutrino propagation-mass theorems.
- Dimensionless neutrino propagation-threshold numerical candidate using
  artifact-backed `K_nu`, `g_nu`, `kappa_nu`, and `tau`.
- Offline neutral unit-source, boundary-measure, and threshold-to-energy audit.
- Bundled legacy curvature-threshold corpus and provenance-backed mass
  functional adapter.

## Candidate

- CP `O_int` symbolic field/action construction retained as representation-only
  history; it is not a core production target.
- Bounded collider-interface and external-tool handoff assets.
- Optional speculative templates, disabled by default.

## Open

- Numerical `X_ch` response normalization and any separate 4D production map.
- Artifact-backed dimensionful neutral scale mapping the response to eV/GeV.
- Physical normalization of `dmu_boundary dt`, neutral background energy
  density, and transport normalization without empirical calibration.
- Derive `r_prop` from the neutral boundary geometry and map the dimensionless
  kernel response to `k_neutral,eff` in `m^-2`.
- Derive the missing physical length normalization or replace the legacy
  `r^2 k` ansatz with a dimensionally consistent result from the boundary action.
- Physical map from neutral boundary channels to oscillation and cosmological
  observables.
- Dirac/Majorana convention only where later comparison/export requires it.
- Any downstream physics theorem explicitly listed by the blocker registry.

## Runtime-Gated

- Live FeynRules validation.
- UFO export and loadability.
- MadGraph smoke testing and event generation.
- Institutional experiment-software integration.

## Next Recommended Work

The v1.9 reviewer hardening layer separates the computational engine from the
conditional physics program, adds deterministic invariants and reproduction
commands, and records falsifiers. It does not close the following items.

1. Derive the complete charged action selection of `Omega_f` and `rho_ch`; the v1.8 common-16 identities are conditional on them.
2. Derive or reject the CKM reciprocal logarithmic transport theorem before promoting `1/16`.
3. Derive the physical dimension and absolute normalization of `dmu_boundary dt`, `Z_ch`, and `A_ch`.
4. Derive the BHSM shape operator, collar orientation, edge condition, and admissible variations.
5. Only after interaction eligibility closes, attempt external HEP runtime validation.
6. Obtain an independent matched-engine reproduction on a PMU-enabled host;
   preserve regressions and null results rather than selecting favorable hosts.
7. Derive or reject the primitive charged-lattice normalization rule from the
   complete action; gcd arithmetic alone is insufficient.
8. Derive the bridge overlap-selection rule and CKM logarithmic averaging
   theorem before promoting `4/3` or `1/16` beyond conditional candidates.
9. Identify the explicit action symmetry or quotient that removes common
   incidence coverings.
10. Construct the CKM transport functional and prove that its physical channel
    decomposition contains sixteen equivalent bilinear contributions.
11. Derive the CKM transport representation from the action and decide among
    `Hom(V_u,V_d)` (8), `End(V_ch)` (49), sectorwise self response (21), and
    maximal primitive self response (16); do not select 16 numerically.
12. Derive the Hermitian off-diagonal charged-current block and its adjoint
    closure from the normalized BHSM action; target-level `+ h.c.` is not enough.
13. Prove or reject the normalized-action CKM transport-space theorem selecting
    `Hom(V_u,V_d) direct_sum Hom(V_d,V_u)` over the one-way 8, maximal
    self-response 16, sector self-response 21, and total endomorphism 49
    alternatives. The CKM exponent remains open until this gate passes.
14. Locate a normalized charged-current action term with explicit operator
    domain/codomain before promoting any CKM transport-space assignment; same
    numerical dimension does not establish the physical source.
15. Supply or rule out a boundary measure, action-derived coefficient, and
    `Pi_u`/`Pi_d` sandwich for `L_CKM_charged_current_bounded`.
16. Prove whether the forward and adjoint terms share one normalized action
    object, then separately prove CKM identification before selecting a space.
17. Attach a physically normalized boundary measure and fixed geometric
    coefficient to the same CKM action term, or preserve the blocker.
18. Derive `g2_BH` from the normalized weak gauge action before promoting the
    artifact-backed charged-current coefficient form to a value prediction.
19. Derive or reject `6*pi^2=3 Vol(S^3_unit)`, the `1:2:7` action-selected sector weights, and their same-action attachment before promoting a universal gauge-coupling quantum.
20. Preserve the neutrino bedrock/dynamic split: sharpen dimensionless PMNS and response-cone theorem provenance while deferring physical `Delta m^2`, matter effects, radiative corrections, and unit normalization to the QFT/SM realization ledger.

<!-- BHSM_FULL_ACTION_CLOSURE_V4_0 -->
## Full action closure v4.0

Status: `FULL_BHSM_NOT_COMPLETE`.

The deterministic blocker DAG is in [docs/full_theorem_blocker_dag.md](docs/full_theorem_blocker_dag.md) and
`artifacts/BHSM_full_theorem_blocker_dag_v4_0.json`.

- BHSM is not complete until the full action-normalization and scale gates close.
- The 1:2:7 gauge-coupling registry pattern is artifact-backed but not action-derived.
- The candidate denominator 6π² = 3 Vol(S³) is not a coupling derivation unless attached to the normalized gauge action.
- Sector weights do not derive gauge couplings without action attachment.
- The overall gauge-action coefficient k remains open unless fixed by the action.
- The CKM coefficient form is artifact-backed, but the CKM coefficient value remains open unless g2_BH is action-derived.
- The CKM exponent remains not derived unless all CKM action, transport, identification, and log-averaging gates close.
- Dimensionless neutral/PMNS structure does not imply physical neutrino masses.
- Physical Delta m², matter effects, radiative corrections, stiffness length, curvature, and unit normalization remain open unless separately derived.
- Full BHSM completion is not claimed by this repository unless every completion gate passes.

<!-- BHSM_BOUNDARY_COLLAR_MEASURE_V4_1 -->
## Boundary/collar measure v4.1

Measure status: `CONDITIONAL_BOUNDARY_COLLAR_MEASURE_SOURCE`. Three coframe directions:
`ARTIFACT_BACKED_THREE_BOUNDARY_FRAME_DIRECTIONS`. Unit-S3 normalization, frame averaging,
gauge trace attachment, and the gauge denominator remain open.

- The mathematical identity Vol(S³_unit)=2π² is not by itself a gauge-coupling derivation.
- The candidate denominator 6π² = 3 Vol(S³_unit) is not action-derived unless BHSM supplies an action-selected three-frame boundary average.
- A three-frame decomposition does not by itself imply a frame average.
- A frame average does not derive gauge couplings unless attached to gauge trace densities in the normalized action.
- The gauge coupling quantum λ_gauge = 1/(6π²) remains open unless the denominator is action-attached.
- The α_i values remain open unless the gauge quantum, sector weights, and action coefficient are attached by the normalized action.
- g2_BH remains open unless α2_BH is action-derived and the weak convention applies.
- The CKM coefficient value remains open unless g2_BH is action-derived.
- The CKM exponent remains not derived.
- Full BHSM remains not complete unless all action-normalization and scale gates close.

<!-- BHSM_BERGER_FRAME_WEIGHTING_V4_2 -->
## Berger frame weighting v4.2

Equal weighting and frame-average normalization remain open. Berger anisotropy compatibility is
conditional on an action-selected orthonormal gauge coframe. Gauge attachment and all downstream
coupling gates remain open.

- Three artifact-backed Berger frame directions do not by themselves imply equal weighting.
- Equal weighting does not by itself imply average normalization by 1/3.
- Average normalization does not by itself attach to gauge trace densities.
- Berger anisotropy must be checked before equal frame averaging can be promoted.
- The denominator 1/[3 Vol(S³)] remains open unless equal frame averaging, unit-volume normalization, and gauge-trace attachment are supported.
- The gauge coupling quantum remains open unless the denominator is action-attached.
- α_i, g2_BH, CKM coefficient value, and CKM exponent remain open unless downstream action gates close.
- Full BHSM remains not complete.
