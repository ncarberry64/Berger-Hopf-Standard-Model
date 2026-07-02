from bhsm.interface.full_action_closure.theorem_blocker_dag import build_theorem_blocker_dag


def test_dag_contains_required_terminal_dependencies():
    payload = build_theorem_blocker_dag()
    nodes = {node["id"] for node in payload["nodes"]}
    assert {"boundary_measure", "alpha_i_derivation", "ckm_exponent", "neutral_scale", "scalar_topographic_decoupling", "full_bhsm_completion"} <= nodes
    assert any(edge["to"] == "full_bhsm_completion" for edge in payload["edges"])
