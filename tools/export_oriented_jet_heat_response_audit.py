from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import oriented_jet_heat_response_audit as jet


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _append_claim_row(claims: dict, row: dict) -> None:
    existing = {entry["claim"] for entry in claims["claim_statuses"]}
    if row["claim"] not in existing:
        claims["claim_statuses"].append(row)


def main() -> None:
    artifacts = ROOT / "artifacts"
    a_local = jet.audit_artifact_from_file(
        artifacts / "charged_branch_matrices_v2_A_local.json"
    )
    a_background = jet.audit_artifact_from_file(
        artifacts / "charged_branch_matrices_v2_A_background_identity.json"
    )
    write_json(artifacts / "oriented_jet_heat_response_audit_A_local_v1.json", a_local)
    write_json(
        artifacts / "oriented_jet_heat_response_audit_A_background_identity_v1.json",
        a_background,
    )

    open_gate_path = artifacts / "full_BHSM_open_gate_ledger_v2.json"
    open_gate = json.loads(open_gate_path.read_text(encoding="utf-8"))
    open_gate["statuses"].update(
        {
            "oriented_jet_heat_response_audit": "RAN",
            "charged_lepton_clean_geometry_gate": "RAN",
            "tau_from_boundary_geometry": "OPEN_LOCALIZABLE",
            "tau_from_mass_fit": "FORBIDDEN",
            "sigma_from_boundary_geometry": "OPEN_LOCALIZABLE",
            "sigma_from_mass_fit": "FORBIDDEN",
            "charged_precision_closure": "OPEN",
            "minimal_diagonal_K_collar_route": "REJECTED_AS_PRIMARY_BY_RESPONSE_AUDIT",
            "oriented_jet_heat_response": a_background["oriented_jet_heat_response"],
            "oriented_jet_heat_stack_verdict": a_background["stack_verdict"],
            "official_predictions": "UNCHANGED",
        }
    )
    blockers = list(open_gate.get("remaining_open_blockers", []))
    blockers = [
        blocker
        for blocker in blockers
        if blocker != "oriented finite-width / jet-heat response audit"
    ]
    for blocker in (
        "boundary-derived tau/sigma",
        "absolute same-sector mass ratios",
        "cross-sector transported mass ratios",
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
            "claim": "Oriented finite-width / jet-heat response",
            "status": a_background["oriented_jet_heat_response"],
            "boundary": (
                "Response-direction audit only; tau/sigma remain boundary-derived/open "
                "and charged numerical closure remains open."
            ),
        },
    )
    _append_claim_row(
        claims,
        {
            "claim": "Charged lepton clean geometry gate",
            "status": "RAN",
            "boundary": "No observed lepton masses or fitted widths are used.",
        },
    )
    write_json(claim_path, claims)


if __name__ == "__main__":
    main()
