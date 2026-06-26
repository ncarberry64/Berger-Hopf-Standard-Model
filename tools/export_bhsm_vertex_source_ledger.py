from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_vertex_source_ledger_v0_2.json"


SOURCES = [
    ("charged_boundary_response", "charged_boundary_response", "artifacts/charged_boundary_bridge_values_v1.json"),
    ("neutral_operator_kernel", "neutral_operator_kernel", "artifacts/neutral_operator_no_fit_output_v1.json"),
    ("ckm_mixing_source", "ckm_mixing_source", "artifacts/CKM_no_fit_operator_output_v1.json"),
    ("pmns_mixing_source", "pmns_mixing_source", "artifacts/PMNS_no_fit_operator_output_v1.json"),
    ("cp_holonomy_source", "cp_holonomy_source", "artifacts/CP_no_fit_holonomy_output_v1.json"),
    ("boundary_transport_identity", "boundary_transport_identity", "artifacts/common_scale_boundary_transport_v1.json"),
]


def build_entries() -> list[dict[str, object]]:
    entries = []
    for source_id, family, artifact in SOURCES:
        entries.append(
            {
                "vertex_source_id": source_id,
                "candidate_interaction_family": family,
                "source_artifact": artifact,
                "source_status": "SYMBOLIC_MAPPING_ONLY",
                "candidate_fields": [],
                "lorentz_structure": None,
                "coupling_symbol": None,
                "coupling_value": None,
                "normalization_status": "MISSING_4D_VERTEX_NORMALIZATION",
                "ufo_ready": False,
                "missing_for_feynman_rule": [
                    "complete 4D Lorentz structure",
                    "gauge-fixed interaction term",
                    "field normalization",
                    "vertex normalization",
                ],
                "missing_for_ufo": [
                    "Feynman rule",
                    "UFO Lorentz object",
                    "UFO coupling object",
                    "validated model directory",
                ],
                "notes": "Source category only; no Feynman rule is exported.",
            }
        )
    return entries


def build_payload() -> dict[str, object]:
    return {
        "artifact": "BHSM_vertex_source_ledger_v0_2",
        "release_basis": "v1.0.1",
        "source_ledger_only": True,
        "feynman_rules_exported": False,
        "entries": build_entries(),
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM phase-two vertex source ledger.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
