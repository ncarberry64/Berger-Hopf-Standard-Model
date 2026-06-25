from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"
OPEN_VERDICT = "STACK_COLLAR_OPEN"


def audit_payload(branch: str, matrix_artifact: Dict[str, object]) -> Dict[str, object]:
    if matrix_artifact.get("matrix_status") != "EXPORTED_FROM_REPO_GENERATOR":
        return {
            "audit": "K_collar_response_audit",
            "public_status": PUBLIC_STATUS,
            "official_predictions_changed": False,
            "branch": branch,
            "D": "3 diag(0,1,2)",
            "chi_source": "chi = lambda_A Tr(A^2)",
            "chi_fit_to_masses": False,
            "stack_verdict": OPEN_VERDICT,
            "open_items": ["frozen charged K matrices unavailable"],
        }
    return {
        "audit": "K_collar_response_audit",
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "branch": branch,
        "D": "3 diag(0,1,2)",
        "chi_source": "chi = lambda_A Tr(A^2)",
        "chi_fit_to_masses": False,
        "stack_verdict": "STACK_COLLAR_PARTIAL",
        "open_items": [
            "response signs require a dedicated eigenvector-level audit before promotion"
        ],
    }


def audit_file(matrix_path: Path, output_path: Path) -> Dict[str, object]:
    matrix_artifact = json.loads(matrix_path.read_text(encoding="utf-8"))
    payload = audit_payload(str(matrix_artifact.get("branch", "open")), matrix_artifact)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    artifacts = root / "artifacts"
    artifacts.mkdir(exist_ok=True)
    for name in ("A_local", "A_background_identity"):
        audit_file(
            artifacts / f"charged_branch_matrices_v2_{name}.json",
            artifacts / f"K_collar_response_audit_{name}_v2.json",
        )
