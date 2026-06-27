"""Demonstrate an explicitly non-validating custom geometry scan."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface import GeometricUnitMapper, HypersphericalGeometry, ParticleMassSolver  # noqa: E402


def build_scan() -> dict[str, object]:
    mapper = GeometricUnitMapper(scale_gev_per_tension=10.0)
    solver = ParticleMassSolver()
    cases = (
        ((1.0, 0.5), (0.25,), 1.0, 1.0, 1.0),
        ((1.0, 0.5), (0.25,), 1.15, 0.8, 1.0),
        ((2.0, 1.0), (0.5,), 1.0, 1.2, 0.75),
    )
    rows = []
    for index, (curvature, hopf, anisotropy, boundary, sector_factor) in enumerate(cases):
        geometry = HypersphericalGeometry(
            curvature_indices=curvature,
            hopf_coefficients=hopf,
            anisotropy=anisotropy,
            boundary_coupling=boundary,
            sector="reviewer_scan",
            mode_label=f"scan_{index}",
        )
        result = solver.solve_mass(
            geometry,
            particle_key=f"scan_candidate_{index}",
            initial_guess_gev=10.0,
            mapper=mapper,
            sector_factor=sector_factor,
        )
        rows.append(
            {
                "geometry": geometry.to_dict(),
                "sector_factor": sector_factor,
                "result": result.to_dict(),
            }
        )
    return {
        "status": "CUSTOM_INTERFACE_SCAN_NOT_BHSM_VALIDATION",
        "rows": rows,
        "frozen_predictions_changed": False,
    }


def main() -> None:
    print(json.dumps(build_scan(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
