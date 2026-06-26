from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import codex_reentry_branch_audit_kcollar as audit
import charged_branch_matrix_export as branch_export
import bhsm_k_collar_response_audit as collar_audit


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def current_branch() -> str:
    return subprocess.check_output(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        text=True,
    ).strip()


def main() -> None:
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    codex_root = ROOT.parent
    branch = current_branch()

    recovery = audit.recovery_report_artifact(
        codex_root=codex_root,
        repo_root=ROOT,
        repo_branch_at_start="bhsm-incidence-normalized-overlap-bridge-source-v1",
        repo_branch_used=branch,
    )
    write_json(artifacts / "bhsm_codex_reentry_recovery_report_v1.json", recovery)
    (artifacts / "bhsm_codex_reentry_recovery_report_v1.md").write_text(
        audit.render_recovery_markdown(recovery),
        encoding="utf-8",
    )

    write_json(
        artifacts / "charged_generator_branch_inspection_v2.json",
        audit.generator_inspection_artifact(ROOT),
    )
    write_json(artifacts / "frozen_constants_v2.json", audit.frozen_constants_artifact())
    a_local = branch_export.branch_artifact("A-local")
    a_background = branch_export.branch_artifact("A-background-identity")
    b_diagnostic = branch_export.branch_artifact("B-diagnostic")
    write_json(artifacts / "charged_branch_matrices_v2_A_local.json", a_local)
    write_json(artifacts / "charged_branch_matrices_v2_A_background_identity.json", a_background)
    write_json(artifacts / "charged_branch_matrices_v2_B_diagnostic.json", b_diagnostic)
    write_json(
        artifacts / "K_collar_response_audit_A_local_v2.json",
        collar_audit.audit_payload("A-local", a_local),
    )
    write_json(
        artifacts / "K_collar_response_audit_A_background_identity_v2.json",
        collar_audit.audit_payload("A-background-identity", a_background),
    )

    open_gate = audit.open_gate_ledger_artifact()
    open_gate["statuses"].update(
        {
            "A_local_branch_matrix_export": "EXPORTED",
            "A_background_identity_branch": "IMPLEMENTED_CONDITIONAL",
            "A_background_dependency_order": "VERIFIED",
            "K_collar_response_audit": "RAN",
        }
    )
    write_json(artifacts / "full_BHSM_open_gate_ledger_v2.json", open_gate)

    claims = audit.claim_status_table_artifact()
    claims["claim_statuses"].extend(
        [
            {
                "claim": "A-local charged branch matrix export",
                "status": "EXPORTED",
                "boundary": "Local action-unit branch only; not numerical closure.",
            },
            {
                "claim": "A-background identity charged branch",
                "status": "IMPLEMENTED_CONDITIONAL",
                "boundary": "Identity collar dependency order is implemented; anisotropic chi remains open.",
            },
        ]
    )
    write_json(artifacts / "full_BHSM_claim_status_table_v2.json", claims)
    write_json(
        artifacts / "a_background_collar_dependency_order_v1.json",
        branch_export.status_artifact(),
    )
    write_json(
        artifacts / "forbidden_claim_audit_v2.json",
        audit.forbidden_claim_audit_artifact(),
    )


if __name__ == "__main__":
    main()
