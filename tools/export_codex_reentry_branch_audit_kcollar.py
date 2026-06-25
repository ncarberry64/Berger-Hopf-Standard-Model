from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import codex_reentry_branch_audit_kcollar as audit


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
    write_json(
        artifacts / "charged_branch_matrices_v2_A_local.json",
        audit.template_branch_matrix_artifact("A-local"),
    )
    write_json(
        artifacts / "charged_branch_matrices_v2_A_background_identity.json",
        audit.template_branch_matrix_artifact("A-background-identity"),
    )
    write_json(
        artifacts / "charged_branch_matrices_v2_B_diagnostic.json",
        audit.b_diagnostic_branch_matrix_artifact(),
    )
    write_json(
        artifacts / "K_collar_response_audit_A_local_v2.json",
        audit.k_collar_open_audit("A-local", "frozen charged K matrices unavailable"),
    )
    write_json(
        artifacts / "K_collar_response_audit_A_background_identity_v2.json",
        audit.k_collar_open_audit(
            "A-background-identity",
            "A-background charged K matrices unavailable",
        ),
    )
    write_json(artifacts / "full_BHSM_open_gate_ledger_v2.json", audit.open_gate_ledger_artifact())
    write_json(
        artifacts / "full_BHSM_claim_status_table_v2.json",
        audit.claim_status_table_artifact(),
    )
    write_json(
        artifacts / "forbidden_claim_audit_v2.json",
        audit.forbidden_claim_audit_artifact(),
    )


if __name__ == "__main__":
    main()
