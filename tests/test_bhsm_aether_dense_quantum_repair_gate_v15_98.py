from bhsm.interface.aether_dense_quantum_repair_gate_v15_98 import (
    completion_payload,
    dense_repair_gate,
)


DENSE_WITNESS = {
    "proper_cycle_K_magnetic": 809.858537429679,
    "proper_cycle_K_electric": 2514.195062100584,
}


def test_dense_gate_requires_order_one_quantum_correction():
    result = dense_repair_gate(DENSE_WITNESS)
    assert result["minimum_max_sector_correction"] > result["dense_K_magnetic"]
    assert result["minimum_log_scale_interval"] > 9000.0
    assert result["controlled_one_loop_or_RG_repair_possible"] is False


def test_dense_gate_keeps_gauge_and_yukawa_in_one_saddle():
    result = dense_repair_gate(DENSE_WITNESS)
    assert result["one_common_quantum_saddle_required"]
    assert result["recompute_gauge_and_Yukawa_together"]


def test_payload_validates(monkeypatch):
    monkeypatch.setattr(
        "bhsm.interface.aether_dense_quantum_repair_gate_v15_98.dense_constraint_solved_cycle",
        lambda: DENSE_WITNESS,
    )
    assert completion_payload()["validation_passed"]
