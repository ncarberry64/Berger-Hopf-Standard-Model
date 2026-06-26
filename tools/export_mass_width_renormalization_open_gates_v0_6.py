from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_d_common import guardrails, phase_three_c_inputs, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_mass_width_renormalization_open_gates_v0_6.json"


GATES = [
    "pole_mass_scheme",
    "running_mass_scheme",
    "decay_width_scheme",
    "gauge_boson_width_scheme",
    "fermion_width_scheme",
    "higgs_width_scheme",
    "neutrino_mass_scheme",
    "reference_scale",
    "gauge_coupling_scheme",
    "yukawa_scheme",
    "threshold_scheme",
    "counterterm_scheme",
    "running_scheme",
    "PDG_target_table",
    "MadGraph_validation",
]


def build_payload() -> dict[str, object]:
    phase_three_c_inputs()
    entries = [
        {
            "gate_id": gate,
            "status": "OPEN",
            "required_for": ["FeynRules", "UFO", "MadGraph"],
            "current_BHSM_source": "candidate/internal source only" if gate not in {"PDG_target_table", "MadGraph_validation"} else None,
            "missing_item": gate,
            "blocks_feynrules": True,
            "blocks_ufo": True,
            "blocks_madgraph": True,
            "notes": "No fake masses, widths, PDG targets, or validation outputs are inserted.",
        }
        for gate in GATES
    ]
    return {
        "artifact": "BHSM_mass_width_renormalization_open_gates_v0_6",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_D",
        "mass_width_scheme_complete": False,
        "renormalization_scheme_complete": False,
        "entries": entries,
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-D mass-width/renormalization open gates.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
