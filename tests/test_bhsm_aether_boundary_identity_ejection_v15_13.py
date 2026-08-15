from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.aether_boundary_identity_ejection_v15_13 import (
    EXACT_NEXT_OBJECT,
    FULL_BHSM_COMPLETE,
    boundary_identity_nonuniqueness_witness,
    boundary_identity_trace_unitary,
    collective_shape_force,
    completion_payload,
    constant_force_trajectory,
    contact_pulse_unitary,
    cross_exchange_norm,
    deterministic_json,
    materialize,
    schur_reduced_curvature,
    signed_normal_separation,
    unit_ball_volume,
    volume_radius,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("alpha_parent", "alpha_child"),
    [(0.0, 0.0), (1.0, 0.0), (0.0, 2.0), (-1.0, 2.0)],
)
def test_boundary_identity_reduces_to_block_diagonal_unitaries(
    alpha_parent: float, alpha_child: float
) -> None:
    unitary = boundary_identity_trace_unitary(alpha_parent, alpha_child)
    assert unitary.shape == (2, 2)
    assert np.conjugate(unitary.T) @ unitary == pytest.approx(np.eye(2))
    assert cross_exchange_norm(unitary) == 0.0


def test_boundary_identity_still_leaves_continuous_domain_family() -> None:
    witness = boundary_identity_nonuniqueness_witness()
    assert witness["boundary_identity_forbids_swap"] is True
    assert witness["boundary_identity_allowed_group"] == "U(1)_parent_times_U(1)_child"
    assert witness["all_witnesses_unitary"] is True
    assert witness["all_witnesses_preserve_boundary_identity"] is True
    assert witness["inequivalent_endpoint_spectra_remain"] is True
    assert witness["remaining_family_dimension"] == 2
    assert witness["self_adjointness_selects_alpha_parent_or_alpha_child"] is False


def test_asymptotic_identity_does_not_fix_transient_contact_history() -> None:
    endpoint = contact_pulse_unitary(math.pi)
    midway = contact_pulse_unitary(math.pi / 2.0)
    assert endpoint == pytest.approx(-np.eye(2))
    assert cross_exchange_norm(endpoint) == pytest.approx(0.0, abs=2e-15)
    assert cross_exchange_norm(midway) == pytest.approx(math.sqrt(2.0))


def test_covariant_volume_radius_has_no_free_normalization() -> None:
    omega7 = unit_ball_volume(7)
    radius = 2.25
    volume = omega7 * radius**7
    assert volume_radius(volume, 7) == pytest.approx(radius)


def test_shape_force_is_negative_relative_energy_variation() -> None:
    # dE/dq = .25*2 + .75*3 = 2.75.
    assert collective_shape_force([2.0, 3.0], [1.0, 1.0], [0.25, 0.75]) == pytest.approx(
        -2.75
    )
    # Equal parent/child on-shell traction yields no force.
    assert collective_shape_force([0.0, 0.0], [1.0, 1.0], [0.25, 0.75]) == 0.0


def test_restoring_curvature_is_the_constraint_reduced_schur_object() -> None:
    value = schur_reduced_curvature(5.0, [1.0, 2.0], [[4.0, 0.0], [0.0, 5.0]])
    assert value == pytest.approx(3.95)
    assert value > 0.0
    with pytest.raises(ValueError, match="positive"):
        schur_reduced_curvature(5.0, [1.0], [[-1.0]])


def test_signed_normal_separation_is_action_owned_local_geometry() -> None:
    assert signed_normal_separation(0.0, 1) == 0.0
    assert signed_normal_separation(0.3, 1) == pytest.approx(0.3)
    assert signed_normal_separation(0.3, -1) == pytest.approx(-0.3)
    with pytest.raises(ValueError):
        signed_normal_separation(0.3, 0)


def test_zero_force_and_zero_contact_momentum_cannot_eject() -> None:
    trajectory = constant_force_trajectory(2.0, 3.0, 0.0, 0.0)
    assert trajectory["separation"] == 0.0
    assert trajectory["normal_momentum"] == 0.0
    assert trajectory["ejected_at_this_time"] is False
    driven = constant_force_trajectory(2.0, 3.0, 0.0, 1.5)
    assert driven["separation"] > 0.0
    assert driven["ejected_at_this_time"] is True


def test_completion_stops_at_a_constructive_foundational_obstruction() -> None:
    payload = completion_payload()
    assert FULL_BHSM_COMPLETE is False
    assert payload["validation_passed"] is True
    identity = payload["boundary_identity_and_transport"]
    assert identity["crosswise_boundary_exchange_allowed"] is False
    assert identity["continuous_ambiguity_remains"] is True
    assert identity["Hayward_selects_skin_matter_phase"] is False
    assert payload["enclosed_spacetime_and_restoring_response"]["new_buoyancy_coefficient"] is None
    assert payload["ejection_gate"]["finite_action_post_contact_trajectory_selected"] is False
    assert payload["v15_10_selection"]["surviving_witness_count"] == 3
    assert payload["scientific_terminal_condition"].startswith("BOUNDARY_IDENTITY_STILL")
    assert EXACT_NEXT_OBJECT.startswith("ACTION_OWNED_PARENT_AND_CHILD_SKIN")


def test_deterministic_materialization_and_repository_artifact(tmp_path: Path) -> None:
    encoded = deterministic_json(completion_payload())
    assert encoded.endswith("\n")
    assert "NaN" not in encoded and "Infinity" not in encoded
    assert json.loads(encoded)["version"] == "v15.13"
    first = materialize(tmp_path / "first")
    second = materialize(tmp_path / "second")
    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()
    assert first.read_bytes() == (ROOT / "artifacts" / first.name).read_bytes()
