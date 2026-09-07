import hashlib

import numpy as np

from bhsm.interface.ae31_c2_coexact_su2l_charged_current import (
    canonical_quark_family_kernel,
    claim_boundary,
    lowest_weyl_coexact_su2l_charged_source_jets,
    weak_charged_representation_ledger,
)
from scripts.materialize_ae31_c2_coexact_su2l_charged_current import (
    TARGET,
    build_payload,
    main,
)


def test_weak_raising_lowering_representation_and_trace():
    result = weak_charged_representation_ledger()
    assert result["T_minus_is_T_plus_adjoint"]
    assert result["one_family_trace_Tminus_Tplus"] == 4.0
    assert result["three_family_trace_Tminus_Tplus"] == 12.0
    assert result["family_action"] == "I3"
    assert not result["independent_family_matrix_inserted"]


def test_coexact_charged_coordinates_are_hermitian_and_equally_normalized():
    result = lowest_weyl_coexact_su2l_charged_source_jets(
        proper_durations=np.asarray([0.2, 0.3]),
        inverse_radii=np.asarray([1.0, 1.1]),
        source_profile=np.ones(2),
        chirality=1,
    )
    for key in ("W1_vertex_elements", "W2_vertex_elements"):
        values = result[key]
        assert np.allclose(values, values.conjugate().transpose(0, 2, 1))
    assert result["equal_coordinate_normalization_inherited"]
    assert not result["new_g2_or_source_coefficient_added"]


def test_current_family_identity_forces_canonical_response_no_mixing():
    result = canonical_quark_family_kernel()
    assert result["kernel_rank"] == 3
    assert result["kernel_unitary"]
    assert result["response_commutator_norm"] == 0.0
    assert result["canonical_response_basis_Jarlskog"] == 0.0
    assert not result["nontrivial_CKM_generated_by_current_family_identity"]
    assert not result["middle_up_half_dressing_inserted"]
    assert not result["physical_CKM_matrix_derived"]


def test_claim_boundary_promotes_current_but_not_physical_ckm_or_w_pole():
    boundary = claim_boundary()
    assert boundary["current_C2_coexact_SU2L_charged_source_pair_derived"]
    assert boundary["current_C2_SU2L_raising_current_family_kernel_is_I3"]
    assert not boundary["present_action_nontrivial_CKM_derived"]
    assert not boundary["physical_CKM_matrix_derived"]
    assert not boundary["physical_W_pole_derived"]


def test_materialized_charged_current_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
