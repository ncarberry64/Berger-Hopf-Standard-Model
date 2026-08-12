from bhsm.interface.aether_event_shell_joint_operator_v15_73 import (
    completion_payload,
    dirichlet_monotonicity_theorem,
    exact_joint_crossing_problem,
    v15_72_reclassification,
)


def test_one_operator_orders_both_outputs() -> None:
    theorem = dirichlet_monotonicity_theorem()
    assert theorem["gauge_order"].startswith("N[W_1]<=")
    assert theorem["current_order"].startswith("G[W_1]>=")


def test_crossing_is_joint() -> None:
    crossing = exact_joint_crossing_problem()
    assert crossing["same_t_star_and_same_Gamma_boundary"]
    assert not crossing["separate_normalization_allowed"]


def test_uniform_shortcut_is_not_promoted() -> None:
    correction = v15_72_reclassification()
    assert correction["not_exact_for_actual_cap"]
    assert not correction["claimed_actual_crossing"]
    assert completion_payload()["validation_passed"]
