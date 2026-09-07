import hashlib

import numpy as np

from bhsm.interface.ae31_c2_neutral_semigroup_response_transport import (
    charged_neutral_common_projector_test,
    claim_boundary,
    neutral_current_c2_attachment_certificate,
    neutral_internal_semigroup_shape,
    neutral_mode_ledger,
    propagation_owner_classification,
)
from scripts.materialize_ae31_c2_neutral_semigroup_response_transport import (
    TARGET,
    build_payload,
    main,
)


def test_retained_neutral_mode_ledger_is_reused():
    result = neutral_mode_ledger()
    assert result["left_neutral_modes"] == [[0, 0], [3, 0], [3, 1]]
    assert result["left_right_ledgers_match"]
    assert not result["mode_ledger_rebuilt"]
    assert not result["particle_spectrum_rebuilt"]


def test_neutral_frozen_response_is_noncentral_with_two_gaps():
    result = neutral_internal_semigroup_shape()
    assert np.allclose(
        result["Berger_generator_costs"],
        [0.0, 18.048968457160573, 15.338774273017842],
        atol=2.0e-15,
        rtol=2.0e-15,
    )
    assert np.allclose(
        result["semigroup_weights"],
        [1.0, 0.23780809030574912, 0.295046923299012],
        atol=2.0e-16,
        rtol=2.0e-15,
    )
    assert result["family_noncentral"]
    assert result["two_nonzero_response_gaps"]
    assert result["positive_definite"]
    assert result["contraction"]


def test_common_projector_response_has_no_nontrivial_mixing():
    result = charged_neutral_common_projector_test()
    assert result["charged_neutral_commutator_norm"] == 0.0
    assert result["canonical_first_slot_source_commutator_norm"] == 0.0
    assert result["common_family_projector_algebra"]
    assert not result["canonical_PMNS_nontrivial"]
    assert not result["physical_weak_flavor_to_internal_slot_intertwiner_derived"]


def test_neutral_shape_attaches_over_tested_current_c2_factors_only():
    result = neutral_current_c2_attachment_certificate()
    assert result["all_tested_attachment_commutators_zero"]
    assert result["frozen_response_attached_by_tensor_factorization"]
    assert not result["frozen_response_current_AE31_variational_term"]
    assert not result["commutator_with_full_D_AE2_squared_derived"]
    assert not result["commutator_with_full_gauge_BRST_action_derived"]
    assert not result["physical_rank_three_neutral_subbundle_projector_derived"]


def test_positive_response_is_not_relabelled_as_lorentzian_propagation():
    shape = neutral_internal_semigroup_shape()
    owner = propagation_owner_classification()
    boundary = claim_boundary()
    assert not shape["Lorentzian_unitary_propagation_operator"]
    assert not shape["physical_neutrino_mass_operator"]
    assert not owner["analytic_continuation_or_Lorentzian_owner_derived"]
    assert not owner["response_gaps_can_be_called_Delta_m_squared"]
    assert not boundary[
        "CURRENT_C2_FAMILY_NONCENTRAL_NEUTRAL_PROPAGATION_OPERATOR_DERIVED"
    ]
    assert not boundary["CURRENT_C2_NONTRIVIAL_PMNS_DERIVED"]


def test_materialized_neutral_response_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
