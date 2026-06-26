from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_parameter_card_export_v0_2.json"


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def entry(name: str, symbol: str, value: Any, source: str, notes: str) -> dict[str, Any]:
    return {
        "parameter_name": name,
        "symbol": symbol,
        "value": value,
        "unit": "BHSM_internal_units",
        "scheme": "BHSM_boundary_no_fit",
        "scale": "mu_BH_boundary",
        "source_artifact": source,
        "source_status": "EXPORTED_INTERNAL_BHSM_ARTIFACT",
        "is_fitted_to_empirical_data": False,
        "ufo_ready": False,
        "missing_for_ufo": [
            "complete collider-ready 4D Lagrangian",
            "field normalization convention",
            "vertex normalization convention",
            "mass/width parameter-card convention",
        ],
        "notes": notes,
    }


def build_entries() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    profile = load("artifacts/profile_scale_closure_values_v1.json")
    for key in ("tau", "sigma", "Z_H", "kappa_H", "r_internal_profile", "r_squared"):
        if key in profile:
            entries.append(entry(key, key, profile[key], "artifacts/profile_scale_closure_values_v1.json", "Profile-scale closure export."))

    charged = load("artifacts/charged_boundary_bridge_values_v1.json")
    for sector, values in charged.get("sectors", {}).items():
        for key in ("beta", "kappa", "beta_tau", "kappa_tau"):
            if key in values:
                entries.append(
                    entry(
                        f"{key}_{sector}",
                        f"{key}_{sector}",
                        values[key],
                        "artifacts/charged_boundary_bridge_values_v1.json",
                        f"Charged boundary bridge value for {sector}.",
                    )
                )

    neutral = load("artifacts/neutral_operator_no_fit_output_v1.json")
    for key in ("eta_nu", "g_nu", "beta_nu", "kappa_nu"):
        if key in neutral:
            entries.append(entry(key, key, neutral[key], "artifacts/neutral_operator_no_fit_output_v1.json", "Neutral operator no-fit output."))

    ckm = load("artifacts/CKM_no_fit_operator_output_v1.json")
    for key, value in ckm.get("angles", {}).items():
        entries.append(entry(key, key, value, "artifacts/CKM_no_fit_operator_output_v1.json", "CKM boundary no-fit angle/source value."))
    if "J_CKM_BH" in ckm:
        entries.append(entry("J_CKM_BH", "J_CKM_BH", ckm["J_CKM_BH"], "artifacts/CKM_no_fit_operator_output_v1.json", "CKM Jarlskog-like boundary output."))

    pmns = load("artifacts/PMNS_no_fit_operator_output_v1.json")
    for key in ("theta12_nu", "theta23_nu", "theta13_nu", "delta_BH", "J_PMNS_BH"):
        if key in pmns:
            entries.append(entry(key, key, pmns[key], "artifacts/PMNS_no_fit_operator_output_v1.json", "PMNS boundary no-fit output."))

    cp = load("artifacts/CP_no_fit_holonomy_output_v1.json")
    if "delta_BH" in cp:
        entries.append(entry("delta_BH_CP", "delta_BH", cp["delta_BH"], "artifacts/CP_no_fit_holonomy_output_v1.json", "CP boundary holonomy output."))

    transport = load("artifacts/common_scale_boundary_transport_v1.json")
    if "T_total(mu_BH_boundary -> mu_BH_boundary)" in transport:
        entries.append(
            entry(
                "boundary_transport_identity",
                "T_boundary_to_boundary",
                transport["T_total(mu_BH_boundary -> mu_BH_boundary)"],
                "artifacts/common_scale_boundary_transport_v1.json",
                "Boundary-scale identity transport.",
            )
        )
    return entries


def build_payload() -> dict[str, object]:
    return {
        "artifact": "BHSM_parameter_card_export_v0_2",
        "release_basis": "v1.0.1",
        "parameter_card_complete_for_ufo": False,
        "entries": build_entries(),
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM phase-two parameter-card source ledger.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
