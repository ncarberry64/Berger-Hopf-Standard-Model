from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_h_common import guardrails, load_phase_three_h_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_neutrino_basis_scale_resolution_attempt_v1_0.json"


def build_payload() -> dict[str, object]:
    load_phase_three_h_inputs()
    return {
        "artifact": "BHSM_neutrino_basis_scale_resolution_attempt_v1_0",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_H_BOUNDED_BLOCKER_RESOLUTION",
        "blocker_id": "neutrino_basis_and_scale",
        "blocker_name": "neutrino basis and scale convention",
        "prior_status": "OPEN",
        "candidate_basis_convention": "candidate runtime/collider-interface neutrino field labels for PMNS charged current",
        "basis_resolution_status": "PARTIALLY_RESOLVED_FOR_PMNS_CHARGED_CURRENT_TARGET",
        "scale_resolution_status": "OPEN",
        "dirac_majorana_status": "OPEN",
        "source_artifacts_checked": source_artifact_list(),
        "affected_vertex_families": ["lepton_charged_current_PMNS_BH", "neutral_operator_kernel_BH"],
        "promoted_vertex_families": ["lepton_charged_current_PMNS_BH"],
        "still_blocked_vertex_families": ["neutral_operator_kernel_BH"],
        "missing_theorem_if_open": (
            "derive the physical neutrino basis, dimensional scale, and "
            "Dirac/Majorana convention for K_nu from BHSM boundary/operator data"
        ),
        "mass_width_dependency": "OPEN",
        "renormalization_dependency": "OPEN",
        "feynrules_ready": False,
        "ufo_ready": False,
        "notes": (
            "K_nu is a boundary/operator source, not yet a collider neutrino mass matrix. "
            "PMNS charged-current labels can be used only as a candidate runtime interface basis."
        ),
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-H neutrino basis/scale resolution attempt.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

