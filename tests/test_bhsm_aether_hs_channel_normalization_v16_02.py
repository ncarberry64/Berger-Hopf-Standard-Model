import math

from bhsm.interface.aether_hs_channel_normalization_v16_02 import (
    broken_branch_dimension_contract,
    hs_channel_normalization,
    u1_dense_repair_fraction,
)


RESPONSE = {
    "HS_delta_Z_seed": 0.06270987557020812,
    "U1_delta_K_magnetic_seed": 6.125407687280419,
    "U1_delta_K_electric_seed": -0.03006315191481446,
}

DENSE = {
    "proper_cycle_K_magnetic": 809.858537429679,
    "proper_cycle_K_electric": 2514.195062100584,
}


def test_hs_normalization_is_a_channel_matrix_not_one_mode_number():
    result = hs_channel_normalization(RESPONSE)
    assert result["pairing_multiplicity_matrix"] == "D=diag(9,9,3,3)"
    assert math.isclose(
        result["canonical_Y_if_channels_are_independent"]["up"],
        6.521032979481711,
    )
    assert math.isclose(
        result["canonical_Y_if_channels_are_independent"]["charged_lepton"],
        11.29476043829458,
    )
    assert result["physical_direction_selected"] is False


def test_u1_matter_hs_response_has_repair_sign_but_is_too_small():
    result = u1_dense_repair_fraction(RESPONSE, DENSE)
    assert result["sign_reduces_classical_mismatch"]
    assert result["fraction_of_required_U1_repair"] < 0.01
    assert result["U1_matter_HS_block_alone_repairs_cone"] is False


def test_broken_branch_is_only_entered_after_hessian_crossing():
    result = broken_branch_dimension_contract(24)
    assert result["symmetric_replacement_KKT_dimension"] == 314
    assert result["broken-neutral-channel_KKT_dimension"] == 410
    assert result["single_Higgs_direction_assumed_before_Hessian"] is False
