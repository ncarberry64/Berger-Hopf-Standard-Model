from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import numpy as np


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"
OPEN_VERDICT = "STACK_COLLAR_OPEN"
PARTIAL_VERDICT = "STACK_COLLAR_PARTIAL"


def _sector_response(matrix: list[list[float]]) -> Dict[str, object]:
    operator = np.array(matrix, dtype=float)
    d_chi = np.diag([0.0, 3.0, 6.0])
    eigenvalues, eigenvectors = np.linalg.eigh(operator)
    derivatives = []
    q_values = []
    for index in range(3):
        vector = eigenvectors[:, index]
        derivative = float(vector.T @ d_chi @ vector)
        derivatives.append(derivative)
        q_values.append(-derivative)
    helps = q_values[0] < q_values[1] < q_values[2]
    compresses = q_values[0] > q_values[1] > q_values[2]
    if helps:
        verdict = "COLLAR_HELPS_HIERARCHY"
    elif compresses:
        verdict = "COLLAR_COMPRESSES_HIERARCHY"
    else:
        verdict = "COLLAR_MIXED_RESPONSE"
    return {
        "eigenvalues": [float(value) for value in eigenvalues],
        "d_lambda_d_chi": derivatives,
        "q_chi": q_values,
        "hierarchy_help_condition_q1_lt_q2_lt_q3": helps,
        "sector_verdict": verdict,
    }


def audit_payload(branch: str, matrix_artifact: Dict[str, object]) -> Dict[str, object]:
    if matrix_artifact.get("matrix_status") not in (
        "EXPORTED_FROM_REPO_GENERATOR",
        "EXPORTED",
    ):
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
    sector_responses = {
        sector: _sector_response(data["K"])
        for sector, data in matrix_artifact["sectors"].items()
    }
    verdicts = {row["sector_verdict"] for row in sector_responses.values()}
    all_help = verdicts == {"COLLAR_HELPS_HIERARCHY"}
    all_compress = verdicts == {"COLLAR_COMPRESSES_HIERARCHY"}
    if all_help:
        stack_verdict = "STACK_COLLAR_SUPPORTED"
    elif all_compress:
        stack_verdict = "STACK_COLLAR_REJECTED_AS_PRIMARY"
    else:
        stack_verdict = PARTIAL_VERDICT
    return {
        "audit": "K_collar_response_audit",
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "branch": branch,
        "D": "3 diag(0,1,2)",
        "chi_source": "chi = lambda_A Tr(A^2)",
        "chi_fit_to_masses": False,
        "stack_verdict": stack_verdict,
        "sector_responses": sector_responses,
        "hierarchy_help_condition": "q_1 < q_2 < q_3",
        "open_items": [
            "chi remains boundary-derived/open; this response audit is structural only",
            "charged precision closure remains open",
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
