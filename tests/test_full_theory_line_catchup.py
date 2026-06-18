from __future__ import annotations

import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_full_theory_line_catchup import (  # noqa: E402
    CKM_1_16_STATUS,
    FACTOR_TAXONOMY_STATUS,
    FULL_THEORY_LINE_STATUS,
    LEPTON_8_9_STATUS,
    LIGHT_UP_SQRT3_STATUS,
    PURE_FIBER_ANTIPODAL_PAIRING_STATUS,
    RESPONSE_SELECTOR_STATUS,
    antipodal_activity_factor,
    antipodal_pairs,
    antipodal_partner,
    audit_payload,
    ckm_23_interface_dimension,
    ckm_23_log_volume_exponent,
    classical_simplex_relative_dimension,
    deck_shift,
    deck_shift_order,
    endH_dimension,
    end_block_dimension,
    export_full_theory_line_outputs,
    factor_response_type,
    geometric_mean_dilution_factor,
    group_algebra_dimension,
    has_antipodal_half_turn,
    independent_antipodal_pair_count,
    is_even_cover,
    is_pure_fiber,
    light_up_projection_candidate,
    log_volume_exponent_from_end_block,
    normalized_amplitude_projection,
    omega_down,
    omega_from_sector_periods,
    omega_lepton,
    omega_up,
    operator_activity_fraction,
    probability_projection,
    pure_fiber_half_pairing_applies,
    q_from_kj,
    traceless_operator_dimension,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_lepton_coherent_endh_arithmetic() -> None:
    assert q_from_kj(5, 2) == 1
    assert q_from_kj(9, 3) == 3
    assert omega_lepton(1, 2) == 3
    assert omega_lepton(3, 3) == 3
    assert group_algebra_dimension(3) == 3
    assert endH_dimension(3) == 9
    assert traceless_operator_dimension(3) == 8
    assert classical_simplex_relative_dimension(3) == 2
    assert operator_activity_fraction(3) == Fraction(8, 9)


def test_action_degree_bridge_arithmetic() -> None:
    assert omega_from_sector_periods(-1, 2, 1, 2) == 3
    assert omega_from_sector_periods(-1, 2, 3, 3) == 3
    assert omega_from_sector_periods(1, -2, 6, 0) == 6
    assert omega_from_sector_periods(1, 4, 0, 3) == 12


def test_pure_fiber_middle_up_half_candidate_arithmetic() -> None:
    assert q_from_kj(6, 0) == 6
    assert omega_up(6, 0) == 6
    assert is_pure_fiber(0) is True
    assert is_even_cover(6) is True
    assert has_antipodal_half_turn(6) is True
    assert antipodal_partner(0, 6) == 3
    assert antipodal_partner(1, 6) == 4
    assert antipodal_partner(2, 6) == 5
    assert antipodal_pairs(6) == ((0, 3), (1, 4), (2, 5))
    assert independent_antipodal_pair_count(6) == 3
    assert antipodal_activity_factor(6) == Fraction(1, 2)
    assert pure_fiber_half_pairing_applies(6, 0, "up") is True


def test_light_up_and_down_guardrails() -> None:
    assert q_from_kj(10, 1) == 8
    assert omega_up(8, 1) == 6
    assert is_pure_fiber(1) is False
    assert pure_fiber_half_pairing_applies(10, 1, "up") is False
    assert math.isclose(normalized_amplitude_projection(3), 1.0 / math.sqrt(3.0))
    assert probability_projection(3) == Fraction(1, 3)

    assert q_from_kj(6, 3) == 0
    assert omega_down(0, 3) == 12
    assert pure_fiber_half_pairing_applies(6, 3, "down") is False
    assert q_from_kj(8, 2) == 4
    assert omega_down(4, 2) == 12
    assert pure_fiber_half_pairing_applies(8, 2, "down") is False


def test_ckm_1_16_candidate_arithmetic() -> None:
    assert ckm_23_interface_dimension() == 4
    assert end_block_dimension(4) == 16
    assert log_volume_exponent_from_end_block(4) == Fraction(1, 16)
    assert ckm_23_log_volume_exponent() == Fraction(1, 16)
    assert math.isclose(
        geometric_mean_dilution_factor(Fraction(1, 2), 4),
        pow(0.5, 1.0 / 16.0),
    )


def test_factor_response_types_are_non_interchangeable() -> None:
    assert factor_response_type("8/9") == "OPERATOR_ACTIVITY_FRACTION"
    assert factor_response_type("1/2") == "PAIR_COUNT_ACTIVITY_REDUCTION"
    assert factor_response_type("1/sqrt(3)") == "COHERENT_AMPLITUDE_PROJECTION"
    assert factor_response_type("1/16") == "END_BLOCK_LOG_VOLUME_DILUTION"
    candidate = light_up_projection_candidate()
    assert candidate["status"] == LIGHT_UP_SQRT3_STATUS
    assert candidate["official_update"] is False


def test_payload_statuses_and_candidate_guards() -> None:
    payload = audit_payload()
    assert payload["full_theory_line_status"] == FULL_THEORY_LINE_STATUS
    assert payload["pure_fiber_antipodal_pairing_status"] == PURE_FIBER_ANTIPODAL_PAIRING_STATUS
    assert payload["response_selector_status"] == RESPONSE_SELECTOR_STATUS
    assert payload["factor_taxonomy_status"] == FACTOR_TAXONOMY_STATUS
    assert payload["lepton_8_9_status"] == LEPTON_8_9_STATUS
    assert payload["light_up_sqrt3_status"] == LIGHT_UP_SQRT3_STATUS
    assert payload["ckm_1_16_status"] == CKM_1_16_STATUS
    assert payload["does_coherent_EndH_give_8_9"] is True
    assert payload["does_up_middle_antipodal_pairing_give_half"] is True
    assert payload["does_light_up_sqrt3_remain_candidate_only"] is True
    assert payload["does_ckm_1_16_remain_candidate_only"] is True
    assert payload["are_factors_marked_non_interchangeable"] is True
    assert payload["does_this_create_new_official_predictions"] is False
    assert payload["does_this_promote_full_bhsm"] is False
    assert payload["does_this_claim_full_standard_model_derivation"] is False


def test_frozen_sanity_and_official_outputs_are_unchanged() -> None:
    payload = audit_payload()
    sanity = payload["frozen_sanity"]
    assert payload["official_outputs_modified"] is False
    assert payload["frozen_predictions_modified"] is False
    assert sanity["BHSM_BARE_V1_unchanged"] is True
    assert sanity["BHSM_DRESSED_V1_CANDIDATE_unchanged"] is True
    assert sanity["dressed_branch_changes_only_c_over_t"] is True
    assert sanity["u_over_t_unchanged"] is True
    assert sanity["ckm_sin_theta_13_unchanged"] is True
    assert sanity["a_unchanged"] is True
    assert sanity["S_unchanged"] is True
    assert sanity["official_branch_comparison"]["no_retuning"] is True


def test_export_writes_reports_without_touching_frozen_predictions() -> None:
    frozen_paths = [
        ROOT / "docs" / "frozen_predictions.md",
        ROOT / "docs" / "frozen_predictions.json",
    ]
    before = {path: _sha(path) for path in frozen_paths}

    export_full_theory_line_outputs(ROOT)

    after = {path: _sha(path) for path in frozen_paths}
    assert before == after

    report_paths = [
        ROOT / "theory" / "full_bhsm_candidate_theory_line.md",
        ROOT / "theory" / "coherent_residue_sheet_channel_theorem.md",
        ROOT / "theory" / "action_to_boundary_phase_map_degree.md",
        ROOT / "theory" / "pure_fiber_even_cover_antipodal_pairing.md",
        ROOT / "theory" / "response_type_factor_taxonomy.md",
        ROOT / "theory" / "factor_guardrails_not_interchangeable.md",
        ROOT / "theory" / "light_up_three_pair_amplitude_projection_candidate.md",
        ROOT / "theory" / "ckm_four_state_interface_log_volume_candidate.md",
        ROOT / "theory" / "full_bhsm_open_blockers.md",
        ROOT / "audits" / "full_theory_line_catchup_audit.md",
        ROOT / "audits" / "full_theory_line_catchup_audit.json",
    ]
    for path in report_paths:
        assert path.exists()

    parsed = json.loads((ROOT / "audits" / "full_theory_line_catchup_audit.json").read_text())
    assert parsed["official_outputs_modified"] is False
    assert parsed["does_this_create_new_official_predictions"] is False
    assert parsed["safe_to_merge_as_candidate_only"] is True


def test_reports_do_not_contain_forbidden_overclaims() -> None:
    export_full_theory_line_outputs(ROOT)
    forbidden = [
        "full standard model derivation claim",
        "standard model replacement claim",
        "completed full bhsm proof claim",
        "official lepton prediction update",
        "official quark prediction update",
        "official u/t correction",
        "official ckm correction",
        "official down-sector dressing update",
        "no-parameter-tuning full-theory claim",
        "ordinary faster-than-light neutrino claim",
        "ordinary environmental mass-drift claim",
        "time-dependent constants as official lab prediction",
        "hidden retuning",
    ]
    paths = [
        ROOT / "theory" / "full_bhsm_candidate_theory_line.md",
        ROOT / "theory" / "response_type_factor_taxonomy.md",
        ROOT / "audits" / "full_theory_line_catchup_audit.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)
    for phrase in forbidden:
        assert phrase not in text
