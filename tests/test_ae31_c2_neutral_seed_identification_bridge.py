import hashlib

import numpy as np

from bhsm.interface.ae31_c2_neutral_seed_identification_bridge import (
    algebraic_mixing_screen,
    claim_boundary,
    historical_neutral_seed_spectrum,
    historical_shape_channel_decomposition,
    mode_coordinate_identification,
    provenance_and_owner_reconciliation,
)
from scripts.materialize_ae31_c2_neutral_seed_identification_bridge import (
    TARGET,
    build_payload,
    main,
)


def test_current_kj_modes_map_exactly_to_historical_qj_slots():
    result = mode_coordinate_identification()
    assert result["current_neutral_modes"] == [[0, 0], [3, 0], [3, 1]]
    assert result["mapped_historical_modes"] == [[0, 0], [3, 0], [1, 1]]
    assert result["slotwise_identification_exact"]
    assert result["historical_mode_costs"] == [0, 9, 5]
    assert result["mode_costs_recovered"]
    assert not result["new_family_or_particle_ledger_created"]


def test_historical_seed_is_exactly_indefinite_as_written():
    result = historical_neutral_seed_spectrum()
    assert result["determinant"] == "-5/27"
    assert result["leading_2x2_principal_minor"] == "-1/9"
    assert result["one_negative_eigenvalue"]
    assert not result["positive_semidefinite_stiffness"]
    assert np.allclose(
        result["eigenvalues"],
        [-0.036785921979225, 1.6471096522119, 3.056342936434],
        atol=5.0e-14,
        rtol=5.0e-14,
    )
    assert not result["common_shift_action_derived"]


def test_seed_supplies_noncommuting_shape_but_not_physical_oscillation():
    result = algebraic_mixing_screen()
    assert result["noncommuting_family_shape_present"]
    assert result["conditional_canonical_source_conversion_condition_satisfied"]
    assert np.isclose(
        result["commutator_norm_with_canonical_first_slot_source"],
        np.sqrt(2.0) / 3.0,
    )
    assert not result["condition_is_sufficient_for_physical_oscillation"]


def test_seed_decomposes_exactly_on_predeclared_v1455_shape_channels():
    result = historical_shape_channel_decomposition()
    assert result["v14_55_channel_labels"] == [
        "M_(0,0)", "M_(3,0)", "M_(1,1)"
    ]
    assert result["exact_coefficients"] == ["0", "sqrt(2)/3", "sqrt(2)/6"]
    assert result["reconstruction_residual"] < 1.0e-15
    assert result["exact_reconstruction"]
    assert not result["direct_0_2_channel_present"]
    assert not result["channel_amplitudes_action_selected"]


def test_variational_and_lorentzian_ownership_remain_open():
    owner = provenance_and_owner_reconciliation()
    boundary = claim_boundary()
    assert owner["same_current_C2_mode_slots_identified"]
    assert not owner["eta_nu_action_source_derived"]
    assert not owner["beta_nu_action_source_derived"]
    assert not owner["kappa_nu_action_source_derived"]
    assert not owner["historical_seed_promoted_to_current_action_term"]
    assert not boundary["CURRENT_C2_ACTION_OWNED_NEUTRAL_MIXING_KERNEL_DERIVED"]
    assert not boundary["CURRENT_C2_PHYSICAL_PMNS_DERIVED"]


def test_materialized_identification_bridge_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
