# Berger-Hopf Standard Model (BHSM)

Status: Full BHSM v1.0 Candidate -- repo-audited candidate architecture, not yet a completed proof or replacement of the Standard Model.

Full BHSM v1.0 Candidate is a repo-audited completion framework, not yet a completed replacement of the Standard Model. Its strategic objective is replacement by derivation: the Standard Model should ultimately emerge as the low-energy effective limit of BHSM. Until that derivation is achieved, local SM gauge structure remains a preserved infrared layer, while BHSM provides a candidate Berger-Hopf/topographic completion of the flavor, channel, generation, response, and collective-threshold architecture.

## What BHSM Is

BHSM is a no-retuning Berger-Hopf/topographic candidate framework for Standard Model flavor, channel, generation, response, mass-structure, and boundary-geometry layers. It preserves the local Standard Model gauge layer as an infrared input until that layer is derived from BHSM.

BHSM is not yet a completed replacement of the Standard Model. The long-term goal is replacement by derivation.

## Current Status

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

## Citation / DOI

Use `CITATION.cff` for citation metadata. Zenodo metadata is recorded in `.zenodo.json`; do not create or edit external release metadata without explicit author instruction.

## Contact / Author

Author: Norman P. Carberry
ORCID: https://orcid.org/0009-0000-6650-3485

## License

All rights reserved. See `LICENSE.md`.
