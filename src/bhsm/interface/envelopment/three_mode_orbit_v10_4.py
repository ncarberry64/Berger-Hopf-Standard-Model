"""Relative-periodic orbit, interference, and Floquet gate for BHSM v10.4."""

from __future__ import annotations

from typing import Any


ORBIT_VERDICT = "BHSM_THREE_MODE_ORBIT_INELIGIBLE_WITHOUT_ACTION_OWNED_DEPTH_MODE"


def orbit_payload() -> dict[str, Any]:
    return {
        "relative_periodic_state": None,
        "period": None,
        "group_element_h": None,
        "q_C_orbit": None,
        "q_W_orbit": None,
        "q_D_orbit": None,
        "sigma_eta_metric_gauge_boundary_solution": None,
        "amplitudes": None,
        "relative_phases": None,
        "Hermitian_interference_operator": None,
        "output_energy": None,
        "field_particle_classification": None,
        "compact_timelike_branch": None,
        "color_open_nested_branch": None,
        "near_null_branch": None,
        "diffuse_field_branch": None,
        "monodromy_operator": None,
        "removed_coordinate_seam_modes": True,
        "physical_Floquet_multipliers": None,
        "stable_directions": None,
        "marginal_directions": None,
        "unstable_directions": None,
        "numerical_solve_performed": False,
        "reason": "q_D, the complete common action, and a stationary common background are absent",
        "verdict": ORBIT_VERDICT,
        "validation_passed": True,
    }
