"""Materialize the AE3.1 charged-lepton pole-dressing invariant."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_charged_lepton_pole_dressing_invariant import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    common_rescaling_no_go,
    pole_dressing_invariant_theorem,
    reference_pole_dressing_target,
)


A = ROOT / "artifacts/action_extension"
SUM_RULE = A / "BHSM_AE31_CHARGED_LEPTON_SCALE_FREE_SUM_RULE.json"
MASS = A / "BHSM_AE31_C2_INTRINSIC_M4_LEPTON_ACTION.json"
HADAMARD = A / "BHSM_AE31_C2_FERMION_HADAMARD_STATE_CLASS.json"
NONUNIQUENESS = A / "BHSM_AE31_C2_FIXED_HISTORY_STATE_NONUNIQUENESS.json"
PREDICTION_LEDGER = ROOT / "theory/bhsm_prediction_ledger.json"
TARGET = A / "BHSM_AE31_CHARGED_LEPTON_POLE_DRESSING_INVARIANT.json"
INPUTS = (
    SUM_RULE,
    MASS,
    HADAMARD,
    NONUNIQUENESS,
    PREDICTION_LEDGER,
    ROOT / "src/bhsm/interface/ae31_charged_lepton_pole_dressing_invariant.py",
)


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    normalized = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(normalized).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    sum_rule, mass, hadamard, nonuniqueness, prediction_rows = map(
        _load, INPUTS[:5]
    )
    prediction_by_id = {row["id"]: row for row in prediction_rows}
    theorem = pole_dressing_invariant_theorem()
    target = reference_pole_dressing_target(
        middle_over_heavy=prediction_by_id[
            "mass_ratio.charged_leptons.middle"
        ]["reference"],
        light_over_heavy=prediction_by_id[
            "mass_ratio.charged_leptons.light"
        ]["reference"],
    )
    common_witnesses = [
        common_rescaling_no_go(factor=value) for value in (0.25, 1.0, 4.0)
    ]
    boundary = claim_boundary()
    tolerance = 2.0e-13
    validation = {
        "same_AE31_action_and_local_tree_operator_reused": (
            mass["action_version"] == ACTION_VERSION
            and sum_rule["action_version"] == ACTION_VERSION
            and mass["claim_boundary"][
                "current_C2_local_tangent_frame_tree_poles_derived"
            ]
        ),
        "scale_free_tree_identity_reused_not_rebuilt": (
            sum_rule["claim_boundary"][
                "AE31_CHARGED_LEPTON_SCALE_FREE_MODE_SUM_RULE_DERIVED"
            ]
            and sum_rule["sum_rule_theorem"]["Berger_elimination_multiplier"] == 9
            and sum_rule["sum_rule_theorem"]["constant_cost_numerator"] == 216
        ),
        "exact_dressing_combination_derived": (
            theorem["log_dressing_coefficients_heavy_middle_light"]
            == [8.0, -9.0, 1.0]
            and theorem["coefficient_sum"] == 0.0
            and theorem["multiplicative_invariant"]
            == "D=Z_e*Z_tau^8/Z_mu^9=exp(R_pole)"
        ),
        "common_multiplicative_rescaling_no_go_verified": all(
            abs(row["dressing_log_invariant"]) < tolerance
            and abs(
                row["dressed_sum_rule_residual"]
                - row["tree_sum_rule_residual"]
            )
            < tolerance
            and not row["nonzero_residual_repaired"]
            for row in common_witnesses
        ),
        "post_derivation_reference_target_quantified_without_fit": (
            target["reference_data_used_only_after_derivation"]
            and not target["target_inserted_into_action"]
            and not target["representative_is_action_solution"]
            and abs(
                target["effective_dressing_invariant_check"]
                - target["required_multiplicative_dressing_invariant"]
            )
            < tolerance
        ),
        "microscopic_correction_class_not_overclaimed": (
            not theorem["microscopic_self_energy_form_derived"]
            and not theorem["additive_or_nondiagonal_pole_corrections_excluded"]
            and not boundary["ACTION_DERIVED_DRESSED_TWO_POINT_OPERATOR_AVAILABLE"]
            and not boundary["MICROSCOPIC_SELF_ENERGY_OR_RG_FLOW_DERIVED"]
        ),
        "state_and_global_pole_obstructions_preserved": (
            hadamard["claim_boundary"][
                "CURRENT_C2_DRESSED_CHARGED_LEPTON_POLES_DERIVED"
            ]
            is False
            and nonuniqueness["claim_boundary"][
                "CURRENT_C2_ACTION_SELECTED_HADAMARD_STATE_DERIVED"
            ]
            is False
            and not boundary["CURRENT_C2_GLOBAL_PHYSICAL_LEPTON_POLES_DERIVED"]
        ),
        "no_spectrum_rebuild_or_g_minus_2_overclaim": (
            not boundary["particle_spectrum_rebuilt"]
            and not boundary["CURRENT_C2_PHYSICAL_MUON_POLE_DERIVED"]
            and not boundary["MUON_MAGNETIC_MOMENT_DERIVED"]
            and not boundary["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_CHARGED_LEPTON_POLE_DRESSING_INVARIANT",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "pole_dressing_invariant_theorem": theorem,
        "common_multiplicative_rescaling_witnesses": common_witnesses,
        "frozen_on_shell_reference_target": target,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 charged-lepton pole-dressing invariant failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
