from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_l_common import disabled_model_path, guardrails, load_phase_three_l_inputs, model_text, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_feynrules_syntax_contract_v1_4.json"


def build_payload() -> dict[str, object]:
    load_phase_three_l_inputs()
    text = model_text()
    checks = [
        {
            "check_id": "contains_minimal_label",
            "passed": "BHSM_MINIMAL_COLLIDER_INTERFACE" in text,
            "notes": "Model draft must identify the minimal collider-interface scope.",
        },
        {
            "check_id": "contains_not_complete_warning",
            "passed": "This is not the complete BHSM 4D Lagrangian" in text,
            "notes": "Model draft must not be presented as complete BHSM.",
        },
        {
            "check_id": "contains_unresolved_vertices_exclusion_warning",
            "passed": "excludes charged boundary response, neutral kernel, and standalone CP holonomy" in text,
            "notes": "Unresolved vertex families must remain excluded.",
        },
        {
            "check_id": "no_numerical_pdg_mass_markers",
            "passed": all(token not in text for token in ["80.379", "91.1876", "125.10", "172.76"]),
            "notes": "No numerical mass constants are inserted.",
        },
        {
            "check_id": "no_fake_width_markers",
            "passed": all(token not in text.lower() for token in ["fake width", "width ="]),
            "notes": "No fake width assignments are inserted.",
        },
        {
            "check_id": "no_lhe_hepmc_claims",
            "passed": all(token not in text.lower() for token in ["lhe generated", "hepmc generated"]),
            "notes": "Model draft must not claim event generation.",
        },
        {
            "check_id": "no_athena_cmssw_readiness_claims",
            "passed": all(token not in text.lower() for token in ["athena ready", "cmssw ready", "official cern"]),
            "notes": "Model draft must not claim detector-software readiness.",
        },
    ]
    return {
        "artifact": "BHSM_feynrules_syntax_contract_v1_4",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_L_FEYNRULES_SYNTAX_RUNNER",
        "model_file_checked": True,
        "model_file_path": disabled_model_path(),
        "model_file_enabled": False,
        "model_scope": "BHSM_MINIMAL_COLLIDER_INTERFACE_ONLY",
        "is_complete_bhsm_model": False,
        "allowed_vertex_families": [
            "q_charged_current_CKM_BH",
            "lepton_charged_current_PMNS_BH",
        ],
        "excluded_vertex_families": [
            "charged_boundary_response_matrix",
            "neutral_operator_kernel_BH",
            "cp_holonomy_phase_attachment",
        ],
        "allowed_runtime_parameters": [
            "g2_BH_runtime",
            "W_mass_runtime",
            "W_width_runtime",
            "fermion_masses_runtime",
            "fermion_widths_runtime",
            "renormalization_scale_runtime",
        ],
        "forbidden_content": [
            "numerical PDG masses",
            "fake widths",
            "LHE/HepMC readiness claims",
            "Athena/CMSSW readiness claims",
            "standalone unresolved vertices as production vertices",
        ],
        "static_contract_checks": checks,
        "static_contract_passed": all(check["passed"] for check in checks),
        "mathematica_syntax_checked": False,
        "feynrules_load_checked": False,
        "feynrules_lagrangian_checked": False,
        "ufo_export_checked": False,
        "known_limitations": [
            "Static text checks are not FeynRules validation.",
            "Model file remains disabled.",
            "Mathematica/FeynRules has not loaded the model.",
        ],
        "notes": "Static repository contract checks passed only if all textual checks pass; this is not FeynRules validation.",
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-L FeynRules syntax contract.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

