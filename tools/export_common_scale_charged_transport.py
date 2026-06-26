from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import common_scale_charged_transport as transport


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _append_claim_row(claims: dict, row: dict) -> None:
    existing = {entry["claim"] for entry in claims["claim_statuses"]}
    if row["claim"] not in existing:
        claims["claim_statuses"].append(row)


def main() -> None:
    artifacts = ROOT / "artifacts"
    write_json(
        artifacts / "common_scale_charged_transport_interface_v1.json",
        transport.transport_interface_artifact(),
    )
    write_json(
        artifacts / "charged_transport_decomposition_template_v1.json",
        transport.build_transport_decomposition_template(),
    )
    write_json(
        artifacts / "common_scale_charged_target_schema_v1.json",
        transport.build_common_scale_target_schema(),
    )
    write_json(
        artifacts / "BHSM_prediction_package_skeleton_v1.json",
        transport.build_prediction_package_skeleton(),
    )

    open_gate_path = artifacts / "full_BHSM_open_gate_ledger_v2.json"
    open_gate = json.loads(open_gate_path.read_text(encoding="utf-8"))
    open_gate["statuses"].update(
        {
            "common_scale_charged_transport_interface": "IMPLEMENTED_CONDITIONAL",
            "charged_transport_decomposition_template": "EXPORTED",
            "common_scale_target_schema": "EXPORTED_EMPTY_COMPARISON_SCHEMA",
            "prediction_package_skeleton": "EXPORTED_NOT_COMPARISON_READY",
            "mixed_pole_running_comparison": "FORBIDDEN",
            "transport_factors_fit_to_residuals": "FORBIDDEN",
            "charged_precision_closure": "OPEN",
            "official_predictions": "UNCHANGED",
        }
    )
    blockers = list(open_gate.get("remaining_open_blockers", []))
    blockers = [
        "numerical residual RG coefficients" if item == "residual RG coefficients" else item
        for item in blockers
    ]
    for blocker in (
        "full scheme/common-scale target population",
        "final populated comparison-ready prediction package",
    ):
        if blocker not in blockers:
            blockers.append(blocker)
    open_gate["remaining_open_blockers"] = blockers
    write_json(open_gate_path, open_gate)

    claim_path = artifacts / "full_BHSM_claim_status_table_v2.json"
    claims = json.loads(claim_path.read_text(encoding="utf-8"))
    _append_claim_row(
        claims,
        {
            "claim": "Common-scale charged transport interface",
            "status": "IMPLEMENTED_CONDITIONAL",
            "boundary": (
                "Defines no-fit transport and common-scale comparison gates; "
                "does not populate empirical targets or close charged precision."
            ),
        },
    )
    _append_claim_row(
        claims,
        {
            "claim": "Comparison-ready prediction package skeleton",
            "status": "EXPORTED_NOT_COMPARISON_READY",
            "boundary": "Skeleton only; target values remain future comparison inputs, not derivation inputs.",
        },
    )
    write_json(claim_path, claims)


if __name__ == "__main__":
    main()
