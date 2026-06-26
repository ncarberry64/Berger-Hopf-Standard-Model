from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import boundary_no_fit_package_completion as package


def write_json(path: Path, payload: dict | list) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _guard(payload: dict) -> dict:
    payload.update(package.guardrails())
    return payload


def _append_or_update_claim(payload: dict, row: dict) -> None:
    for entry in payload["claim_statuses"]:
        if entry["claim"] == row["claim"]:
            entry.update(row)
            return
    payload["claim_statuses"].append(row)


def update_profile_normalization_hessian(path: Path) -> None:
    payload = _guard(load_json(path))
    values = package.profile_scale_values()
    payload["canonical_profile_hessian_theorem"] = package.AUTHOR_HESSIAN_STATUS
    payload["kappa_H"]["status"] = package.DERIVED_CONDITIONAL
    payload["kappa_H"]["derived"] = True
    payload["kappa_H"]["value"] = values["kappa_H"]
    payload["kappa_H"]["formula"] = "kappa_H = mu_H = 64*pi^5"
    payload["kappa_H"]["mu_H_identified_with_kappa_H"] = True
    payload["kappa_H_profile_hessian"] = package.DERIVED_CONDITIONAL
    payload["profile_scale_closure"] = package.DERIVED_CONDITIONAL
    payload["sigma_tau"] = package.tau_sigma_boundary_values()
    payload["remaining_blockers"] = []
    payload["charged_outputs_at_tau"] = {
        **package.guardrails(),
        "exported": True,
        "status": package.NO_FIT_OUTPUT_CANDIDATE_EXPORTED,
        "output_files": [
            "artifacts/charged_outputs_at_boundary_tau_A_local_v1.json",
            "artifacts/charged_outputs_at_boundary_tau_A_background_identity_v1.json",
        ],
    }
    write_json(path, payload)


def update_z_h(path: Path) -> None:
    payload = _guard(load_json(path))
    payload["status"] = package.DERIVED_CONDITIONAL
    payload["derived"] = True
    payload["value"] = 1.0
    write_json(path, payload)


def update_kappa(path: Path) -> None:
    payload = _guard(load_json(path))
    values = package.profile_scale_values()
    payload["status"] = package.DERIVED_CONDITIONAL
    payload["derived"] = True
    payload["value"] = values["kappa_H"]
    payload["formula"] = "kappa_H = mu_H = 64*pi^5"
    payload["canonical_profile_hessian_theorem"] = package.AUTHOR_HESSIAN_STATUS
    payload["mu_H_identified_with_kappa_H"] = True
    payload["missing_objects"] = []
    payload["obstruction"] = None
    write_json(path, payload)


def update_tau_sigma_profile(path: Path) -> None:
    payload = _guard(load_json(path))
    payload.update(package.tau_sigma_boundary_values())
    payload["artifact"] = "tau_sigma_profile_scale_closure_v1"
    write_json(path, payload)


def update_profile_scale_update(path: Path) -> None:
    payload = _guard(load_json(path))
    values = package.profile_scale_values()
    update = payload["profile_scale_tau_sigma_update"]
    update["Z_H_status"] = package.DERIVED_CONDITIONAL
    update["Z_H"] = 1.0
    update["kappa_H_status"] = package.DERIVED_CONDITIONAL
    update["kappa_H"] = values["kappa_H"]
    update["sigma_from_boundary_geometry"] = package.DERIVED_CONDITIONAL
    update["tau_from_boundary_geometry"] = package.DERIVED_CONDITIONAL
    update["sigma_derived"] = True
    update["tau_derived"] = True
    update["sigma"] = values["sigma"]
    update["tau"] = values["tau"]
    update["missing_objects"] = []
    update["sigma_formula_after_hessian_closure"] = "sigma = 4*pi^(5/2)"
    update["tau_formula_after_hessian_closure"] = "tau = 1/(4*pi^(3/2))"
    update["charged_outputs_at_tau_exported"] = True
    payload["boundary_profile_scale_closure"] = package.DERIVED_CONDITIONAL
    payload["missing_objects"] = []
    payload["charged_outputs_at_tau_exported"] = True
    write_json(path, payload)


def update_boundary_profile(path: Path) -> None:
    payload = _guard(load_json(path))
    values = package.profile_scale_values()
    payload["targeted_followup_from_boundary_no_fit_package_completion"] = {
        "source_artifact": "artifacts/BHSM_boundary_no_fit_prediction_package_v1.json",
        "kappa_H_status": package.DERIVED_CONDITIONAL,
        "kappa_H": values["kappa_H"],
        "sigma": values["sigma"],
        "tau": values["tau"],
        "remaining_blockers": [],
    }
    payload["kappa_H_result"]["status"] = package.DERIVED_CONDITIONAL
    payload["kappa_H_result"]["derived"] = True
    payload["kappa_H_result"]["value"] = values["kappa_H"]
    payload["kappa_H_result"]["formula"] = "kappa_H = mu_H = 64*pi^5"
    payload["sigma_tau_result"] = package.tau_sigma_boundary_values()
    payload["boundary_profile_scale_closure"] = package.DERIVED_CONDITIONAL
    payload["missing_objects"] = []
    payload["refined_missing_objects_after_boundary_no_fit_package"] = []
    payload["charged_outputs_at_tau_exported"] = True
    write_json(path, payload)


def update_numerical_gate(path: Path) -> None:
    payload = _guard(load_json(path))
    payload["gates"]["tau_sigma"]["targeted_followup_from_boundary_no_fit_package_completion"] = {
        "source_artifact": "artifacts/BHSM_boundary_no_fit_prediction_package_v1.json",
        "profile_scale_closure": package.DERIVED_CONDITIONAL,
        "sigma_from_boundary_geometry": package.DERIVED_CONDITIONAL,
        "tau_from_boundary_geometry": package.DERIVED_CONDITIONAL,
        "remaining_blockers": [],
    }
    payload["gates"]["tau_sigma"]["missing_objects"] = []
    payload["gates"]["tau_sigma"]["refined_missing_objects_after_boundary_no_fit_package"] = []
    payload["gates"]["charged_outputs_at_tau"]["status"] = package.NO_FIT_OUTPUT_CANDIDATE_EXPORTED
    payload["gates"]["charged_outputs_at_tau"]["missing_objects"] = []
    payload["gates"]["charged_outputs_at_tau"]["refined_missing_objects_after_boundary_no_fit_package"] = []
    payload["promoted_statuses"] = [
        {"gate": "internal_berger_radius_selection_theorem", "status": "DERIVED_CONDITIONAL_FROM_AUTHOR_AXIOM"},
        {"gate": "r_internal_profile", "status": package.DERIVED_CONDITIONAL},
        {"gate": "Z_H_profile_normalization", "status": package.DERIVED_CONDITIONAL},
        {"gate": "kappa_H_profile_hessian", "status": package.DERIVED_CONDITIONAL},
        {"gate": "profile_scale_closure", "status": package.DERIVED_CONDITIONAL},
        {"gate": "charged_outputs_at_boundary_tau", "status": package.NO_FIT_OUTPUT_CANDIDATE_EXPORTED},
    ]
    payload["BHSM_boundary_no_fit_prediction_package"] = package.COMPLETE_EXPORTED
    payload["BHSM_internal_boundary_package"] = package.COMPLETE
    payload["external_empirical_comparison_package"] = package.EXTERNAL_LAYER
    payload["public_status_after_sprint"] = package.PUBLIC_STATUS
    write_json(path, payload)


def update_prediction_package(path: Path) -> None:
    payload = _guard(load_json(path))
    payload["BHSM_boundary_no_fit_prediction_package"] = package.COMPLETE_EXPORTED
    payload["BHSM_internal_boundary_package"] = package.COMPLETE
    payload["external_empirical_comparison_package"] = package.EXTERNAL_LAYER
    payload["sections"]["open_boundary_parameters"]["status"] = package.DERIVED_CONDITIONAL
    payload["sections"]["open_boundary_parameters"]["comparison_ready"] = False
    payload["sections"]["open_boundary_parameters"]["open_blockers"] = []
    payload["sections"]["open_boundary_parameters"]["refined_open_blockers_after_boundary_no_fit_package"] = []
    payload["sections"]["charged_same_sector_ratios"]["status"] = package.NO_FIT_OUTPUT_CANDIDATE_EXPORTED
    payload["sections"]["charged_same_sector_ratios"]["source_artifact_from_boundary_no_fit_package"] = (
        "artifacts/charged_boundary_bridge_values_v1.json"
    )
    write_json(path, payload)


def update_open_gate_ledger(path: Path) -> None:
    payload = _guard(load_json(path))
    payload["statuses"].update(
        {
            "canonical_profile_hessian_theorem": package.AUTHOR_HESSIAN_STATUS,
            "kappa_H_profile_hessian": package.DERIVED_CONDITIONAL,
            "profile_scale_closure": package.DERIVED_CONDITIONAL,
            "sigma_from_boundary_geometry": package.DERIVED_CONDITIONAL,
            "tau_from_boundary_geometry": package.DERIVED_CONDITIONAL,
            "charged_no_fit_outputs": package.NO_FIT_OUTPUT_CANDIDATE_EXPORTED,
            "common_scale_boundary_transport": package.DERIVED_FIXED_IDENTITY,
            "neutral_boundary_operator": "CLOSED_AS_BOUNDARY_SEED",
            "PMNS_boundary_no_fit_output": "CLOSED_UNDER_CANONICAL_MINIMAL_CHARGED_DIAGONAL_CONVENTION",
            "CKM_full_boundary_no_fit_output": "CLOSED_BY_TAU_SUPPRESSED_HIGHER_CHANNEL_THEOREM",
            "CP_boundary_holonomy": "CLOSED",
            "BHSM_boundary_no_fit_prediction_package": package.COMPLETE_EXPORTED,
            "BHSM_internal_boundary_package": package.COMPLETE,
            "external_empirical_comparison_package": package.EXTERNAL_LAYER,
            "official_predictions": "UNCHANGED",
            "empirical_derivation_inputs_used": False,
        }
    )
    payload["remaining_open_blockers"] = [
        item for item in payload.get("remaining_open_blockers", []) if item not in ("kappa_H", "Z_H", "r_internal_profile")
    ]
    payload["official_predictions_changed"] = False
    write_json(path, payload)


def update_claim_status(path: Path) -> None:
    payload = _guard(load_json(path))
    for row in (
        {
            "claim": "Canonical profile Hessian theorem",
            "status": package.AUTHOR_HESSIAN_STATUS,
            "boundary": "Author BHSM theorem identifies kappa_H with mu_H = 64*pi^5.",
        },
        {
            "claim": "kappa_H profile second variation closure",
            "status": package.DERIVED_CONDITIONAL,
            "boundary": "Closed conditionally by CANONICAL_PROFILE_HESSIAN_THEOREM; no observed Higgs value is used.",
        },
        {
            "claim": "Tau/sigma profile scale closure",
            "status": package.DERIVED_CONDITIONAL,
            "boundary": "sigma=4*pi^(5/2), tau=1/(4*pi^(3/2)) from author-normalized boundary package.",
        },
        {
            "claim": "BHSM boundary no-fit prediction package",
            "status": package.COMPLETE_EXPORTED,
            "boundary": "Internal boundary no-fit package exported; external empirical comparison remains separate/open.",
        },
    ):
        _append_or_update_claim(payload, row)
    payload["official_predictions_changed"] = False
    write_json(path, payload)


def update_current_status(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    marker = "## BHSM Boundary No-Fit Package Completion"
    section = f"""
{marker}

The internal BHSM boundary no-fit package is exported as
`{package.COMPLETE_EXPORTED}`. The completed internal profile-scale values are:

- `r_internal_profile^2 = 1/(4*pi)`;
- `Z_H = 1`;
- `kappa_H = mu_H = 64*pi^5`;
- `sigma = 4*pi^(5/2)`;
- `tau = 1/(4*pi^(3/2))`.

The package also exports charged boundary bridge values, identity transport at
`mu_BH_boundary`, the neutral boundary seed, PMNS/CKM no-fit operator outputs,
and the `delta_BH=pi/3` CP holonomy seed. This is an internal boundary no-fit
export only. The external empirical comparison package remains
`{package.EXTERNAL_LAYER}`; no observed masses, Higgs value, gauge values,
CKM/PMNS data, CP data, or cosmology residuals are used as derivation inputs.
Frozen and official predictions remain unchanged.
"""
    if marker in text:
        text = text.split(marker, 1)[0].rstrip() + "\n\n" + section.strip() + "\n"
    else:
        text = text.rstrip() + "\n\n" + section.strip() + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    artifacts = ROOT / "artifacts"
    write_json(artifacts / "canonical_profile_hessian_theorem_v1.json", package.canonical_profile_hessian_theorem(ROOT))
    write_json(artifacts / "tau_sigma_boundary_values_v1.json", package.tau_sigma_boundary_values())
    write_json(artifacts / "profile_scale_closure_values_v1.json", package.profile_scale_values())
    write_json(artifacts / "charged_boundary_bridge_values_v1.json", package.charged_bridge_values())
    write_json(
        artifacts / "charged_outputs_at_boundary_tau_A_local_v1.json",
        package.charged_outputs_at_boundary_tau("A_local"),
    )
    write_json(
        artifacts / "charged_outputs_at_boundary_tau_A_background_identity_v1.json",
        package.charged_outputs_at_boundary_tau("A_background_identity"),
    )
    write_json(artifacts / "common_scale_boundary_transport_v1.json", package.common_scale_boundary_transport())
    write_json(artifacts / "neutral_operator_no_fit_output_v1.json", package.neutral_operator_output())
    write_json(artifacts / "PMNS_no_fit_operator_output_v1.json", package.pmns_output())
    write_json(artifacts / "CKM_no_fit_operator_output_v1.json", package.ckm_output())
    write_json(artifacts / "CP_no_fit_holonomy_output_v1.json", package.cp_holonomy_output())
    write_json(artifacts / "BHSM_boundary_no_fit_prediction_package_v1.json", package.boundary_no_fit_prediction_package())

    update_profile_normalization_hessian(artifacts / "profile_normalization_hessian_closure_v1.json")
    update_z_h(artifacts / "Z_H_profile_normalization_value_or_obstruction_v2.json")
    update_kappa(artifacts / "kappa_H_profile_hessian_value_or_obstruction_v2.json")
    update_tau_sigma_profile(artifacts / "tau_sigma_profile_scale_closure_v1.json")
    update_profile_scale_update(artifacts / "profile_scale_tau_sigma_update_v1.json")
    update_boundary_profile(artifacts / "boundary_profile_scale_closure_v1.json")
    update_numerical_gate(artifacts / "BHSM_numerical_gate_closure_assault_v1.json")
    update_prediction_package(artifacts / "BHSM_prediction_package_skeleton_v1.json")
    update_open_gate_ledger(artifacts / "full_BHSM_open_gate_ledger_v2.json")
    update_claim_status(artifacts / "full_BHSM_claim_status_table_v2.json")
    update_current_status(ROOT / "docs" / "current_status.md")


if __name__ == "__main__":
    main()
