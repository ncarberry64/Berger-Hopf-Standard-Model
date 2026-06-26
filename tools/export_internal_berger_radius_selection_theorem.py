from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import internal_berger_radius_selection_theorem as theorem


ORIGINAL_PR46_MISSING_OBJECTS = ["kappa_H", "Z_H", "r"]
POST_RADIUS_MISSING_OBJECTS = ["Z_H", "kappa_H"]


def write_json(path: Path, payload: dict | list) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _append_claim_row(claims: dict, row: dict) -> None:
    for entry in claims["claim_statuses"]:
        if entry["claim"] == row["claim"]:
            entry.update(row)
            return
    claims["claim_statuses"].append(row)


def _unique_extend(items: list, additions: list[str]) -> list:
    result = list(items)
    for item in additions:
        if item not in result:
            result.append(item)
    return result


def update_profile_scale(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    update = payload["profile_scale_tau_sigma_update"]
    update["r_internal_profile_status"] = theorem.RADIUS_STATUS
    update["r_internal_profile"] = artifact["r_internal_profile_value"]
    update["r_internal_profile_squared"] = artifact["r_internal_profile_squared"]
    update["missing_objects"] = POST_RADIUS_MISSING_OBJECTS
    update["tau_formula_after_radius_substitution"] = artifact["tau_sigma_obstruction_chain"][
        "tau_symbolic_after_radius_substitution"
    ]
    update["sigma_derived"] = False
    update["tau_derived"] = False
    update["charged_outputs_at_tau_exported"] = False
    payload["boundary_profile_scale_closure"] = "BLOCKED_BY_MISSING_OBJECTS"
    payload["missing_objects"] = POST_RADIUS_MISSING_OBJECTS
    payload["charged_outputs_at_tau_exported"] = False
    payload["radius_selected_by"] = theorem.AUTHOR_SELECTION
    payload["official_predictions_changed"] = False
    payload["empirical_derivation_inputs_used"] = False
    write_json(path, payload)


def update_boundary_profile(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    payload["targeted_followup_from_author_radius_selection"] = {
        "source_artifact": "artifacts/internal_berger_radius_selection_theorem_v1.json",
        "r_internal_profile_status": theorem.RADIUS_STATUS,
        "radius_normalization_fork": theorem.FORK_STATUS,
        "remaining_blockers": POST_RADIUS_MISSING_OBJECTS,
    }
    payload["r"]["status"] = theorem.RADIUS_STATUS
    payload["r"]["value"] = artifact["r_internal_profile_value"]
    payload["r"]["formula"] = "r_internal_profile = 1/sqrt(4*pi)"
    payload["boundary_profile_scale_closure"] = "BLOCKED_BY_MISSING_OBJECTS"
    payload["missing_objects"] = ORIGINAL_PR46_MISSING_OBJECTS
    payload["refined_missing_objects_after_radius_selection"] = POST_RADIUS_MISSING_OBJECTS
    payload["charged_outputs_at_tau_exported"] = False
    payload["radius_selected_by"] = theorem.AUTHOR_SELECTION
    payload["official_predictions_changed"] = False
    payload["empirical_derivation_inputs_used"] = False
    write_json(path, payload)


def update_radius_fork_artifacts(paths: list[Path], artifact: dict) -> None:
    for path in paths:
        payload = load_json(path)
        payload["targeted_followup_from_author_radius_selection"] = {
            "source_artifact": "artifacts/internal_berger_radius_selection_theorem_v1.json",
            "r_internal_profile_status": theorem.RADIUS_STATUS,
            "radius_normalization_fork": theorem.FORK_STATUS,
            "selected_route": artifact["selected_route"],
        }
        payload["r_internal_profile_status"] = theorem.RADIUS_STATUS
        payload["r_internal_profile_value"] = artifact["r_internal_profile_value"]
        payload["selected_route"] = artifact["selected_route"]
        payload["radius_normalization_fork"] = theorem.FORK_STATUS
        payload["radius_selected_by"] = theorem.AUTHOR_SELECTION
        payload["official_predictions_changed"] = False
        payload["empirical_derivation_inputs_used"] = False
        write_json(path, payload)


def update_tau_sigma(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    payload["targeted_followup_from_author_radius_selection"] = {
        "source_artifact": "artifacts/profile_scale_tau_sigma_update_v1.json",
        "r_internal_profile_status": theorem.RADIUS_STATUS,
        "remaining_blockers": POST_RADIUS_MISSING_OBJECTS,
        "tau_symbolic_after_radius_substitution": artifact["tau_sigma_obstruction_chain"][
            "tau_symbolic_after_radius_substitution"
        ],
    }
    payload["missing_objects"] = ORIGINAL_PR46_MISSING_OBJECTS
    payload["refined_missing_objects_after_radius_selection"] = POST_RADIUS_MISSING_OBJECTS
    payload["status"] = "OPEN_LOCALIZABLE"
    payload["official_predictions_changed"] = False
    payload["empirical_derivation_inputs_used"] = False
    payload["radius_selected_by"] = theorem.AUTHOR_SELECTION
    write_json(path, payload)


def update_numerical_gate(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    tau = payload["gates"]["tau_sigma"]
    tau["targeted_followup_from_author_radius_selection"] = {
        "source_artifact": "artifacts/internal_berger_radius_selection_theorem_v1.json",
        "r_internal_profile_status": theorem.RADIUS_STATUS,
        "remaining_blockers": POST_RADIUS_MISSING_OBJECTS,
        "tau_symbolic_after_radius_substitution": artifact["tau_sigma_obstruction_chain"][
            "tau_symbolic_after_radius_substitution"
        ],
    }
    tau["missing_objects"] = ORIGINAL_PR46_MISSING_OBJECTS
    tau["refined_missing_objects_after_radius_selection"] = POST_RADIUS_MISSING_OBJECTS
    payload["gates"]["charged_outputs_at_tau"]["missing_objects"] = ORIGINAL_PR46_MISSING_OBJECTS
    payload["gates"]["charged_outputs_at_tau"]["refined_missing_objects_after_radius_selection"] = (
        POST_RADIUS_MISSING_OBJECTS
    )
    payload["promoted_statuses"] = [
        {
            "gate": "internal_berger_radius_selection_theorem",
            "status": theorem.THEOREM_STATUS,
        },
        {
            "gate": "r_internal_profile",
            "status": theorem.RADIUS_STATUS,
        },
    ]
    payload["public_status_after_sprint"] = theorem.PUBLIC_STATUS
    payload["official_predictions_changed"] = False
    payload["empirical_derivation_inputs_used"] = False
    write_json(path, payload)


def update_prediction_package(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    payload["sections"]["charged_same_sector_ratios"]["open_blockers"] = ORIGINAL_PR46_MISSING_OBJECTS
    payload["sections"]["charged_same_sector_ratios"]["refined_open_blockers_after_radius_selection"] = (
        POST_RADIUS_MISSING_OBJECTS
    )
    payload["sections"]["open_boundary_parameters"].update(
        {
            "status": "BLOCKED_BY_MISSING_OBJECTS",
            "source_artifact": "artifacts/profile_scale_tau_sigma_update_v1.json",
            "source_artifact_from_author_radius_selection": (
                "artifacts/internal_berger_radius_selection_theorem_v1.json"
            ),
            "uses_empirical_input": False,
            "comparison_ready": False,
            "open_blockers": ORIGINAL_PR46_MISSING_OBJECTS,
            "refined_open_blockers_after_radius_selection": POST_RADIUS_MISSING_OBJECTS,
        }
    )
    payload["official_predictions_changed"] = False
    payload["empirical_derivation_inputs_used"] = False
    write_json(path, payload)


def update_open_gate_ledger(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    payload["statuses"].update(
        {
            "internal_berger_radius_selection_theorem": theorem.THEOREM_STATUS,
            "internal_profile_radius_normalization": theorem.RADIUS_STATUS,
            "berger_radius_measure_normalization": theorem.RADIUS_STATUS,
            "radius_normalization_fork": theorem.FORK_STATUS,
            "boundary_profile_scale_closure": "BLOCKED_BY_MISSING_OBJECTS",
            "sigma_from_boundary_geometry": "OPEN_LOCALIZABLE",
            "tau_from_boundary_geometry": "OPEN_LOCALIZABLE",
            "charged_no_fit_outputs": "BLOCKED_BY_TAU_SIGMA_BOUNDARY_DERIVATION",
            "official_predictions": "UNCHANGED",
            "empirical_derivation_inputs_used": False,
        }
    )
    payload["remaining_open_blockers"] = _unique_extend(payload["remaining_open_blockers"], POST_RADIUS_MISSING_OBJECTS)
    payload["official_predictions_changed"] = False
    write_json(path, payload)


def update_claim_status(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    _append_claim_row(
        payload,
        {
            "claim": "Author-supplied internal Berger radius selection theorem",
            "status": theorem.THEOREM_STATUS,
            "boundary": "Author BHSM axiom identifies r_internal_profile^2 = Lambda_squared = S = 1/(4*pi); this closes only the radius gate.",
        },
    )
    _append_claim_row(
        payload,
        {
            "claim": "Internal profile radius value",
            "status": theorem.RADIUS_STATUS,
            "boundary": "r_internal_profile = 1/sqrt(4*pi); tau remains blocked by Z_H and kappa_H.",
        },
    )
    _append_claim_row(
        payload,
        {
            "claim": "Internal radius normalization fork",
            "status": theorem.FORK_STATUS,
            "boundary": "Lambda-radius and overlap-radius are selected as semantically equivalent under the author normalization.",
        },
    )
    payload["official_predictions_changed"] = False
    write_json(path, payload)


def update_current_status(path: Path, artifact: dict) -> None:
    text = path.read_text(encoding="utf-8")
    marker = "## Author-Supplied Internal Berger Radius Selection"
    section = f"""
{marker}

The radius fork from PR #49 is resolved by the author-supplied BHSM overlap
normalization:

`r_internal_profile^2 = Lambda_squared = S = 1/(4*pi)`.

Therefore `r_internal_profile = 1/sqrt(4*pi)` and the local radius gate is
`{theorem.RADIUS_STATUS}` with theorem status `{theorem.THEOREM_STATUS}`.
The Lambda-radius and overlap-radius routes are selected as the same semantic
BHSM overlap-scale normalization, not merely as numerically equal constants.

The global public status remains `{theorem.PUBLIC_STATUS}`. `Z_H` and `kappa_H`
remain open, so `sigma` and `tau` are not numerically computed. With the radius
substituted, the symbolic dependency is
`tau(Z_H,kappa_H) = 2*pi*sqrt(Z_H/kappa_H)`. No charged outputs at boundary tau
are exported, and official/frozen predictions remain unchanged.
"""
    if marker in text:
        text = text.split(marker, 1)[0].rstrip() + "\n\n" + section.strip() + "\n"
    else:
        text = text.rstrip() + "\n\n" + section.strip() + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    artifacts = ROOT / "artifacts"
    artifact = theorem.build_author_radius_selection_artifact(ROOT)
    write_json(artifacts / "internal_berger_radius_selection_theorem_v1.json", artifact)
    write_json(
        artifacts / "internal_profile_radius_value_v1.json",
        {
            **theorem._guardrails(),
            "artifact": "internal_profile_radius_value_v1",
            "r_internal_profile_status": theorem.RADIUS_STATUS,
            "r_internal_profile_squared_formula": "S = Lambda_squared = 1/(4*pi)",
            "r_internal_profile_squared": artifact["r_internal_profile_squared"],
            "r_internal_profile_formula": "1/sqrt(4*pi)",
            "r_internal_profile": artifact["r_internal_profile_value"],
            "radius_selected_by": theorem.AUTHOR_SELECTION,
        },
    )
    write_json(
        artifacts / "internal_radius_route_consistency_matrix_v1.json",
        {
            **theorem._guardrails(),
            "artifact": "internal_radius_route_consistency_matrix_v1",
            "route_verdicts": artifact["route_verdicts"],
        },
    )
    write_json(
        artifacts / "internal_radius_equivalence_classes_v1.json",
        {
            **theorem._guardrails(),
            "artifact": "internal_radius_equivalence_classes_v1",
            "equivalence_classes": [
                {
                    "class_id": "author_overlap_scale_radius",
                    "members": ["Lambda radius", "overlap radius"],
                    "status": theorem.SELECTED_BY_AUTHOR_AXIOM,
                    "semantic_equivalence": artifact["lambda_overlap_equivalence"]["semantic_equivalence"],
                },
                {
                    "class_id": "nonprimary_geometry_routes",
                    "members": ["Berger volume normalization", "collar-depth matching"],
                    "status": theorem.NOT_PRIMARY_ROUTE,
                },
                {
                    "class_id": "rejected_unit_radius",
                    "members": ["unit internal radius"],
                    "status": theorem.REJECTED_BY_AUTHOR_NORMALIZATION,
                },
            ],
        },
    )

    update_profile_scale(artifacts / "profile_scale_tau_sigma_update_v1.json", artifact)
    update_boundary_profile(artifacts / "boundary_profile_scale_closure_v1.json", artifact)
    update_radius_fork_artifacts(
        [
            artifacts / "berger_radius_measure_normalization_v1.json",
            artifacts / "internal_profile_radius_closure_or_obstruction_v2.json",
            artifacts / "internal_radius_normalization_forks_v1.json",
            artifacts / "berger_measure_domain_v1.json",
            artifacts / "internal_profile_radius_normalization_v1.json",
        ],
        artifact,
    )
    update_tau_sigma(artifacts / "tau_sigma_boundary_derivation_closure_or_obstruction_v1.json", artifact)
    update_numerical_gate(artifacts / "BHSM_numerical_gate_closure_assault_v1.json", artifact)
    update_prediction_package(artifacts / "BHSM_prediction_package_skeleton_v1.json", artifact)
    update_open_gate_ledger(artifacts / "full_BHSM_open_gate_ledger_v2.json", artifact)
    update_claim_status(artifacts / "full_BHSM_claim_status_table_v2.json", artifact)
    update_current_status(ROOT / "docs" / "current_status.md", artifact)


if __name__ == "__main__":
    main()
