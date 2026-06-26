from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import profile_normalization_hessian_closure as closure


ORIGINAL_PR46_MISSING_OBJECTS = ["kappa_H", "Z_H", "r"]
POST_RADIUS_MISSING_OBJECTS = ["Z_H", "kappa_H"]
POST_PROFILE_NORMALIZATION_MISSING_OBJECTS = ["kappa_H"]


def write_json(path: Path, payload: dict | list) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _guard(payload: dict) -> dict:
    payload.update(
        {
            "public_status_before_gate": closure.PUBLIC_STATUS,
            "official_predictions_changed": False,
            "empirical_derivation_inputs_used": False,
            "observed_masses_used": False,
            "observed_Higgs_used": False,
            "observed_gauge_values_used": False,
            "tau_fit_to_masses": False,
            "sigma_fit_to_masses": False,
            "radius_gate_status": closure.RADIUS_GATE_STATUS,
        }
    )
    return payload


def _append_or_update_claim(payload: dict, row: dict) -> None:
    for entry in payload["claim_statuses"]:
        if entry["claim"] == row["claim"]:
            entry.update(row)
            return
    payload["claim_statuses"].append(row)


def update_profile_scale(path: Path, artifact: dict) -> None:
    payload = _guard(load_json(path))
    update = payload["profile_scale_tau_sigma_update"]
    update["r_internal_profile_status"] = "DERIVED_CONDITIONAL"
    update["Z_H_status"] = closure.DERIVED_CONDITIONAL
    update["Z_H"] = 1.0
    update["kappa_H_status"] = closure.BLOCKED_BY_MISSING_PROFILE_HESSIAN_THEOREM
    update["missing_objects"] = POST_PROFILE_NORMALIZATION_MISSING_OBJECTS
    update["sigma_from_boundary_geometry"] = closure.OPEN_LOCALIZABLE_BLOCKED_BY_KAPPA_H
    update["tau_from_boundary_geometry"] = closure.OPEN_LOCALIZABLE_BLOCKED_BY_KAPPA_H
    update["sigma_formula_after_Z_H_substitution"] = "sigma(kappa_H) = (1/2)*sqrt(kappa_H)"
    update["tau_formula_after_Z_H_substitution"] = "tau(kappa_H) = 2*pi/sqrt(kappa_H)"
    update["sigma_derived"] = False
    update["tau_derived"] = False
    update["tau"] = None
    update["charged_outputs_at_tau_exported"] = False
    update["targeted_followup_from_profile_normalization_hessian_closure"] = {
        "source_artifact": "artifacts/profile_normalization_hessian_closure_v1.json",
        "Z_H_status": closure.DERIVED_CONDITIONAL,
        "Z_H_value": 1.0,
        "kappa_H_status": closure.BLOCKED_BY_MISSING_PROFILE_HESSIAN_THEOREM,
        "remaining_blockers": POST_PROFILE_NORMALIZATION_MISSING_OBJECTS,
    }
    payload["boundary_profile_scale_closure"] = closure.BLOCKED_BY_MISSING_OBJECTS
    payload["missing_objects"] = POST_PROFILE_NORMALIZATION_MISSING_OBJECTS
    payload["charged_outputs_at_tau_exported"] = False
    write_json(path, payload)


def update_boundary_profile(path: Path, artifact: dict) -> None:
    payload = _guard(load_json(path))
    payload["targeted_followup_from_profile_normalization_hessian_closure"] = {
        "source_artifact": "artifacts/profile_normalization_hessian_closure_v1.json",
        "Z_H_status": closure.DERIVED_CONDITIONAL,
        "Z_H_value": 1.0,
        "kappa_H_status": closure.BLOCKED_BY_MISSING_PROFILE_HESSIAN_THEOREM,
        "remaining_blockers": POST_PROFILE_NORMALIZATION_MISSING_OBJECTS,
    }
    payload["Z_H_result"] = artifact["Z_H"]
    payload["kappa_H_result"] = artifact["kappa_H"]
    payload["boundary_profile_scale_closure"] = closure.BLOCKED_BY_MISSING_OBJECTS
    payload["missing_objects"] = ORIGINAL_PR46_MISSING_OBJECTS
    payload["refined_missing_objects_after_radius_selection"] = POST_RADIUS_MISSING_OBJECTS
    payload["refined_missing_objects_after_profile_normalization"] = POST_PROFILE_NORMALIZATION_MISSING_OBJECTS
    payload["charged_outputs_at_tau_exported"] = False
    write_json(path, payload)


def update_numerical_gate(path: Path, artifact: dict) -> None:
    payload = _guard(load_json(path))
    tau = payload["gates"]["tau_sigma"]
    tau["targeted_followup_from_profile_normalization_hessian_closure"] = {
        "source_artifact": "artifacts/profile_normalization_hessian_closure_v1.json",
        "Z_H_status": closure.DERIVED_CONDITIONAL,
        "Z_H_value": 1.0,
        "kappa_H_status": closure.BLOCKED_BY_MISSING_PROFILE_HESSIAN_THEOREM,
        "remaining_blockers": POST_PROFILE_NORMALIZATION_MISSING_OBJECTS,
        "tau_symbolic_after_Z_H_substitution": "tau(kappa_H) = 2*pi/sqrt(kappa_H)",
    }
    tau["refined_missing_objects_after_profile_normalization"] = POST_PROFILE_NORMALIZATION_MISSING_OBJECTS
    payload["gates"]["charged_outputs_at_tau"]["refined_missing_objects_after_profile_normalization"] = (
        POST_PROFILE_NORMALIZATION_MISSING_OBJECTS
    )
    payload["promoted_statuses"] = [
        {
            "gate": "internal_berger_radius_selection_theorem",
            "status": closure.RADIUS_GATE_STATUS,
        },
        {"gate": "r_internal_profile", "status": "DERIVED_CONDITIONAL"},
        {"gate": "Z_H_profile_normalization", "status": closure.DERIVED_CONDITIONAL},
    ]
    payload["public_status_after_sprint"] = closure.PUBLIC_STATUS
    write_json(path, payload)


def update_prediction_package(path: Path, artifact: dict) -> None:
    payload = _guard(load_json(path))
    open_params = payload["sections"]["open_boundary_parameters"]
    open_params.update(
        {
            "status": closure.BLOCKED_BY_MISSING_OBJECTS,
            "source_artifact_from_profile_normalization_hessian_closure": (
                "artifacts/profile_normalization_hessian_closure_v1.json"
            ),
            "uses_empirical_input": False,
            "comparison_ready": False,
            "open_blockers": ORIGINAL_PR46_MISSING_OBJECTS,
            "refined_open_blockers_after_radius_selection": POST_RADIUS_MISSING_OBJECTS,
            "refined_open_blockers_after_profile_normalization": POST_PROFILE_NORMALIZATION_MISSING_OBJECTS,
            "Z_H_status": closure.DERIVED_CONDITIONAL,
            "Z_H_value": 1.0,
            "kappa_H_status": closure.BLOCKED_BY_MISSING_PROFILE_HESSIAN_THEOREM,
        }
    )
    payload["sections"]["charged_same_sector_ratios"]["refined_open_blockers_after_profile_normalization"] = (
        POST_PROFILE_NORMALIZATION_MISSING_OBJECTS
    )
    write_json(path, payload)


def update_open_gate_ledger(path: Path, artifact: dict) -> None:
    payload = _guard(load_json(path))
    payload["statuses"].update(
        {
            "Z_H_profile_normalization": closure.DERIVED_CONDITIONAL,
            "kappa_H_profile_hessian": closure.BLOCKED_BY_MISSING_PROFILE_HESSIAN_THEOREM,
            "boundary_profile_scale_closure": closure.BLOCKED_BY_MISSING_OBJECTS,
            "sigma_from_boundary_geometry": closure.OPEN_LOCALIZABLE_BLOCKED_BY_KAPPA_H,
            "tau_from_boundary_geometry": closure.OPEN_LOCALIZABLE_BLOCKED_BY_KAPPA_H,
            "charged_no_fit_outputs": "BLOCKED_BY_TAU_SIGMA_BOUNDARY_DERIVATION",
            "official_predictions": "UNCHANGED",
            "empirical_derivation_inputs_used": False,
        }
    )
    payload["remaining_open_blockers"] = [
        item
        for item in payload.get("remaining_open_blockers", [])
        if item not in ("Z_H", "r_internal_profile")
    ]
    if "kappa_H" not in payload["remaining_open_blockers"]:
        payload["remaining_open_blockers"].append("kappa_H")
    payload["official_predictions_changed"] = False
    write_json(path, payload)


def update_claim_status(path: Path, artifact: dict) -> None:
    payload = _guard(load_json(path))
    _append_or_update_claim(
        payload,
        {
            "claim": "Z_H profile normalization",
            "status": closure.DERIVED_CONDITIONAL,
            "boundary": (
                "Author/canonical BHSM profile normalization theorem sets "
                "Z_H = integral_B |Phi|^2 dmu_Berger = 1."
            ),
        },
    )
    _append_or_update_claim(
        payload,
        {
            "claim": "Z_H profile normalization closure",
            "status": closure.DERIVED_CONDITIONAL,
            "boundary": "Closed conditionally by CANONICAL_INTERNAL_PROFILE_NORMALIZATION_THEOREM.",
        },
    )
    _append_or_update_claim(
        payload,
        {
            "claim": "kappa_H profile second variation closure",
            "status": closure.BLOCKED_BY_MISSING_PROFILE_HESSIAN_THEOREM,
            "boundary": (
                "Blocked until CANONICAL_PROFILE_HESSIAN_THEOREM evaluates "
                "delta^2 S_eff^(H) at Phi_H; mu_H is not identified with kappa_H."
            ),
        },
    )
    _append_or_update_claim(
        payload,
        {
            "claim": "Profile normalization/Hessian closure sprint",
            "status": closure.BLOCKED_BY_MISSING_PROFILE_HESSIAN_THEOREM,
            "boundary": "Z_H closed; kappa_H remains the single local profile-scale blocker.",
        },
    )
    payload["official_predictions_changed"] = False
    write_json(path, payload)


def update_current_status(path: Path, artifact: dict) -> None:
    text = path.read_text(encoding="utf-8")
    marker = "## Z_H Profile Normalization And kappa_H Hessian Closure"
    section = f"""
{marker}

The radius gate remains closed by `{closure.RADIUS_GATE_STATUS}` and is not
reopened. The author/canonical BHSM profile normalization theorem is encoded as:

`Z_H = integral_B |Phi(y)|^2 dmu_Berger = 1`.

Therefore `Z_H` is locally `{closure.DERIVED_CONDITIONAL}`. The Higgs/profile
Hessian coefficient `kappa_H` remains blocked by
`{closure.BLOCKED_BY_MISSING_PROFILE_HESSIAN_THEOREM}` because no source-traced
repo convention identifies `mu_H` or any existing stiffness object with
`kappa_H`.

With `r_internal_profile^2=1/(4*pi)` and `Z_H=1`, the symbolic dependency is
`tau(kappa_H) = 2*pi/sqrt(kappa_H)`. Tau and sigma are not numerically computed,
charged outputs at boundary tau are not exported, and official/frozen
predictions remain unchanged. The global public status remains
`{closure.PUBLIC_STATUS}`.
"""
    if marker in text:
        text = text.split(marker, 1)[0].rstrip() + "\n\n" + section.strip() + "\n"
    else:
        text = text.rstrip() + "\n\n" + section.strip() + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    artifacts = ROOT / "artifacts"
    artifact = closure.build_profile_normalization_hessian_closure_artifact(ROOT)
    z_h = closure.derive_Z_H_from_profile_normalization_if_possible(ROOT)
    kappa = closure.derive_kappa_H_from_profile_hessian_if_possible(ROOT)
    sigma_tau = closure.derive_sigma_tau_if_possible(ROOT)

    write_json(artifacts / "profile_normalization_hessian_closure_v1.json", artifact)
    write_json(
        artifacts / "Z_H_profile_normalization_value_or_obstruction_v2.json",
        {
            **closure._guardrails(),
            **closure._radius_values(),
            "artifact": "Z_H_profile_normalization_value_or_obstruction_v2",
            **z_h,
        },
    )
    write_json(
        artifacts / "kappa_H_profile_hessian_value_or_obstruction_v2.json",
        {
            **closure._guardrails(),
            **closure._radius_values(),
            "artifact": "kappa_H_profile_hessian_value_or_obstruction_v2",
            **kappa,
        },
    )
    write_json(
        artifacts / "tau_sigma_profile_scale_closure_v1.json",
        {
            **closure._guardrails(),
            **closure._radius_values(),
            "artifact": "tau_sigma_profile_scale_closure_v1",
            **sigma_tau,
        },
    )

    update_profile_scale(artifacts / "profile_scale_tau_sigma_update_v1.json", artifact)
    update_boundary_profile(artifacts / "boundary_profile_scale_closure_v1.json", artifact)
    update_numerical_gate(artifacts / "BHSM_numerical_gate_closure_assault_v1.json", artifact)
    update_prediction_package(artifacts / "BHSM_prediction_package_skeleton_v1.json", artifact)
    update_open_gate_ledger(artifacts / "full_BHSM_open_gate_ledger_v2.json", artifact)
    update_claim_status(artifacts / "full_BHSM_claim_status_table_v2.json", artifact)
    update_current_status(ROOT / "docs" / "current_status.md", artifact)


if __name__ == "__main__":
    main()
