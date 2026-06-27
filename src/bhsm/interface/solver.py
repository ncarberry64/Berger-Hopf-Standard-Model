"""Root-solving interface for replaceable BHSM equilibrium equations."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import isfinite
from typing import Any, Callable, Mapping, Sequence

import numpy as np
from scipy.optimize import root

from .geometry import HypersphericalGeometry
from .units import GeometricUnitMapper


@dataclass
class SolverResult:
    particle_key: str
    success: bool
    mass_gev: float | None
    mass_ev: float | None
    residual: float | None
    solver_message: str
    initial_guess_gev: float
    calibration_anchor: str | None
    is_anchor_particle: bool
    prediction_status: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ParticleMassSolver:
    """Solve one-dimensional particle mass equilibrium equations."""

    def __init__(self, residual_tolerance: float = 1.0e-10) -> None:
        if residual_tolerance <= 0.0:
            raise ValueError("residual_tolerance must be positive")
        self.residual_tolerance = residual_tolerance

    def solve_mass(
        self,
        geometry: HypersphericalGeometry,
        particle_key: str,
        initial_guess_gev: float,
        mapper: GeometricUnitMapper,
        sector_factor: float = 1.0,
        equilibrium_params: Mapping[str, float] | None = None,
        custom_residual_fn: Callable[..., float] | None = None,
    ) -> SolverResult:
        """Solve a mass and return an explicit success or failure record."""

        is_anchor = particle_key == mapper.anchor_particle
        status = (
            "CALIBRATION_ANCHOR_NOT_INDEPENDENT_PREDICTION"
            if is_anchor
            else "MODEL_PREDICTION_GIVEN_CALIBRATION"
        )

        def residual_vector(values: np.ndarray) -> np.ndarray:
            value = geometry.equilibrium_residual(
                float(values[0]),
                mapper,
                sector_factor=sector_factor,
                equilibrium_params=equilibrium_params,
                residual_fn=custom_residual_fn,
            )
            return np.asarray([value], dtype=float)

        try:
            solved = root(residual_vector, np.asarray([initial_guess_gev], dtype=float))
            mass = float(solved.x[0])
            residual = float(residual_vector(np.asarray([mass]))[0])
            success = bool(
                solved.success
                and isfinite(mass)
                and mass >= 0.0
                and isfinite(residual)
                and abs(residual) <= self.residual_tolerance
            )
            message = str(solved.message)
            if not success:
                message = f"ROOT_SOLVE_FAILED_OR_NONPHYSICAL: {message}"
                mass_out = None
                ev_out = None
            else:
                mass_out = mass
                ev_out = mapper.mass_gev_to_ev(mass)
            return SolverResult(
                particle_key=particle_key,
                success=success,
                mass_gev=mass_out,
                mass_ev=ev_out,
                residual=residual if isfinite(residual) else None,
                solver_message=message,
                initial_guess_gev=float(initial_guess_gev),
                calibration_anchor=mapper.anchor_particle,
                is_anchor_particle=is_anchor,
                prediction_status=status,
                metadata={
                    "geometry_formula_status": geometry.to_dict()["formula_status"],
                    "calibration_mode": mapper.calibration_mode,
                    "empirical_derivation_input_used": False,
                },
            )
        except Exception as exc:  # explicit failure record is part of the public API
            return SolverResult(
                particle_key=particle_key,
                success=False,
                mass_gev=None,
                mass_ev=None,
                residual=None,
                solver_message=f"ROOT_SOLVE_EXCEPTION: {type(exc).__name__}: {exc}",
                initial_guess_gev=float(initial_guess_gev),
                calibration_anchor=mapper.anchor_particle,
                is_anchor_particle=is_anchor,
                prediction_status=status,
                metadata={"calibration_mode": mapper.calibration_mode},
            )

    def solve_many(self, requests: Sequence[Mapping[str, Any]]) -> list[SolverResult]:
        """Solve a sequence of keyword-compatible solve requests."""

        return [self.solve_mass(**dict(request)) for request in requests]

    def scan_initial_guesses(
        self,
        initial_guesses_gev: Sequence[float],
        **solve_kwargs: Any,
    ) -> list[SolverResult]:
        """Run the same equation from multiple declared initial guesses."""

        return [
            self.solve_mass(initial_guess_gev=guess, **solve_kwargs)
            for guess in initial_guesses_gev
        ]
