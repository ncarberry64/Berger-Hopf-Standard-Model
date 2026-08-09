from __future__ import annotations

from math import cos
from pathlib import Path

import numpy as np

from bhsm.interface.completion.common_domain_eta_su3_reduction_v14_30 import (
    EXACT_NEXT_OBJECT,
    OUTCOME_C,
    bundle_reduction_payload,
    candidate_bridge_audit,
    collar_integral_factor,
    collar_jacobian,
    common_fixed_tangent_dimension,
    completion_payload,
    critical_value_derivative,
    dtn_hessian,
    hopf_section_exists,
    measure_action_variation_payload,
    nonlinear_fiber_moment,
    uniqueness_payload,
)
from bhsm.interface.completion.view2_completion_gate_v14_30 import (
    all_payloads,
    materialization_hashes,
)


def test_01_nontrivial_hopf_bundle_has_no_global_section():
    assert hopf_section_exists(0)
    assert not hopf_section_exists(1)


def test_02_v7_collar_jacobian_and_integral_are_exact():
    epsilon, scale = 0.37, 2.4
    grid = np.linspace(0.0, epsilon, 100_001)
    numeric = scale * np.trapezoid(np.cos(grid) ** 3, grid)
    assert collar_jacobian(epsilon) == cos(epsilon) ** 3
    assert np.isclose(collar_integral_factor(epsilon, scale), numeric, rtol=2e-11)


def test_03_nonlinear_p8_fiber_pushforward_does_not_close():
    witness = nonlinear_fiber_moment((1.0, 3.0))
    assert witness == {
        "average_then_power": 16.0,
        "power_then_average": 41.0,
        "defect": 25.0,
    }


def test_04_constant_fiber_mode_is_the_only_equality_witness_here():
    witness = nonlinear_fiber_moment((2.0, 2.0, 2.0))
    assert witness["defect"] == 0.0


def test_05_dtn_hessian_depends_on_outer_endpoint_domain():
    neumann = dtn_hessian(1.3, 0.8, "neumann")
    dirichlet = dtn_hessian(1.3, 0.8, "dirichlet")
    assert 0.0 < neumann < dirichlet


def test_06_critical_bulk_solution_has_nonzero_reduced_trace_derivative():
    # The interior Euler operator is zero by construction, whereas the exact
    # derivative is the sum of conormal fluxes.
    assert critical_value_derivative(0.7, 1.3, 0.8) != 0.0


def test_07_no_nonzero_su3_fixed_vector_in_the_tangent_three():
    assert common_fixed_tangent_dimension() == 0


def test_08_bundle_audit_preserves_general_c2_without_inventing_R_eta():
    payload = bundle_reduction_payload()
    assert payload["validation_passed"]
    assert payload["validation"]["associated_bundle_valid_for_arbitrary_c2"]
    assert payload["validation"]["R_eta_absent"]
    assert payload["diagram"]["requested_five_dimensional_inclusion"].startswith("exists after choosing")


def test_09_representation_and_orientation_claim_boundary_preserved():
    payload = bundle_reduction_payload()
    assert payload["representation"] == "m_C=3+bar3; reversing the oriented G2 branch conjugates 3 and bar3"
    assert payload["orientation_selection"].startswith("conditional")


def test_10_all_retained_bridge_candidates_answer_required_audit_questions():
    rows = candidate_bridge_audit()
    assert len(rows) == 5
    required = {
        "present_in_action",
        "acts_on_eta",
        "acts_on_physical_SU3",
        "common_domain",
        "measure",
        "commutes_with_variation",
        "coefficient",
        "duplicates_action",
        "verdict",
    }
    assert all(required <= row.keys() for row in rows)


def test_11_measure_variation_audit_contains_exact_failure_witnesses():
    payload = measure_action_variation_payload()
    assert payload["validation_passed"]
    assert payload["p8_Jensen_witness"]["defect"] > 0
    assert payload["dtn_counterexample"]["bulk_Euler_operator_on_critical_field"] == 0
    assert payload["dtn_counterexample"]["reduced_derivative_at_q"] != 0


def test_12_double_action_ledger_fails_closed():
    ledger = measure_action_variation_payload()["no_double_action_ledger"]
    status = {row["entry"]: row["status"] for row in ledger}
    assert status["parent eta term"] == "retained"
    assert status["collar gauged eta term"] == "not in retained action"
    assert status["double counting"].startswith("unresolved")


def test_13_uniqueness_audit_rejects_outcome_b():
    payload = uniqueness_payload()
    assert payload["validation_passed"]
    assert payload["uniqueness_theorem"] is None
    assert len(payload["surviving_inequivalent_choices"]) >= 5


def test_14_completion_gate_is_outcome_c_and_stops_downstream():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["primary_verdict"] == OUTCOME_C
    assert payload["BHSM_complete"] is False
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["FR_Dirac_matching_gate"] == "NOT_ELIGIBLE"
    assert payload["non_Abelian_BVP_gate"] == "NOT_ELIGIBLE"


def test_15_v14_29_claim_boundaries_and_frozen_outputs_preserved():
    payload = completion_payload()
    assert payload["validation"]["v14_29_local_current_preserved_conditionally"]
    assert payload["frozen_predictions_changed"] is False
    assert payload["physical_outputs_emitted"] is False


def test_16_materialization_is_byte_deterministic(tmp_path: Path):
    first = materialization_hashes(tmp_path / "first")
    second = materialization_hashes(tmp_path / "second")
    assert first == second
    assert "BHSM_completion_gate_v14_30.json" in first
    assert len(first) >= 19


def test_17_required_proof_report_contains_theorems_and_failure_cases():
    report = (
        Path(__file__).parents[1]
        / "docs"
        / "BHSM_COMMON_DOMAIN_ETA_SU3_REDUCTION_PROOF.md"
    ).read_text(encoding="utf-8")
    for required in (
        "Theorem 1",
        "Theorem 2",
        "Theorem 3",
        "Dirichlet-to-Neumann",
        "Outcome C",
        EXACT_NEXT_OBJECT,
    ):
        assert required in report


def test_18_all_materialized_payloads_validate_or_are_preserved_v14_29_records():
    payloads = all_payloads()
    assert "BHSM_completion_gate_v14_29.json" in payloads
    for name, payload in payloads.items():
        if name.endswith("v14_30.json"):
            assert payload["validation_passed"]
