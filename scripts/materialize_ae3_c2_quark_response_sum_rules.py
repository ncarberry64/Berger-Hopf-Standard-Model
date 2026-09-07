"""Materialize the current-C2 quark response sum-rule theorem."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae3_c2_quark_response_sum_rules import (
    ACTION_VERSION,
    CLASSIFICATION,
    attached_operator_witness,
    claim_boundary,
    quark_response_sum_rule_theorem,
    quark_response_sum_rule_witness,
)


A = ROOT / "artifacts/action_extension"
SEMIGROUP = A / "BHSM_AE3_C2_HOPF_SEMIGROUP_TRANSPORT.json"
PULLBACK = A / "BHSM_AE3_FAMILY_HARMONIC_ENERGY_PULLBACK_AUDIT.json"
CHARGED_CURRENT = A / "BHSM_AE31_C2_COEXACT_SU2L_CHARGED_CURRENT.json"
LEPTON_RULE = A / "BHSM_AE31_CHARGED_LEPTON_SCALE_FREE_SUM_RULE.json"
TARGET = A / "BHSM_AE3_C2_QUARK_RESPONSE_SUM_RULES.json"
INPUTS = (
    SEMIGROUP,
    PULLBACK,
    CHARGED_CURRENT,
    LEPTON_RULE,
    ROOT / "theory/derived_generation_raw_mode_ledgers.md",
    ROOT / "src/bhsm/interface/ae3_c2_quark_response_sum_rules.py",
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
    semigroup, pullback, charged_current, lepton_rule = map(_load, INPUTS[:4])
    theorem = quark_response_sum_rule_theorem()
    attachment = attached_operator_witness()
    sample_witnesses = [
        quark_response_sum_rule_witness(squashing=value)
        for value in (0.8, 1.0, 1.157054135733433, 1.4)
    ]
    boundary = claim_boundary()
    tolerance = 5.0e-13
    validation = {
        "frozen_modes_and_current_C2_attachment_reused": (
            semigroup["action_version"] == ACTION_VERSION
            and semigroup["claim_boundary"][
                "frozen_internal_Hopf_response_operator_attached_to_current_C2"
            ]
            and semigroup["claim_boundary"][
                "frozen_mass_ratio_screens_transported_unchanged"
            ]
            and pullback["claim_boundary"][
                "family_noncentral_spectral_stiffness_derived"
            ]
            and pullback["harmonic_spectral_pullback"]["sectors"]["up"]["modes"]
            == [[0, 0], [6, 0], [10, 1]]
            and pullback["harmonic_spectral_pullback"]["sectors"]["down"]["modes"]
            == [[0, 0], [6, 3], [8, 2]]
        ),
        "up_integer_eliminant_exact": (
            theorem["up"]["modes"] == [[0, 0], [6, 0], [10, 1]]
            and theorem["up"]["K_equals_k_times_k_plus_2"] == [0, 48, 120]
            and theorem["up"]["q_squared_equals_k_minus_2j_squared"]
            == [0, 36, 64]
            and theorem["up"]["primitive_log_coefficients_middle_light"]
            == [16, -9]
            and theorem["up"]["primitive_cost_constant"] == -312
            and theorem["up"]["Berger_term_cancels_exactly"]
        ),
        "down_integer_eliminant_exact": (
            theorem["down"]["modes"] == [[0, 0], [6, 3], [8, 2]]
            and theorem["down"]["K_equals_k_times_k_plus_2"] == [0, 48, 80]
            and theorem["down"]["q_squared_equals_k_minus_2j_squared"]
            == [0, 0, 16]
            and theorem["down"]["primitive_log_coefficients_middle_light"]
            == [1, 0]
            and theorem["down"]["primitive_cost_constant"] == 48
            and theorem["down"]["Berger_term_cancels_exactly"]
        ),
        "identities_hold_across_positive_squashing_samples": all(
            abs(row["sectors"][sector]["log_sum_rule_residual"]) < tolerance
            and abs(
                row["sectors"][sector]["multiplicative_sum_rule_residual"]
            )
            < tolerance
            for row in sample_witnesses
            for sector in ("up", "down")
        ),
        "attached_operator_satisfies_both_identities": (
            attachment["all_attachment_commutators_zero"]
            and all(
                row["maximum_reconstruction_residual"] < 2.0e-16
                and abs(row["log_sum_rule_residual"]) < tolerance
                for row in attachment["comparison"].values()
            )
            and not attachment["response_weights_relabelled_as_quark_masses"]
        ),
        "lepton_rule_consistency_without_rederivation": (
            lepton_rule["sum_rule_theorem"]["modes"]
            == [[0, 0], [5, 2], [9, 3]]
            and lepton_rule["claim_boundary"][
                "AE31_CHARGED_LEPTON_SCALE_FREE_MODE_SUM_RULE_DERIVED"
            ]
        ),
        "quark_action_and_CKM_boundary_preserved": (
            not charged_current["claim_boundary"][
                "up_down_absolute_Yukawa_prefactors_derived"
            ]
            and not charged_current["claim_boundary"]["physical_CKM_matrix_derived"]
            and not boundary["CURRENT_C2_UP_DOWN_YUKAWA_OPERATORS_DERIVED"]
            and not boundary["CURRENT_C2_PHYSICAL_QUARK_MASS_RATIOS_DERIVED"]
            and not boundary["CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED"]
        ),
        "no_mass_input_spectrum_rebuild_or_completion_overclaim": (
            not theorem["measured_quark_mass_used"]
            and not theorem["quark_Yukawa_operator_used"]
            and not boundary["MEASURED_QUARK_MASS_USED"]
            and not boundary["particle_spectrum_rebuilt"]
            and not boundary["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_AE3_C2_QUARK_RESPONSE_SUM_RULES",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "quark_response_sum_rule_theorem": theorem,
        "attached_frozen_internal_operator_witness": attachment,
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
        raise SystemExit("current-C2 quark response sum rules failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
