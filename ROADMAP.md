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

1. Derive the complete charged action selection of `Omega_f` and `rho_ch`; the v1.8 common-16 identities are conditional on them.
2. Derive or reject the CKM reciprocal logarithmic transport theorem before promoting `1/16`.
3. Derive the physical dimension and absolute normalization of `dmu_boundary dt`, `Z_ch`, and `A_ch`.
4. Derive the BHSM shape operator, collar orientation, edge condition, and admissible variations.
5. Only after interaction eligibility closes, attempt external HEP runtime validation.
