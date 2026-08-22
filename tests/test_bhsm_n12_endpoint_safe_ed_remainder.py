import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_ENDPOINT_SAFE_ED_REMAINDER.json"
)


def test_endpoint_safe_ed_remainder_fails_closed_on_pole_rows():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    pole = payload["exact_round_pole_zero_order_matrix"]
    assert pole["rank"] == 2
    assert pole["Berger_b_diagonal_entry"] == 12
    assert pole[
        "remaining_critical_conformal_line_proved_absent_after_source_normal_compression"
    ] is False
    assert "ALL_DERIVATIVE_VELOCITY" in payload["principal_blocks_retained"]
    assert payload[
        "remaining_principal_or_weighted_H2_indicial_row_count"
    ] >= 0
    for sector in payload["sectors"].values():
        assert sector["interior_interval_matrix_enclosure_completed"] is True
        assert sector["direct_compact_matrix_enclosure"]["C_ED_G_upper"] > 0.0
        assert (
            sector["direct_omega_multiplier_count"]
            + sector["principal_or_weighted_H2_indicial_count"]
            == sector["coefficient_count"]
        )
    assert payload["epsilon_obs_M_evaluable"] is False
    assert payload["direct_C_ED_G_enclosure_complete"] is True
    assert payload["fixed_ball_state_variation_modulus_complete"] is True
    assert (
        payload["joint_fixed_ball_C_ED_G_variation_upper"]
        == 2.0 * payload["joint_direct_C_ED_G_upper"]
    )
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
