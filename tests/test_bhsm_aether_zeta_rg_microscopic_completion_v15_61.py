import math

import pytest

from bhsm.interface import aether_zeta_rg_microscopic_completion_v15_61 as zeta


def test_zeta_scale_law_and_domain():
    assert math.isclose(zeta.zeta_scale_shift(1.0, 2.0), math.log(4.0))
    with pytest.raises(ValueError):
        zeta.zeta_scale_shift(1.0, 0.0)


def test_actual_operator_has_no_hidden_finite_yukawa_block():
    result = zeta.actual_operator_spectral_contract()
    assert result["finite_off_diagonal_Dirac_block"] == "0"
    assert result["inner_fluctuation_contains_Higgs_doublet"] is False
    assert result["Yukawa_entries_generated_by_heat_trace"] is False


def test_one_loop_flow_does_not_preserve_trace_ray_or_select_amplitude():
    result = zeta.one_loop_ray_flow()
    assert result["trace_ray_preserved_by_one_loop_SM_flow"] is False
    assert result["ray_transverse_norm"] > 1e-3
    assert result["nonzero_common_perturbative_fixed_point"] is False
    assert result["matching_amplitude_selected_by_RG_fixed_point"] is False


def test_spectral_candidates_do_not_generate_their_missing_operator_data():
    result = zeta.microscopic_candidate_exhaustion()
    assert result["single_zero-input_candidate_closes_observed_interacting_SM"] is False
    assert "finite_Dirac_data" in result["cutoff_spectral_action"]["requires"]


def test_payload_json_is_deterministic_and_valid():
    payload = zeta.completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["child_matching_scale_selected"]
    assert payload["claim_boundary"]["absolute_M4_normalization_selected"] is False
    assert zeta.deterministic_json(payload) == zeta.deterministic_json(
        zeta.completion_payload()
    )
