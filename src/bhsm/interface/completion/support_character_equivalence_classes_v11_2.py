"""Equivalence and physical-flatness disposition of support characters."""

from __future__ import annotations

from typing import Any


def equivalence_class_payload() -> dict[str, Any]:
    pure_gauge = {
        "local_curvature": "dA_D=0 on every smooth regular chart",
        "regular_field_redefinition": "Phi_w -> upsilon^(-w) Phi_w removes A_D from D=nabla-wA_D",
        "globally_trivial_on_regular_domain": "yes when upsilon is single-valued and strictly positive and the bundle has no extra support holonomy",
        "boundary_conditions_preserved": None,
        "wall_topology_preserved": None,
        "core_map_invertible": False,
        "nontrivial_holonomy": "none from exact d log upsilon on a single-valued regular chart; extra bundle data are not supplied",
        "fiber_integration_preserved": None,
        "quantum_measure_preserved": None,
        "classification": "LOCALLY_PURE_GAUGE_AS_A_CONNECTION_FORM_BUT_NOT_PROVEN_PHYSICALLY_REMOVABLE_AT_BOUNDARY_OR_CORE",
    }
    rescaling = {
        "candidate": "w_a->c w_a, lambda_D->c lambda_D",
        "beta_a_invariant": "beta_a=w_a/lambda_D",
        "connection_couplings_in_q_D_coordinates": "depend on beta_a",
        "canonical_q_D_kinetic_term_invariant": False,
        "reason": "q_D->c q_D changes the canonically normalized kinetic coefficient unless an action coefficient is also transformed",
        "complete_symplectic_equivalence": None,
        "boundary_core_equivalence": None,
        "common_scaling_quotiented": False,
    }
    validation = {
        "flat_not_equated_with_irrelevance": pure_gauge["boundary_conditions_preserved"] is None,
        "regular_redefinition_explicit": bool(pure_gauge["regular_field_redefinition"]),
        "core_singularity_explicit": pure_gauge["core_map_invertible"] is False,
        "beta_invariance_recorded": bool(rescaling["beta_a_invariant"]),
        "normalization_not_prematurely_quotiented": not rescaling["common_scaling_quotiented"],
    }
    return {
        "artifact": "BHSM_support_character_equivalence_classes_v11_2",
        "pure_gauge_test": pure_gauge,
        "common_rescaling_test": rescaling,
        "number_of_action_allowed_null_directions": 5,
        "null_directions_form_one_common_normalization": False,
        "multiple_physically_equivalent_ledgers_proven": False,
        "multiple_physically_inequivalent_ledgers_proven": False,
        "Haar_scale_disposition": "UNRESOLVED: five independent character directions remain, and canonical/domain equivalence is incomplete",
        "status": "BHSM_SUPPORT_CHARACTER_EQUIVALENCE_QUOTIENT_EXHAUSTED_BUT_NOT_CLOSED",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

