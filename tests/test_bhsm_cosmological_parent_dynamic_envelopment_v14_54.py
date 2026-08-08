from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.completion.cosmological_parent_dynamic_envelopment_v14_54 import (
    CHANNEL_TABLE,
    EXACT_NEXT_OBJECT,
    completion_payload,
    cosmological_parent_anchor_payload,
    dynamic_c3_commutator_witness,
    materialize,
    mass_cycle_payload,
    nesting_and_orbit_contract,
    noncentral_floquet_witness,
    shape_derivative_current_payload,
)


def test_cosmological_anchor_is_effective_not_zero_input():
    p = cosmological_parent_anchor_payload()
    assert p["effective_branch"]["absolute_unit_closed_conditionally"] is True
    assert p["effective_branch"]["zero_input_scale_derived"] is False
    assert "lambda_0" in p["nesting_law"]["first_child"]


def test_moving_seam_contract_requires_full_periodic_solution():
    p = nesting_and_orbit_contract()
    assert p["current_archive_satisfies_contract"] is False
    assert "Phi(tau+T)=h.Phi(tau)" == p["relative_periodicity"]
    assert len(p["missing"]) >= 5


def test_all_nine_channel_slots_and_three_channel_rank_requirement():
    p = shape_derivative_current_payload()
    assert len(CHANNEL_TABLE) == 3 and all(len(row) == 3 for row in CHANNEL_TABLE)
    assert p["all_nine_kinematic_channels_present"] is True
    assert p["minimum_independent_separable_channels_for_rank_three"] == 3
    assert "delta^4 S_cc" in p["shape_dressed_vertex"]


def test_time_dependent_C3_algebra_still_commutes():
    p = dynamic_c3_commutator_witness()
    assert p["commutes_to_machine_precision"] is True
    assert p["commutator_frobenius_norm"] < 1e-14


def test_noncentral_floquet_witness_is_unitary_and_cp_capable():
    p = noncentral_floquet_witness()
    assert p["unitary_row_residual"] < 1e-12
    assert p["unitary_column_residual"] < 1e-12
    assert p["nonzero_jarlskog"] is True
    assert abs(p["jarlskog_witness"]) > 1e-8
    assert p["status"].endswith("NOT_A_PREDICTION")


def test_mass_is_cycle_invariant_not_snapshot():
    p = mass_cycle_payload()
    assert p["instantaneous_snapshot_is_physical_mass"] is False
    assert "T_f" in p["quasi_energy"]
    assert "composite-minus-parent" in p["relative_charge"]


def test_completion_gate_fails_closed():
    p = completion_payload()
    assert p["validation_passed"] is True
    assert p["Mark_III"] == "NOT_REACHED"
    assert p["BHSM_physical_completion"] is False
    assert p["exact_next_object"] == EXACT_NEXT_OBJECT
    assert p["validation"]["no_physical_CKM_emitted"] is True
    assert p["validation"]["USB_untouched"] is True


def test_materialization_is_byte_deterministic(tmp_path: Path):
    first = {p.name: p.read_bytes() for p in materialize(tmp_path)}
    second = {p.name: p.read_bytes() for p in materialize(tmp_path)}
    assert first == second
    for payload in first.values():
        json.loads(payload)
