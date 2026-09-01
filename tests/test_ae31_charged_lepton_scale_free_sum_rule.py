import hashlib

import pytest

from bhsm.interface.ae31_charged_lepton_scale_free_sum_rule import (
    charged_lepton_sum_rule_theorem,
    claim_boundary,
    composed_ae31_operator_witness,
    frozen_reference_diagnostic,
    sum_rule_witness,
)
from scripts.materialize_ae31_charged_lepton_scale_free_sum_rule import (
    TARGET,
    build_payload,
    main,
)


def test_exact_integer_mode_elimination_gives_scale_free_sum_rule():
    theorem = charged_lepton_sum_rule_theorem()
    assert theorem["modes"] == [[0, 0], [5, 2], [9, 3]]
    assert theorem["K_equals_k_times_k_plus_2"] == [0, 35, 99]
    assert theorem["q_squared_equals_k_minus_2j_squared"] == [0, 1, 9]
    assert theorem["Berger_elimination_multiplier"] == 9
    assert theorem["constant_cost_numerator"] == 216
    assert theorem["exact_log_sum_rule"] == (
        "log(m_e/m_tau)=9*log(m_mu/m_tau)+54/pi"
    )


@pytest.mark.parametrize("squashing", [0.5, 0.8, 1.0, 1.157054135733433, 1.4, 2.0])
def test_sum_rule_is_independent_of_Berger_squashing(squashing):
    witness = sum_rule_witness(squashing=squashing)
    assert abs(witness["log_sum_rule_residual"]) < 2.0e-13
    assert abs(witness["multiplicative_sum_rule_residual"]) < 2.0e-13
    assert not witness["measured_lepton_mass_used"]


def test_invalid_squashing_is_rejected():
    with pytest.raises(ValueError):
        sum_rule_witness(squashing=0.0)


def test_composed_ae31_yukawa_operator_obeys_the_identity():
    witness = composed_ae31_operator_witness()
    assert abs(witness["log_sum_rule_residual"]) < 2.0e-13
    assert not witness["squashing_value_used_to_derive_identity"]
    assert not witness["absolute_energy_calibration_used"]
    assert not witness["measured_lepton_mass_used"]


def test_frozen_reference_comparison_is_post_derivation_and_unfitted():
    diagnostic = frozen_reference_diagnostic(
        middle_over_heavy=0.05946353426831603,
        light_over_heavy=0.0002875853753250115,
    )
    assert diagnostic["reference_data_used_only_after_derivation"]
    assert not diagnostic["comparison_is_parameter_fit"]
    assert not diagnostic["dressing_factor_inserted_into_action"]
    assert diagnostic["required_multiplicative_dressing"] == pytest.approx(
        1.0605668991516541
    )


def test_claim_boundary_does_not_promote_global_physical_poles():
    boundary = claim_boundary()
    assert boundary["AE31_CHARGED_LEPTON_SCALE_FREE_MODE_SUM_RULE_DERIVED"]
    assert boundary["ABSOLUTE_UNIT_DEPENDENCE_ELIMINATED_FROM_SUM_RULE"]
    assert boundary["BERGER_SQUASHING_DEPENDENCE_ELIMINATED_FROM_SUM_RULE"]
    assert not boundary["MEASURED_LEPTON_MASS_USED_TO_DERIVE_SUM_RULE"]
    assert not boundary["CURRENT_C2_GLOBAL_PHYSICAL_LEPTON_POLES_DERIVED"]
    assert not boundary["CURRENT_C2_PHYSICAL_MUON_POLE_DERIVED"]
    assert not boundary["MUON_MAGNETIC_MOMENT_DERIVED"]
    assert not boundary["particle_spectrum_rebuilt"]


def test_materialized_sum_rule_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
