import json
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.covariant_bubble_interface_mechanics import (
    curvature_traction,
    interface_stiffness,
    relativistic_radial_membrane_traction,
    spectral_formation_number,
)


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/action_extension/BHSM_COVARIANT_BUBBLE_INTERFACE_MECHANICS.json"


def _payload():
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_fsc_stiffness_has_the_required_scale_power():
    assert interface_stiffness(0.01, 2.0, 3) == pytest.approx(0.00125)
    ratio = interface_stiffness(0.01, 2.0, 4) / interface_stiffness(0.01, 4.0, 4)
    assert ratio == pytest.approx(16.0)


def test_curvature_traction_is_the_oriented_mean_curvature_term():
    assert curvature_traction(2.5, [0.25, 0.25]) == pytest.approx(1.25)
    assert curvature_traction(2.5, [0.25, -0.25]) == pytest.approx(0.0)


def test_relativistic_radial_equation_reduces_to_static_laplace_term():
    value = relativistic_radial_membrane_traction(3.0, 2, 4.0, 0.0, 0.0)
    assert value == pytest.approx(1.5)
    moving = relativistic_radial_membrane_traction(3.0, 2, 4.0, 0.2, 0.1)
    assert moving > value


def test_formation_number_is_dimensionless_threshold():
    assert spectral_formation_number(6.0, 2.0, 4.0) == pytest.approx(1.0)
    assert spectral_formation_number(3.0, 2.0, 4.0) < 1.0


def test_invalid_physical_helper_domains_fail_closed():
    with pytest.raises(ValueError):
        interface_stiffness(0.01, 0.0, 3)
    with pytest.raises(ValueError):
        relativistic_radial_membrane_traction(1.0, 2, 1.0, 1.0, 0.0)
    with pytest.raises(ValueError):
        spectral_formation_number(1.0, -2.0, 1.0)


def test_artifact_is_valid_but_does_not_claim_completion_or_track1():
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["interface_stiffness"]["classification"] == "GAMMA1"
    assert payload["formation_number"]["classification"] == "RHO-B2"
    assert payload["carrier_reset"]["carrier_class"] == "CARR2_CONDITIONAL"
    assert payload["N12"]["new_independent_rank"] == 0
    assert payload["N12"]["Gate7_result_imported"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert len(payload["OPEN"]) == 1


def test_surface_law_contains_no_fitted_or_phenomenological_terms():
    payload = _payload()
    assert payload["interface_stiffness"]["fitted_coefficient"] is None
    assert payload["moving_interface"]["damping"].startswith("none locally")
    assert payload["interface_action"]["extra_viscosity"] is False
    assert payload["interface_action"]["new_bending_coefficient"] is False
    assert payload["FSC"]["observed_alpha_EM_used"] is False
    assert "no pressure" in payload["domain"]["pregeometry"]


def test_static_spherical_curvature_matches_radial_equation():
    gamma, radius, p = 0.7, 3.2, 5
    principal = np.full(p, 1.0 / radius)
    geometric = curvature_traction(gamma, principal)
    radial = relativistic_radial_membrane_traction(
        gamma, p, radius, 0.0, 0.0
    )
    assert radial == pytest.approx(geometric)
