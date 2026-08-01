from __future__ import annotations

from bhsm.interface.envelopment import buoyancy_functional_v10_2 as buoyancy


def test_obstruction_theorem_has_all_required_premises():
    theorem = buoyancy.obstruction_theorem()
    assert theorem["premises_all_proved"] is True
    assert all(theorem["premises"].values())
    assert theorem["conclusion"] == buoyancy.PRIMARY_VERDICT


def test_no_buoyancy_functional_or_physical_equilibrium_is_emitted():
    row = buoyancy.functional_gate()
    assert row["U_buoy"] is None
    assert row["delta_U_delta_psi"] is None
    assert row["delta_U_delta_a_F"] is None
    assert row["equilibrium"] is None
    assert row["proxy_R_promoted"] is False


def test_weak_field_and_numerical_scan_fail_closed():
    row = buoyancy.weak_field_gate()
    assert row["action_selected_static_background"] is None
    assert row["effective_Newtonian_potential"] is None
    assert row["effective_G"] is None
    assert row["empirical_constants_used"] == []
    assert row["numerical_scan_performed"] is False


def test_dynamic_proxy_is_not_coupled_by_arbitrary_terms():
    row = buoyancy.dynamic_envelope_coupling()
    assert row["R_map"] is None
    assert row["mixed_action_blocks"] == {
        "delta2S_da_F_delta_Psi": 0,
        "delta2S_da_F_delta_H": 0,
    }
    assert row["coupled_reduced_action"] is None
    assert row["arbitrary_coupling_added"] is False


def test_absolute_scale_and_extension_comparison_remain_unadopted():
    scale = buoyancy.absolute_scale_gate()
    assert scale["unique_scale"] is False
    assert scale["remaining_dimensional_degeneracy"] == 1
    assert scale["physical_eV_GeV_output"] is None
    assert not any(row["adopted"] for row in buoyancy.extension_comparison())
