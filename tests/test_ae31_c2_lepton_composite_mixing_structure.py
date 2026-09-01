import hashlib

import numpy as np

from bhsm.interface.ae31_c2_lepton_composite_mixing_structure import (
    claim_boundary,
    exact_remaining_owner,
    nonzero_gauge_hs_channel_extension,
    one_loop_mixing_factorization,
    shared_charged_lepton_vertex_jet,
    species_block_selection_theorem,
)
from scripts.materialize_ae31_c2_lepton_composite_mixing_structure import (
    TARGET,
    build_payload,
    main,
)


def test_nonzero_gauge_channels_include_charged_lepton_not_neutrino():
    result = nonzero_gauge_hs_channel_extension()
    assert result["bare_inverse_coefficients_over_G_C2"] == {
        "up": "5/14",
        "down": "5/13",
        "charged_lepton": "5/3",
    }
    assert not result["neutrino_zero_kernel_HS_inverse_defined"]
    assert not result["new_continuous_coefficient"]


def test_shared_lepton_vertex_jet_is_odd_and_cross_contact_closes():
    result = shared_charged_lepton_vertex_jet()
    assert result["intrinsic_grading_residual"] == 0.0
    assert result["auxiliary_grading_residual"] == 0.0
    assert result["first_order_mixed_contact"] == 0.0
    assert result["squared_pencil_cross_contact_residual"] < 1.0e-14
    assert np.asarray(result["squared_pencil_mixed_contact"]).shape == (6, 6)
    assert not result["measured_lepton_mass_used"]


def test_hadamard_mixing_direction_reuses_family_noncentral_yukawa():
    result = one_loop_mixing_factorization()
    assert result["Y_l_family_noncentral"]
    assert result["universal_pole_family_direction_action_derived"]
    assert not result["finite_chi_f_selected"]
    assert not result["full_numeric_mixing_matrix_derived"]


def test_species_pattern_excludes_vector_gauge_link_on_symmetric_background():
    result = species_block_selection_theorem()
    assert result["intrinsic_to_charged_lepton_composite_shared_species"]
    assert result["direct_one_fermion_loop_intrinsic_quark_mixing_zero"]
    assert result["vector_gauge_vertices_preserve_chirality_and_species"]
    assert result["all_orders_vector_gauge_mixing_zero_at_chirally_symmetric_quark_background"]
    assert not result["nonperturbative_chirality_violating_topological_vertex_excluded"]
    owner = exact_remaining_owner()
    assert not owner["one_loop_zero_replaced_by_fitted_mixing"]


def test_claim_boundary_and_materialization_are_conservative():
    claims = claim_boundary()
    assert claims["CURRENT_C2_INTRINSIC_LEPTON_COMPOSITE_VERTEX_JET_DERIVED"]
    assert claims["CURRENT_C2_LEPTON_COMPOSITE_HADAMARD_POLE_DIRECTION_DERIVED"]
    assert claims["CURRENT_C2_VECTOR_GAUGE_INTRINSIC_QUARK_MIXING_EXCLUDED_ON_SYMMETRIC_BACKGROUND"]
    assert not claims["CURRENT_C2_COMMON_PARENT_ODD_QUARK_ENDOMORPHISM_DERIVED"]
    assert not claims["CURRENT_C2_PHYSICAL_SINGLE_HIGGS_DIRECTION_SELECTED"]
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
