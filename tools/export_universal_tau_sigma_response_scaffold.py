from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import universal_tau_sigma_response_scaffold as tau_sigma


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _load(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def _append_claim_row(claims: dict, row: dict) -> None:
    existing = {entry["claim"] for entry in claims["claim_statuses"]}
    if row["claim"] not in existing:
        claims["claim_statuses"].append(row)


def main() -> None:
    artifacts = ROOT / "artifacts"
    scaffold = tau_sigma.scaffold_artifact()
    a_local = tau_sigma.response_curve_artifact_from_branch_matrix_artifact(
        _load("charged_branch_matrices_v2_A_local.json")
    )
    a_background = tau_sigma.response_curve_artifact_from_branch_matrix_artifact(
        _load("charged_branch_matrices_v2_A_background_identity.json")
    )
    write_json(artifacts / "universal_tau_sigma_response_scaffold_v1.json", scaffold)
    write_json(artifacts / "tau_response_curves_A_local_v1.json", a_local)
    write_json(artifacts / "tau_response_curves_A_background_identity_v1.json", a_background)

    open_gate_path = artifacts / "full_BHSM_open_gate_ledger_v2.json"
    open_gate = json.loads(open_gate_path.read_text(encoding="utf-8"))
    open_gate["statuses"].update(
        {
            "universal_tau_sigma_scaffold": "IMPLEMENTED_CONDITIONAL",
            "tau_response_curves": "EXPORTED_NO_FIT_DIAGNOSTIC",
            "oriented_jet_heat_response": "STRUCTURALLY_SUPPORTED_CANDIDATE",
            "tau_from_boundary_geometry": "OPEN_LOCALIZABLE",
            "tau_from_mass_fit": "FORBIDDEN",
            "sigma_from_boundary_geometry": "OPEN_LOCALIZABLE",
            "sigma_from_mass_fit": "FORBIDDEN",
            "charged_precision_closure": "OPEN",
            "official_predictions": "UNCHANGED",
        }
    )
    blockers = list(open_gate.get("remaining_open_blockers", []))
    for blocker in ("boundary-derived tau/sigma", "absolute same-sector mass ratios"):
        if blocker not in blockers:
            blockers.append(blocker)
    open_gate["remaining_open_blockers"] = blockers
    write_json(open_gate_path, open_gate)

    claim_path = artifacts / "full_BHSM_claim_status_table_v2.json"
    claims = json.loads(claim_path.read_text(encoding="utf-8"))
    _append_claim_row(
        claims,
        {
            "claim": "Universal tau/sigma finite-width scaffold",
            "status": "IMPLEMENTED_CONDITIONAL",
            "boundary": (
                "Universal tau is frozen as a structural branch variable; "
                "tau/sigma remain boundary-derived/open-localizable and are not fitted."
            ),
        },
    )
    _append_claim_row(
        claims,
        {
            "claim": "Tau response curves",
            "status": "EXPORTED_NO_FIT_DIAGNOSTIC",
            "boundary": "Fixed diagnostic tau grid only; no observed masses or target ratios are used.",
        },
    )
    write_json(claim_path, claims)


if __name__ == "__main__":
    main()
