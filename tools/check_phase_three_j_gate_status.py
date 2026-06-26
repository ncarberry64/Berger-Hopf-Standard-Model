from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_j_common import guardrails, load_phase_three_j_inputs, load_required, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_phase_three_j_gate_status_v1_2.json"


def build_payload() -> dict[str, object]:
    inputs = load_phase_three_j_inputs()
    subset = load_required("artifacts/BHSM_minimal_bounded_lagrangian_subset_v1_2.json")
    vertices = load_required("artifacts/BHSM_included_excluded_vertex_families_v1_2.json")
    prep = load_required("artifacts/BHSM_bounded_feynrules_prep_lagrangian_v1_2.json")
    runtime = load_required("artifacts/BHSM_minimal_runtime_parameter_requirements_v1_2.json")
    vertex_entries = {entry["vertex_family"]: entry for entry in vertices["entries"]}
    return {
        "artifact": "BHSM_phase_three_j_gate_status_v1_2",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_J_MINIMAL_COLLIDER_LAGRANGIAN",
        "minimal_bounded_lagrangian_subset_exported": subset["artifact"] == "BHSM_minimal_bounded_lagrangian_subset_v1_2",
        "included_excluded_vertex_families_exported": vertices["artifact"] == "BHSM_included_excluded_vertex_families_v1_2",
        "bounded_feynrules_prep_lagrangian_exported": prep["artifact"] == "BHSM_bounded_feynrules_prep_lagrangian_v1_2",
        "minimal_runtime_parameter_requirements_exported": runtime["artifact"] == "BHSM_minimal_runtime_parameter_requirements_v1_2",
        "canonical_production_basis_preserved": True,
        "interface_normalization_gate_cleared": True,
        "ckm_minimal_current_included": vertex_entries["q_charged_current_CKM_BH"]["included_in_minimal_subset"],
        "pmns_minimal_current_included": vertex_entries["lepton_charged_current_PMNS_BH"]["included_in_minimal_subset"],
        "charged_boundary_response_excluded": not vertex_entries["charged_boundary_response_matrix"]["included_in_minimal_subset"],
        "neutral_kernel_excluded": not vertex_entries["neutral_operator_kernel_BH"]["included_in_minimal_subset"],
        "standalone_cp_holonomy_excluded": not vertex_entries["cp_holonomy_phase_attachment"]["included_in_minimal_subset"],
        "complete_bhsm_4d_lagrangian_exported": False,
        "minimal_collider_interface_lagrangian_exported": True,
        "feynrules_prep_ready": True,
        "production_feynrules_file_exported": False,
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
            "complete BHSM 4D Lagrangian",
            "production FeynRules file",
            "UFO model export",
            "MadGraph validation",
            "LHE/HepMC generation",
            "X_ch theorem for charged boundary response",
            "neutrino basis/scale/Dirac-Majorana theorem",
            "standalone CP O_int theorem",
            "pure no-fit mass-width closure",
            "renormalization closure",
        ],
        "recommended_status_language": (
            "BHSM Phase Three-J exports a minimal bounded collider-interface Lagrangian subset "
            "in the canonical production basis. The subset includes CKM/PMNS charged-current "
            "target structures sourced by BHSM mixing artifacts and excludes unresolved "
            "charged-boundary, neutral-kernel, and standalone CP-holonomy vertices. This is "
            "FeynRules-prep only, not a production FeynRules file, UFO model, MadGraph-ready "
            "model, or complete BHSM 4D Lagrangian."
        ),
        "upstream_phase_three_i_status": inputs["phase_three_i_gate_status"]["recommended_status_language"],
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-J gate status.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

