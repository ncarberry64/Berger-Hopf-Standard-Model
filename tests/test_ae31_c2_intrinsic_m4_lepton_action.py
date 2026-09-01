import hashlib

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import (
    ACTION_VERSION,
    action_composition_contract,
    charged_lepton_yukawa_operator,
    claim_boundary,
    conditional_higgs_saddle,
    conditional_tree_mass_operator,
    first_variation_and_pole_gate,
    local_tangent_frame_poles,
)
from scripts.materialize_ae31_c2_intrinsic_m4_lepton_action import (
    TARGET,
    build_payload,
    main,
)


def test_action_composition_is_versioned_and_does_not_double_count():
    result = action_composition_contract()
    assert ACTION_VERSION == "BHSM-AE-3.1.0"
    assert result["predecessor_action_version"] == "BHSM-AE-3.0.0"
    assert not result["independent_Y_e_retained"]
    assert not result["separate_post_EWSB_mass_term_added"]
    assert not result["new_family_coefficient_added_by_transport"]
    assert not result["up_down_Yukawa_terms_added"]


def test_charged_lepton_yukawa_operator_is_noncentral_and_no_fit():
    result = charged_lepton_yukawa_operator()
    values = result["eigenvalues_heavy_middle_light"]
    assert result["Hermitian"]
    assert result["positive_definite"]
    assert result["family_noncentral"]
    assert values[0] > values[1] > values[2]
    assert not result["measured_lepton_mass_used"]
    assert not result["independent_Yukawa_matrix_used"]


def test_conditional_higgs_saddle_uses_no_measured_vev():
    result = conditional_higgs_saddle()
    assert np.isclose(result["v_BH_GeV"], 246.16986520825228, atol=3.0e-13)
    assert not result["measured_Higgs_VEV_used"]
    assert not result["universal_energy_calibration_action_derived"]


def test_action_variation_derives_the_historical_conditional_triplet():
    result = conditional_tree_mass_operator()
    assert np.allclose(
        result["eigenvalues_GeV_heavy_middle_light"],
        [1.758930614523592, 0.10566682607467498, 0.0005229143548875549],
        atol=3.0e-15,
        rtol=2.0e-15,
    )
    assert not result["current_C2_finite_core_poles_evaluated"]
    assert not result["absolute_unit_action_derived"]
    assert not result["measured_lepton_mass_used"]


def test_next_operator_is_the_first_order_chiral_current_c2_block():
    result = first_variation_and_pole_gate()
    assert result["variation_is_family_noncentral"]
    assert not result["same_current_C2_first_order_LR_block_assembled"]
    assert not result["simple_pole_residues_evaluated"]
    assert "CURRENT_C2_FIRST_ORDER_CHIRAL_BLOCK" in result["exact_next_operator"]


def test_local_enclosure_tree_poles_follow_from_the_lorentzian_symbol():
    result = local_tangent_frame_poles()
    assert result["continuous_frequency"]
    assert result["three_distinct_positive_local_mass_shells"]
    assert result["all_energy_poles_simple"]
    assert result["canonical_tree_kinetic_residue_used"]
    assert not result["independent_wavefunction_residue_fitted"]
    assert not result["global_current_C2_Green_function_derived"]
    assert [row["role"] for row in result["rows"]] == [
        "heavy",
        "middle",
        "light",
    ]


def test_claim_boundary_promotes_only_the_successor_action_tree_operator():
    boundary = claim_boundary()
    assert boundary["versioned_successor_action_composed"]
    assert boundary["charged_lepton_family_noncentral_Yukawa_operator_derived"]
    assert boundary["conditional_tree_level_charged_lepton_mass_operator_derived"]
    assert boundary["current_C2_local_tangent_frame_tree_poles_derived"]
    assert boundary[
        "local_enclosure_particle_identification_bridge_closed_conditionally"
    ]
    assert not boundary["current_C2_physical_charged_lepton_poles_derived"]
    assert not boundary["up_down_action_prefactors_derived"]


def test_materialized_ae31_action_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
