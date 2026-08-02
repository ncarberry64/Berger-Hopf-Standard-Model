from __future__ import annotations

import json

from sympy import Matrix, symbols, expand, diff

from bhsm.interface.completion import final_completion_gate_v11_2 as gate
from bhsm.interface.completion.primitive_support_character_ledger_v11_2 import (
    NEXT_OBJECT,
    VERDICT,
    coframe_candidate_test,
    ledger_payload,
)
from bhsm.interface.completion.support_character_boundary_core_selection_v11_2 import boundary_core_payload
from bhsm.interface.completion.support_character_constraint_system_v11_2 import VARIABLES, constraint_matrix, constraint_payload
from bhsm.interface.completion.support_character_equivalence_classes_v11_2 import equivalence_class_payload
from bhsm.interface.completion.support_linear_quadratic_connection_couplings_v11_2 import couplings_payload, real_scalar_expansion
from bhsm.interface.completion.support_noether_current_v11_2 import current_payload, derivative_residual


def test_primitive_object_inventory_and_composite_inheritance() -> None:
    payload = ledger_payload()
    rows = {row["object"]: row for row in payload["primitive_objects"]}
    assert payload["validation_passed"]
    assert len(rows) >= 39
    assert rows["metric_G_AB"]["candidate_support_character"] == "2 r_e"
    assert rows["inverse_metric_G_AB"]["candidate_support_character"] == "-2 r_e"
    assert rows["bulk_measure"]["candidate_support_character"] == "8 r_e for full support"
    assert rows["sector_projectors"]["candidate_support_character"] == "0"
    assert payload["nontrivial_action_owned_ledger"] is None


def test_coframe_candidate_is_rejected_nontrivially_by_existing_action() -> None:
    test = coframe_candidate_test()
    assert test["solution_with_inert_existing_coefficients"] == {"r_e": 0}
    assert test["support_definition_fixes_nonzero_r_e"] is False
    assert "Weyl compensator" in test["local_scaling_obstruction"]


def test_infinitesimal_sign_is_derived_not_assumed() -> None:
    assert derivative_residual(-1, +1) == 0
    assert derivative_residual(+1, +1) == 6
    assert derivative_residual(+1, -1) == 0
    payload = current_payload()
    assert payload["validation_passed"]
    assert payload["transformation_classification"]["local_gauge_redundancy"] is False


def test_exact_action_character_matrix_rank_nullity_and_kernel() -> None:
    matrix = constraint_matrix()
    payload = constraint_payload()
    assert isinstance(matrix, Matrix)
    assert matrix.rank() == payload["rank"] == 7
    assert len(matrix.nullspace()) == payload["nullity"] == 12
    assert payload["unconstrained"] == VARIABLES[7:]
    assert payload["forced_zero_within_full_coframe_candidate"] == VARIABLES[:7]
    assert all(matrix * vector == Matrix.zeros(matrix.rows, 1) for vector in matrix.nullspace())
    assert payload["validation_passed"]


def test_real_scalar_linear_quadratic_identity_is_exact() -> None:
    phi, dphi, w, a = symbols("phi dphi w a")
    lhs = (dphi - w * a * phi) ** 2
    rhs = dphi**2 - 2 * w * a * phi * dphi + w**2 * a**2 * phi**2
    assert expand(lhs - rhs) == 0
    assert real_scalar_expansion(2, 5, 3, 7)[0] == sum(real_scalar_expansion(2, 5, 3, 7)[1:])
    assert couplings_payload()["validation_passed"]


def test_integration_by_parts_boundary_identity_is_exact() -> None:
    x = symbols("x")
    # Pointwise product rule underlying integral -w A d(phi^2).
    A = x**2 + 1
    phi2 = x**4 + x
    assert expand(-A * diff(phi2, x) - (diff(-A * phi2, x) + diff(A, x) * phi2)) == 0


def test_boundary_core_flux_and_anomaly_tests_fail_closed() -> None:
    payload = boundary_core_payload()
    assert payload["validation_passed"]
    assert payload["boundary_selects_ledger"] is False
    assert payload["core_test"]["finite_symplectic_flux"] is None
    assert payload["core_test"]["finite_support_flux"] is None
    assert payload["anomaly_test"]["mixed_support_gauge_anomalies"] is None
    assert "trivially compatible" in payload["anomaly_test"]["forced_zero_matter_candidate"]


def test_common_rescaling_and_flat_connection_are_not_overquotiented() -> None:
    payload = equivalence_class_payload()
    assert payload["validation_passed"]
    assert payload["common_rescaling_test"]["beta_a_invariant"]
    assert payload["common_rescaling_test"]["canonical_q_D_kinetic_term_invariant"] is False
    assert payload["number_of_action_allowed_null_directions"] == 5
    assert payload["null_directions_form_one_common_normalization"] is False
    assert payload["pure_gauge_test"]["core_map_invertible"] is False


def test_all_six_steering_artifacts_carry_required_common_record(tmp_path) -> None:
    gate.materialize(tmp_path)
    names = [name for key, name in gate.ARTIFACT_FILES.items() if key in {
        "primitive_support_character_ledger", "support_noether_current",
        "support_linear_quadratic_connection_couplings", "support_character_constraint_system",
        "support_character_boundary_core_selection", "support_character_equivalence_classes",
    }]
    required = {"historical_sources", "primitive_fields", "candidate_weights", "derivation_equations", "constraint_matrix", "rank", "nullity", "normalization_freedom", "current", "linear_couplings", "quadratic_couplings", "boundary_result", "core_result", "anomaly_result", "frozen_limit", "final_status"}
    for name in names:
        payload = json.loads((tmp_path / "artifacts" / name).read_text())
        assert required <= payload.keys(), name
        assert payload["rank"] == 7 and payload["nullity"] == 12
        assert payload["final_status"] == VERDICT


def test_final_gate_and_blocker_readiness_after_exhaustion() -> None:
    payload = gate.completion_payload()
    assert payload["validation_passed"]
    assert payload["primary_verdict"] == VERDICT
    assert payload["exact_next_object"] == NEXT_OBJECT
    assert payload["historical_recovery"]["historical_routes_exhausted"]
    assert payload["Mark_II"] == "NOT_REACHED"
    assert payload["physical_outputs_promoted"] == []
    assert payload["frozen_predictions_changed"] is False
