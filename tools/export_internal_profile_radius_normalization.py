from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import internal_profile_radius_normalization as norm

ORIGINAL_PR46_MISSING_OBJECTS = ["kappa_H", "Z_H", "r"]


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


def _guarded_subset(payload: dict, keys: list[str]) -> dict:
    return {key: payload[key] for key in keys}


def update_previous_boundary_profile_artifact(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    payload["targeted_followup_from_PR47"] = {
        "sprint": "Internal/Profile Berger Radius Normalization + Higgs/Profile Normal Form Assault",
        "source_artifact": "artifacts/internal_profile_radius_normalization_v1.json",
        "r_internal_profile_status": artifact["r_internal_profile"]["status"],
        "Phi_profile_status": artifact["Phi_profile"]["status"],
        "Z_H_status": artifact["Z_H"]["status"],
        "kappa_H_status": artifact["kappa_H"]["status"],
        "boundary_profile_scale_closure": artifact["boundary_profile_scale_closure"],
        "missing_objects": artifact["missing_objects"],
    }
    payload["boundary_profile_scale_closure"] = artifact["boundary_profile_scale_closure"]
    payload["sigma_from_boundary_geometry"] = artifact["sigma_from_boundary_geometry"]
    payload["tau_from_boundary_geometry"] = artifact["tau_from_boundary_geometry"]
    payload["missing_objects"] = ORIGINAL_PR46_MISSING_OBJECTS
    payload["refined_missing_objects_from_PR47_followup"] = artifact["missing_objects"]
    payload["charged_outputs_at_tau_exported"] = artifact["charged_outputs_at_tau_exported"]
    payload["public_status_after_gate"] = artifact["public_status_after_gate"]
    payload["official_predictions_changed"] = False
    payload["empirical_derivation_inputs_used"] = False
    write_json(path, payload)


def update_tau_sigma_artifact(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    payload["targeted_followup_from_PR47"] = {
        "source_artifact": "artifacts/profile_scale_tau_sigma_update_v1.json",
        "r_internal_profile_status": artifact["r_internal_profile"]["status"],
        "Z_H_status": artifact["Z_H"]["status"],
        "kappa_H_status": artifact["kappa_H"]["status"],
        "missing_objects": artifact["missing_objects"],
    }
    payload["status"] = "OPEN_LOCALIZABLE"
    payload["sigma_from_boundary_geometry"] = "OPEN_LOCALIZABLE"
    payload["tau_from_boundary_geometry"] = "OPEN_LOCALIZABLE"
    payload["missing_objects"] = ORIGINAL_PR46_MISSING_OBJECTS
    payload["refined_missing_objects_from_PR47_followup"] = artifact["missing_objects"]
    payload["obstruction"] = (
        "Cannot compute sigma=(1/2)sqrt(kappa_H/Z_H) and tau=1/(4 sigma r^2) "
        "until r_internal_profile, Z_H, and kappa_H are repo-derived."
    )
    payload["official_predictions_changed"] = False
    payload["empirical_derivation_inputs_used"] = False
    payload["observed_masses_used"] = False
    payload["observed_Higgs_used"] = False
    payload["observed_gauge_values_used"] = False
    payload["tau_fit_to_masses"] = False
    payload["sigma_fit_to_masses"] = False
    write_json(path, payload)


def update_numerical_gate_report(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    tau = payload["gates"]["tau_sigma"]
    tau["targeted_followup_from_PR47"] = {
        "source_artifact": "artifacts/internal_profile_radius_normalization_v1.json",
        "boundary_profile_scale_closure": artifact["boundary_profile_scale_closure"],
        "r_internal_profile_status": artifact["r_internal_profile"]["status"],
        "Phi_profile_status": artifact["Phi_profile"]["status"],
        "Z_H_status": artifact["Z_H"]["status"],
        "kappa_H_status": artifact["kappa_H"]["status"],
    }
    tau["missing_objects"] = ORIGINAL_PR46_MISSING_OBJECTS
    tau["refined_missing_objects_from_PR47_followup"] = artifact["missing_objects"]
    payload["gates"]["charged_outputs_at_tau"]["missing_objects"] = ORIGINAL_PR46_MISSING_OBJECTS
    payload["gates"]["charged_outputs_at_tau"]["refined_missing_objects_from_PR47_followup"] = artifact[
        "missing_objects"
    ]
    payload["gates"]["charged_outputs_at_tau"]["status"] = "BLOCKED_BY_TAU_SIGMA_BOUNDARY_DERIVATION"
    payload["promoted_statuses"] = []
    payload["missing_objects"] = _unique_extend(payload["missing_objects"], artifact["missing_objects"])
    payload["public_status_after_sprint"] = norm.PUBLIC_STATUS
    payload["official_predictions_changed"] = False
    payload["empirical_derivation_inputs_used"] = False
    write_json(path, payload)


def update_prediction_package(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    payload["sections"]["charged_same_sector_ratios"]["open_blockers"] = ORIGINAL_PR46_MISSING_OBJECTS
    payload["sections"]["charged_same_sector_ratios"]["refined_open_blockers_from_PR47_followup"] = artifact[
        "missing_objects"
    ]
    payload["sections"]["open_boundary_parameters"].update(
        {
            "status": "BLOCKED_BY_MISSING_OBJECTS",
            "source_artifact": "artifacts/profile_scale_tau_sigma_update_v1.json",
            "uses_empirical_input": False,
            "comparison_ready": False,
            "open_blockers": ORIGINAL_PR46_MISSING_OBJECTS,
            "refined_open_blockers_from_PR47_followup": artifact["missing_objects"],
        }
    )
    payload["package_status"] = "EXPORTED_NOT_COMPARISON_READY"
    payload["official_predictions_changed"] = False
    payload["empirical_derivation_inputs_used"] = False
    write_json(path, payload)


def update_open_gate_ledger(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    payload["statuses"].update(
        {
            "internal_profile_radius_normalization": artifact["r_internal_profile"]["status"],
            "Phi_profile_normal_form": artifact["Phi_profile"]["status"],
            "Z_H_profile_normalization": artifact["Z_H"]["status"],
            "kappa_H_profile_second_variation": artifact["kappa_H"]["status"],
            "boundary_profile_scale_closure": artifact["boundary_profile_scale_closure"],
            "sigma_from_boundary_geometry": artifact["sigma_from_boundary_geometry"],
            "tau_from_boundary_geometry": artifact["tau_from_boundary_geometry"],
            "charged_no_fit_outputs": "BLOCKED_BY_TAU_SIGMA_BOUNDARY_DERIVATION",
            "empirical_derivation_inputs_used": False,
            "official_predictions": "UNCHANGED",
        }
    )
    payload["remaining_open_blockers"] = _unique_extend(
        payload["remaining_open_blockers"],
        [
            "Hopf fiber-radius normalization theorem",
            "Berger volume normalization theorem",
            "profile normalization theorem identifying Z_H with unit norm",
            "S_eff^(H) Higgs/profile effective action",
            "boundary potential curvature coefficients",
        ],
    )
    payload["official_predictions_changed"] = False
    write_json(path, payload)


def update_claim_status(path: Path, artifact: dict) -> None:
    payload = load_json(path)
    _append_claim_row(
        payload,
        {
            "claim": "Internal/profile Berger radius normalization",
            "status": artifact["r_internal_profile"]["status"],
            "boundary": "Blocked by missing Hopf fiber-radius, Berger volume, profile-domain, collar-depth, and Lambda-to-radius conventions.",
        },
    )
    _append_claim_row(
        payload,
        {
            "claim": "Higgs/topographic profile normal form",
            "status": artifact["Phi_profile"]["status"],
            "boundary": "Gaussian/topographic normal form localized; Phi_0 is symbolic only until sigma, domain, and measure are derived.",
        },
    )
    _append_claim_row(
        payload,
        {
            "claim": "Z_H profile normalization closure",
            "status": artifact["Z_H"]["status"],
            "boundary": "Z_H is not set to one without a profile normalization theorem and evaluated measure.",
        },
    )
    _append_claim_row(
        payload,
        {
            "claim": "kappa_H profile second variation closure",
            "status": artifact["kappa_H"]["status"],
            "boundary": "Blocked until S_eff^(H), profile saddle, H_H, V_eff'', and boundary potential curvature coefficients are derived.",
        },
    )
    payload["official_predictions_changed"] = False
    write_json(path, payload)


def update_current_status(path: Path, artifact: dict) -> None:
    text = path.read_text(encoding="utf-8")
    marker = "## Internal/Profile Radius And Higgs/Profile Normal Form Assault"
    section = f"""
{marker}

This targeted follow-up reduces the first blocker from PR #47. It attacks the
internal/profile Berger radius, canonical profile normal form, profile
normalization `Z_H`, and Higgs/profile second variation `kappa_H`. It does not
use observed masses, Higgs data, gauge values, target ratios, CKM, PMNS,
neutrino data, cosmology residuals, or DESI residuals as derivation inputs.

Result: `{artifact["boundary_profile_scale_closure"]}`.

- `r_internal_profile`: `{artifact["r_internal_profile"]["status"]}`. Missing
  theorem inputs are Hopf fiber-radius normalization, Berger volume
  normalization, internal profile-domain measure, collar-depth matching, and
  Lambda-to-radius convention.
- `Phi(y)`: `{artifact["Phi_profile"]["status"]}`. The normal form
  `Phi(y)=Phi_0 exp[-sigma d_B(y,y_0)^2]` is localized conditionally, but
  `Phi_0` remains symbolic until sigma, domain, and measure are fixed.
- `Z_H`: `{artifact["Z_H"]["status"]}`. It is not set to one without a profile
  normalization theorem and evaluated profile/collar measure.
- `kappa_H`: `{artifact["kappa_H"]["status"]}`. The second-variation formula is
  localized, but `S_eff^(H)`, the profile saddle, `H_H`, `V_eff''`, and boundary
  curvature coefficients remain open.

Therefore `sigma` and `tau` remain `OPEN_LOCALIZABLE`, no charged outputs at
boundary tau are exported, and official/frozen predictions remain unchanged.
"""
    if marker in text:
        text = text.split(marker, 1)[0].rstrip() + "\n\n" + section.strip() + "\n"
    else:
        text = text.rstrip() + "\n\n" + section.strip() + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    artifacts = ROOT / "artifacts"
    artifact = norm.build_internal_profile_radius_closure_artifact(ROOT)
    write_json(artifacts / "internal_profile_radius_normalization_v1.json", artifact)
    write_json(
        artifacts / "Phi_profile_normal_form_v1.json",
        {
            **norm._guardrails(),
            "artifact": "Phi_profile_normal_form_v1",
            "profile": artifact["Phi_profile"],
        },
    )
    write_json(
        artifacts / "Z_H_profile_normalization_closure_or_obstruction_v1.json",
        {
            **norm._guardrails(),
            "artifact": "Z_H_profile_normalization_closure_or_obstruction_v1",
            "Z_H": artifact["Z_H"],
        },
    )
    write_json(
        artifacts / "kappa_H_profile_second_variation_closure_or_obstruction_v1.json",
        {
            **norm._guardrails(),
            "artifact": "kappa_H_profile_second_variation_closure_or_obstruction_v1",
            "kappa_H": artifact["kappa_H"],
        },
    )
    write_json(
        artifacts / "profile_scale_tau_sigma_update_v1.json",
        {
            **norm._guardrails(),
            "artifact": "profile_scale_tau_sigma_update_v1",
            "profile_scale_tau_sigma_update": artifact["profile_scale_tau_sigma_update"],
            "boundary_profile_scale_closure": artifact["boundary_profile_scale_closure"],
            "missing_objects": artifact["missing_objects"],
            "charged_outputs_at_tau_exported": artifact["charged_outputs_at_tau_exported"],
        },
    )

    update_previous_boundary_profile_artifact(artifacts / "boundary_profile_scale_closure_v1.json", artifact)
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
