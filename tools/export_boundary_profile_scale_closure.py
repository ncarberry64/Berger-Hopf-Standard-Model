from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import boundary_profile_scale_closure as closure


def write_json(path: Path, payload: dict | list) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _append_claim_row(claims: dict, row: dict) -> None:
    existing = {entry["claim"] for entry in claims["claim_statuses"]}
    if row["claim"] not in existing:
        claims["claim_statuses"].append(row)
        return
    for entry in claims["claim_statuses"]:
        if entry["claim"] == row["claim"]:
            entry.update(row)
            return


def _unique_extend(items: list, additions: list[str]) -> list:
    result = list(items)
    for item in additions:
        if item not in result:
            result.append(item)
    return result


def update_tau_sigma_artifact(path: Path, scale_artifact: dict) -> None:
    payload = load_json(path)
    payload["targeted_followup"] = {
        "sprint": "Boundary/Profile Scale Closure Assault for kappa_H, Z_H, and r",
        "source_artifact": "artifacts/boundary_profile_scale_closure_v1.json",
        "targeted_first_blocker_from_PR_46": True,
        "boundary_profile_scale_closure": scale_artifact["boundary_profile_scale_closure"],
        "r_status": scale_artifact["r"]["status"],
        "Z_H_status": scale_artifact["Z_H"]["status"],
        "kappa_H_status": scale_artifact["kappa_H"]["status"],
        "missing_objects": scale_artifact["missing_objects"],
    }
    payload["status"] = "OPEN_LOCALIZABLE"
    payload["sigma_from_boundary_geometry"] = "OPEN_LOCALIZABLE"
    payload["tau_from_boundary_geometry"] = "OPEN_LOCALIZABLE"
    payload["missing_objects"] = scale_artifact["missing_objects"]
    payload["obstruction"] = scale_artifact["obstruction"]
    payload["official_predictions_changed"] = False
    payload["empirical_derivation_inputs_used"] = False
    payload["observed_masses_used"] = False
    payload["observed_Higgs_used"] = False
    payload["observed_gauge_values_used"] = False
    payload["tau_fit_to_masses"] = False
    payload["sigma_fit_to_masses"] = False
    write_json(path, payload)


def update_numerical_gate_report(path: Path, scale_artifact: dict) -> None:
    payload = load_json(path)
    tau = payload["gates"]["tau_sigma"]
    tau["targeted_followup"] = {
        "sprint": "Boundary/Profile Scale Closure Assault for kappa_H, Z_H, and r",
        "source_artifact": "artifacts/boundary_profile_scale_closure_v1.json",
        "targeted_first_blocker_from_PR_46": True,
        "boundary_profile_scale_closure": scale_artifact["boundary_profile_scale_closure"],
        "r_status": scale_artifact["r"]["status"],
        "Z_H_status": scale_artifact["Z_H"]["status"],
        "kappa_H_status": scale_artifact["kappa_H"]["status"],
        "charged_outputs_at_tau_exported": scale_artifact["charged_outputs_at_tau_exported"],
    }
    tau["status"] = "OPEN_LOCALIZABLE"
    tau["missing_objects"] = scale_artifact["missing_objects"]
    payload["gates"]["charged_outputs_at_tau"]["missing_objects"] = scale_artifact["missing_objects"]
    payload["gates"]["charged_outputs_at_tau"]["status"] = "BLOCKED_BY_TAU_SIGMA_BOUNDARY_DERIVATION"
    payload["promoted_statuses"] = []
    payload["missing_objects"] = _unique_extend(payload["missing_objects"], scale_artifact["missing_objects"])
    payload["public_status_after_sprint"] = closure.PUBLIC_STATUS
    payload["official_predictions_changed"] = False
    payload["empirical_derivation_inputs_used"] = False
    write_json(path, payload)


def update_prediction_package(path: Path, scale_artifact: dict) -> None:
    payload = load_json(path)
    sections = payload["sections"]
    sections["charged_same_sector_ratios"]["status"] = "BLOCKED_BY_TAU_SIGMA_BOUNDARY_DERIVATION"
    sections["charged_same_sector_ratios"]["open_blockers"] = scale_artifact["missing_objects"]
    sections["charged_same_sector_ratios"]["comparison_ready"] = False
    sections["open_boundary_parameters"].update(
        {
            "status": "BLOCKED_BY_MISSING_OBJECTS",
            "source_artifact": "artifacts/boundary_profile_scale_closure_v1.json",
            "uses_empirical_input": False,
            "comparison_ready": False,
            "open_blockers": scale_artifact["missing_objects"],
        }
    )
    payload["package_status"] = "EXPORTED_NOT_COMPARISON_READY"
    payload["official_predictions_changed"] = False
    payload["empirical_derivation_inputs_used"] = False
    write_json(path, payload)


def update_open_gate_ledger(path: Path, scale_artifact: dict) -> None:
    payload = load_json(path)
    payload["statuses"].update(
        {
            "boundary_profile_scale_closure": scale_artifact["boundary_profile_scale_closure"],
            "profile_radius_r": scale_artifact["r"]["status"],
            "Z_H_profile_normalization": scale_artifact["Z_H"]["status"],
            "kappa_H_profile_curvature": scale_artifact["kappa_H"]["status"],
            "sigma_from_boundary_geometry": scale_artifact["sigma_from_boundary_geometry"],
            "tau_from_boundary_geometry": scale_artifact["tau_from_boundary_geometry"],
            "charged_no_fit_outputs": "BLOCKED_BY_TAU_SIGMA_BOUNDARY_DERIVATION",
            "empirical_derivation_inputs_used": False,
            "official_predictions": "UNCHANGED",
        }
    )
    payload["remaining_open_blockers"] = _unique_extend(
        payload["remaining_open_blockers"],
        [
            "internal/profile Berger radius normalization theorem",
            "explicit Phi(y) solution",
            "H_H Higgs saddle Hessian",
            "S_eff^(H) Higgs/profile action",
        ],
    )
    payload["official_predictions_changed"] = False
    write_json(path, payload)


def update_claim_status(path: Path, scale_artifact: dict) -> None:
    payload = load_json(path)
    _append_claim_row(
        payload,
        {
            "claim": "Boundary/profile scale closure",
            "status": scale_artifact["boundary_profile_scale_closure"],
            "boundary": "Targeted PR #46 first blocker; blocked until kappa_H, Z_H, and r are repo-derived.",
        },
    )
    _append_claim_row(
        payload,
        {
            "claim": "Profile radius r",
            "status": scale_artifact["r"]["status"],
            "boundary": "Cosmological radius, heat cutoff, overlap width, collar coordinate, and matching scale are rejected as substitutes.",
        },
    )
    _append_claim_row(
        payload,
        {
            "claim": "Z_H profile normalization",
            "status": scale_artifact["Z_H"]["status"],
            "boundary": "Formula localized as a profile/collar normalization; explicit profile and measure values remain open.",
        },
    )
    _append_claim_row(
        payload,
        {
            "claim": "kappa_H profile curvature",
            "status": scale_artifact["kappa_H"]["status"],
            "boundary": "Formula localized as a Higgs/profile second variation; full action Hessian values remain open.",
        },
    )
    payload["official_predictions_changed"] = False
    write_json(path, payload)


def update_current_status(path: Path, scale_artifact: dict) -> None:
    marker = "## Boundary/Profile Scale Closure Assault"
    text = path.read_text(encoding="utf-8")
    section = f"""
{marker}

This targeted follow-up attacks the first exact blocker from PR #46: `kappa_H`,
`Z_H`, and the internal/profile radius `r`. It does not rerun the broader
numerical gate closure assault and does not use observed masses, Higgs data,
gauge values, target ratios, CKM, PMNS, neutrino data, cosmology residuals, or
DESI residuals as derivation inputs.

Result: `{scale_artifact["boundary_profile_scale_closure"]}`.

- `r`: `{scale_artifact["r"]["status"]}`. The needed object is the
  dimensionless internal/profile Berger radius; cosmological `R_H_Gpc`,
  `Lambda_squared`, `S=1/(4*pi)`, collar `rho`, and matching scales are not
  substitutes.
- `Z_H`: `{scale_artifact["Z_H"]["status"]}`. The profile-normalization formula
  is localized, but the explicit profile, threshold/normalization, measure, and
  collar Jacobian values remain open.
- `kappa_H`: `{scale_artifact["kappa_H"]["status"]}`. The second-variation route
  is localized, but the Higgs/profile action, saddle Hessian, and curvature
  coefficients remain open.

Therefore `sigma` and `tau` remain `OPEN_LOCALIZABLE`, no charged outputs at
boundary tau are exported, and official/frozen predictions remain unchanged.
"""
    if marker in text:
        prefix = text.split(marker, 1)[0].rstrip()
        text = prefix + "\n\n" + section.strip() + "\n"
    else:
        text = text.rstrip() + "\n\n" + section.strip() + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    artifacts = ROOT / "artifacts"
    scale_artifact = closure.build_boundary_profile_scale_closure_artifact(ROOT)
    write_json(artifacts / "boundary_profile_scale_closure_v1.json", scale_artifact)
    write_json(
        artifacts / "radius_symbol_disambiguation_v1.json",
        {
            **{k: scale_artifact[k] for k in closure._guardrails().keys()},
            "artifact": "radius_symbol_disambiguation_v1",
            "radius_disambiguation": scale_artifact["radius_disambiguation"],
            "r_status": scale_artifact["r"]["status"],
            "r_classification": scale_artifact["r"]["classification"],
        },
    )
    write_json(
        artifacts / "Z_H_closure_or_obstruction_v1.json",
        {
            **closure._guardrails(),
            "artifact": "Z_H_closure_or_obstruction_v1",
            "Z_H": scale_artifact["Z_H"],
            "result": scale_artifact["Z_H_result"],
        },
    )
    write_json(
        artifacts / "kappa_H_closure_or_obstruction_v1.json",
        {
            **closure._guardrails(),
            "artifact": "kappa_H_closure_or_obstruction_v1",
            "kappa_H": scale_artifact["kappa_H"],
            "result": scale_artifact["kappa_H_result"],
        },
    )

    update_tau_sigma_artifact(
        artifacts / "tau_sigma_boundary_derivation_closure_or_obstruction_v1.json",
        scale_artifact,
    )
    update_numerical_gate_report(artifacts / "BHSM_numerical_gate_closure_assault_v1.json", scale_artifact)
    update_prediction_package(artifacts / "BHSM_prediction_package_skeleton_v1.json", scale_artifact)
    update_open_gate_ledger(artifacts / "full_BHSM_open_gate_ledger_v2.json", scale_artifact)
    update_claim_status(artifacts / "full_BHSM_claim_status_table_v2.json", scale_artifact)
    update_current_status(ROOT / "docs" / "current_status.md", scale_artifact)


if __name__ == "__main__":
    main()
