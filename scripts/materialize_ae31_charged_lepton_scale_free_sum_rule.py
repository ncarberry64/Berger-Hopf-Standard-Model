"""Materialize the AE3.1 charged-lepton scale-free mode sum rule."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_charged_lepton_scale_free_sum_rule import (
    ACTION_VERSION,
    CLASSIFICATION,
    charged_lepton_sum_rule_theorem,
    claim_boundary,
    composed_ae31_operator_witness,
    frozen_reference_diagnostic,
    sum_rule_witness,
)


A = ROOT / "artifacts/action_extension"
MASS = A / "BHSM_AE31_C2_INTRINSIC_M4_LEPTON_ACTION.json"
SEMIGROUP = A / "BHSM_AE3_C2_HOPF_SEMIGROUP_TRANSPORT.json"
ONTOLOGY = A / "BHSM_AE3_FAMILY_MASS_ONTOLOGY_RECOVERY_AUDIT.json"
PREDICTION_LEDGER = ROOT / "theory/bhsm_prediction_ledger.json"
TARGET = A / "BHSM_AE31_CHARGED_LEPTON_SCALE_FREE_SUM_RULE.json"
INPUTS = (
    MASS,
    SEMIGROUP,
    ONTOLOGY,
    PREDICTION_LEDGER,
    ROOT / "theory/derived_generation_raw_mode_ledgers.md",
    ROOT / "src/bhsm/interface/ae31_charged_lepton_scale_free_sum_rule.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    normalized = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(normalized).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    mass, semigroup, ontology, prediction_rows = map(_load, INPUTS[:4])
    theorem = charged_lepton_sum_rule_theorem()
    operator_witness = composed_ae31_operator_witness()
    sample_witnesses = [
        sum_rule_witness(squashing=value) for value in (0.8, 1.0, 1.157054135733433, 1.4)
    ]
    prediction_by_id = {row["id"]: row for row in prediction_rows}
    reference_diagnostic = frozen_reference_diagnostic(
        middle_over_heavy=prediction_by_id[
            "mass_ratio.charged_leptons.middle"
        ]["reference"],
        light_over_heavy=prediction_by_id[
            "mass_ratio.charged_leptons.light"
        ]["reference"],
    )
    boundary = claim_boundary()
    tolerance = 2.0e-13
    validation = {
        "same_AE31_composed_lepton_action": (
            mass["action_version"] == ACTION_VERSION
            and mass["claim_boundary"][
                "charged_lepton_M4_semigroup_coupling_action_owned_in_successor"
            ]
            and mass["claim_boundary"][
                "current_C2_local_tangent_frame_tree_poles_derived"
            ]
        ),
        "frozen_mode_ledger_and_semigroup_reused": (
            semigroup["claim_boundary"][
                "frozen_internal_Hopf_response_operator_attached_to_current_C2"
            ]
            and theorem["modes"] == [[0, 0], [5, 2], [9, 3]]
            and theorem["K_equals_k_times_k_plus_2"] == [0, 35, 99]
            and theorem["q_squared_equals_k_minus_2j_squared"] == [0, 1, 9]
        ),
        "exact_integer_elimination_derived": (
            theorem["Berger_elimination_multiplier"] == 9
            and theorem["constant_cost_numerator"] == 216
            and theorem["exact_log_sum_rule"]
            == "log(m_e/m_tau)=9*log(m_mu/m_tau)+54/pi"
        ),
        "identity_holds_across_squashing_samples": all(
            abs(row["log_sum_rule_residual"]) < tolerance
            and abs(row["multiplicative_sum_rule_residual"]) < tolerance
            for row in sample_witnesses
        ),
        "composed_operator_satisfies_identity": abs(
            operator_witness["log_sum_rule_residual"]
        )
        < tolerance,
        "scale_squashing_and_lepton_inputs_absent": (
            theorem["absolute_energy_scale_cancels"]
            and theorem["Higgs_saddle_scale_cancels"]
            and theorem["trace_normalized_Yukawa_prefactor_cancels"]
            and theorem["Berger_squashing_cancels"]
            and theorem["measured_fine_structure_anchor_cancels_with_squashing"]
            and not theorem["measured_lepton_mass_used_to_derive_relation"]
            and not operator_witness["absolute_energy_calibration_used"]
            and not operator_witness["measured_lepton_mass_used"]
        ),
        "frozen_reference_used_only_as_post_derivation_test": (
            reference_diagnostic["reference_data_used_only_after_derivation"]
            and not reference_diagnostic["comparison_is_parameter_fit"]
            and not reference_diagnostic["dressing_factor_inserted_into_action"]
            and reference_diagnostic["required_multiplicative_dressing"] > 1.0
        ),
        "mass_ontology_and_physical_pole_boundary_preserved": (
            ontology["claim_boundary"]["v14_54_mass_ontology_recovered"]
            and not ontology["claim_boundary"][
                "current_C2_parent_relative_energy_evaluated"
            ]
            and not boundary["CURRENT_C2_GLOBAL_PHYSICAL_LEPTON_POLES_DERIVED"]
            and not boundary["CURRENT_C2_PHYSICAL_MUON_POLE_DERIVED"]
        ),
        "no_spectrum_rebuild_or_g_minus_2_overclaim": (
            not boundary["particle_spectrum_rebuilt"]
            and not boundary["MUON_MAGNETIC_MOMENT_DERIVED"]
            and not boundary["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_CHARGED_LEPTON_SCALE_FREE_SUM_RULE",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "sum_rule_theorem": theorem,
        "composed_AE31_operator_witness": operator_witness,
        "frozen_on_shell_reference_diagnostic": reference_diagnostic,
        "squashing_independence_witnesses": sample_witnesses,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 charged-lepton sum rule failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
