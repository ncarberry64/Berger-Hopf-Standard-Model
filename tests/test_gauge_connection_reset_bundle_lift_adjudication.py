from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

from bhsm.interface.gauge_connection_reset_bundle_lift_adjudication import (
    EXACT_MISSING_DATUM,
    STATUS,
    claim_boundary,
    conditional_geometry_checks,
    connection_pullback_residual,
    connection_reset_linearization,
    downstream_status,
    induced_connection_transport,
    local_one_jet_nonuniqueness_witness,
    ownership_levels,
    source_lineage_ledger,
    weighted_cotangent_momentum_map,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_gauge_connection_reset_bundle_lift_adjudication.py"


def _materializer():
    spec = importlib.util.spec_from_file_location("gauge_reset_materializer", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_three_ownership_levels_are_not_conflated() -> None:
    levels = ownership_levels()
    assert levels["bundle_isomorphism_class"]["status"] == "EXISTS"
    assert levels["actual_equivariant_bundle_morphism"]["status"] == (
        "EXISTS_ABSTRACTLY_ON_THE_AE2_BOUNDARY_BUNDLE"
    )
    actual = levels["actual_equivariant_bundle_morphism"]
    assert actual["smooth"] is True
    assert actual["principal_bundle_local_representative_evaluable"] is False
    assert actual["vertical_first_derivative_dg_B_evaluable"] is False
    assert actual["base_tangent_DF_B_evaluable"] is False
    assert levels["induced_connection_transport"]["configuration_map"] is None


def test_conditional_connection_law_satisfies_repository_pullback_equation() -> None:
    lift = np.eye(2, dtype=complex)
    tangent = np.asarray(((2.0, 0.0), (0.0, 0.5)))
    event = np.asarray((1.0j * np.eye(2), 2.0j * np.eye(2)))
    derivative = np.asarray((0.25j * lift, -0.5j * lift))
    child = induced_connection_transport(event, tangent, lift, derivative)
    assert connection_pullback_residual(
        event, child, tangent, lift, derivative
    ) < 1.0e-12
    assert np.linalg.norm(child) > 0.0


def test_connection_law_is_affine_and_linearization_excludes_dg_term() -> None:
    root = 1.0 / np.sqrt(2.0)
    lift = root * np.asarray(((1.0, 1.0j), (1.0j, 1.0)), dtype=complex)
    tangent = np.asarray([[2.0]])
    derivative = np.asarray([0.25j * lift])
    zero = np.zeros((1, 2, 2), dtype=complex)
    first = np.asarray([((0.0j, 2.0j), (2.0j, 0.0j))])
    child_zero = induced_connection_transport(zero, tangent, lift, derivative)
    child_first = induced_connection_transport(first, tangent, lift, derivative)
    linearization = connection_reset_linearization(tangent, lift)
    delta = (child_first - child_zero).reshape(-1)
    assert np.allclose(delta, linearization @ first.reshape(-1))
    assert not np.allclose(child_zero, 0.0)


def test_focused_source_lineage_finds_no_local_principal_lift_one_jet() -> None:
    rows = source_lineage_ledger()
    assert len(rows) == 11
    assert any("ABSTRACT_ACTUAL_SMOOTH" in row["found"] for row in rows)
    assert any("PARAMETER_SPACE_RANDOM_FRAME" in row["found"] for row in rows)
    assert not any("LOCAL_F_B_DF_B_g_B_dg_B" in row["found"] for row in rows)
    assert all(row["not_found"] for row in rows)


def test_pointwise_lift_and_incidence_do_not_determine_connection_transport() -> None:
    witness = local_one_jet_nonuniqueness_witness()
    assert witness["same_pointwise_gauge_lift"] is True
    assert witness["same_bundle_isomorphism_class"] is True
    assert witness["distinct_children_from_missing_vertical_one_jet"] is True
    assert witness["same_base_incidence_point"] is True
    assert witness["distinct_children_from_missing_base_tangent"] is True


def test_reference_identity_recovers_zero_but_does_not_select_nonzero_map() -> None:
    checks = conditional_geometry_checks()
    assert checks["connection_pullback_residual"] < 1.0e-12
    assert checks["nonzero_trace_transported"] is True
    assert checks["affine_term_nonzero"] is True
    assert checks["reference_identity_zero_field_recovery_residual"] == 0.0
    assert checks["not_an_admissible_BHSM_background_evaluation"] is True


def test_weighted_cotangent_rule_preserves_the_exact_pairing() -> None:
    derivative = np.asarray(((2.0, 0.0), (0.0, 0.5)), dtype=complex)
    event_weight = np.diag((3.0, 5.0)).astype(complex)
    child_weight = np.diag((7.0, 11.0)).astype(complex)
    event_momentum = np.asarray((1.0 + 2.0j, -0.5j))
    variation = np.asarray((0.25 - 0.1j, 2.0j))
    child_momentum = weighted_cotangent_momentum_map(
        event_momentum, derivative, event_weight, child_weight
    )
    event_pairing = np.vdot(event_momentum, event_weight @ variation)
    child_pairing = np.vdot(
        child_momentum, child_weight @ (derivative @ variation)
    )
    assert abs(event_pairing - child_pairing) < 1.0e-12


def test_downstream_chain_fails_closed_at_the_local_one_jet() -> None:
    result = downstream_status()
    assert result["R_A"] is None
    assert result["D_R_A_at_zero"] is None
    assert result["D_R_A_at_two_admissible_backgrounds"] is None
    assert result["Maxwell_conormal_cotangent_lift"] is None
    assert result["gauge_symplectic_reset"] is None
    assert result["S_RESET_GFHS"] is None
    assert result["D3_Theta"] is None
    assert result["HS_normal_Legendre_rank"] == 0
    assert result["pi_H"] == 0.0
    assert result["blocked_by"] == EXACT_MISSING_DATUM


def test_claim_boundary_preserves_physical_and_gate7_flags() -> None:
    claims = claim_boundary()
    assert claims["status"] == STATUS
    assert claims["bundle_isomorphism_class_exists"] is True
    assert claims["abstract_AE2_equivariant_boundary_lift_exists"] is True
    assert claims["evaluable_principal_bundle_lift_local_one_jet_exists"] is False
    assert claims["connection_transport_derived"] is False
    assert claims["constant_v15_57_reused"] is False
    assert claims["family_spectrum_rebuilt"] is False
    assert claims["empirical_coefficients_used"] is False
    assert claims["FULL_FIELD_ACTION_ATTACHMENT_READY_FOR_GATE7_BACKGROUND"] is False
    assert claims["FULL_BHSM_COMPLETE"] is False
    assert claims["exact_missing_datum"] == EXACT_MISSING_DATUM


def test_materialized_hindsight_payload_is_deterministic() -> None:
    module = _materializer()
    first = module.build_payload()
    second = module.build_payload()
    assert first["VALIDATED"]
    assert first["INVALIDATED"]
    assert first["OPEN"] == [EXACT_MISSING_DATUM]
    assert first["EXACT_NEXT_OBJECT"] == EXACT_MISSING_DATUM
    assert first["ownership_levels"]["induced_connection_transport"]["status"] == (
        "CONDITIONAL_FORMULA_ONLY_NOT_ACTION_OWNED_EVALUABLE_MAP"
    )
    assert first["validation_passed"] is True
    assert module.deterministic_json(first) == module.deterministic_json(second)


def test_materializer_is_byte_identical() -> None:
    module = _materializer()
    path = module.main()
    first = path.read_bytes()
    module.main()
    assert path.read_bytes() == first
    assert json.loads(first)["validation_passed"] is True
