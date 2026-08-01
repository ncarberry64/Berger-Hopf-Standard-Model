"""Closed-global-geometry and cosmic unit-anchor policy audit."""

from __future__ import annotations

from typing import Any


GLOBAL_VERDICT = "BHSM_COMPLETE_ACTION_DOES_NOT_SELECT_A_UNIQUE_GLOBAL_GEOMETRY"


def global_scale_payload() -> dict[str, Any]:
    forbidden = ["particle mass", "gauge coupling", "CKM", "PMNS", "Higgs value", "electroweak value"]
    particle_inputs_used: list[str] = []
    payload = {
        "artifact": "BHSM_global_scale_anchor_policy_v10_3",
        "ontology": "closed topology plus complete action selects the global equilibrium geometry",
        "stationary_global_solution": None,
        "unique_dimensionless_shape": False,
        "known_shape_candidates": ["round x=1", "Jensen x=1/5"],
        "current_static_Hopf_solution": False,
        "remaining_scale_symmetry": True,
        "derived_dimensionless_geometry": None,
        "empirical_global_unit_conversion": None,
        "cosmic_anchor_allowed": True,
        "maximum_cosmic_anchors": 1,
        "anchor_used": False,
        "particle_inputs_forbidden": forbidden,
        "particle_inputs_used": particle_inputs_used,
        "anchor_changes_dimensionless_ratios": False,
        "absolute_particle_scale": None,
        "verdict": GLOBAL_VERDICT,
    }
    payload["validation_passed"] = (
        len(particle_inputs_used) == 0
        and payload["maximum_cosmic_anchors"] == 1
        and payload["anchor_used"] is False
        and payload["absolute_particle_scale"] is None
    )
    return payload
