from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_g_common import guardrails, load_required, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_vertex_readiness_matrix_v0_9.json"


def row(vertex: dict[str, object]) -> dict[str, object]:
    family = str(vertex["vertex_family"])
    return {
        "vertex_family": family,
        "field_dictionary_ready": "partial",
        "canonical_basis_ready": True,
        "lorentz_structure_ready": vertex["lorentz_structure_status"] == "STANDARD_HEP_TARGET_CONVENTION",
        "gauge_structure_ready": "partial" if family in {"q_charged_current_CKM_BH", "lepton_charged_current_PMNS_BH"} else False,
        "coupling_ready": False,
        "mixing_or_matrix_ready": family in {"q_charged_current_CKM_BH", "lepton_charged_current_PMNS_BH", "charged_boundary_response_matrix", "neutral_operator_kernel_BH", "cp_holonomy_phase_attachment"},
        "mass_width_ready": False,
        "renormalization_ready": False,
        "runtime_parameter_policy_ready": True,
        "feynrules_ready": False,
        "ufo_ready": False,
        "madgraph_ready": False,
        "blocking_items": vertex["missing_for_feynrules"],
    }


def build_payload() -> dict[str, object]:
    vertices = load_required("artifacts/BHSM_production_vertex_table_candidate_v0_9.json")
    return {
        "artifact": "BHSM_vertex_readiness_matrix_v0_9",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_G_VERTEX_TABLE_LAGRANGIAN_CANDIDATE",
        "vertex_readiness_matrix_exported": True,
        "rows": [row(entry) for entry in vertices["entries"]],
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-G vertex readiness matrix.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

