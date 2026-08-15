from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.aether_moving_interface_transfer_v15_12 import (
    EXACT_NEXT_OBJECT,
    FULL_BHSM_COMPLETE,
    cayley_trace_unitary,
    completion_payload,
    conservative_moving_jump_residual,
    contact_ball_capacity,
    deterministic_json,
    hayward_corner_action,
    hayward_corner_variation,
    materialize,
    neck_scaling,
    self_adjoint_transfer_generator,
    transfer_nonuniqueness_witness,
    v15_10_interface_selection_payload,
    v15_9_incoming_interface_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_two_face_hayward_action_is_coefficient_locked() -> None:
    assert hayward_corner_action(2.0, 3.0, 0.25) == 1.5
    variation = hayward_corner_variation(2.0, 3.0, 0.25)
    assert variation["gradient"] == [0.5, 6.0]
    assert variation["cross_variation"] == 2.0
    assert variation["hessian"] == [[0.0, 2.0], [2.0, 0.0]]
    assert variation["symplectic_rank"] == 2
    assert variation["new_transfer_coefficient"] is False


def test_moving_jump_identity_is_conservative_but_not_a_selector() -> None:
    # [J.n]=3 and V[Q]=2*(4-2)=4 would fail by -1.
    assert conservative_moving_jump_residual(5.0, 2.0, 2.0, 4.0, 2.0) == -1.0
    assert conservative_moving_jump_residual(6.0, 2.0, 2.0, 4.0, 2.0) == 0.0


def test_seven_dimensional_contact_capacity_is_epsilon_fifth() -> None:
    expected = 16.0 * math.pi**3 / 3.0
    assert contact_ball_capacity(1.0, 7) == pytest.approx(expected)
    assert contact_ball_capacity(0.1, 7) / contact_ball_capacity(1.0, 7) == pytest.approx(1e-5)


def test_neck_power_count_preserves_gravity_but_controls_eta_p8() -> None:
    fixed = neck_scaling(0.1, eta_jump_scaling_exponent=0.0)
    smaller = neck_scaling(0.01, eta_jump_scaling_exponent=0.0)
    matched = neck_scaling(0.01, eta_jump_scaling_exponent=1.0 / 8.0)
    assert fixed["capacity_power"] == 5
    assert smaller["Einstein_Hilbert_proxy"] < fixed["Einstein_Hilbert_proxy"]
    assert smaller["eta_p8_proxy"] > fixed["eta_p8_proxy"]
    assert fixed["finite_O1_eta_jump_allowed"] is False
    assert matched["eta_p8_finite_limit_condition"] is True
    assert matched["eta_p8_proxy"] == pytest.approx(1.0)


def test_self_adjointness_does_not_select_transfer() -> None:
    weak = self_adjoint_transfer_generator(1.0, 1.7, 0.25, 0.0)
    strong = self_adjoint_transfer_generator(1.0, 1.7, 0.75, 0.0)
    phased = self_adjoint_transfer_generator(1.0, 1.7, 0.75, 0.61)
    for generator in (weak, strong, phased):
        assert generator == pytest.approx(np.conjugate(generator.T))
    assert np.linalg.eigvalsh(weak) != pytest.approx(np.linalg.eigvalsh(strong))
    witness = transfer_nonuniqueness_witness()
    assert witness["all_complete_generators_self_adjoint"] is True
    assert witness["inequivalent_transfer_spectra"] is True
    assert witness["self_adjointness_selects_transfer_amplitude"] is False


@pytest.mark.parametrize("alpha", [-2.0, -1.0, 0.0, 1.0, 2.0])
def test_all_cayley_graph_members_cancel_flux(alpha: float) -> None:
    assert abs(cayley_trace_unitary(alpha)) == pytest.approx(1.0)


def test_v15_9_incoming_branch_has_no_Hopf_contact_embedding() -> None:
    payload = v15_9_incoming_interface_payload((1.001, 1.01), modes=12)
    assert payload["unique_radial_level_for_each_profile_value"] is True
    assert all(row["degree"] == pytest.approx(1.0, abs=2e-12) for row in payload["rows"])
    assert all(row["radial_profile_strictly_monotone"] for row in payload["rows"])
    assert payload["radial_level_topology"] == "S6"
    assert payload["required_physical_child_seam_topology"] == "S3_times_S3"
    assert payload["radial_level_is_physical_Hopf_contact_interface"] is False


def test_minimal_corner_action_does_not_select_v15_10_witness() -> None:
    payload = v15_10_interface_selection_payload()
    assert payload["witnesses"] == ["A", "B", "C"]
    assert payload["direct_Hayward_selector_jacobian_d_alpha_r_gamma"] == [0, 0, 0]
    assert payload["surviving_witness_count_before_unavailable_backreacted_contact_BVP"] == 3
    assert payload["v15_10_nonuniqueness_resolved"] is False


def test_completion_stops_only_at_new_foundational_obstruction() -> None:
    payload = completion_payload()
    assert FULL_BHSM_COMPLETE is False
    assert payload["validation_passed"] is True
    assert payload["moving_interface_action"]["genuine_corner_has_nonzero_geometric_cross_variation"] is True
    assert payload["moving_interface_action"]["corner_term_alone_is_physical_transfer_Hamiltonian"] is False
    assert payload["interface_equations"]["physical_flux_residual_evaluable"] is False
    assert payload["reconnection_obstruction"]["geometric_corner_mechanics_action_owned"] is True
    assert payload["reconnection_obstruction"]["conservative_nonzero_transfer_uniquely_selected"] is False
    assert payload["scientific_terminal_condition"].startswith("GENUINE_RECONNECTION")
    assert EXACT_NEXT_OBJECT.startswith("ACTION_SELECTED_RECONNECTION_COBORDISM")


def test_deterministic_materialization_and_committed_artifact(tmp_path: Path) -> None:
    encoded = deterministic_json(completion_payload())
    assert encoded.endswith("\n")
    assert "NaN" not in encoded and "Infinity" not in encoded
    assert json.loads(encoded)["version"] == "v15.12"
    first = materialize(tmp_path / "a")
    second = materialize(tmp_path / "b")
    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()
    assert first.read_bytes() == (ROOT / "artifacts" / first.name).read_bytes()
