from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_e_common import guardrails, load_phase_three_inputs, parameter_entries, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_gauge_fixing_production_coupling_scheme_v0_7.json"


def coupling_entry(parameter: str, entries: dict[str, dict[str, object]]) -> dict[str, object]:
    source = entries[parameter]
    return {
        "parameter": parameter,
        "value_exact": source["value_exact"],
        "value_approx": source["value_approx"],
        "source": source["source"],
        "status": "SCHEME_CONDITIONAL",
        "production_ready": False,
        "requires": [
            "reference scale",
            "normalization convention",
            "threshold/running scheme",
            "renormalization scheme",
        ],
    }


def build_payload() -> dict[str, object]:
    load_phase_three_inputs()
    params = parameter_entries()
    return {
        "artifact": "BHSM_gauge_fixing_production_coupling_scheme_v0_7",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_E_NORMALIZATION_GAUGE_SCHEME",
        "target_gauge_group": "SU(3)c x SU(2)L x U(1)Y",
        "canonical_vector_kinetic_terms": True,
        "canonical_vector_kinetic_terms_status": "STANDARD_HEP_TARGET_CONVENTION",
        "gauge_fixing_status": "OPEN_OR_TARGET_CONVENTION_ONLY",
        "production_coupling_status": "SCHEME_CONDITIONAL",
        "candidate_couplings": [
            coupling_entry("g1_BH_candidate", params),
            coupling_entry("g2_BH_candidate", params),
            coupling_entry("g3_BH_candidate", params),
        ],
        "missing_for_production_couplings": [
            "reference scale",
            "normalization convention",
            "threshold/running scheme",
            "renormalization scheme",
            "gauge fixing convention",
            "validated production parameter card",
        ],
        "source_artifacts": source_artifact_list(),
        "feynrules_ready": False,
        "ufo_ready": False,
        "notes": (
            "Gauge coupling candidates are imported from existing BHSM artifacts "
            "as scheme-conditional interface candidates. They are not final UFO "
            "production couplings."
        ),
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-E gauge fixing/coupling scheme status.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

