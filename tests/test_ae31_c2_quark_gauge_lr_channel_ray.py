import hashlib

from bhsm.interface.ae31_c2_quark_gauge_lr_channel_ray import (
    channel_direction_effect,
    claim_boundary,
    current_c2_transport_contract,
    exact_group_factor_ray,
    exact_remaining_owner,
    family_and_higgs_boundary,
)
from scripts.materialize_ae31_c2_quark_gauge_lr_channel_ray import TARGET, build_payload, main


def test_exact_group_factor_ray():
    ray = exact_group_factor_ray()
    assert ray["pre_Fierz_weights"] == {"up": "7/5", "down": "13/10"}
    assert ray["C_up_minus_C_down"] == "1/10"
    assert ray["C_up_over_C_down"] == "14/13"
    assert not ray["measured_quark_mass_used"]


def test_transport_is_relative_not_local_Maxwell_promotion():
    theorem = current_c2_transport_contract()
    assert not theorem["absolute_G_C2_evaluated_here"]
    assert not theorem["local_Lorentzian_Maxwell_residue_required_for_relative_ray"]
    assert not theorem["Lorentzian_Maxwell_mismatch_overridden"]
    assert not theorem["nonlocal_static_kernel_relabelled_as_local_photon_exchange"]


def test_unequal_diagonal_ray_breaks_O2_but_selects_no_mixture():
    effect = channel_direction_effect()
    assert effect["eigenvalue_splitting"] > 0
    assert effect["isolated_O2_quark_plane_degeneracy_broken"]
    assert effect["largest_attraction_axis"] == "up"
    assert not effect["mixed_up_down_eigendirection_selected"]
    assert not effect["c_up_over_c_down_Yukawa_residue_derived"]


def test_family_and_higgs_boundaries_remain_open():
    boundary = family_and_higgs_boundary()
    assert not boundary["family_hierarchy_generated"]
    assert not boundary["CKM_generated"]
    assert not boundary["single_intrinsic_Higgs_direction_selected"]
    owner = exact_remaining_owner()
    assert not owner["group_factor_ratio_may_be_called_Yukawa_ratio"]
    claims = claim_boundary()
    assert claims["CURRENT_C2_QUARK_GAUGE_LR_RELATIVE_CHANNEL_RAY_DERIVED"]
    assert not claims["CURRENT_C2_UP_DOWN_RELATIVE_YUKAWA_RESIDUE_DERIVED"]


def test_materialized_channel_ray_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
