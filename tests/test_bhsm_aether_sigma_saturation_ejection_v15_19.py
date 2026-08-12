from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.aether_sigma_saturation_ejection_v15_19 import (
    EXACT_NEXT_OBJECT,
    FULL_BHSM_COMPLETE,
    completion_payload,
    deterministic_json,
    formation_homoclinic_state,
    higher_inertia_quartic,
    materialize,
    maximum_formation_inertial_drive,
    round_contact_provenance_payload,
    schur_reduced_quartic,
    tachyonic_activation_windows,
    two_coordinate_kinetic_transfer,
)


ROOT = Path(__file__).resolve().parents[1]


def test_exact_homoclinic_solves_v15_9_reduced_dynamics() -> None:
    for tau in (-6.0, -1.3, 0.0, 0.8, 5.0):
        state = formation_homoclinic_state(
            tau, supercriticality=0.7, critical_radius=1.9
        )
        assert state["Euler_residual"] == pytest.approx(0.0, abs=1e-14)
        assert state["Hamiltonian"] == pytest.approx(0.0, abs=2e-14)


def test_exact_peak_inertial_drive() -> None:
    result = maximum_formation_inertial_drive(
        supercriticality=0.6, critical_radius=2.4
    )
    assert result["maximum_q_dot_squared"] == pytest.approx(
        75 * 0.6**2 / (92 * 2.4**2)
    )
    assert result["M_q_times_maximum_q_dot_squared"] == pytest.approx(
        225 * 0.6**2 / 184
    )
    assert result["q_squared_at_velocity_maximum"] == pytest.approx(45 * 0.6 / 23)


def test_activation_is_transient_tachyonic_not_floquet() -> None:
    active = tachyonic_activation_windows(
        static_sigma_curvature=0.02,
        g=1.0,
        supercriticality=0.4,
        critical_radius=2.0,
    )
    inactive = tachyonic_activation_windows(
        static_sigma_curvature=2.0,
        g=1.0,
        supercriticality=0.4,
        critical_radius=2.0,
    )
    assert active["activation"] is True
    assert active["Floquet"] is False
    assert active["incoming_window"][1] < 0.0
    assert active["outgoing_window"][0] > 0.0
    assert active["turning_point_is_tangent_stable_again"] is True
    assert active["constant_static_curvature_control"] is True
    assert inactive["activation"] is False


def test_positive_response_schur_elimination_softens_quartic() -> None:
    result = schur_reduced_quartic(
        1.2, [0.4, -0.3], [[2.0, 0.1], [0.1, 1.5]]
    )
    assert result["Schur_norm"] > 0.0
    assert result["effective_quartic"] < result["direct_quartic"]
    assert result["softens_or_equal"] is True
    zero = schur_reduced_quartic(0.0, [0.4], [[2.0]])
    assert zero["effective_quartic"] < 0.0
    assert zero["positive_saturation_generated_from_zero_direct"] is False


def test_higher_inertia_quartic_has_declared_lorentzian_sign() -> None:
    positive_h = higher_inertia_quartic(0.0, 0.2, 2.0, 0.7)
    negative_h = higher_inertia_quartic(0.0, -0.2, 2.0, 0.7)
    assert positive_h["effective_quartic"] < 0.0
    assert negative_h["effective_quartic"] > 0.0


def test_cross_inertia_transfer_requires_positive_kinetic_metric() -> None:
    result = two_coordinate_kinetic_transfer(
        i_qq=2.0, i_dd=3.0, i_dq=0.4, q_dot=0.7, d_dot=0.0
    )
    assert result["Cauchy_bound_satisfied"] is True
    assert result["P_d_from_q_when_d_dot_zero"] == pytest.approx(0.28)
    with pytest.raises(ValueError, match="positive definite"):
        two_coordinate_kinetic_transfer(
            i_qq=1.0, i_dd=1.0, i_dq=1.1, q_dot=0.7, d_dot=0.0
        )


def test_round_seam_cannot_supply_first_order_cross_inertia() -> None:
    payload = round_contact_provenance_payload()
    assert payload["round_equator_K"] == 0.0
    assert payload["pure_normal_round_trace_response_norm"] == 0.0
    assert payload["normal_d_is_first_order_metric_trace_kernel"] is True
    assert payload["pure_cap_repartition_inertia"] == pytest.approx(0.0, abs=1e-8)
    assert payload["first_order_round_I_dq"] == 0.0
    assert payload["physical_nonround_or_second_shape_I_dq"] is None


def test_completion_stops_before_skin_and_ejection_claims() -> None:
    payload = completion_payload()
    assert FULL_BHSM_COMPLETE is False
    assert payload["validation_passed"] is True
    assert payload["sigma_activation"]["Floquet"] is False
    assert payload["physical_activation_gate"]["physical_window_endpoints_evaluated"] is False
    assert payload["quartic_saturation"]["unique_sigma_plus_minus_amplitude"] is None
    assert payload["contact_and_ejection"]["physical_P_d"] is None
    assert payload["contact_and_ejection"]["ejection"] is False
    assert EXACT_NEXT_OBJECT.startswith("ACTION_OWNED_NONROUND_OR_SECOND_SHAPE")


def test_deterministic_materialization_and_repository_artifact(tmp_path: Path) -> None:
    encoded = deterministic_json(completion_payload())
    assert encoded.endswith("\n")
    assert "NaN" not in encoded and "Infinity" not in encoded
    assert json.loads(encoded)["version"] == "v15.19"
    first = materialize(tmp_path / "first")
    second = materialize(tmp_path / "second")
    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()
    assert first.read_bytes() == (ROOT / "artifacts" / first.name).read_bytes()
