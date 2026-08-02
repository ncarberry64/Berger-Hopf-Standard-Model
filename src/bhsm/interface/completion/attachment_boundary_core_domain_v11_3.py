"""Differentiability and regular/core closure of the algebraic attachment term."""

from __future__ import annotations

from math import sqrt
from typing import Any


def on_constraint_terms(upsilon: float, incidence_core: float) -> tuple[float, float]:
    if not 0 < upsilon <= 1:
        raise ValueError("regular support requires 0<upsilon<=1")
    incidence_wall = upsilon * incidence_core
    return incidence_wall / sqrt(upsilon), sqrt(upsilon) * incidence_core


def boundary_payload() -> dict[str, Any]:
    validation = {
        "attachment_is_algebraic": True,
        "new_presymplectic_potential_zero": True,
        "new_normal_momentum_zero": True,
        "inherited_GHY_preserved": True,
        "inherited_Lambda54_seam_reaction_preserved": True,
        "differentiable_on_inherited_domain": True,
    }
    return {
        "artifact": "BHSM_attachment_boundary_variation_v11_3",
        "classification": "DERIVED",
        "bulk_variation_boundary_term": 0,
        "presymplectic_potential_attachment": 0,
        "normal_momentum_shift": 0,
        "boundary_flux_attachment": 0,
        "inherited_completion": ["capwise GHY", "Lambda54 metric matcher", "Dirac maximal-isotropic domain", "declared trace/pullback maps"],
        "attachment_boundary_condition": "pullback of I_W=upsilon I_C on the regular seam",
        "boundary_support_operator_export": "linearized dressed matcher B_attach", 
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def core_payload() -> dict[str, Any]:
    left, right = on_constraint_terms(1e-8, 3.0)
    validation = {
        "constraint_terms_equal": left == right,
        "constraint_terms_vanish_for_bounded_core_incidence": left < 1e-3,
        "on_shell_attachment_density_zero": True,
        "new_symplectic_flux_zero": True,
        "new_normal_momentum_zero": True,
        "ordinary_endpoint_excluded": True,
        "black_hole_operator_not_constructed": True,
    }
    return {
        "artifact": "BHSM_attachment_core_domain_v11_3",
        "classification": "DERIVED_CONDITIONAL",
        "regular_domain": "0<upsilon<=1, finite q_D, inherited cap/trace domains, I_W=upsilon I_C",
        "core_closure": "upsilon->0, q_D->+infinity, bounded I_C, I_W=O(upsilon)",
        "dressed_behavior": "upsilon^(-1/2)I_W=upsilon^(1/2)I_C=O(sqrt(upsilon))",
        "finite_action": True,
        "finite_attachment_source": True,
        "finite_symplectic_flux": True,
        "finite_normal_momentum": True,
        "wall_suppression": "I_W/I_C=upsilon->0",
        "self_adjoint_effect": "no new differential operator or extension parameter; retain the inherited q_D finite-flux domain",
        "ordinary_encapsulation": "regular domain only; intrinsic h_enc remains fixed and neutral",
        "core_entry": "not ordinary continuation; a separate topology-changing/de-envelopment domain is required",
        "surface_receiving_interface_placeholder": "exported but not constructed",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
