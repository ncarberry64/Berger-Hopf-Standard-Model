import numpy as np

from bhsm.interface import aether_m4_completion_nonuniqueness_v15_62 as rank


def test_intrinsic_m4_parameter_rank_survives_family_centrality():
    result = rank.intrinsic_wilson_parameterization()
    assert result["raw_real_dimension"] == 75
    assert result["family_central_real_dimension"] == 11


def test_reset_background_has_zero_coefficient_jacobian():
    jacobian = rank.reset_background_coefficient_jacobian()
    assert jacobian.shape == (11, 11)
    assert np.count_nonzero(jacobian) == 0
    assert np.linalg.matrix_rank(jacobian) == 0


def test_inequivalent_actions_share_the_same_zero_background():
    result = rank.explicit_inequivalent_completion_family()
    assert result["same_background_first_variation"]
    assert result["same_event_invariant_tuple"]
    assert result["different_fluctuation_Hessians_and_scattering"]
    assert result["continuum_cardinality"]


def test_unique_state_does_not_imply_unique_theory():
    result = rank.unique_actualization_distinction()
    assert result["state_level_unique"]
    assert result["theory_level_unique"] is False
    functor = rank.coefficient_functor_requirement()
    assert functor["such_a_map_present_in_current_action"] is False


def test_payload_json_is_deterministic_and_valid():
    payload = rank.completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["theory_level_intrinsic_M4_nonuniqueness_derived"]
    assert rank.deterministic_json(payload) == rank.deterministic_json(
        rank.completion_payload()
    )
