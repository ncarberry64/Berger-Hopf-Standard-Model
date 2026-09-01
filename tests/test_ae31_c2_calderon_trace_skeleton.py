import hashlib

import numpy as np
import pytest

from bhsm.interface.ae31_c2_calderon_trace_skeleton import (
    claim_boundary,
    exact_remaining_owner,
    orthogonal_graph_projector,
    physical_outer_calderon_contract,
    reset_transmission_complex,
    transmission_is_not_outer_calderon,
)
from scripts.materialize_ae31_c2_calderon_trace_skeleton import (
    TARGET,
    build_payload,
    main,
)


def test_unitary_graph_projector_is_exact_and_half_rank():
    lift = np.asarray(((0.0, 1.0), (-1.0, 0.0)), dtype=complex)
    result = orthogonal_graph_projector(lift)
    assert result["Hermitian_residual"] < 1.0e-12
    assert result["idempotence_residual"] < 1.0e-12
    assert result["graph_fixing_residual"] < 1.0e-12
    assert result["half_rank"]
    with pytest.raises(ValueError):
        orthogonal_graph_projector(np.asarray(((1.0, 1.0), (0.0, 1.0))))


def test_combined_trace_skeleton_closes_all_reset_graphs():
    result = reset_transmission_complex()
    assert result["all_Hermitian"]
    assert result["all_idempotent"]
    assert result["all_fix_the_reset_graph"]
    assert result["all_half_rank"]
    assert result["BRST_constraint_and_ghost_reset_matched"]
    assert not result["new_boundary_parameter"]


def test_transmission_graph_is_not_misidentified_as_physical_projector():
    result = transmission_is_not_outer_calderon()
    assert not result["same_object"]
    assert not result["reset_graph_repairs_gauge_residue"]
    assert result["reset_graph_preserves_Hadamard_covariance_continuum"]
    assert not result["reset_graph_selects_positive_frequency_covariance"]
    assert not result["reset_graph_fixes_finite_scalar_determinant"]


def test_one_missing_outer_operator_has_three_typed_outputs():
    result = physical_outer_calderon_contract()
    assert len(result["source_trace_space"]) == 4
    assert result["required_delta_Zt_minus_delta_Zs"] > 0.0
    assert result["one_operator_would_close_three_dependencies"]
    assert not result["current_N3_gauge_spinor_ghost_projector_present"]
    assert not result["operator_constructed_here"]


def test_claim_boundary_and_materialization_are_conservative():
    claims = claim_boundary()
    assert claims["CURRENT_C2_RESET_CALDERON_TRACE_SKELETON_DERIVED"]
    assert claims["RESET_TRANSMISSION_NOT_PHYSICAL_OUTER_CALDERON_DERIVED"]
    assert not claims["CURRENT_C2_PHYSICAL_GAUGE_SPINOR_GHOST_CALDERON_PROJECTOR_DERIVED"]
    assert not claims["MUON_MAGNETIC_MOMENT_DERIVED"]
    assert not exact_remaining_owner()["archived_Wentzell_matrix_may_be_inserted"]
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
