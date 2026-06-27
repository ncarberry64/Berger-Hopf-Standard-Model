from __future__ import annotations

import math

import pytest

from bhsm.interface.geometry import HypersphericalGeometry
from bhsm.interface.solver import ParticleMassSolver
from bhsm.interface.units import GeometricUnitMapper


def test_solver_solves_default_residual_and_labels_anchor() -> None:
    geometry = HypersphericalGeometry((1.0,), (0.0,))
    mapper = GeometricUnitMapper.from_anchor(1.0, 80.0, "W_boson", "test source")
    result = ParticleMassSolver().solve_mass(geometry, "W_boson", 79.0, mapper)
    assert result.success
    assert result.mass_gev == pytest.approx(80.0)
    assert result.is_anchor_particle
    assert result.prediction_status == "CALIBRATION_ANCHOR_NOT_INDEPENDENT_PREDICTION"


def test_solver_solves_custom_equilibrium_and_labels_non_anchor() -> None:
    geometry = HypersphericalGeometry((1.0,), (0.0,))
    mapper = GeometricUnitMapper.from_anchor(1.0, 80.0, "W_boson", "test source")
    result = ParticleMassSolver().solve_mass(
        geometry,
        "candidate",
        1.0,
        mapper,
        custom_residual_fn=lambda mass, _geometry, _mapper, _factor, _params: mass**2 - 4.0,
    )
    assert result.success
    assert result.mass_gev == pytest.approx(2.0)
    assert result.prediction_status == "MODEL_PREDICTION_GIVEN_CALIBRATION"


def test_solver_failure_is_explicit() -> None:
    geometry = HypersphericalGeometry((1.0,), (0.0,))
    result = ParticleMassSolver().solve_mass(
        geometry,
        "bad_candidate",
        1.0,
        GeometricUnitMapper(),
        custom_residual_fn=lambda *_args: math.nan,
    )
    assert not result.success
    assert result.mass_gev is None
    assert "FAILED" in result.solver_message or "EXCEPTION" in result.solver_message


def test_solve_many_and_guess_scan_return_structured_rows() -> None:
    geometry = HypersphericalGeometry((1.0,), (0.0,))
    mapper = GeometricUnitMapper()
    solver = ParticleMassSolver()
    many = solver.solve_many(
        [
            {
                "geometry": geometry,
                "particle_key": "x",
                "initial_guess_gev": 0.5,
                "mapper": mapper,
            }
        ]
    )
    scan = solver.scan_initial_guesses(
        [0.5, 2.0], geometry=geometry, particle_key="x", mapper=mapper
    )
    assert len(many) == 1 and many[0].success
    assert len(scan) == 2 and all(row.success for row in scan)
