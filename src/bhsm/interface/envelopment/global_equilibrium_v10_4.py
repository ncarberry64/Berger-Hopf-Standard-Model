"""Closed global equilibrium audit downstream of the v10.4 depth no-go."""

from __future__ import annotations

from typing import Any


GLOBAL_VERDICT = "BHSM_COMPLETE_ACTION_DOES_NOT_SELECT_A_UNIQUE_GLOBAL_GEOMETRY"


def global_equilibrium_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_global_equilibrium_gate_v10_4",
        "declared_parent_topology": "I_t x S7 with stratified M5/M4 compatibility data; a closed full spacetime solution is not selected",
        "complete_action_available": False,
        "stationary_background": None,
        "known_fixed_shape_candidates": {
            "round": "fixed-lapse extremum; static Lorentzian product requires unsupported dust-like stress",
            "Jensen": "fixed-lapse saddle and one unstable homogeneous Lorentzian shape mode",
        },
        "exact_dynamic_round_branch": "nonstationary cosh branch, not a localized three-mode equilibrium",
        "global_curvature_ratios": None,
        "Hopf_base_ratio_selected": None,
        "unique_dimensionless_shape": False,
        "global_topology_sector_selected": False,
        "relative_volumes_selected": False,
        "residual_scale_symmetry": True,
        "one_dimensional_modulus_only": False,
        "particle_inputs_used": [],
        "verdict": GLOBAL_VERDICT,
        "validation_passed": True,
    }
