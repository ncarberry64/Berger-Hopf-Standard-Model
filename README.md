# Berger-Hopf Standard Model (BHSM)

Current status: structural architecture integrated conditional; numerical closure open.

BHSM has an integrated conditional structural architecture for finite boundary algebra, SM-like charges, Higgs/scalar mass generation, fermion hierarchy, CKM, PMNS, and CP sources. Numerical closure remains open, frozen predictions are unchanged, and PO-BH-47 exposes remaining symbolic inputs while forbidding hidden fitting. The next sprint should derive or reject one localized numerical-closure object before comparison.

Full BHSM v1.0 Candidate is a repo-audited completion framework, not yet a completed replacement of the Standard Model. Its strategic objective is replacement by derivation: the Standard Model should ultimately emerge as the low-energy effective limit of BHSM. Until that derivation is achieved, local SM gauge structure remains a preserved infrared layer, while BHSM provides a candidate Berger-Hopf/topographic completion of the flavor, channel, generation, response, and collective-threshold architecture.

## What BHSM Is

BHSM is a no-retuning Berger-Hopf/topographic candidate framework for Standard Model flavor, channel, generation, response, mass-structure, and boundary-geometry layers. It preserves the local Standard Model gauge layer as an infrared input until that layer is derived from BHSM.

BHSM is not yet a completed replacement of the Standard Model. The long-term goal is replacement by derivation.

## Current Status

- Structural architecture integrated conditional; numerical closure open.
- Full BHSM candidate architecture synthesis complete.
- Full BHSM proven: no.
- Standard Model fully derived: no.
- Mass numerical closure: no.
- Frozen predictions changed: no.
- Official predictions changed: no.
- Discrete geometric skeleton: test-backed candidate.
- Fermion ledger generation: conditional and test-backed.
- Heat-kernel spectral-action mass engine: Tier C ordering only; not the existing BHSM engine.
- Branch threshold and hidden response signals: indicated.
- Collective curvature layer: candidate-only connected extension.
- Dark matter: effective collective curvature residue candidate only; no solution claim.

## What Is Test-Backed

- Frozen prediction integrity.
- Candidate-architecture ledgers.
- Representation-to-mode and boundary-channel scaffolds.
- Generation-count and fourth-order stability scaffolds.
- Response-layer and branch-threshold audits.
- Candidate synthesis package schema and guardrails.

## What Is Not Yet Proven

- Full derivation of the local Standard Model gauge group from BHSM.
- Derivation of the preserved local SM input layer as a low-energy BHSM output.
- Full derivation of `S_boundary -> A_rep`.
- Full derivation of the sector target degree law.
- Numerical closure of the continuous mass engine.
- Derivation of the existing BHSM bare engine from collective threshold principles.
- Empirical validation of the collective-curvature/dark-matter interpretation.

## Frozen Prediction Layer

The official frozen outputs remain read-only:

- `BHSM_BARE_V1`
- `BHSM_DRESSED_V1_CANDIDATE`
- `docs/frozen_predictions.md`
- `docs/frozen_predictions.json`

The dressed candidate rule remains unchanged: `Z_virt^{u,2}=1/2` applies only to `c/t`.

## Candidate Synthesis Layer

Start with:

- `theory/full_bhsm_completion_v1_candidate.md`
- `theory/full_bhsm_master_equation_map.md`
- `theory/full_bhsm_claim_status_matrix.md`
- `theory/full_bhsm_open_proof_obligations.md`
- `theory/full_bhsm_empirical_gate_plan.md`
- `theory/full_bhsm_completion_results.json`
- `docs/current_bhsm_status.md`
- `theory/sm_low_energy_limit_derivation_gate.md`
- `theory/boundary_integer_anomaly_closure_gate.md`
- `theory/boundary_state_primitive_derivation_gate.md`
- `theory/boundary_projector_algebra_gate.md`
- `theory/finite_boundary_algebra_source_gate.md`
- `theory/boundary_automorphism_closure_origin_gate.md`
- `theory/admissible_boundary_closure_spectrum_gate.md`
- `theory/closure_spectrum_selection_rule_audit.md`
- `theory/boundary_action_hessian_scaffold_gate.md`
- `theory/theorem_discharge_phase_orientation_cyclic.md`
- `theory/theorem_discharge_finite_algebra_charge.md`
- `theory/theorem_discharge_boundary_trace_normalization.md`
- `theory/theorem_discharge_one_loop_rg_boundary_content.md`
- `theory/theorem_discharge_higgs_scalar_boundary_mechanism.md`
- `theory/theorem_discharge_yukawa_operator_closure.md`
- `theory/theorem_discharge_yukawa_overlap_texture_source.md`
- `theory/theorem_discharge_yukawa_overlap_kernel_selection.md`
- `theory/theorem_discharge_yukawa_distance_overlap_law.md`
- `theory/theorem_discharge_legacy_geometric_overlap_bridge.md`
- `theory/theorem_discharge_finite_width_overlap_rank.md`
- `theory/theorem_discharge_qj_eigenfunction_map.md`
- `theory/theorem_discharge_raw_mode_berger_harmonic_map.md`
- `theory/theorem_discharge_m_weight_assignment.md`
- `theory/theorem_discharge_harmonic_highest_weight_normalization.md`
- `theory/theorem_discharge_leading_axis_m_weight.md`
- `theory/theorem_discharge_y0_axis_identification.md`
- `theory/theorem_discharge_m_multiplet_harmonic_features.md`
- `theory/theorem_discharge_generic_y0_wigner_feature_rank.md`
- `theory/theorem_discharge_y0_coordinate_constraint.md`
- `theory/theorem_discharge_generic_finite_width_feature_rank.md`

Candidate master equation:

```text
S_BHSM,candidate =
S_SM,local
+ S_T
+ S_boundary
+ S_response
+ S_collective-threshold
```

## Connected Topographic-Curvature Extension

The collective-curvature layer is a connected topographic-gravity extension candidate. It does not claim that dark matter is solved, and it does not claim that particle dark matter is disproven. Empirical gravity tests remain required.

## How To Reproduce

```powershell
git clone https://github.com/ncarberry64/Berger-Hopf-Standard-Model.git
cd Berger-Hopf-Standard-Model
python -m pip install -e .
python -m pytest -q
```

Optional audit tools:

```powershell
python tools/audit_forbidden_claims.py
python tools/audit_bhsm_status.py
python tools/audit_frozen_prediction_integrity.py
```

## Repository Map

| Path | Purpose |
| --- | --- |
| `src/` | executable model, screen, and audit code |
| `tests/` | regression, guardrail, and integrity tests |
| `theory/` | theory ledgers, candidate synthesis, and machine-readable reports |
| `docs/` | GitHub-facing reader, claim, reproducibility, and release-status docs |
| `audits/` | sprint audit scripts and reports |
| `candidates/` | non-official candidate variants |
| `manuscript/` | manuscript source and paper artifacts |
| `tools/` | repository status and guardrail audit helpers |

## Claim Hygiene

Allowed public language includes:

- candidate completion framework
- repo-audited candidate architecture
- test-backed discrete geometric skeleton
- conditional fermion ledger generation
- mass numerical closure unresolved
- replacement by derivation remains the long-term goal
- collective-curvature dark-matter interpretation candidate
- connected topographic-gravity extension

Forbidden public language includes claims that BHSM proves or has replaced the Standard Model, solves dark matter, disproves particle dark matter, closes the mass engine, or derives all Standard Model constants.

Boundary-action status: the current development line includes a candidate boundary action term-realization audit for the Hessian scaffold. It supports the closure-spectrum route diagnostically, while the full Berger-Hopf boundary action and full Hessian proof remain open.

Second-variation status: the follow-on audit computes local Hessian coefficients for the finite boundary-action surrogates and supports the projector scaffold diagnostically. It does not complete the full Berger-Hopf Hessian proof.

Theorem-level boundary status: the current scaffold separates Berger-Hopf boundary axioms, theorem statements, lemmas, proof obligations, and non-tautology risks. It does not claim the boundary action, full Hessian, closure spectrum, finite algebra, or charge/anomaly bridge are fully derived.

Primitive closure discharge status: the current theorem-discharge branch conditionally derives positive integer phase admissibility, the minimal orientation sector `d=2`, the minimal non-involutive cyclic sector `d=3`, and primitive closure selectors `{1,2,3}`. Downstream Standard Model derivation and replacement readiness remain open.

Yukawa operator-closure status: the current theorem-discharge branch conditionally derives exactly four renormalizable boundary Yukawa closure classes from boundary hypercharge closure, active-orientation contraction, cyclic/reference contraction, and the derived scalar/conjugate scalar doublets. Numerical Yukawa values, fermion mass ratios, CKM/PMNS mixing, and replacement readiness remain open.

Yukawa overlap texture-source status: the current theorem-discharge branch conditionally lifts those four operator classes to symbolic 3x3 boundary-overlap Yukawa matrix scaffolds with `M_f=vY_f/sqrt(2)`. Numerical overlap values, fermion mass ratios, CKM/PMNS mixing, and replacement readiness remain open.

Yukawa overlap-kernel selection status: the current theorem-discharge branch conditionally classifies leading diagonal overlap sources and conditional off-diagonal overlap sources from mode alignment and diagnostic mode distances. Numerical overlap values, fermion mass ratios, CKM/PMNS mixing, and replacement readiness remain open.

Yukawa distance-to-overlap law status: the current theorem-discharge branch audits exponential, Gaussian, power/dressing, boundary-action Hessian, and selection-only candidate laws. The selection-only scaffold remains conditionally derived, but no numerical distance-to-overlap law is promoted; numerical overlap values remain open.

Legacy geometric-overlap bridge status: the current theorem-discharge branch conditionally identifies the BHSM overlap kernel with the legacy scalar-topographic internal overlap integral. The sharp-peak term is guarded as a rank-limited leading focusing approximation (`rank <= 1`), so numerical eigenfunction amplitudes, finite-width overlap moments, fermion mass ratios, CKM values, and PMNS values remain open.

Finite-width overlap-rank status: the current theorem-discharge branch derives the symbolic finite-width moment expansion and the condition under which moment terms can exceed the strict point-sampling rank-one limit. Rank-three Yukawa structure remains open until internal eigenfunction independence and finite-width moment contractions are derived from BHSM geometry without fitted masses.

QJ eigenfunction-map status: the current theorem-discharge branch derives the symbolic scaffold `E:(q,j)->psi_qj(y)` and the local value/gradient/Hessian feature vectors needed to test diagonal hierarchy and rank-three support. The explicit Berger/BHSM eigenfunction map, feature independence, numerical Yukawa values, mass ratios, CKM values, and PMNS values remain open.

Raw-mode Berger/Hopf harmonic status: the current theorem-discharge branch derives the raw-mode map `k=q+2j` from the existing `q=k-2j` relation and converts all generation ledgers to raw `(k,j)` labels. The candidate harmonic form and `j` fiber-weight interpretation remain structurally motivated; the `m` orientation/base-weight assignment, explicit eigenfunction values, rank-three Yukawa theorem, and numerical Yukawa values remain open.

M-weight assignment status: the current theorem-discharge branch audits Wigner/Hopf admissibility and candidate boundary/orientation sources for the remaining `m` label. The naive convention `ell=k/2, n=j` fails admissibility on the frozen ledgers and is reported as a guardrail failure. No `m` assignment or harmonic convention is selected; explicit eigenfunctions, rank-three Yukawa support, numerical Yukawa values, and replacement readiness remain open.

Harmonic highest-weight status: the current theorem-discharge branch conditionally derives the `n`-weight convention from `q=k-2j` by rewriting `q/2=k/2-j`. With `ell=k/2`, this gives `n=q/2` and `j=ell-n` as the lowering index across the frozen ledgers. The `m` orientation/base-weight assignment, explicit eigenfunctions, rank-three Yukawa theorem, numerical Yukawa values, and replacement readiness remain open.

Leading-axis m-weight status: the current theorem-discharge branch audits the candidate leading focused component `m=n=q/2`. The labels are admissible on the frozen ledgers, but the assignment is not promoted because the repo does not yet derive `y0` as a Berger/Hopf identity axis or equivalent focal point, nor the corresponding Wigner/Hopf axis-sampling rule. Finite-width rank-three, numerical Yukawa, CKM, PMNS, and replacement-level claims remain open.

Y0 axis-identification status: the current theorem-discharge branch separates the supported statement that `y0` is the universal scalar/topographic profile peak from the stronger, still-open statement that `y0` is a group identity, Hopf pole, Berger axis, or canonical Wigner sampling point. Therefore `m=n=q/2` remains structurally motivated rather than derived.

M-multiplet harmonic feature status: the current theorem-discharge branch derives a conditional scaffold that assigns the full admissible Wigner/Hopf `m`-multiplet to each `(k,q)` internal mode. It documents the axis-collapse case and the generic-`y0` case, but it does not force a single `m`, derive finite-width rank-three support, numerical Yukawa values, CKM, PMNS, or replacement readiness.

Generic-y0 Wigner feature-rank status: the current theorem-discharge branch derives the symbolic evaluation scaffold `D^{k/2}_{m,q/2}(y0)=exp(-i*m*alpha0)*d^{k/2}_{m,q/2}(beta0)*exp(-i*(q/2)*gamma0)`. It identifies `beta0` as the reduced-Wigner magnitude selector and `alpha0,gamma0` as phase structure, while leaving numerical y0 coordinates, feature-rank independence, finite-width rank-three, numerical Yukawa values, CKM, PMNS, and replacement readiness open.

Y0 coordinate-constraint status: the current theorem-discharge branch records `alpha0,gamma0` as conditional phase-structure coordinates and `beta0` as the reduced-Wigner magnitude selector. It does not derive alpha/gamma gauge fixing, a geometry-fixed beta0, beta0 axis-collapse, full y0 coordinates, finite-width rank-three support, numerical Yukawa values, CKM, PMNS, or replacement readiness.

Generic finite-width feature-rank status: the current theorem-discharge branch defines the symbolic finite-width feature-rank scaffold and Gram/minor rank condition for the retained y0 Wigner feature multiplets. It does not derive a nonzero symbolic determinant, feature-rank independence, finite-width rank-three Yukawa matrices, numerical Yukawa values, CKM, PMNS, or replacement readiness.

Explicit symbolic Gram/minor status: the current theorem-discharge branch constructs explicit generation feature matrices and enumerates symbolic 3x3 minor candidates tied to Wigner/Hopf jet expressions. It does not derive a nonzero symbolic minor, local Wigner/Hopf jet independence, finite-width rank-three Yukawa matrices, numerical Yukawa values, CKM, PMNS, or replacement readiness.

Numerical input closure-map status: BHSM now has an integrated conditional structural architecture for SM-like finite algebra, charges, Higgs/scalar mass generation, fermion hierarchy, CKM, PMNS, and CP sources. Numerical closure remains open. The closure map exposes remaining symbolic inputs, marks forbidden fit routes, and requires pre-comparison locking before any numerical prediction claim.

## Citation / DOI

Use `CITATION.cff` for citation metadata. Zenodo metadata is recorded in `.zenodo.json`; do not create or edit external release metadata without explicit author instruction.

## Contact / Author

Author: Norman P. Carberry
ORCID: https://orcid.org/0009-0000-6650-3485

## License

All rights reserved. See `LICENSE.md`.
