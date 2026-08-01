from __future__ import annotations

from bhsm.interface.envelopment import global_constraint_v10_2 as constraint


def test_all_global_constraint_candidates_fail_closed():
    rows = constraint.constraint_candidates()
    assert len(rows) == 6
    assert not any(row["viable_buoyancy_restoring_constraint"] for row in rows)
    volume = next(row for row in rows if row["candidate"].startswith("fixed total"))
    assert volume["source"] is None
    assert volume["dimensionful_input"] is True


def test_hamiltonian_constraint_propagates_but_is_not_total_energy_or_restoring_law():
    row = constraint.hamiltonian_constraint_audit()
    assert row["zero_surface_preserved"] is True
    assert row["scalar_total_energy"] is False
    assert row["global_modulus_stationarity_equation"] is False
    assert row["compactness_depth_response"] is None


def test_fixed_topology_is_scale_free():
    row = constraint.scale_audit()
    assert row["topology_selects_length"] is False
    assert row["absolute_unit"] is None
    assert row["physical_eV_GeV_output"] is None


def test_global_constraint_payload_validates_with_no_selected_constraint():
    payload = constraint.global_constraint_payload()
    assert payload["validation_passed"] is True
    assert payload["selected_constraint"] is None
