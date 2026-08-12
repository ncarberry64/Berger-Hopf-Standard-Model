from bhsm.interface.aether_quantum_functional_accounting_v16_00 import (
    common_observable_order,
    completion_payload,
    determinant_accounting_identity,
    global_hybrid_cycle_kkt,
)


def test_zeta_vacuum_is_replaced_not_double_counted():
    result = determinant_accounting_identity()
    assert "Gamma_parent+Gamma_SM_heat" in result["physical_quantum_functional"]
    assert "Gamma_attached_zeta-Gamma_SM_zeta" in result["equivalent_replacement_form"]
    assert result["same_replacement_for_geometry_gauge_and_Yukawa"]


def test_global_cycle_kkt_is_square_and_nonlocal():
    result = global_hybrid_cycle_kkt(24)
    assert result["total_unknown_count"] == 314
    assert result["total_equation_count"] == 314
    assert result["logdet_is_global_in_cycle_time"]
    assert result["can_be_inserted_as_independent_local_acceleration"] is False


def test_gauge_and_yukawa_share_all_quantum_semantics():
    result = common_observable_order()
    assert result["absolute_gauge_normalization_and_nonzero_Yukawa_share_saddle"]
    assert result["absolute_gauge_normalization_and_nonzero_Yukawa_share_regulator"]
    assert result[
        "absolute_gauge_normalization_and_nonzero_Yukawa_share_renormalization_replacement"
    ]
    assert result["split_repair_allowed"] is False


def test_payload_validates_without_claiming_solve():
    result = completion_payload()
    assert result["validation_passed"]
    assert result["claim_boundary"]["replacement_quantum_saddle_solved"] is False
