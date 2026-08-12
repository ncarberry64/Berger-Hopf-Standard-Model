from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.aether_dimensional_crossover_sigma_v15_17 import (
    CAMPAIGN_OBJECT,
    EXACT_NEXT_OBJECT,
    FULL_BHSM_COMPLETE,
    bhsm_dimension_ledger,
    completion_payload,
    deterministic_json,
    dimensional_crossover_payload,
    equatorial_collar_geometry,
    m5_normal_scalar_operator,
    materialize,
    reduced_sigma_response_jet,
    reduction_sensitivity_jacobian,
    round_bubble_geometry,
    unit_sphere_area,
)


ROOT = Path(__file__).resolve().parents[1]


def test_bhsm_actual_dimension_convention() -> None:
    ledger = bhsm_dimension_ledger()
    assert ledger["M4"]["spatial_dimension"] == 3
    assert ledger["M5"]["spatial_dimension"] == 4
    assert ledger["M8_to_M5"].startswith("oriented_S3_fiber_pushforward")
    assert ledger["M5_to_M4"] == "equatorial_trace_plus_constrained_critical_value"
    assert ledger["local_dimension_field_in_retained_action"] is False


def test_endpoint_bubble_geometry_is_dimension_dependent() -> None:
    three = round_bubble_geometry(3, 2.0)
    four = round_bubble_geometry(4, 2.0)
    assert unit_sphere_area(2) == pytest.approx(4.0 * math.pi)
    assert unit_sphere_area(3) == pytest.approx(2.0 * math.pi**2)
    assert three["area"] == pytest.approx(16.0 * math.pi)
    assert three["volume"] == pytest.approx(32.0 * math.pi / 3.0)
    assert three["summed_mean_curvature"] == pytest.approx(1.0)
    assert four["area"] == pytest.approx(16.0 * math.pi**2)
    assert four["volume"] == pytest.approx(8.0 * math.pi**2)
    assert four["summed_mean_curvature"] == pytest.approx(1.5)


def test_round_collar_is_even_smooth_and_totally_geodesic_at_seam() -> None:
    left = equatorial_collar_geometry(-0.2, 1.7)
    right = equatorial_collar_geometry(0.2, 1.7)
    seam = equatorial_collar_geometry(0.0, 1.7)
    assert left["dimensionless_density_factor"] == pytest.approx(
        right["dimensionless_density_factor"]
    )
    assert left["d_log_density_d_rho"] == pytest.approx(
        -right["d_log_density_d_rho"]
    )
    assert seam["d_log_density_d_rho"] == 0.0
    assert seam["M4_slice_extrinsic_curvature_trace"] == 0.0
    assert seam["d2_log_density_d_rho2"] == pytest.approx(-3.0)


def test_m5_transverse_operator_has_constant_neumann_zero_mode() -> None:
    for chi in (0.2, 0.7, math.pi / 2.0, 2.3, 2.9):
        assert m5_normal_scalar_operator(0.0, 0.0, chi, 2.0) == 0.0
    assert m5_normal_scalar_operator(1.0, 0.0, math.pi / 2.0, 2.0) == pytest.approx(0.0)


def test_reduction_transports_but_does_not_select_response_jet() -> None:
    jet = reduced_sigma_response_jet(-1.0, 1.0, 3.0, profile_measure=2.0)
    assert jet["dS_sigma_dX"] == pytest.approx(6.0)
    jacobian = reduction_sensitivity_jacobian(-1.0, 1.0, 3.0, profile_measure=2.0)
    assert np.linalg.matrix_rank(jacobian) == 3
    payload = dimensional_crossover_payload()["reduction_response_test"]
    assert payload["transport_sensitivity_rank"] == 3
    assert payload["action_owned_target_response_jet_from_crossover"] is None
    assert payload["physical_selector_rank"] == 0


def test_existing_compatibility_multiplier_is_not_a_sigma_law() -> None:
    payload = dimensional_crossover_payload()
    term = payload["existing_cross_stratum_sigma_term"]
    assert term["formula"] == "integral_M5<lambda_sigma,sigma5-P0_sigma8>"
    assert term["multiplier_has_kinetic_term"] is False
    assert term["generates_sigma_mass_X_derivative_or_quartic"] is False
    critical = payload["existing_M5_to_M4_critical_value"]
    assert critical["global_unique_physical_kernel_evaluated"] is False
    assert critical["sigma_Wilson_data_eliminated_by_critical_value"] is False


def test_completion_preserves_claim_boundary() -> None:
    payload = completion_payload()
    assert FULL_BHSM_COMPLETE is False
    assert payload["validation_passed"] is True
    assert payload["campaign_object"] == CAMPAIGN_OBJECT
    assert payload["post_crossover_traction"].startswith("ENDPOINT_GEOMETRIC_FORMULAS_ONLY")
    assert payload["dimensional_crossover_audit"]["dimensional_skin_energy"][
        "independent_E_dim_term_in_retained_action"
    ] is None
    assert EXACT_NEXT_OBJECT.startswith("ACTION_OWNED_M5_TO_M4_CROSS_STRATUM")


def test_deterministic_materialization_and_repository_artifact(tmp_path: Path) -> None:
    encoded = deterministic_json(completion_payload())
    assert encoded.endswith("\n")
    assert "NaN" not in encoded and "Infinity" not in encoded
    assert json.loads(encoded)["version"] == "v15.17"
    first = materialize(tmp_path / "first")
    second = materialize(tmp_path / "second")
    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()
    assert first.read_bytes() == (ROOT / "artifacts" / first.name).read_bytes()
