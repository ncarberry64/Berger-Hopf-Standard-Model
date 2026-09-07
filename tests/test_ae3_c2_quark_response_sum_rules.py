import hashlib

import pytest

from bhsm.interface.ae3_c2_quark_response_sum_rules import (
    attached_operator_witness,
    claim_boundary,
    quark_response_sum_rule_theorem,
    quark_response_sum_rule_witness,
)
from scripts.materialize_ae3_c2_quark_response_sum_rules import (
    TARGET,
    build_payload,
    main,
)


def test_integer_mode_elimination_gives_exact_up_and_down_response_rules():
    theorem = quark_response_sum_rule_theorem()
    assert theorem["up"]["modes"] == [[0, 0], [6, 0], [10, 1]]
    assert theorem["up"]["K_equals_k_times_k_plus_2"] == [0, 48, 120]
    assert theorem["up"]["q_squared_equals_k_minus_2j_squared"] == [0, 36, 64]
    assert theorem["up"]["primitive_log_coefficients_middle_light"] == [16, -9]
    assert theorem["up"]["primitive_cost_constant"] == -312
    assert theorem["up"]["exact_log_sum_rule"] == (
        "9*log(r_light)-16*log(r_middle)=-78/pi"
    )
    assert theorem["down"]["modes"] == [[0, 0], [6, 3], [8, 2]]
    assert theorem["down"]["K_equals_k_times_k_plus_2"] == [0, 48, 80]
    assert theorem["down"]["q_squared_equals_k_minus_2j_squared"] == [0, 0, 16]
    assert theorem["down"]["primitive_log_coefficients_middle_light"] == [1, 0]
    assert theorem["down"]["primitive_cost_constant"] == 48
    assert theorem["down"]["exact_log_sum_rule"] == "log(r_middle)=-12/pi"
    assert theorem["up"]["Berger_term_cancels_exactly"]
    assert theorem["down"]["Berger_term_cancels_exactly"]


@pytest.mark.parametrize("squashing", [0.4, 0.8, 1.0, 1.157054135733433, 1.7, 3.0])
def test_quark_response_identities_hold_for_every_sampled_positive_squashing(
    squashing,
):
    witness = quark_response_sum_rule_witness(squashing=squashing)
    assert abs(witness["sectors"]["up"]["log_sum_rule_residual"]) < 5.0e-13
    assert abs(
        witness["sectors"]["up"]["multiplicative_sum_rule_residual"]
    ) < 5.0e-13
    assert abs(witness["sectors"]["down"]["log_sum_rule_residual"]) < 5.0e-13
    assert abs(
        witness["sectors"]["down"]["multiplicative_sum_rule_residual"]
    ) < 5.0e-13
    assert not witness["measured_quark_mass_used"]
    assert not witness["quark_Yukawa_operator_used"]


def test_invalid_squashing_is_rejected():
    with pytest.raises(ValueError):
        quark_response_sum_rule_witness(squashing=0.0)


def test_reused_attached_internal_operator_obeys_both_identities():
    witness = attached_operator_witness()
    assert witness["all_attachment_commutators_zero"]
    for sector in ("up", "down"):
        assert witness["comparison"][sector]["maximum_reconstruction_residual"] < 2e-16
        assert abs(witness["comparison"][sector]["log_sum_rule_residual"]) < 5e-13
    assert not witness["response_weights_relabelled_as_quark_masses"]


def test_claim_boundary_stops_at_response_shapes():
    boundary = claim_boundary()
    assert boundary["CURRENT_C2_UP_QUARK_SCALE_FREE_RESPONSE_SUM_RULE_DERIVED"]
    assert boundary["CURRENT_C2_DOWN_QUARK_SCALE_FREE_RESPONSE_SUM_RULE_DERIVED"]
    assert boundary[
        "CURRENT_C2_QUARK_RESPONSE_IDENTITIES_HOLD_FOR_ALL_POSITIVE_SQUASHING"
    ]
    assert not boundary["CURRENT_C2_UP_DOWN_YUKAWA_OPERATORS_DERIVED"]
    assert not boundary["CURRENT_C2_UP_DOWN_ABSOLUTE_YUKAWA_PREFACTORS_DERIVED"]
    assert not boundary["CURRENT_C2_PHYSICAL_QUARK_MASS_RATIOS_DERIVED"]
    assert not boundary["CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED"]
    assert not boundary["CKM_MATRIX_DERIVED"]
    assert not boundary["MEASURED_QUARK_MASS_USED"]
    assert not boundary["particle_spectrum_rebuilt"]


def test_materialized_quark_response_sum_rules_are_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
