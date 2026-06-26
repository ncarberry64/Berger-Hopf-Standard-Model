from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_j_common import guardrails, load_phase_three_j_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_bounded_feynrules_prep_lagrangian_v1_2.json"


def term(term_id: str, expression: str, field_requirements: list[str], parameter_requirements: list[str], notes: str) -> dict[str, object]:
    return {
        "term_id": term_id,
        "symbolic_expression": expression,
        "field_requirements": field_requirements,
        "parameter_requirements": parameter_requirements,
        "source_artifacts": source_artifact_list(),
        "runtime_inputs_allowed": True,
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_runtime_inputs": False,
        "translation_status": "FEYNRULES_PREP_CANDIDATE_NOT_FR_FILE",
        "missing_for_feynrules_file": [
            "complete particle class declarations",
            "parameter-card syntax",
            "runtime mass and width assignments",
            "renormalization scheme",
            "FeynRules syntax export",
        ],
        "notes": notes,
    }


def build_payload() -> dict[str, object]:
    load_phase_three_j_inputs()
    return {
        "artifact": "BHSM_bounded_feynrules_prep_lagrangian_v1_2",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_J_MINIMAL_COLLIDER_LAGRANGIAN",
        "model_name": "BHSM_MINIMAL_COLLIDER_INTERFACE_PREP",
        "parameter_mode": "BHSM_COLLIDER_INTERFACE",
        "is_complete_bhsm_model": False,
        "is_feynrules_file": False,
        "is_ufo_model": False,
        "required_statements": [
            "g2_BH_runtime is a runtime/scheme parameter in BHSM_COLLIDER_INTERFACE mode.",
            "Runtime values are simulation/comparison inputs only and do not derive or retune BHSM constants.",
            "V_CKM_BH and U_PMNS_BH are BHSM source matrices from repo artifacts.",
        ],
        "terms": [
            term(
                "L_kin",
                "canonical kinetic terms in the Phase Three-F production basis",
                ["canonical production-basis fields"],
                [],
                "Prep-only kinetic structure in the canonical production basis.",
            ),
            term(
                "L_gauge",
                "standard target gauge convention terms",
                ["W_plus_mu", "W_minus_mu", "standard target gauge fields"],
                ["g2_BH_runtime"],
                "Gauge terms use standard target conventions and scheme/runtime coupling inputs.",
            ),
            term(
                "L_CC_q_BHSM_CKM",
                "(g2_BH_runtime / sqrt(2)) * ubar_i gamma^mu P_L V_CKM_BH[i,j] d_j W_plus_mu + h.c.",
                ["ubar_i", "d_j", "W_plus_mu", "P_L", "gamma^mu"],
                ["g2_BH_runtime", "V_CKM_BH"],
                "V_CKM_BH is a BHSM source matrix; g2_BH_runtime is runtime/scheme input only.",
            ),
            term(
                "L_CC_l_BHSM_PMNS",
                "(g2_BH_runtime / sqrt(2)) * ellbar_i gamma^mu P_L U_PMNS_BH[i,j] nu_j W_minus_mu + h.c.",
                ["ellbar_i", "nu_j", "W_minus_mu", "P_L", "gamma^mu"],
                ["g2_BH_runtime", "U_PMNS_BH", "neutrino_runtime_convention_for_PMNS_labels"],
                "U_PMNS_BH is a BHSM source matrix; neutrino labels are collider-interface labels only.",
            ),
        ],
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-J bounded FeynRules-prep Lagrangian.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

