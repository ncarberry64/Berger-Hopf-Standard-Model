from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_k_common import guardrails, load_required, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_software_track_readiness_gates_v1_3.json"


def gate(gate_id: str, status: str, support: list[str], blocks_next_step: bool, missing_item: str, notes: str) -> dict[str, object]:
    return {
        "gate_id": gate_id,
        "status": status,
        "artifact_support": support,
        "blocks_next_step": blocks_next_step,
        "missing_item": missing_item,
        "notes": notes,
    }


def build_payload() -> dict[str, object]:
    load_required("artifacts/BHSM_minimal_feynrules_model_export_attempt_v1_3.json")
    load_required("artifacts/BHSM_feynrules_to_ufo_export_contract_v1_3.json")
    load_required("artifacts/BHSM_madgraph_smoke_test_plan_v1_3.json")
    return {
        "artifact": "BHSM_software_track_readiness_gates_v1_3",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_K_FEYNRULES_EXPORT_ATTEMPT",
        "gates": [
            gate(
                "bounded_feynrules_model_file",
                "DISABLED_DRAFT_EXPORTED",
                ["models/feynrules/BHSM_Minimal_Collider_Interface.fr.disabled"],
                True,
                "enabled validated .fr model file",
                "A disabled bounded draft exists; it is not a production FeynRules file.",
            ),
            gate(
                "feynrules_syntax_validation",
                "NOT_VALIDATED",
                ["artifacts/BHSM_minimal_feynrules_model_export_attempt_v1_3.json"],
                True,
                "Mathematica/FeynRules syntax validation",
                "No FeynRules validation was run.",
            ),
            gate(
                "ufo_export",
                "NOT_ATTEMPTED",
                ["artifacts/BHSM_feynrules_to_ufo_export_contract_v1_3.json"],
                True,
                "enabled validated .fr model and FeynRules runtime",
                "UFO export is a future contract only.",
            ),
            gate(
                "ufo_loadability",
                "NOT_TESTED",
                ["artifacts/BHSM_feynrules_to_ufo_export_contract_v1_3.json"],
                True,
                "generated UFO model",
                "No UFO model exists to load.",
            ),
            gate(
                "madgraph_import",
                "NOT_ATTEMPTED",
                ["artifacts/BHSM_madgraph_smoke_test_plan_v1_3.json"],
                True,
                "loadable UFO model and MadGraph runtime",
                "MadGraph import is planned only.",
            ),
            gate(
                "madgraph_smoke_process",
                "PLANNED_NOT_ATTEMPTED",
                ["artifacts/BHSM_madgraph_smoke_test_plan_v1_3.json"],
                True,
                "loadable UFO model, parameter card, and MadGraph runtime",
                "Minimal processes are planned but not executed.",
            ),
            gate(
                "lhe_generation",
                "NOT_READY",
                ["artifacts/BHSM_madgraph_smoke_test_plan_v1_3.json"],
                True,
                "passing MadGraph smoke test",
                "No event files are generated.",
            ),
            gate(
                "hepmc_generation",
                "NOT_READY",
                ["artifacts/BHSM_madgraph_smoke_test_plan_v1_3.json"],
                True,
                "passing event generation and shower/conversion path",
                "No event files are generated.",
            ),
            gate(
                "athena_boundary",
                "NOT_READY",
                ["artifacts/BHSM_phase_three_k_gate_status_v1_3.json"],
                True,
                "validated event generation and detector-interface package",
                "No Athena readiness is claimed.",
            ),
            gate(
                "cmssw_boundary",
                "NOT_READY",
                ["artifacts/BHSM_phase_three_k_gate_status_v1_3.json"],
                True,
                "validated event generation and detector-interface package",
                "No CMSSW readiness is claimed.",
            ),
        ],
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-K software-track readiness gates.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

