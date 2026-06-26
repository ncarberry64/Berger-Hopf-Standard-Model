from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_ufo_phase_three_readiness_v0_3.json"


def exists(relative: str) -> bool:
    return (ROOT / relative).exists()


def load_or_empty(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    gate = load_or_empty("artifacts/BHSM_feynrules_translation_gate_v0_3.json")
    remaining = list(gate.get("blockers", []))
    if not remaining:
        remaining = [
            "production UFO model not exported",
            "MadGraph load validation not performed",
            "LHE/HepMC generation not enabled",
            "Athena/CMSSW integration not present",
        ]
    return {
        "artifact": "BHSM_ufo_phase_three_readiness_v0_3",
        "release_basis": "v1.0.1",
        "complete_4d_lagrangian_exported": False,
        "effective_lagrangian_candidate_exported": exists("artifacts/BHSM_effective_lagrangian_candidate_v0_3.json"),
        "field_normalization_ledger_exported": exists("artifacts/BHSM_field_normalization_ledger_v0_3.json"),
        "vertex_normalization_ledger_exported": exists("artifacts/BHSM_vertex_normalization_ledger_v0_3.json"),
        "mass_width_scheme_status_exported": exists("artifacts/BHSM_mass_width_scheme_status_v0_3.json"),
        "renormalization_scheme_status_exported": exists("artifacts/BHSM_renormalization_scheme_status_v0_3.json"),
        "feynrules_translation_gate_exported": exists("artifacts/BHSM_feynrules_translation_gate_v0_3.json"),
        "production_ufo_model_exported": False,
        "loadable_ufo_model": False,
        "madgraph_ready": False,
        "lhe_generation_ready": False,
        "hepmc_generation_ready": False,
        "athena_ready": False,
        "cmssw_ready": False,
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
        "source_model_files_changed": False,
        "remaining_blockers": remaining,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BHSM Phase Three-A UFO readiness.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
