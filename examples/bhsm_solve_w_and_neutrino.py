"""Offline calibration/prediction/comparison example for the BHSM interface."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface import (  # noqa: E402
    GeometricUnitMapper,
    HypersphericalGeometry,
    ParticleMassSolver,
    ValidationComparison,
    load_reference_with_fallback,
)

CALIBRATION_WARNING = "W is used as calibration anchor, not independent prediction."
NEUTRINO_WARNING = (
    "Electron-neutrino comparison is against upper limit, not central measured mass."
)


def build_summary() -> dict[str, Any]:
    """Build a deterministic interface demonstration without network access."""

    w_reference = load_reference_with_fallback("W_boson")
    neutrino_reference = load_reference_with_fallback("electron_neutrino")
    assert w_reference.value_gev is not None

    w_geometry = HypersphericalGeometry(
        curvature_indices=(1.0,),
        hopf_coefficients=(0.0,),
        sector="electroweak_vector",
        mode_label="interface_demo_w_anchor",
        metadata={"purpose": "unit_calibration_demonstration"},
    )
    mapper = GeometricUnitMapper.from_anchor(
        anchor_tension=w_geometry.geometric_tension(),
        anchor_mass_gev=w_reference.value_gev,
        anchor_particle="W_boson",
        anchor_source=w_reference.source_label,
    )
    solver = ParticleMassSolver()
    w_result = solver.solve_mass(w_geometry, "W_boson", 80.0, mapper)

    # This tiny dimensionless demo mode is not asserted to be a BHSM theorem.
    neutrino_geometry = HypersphericalGeometry(
        curvature_indices=(1.0e-12,),
        hopf_coefficients=(0.0,),
        sector="effective_neutrino_extension",
        mode_label="interface_demo_electron_neutrino",
        metadata={"purpose": "upper_limit_interface_demonstration"},
    )
    neutrino_result = solver.solve_mass(
        neutrino_geometry,
        "electron_neutrino",
        1.0e-10,
        mapper,
    )
    if not w_result.success or not neutrino_result.success:
        raise RuntimeError("deterministic interface example failed to solve")
    assert w_result.mass_gev is not None and neutrino_result.mass_gev is not None

    return {
        "interface_status": "DEMONSTRATION_ONLY_NOT_EMPIRICAL_VALIDATION",
        "w_boson_result": w_result.to_dict(),
        "electron_neutrino_result": neutrino_result.to_dict(),
        "calibration_metadata": mapper.to_dict(),
        "comparison_metadata": {
            "W_boson": ValidationComparison.compare(
                w_result.mass_gev, w_reference
            ).to_dict(),
            "electron_neutrino": ValidationComparison.compare(
                neutrino_result.mass_gev, neutrino_reference
            ).to_dict(),
        },
        "warnings": [CALIBRATION_WARNING, NEUTRINO_WARNING],
        "frozen_predictions_changed": False,
        "empirical_derivation_inputs_used": False,
    }


def main() -> None:
    print(CALIBRATION_WARNING)
    print(NEUTRINO_WARNING)
    print(json.dumps(build_summary(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
