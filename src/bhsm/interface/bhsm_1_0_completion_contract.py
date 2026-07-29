"""BHSM v6.30.6 governance-only completion contract.

This module reconciles the repository's historical completion ledgers with
one explicit three-tier BHSM 1.0 definition of done.  It adds no physics and
changes no frozen prediction.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


VERSION = "v6.30.6"
SPRINT = "bhsm-1-0-completion-contract-v6-30-6"
SOURCE_MAIN_SHA = "e39f936b285d1917e29ed4803dc5e46e65e4bfc2"
PRIMARY_VERDICT = (
    "BHSM_1_0_COMPLETION_CONTRACT_ESTABLISHED_RELEASE_BLOCKERS_OPEN"
)
NEXT_BLOCKER = "RB-02_SCALAR_QUARTIC_INVARIANT_SELECTION"

ARTIFACT_FILES = {
    "completion": "BHSM_1_0_completion_gate.json",
    "dag": "BHSM_release_blocker_DAG.json",
    "scope": "BHSM_scope_relevance_registry.json",
}

FROZEN_HASHES = {
    "docs/frozen_predictions.md": (
        "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
    ),
    "docs/frozen_predictions.json": (
        "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"
    ),
}

GUARDS = {
    "scientific_formula_changed": False,
    "frozen_prediction_changed": False,
    "official_prediction_changed": False,
    "measured_input_used": False,
    "fitted_parameter_used": False,
    "new_action_term_added": False,
    "new_primitive_added": False,
    "new_scale_added": False,
    "empirical_inverse_used": False,
    "pseudoinverse_used": False,
    "regulator_changed": False,
    "vacuum_subtracted": False,
    "physical_mass_claimed": False,
    "global_stability_claimed": False,
    "peer_review_made_internal_gate": False,
    "institutional_acceptance_made_internal_gate": False,
}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def tier_definitions() -> list[dict[str, Any]]:
    return [
        {
            "tier": "A",
            "name": "BHSM Core Complete",
            "possible_verdict": "BHSM_CORE_COMPLETE",
            "cumulative": True,
            "requirements": [
                "one parent action for every claimed sector",
                "complete configuration and variational domain",
                "correct gauge and fermion structure",
                "anomaly consistency",
                "generation structure",
                "charged and neutral current structure",
                "mathematically valid operators and reductions",
                "all dimensionless headline relations closed",
                (
                    "no unselected dimensionless coefficient that changes "
                    "an official prediction"
                ),
            ],
            "current_status": "BLOCKED",
            "verdict_emitted": False,
            "blocking_gates": ["G1", "G2", "G3", "G4_dimensionless"],
        },
        {
            "tier": "B",
            "name": "BHSM Physical Complete",
            "possible_verdicts": [
                "BHSM_PHYSICAL_COMPLETE_ACTION_DERIVED_SCALE",
                "BHSM_PHYSICAL_COMPLETE_ONE_UNIVERSAL_SCALE_CALIBRATION",
            ],
            "cumulative": True,
            "requires_tier": "A",
            "requirements": [
                "canonical four-dimensional normalization",
                "physical scale bridge",
                "physical observable map",
                "masses, couplings, and mixing quantities classified by scheme",
                "no hidden retuning",
                "representative established-physics benchmarks",
            ],
            "one_scale_allowance": {
                "dimensionless_structure_independently_derived": True,
                "exactly_one_universal_dimensionful_scale": True,
                "common_to_all_sectors": True,
                "openly_labeled_calibration": True,
                "calibrated_quantity_not_prediction": True,
                "no_dimensionless_fit": True,
                "no_sector_retuning": True,
            },
            "current_status": "NOT_ELIGIBLE_TIER_A_BLOCKED",
            "verdict_emitted": False,
            "blocking_gates": ["G4"],
        },
        {
            "tier": "C",
            "name": "BHSM 1.0 Release Complete",
            "possible_verdict": "BHSM_1_0_RELEASE_COMPLETE",
            "cumulative": True,
            "requires_tier": "B",
            "requirements": [
                "frozen finite benchmark suite",
                "frozen novel predictions",
                "falsification criteria",
                "reproducible clean-environment build",
                "deterministic artifacts",
                "complete derivation manuscript",
                "status and claim ledgers",
                "public release package",
                "no remaining release blocker",
            ],
            "current_status": "NOT_ELIGIBLE_TIER_B_BLOCKED",
            "verdict_emitted": False,
            "blocking_gates": ["G5", "G6"],
        },
    ]


def gate_rows() -> list[dict[str, Any]]:
    return [
        {
            "gate_id": "G1",
            "name": "Parent action",
            "tier": "A",
            "status": "BLOCKED",
            "evidence": [
                "artifacts/BHSM_full_completion_gate_v4_0.json",
                "artifacts/BHSM_action_derivation_gates_report_v1_9.json",
                "artifacts/BHSM_G5_action_source_ledger_v6_30_7.json (required)",
            ],
            "open_blockers": ["RB-01", "RB-02", "RB-03", "RB-09"],
        },
        {
            "gate_id": "G2",
            "name": "Mathematical legitimacy",
            "tier": "A",
            "status": "PARTIAL",
            "evidence": [
                (
                    "docs/bhsm_fixed_h_lyapunov_schmidt_potential_"
                    "v6_30_5.md"
                ),
                "artifacts/BHSM_full_completion_blocker_ledger_v1_8.json",
            ],
            "closed_subresults": [
                "strict D0 fixed-h operator and adjoint domain",
                "D0 complement inverse and reduction through fourth order",
                "exact-branch obstruction correctly separated",
            ],
            "open_blockers": ["RB-03", "RB-10", "RB-11"],
        },
        {
            "gate_id": "G3",
            "name": "Standard Model structure",
            "tier": "A",
            "status": "BLOCKED",
            "evidence": [
                "docs/current_bhsm_status.md",
                "artifacts/BHSM_full_completion_blocker_ledger_v1_8.json",
                "docs/BHSM_HARD_CLOSURE_STATUS.json",
            ],
            "open_blockers": [
                "RB-03",
                "RB-04",
                "RB-05",
                "RB-06",
                "RB-07",
                "RB-08",
                "RB-10",
                "RB-11",
            ],
        },
        {
            "gate_id": "G4",
            "name": "Parameter and scale closure",
            "tier": "B",
            "status": "BLOCKED",
            "dimensionless_status": "BLOCKED",
            "scale_status": "BLOCKED",
            "evidence": [
                "artifacts/BHSM_scale_phase_permission_v6_30_5.json",
                "artifacts/BHSM_physical_normalization_gate_v2_0.json",
                "artifacts/BHSM_dimensionful_scale_bridge_v4_0.json",
            ],
            "open_blockers": [
                "RB-02",
                "RB-04",
                "RB-05",
                "RB-06",
                "RB-08",
                "RB-09",
                "RB-12",
                "RB-13",
            ],
        },
        {
            "gate_id": "G5",
            "name": "Finite validation and prediction set",
            "tier": "C",
            "status": "BLOCKED_DOWNSTREAM",
            "evidence": [
                "docs/bhsm_completion_scorecard.json",
                "artifacts/BHSM_falsification_gates_v1.json",
                "artifacts/BHSM_v1_2_0_prediction_registry_status.json",
            ],
            "open_blockers": ["RB-14", "RB-15"],
        },
        {
            "gate_id": "G6",
            "name": "Reproducibility and release",
            "tier": "C",
            "status": "PARTIAL_DOWNSTREAM",
            "evidence": [
                "artifacts/BHSM_public_review_readiness_manifest_v6_21_0.json",
                "docs/external_reproduction_status.md",
                "ARTIFACT_INDEX.md",
            ],
            "closed_subresults": [
                "offline test suite",
                "frozen hash audit",
                "claim audit",
                "public repository readiness",
            ],
            "open_blockers": ["RB-16"],
        },
    ]


def _blocker(
    blocker_id: str,
    title: str,
    gate: str,
    rationale: str,
    affected: list[str],
    evidence: list[str],
    dependencies: list[str],
    next_action: str,
    *,
    tractable_now: bool,
) -> dict[str, Any]:
    return {
        "blocker_id": blocker_id,
        "title": title,
        "release_blocking": True,
        "release_relevance_rationale": rationale,
        "affected_headline_deliverables": affected,
        "gate": gate,
        "evidence_files": evidence,
        "dependencies": dependencies,
        "next_valid_action": next_action,
        "tractable_now": tractable_now,
        "status": "OPEN",
    }


def release_blockers() -> list[dict[str, Any]]:
    return [
        _blocker(
            "RB-01",
            "Unified parent-action provenance",
            "G1",
            (
                "Missing coefficient provenance can change parent-action "
                "terms and every downstream operator."
            ),
            ["frozen parent action", "all sector action maps"],
            [
                "artifacts/BHSM_full_completion_gate_v4_0.json",
                "artifacts/BHSM_full_completion_blocker_ledger_v1_8.json",
            ],
            [],
            "close or remove every claimed sector lacking one action source",
            tractable_now=False,
        ),
        _blocker(
            "RB-02",
            "Scalar quartic invariant selection",
            "G1",
            (
                "The unselected dimensionless scalar quartic invariant "
                "changes the canonical quartic and local stability."
            ),
            [
                "BHSM fixed-h canonical quartic",
                "scalar local-stability verdict",
                "Tier A dimensionless parameter ledger",
            ],
            [
                "artifacts/BHSM_fixed_h_canonical_interaction_v6_30_5.json",
                "artifacts/BHSM_scale_phase_permission_v6_30_5.json",
            ],
            [],
            (
                "derive field-normalization invariant and audit its actual "
                "parent-action source in v6.30.7"
            ),
            tractable_now=True,
        ),
        _blocker(
            "RB-03",
            "Sector projectors, domains, and boundary operators",
            "G2",
            (
                "Open projector and action-domain provenance can change "
                "charges, generations, and particle assignments."
            ),
            ["sector assignment ledger", "generation and charge benchmark"],
            [
                "artifacts/BHSM_action_derivation_gates_report_v1_9.json",
                "artifacts/BHSM_full_completion_blocker_ledger_v1_8.json",
            ],
            ["RB-01"],
            "derive sector boundary functional from the unified action",
            tractable_now=False,
        ),
        _blocker(
            "RB-04",
            "Charged hierarchy and stiffness normalization",
            "G3",
            (
                "Unselected charged stiffness changes official charged "
                "mass-ratio relations."
            ),
            ["charged mass-ratio benchmark", "charged K_f operator"],
            ["artifacts/BHSM_full_completion_blocker_ledger_v1_8.json"],
            ["RB-01", "RB-03"],
            "derive rho_ch and bridge magnitudes from the charged action",
            tractable_now=False,
        ),
        _blocker(
            "RB-05",
            "Charged-lepton eta_l action source",
            "G3",
            (
                "The candidate eta_l changes headline charged-lepton ratios "
                "and is not independently derived."
            ),
            ["charged-lepton ratio benchmark"],
            [
                "docs/BHSM_HARD_CLOSURE_STATUS.json",
                "docs/BHSM_SEQUENTIAL_BLOCKER_CLOSURE.json",
            ],
            ["RB-01", "RB-03"],
            "derive or remove eta_l from the official prediction set",
            tractable_now=False,
        ),
        _blocker(
            "RB-06",
            "CKM mixing law and 1/16 exponent",
            "G3",
            (
                "The exponent changes headline CKM elements and remains a "
                "candidate projection chain."
            ),
            ["CKM benchmark", "CKM official prediction artifact"],
            [
                "docs/BHSM_HARD_CLOSURE_STATUS.json",
                "artifacts/BHSM_ckm_completion_gate_v4_0.json",
            ],
            ["RB-03", "RB-04"],
            "derive or reject the exponent without comparison input",
            tractable_now=False,
        ),
        _blocker(
            "RB-07",
            "PMNS and neutrino structural closure",
            "G3",
            (
                "The current candidate leakage ledger does not fix the "
                "claimed neutrino operator, PMNS map, or physical unit map."
            ),
            ["PMNS benchmark", "neutrino observable map"],
            [
                "docs/BHSM_SEQUENTIAL_BLOCKER_CLOSURE.json",
                "artifacts/BHSM_neutral_scale_gate_v4_0.json",
            ],
            ["RB-01", "RB-03", "RB-10", "RB-13"],
            "derive the operator and map or remove numerical claims",
            tractable_now=False,
        ),
        _blocker(
            "RB-08",
            "Gauge normalization",
            "G3",
            (
                "Conditional gauge normalization can change canonical "
                "dimensionless couplings."
            ),
            ["gauge-coupling benchmark", "canonical 4D action"],
            [
                "artifacts/BHSM_full_completion_blocker_ledger_v1_8.json",
                "docs/physical_normalization_gate.md",
            ],
            ["RB-01", "RB-03", "RB-09"],
            "derive boundary trace and gauge kinetic normalization",
            tractable_now=False,
        ),
        _blocker(
            "RB-09",
            "Boundary measure, collar, and transport normalization",
            "G1",
            (
                "The missing normalized measure affects action coefficients "
                "and physical observable transport."
            ),
            ["normalized parent action", "physical observable map"],
            ["artifacts/BHSM_full_completion_blocker_ledger_v1_8.json"],
            ["RB-01"],
            "derive physical measure units and cross-scale transport",
            tractable_now=False,
        ),
        _blocker(
            "RB-10",
            "Neutral response domain and positivity",
            "G2",
            (
                "The response cone is conditional and can change the "
                "admissible neutral field domain."
            ),
            ["neutral-current benchmark", "neutral response operator"],
            ["artifacts/BHSM_full_completion_blocker_ledger_v1_8.json"],
            ["RB-01", "RB-09"],
            "derive the response cone from the complete neutral action",
            tractable_now=False,
        ),
        _blocker(
            "RB-11",
            "Scalar/topographic claimed-sector action closure",
            "G2",
            (
                "The complete claimed scalar/topographic profile and collar "
                "action remain conditional beyond the D0 local reduction."
            ),
            ["scalar-role benchmark", "claimed Higgs/topographic map"],
            [
                "artifacts/BHSM_full_completion_blocker_ledger_v1_8.json",
                "theory/theorem_discharge_higgs_scalar_boundary_mechanism.md",
            ],
            ["RB-01", "RB-02", "RB-09"],
            "close only profile/action pieces retained in the 1.0 claim set",
            tractable_now=False,
        ),
        _blocker(
            "RB-12",
            "Physical scale bridge",
            "G4",
            (
                "No physical mass or unit-bearing observable is defined "
                "until one action-derived scale or one allowed universal "
                "calibration is isolated."
            ),
            ["physical mass map", "physical scale artifact"],
            [
                "artifacts/BHSM_scale_phase_permission_v6_30_5.json",
                "artifacts/BHSM_dimensionful_scale_bridge_v4_0.json",
            ],
            ["RB-02", "RB-08", "RB-09", "RB-11"],
            "enter v6.31 only after an explicit scalar-quartic permission",
            tractable_now=False,
        ),
        _blocker(
            "RB-13",
            "Scheme and observable transport map",
            "G4",
            (
                "Official masses, couplings, and mixings require a common "
                "scheme and observable map without hidden retuning."
            ),
            ["physical observable map", "scheme-classified benchmark"],
            [
                "docs/mass_width_renormalization_open_gates.md",
                "artifacts/common_scale_transport_closure_or_obstruction_v1.json",
            ],
            ["RB-04", "RB-06", "RB-08", "RB-09", "RB-12"],
            "derive the minimal scheme map for retained 1.0 observables",
            tractable_now=False,
        ),
        _blocker(
            "RB-14",
            "Finite official benchmark suite freeze",
            "G5",
            (
                "Without a finite typed benchmark set, headline equations "
                "cannot be reproducibly evaluated or frozen."
            ),
            ["BHSM 1.0 benchmark manifest"],
            ["docs/bhsm_completion_scorecard.json"],
            ["RB-03", "RB-04", "RB-06", "RB-07", "RB-08", "RB-11", "RB-13"],
            "freeze only representative benchmarks after upstream closure",
            tractable_now=False,
        ),
        _blocker(
            "RB-15",
            "Novel prediction and falsification freeze",
            "G5",
            (
                "Release claims require immutable no-fit predictions and "
                "explicit kill criteria."
            ),
            ["novel prediction registry", "falsification criteria"],
            [
                "artifacts/BHSM_falsification_gates_v1.json",
                "artifacts/BHSM_v1_2_0_prediction_registry_status.json",
            ],
            ["RB-12", "RB-13", "RB-14"],
            "freeze the retained prediction set after upstream closure",
            tractable_now=False,
        ),
        _blocker(
            "RB-16",
            "BHSM 1.0 release manuscript and clean reproduction package",
            "G6",
            (
                "Tier C requires a clean environment to regenerate all "
                "headline artifacts and the complete manuscript."
            ),
            ["release manuscript", "release manifest", "clean build report"],
            [
                "artifacts/BHSM_public_review_readiness_manifest_v6_21_0.json",
                "docs/external_reproduction_status.md",
            ],
            ["RB-14", "RB-15"],
            "assemble only after all scientific release blockers close",
            tractable_now=False,
        ),
    ]


def post_1_0_backlog() -> list[dict[str, Any]]:
    rows = [
        (
            "P10-01",
            "exact_branch_restoration",
            "restore the generic fixed-h neighboring exact branch",
            "the reduced effective family is the operative 1.0 scalar object",
        ),
        (
            "P10-02",
            "isolated_cancellation_higher_order",
            "higher interaction at the unselected exact-branch cancellation",
            "no frozen mechanism selects the cancellation value",
        ),
        (
            "P10-03",
            "arbitrary_perturbative_orders",
            "orders beyond the first physically relevant interaction",
            "cannot alter the established first interaction absent a dependency",
        ),
        (
            "P10-04",
            "global_vacuum_classification",
            "classify every vacuum and nonlinear solution",
            "Tier A needs only configurations used by retained predictions",
        ),
        (
            "P10-05",
            "topology_catalogue",
            "classify every boundary topology and admissible manifold",
            "not required by a retained 1.0 headline claim",
        ),
        (
            "P10-06",
            "quantum_gravity",
            "full nonperturbative quantum-gravity completion",
            "outside the declared finite BHSM 1.0 claim set",
        ),
        (
            "P10-07",
            "all_loop_rg",
            "all-loop renormalization and every threshold",
            "only minimal scheme maps for retained benchmarks are required",
        ),
        (
            "P10-08",
            "collider_catalogue",
            "every amplitude, collider process, and full hadronization",
            "collider production is not a current BHSM 1.0 claim",
        ),
        (
            "P10-09",
            "downstream_matter",
            "hadron, nuclear, atomic, molecular, material, or biological models",
            "outside release claims",
        ),
        (
            "P10-10",
            "astrophysical_cosmological_catalogue",
            "full astrophysical simulations and cosmological history",
            "not required by a frozen 1.0 prediction",
        ),
        (
            "P10-11",
            "black_hole_catalogue",
            "black-hole classifications unrelated to a retained 1.0 claim",
            "scope-creep firewall",
        ),
        (
            "P10-12",
            "external_acceptance",
            "peer review, citation, institutional endorsement, future confirmation",
            "external validation begins after internal release completion",
        ),
        (
            "P10-13",
            "external_hep_runtime",
            "licensed FeynRules/MadGraph production for unclaimed collider outputs",
            "nonblocking unless a later official 1.0 deliverable depends on it",
        ),
    ]
    return [
        {
            "item_id": item_id,
            "post_1_0_category": category,
            "title": title,
            "release_blocking": False,
            "nonblocking_rationale": rationale,
            "status": "POST_BHSM_1_0_RESEARCH_BACKLOG",
        }
        for item_id, category, title, rationale in rows
    ]


def scope_relevance_test() -> dict[str, Any]:
    return {
        "release_blocking_rule": (
            "release_blocking=true only when resolution can materially change "
            "one of the ten enumerated release objects"
        ),
        "material_change_objects": [
            "parent-action term or coefficient",
            "admissible field or variational domain",
            "gauge representation, charge, generation, or particle assignment",
            "canonical dimensionless parameter",
            "physical scale or observable map",
            "official benchmark result",
            "official novel prediction",
            "falsification criterion",
            "reproducibility of a headline result",
            "truth of a BHSM 1.0 claim",
        ],
        "requirements": [
            "every release blocker names an affected headline deliverable",
            "every release blocker gives a material-change rationale",
            "every nonblocking item has a post-1.0 category",
        ],
    }


def exact_branch_scope_row() -> dict[str, Any]:
    return {
        "item_id": "D0_EXACT_BRANCH_RESTORATION",
        "release_blocking": False,
        "status": "COMPLETED_SCIENTIFIC_OBSTRUCTION",
        "branch_cancellation_lambda5": -18.19749278903491,
        "quartic_minimum_threshold": -13.95809839182684,
        "strict_inequality": (
            "lambda5_exact_branch < lambda5_quartic_minimum_threshold"
        ),
        "inequality_holds": True,
        "reason": (
            "the cancellation locus lies in the quartic-maximum region; the "
            "valid reduced effective family is sufficient for the BHSM 1.0 "
            "local scalar object"
        ),
        "higher_order_at_cancellation": "POST_BHSM_1_0_RESEARCH_BACKLOG",
        "evidence": [
            "artifacts/BHSM_fixed_h_exact_branch_permission_v6_30_5.json",
            "artifacts/BHSM_fixed_h_local_stability_v6_30_5.json",
        ],
    }


def dag_payload() -> dict[str, Any]:
    blockers = release_blockers()
    nodes = [
        {
            "node_id": row["blocker_id"],
            "kind": "release_blocker",
            "depends_on": row["dependencies"],
            "unlocks_gate": row["gate"],
            "status": row["status"],
        }
        for row in blockers
    ]
    nodes.extend(
        {
            "node_id": row["gate_id"],
            "kind": "completion_gate",
            "depends_on": row["open_blockers"],
            "status": row["status"],
        }
        for row in gate_rows()
    )
    nodes.extend(
        [
            {
                "node_id": "TIER_A",
                "kind": "completion_tier",
                "depends_on": ["G1", "G2", "G3", "G4"],
                "status": "BLOCKED",
            },
            {
                "node_id": "TIER_B",
                "kind": "completion_tier",
                "depends_on": ["TIER_A", "G4"],
                "status": "NOT_ELIGIBLE",
            },
            {
                "node_id": "TIER_C",
                "kind": "completion_tier",
                "depends_on": ["TIER_B", "G5", "G6"],
                "status": "NOT_ELIGIBLE",
            },
        ]
    )
    return {
        "artifact": "BHSM_release_blocker_DAG",
        "version": VERSION,
        "source_main_sha": SOURCE_MAIN_SHA,
        "nodes": nodes,
        "highest_upstream_tractable_blocker": NEXT_BLOCKER,
        "dependent_work_forbidden_until_parent_closes": True,
        "historical_ledgers_extended": [
            "artifacts/BHSM_full_completion_blocker_ledger_v1_8.json",
            "docs/BHSM_HARD_CLOSURE_STATUS.json",
            "docs/BHSM_SEQUENTIAL_BLOCKER_CLOSURE.json",
        ],
        **GUARDS,
    }


def historical_completion_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_1_0_completion_gate",
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "definition_of_release_complete": (
            "Every official prediction and benchmark is derived from one "
            "frozen parent action and input ledger; required mathematical, "
            "normalization, scale, and observable maps close; benchmarks, "
            "novel predictions, and falsification conditions are frozen; "
            "and no release blocker can change a headline deliverable."
        ),
        "tiers": tier_definitions(),
        "gates": gate_rows(),
        "release_blockers": release_blockers(),
        "post_1_0_items": post_1_0_backlog(),
        "current_tier_status": {
            "Tier_A": "BLOCKED",
            "Tier_B": "NOT_ELIGIBLE_TIER_A_BLOCKED",
            "Tier_C": "NOT_ELIGIBLE_TIER_B_BLOCKED",
        },
        "next_highest_upstream_blocker": NEXT_BLOCKER,
        "current_verdict": PRIMARY_VERDICT,
        "BHSM_1_0_release_complete": False,
        "external_validation_is_internal_gate": False,
        "frozen_hashes": FROZEN_HASHES,
        **GUARDS,
    }


def completion_payload() -> dict[str, Any]:
    """Return the v6.30.8-reconciled canonical completion gate.

    The historical v6.30.6 DAG and scope registry remain reproducible, but
    the older materializer must not restore a stale canonical gate.
    """

    from bhsm.interface import claim_input_completion_consistency as current

    return current.canonical_completion_gate_payload()


def scope_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_scope_relevance_registry",
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "release_relevance_test": scope_relevance_test(),
        "release_blockers": release_blockers(),
        "nonblocking_items": post_1_0_backlog(),
        "fixed_h_exact_branch": exact_branch_scope_row(),
        "peer_review_internal_blocker": False,
        "institutional_acceptance_internal_blocker": False,
        "arbitrary_higher_order_internal_blocker": False,
        "primary_verdict": PRIMARY_VERDICT,
        "frozen_hashes": FROZEN_HASHES,
        **GUARDS,
    }


def validate_contract() -> dict[str, bool]:
    blockers = release_blockers()
    backlog = post_1_0_backlog()
    return {
        "every_open_item_has_release_blocking": all(
            "release_blocking" in row for row in blockers + backlog
        ),
        "every_release_blocker_has_rationale": all(
            bool(row["release_relevance_rationale"]) for row in blockers
        ),
        "every_release_blocker_names_headline": all(
            bool(row["affected_headline_deliverables"]) for row in blockers
        ),
        "every_nonblocking_item_has_category": all(
            bool(row["post_1_0_category"]) for row in backlog
        ),
        "peer_review_not_internal_blocker": True,
        "institutional_acceptance_not_internal_blocker": True,
        "arbitrary_higher_order_not_blocking": True,
        "exact_branch_restoration_not_blocking": (
            exact_branch_scope_row()["release_blocking"] is False
        ),
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "completion": completion_payload(),
        "dag": dag_payload(),
        "scope": scope_payload(),
    }


def artifact_bytes() -> dict[str, bytes]:
    return {
        ARTIFACT_FILES[key]: deterministic_json(payload).encode("utf-8")
        for key, payload in artifact_payloads().items()
    }


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    paths = []
    for filename, content in artifact_bytes().items():
        path = target / filename
        path.write_bytes(content)
        paths.append(path)
    return paths
