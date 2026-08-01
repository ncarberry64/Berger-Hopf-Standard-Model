"""Downstream orbit/Floquet gate after the v10.4 support-action audit."""

from __future__ import annotations

from typing import Any


ORBIT_STATUS = "BHSM_SUPPORT_RELATIVE_PERIODIC_ORBIT_BLOCKED_BY_INCOMPLETE_THREE_MODE_ACTION"


def support_orbit_payload() -> dict[str, Any]:
    prerequisites = {
        "unique_support_action": False,
        "complete_common_three_mode_domain": False,
        "positive_full_reduced_kinetic_matrix": False,
        "stationary_localized_background": False,
        "complete_boundary_and_core_data": False,
        "gauge_fixed_nonlinear_equations": False,
    }
    return {
        "artifact": "BHSM_support_orbit_gate_v10_4",
        "relative_periodic_condition": "Phi(tau+T)=h.Phi(tau)",
        "required_state": ["q_C", "q_W", "q_D", "eta", "sigma", "metric", "gauge dressing", "core boundary data"],
        "prerequisites": prerequisites,
        "orbit": None,
        "monodromy_operator": None,
        "gauge_zero_modes_removed": False,
        "constraint_zero_modes_removed": False,
        "physical_floquet_spectrum": None,
        "sector_phase_eigenspaces": None,
        "frozen_family_ledger_relation": None,
        "physical_outputs": {
            "timelike_self_envelopment": None,
            "color_open_nested_sub_envelopment": None,
            "near_null_envelopment": None,
            "diffuse_field_output": None,
            "core_transition_state": None,
            "unstable_branch": None,
        },
        "quantum_core_interface": {
            "shape": "Phi_in^M4 -> Phi_core -> Phi_out,a^M4",
            "transition_amplitude": None,
            "norm_preservation": None,
            "probability_normalization": None,
            "no_signalling": None,
            "detector_environment_coupling": None,
            "quantum_mechanics_derived": False,
        },
        "numerical_solve_performed": False,
        "status": ORBIT_STATUS,
        "validation_passed": not any(prerequisites.values()),
    }
