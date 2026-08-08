import math

from bhsm.interface.completion.relative_anomaly_tensor_current_v14_53 import (
    berger_weyl_shape,
    berger_weyl_shape_derivatives,
    c3_commutant_response,
    c3_group_algebra_no_go,
    commutator_norm,
    completion_payload,
    frozen_berger_witness,
    full_preimage_evaluability_gate,
    integrated_berger_weyl_squared,
    materialize,
    minimal_dirac_relative_weyl_anomaly,
    normalized_scale_witness,
    peter_weyl_tensor_current_contract,
    relative_anomaly_payload,
)


def test_round_parent_has_zero_weyl_shape_and_anomaly():
    assert berger_weyl_shape(1.0) == 0.0
    payload = minimal_dirac_relative_weyl_anomaly(1.0)
    assert abs(payload["integrated_C2"]) < 1e-15
    assert abs(payload["zeta_rel_weyl_component"]) < 1e-15


def test_berger_shape_derivatives_are_exact():
    a = 1.2
    f, fp, fpp = berger_weyl_shape_derivatives(a)
    h = 1e-6
    fd = (berger_weyl_shape(a + h) - berger_weyl_shape(a - h)) / (2 * h)
    fdd = (
        berger_weyl_shape(a + h)
        - 2 * berger_weyl_shape(a)
        + berger_weyl_shape(a - h)
    ) / (h * h)
    assert math.isclose(fp, fd, rel_tol=1e-8, abs_tol=1e-8)
    assert math.isclose(fpp, fdd, rel_tol=2e-4, abs_tol=2e-4)
    assert f > 0


def test_integrated_weyl_and_anomaly_prefactor():
    a = 1.3
    c2 = integrated_berger_weyl_squared(a)
    anomaly = minimal_dirac_relative_weyl_anomaly(a)
    expected = -c2 / (320.0 * math.pi**2)
    assert math.isclose(anomaly["zeta_rel_weyl_component"], expected, rel_tol=1e-13)


def test_frozen_berger_witness_has_negative_scale_stabilizing_component():
    payload = minimal_dirac_relative_weyl_anomaly(frozen_berger_witness())
    assert payload["shape_F"] > 0
    assert payload["zeta_rel_weyl_component"] < 0
    assert payload["d_zeta_rel_weyl_da"] < 0


def test_normalized_power_six_witness_is_stable_for_negative_anomaly():
    z = minimal_dirac_relative_weyl_anomaly(frozen_berger_witness())[
        "zeta_rel_weyl_component"
    ]
    point = normalized_scale_witness(z, power=6, amplitude=1.0)
    assert point.exists
    assert point.scale_ratio is not None and point.scale_ratio > 0
    assert point.scale_curvature is not None and point.scale_curvature > 0
    assert point.stable


def test_relative_anomaly_payload_remains_component_scoped():
    payload = relative_anomaly_payload()
    assert payload["validation"]["nonround_component_negative"]
    assert payload["validation"]["full_anomaly_not_claimed"]
    assert len(payload["scope_exclusions"]) >= 5


def test_full_preimage_gate_is_fail_closed():
    payload = full_preimage_evaluability_gate()
    assert payload["numerical_full_preimage_scale_point_emitted"] is False
    assert all(value is False for value in payload["required_objects"].values())
    assert payload["validation"]["partial_witness_not_promoted"]


def test_all_c3_commutant_responses_commute():
    h1 = c3_commutant_response(1.0, 0.2, 0.03)
    h2 = c3_commutant_response(-0.4, 0.7, -0.11)
    assert commutator_norm(h1, h2) < 1e-12


def test_c3_no_go_blocks_ckm_and_cp():
    payload = c3_group_algebra_no_go()
    assert payload["validation"]["representative_commutator_zero"]
    assert not payload["consequences"][
        "different_up_down_C3_commutant_coefficients_generate_CKM"
    ]
    assert not payload["consequences"][
        "G2_C3_odd_coefficient_alone_generates_physical_CP"
    ]


def test_peter_weyl_contract_requires_noncentral_channels():
    payload = peter_weyl_tensor_current_contract()
    table = payload["weak_current_channel_table"]["entries_minimal_L_r"]
    assert len(table) == 3 and all(len(row) == 3 for row in table)
    assert payload["action_ownership_audit"][
        "current_action_fixes_channel_coefficients"
    ] is False
    assert payload["validation"]["minimum_three_separable_channels"]


def test_completion_gate_remains_physically_open():
    payload = completion_payload()
    assert payload["gates"]["minimal_Dirac_relative_Weyl_component_evaluated"]
    assert not payload["gates"]["total_relative_anomaly_evaluated"]
    assert not payload["gates"]["Peter_Weyl_tensor_current_action_owned"]
    assert not payload["gates"]["physical_CKM_emitted"]
    assert not payload["gates"]["physical_scale_emitted"]
    assert not payload["gates"]["BHSM_physical_completion"]
    assert payload["validation_passed"]


def test_materialization_is_byte_deterministic(tmp_path):
    first = {p.name: p.read_bytes() for p in materialize(tmp_path)}
    second = {p.name: p.read_bytes() for p in materialize(tmp_path)}
    assert first == second
    assert len(first) == 5
