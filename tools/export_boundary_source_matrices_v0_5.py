from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from phase_three_c_common import guardrails, load_packet, source_packet_ref, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_boundary_source_matrices_v0_5.json"


def normalize_matrix(matrix_id: str, entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "matrix_id": matrix_id,
        "definition": entry.get("definition"),
        "exact": entry.get("exact", entry.get("matrix")),
        "approx_diagonal": entry.get("approx_diagonal"),
        "matrix": entry.get("matrix"),
        "status": entry.get("status", "DERIVED_FROM_REPO_ARTIFACT"),
        "ufo_ready": False,
        "notes": entry.get("notes", "boundary-source matrix only; not a collider vertex yet"),
        "production_status": "BOUNDARY_SOURCE_MATRIX_ONLY",
    }


def build_payload() -> dict[str, Any]:
    packet = load_packet()
    matrices = packet["boundary_source_matrices"]
    return {
        "artifact": "BHSM_boundary_source_matrices_v0_5",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_C",
        **source_packet_ref(),
        "boundary_source_vertex_matrices_exported": True,
        "not_collider_vertices": True,
        "ufo_ready": False,
        "matrices": [
            normalize_matrix(matrix_id, entry)
            for matrix_id, entry in matrices.items()
        ],
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-C boundary-source matrices.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
