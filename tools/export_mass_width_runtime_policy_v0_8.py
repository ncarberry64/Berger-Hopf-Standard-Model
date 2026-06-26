from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_f_common import guardrails, load_phase_three_f_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_mass_width_runtime_policy_v0_8.json"


def build_payload() -> dict[str, object]:
    load_phase_three_f_inputs()
    return {
        "artifact": "BHSM_mass_width_runtime_policy_v0_8",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_F_PRODUCTION_BASIS_RUNTIME_PARAMS",
        "policy_name": "BHSM_MASS_WIDTH_RUNTIME_POLICY",
        "pure_no_fit_mass_width_status": "OPEN_NO_EXTERNAL_RUNTIME_INPUTS",
        "collider_interface_mass_width_status": "RUNTIME_INPUTS_ALLOWED_FOR_COMPARISON_ONLY",
        "allowed_runtime_mass_width_inputs": [
            "external mass cards for simulation/comparison",
            "external width cards for simulation/comparison",
            "detector/event runtime cards",
        ],
        "forbidden_derivation_uses": [
            "derive BHSM constants",
            "retune boundary coefficients",
            "modify mixing matrices",
            "modify frozen predictions",
        ],
        "kappa_H_policy": (
            "kappa_H = 64*pi^5 is a BHSM profile Hessian curvature, not "
            "automatically a collider Higgs mass."
        ),
        "fermion_mass_policy": "BHSM_PURE_NOFIT remains open; collider interface may accept runtime values only.",
        "gauge_boson_mass_policy": "BHSM_PURE_NOFIT remains open; collider interface may accept runtime values only.",
        "neutrino_mass_policy": "BHSM_PURE_NOFIT remains open; neutrino basis and mass convention remain open.",
        "width_policy": "No no-fit width scheme is complete; runtime widths are comparison inputs only.",
        "pdg_target_policy": "No PDG values are inserted into BHSM derivation artifacts.",
        "event_generation_policy": (
            "A production UFO may require runtime mass/width cards for practical "
            "event generation, but those cards are not derivation inputs."
        ),
        "contains_fake_masses": False,
        "contains_fake_widths": False,
        "source_artifacts": source_artifact_list(),
        "notes": (
            "BHSM_PURE_NOFIT does not import PDG masses or widths. "
            "BHSM_COLLIDER_INTERFACE may accept external mass/width cards as "
            "runtime simulation inputs only. Runtime inputs do not modify BHSM "
            "constants, boundary coefficients, mixing matrices, or frozen predictions."
        ),
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-F mass-width runtime policy.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

