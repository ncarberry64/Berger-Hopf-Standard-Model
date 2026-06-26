from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import berger_radius_measure_normalization as radius


ORIGINAL_PR46_MISSING_OBJECTS = ["kappa_H", "Z_H", "r"]
PR48_REFINED_MISSING_OBJECTS = ["r_internal_profile", "Z_H", "kappa_H"]


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


def update_radius_symbol_disambiguation(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    payload["targeted_followup_from_PR48"] = {
        "source_artifact": "artifacts/berger_radius_measure_normalization_v1.json",
        "r_internal_profile_status": artifact["r_internal_profile_status"],
        "missing_theorem": artifact["missing_theorem"],
    }
    payload["radius_measure_symbols_from_PR48_followup"] = artifact["radius_symbols"]
    payload["r_status"] = artifact["r_internal_profile_status"]
    payload["official_predictions_changed"] = False
    payload["empirical_derivation_inputs_used"] = False
    write_json(path, payload)


def update_internal_profile_artifact(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    payload["targeted_followup_from_PR48"] = {
        "source_artifact": "artifacts/berger_radius_measure_normalization_v1.json",
        "r_internal_profile_status": artifact["r_internal_profile_status"],
        "selected_route": artifact["selected_route"],
        "missing_theorem": artifact["missing_theorem"],
        "dmu_Berger_domain_status": artifact["dmu_Berger_domain_status"],
    }
    payload["r_internal_profile"]["status"] = artifact["r_internal_profile_status"]
    payload["r_internal_profile"]["missing_theorem"] = artifact["missing_theorem"]
    payload["r_internal_profile"]["normalization_fork_status"] = artifact["r_internal_profile_status"]
    payload["r_internal_profile"]["value"] = artifact["r_internal_profile_value"]
    payload["radius_normalization_forks_from_PR48_followup"] = artifact["radius_normalization_forks"]
    payload["profile_scale_tau_sigma_update"]["missing_objects"] = PR48_REFINED_MISSING_OBJECTS
    payload["missing_objects"] = PR48_REFINED_MISSING_OBJECTS
    payload["official_predictions_changed"] = False
    payload["empirical_derivation_inputs_used"] = False
    write_json(path, payload)


def update_boundary_profile_artifact(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    payload["targeted_followup_from_PR48"] = {
        "source_artifact": "artifacts/berger_radius_measure_normalization_v1.json",
        "r_internal_profile_status": artifact["r_internal_profile_status"],
        "missing_theorem": artifact["missing_theorem"],
        "selected_route": artifact["selected_route"],
    }
    payload["boundary_profile_scale_closure"] = "BLOCKED_BY_MISSING_OBJECTS"
    payload["sigma_from_boundary_geometry"] = "OPEN_LOCALIZABLE"
    payload["tau_from_boundary_geometry"] = "OPEN_LOCALIZABLE"
    payload["missing_objects"] = ORIGINAL_PR46_MISSING_OBJECTS
    payload["refined_missing_objects_from_PR48_followup"] = PR48_REFINED_MISSING_OBJECTS
    payload["charged_outputs_at_tau_exported"] = False
    payload["official_predictions_changed"] = False
    payload["empirical_derivation_inputs_used"] = False
    write_json(path, payload)


def update_profile_scale_artifact(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    payload["targeted_followup_from_PR48"] = {
        "source_artifact": "artifacts/internal_profile_radius_closure_or_obstruction_v2.json",
        "r_internal_profile_status": artifact["r_internal_profile_status"],
        "missing_theorem": artifact["missing_theorem"],
    }
    update = payload["profile_scale_tau_sigma_update"]
    update["missing_objects"] = PR48_REFINED_MISSING_OBJECTS
    update["boundary_profile_scale_closure"] = "BLOCKED_BY_MISSING_OBJECTS"
    update["sigma_from_boundary_geometry"] = "OPEN_LOCALIZABLE"
    update["tau_from_boundary_geometry"] = "OPEN_LOCALIZABLE"
    update["sigma_derived"] = False
    update["tau_derived"] = False
    update["charged_outputs_at_tau_exported"] = False
    payload["missing_objects"] = PR48_REFINED_MISSING_OBJECTS
    payload["charged_outputs_at_tau_exported"] = False
    payload["official_predictions_changed"] = False
    payload["empirical_derivation_inputs_used"] = False
    write_json(path, payload)


def update_tau_sigma_artifact(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    payload["targeted_followup_from_PR48"] = {
        "source_artifact": "artifacts/internal_profile_radius_closure_or_obstruction_v2.json",
        "r_internal_profile_status": artifact["r_internal_profile_status"],
        "missing_theorem": artifact["missing_theorem"],
    }
    payload["missing_objects"] = ORIGINAL_PR46_MISSING_OBJECTS
    payload["refined_missing_objects_from_PR48_followup"] = PR48_REFINED_MISSING_OBJECTS
    payload["status"] = "OPEN_LOCALIZABLE"
    payload["official_predictions_changed"] = False
    payload["empirical_derivation_inputs_used"] = False
    write_json(path, payload)


def update_numerical_gate_report(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    tau = payload["gates"]["tau_sigma"]
    tau["targeted_followup_from_PR48"] = {
        "source_artifact": "artifacts/berger_radius_measure_normalization_v1.json",
        "r_internal_profile_status": artifact["r_internal_profile_status"],
        "missing_theorem": artifact["missing_theorem"],
    }
    tau["missing_objects"] = ORIGINAL_PR46_MISSING_OBJECTS
    tau["refined_missing_objects_from_PR48_followup"] = PR48_REFINED_MISSING_OBJECTS
    payload["gates"]["charged_outputs_at_tau"]["missing_objects"] = ORIGINAL_PR46_MISSING_OBJECTS
    payload["gates"]["charged_outputs_at_tau"]["refined_missing_objects_from_PR48_followup"] = (
        PR48_REFINED_MISSING_OBJECTS
    )
    payload["public_status_after_sprint"] = radius.PUBLIC_STATUS
    payload["official_predictions_changed"] = False
    payload["empirical_derivation_inputs_used"] = False
    payload["promoted_statuses"] = []
    write_json(path, payload)


def update_prediction_package(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    payload["sections"]["charged_same_sector_ratios"]["open_blockers"] = ORIGINAL_PR46_MISSING_OBJECTS
    payload["sections"]["charged_same_sector_ratios"]["refined_open_blockers_from_PR48_followup"] = (
        PR48_REFINED_MISSING_OBJECTS
    )
    payload["sections"]["open_boundary_parameters"].update(
        {
            "status": "BLOCKED_BY_MISSING_OBJECTS",
            "source_artifact": "artifacts/profile_scale_tau_sigma_update_v1.json",
            "source_artifact_from_PR48_followup": "artifacts/internal_profile_radius_closure_or_obstruction_v2.json",
            "uses_empirical_input": False,
            "comparison_ready": False,
            "open_blockers": ORIGINAL_PR46_MISSING_OBJECTS,
            "refined_open_blockers_from_PR48_followup": PR48_REFINED_MISSING_OBJECTS,
        }
    )
    payload["official_predictions_changed"] = False
    payload["empirical_derivation_inputs_used"] = False
    write_json(path, payload)


def update_open_gate_ledger(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    payload["statuses"].update(
        {
            "berger_radius_measure_normalization": artifact["r_internal_profile_status"],
            "internal_profile_radius_normalization": artifact["r_internal_profile_status"],
            "berger_measure_domain": artifact["dmu_Berger_domain_status"],
            "boundary_profile_scale_closure": "BLOCKED_BY_MISSING_OBJECTS",
            "sigma_from_boundary_geometry": "OPEN_LOCALIZABLE",
            "tau_from_boundary_geometry": "OPEN_LOCALIZABLE",
            "charged_no_fit_outputs": "BLOCKED_BY_TAU_SIGMA_BOUNDARY_DERIVATION",
            "empirical_derivation_inputs_used": False,
            "official_predictions": "UNCHANGED",
        }
    )
    payload["remaining_open_blockers"] = _unique_extend(
        payload["remaining_open_blockers"],
        [radius.MISSING_SELECTION_THEOREM, "Z_H", "kappa_H"],
    )
    payload["official_predictions_changed"] = False
    write_json(path, payload)


def update_claim_status(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    _append_claim_row(
        payload,
        {
            "claim": "Internal Berger radius selection theorem",
            "status": artifact["r_internal_profile_status"],
            "boundary": "Multiple repo-localized normalization routes remain candidates; missing theorem INTERNAL_BERGER_RADIUS_SELECTION_THEOREM.",
        },
    )
    _append_claim_row(
        payload,
        {
            "claim": "Berger measure/domain normalization",
            "status": artifact["dmu_Berger_domain_status"],
            "boundary": "Metric and domain are localized, but volume/measure normalization depends on the unselected internal radius convention.",
        },
    )
    payload["official_predictions_changed"] = False
    write_json(path, payload)


def update_current_status(path: Path, artifact: dict) -> None:
    text = path.read_text(encoding="utf-8")
    marker = "## Internal Berger Radius And Measure Normalization Assault"
    section = f"""
{marker}

This targeted follow-up attacks the first blocker from PR #48:
`r_internal_profile` and the internal Berger measure/domain normalization. It
tests unit-radius, Lambda-radius, overlap-radius, Berger-volume, and
collar-depth matching routes without using observed masses, Higgs data, gauge
values, CKM, PMNS, neutrino data, DESI residuals, or target ratios.

Result: `{artifact["r_internal_profile_status"]}`.

No route is uniquely selected by current repo axioms. The exact missing theorem
is `{artifact["missing_theorem"]}`. It must choose among a unit-radius
convention, Lambda-to-radius convention, overlap-width-to-radius convention,
Berger-volume normalization theorem, or collar-depth matching theorem.

`dmu_Berger` and the internal profile domain remain `{artifact["dmu_Berger_domain_status"]}`.
`Z_H` is not set to one, `sigma` and `tau` remain `OPEN_LOCALIZABLE`, no charged
outputs at boundary tau are exported, and official/frozen predictions remain
unchanged.
"""
    if marker in text:
        text = text.split(marker, 1)[0].rstrip() + "\n\n" + section.strip() + "\n"
    else:
        text = text.rstrip() + "\n\n" + section.strip() + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    artifacts = ROOT / "artifacts"
    artifact = radius.build_radius_measure_closure_or_obstruction_artifact(ROOT)
    forks = radius.build_radius_normalization_forks(ROOT)
    measure = radius.build_berger_measure_domain_artifact(ROOT)

    write_json(artifacts / "berger_radius_measure_normalization_v1.json", artifact)
    write_json(
        artifacts / "internal_radius_normalization_forks_v1.json",
        {
            **radius._guardrails(),
            "artifact": "internal_radius_normalization_forks_v1",
            "normalization_forks": [fork.__dict__ for fork in forks],
            "selection": radius.select_unique_radius_normalization_if_possible(ROOT),
        },
    )
    write_json(artifacts / "berger_measure_domain_v1.json", measure)
    write_json(
        artifacts / "internal_profile_radius_closure_or_obstruction_v2.json",
        {
            **radius._guardrails(),
            "public_status": radius.PUBLIC_STATUS,
            "artifact": "internal_profile_radius_closure_or_obstruction_v2",
            "r_internal_profile_status": artifact["r_internal_profile_status"],
            "r_internal_profile_value": artifact["r_internal_profile_value"],
            "selected_route": artifact["selected_route"],
            "missing_theorem": artifact["missing_theorem"],
            "requires_one_of": artifact["requires_one_of"],
            "dmu_Berger_domain_status": artifact["dmu_Berger_domain_status"],
            "obstruction": artifact["obstruction"],
        },
    )

    if artifact["r_internal_profile_status"] in (radius.DERIVED_FIXED, radius.DERIVED_CONDITIONAL):
        write_json(
            artifacts / "internal_profile_radius_value_v1.json",
            {
                **radius._guardrails(),
                "artifact": "internal_profile_radius_value_v1",
                "r_internal_profile": artifact["r_internal_profile_value"],
                "selected_route": artifact["selected_route"],
            },
        )

    update_boundary_profile_artifact(artifacts / "boundary_profile_scale_closure_v1.json", artifact)
    update_radius_symbol_disambiguation(artifacts / "radius_symbol_disambiguation_v1.json", artifact)
    update_internal_profile_artifact(artifacts / "internal_profile_radius_normalization_v1.json", artifact)
    update_profile_scale_artifact(artifacts / "profile_scale_tau_sigma_update_v1.json", artifact)
    update_tau_sigma_artifact(
        artifacts / "tau_sigma_boundary_derivation_closure_or_obstruction_v1.json",
        artifact,
    )
    update_numerical_gate_report(artifacts / "BHSM_numerical_gate_closure_assault_v1.json", artifact)
    update_prediction_package(artifacts / "BHSM_prediction_package_skeleton_v1.json", artifact)
    update_open_gate_ledger(artifacts / "full_BHSM_open_gate_ledger_v2.json", artifact)
    update_claim_status(artifacts / "full_BHSM_claim_status_table_v2.json", artifact)
    update_current_status(ROOT / "docs" / "current_status.md", artifact)


if __name__ == "__main__":
    main()
