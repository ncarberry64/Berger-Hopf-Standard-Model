from bhsm.interface.aether_quantum_cone_repair_gate_v15_95 import (
    completion_payload,
    exact_quantum_problem,
    necessary_quantum_correction,
    perturbative_rg_scale_test,
)


def test_any_cone_repair_needs_a_nonperturbatively_large_correction():
    result = necessary_quantum_correction()
    assert result["triangle_inequality_minimum_max_correction"] > 951.0
    assert result["minimum_correction_over_K_magnetic"] > 1.16
    assert result["controlled_one_loop_repair_possible"] is False


def test_optimistic_one_loop_rg_rate_needs_over_ten_thousand_efolds():
    result = perturbative_rg_scale_test()
    assert result["minimum_log_scale_interval_at_that_rate"] > 1.0e4
    assert result["natural_finite_log_interval_can_repair"] is False


def test_full_common_quantum_saddle_keeps_yukawa_and_gauge_together():
    result = exact_quantum_problem()
    assert result["one_loop_evaluation_about_unshifted_classical_saddle_sufficient"] is False
    assert result["separate_gauge_counterterm_allowed"] is False
    assert result["Yukawa_must_be_recomputed_with_same_quantum_saddle"]


def test_payload_validates():
    assert completion_payload()["validation_passed"]
