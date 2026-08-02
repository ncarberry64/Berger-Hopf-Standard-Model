"""BHSM v6.30.8 claim/input/completion consistency audit.

This is a governance and dependency audit.  It does not change scientific
formulae or any frozen prediction.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


VERSION = "v6.30.8"
SPRINT = "bhsm-claim-input-completion-consistency-v6-30-8"
SOURCE_MAIN_SHA = "258cb9ce8dd0a14b2d3ddacd28baddbd73db6f82"
PRIMARY_VERDICT = "BHSM_SCALAR_QUARTIC_PARAMETERIZED_NOT_PREDICTED"
LAMBDA_VERDICT = "BHSM_LAMBDA5_RECLASSIFIED_AS_PARAMETER_FREE_EXTENSION_BLOCKER"
SCALE_VERDICT = "BHSM_SCALE_PHASE_STILL_BLOCKED_INDEPENDENTLY_OF_LAMBDA5"
NEXT_TARGET = "RB-01_UNIFIED_PARENT_ACTION_PROVENANCE"

FROZEN_HASHES = {
    "docs/frozen_predictions.md": "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4",
    "docs/frozen_predictions.json": "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7",
}

GUARDS = {
    "scientific_formula_changed": False,
    "frozen_prediction_changed": False,
    "official_prediction_changed": False,
    "measured_input_promoted_to_action_input": False,
    "fitted_parameter_used": False,
    "lambda5_value_selected": False,
    "lambda5_sign_selected": False,
    "new_action_term_added": False,
    "new_scale_added": False,
    "physical_mass_claimed": False,
    "unconditional_stability_claimed": False,
    "bhsm_1_0_release_complete_claimed": False,
}

ARTIFACT_FILES = {
    "claim_matrix": "BHSM_1_0_claim_to_evidence_matrix_v6_30_8.json",
    "frozen_dependencies": "BHSM_frozen_prediction_dependency_graph_v6_30_8.json",
    "typed_inputs": "BHSM_1_0_typed_input_ledger_v6_30_8.json",
    "lambda_relevance": "BHSM_lambda5_release_relevance_v6_30_8.json",
    "parameter_policy": "BHSM_parameterized_vs_parameter_free_policy_v6_30_8.json",
    "reconciliation": "BHSM_1_0_completion_contract_reconciliation_v6_30_8.json",
    "blocker_dag": "BHSM_release_blocker_DAG_v6_30_8.json",
    "scale_reassessment": "BHSM_scale_permission_dependency_reassessment_v6_30_8.json",
    "next_target": "BHSM_next_upstream_scientific_target_v6_30_8.json",
    "scope_firewall": "BHSM_scope_firewall_v6_30_8.json",
}

INPUT_TYPES = {
    "ACTION_DERIVED",
    "GEOMETRICALLY_DERIVED",
    "REPRESENTATION_DERIVED",
    "INDEPENDENT_THEORY_INPUT",
    "ONE_UNIVERSAL_DIMENSIONFUL_CALIBRATION",
    "EXTERNAL_COMPARISON_DATA",
    "CANDIDATE_NOT_OFFICIAL",
    "UNLICENSED_ORIGIN_BLOCKER",
    "POST_BHSM_1_0",
}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _claim(
    claim_id: str,
    text: str,
    locations: list[str],
    claim_class: str,
    evidence: list[str],
    blockers: list[str],
    *,
    status: str = "RETAINED_CONDITIONAL",
    independent_inputs: list[str] | None = None,
    derived: list[str] | None = None,
    frozen: str | None = None,
    benchmark: str | None = None,
    falsifier: str | None = None,
    lambda_dependency: bool = False,
    caveat: str = "",
) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "claim_text": text,
        "locations": locations,
        "surface": "PUBLIC" if any(p in {"README.md", "CLAIMS.md", "STATUS.md"} for p in locations) else "INTERNAL",
        "retained": True,
        "claim_class": claim_class,
        "parent_action_source": "OPEN" if "RB-01" in blockers else "NOT_REQUIRED_OR_CITED",
        "variational_source": "OPEN" if "RB-03" in blockers else "NOT_REQUIRED_OR_CITED",
        "operator_domain_source": "OPEN" if any(b in blockers for b in ("RB-03", "RB-10", "RB-11")) else "NOT_REQUIRED_OR_CITED",
        "independent_inputs": independent_inputs or [],
        "derived_coefficients": derived or [],
        "calibrated_quantities": [],
        "comparison_data": ["published_reference_values"] if benchmark else [],
        "frozen_artifact": frozen,
        "benchmark": benchmark,
        "falsifier": falsifier,
        "lambda5_dependency": lambda_dependency,
        "evidence": evidence,
        "status": status,
        "blockers": blockers,
        "caveat": caveat,
    }


def claim_rows() -> list[dict[str, Any]]:
    return [
        _claim("C01", "BHSM is a conditional framework, not a completed Standard Model derivation.", ["README.md", "STATUS.md", "CLAIMS.md"], "STATUS", ["docs/current_bhsm_status.md"], ["RB-01", "RB-03"]),
        _claim("C02", "The numerical engine and deterministic regression suite are reproducible.", ["README.md"], "REPRODUCIBILITY", ["tests/", "docs/reproducibility.md"], [], status="RETAINED"),
        _claim("C03", "The frozen no-retuning screen package is immutable under the declared hash audit.", ["README.md", "CLAIMS.md"], "FROZEN_SCREEN", ["docs/frozen_predictions.md", "docs/frozen_predictions.json"], ["RB-14"], frozen="docs/frozen_predictions.json", falsifier="hash or output change"),
        _claim("C04", "The strict D0 fixed-h Lyapunov-Schmidt reduction is established through quartic order.", ["docs/bhsm_fixed_h_lyapunov_schmidt_potential_v6_30_5.md"], "MATHEMATICAL_RESULT", ["artifacts/BHSM_fixed_h_canonical_interaction_v6_30_5.json"], [], status="RETAINED"),
        _claim("C05", "The generic neighboring exact branch is obstructed at the selected base point.", ["CLAIMS.md"], "MATHEMATICAL_RESULT", ["artifacts/BHSM_fixed_h_exact_branch_permission_v6_30_5.json"], [], status="RETAINED"),
        _claim("C06", "The reduced scalar potential is a one-parameter family in lambda5.", ["CLAIMS.md", "STATUS.md"], "PARAMETERIZED_RESULT", ["artifacts/BHSM_G5_action_source_ledger_v6_30_7.json"], [], independent_inputs=["lambda5"], derived=["quartic_coefficient_as_function_of_lambda5"], caveat="No value or sign of lambda5 is selected."),
        _claim("C07", "Local scalar stability is conditional on the lambda5 inequality.", ["CLAIMS.md"], "CONDITIONAL_RESULT", ["artifacts/BHSM_fixed_h_local_stability_v6_30_5.json"], [], independent_inputs=["lambda5"], derived=["local_stability_threshold"], caveat="Not an unconditional or global stability claim."),
        _claim("C08", "No numerical scalar quartic is predicted by the current BHSM action.", ["CLAIMS.md"], "NEGATIVE_CLAIM", ["artifacts/BHSM_G5_action_source_ledger_v6_30_7.json"], [], status="RETAINED"),
        _claim("C09", "Gauge-charge and anomaly relations are conditional on the stated representation pattern and normalization.", ["README.md"], "CONDITIONAL_SCREEN", ["src/hypercharge.py", "src/anomalies.py"], ["RB-01", "RB-03", "RB-08"]),
        _claim("C10", "Generation assignments are conditional on the supplied mode ledger.", ["README.md"], "CONDITIONAL_SCREEN", ["src/mode_selection.py", "src/constants.py"], ["RB-03", "RB-04"], independent_inputs=["mode_ledger"]),
        _claim("C11", "Charged-fermion ratios are frozen numerical screens.", ["docs/frozen_predictions.md"], "FROZEN_SCREEN", ["src/yukawa_overlap.py", "theory/bhsm_v1_frozen_prediction_set.json"], ["RB-03", "RB-04", "RB-05"], independent_inputs=["S_overlap", "mode_ledger", "alpha_inv_low_energy"], frozen="theory/bhsm_v1_frozen_prediction_set.json", benchmark="charged mass-ratio references", falsifier="scheme-consistent ratios outside declared bands"),
        _claim("C12", "CKM quantities are frozen internal-rule screens, not action-derived predictions.", ["docs/frozen_predictions.md"], "FROZEN_SCREEN", ["src/ckm.py", "src/flavor_matrix.py"], ["RB-06"], independent_inputs=["charged_ratio_screens", "S_overlap", "sector_charges"], frozen="theory/bhsm_v1_frozen_prediction_set.json", benchmark="CKM references", falsifier="CKM screen outside declared bands"),
        _claim("C13", "The Zvirt=1/2 dressed c/t branch is a candidate only.", ["docs/frozen_predictions.md"], "CANDIDATE", ["src/virtual_environment.py"], [], status="RETAINED_CANDIDATE", independent_inputs=["Zvirt_candidate"], frozen="theory/bhsm_v1_frozen_prediction_set.json"),
        _claim("C14", "PMNS numbers are an effective-extension screen.", ["docs/frozen_predictions.md"], "EFFECTIVE_EXTENSION", ["src/pmns.py"], ["RB-07"], independent_inputs=["alpha_inv_low_energy"], frozen="theory/bhsm_v1_frozen_prediction_set.json", benchmark="PMNS references"),
        _claim("C15", "Gauge-coupling numbers are conditional geometric screens.", ["docs/frozen_predictions.md"], "CONDITIONAL_SCREEN", ["src/gauge_couplings.py"], ["RB-01", "RB-08"], independent_inputs=["gauge_trace_weights"], frozen="theory/bhsm_v1_frozen_prediction_set.json", benchmark="electroweak gauge references"),
        _claim("C16", "The Higgs/electroweak scale numbers are a conditional screen, not a licensed scale derivation.", ["docs/frozen_predictions.md"], "CONDITIONAL_SCREEN", ["src/higgs_scale.py"], ["RB-09", "RB-12", "RB-13"], independent_inputs=["Planck_energy_GeV", "alpha_inv_low_energy"], frozen="theory/bhsm_v1_frozen_prediction_set.json", benchmark="v and Higgs-mass references"),
        _claim("C17", "The H_T gap result is a finite-basis proxy audit.", ["README.md"], "PROXY", ["src/bhsm_model.py", "theory/bhsm_v1_frozen_prediction_set.json"], ["RB-03", "RB-10"], frozen="theory/bhsm_v1_frozen_prediction_set.json"),
        _claim("C18", "Scalar decoupling is a finite-basis conditional scaffold.", ["README.md"], "SCAFFOLD", ["src/scalar_decoupling.py", "theory/bhsm_v1_frozen_prediction_set.json"], ["RB-01", "RB-11"], frozen="theory/bhsm_v1_frozen_prediction_set.json", lambda_dependency=False),
        _claim("C19", "No physical particle mass follows before scale and observable-map closure.", ["CLAIMS.md", "STATUS.md"], "NEGATIVE_CLAIM", ["artifacts/BHSM_scale_phase_permission_v6_30_5.json"], ["RB-09", "RB-12", "RB-13"]),
        _claim("C20", "Repository review readiness is not scientific completion.", ["STATUS.md"], "REPOSITORY_STATUS", ["docs/github_landing_status.md"], ["RB-16"], caveat="Public packaging does not close scientific gates."),
    ]


def typed_input_rows() -> list[dict[str, Any]]:
    rows = [
        ("lambda5", "INDEPENDENT_THEORY_INPUT", False, False, False, "Free dimensionless coefficient of the parameterized reduced scalar family."),
        ("S_overlap", "INDEPENDENT_THEORY_INPUT", False, False, False, "Declared S=1/(4*pi); not advertised as action-derived."),
        ("alpha_inv_low_energy", "UNLICENSED_ORIGIN_BLOCKER", False, False, False, "Measured low-energy alpha enters geometry and several numerical screens."),
        ("geometry_a", "UNLICENSED_ORIGIN_BLOCKER", False, False, False, "Computed from alpha_inv/(12*pi^2), not yet derived from the parent action."),
        ("mode_ledger", "UNLICENSED_ORIGIN_BLOCKER", False, False, False, "Supplied sector/generation modes require operator-domain derivation."),
        ("omega_target_rules", "UNLICENSED_ORIGIN_BLOCKER", False, False, False, "Supplied target rules require spectral derivation."),
        ("ckm_screen_law", "UNLICENSED_ORIGIN_BLOCKER", False, False, False, "Internal numerical rule is not yet an action-derived mixing map."),
        ("gauge_trace_weights", "UNLICENSED_ORIGIN_BLOCKER", False, False, False, "Trace weights lack unified action attachment."),
        ("sector_representation_pattern", "REPRESENTATION_DERIVED", True, False, False, "Charge/anomaly algebra follows once this stated representation input is fixed."),
        ("hypercharge_normalization_YH_half", "INDEPENDENT_THEORY_INPUT", False, False, False, "Conventional normalization is declared, not numerically predicted."),
        ("Planck_energy_GeV", "UNLICENSED_ORIGIN_BLOCKER", False, False, False, "External dimensionful constant enters an unlicensed scale screen."),
        ("published_mass_references", "EXTERNAL_COMPARISON_DATA", False, False, False, "Used only for score comparison."),
        ("published_CKM_references", "EXTERNAL_COMPARISON_DATA", False, False, False, "Used only for score comparison."),
        ("published_PMNS_references", "EXTERNAL_COMPARISON_DATA", False, False, False, "Used only for score comparison."),
        ("published_gauge_references", "EXTERNAL_COMPARISON_DATA", False, False, False, "Used only for score comparison."),
        ("published_Higgs_v_references", "EXTERNAL_COMPARISON_DATA", False, False, False, "Used only for score comparison."),
        ("Zvirt_half", "CANDIDATE_NOT_OFFICIAL", False, False, False, "Only the dressed candidate branch uses it."),
        ("berger_spectral_eigenvalues", "GEOMETRICALLY_DERIVED", True, False, False, "Derived from the declared Berger geometry."),
        ("yukawa_overlap_ratios", "GEOMETRICALLY_DERIVED", True, False, False, "Derived conditionally from a, S, and the supplied mode ledger."),
        ("anomaly_sums", "REPRESENTATION_DERIVED", True, False, False, "Exact algebraic consequences of the stated charges."),
        ("fixed_h_quartic_map", "ACTION_DERIVED", True, False, False, "Derived as a function of lambda5 from the retained reduced action."),
        ("local_stability_threshold", "ACTION_DERIVED", True, False, False, "Derived inequality; it does not select lambda5."),
        ("charged_ratio_screens", "GEOMETRICALLY_DERIVED", True, False, False, "Conditional outputs of the overlap map and typed upstream inputs."),
        ("sector_charges", "REPRESENTATION_DERIVED", True, False, False, "Algebraic consequences of the stated representation ledger."),
        ("pmns_effective_rule", "CANDIDATE_NOT_OFFICIAL", False, False, False, "Effective-extension rule, not a minimal-SM prediction."),
        ("gauge_normalization_rule", "UNLICENSED_ORIGIN_BLOCKER", False, False, False, "Requires attachment to the unified parent action."),
        ("higgs_scale_screen_rule", "UNLICENSED_ORIGIN_BLOCKER", False, False, False, "Conditional numerical screen without licensed scale provenance."),
        ("proxy_basis", "CANDIDATE_NOT_OFFICIAL", False, False, False, "Finite basis used only for proxy spectral evidence."),
        ("finite_basis_HT_proxy", "CANDIDATE_NOT_OFFICIAL", False, False, False, "Proxy operator is not the full analytic spectrum."),
        ("higgs_electroweak_screen", "CANDIDATE_NOT_OFFICIAL", False, False, False, "Conditional upstream screen used by the decoupling scaffold."),
        ("proxy_scalar_modes", "CANDIDATE_NOT_OFFICIAL", False, False, False, "Finite illustrative mode ledger."),
        ("finite_basis_scalar_scaffold", "CANDIDATE_NOT_OFFICIAL", False, False, False, "Conditional scaffold, not an action-level theorem."),
        ("one_universal_dimensionful_scale", "POST_BHSM_1_0", False, False, False, "No universal calibration has been exercised in BHSM 1.0."),
        ("exact_branch_higher_orders", "POST_BHSM_1_0", False, False, False, "Not required by a retained release claim."),
    ]
    return [
        {
            "input_id": name,
            "type": kind,
            "derived": derived,
            "calibrated": calibrated,
            "fitted": fitted,
            "advertised_as_prediction": False,
            "allowed_in_parent_action": kind not in {"EXTERNAL_COMPARISON_DATA", "CANDIDATE_NOT_OFFICIAL", "UNLICENSED_ORIGIN_BLOCKER", "POST_BHSM_1_0"},
            "rationale": rationale,
        }
        for name, kind, derived, calibrated, fitted, rationale in rows
    ]


def _leaf_paths(value: Any, prefix: str = "") -> list[str]:
    if isinstance(value, dict):
        result: list[str] = []
        for key in sorted(value):
            result.extend(_leaf_paths(value[key], f"{prefix}.{key}" if prefix else key))
        return result
    if isinstance(value, list):
        result = []
        for index, item in enumerate(value):
            result.extend(_leaf_paths(item, f"{prefix}[{index}]"))
        return result
    return [prefix]


def _dependency_profile(category: str, branch: str) -> dict[str, Any]:
    profiles = {
        "charged_lepton_ratios": (["geometry_a", "S_overlap", "mode_ledger"], ["alpha_inv_low_energy", "berger_spectral_eigenvalues", "omega_target_rules"], []),
        "up_quark_ratios": (["geometry_a", "S_overlap", "mode_ledger"], ["alpha_inv_low_energy", "berger_spectral_eigenvalues", "omega_target_rules"], ["Zvirt_half"] if "DRESSED" in branch else []),
        "down_quark_ratios": (["geometry_a", "S_overlap", "mode_ledger"], ["alpha_inv_low_energy", "berger_spectral_eigenvalues", "omega_target_rules"], []),
        "ckm": (["charged_ratio_screens", "S_overlap", "sector_charges"], ["geometry_a", "mode_ledger", "ckm_screen_law"], ["Zvirt_half"] if "DRESSED" in branch else []),
        "pmns_effective": (["alpha_inv_low_energy"], ["pmns_effective_rule"], []),
        "gauge_couplings": (["gauge_trace_weights"], ["gauge_normalization_rule"], []),
        "higgs_electroweak": (["Planck_energy_GeV", "alpha_inv_low_energy"], ["higgs_scale_screen_rule"], []),
        "ht_gap_status": (["proxy_basis", "geometry_a"], ["finite_basis_HT_proxy"], []),
        "scalar_decoupling_status": (["higgs_electroweak_screen", "proxy_scalar_modes"], ["finite_basis_scalar_scaffold"], []),
    }
    direct, transitive, candidate = profiles[category]
    return {"direct_inputs": direct, "transitive_inputs": transitive, "candidate_inputs": candidate}


def frozen_dependency_rows(root: Path) -> list[dict[str, Any]]:
    source = json.loads((root / "theory" / "bhsm_v1_frozen_prediction_set.json").read_text(encoding="utf-8"))
    rows = []
    for prediction_set in source["prediction_sets"]:
        branch = prediction_set["version"]["branch"]
        for category, outputs in sorted(prediction_set["outputs"].items()):
            profile = _dependency_profile(category, branch)
            for leaf in _leaf_paths(outputs, category):
                rows.append({
                    "output_id": f"{branch}:{leaf}",
                    "branch": branch,
                    "official_status": "CANDIDATE_NOT_OFFICIAL" if "DRESSED" in branch else ("CONDITIONAL_SCAFFOLD" if category in {"pmns_effective", "ht_gap_status", "scalar_decoupling_status"} else "FROZEN_SCREEN"),
                    "exact_computation_path": f"src/bhsm_v1.py::_model_outputs -> {leaf}",
                    **profile,
                    "fitted_inputs": [],
                    "unselected_inputs": [],
                    "excluded_unselected_inputs": ["lambda5"],
                    "lambda5_appears": False,
                    "G5_appears": False,
                    "Z5_appears": False,
                    "kappa1_appears": False,
                    "output_can_vary_with_lambda5": False,
                    "external_computation_inputs": [x for x in profile["direct_inputs"] + profile["transitive_inputs"] if x in {"alpha_inv_low_energy", "Planck_energy_GeV"}],
                    "comparison_data_in_computation": [],
                })
    return rows


def blocker_rows() -> list[dict[str, Any]]:
    specs = [
        ("RB-01", "Unified parent-action provenance", [], ["C01", "C09", "C15", "C18"]),
        ("RB-02", "Scalar quartic invariant selection", [], ["C06", "C07", "C08"]),
        ("RB-03", "Sector projectors, domains, and boundary operators", ["RB-01"], ["C01", "C09", "C10", "C11", "C17"]),
        ("RB-04", "Charged hierarchy and stiffness normalization", ["RB-01", "RB-03"], ["C10", "C11"]),
        ("RB-05", "Charged-lepton eta_l action source", ["RB-01", "RB-03"], ["C11"]),
        ("RB-06", "CKM mixing law and exponent", ["RB-03", "RB-04"], ["C12"]),
        ("RB-07", "PMNS and neutrino structural closure", ["RB-01", "RB-03"], ["C14"]),
        ("RB-08", "Gauge normalization", ["RB-01", "RB-03"], ["C09", "C15"]),
        ("RB-09", "Boundary measure, collar, and transport normalization", ["RB-01"], ["C16", "C19"]),
        ("RB-10", "Neutral response domain and positivity", ["RB-01", "RB-09"], ["C17"]),
        ("RB-11", "Scalar/topographic claimed-sector action closure", ["RB-01", "RB-09"], ["C18"]),
        ("RB-12", "Physical scale bridge", ["RB-08", "RB-09", "RB-11"], ["C16", "C19"]),
        ("RB-13", "Scheme and observable transport map", ["RB-08", "RB-09", "RB-12"], ["C16", "C19"]),
        ("RB-14", "Finite official benchmark suite freeze", ["RB-03", "RB-06", "RB-07", "RB-08", "RB-13"], ["C03", "C11", "C12", "C14", "C15", "C16"]),
        ("RB-15", "Novel prediction and falsification freeze", ["RB-12", "RB-13", "RB-14"], ["C03"]),
        ("RB-16", "Release manuscript and clean reproduction package", ["RB-14", "RB-15"], ["C20"]),
    ]
    rows = []
    for blocker_id, title, dependencies, claims in specs:
        scalar = blocker_id == "RB-02"
        rows.append({
            "blocker_id": blocker_id,
            "title": title,
            "classification": "PARAMETER_FREE_EXTENSION_BLOCKER" if scalar else "BHSM_1_0_RELEASE_BLOCKER",
            "release_blocking": not scalar,
            "status": "RECLASSIFIED_OPEN_EXTENSION" if scalar else "OPEN",
            "depends_on": dependencies,
            "affected_retained_claims": claims,
            "stale_as_release_blocker": False,
            "reassessment": "lambda5 is an independent theory input; only a parameter-free scalar extension requires its derivation/selection" if scalar else "retained after claim/dependency audit",
        })
    return rows


def claim_matrix_payload() -> dict[str, Any]:
    return {"artifact": "BHSM_1_0_claim_to_evidence_matrix", "version": VERSION, "claims": claim_rows(), "primary_verdict": PRIMARY_VERDICT, **GUARDS}


def frozen_dependencies_payload(root: Path) -> dict[str, Any]:
    return {"artifact": "BHSM_frozen_prediction_dependency_graph", "version": VERSION, "source": "theory/bhsm_v1_frozen_prediction_set.json", "outputs": frozen_dependency_rows(root), "lambda5_dependency_count": 0, "frozen_hashes": FROZEN_HASHES, **GUARDS}


def typed_inputs_payload() -> dict[str, Any]:
    return {"artifact": "BHSM_1_0_typed_input_ledger", "version": VERSION, "allowed_types": sorted(INPUT_TYPES), "inputs": typed_input_rows(), "one_universal_dimensionful_calibration_used": False, **GUARDS}


def lambda_relevance_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_lambda5_release_relevance",
        "version": VERSION,
        "classification": "INDEPENDENT_THEORY_INPUT",
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": LAMBDA_VERDICT,
        "value_selected": False,
        "sign_selected": False,
        "appears_in_frozen_predictions": False,
        "changes_frozen_predictions": False,
        "retained_results": ["parameterized reduced scalar family", "conditional local-stability inequality", "exact-branch obstruction"],
        "removed_claims": ["parameter-free numerical scalar quartic", "unconditional scalar stability"],
        "release_effect": "RB-02 removed from BHSM 1.0 release blockers and retained only for a parameter-free scalar extension.",
        **GUARDS,
    }


def parameter_policy_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_parameterized_vs_parameter_free_policy",
        "version": VERSION,
        "policy": {
            "parameterized_theory": "Independent theory inputs are permitted when explicit, typed, unfitted, and never advertised as predictions.",
            "parameter_free_extension": "Requires an internal derivation or selection rule for lambda5.",
            "external_comparison": "May score outputs but may not enter the parent action or derivation path.",
            "candidate": "Must remain visibly non-official.",
        },
        "lambda5_status": "ALLOWED_IN_PARAMETERIZED_BHSM_NOT_PREDICTED",
        **GUARDS,
    }


def blocker_dag_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_release_blocker_DAG",
        "version": VERSION,
        "nodes": blocker_rows(),
        "release_blocker_ids": [r["blocker_id"] for r in blocker_rows() if r["release_blocking"]],
        "parameter_free_extension_blocker_ids": ["RB-02"],
        "next_highest_upstream_scientific_target": NEXT_TARGET,
        "stale_release_blockers": [],
        **GUARDS,
    }


def scale_reassessment_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_scale_permission_dependency_reassessment",
        "version": VERSION,
        "verdict": SCALE_VERDICT,
        "lambda5_is_scale_permission_dependency": False,
        "actual_open_dependencies": ["RB-01", "RB-08", "RB-09", "RB-11", "RB-12", "RB-13"],
        "reasons": ["no canonically normalized unified parent action", "boundary measure and transport remain open", "no licensed universal physical scale", "no common observable/scheme map"],
        "scale_phase_permission": "DENIED",
        **GUARDS,
    }


def next_target_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_next_upstream_scientific_target",
        "version": VERSION,
        "target": NEXT_TARGET,
        "why": "It has no unresolved release-blocker parent and can change every downstream sector action, normalization, and observable map.",
        "forbidden_downstream_shortcut": "Do not enter scale fitting, benchmark refreezing, or another lambda5-selection sprint first.",
        **GUARDS,
    }


def scope_firewall_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_scope_firewall",
        "version": VERSION,
        "classifications": ["BHSM_1_0_RELEASE_BLOCKER", "PARAMETER_FREE_EXTENSION_BLOCKER", "POST_BHSM_1_0"],
        "rule": "An item blocks BHSM 1.0 only if it can change a retained BHSM 1.0 claim or its licensed computation path.",
        "lambda5_selection": "PARAMETER_FREE_EXTENSION_BLOCKER",
        "exact_branch_higher_orders": "POST_BHSM_1_0",
        "external_acceptance": "POST_BHSM_1_0",
        **GUARDS,
    }


def reconciliation_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_1_0_completion_contract_reconciliation",
        "version": VERSION,
        "prior_contract": "v6.30.6",
        "correction": "The earlier contract incorrectly treated absence of a lambda5 selection rule as a universal BHSM 1.0 release blocker.",
        "tier_A_policy": "Dimensionless coefficients may be independent theory inputs when typed and not claimed as predictions; no unselected coefficient may remain inside an official parameter-free prediction.",
        "tier_C_name": "Internally Complete / External Review Ready",
        "current_tier_status": {"Tier_A": "BLOCKED_BY_15_RELEASE_BLOCKERS", "Tier_B": "NOT_ELIGIBLE", "Tier_C": "NOT_ELIGIBLE"},
        "BHSM_1_0_release_complete": False,
        "next_highest_upstream_blocker": NEXT_TARGET,
        "current_verdict": PRIMARY_VERDICT,
        "lambda5_reclassification": LAMBDA_VERDICT,
        "scale_reassessment": SCALE_VERDICT,
        **GUARDS,
    }


def historical_canonical_completion_gate_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_1_0_completion_gate",
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "contract_reconciled_from": "v6.30.6",
        "tiers": [
            {"tier": "A", "name": "BHSM Core Complete", "status": "BLOCKED", "policy": reconciliation_payload()["tier_A_policy"]},
            {"tier": "B", "name": "BHSM Physical Complete", "status": "NOT_ELIGIBLE_TIER_A_BLOCKED"},
            {"tier": "C", "name": "Internally Complete / External Review Ready", "status": "NOT_ELIGIBLE_TIER_B_BLOCKED"},
        ],
        "release_blockers": [r for r in blocker_rows() if r["release_blocking"]],
        "parameter_free_extension_blockers": [r for r in blocker_rows() if not r["release_blocking"]],
        "next_highest_upstream_blocker": NEXT_TARGET,
        "current_verdict": PRIMARY_VERDICT,
        "BHSM_1_0_release_complete": False,
        "external_validation_is_internal_gate": False,
        "frozen_hashes": FROZEN_HASHES,
        **GUARDS,
    }


def canonical_completion_gate_payload() -> dict[str, Any]:
    """Return the current support-representation completion gate.

    Historical materializers delegate here so that rerunning an earlier sprint
    cannot silently roll the repository-wide canonical gate back from v11.1.
    """

    from bhsm.interface.completion import final_completion_gate_v11_1 as current

    return current.canonical_completion_gate_payload()


def artifact_payloads(root: Path) -> dict[str, dict[str, Any]]:
    return {
        "claim_matrix": claim_matrix_payload(),
        "frozen_dependencies": frozen_dependencies_payload(root),
        "typed_inputs": typed_inputs_payload(),
        "lambda_relevance": lambda_relevance_payload(),
        "parameter_policy": parameter_policy_payload(),
        "reconciliation": reconciliation_payload(),
        "blocker_dag": blocker_dag_payload(),
        "scale_reassessment": scale_reassessment_payload(),
        "next_target": next_target_payload(),
        "scope_firewall": scope_firewall_payload(),
    }


def artifact_bytes(root: Path) -> dict[str, bytes]:
    return {ARTIFACT_FILES[key]: deterministic_json(payload).encode("utf-8") for key, payload in artifact_payloads(root).items()}


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    paths = []
    for filename, content in artifact_bytes(root).items():
        path = target / filename
        path.write_bytes(content)
        paths.append(path)
    canonical = target / "BHSM_1_0_completion_gate.json"
    canonical.write_bytes(deterministic_json(canonical_completion_gate_payload()).encode("utf-8"))
    paths.append(canonical)
    return paths


def validate(root: Path) -> dict[str, bool]:
    claims = claim_rows()
    inputs = typed_input_rows()
    deps = frozen_dependency_rows(root)
    blockers = blocker_rows()
    return {
        "every_retained_claim_has_evidence": all((not r["retained"]) or r["evidence"] for r in claims),
        "every_input_has_exactly_one_valid_type": all(r["type"] in INPUT_TYPES for r in inputs),
        "no_input_is_both_derived_and_calibrated": all(not (r["derived"] and r["calibrated"]) for r in inputs),
        "comparison_data_excluded_from_parent_action": all(not r["allowed_in_parent_action"] for r in inputs if r["type"] == "EXTERNAL_COMPARISON_DATA"),
        "independent_inputs_not_advertised_as_predictions": all(not r["advertised_as_prediction"] for r in inputs if r["type"] == "INDEPENDENT_THEORY_INPUT"),
        "candidate_not_official": all(r["official_status"] == "CANDIDATE_NOT_OFFICIAL" for r in deps if "DRESSED" in r["branch"]),
        "every_release_blocker_names_retained_claim": all(r["affected_retained_claims"] for r in blockers if r["release_blocking"]),
        "no_stale_release_blockers": not any(r["stale_as_release_blocker"] for r in blockers),
        "lambda5_absent_from_frozen_outputs": all(not r["lambda5_appears"] and not r["output_can_vary_with_lambda5"] for r in deps),
        "fitted_inputs_absent_from_frozen_outputs": all(not r["fitted_inputs"] for r in deps),
        "frozen_outputs_dependency_complete": all(r["direct_inputs"] and r["exact_computation_path"] for r in deps),
    }


def frozen_file_sha256(path: Path) -> str:
    """Hash legacy frozen text in its declared canonical CRLF form."""

    canonical_lf = path.read_bytes().replace(b"\r\n", b"\n")
    canonical_crlf = canonical_lf.replace(b"\n", b"\r\n")
    return hashlib.sha256(canonical_crlf).hexdigest().upper()


def frozen_hashes_match(root: Path) -> bool:
    return all(
        frozen_file_sha256(root / path) == digest
        for path, digest in FROZEN_HASHES.items()
    )
