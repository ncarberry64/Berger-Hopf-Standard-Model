from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import numerical_gate_closure_assault as assault


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _append_claim_row(claims: dict, row: dict) -> None:
    existing = {entry["claim"] for entry in claims["claim_statuses"]}
    if row["claim"] not in existing:
        claims["claim_statuses"].append(row)


def main() -> None:
    artifacts = ROOT / "artifacts"
    gates = assault.build_gate_artifacts(ROOT)
    report = assault.central_report(ROOT)
    write_json(artifacts / "tau_sigma_boundary_derivation_closure_or_obstruction_v1.json", gates["tau_sigma"])
    write_json(artifacts / "common_scale_transport_closure_or_obstruction_v1.json", gates["common_scale_transport"])
    write_json(artifacts / "neutral_parameter_closure_or_obstruction_v1.json", gates["neutral_parameters"])
    write_json(artifacts / "PMNS_obstruction_v1.json", gates["PMNS"])
    write_json(artifacts / "CKM_obstruction_v1.json", gates["CKM"])
    write_json(artifacts / "CP_obstruction_v1.json", gates["CP"])
    write_json(artifacts / "Higgs_EW_closure_or_obstruction_v1.json", gates["Higgs_EW"])
    write_json(artifacts / "hyperspherical_cosmology_desi_pipeline_v1.json", gates["cosmology_DESI"])
    write_json(artifacts / "BHSM_numerical_gate_closure_assault_v1.json", report)

    package_path = artifacts / "BHSM_prediction_package_skeleton_v1.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    write_json(package_path, assault.update_prediction_package(package, gates))

    open_gate_path = artifacts / "full_BHSM_open_gate_ledger_v2.json"
    open_gate = json.loads(open_gate_path.read_text(encoding="utf-8"))
    open_gate["statuses"].update(
        {
            "numerical_gate_closure_assault": "RAN",
            "tau_sigma_gate": gates["tau_sigma"]["status"],
            "charged_no_fit_outputs": gates["charged_outputs_at_tau"]["status"],
            "common_scale_transport_population": gates["common_scale_transport"]["status"],
            "neutral_parameter_derivation": gates["neutral_parameters"]["neutral_parameter_final_derivation"],
            "PMNS_numerical_output": gates["PMNS"]["status"],
            "CKM_numerical_output": gates["CKM"]["status"],
            "CP_numerical_output": gates["CP"]["status"],
            "Higgs_EW_closure": gates["Higgs_EW"]["status"],
            "cosmology_DESI_pipeline": gates["cosmology_DESI"]["status"],
            "empirical_derivation_inputs_used": False,
            "official_predictions": "UNCHANGED",
        }
    )
    open_gate["remaining_open_blockers"] = report["missing_objects"]
    write_json(open_gate_path, open_gate)

    claim_path = artifacts / "full_BHSM_claim_status_table_v2.json"
    claims = json.loads(claim_path.read_text(encoding="utf-8"))
    _append_claim_row(
        claims,
        {
            "claim": "Numerical gate closure assault",
            "status": "RAN_WITH_EXACT_OBSTRUCTIONS",
            "boundary": "No gate was promoted without repo-derived source objects; empirical derivation inputs were not used.",
        },
    )
    _append_claim_row(
        claims,
        {
            "claim": "Tau/sigma numerical boundary derivation",
            "status": gates["tau_sigma"]["status"],
            "boundary": "Blocked until kappa_H, Z_H, and r are repo-derived.",
        },
    )
    write_json(claim_path, claims)


if __name__ == "__main__":
    main()
