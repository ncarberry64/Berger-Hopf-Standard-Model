from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.aether_material_skin_variation_v15_15 import (
    EXACT_NEXT_OBJECT,
    FULL_BHSM_COMPLETE,
    completion_payload,
    curvature_traction_density,
    deterministic_json,
    eta_flat_layer_scaling,
    internal_seam_green_residual,
    level_set_normal_velocity,
    material_skin_contact_impulse,
    material_trace_payload,
    materialize,
    sigma_kink_data,
    sigma_kink_profile,
    sigma_wall_witness_payload,
    spin_lift_transmission,
)


ROOT = Path(__file__).resolve().parents[1]


def test_global_spin_bundle_cancels_internal_seam_green_form() -> None:
    psi = np.array([1.0 + 0.2j, -0.3j, 0.7, -0.4])
    phi = np.array([0.1j, 0.5, -0.2j, 0.6])
    normal_form = np.diag([1.0, 1.0, -1.0, -1.0])
    assert internal_seam_green_residual(psi, phi, normal_form) < 1e-14
    transmitted = spin_lift_transmission(psi, np.eye(4))
    assert transmitted == pytest.approx(psi)


def test_material_trace_law_resolves_the_terminal_boundary_phase() -> None:
    payload = material_trace_payload()
    assert payload["skin_classification"].startswith("resolved_internal_material")
    assert payload["v14_45_matcher_status"] == "FIXED_BY_THE_ADOPTED_GLOBAL_SPIN_BUNDLE"
    assert payload["independent_self_adjoint_extension_phase"] is False
    assert payload["self_adjointness_check"] is True
    assert payload["free_inception_phase"] is False


def test_level_set_motion_supplies_the_skin_kinematic_law() -> None:
    assert level_set_normal_velocity(0.6, 0.3) == pytest.approx(-2.0)
    with pytest.raises(ValueError, match="positive"):
        level_set_normal_velocity(0.6, 0.0)


def test_eta_p2_p8_local_layer_has_no_selected_finite_width() -> None:
    narrow = eta_flat_layer_scaling(1.0, 1.0)
    wide = eta_flat_layer_scaling(1.0, 2.0)
    wider = eta_flat_layer_scaling(1.0, 4.0)
    assert narrow["width_derivative"] < 0.0
    assert wide["width_derivative"] < 0.0
    assert narrow["total_energy_per_area"] > wide["total_energy_per_area"]
    assert wide["total_energy_per_area"] > wider["total_energy_per_area"]
    assert wide["finite_stationary_width"] is False


@pytest.mark.parametrize(
    ("A", "G", "Z"),
    [(-1.0, 2.0, 1.0), (-2.0, 3.0, 0.7), (-0.4, 1.1, 2.0)],
)
def test_sigma_kink_exactly_solves_the_flat_euler_equation(A: float, G: float, Z: float) -> None:
    data = sigma_kink_data(A, G, Z)
    assert data["excess_tension"] > 0.0
    for multiple in (-3.0, -0.7, 0.0, 0.7, 3.0):
        sample = sigma_kink_profile(multiple * data["width"], A, G, Z)
        assert sample["Euler_residual"] == pytest.approx(0.0, abs=2e-14)


def test_all_v15_10_completions_are_bubble_compatible_but_physically_distinct() -> None:
    payload = sigma_wall_witness_payload()
    assert list(payload["walls"]) == ["A", "B", "C"]
    assert payload["all_A_B_C_have_exact_flat_kinks"] is True
    assert payload["all_A_B_C_have_positive_derived_tension"] is True
    assert payload["tensions_are_physically_distinct"] is True
    assert payload["bubble_structure_selects_one_witness"] is False
    tensions = [row["excess_tension"] for row in payload["walls"].values()]
    assert tensions == pytest.approx(
        [0.2465748259063099, 0.36117175983029653, 0.08219160863543663]
    )


def test_curvature_response_and_contact_projection_add_no_coefficient() -> None:
    assert curvature_traction_density(0.25, 4.0) == pytest.approx(1.0)
    impulse = material_skin_contact_impulse(
        0.25,
        2.0,
        kappa1=2.0,
        joint_measure=3.0,
        boost_angle=0.5,
        joint_measure_d=0.4,
        boost_angle_d=-0.2,
    )
    assert impulse["skin_profile"] == pytest.approx(-0.5)
    assert impulse["Hayward"] == pytest.approx(0.8)
    assert impulse["total"] == pytest.approx(0.3)


def test_completion_closes_phase_but_stops_at_material_response_obstruction() -> None:
    payload = completion_payload()
    assert FULL_BHSM_COMPLETE is False
    assert payload["validation_passed"] is True
    assert payload["phase_domain_gate"] == "CLOSED_BY_GLOBAL_SPIN_BUNDLE_MATERIAL_TRANSMISSION"
    assert payload["skin_stress_gate"].startswith("OPEN_SIGMA_RESPONSE")
    assert payload["contact_and_ejection"]["impulse_magnitude_or_sign_selected"] is False
    assert payload["ejection_gate"] == "OPEN_NO_PHYSICAL_CONTACT_IMPULSE"
    assert payload["scientific_terminal_condition"].startswith("ALL_RETAINED_MATERIAL_INTERFACE")
    assert EXACT_NEXT_OBJECT.startswith("ACTION_OWNED_SIGMA_RESPONSE_JET")


def test_deterministic_materialization_and_repository_artifact(tmp_path: Path) -> None:
    encoded = deterministic_json(completion_payload())
    assert encoded.endswith("\n")
    assert "NaN" not in encoded and "Infinity" not in encoded
    assert json.loads(encoded)["version"] == "v15.15"
    first = materialize(tmp_path / "first")
    second = materialize(tmp_path / "second")
    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()
    assert first.read_bytes() == (ROOT / "artifacts" / first.name).read_bytes()
