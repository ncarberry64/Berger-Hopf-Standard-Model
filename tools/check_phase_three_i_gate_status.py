from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_i_common import guardrails, load_phase_three_i_inputs, load_required, runtime_policy_defined, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_phase_three_i_gate_status_v1_1.json"


def build_payload() -> dict[str, object]:
    inputs = load_phase_three_i_inputs()
    x_ch = load_required("artifacts/BHSM_x_ch_charged_boundary_response_theorem_v1_1.json")
    neutrino = load_required("artifacts/BHSM_neutrino_dirac_majorana_basis_scale_theorem_v1_1.json")
    cp = load_required("artifacts/BHSM_cp_holonomy_o_int_attachment_theorem_v1_1.json")
    load_required("artifacts/BHSM_interaction_theorem_closure_audit_v1_1.json")
    return {
        "artifact": "BHSM_phase_three_i_gate_status_v1_1",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_I_INTERACTION_THEOREM_CLOSURE",
        "x_ch_theorem_exported": True,
        "neutrino_dirac_majorana_theorem_exported": True,
        "cp_o_int_theorem_exported": True,
        "interaction_theorem_closure_audit_exported": True,
        "x_ch_theorem_status": "OPEN_EXACT_MISSING_THEOREM_FOR_BOUNDARY_RESPONSE",
        "neutrino_basis_status": neutrino["basis_status"],
        "neutrino_scale_status": neutrino["scale_status"],
        "dirac_majorana_status": neutrino["dirac_majorana_status"],
        "cp_o_int_status": "OPEN_EXACT_MISSING_THEOREM_FOR_STANDALONE_VERTEX",
        "ckm_pmns_mediator_status": "STANDARD_TARGET_CONVENTION_FOR_CHARGED_CURRENT_ONLY",
        "ckm_pmns_cp_attachment_status": "PARTIALLY_RESOLVED_THROUGH_MIXING_SOURCES",
        "charged_boundary_response_promoted": x_ch["promotes_charged_boundary_response"],
        "neutral_kernel_promoted": neutrino["promotes_neutral_kernel"],
        "standalone_cp_holonomy_vertex_promoted": cp["promotes_standalone_cp_vertex"],
        "any_new_vertex_promoted_to_feynrules_ready": False,
        "complete_4d_lagrangian_exported": False,
        "production_vertex_table_complete": False,
        "mass_width_scheme_complete_for_pure_no_fit": False,
        "runtime_mass_width_policy_defined": runtime_policy_defined(inputs),
        "renormalization_scheme_complete": False,
        "feynrules_ready": False,
        "ufo_ready": False,
        "madgraph_ready": False,
        "lhe_generation_ready": False,
        "hepmc_generation_ready": False,
        "athena_ready": False,
        "cmssw_ready": False,
        "empirical_derivation_inputs_used": False,
        "empirical_runtime_inputs_allowed_in_collider_mode": True,
        "boundary_predictions_modified_by_runtime_inputs": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
        "source_model_files_changed": False,
        "remaining_blockers": [
            "X_ch theorem assigning the separate charged boundary response a production interaction operator",
            "neutrino physical basis, dimensional scale, and Dirac/Majorana theorem",
            "standalone CP holonomy interaction operator O_int",
            "complete 4D Lagrangian",
            "production vertex table",
            "mass-width closure for BHSM_PURE_NOFIT",
            "renormalization closure",
            "FeynRules/UFO/MadGraph/LHE/HepMC/Athena/CMSSW readiness",
        ],
        "recommended_status_language": (
            "BHSM Phase Three-I performs direct interaction-theorem closure attempts for X_ch, "
            "neutrino Dirac-Majorana basis/scale, and standalone CP O_int attachment. The sprint "
            "distinguishes already-supported CKM/PMNS target-current attachments from the still-open "
            "standalone boundary-response, neutral-kernel, and CP-holonomy interaction theorems. "
            "This is not complete 4D Lagrangian export or production FeynRules/UFO readiness."
        ),
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-I gate status.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

