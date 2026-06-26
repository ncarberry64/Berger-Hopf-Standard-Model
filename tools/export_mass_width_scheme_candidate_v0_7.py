from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_e_common import guardrails, load_phase_three_inputs, parameter_entries, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_mass_width_scheme_candidate_v0_7.json"


def build_payload() -> dict[str, object]:
    load_phase_three_inputs()
    params = parameter_entries()
    kappa = params.get("kappa_H_BH", {})
    missing = [
        "pole mass convention",
        "running mass convention",
        "decay width convention",
        "neutrino mass convention",
        "reference scale",
        "validated production parameter card",
    ]
    return {
        "artifact": "BHSM_mass_width_scheme_candidate_v0_7",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_E_NORMALIZATION_GAUGE_SCHEME",
        "mass_scheme_status": "STRUCTURAL_CANDIDATE",
        "width_scheme_status": "BLOCKED_BY_MISSING_THEOREM",
        "scalar_profile_mass_status": {
            "status": "STRUCTURAL_CANDIDATE",
            "kappa_H_parameter": "kappa_H_BH",
            "value_exact": kappa.get("value_exact", "64*pi^5"),
            "value_approx": kappa.get("value_approx"),
            "source": kappa.get("source", "canonical_profile_hessian_theorem_v1"),
            "notes": "kappa_H is a BHSM profile Hessian curvature, not automatically a collider Higgs mass.",
        },
        "fermion_mass_status": "BLOCKED_BY_MISSING_THEOREM",
        "gauge_boson_mass_status": "BLOCKED_BY_MISSING_THEOREM",
        "neutrino_mass_status": "BLOCKED_BY_MISSING_THEOREM",
        "decay_width_status": "BLOCKED_BY_MISSING_THEOREM",
        "source_artifacts": source_artifact_list(),
        "missing_items": missing,
        "contains_pdg_masses": False,
        "contains_fake_widths": False,
        "feynrules_ready": False,
        "ufo_ready": False,
        "notes": "No PDG masses, fake collider masses, or fake decay widths are inserted.",
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-E mass-width scheme candidate.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

