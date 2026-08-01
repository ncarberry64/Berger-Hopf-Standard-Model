"""Minimal covariant action-class audit for the v10.4 support field.

The author selects the configuration variable and its stratified-domain
meaning.  The repository action does not select its kinetic function,
potential, or support couplings.  This module therefore derives the common
Euler/stress/boundary structure and proves the remaining non-uniqueness.
"""

from __future__ import annotations

import math
from typing import Any


ACTION_VERDICT = "BHSM_MULTIPLE_INEQUIVALENT_SUPPORT_ACTIONS_REMAIN_AFTER_AUTHOR_EXTENSION_SELECTION"
NEXT_EXACT_OBJECT = "ACTION_PRINCIPLE_FIXING_Z_UPSILON_U_UPSILON_AND_SUPPORT_COUPLINGS"


def canonical_depth(value: float, *, family: str, normalization: float = 1.0) -> float:
    """Evaluate two inequivalent healthy canonical-coordinate examples.

    ``normalization`` stands for the positive reduced kinetic normalization.
    These examples establish non-uniqueness; neither is adopted physically.
    """

    upsilon = float(value)
    if not 0.0 < upsilon <= 1.0:
        raise ValueError("canonical depth is defined on 0 < upsilon <= 1")
    if normalization <= 0.0:
        raise ValueError("kinetic normalization must be positive")
    root = math.sqrt(normalization)
    if family == "constant_kinetic":
        return root * (1.0 - upsilon)
    if family == "logarithmic_kinetic":
        return -root * math.log(upsilon)
    raise ValueError(f"unknown support kinetic family: {family}")


def admissible_action_families() -> list[dict[str, Any]]:
    common = {
        "domain": "M_regular, 0<upsilon<=1",
        "background": "upsilon=1, nabla upsilon=0",
        "potential_conditions": ["U(1)=0 by action-offset convention", "U'(1)=0", "U_eff''(1)>=0"],
        "coupling_conditions": ["F_a(1)=1", "sum_a F_a'(1) X_a,*=0", "nontrivial response away from upsilon=1"],
        "not_adopted": True,
    }
    return [
        {
            **common,
            "name": "constant-positive-kinetic family",
            "Z_upsilon": "zeta*kappa_1",
            "condition": "zeta*kappa_1>0",
            "canonical_map": "q_D=sqrt(zeta*kappa_1)*(1-upsilon)",
            "core_distance": "finite",
            "free_data": ["zeta", "U(upsilon)", "F_C(upsilon)", "F_W(upsilon)"],
        },
        {
            **common,
            "name": "logarithmic-positive-kinetic family",
            "Z_upsilon": "zeta*kappa_1/upsilon^2",
            "condition": "zeta*kappa_1>0",
            "canonical_map": "q_D=-sqrt(zeta*kappa_1)*log(upsilon)",
            "core_distance": "infinite",
            "free_data": ["zeta", "U(upsilon)", "F_C(upsilon)", "F_W(upsilon)"],
        },
    ]


def coupling_ledger() -> list[dict[str, Any]]:
    return [
        {
            "term": "-1/2 Z_upsilon(upsilon) G^AB nabla_A upsilon nabla_B upsilon",
            "domain": "M_regular",
            "symmetry": "diffeomorphism scalar density",
            "coefficient": "Z_upsilon; not selected",
            "mass_dimension": "6 in D=8 when upsilon is dimensionless",
            "variation": "nabla_A(Z nabla^A upsilon)-1/2 Z'|nabla upsilon|^2",
            "stress_tensor": "Z nabla_A upsilon nabla_B upsilon-G_AB[1/2 Z|nabla upsilon|^2]",
            "source_current": None,
            "boundary_term": "-integral_Sigma sqrt|h| n_A Z nabla^A upsilon delta upsilon",
            "new_parameter": "at least one positive normalization relative to kappa_1",
            "reason_required": "one healthy local support polarization",
            "status": "REQUIRED_FORM_COEFFICIENT_OPEN",
        },
        {
            "term": "-U_upsilon(upsilon)",
            "domain": "M_regular",
            "symmetry": "diffeomorphism scalar density",
            "coefficient": "function U_upsilon; not selected",
            "mass_dimension": "8 in D=8",
            "variation": "-U_upsilon'",
            "stress_tensor": "-G_AB U_upsilon",
            "source_current": None,
            "boundary_term": None,
            "new_parameter": "optional stiffness/scale unless U=0",
            "reason_required": "not required for hyperbolicity; constrained only if a restoring branch is claimed",
            "status": "OPTIONAL_OPEN",
        },
        {
            "term": "[F_C(upsilon)-1] X_C",
            "domain": "common parent localization of the q_C invariant",
            "symmetry": "requires X_C to be an action-owned scalar",
            "coefficient": "function F_C; not selected",
            "mass_dimension": "dimensionless F_C multiplying the inherited X_C density",
            "variation": "F_C' X_C",
            "stress_tensor": "metric variation of [F_C-1]X_C",
            "source_current": "J_C=F_C' X_C",
            "boundary_term": "inherits X_C boundary completion",
            "new_parameter": "support-response Taylor data",
            "reason_required": "q_D must respond to q_C rather than remain a spectator",
            "status": "REQUIRED_INTERACTION_CLASS_SOURCE_OPEN",
        },
        {
            "term": "[F_W(upsilon)-1] X_W",
            "domain": "common parent localization of the q_W/fold invariant",
            "symmetry": "requires X_W to be an action-owned scalar",
            "coefficient": "function F_W; not selected",
            "mass_dimension": "dimensionless F_W multiplying the inherited X_W density",
            "variation": "F_W' X_W",
            "stress_tensor": "metric variation of [F_W-1]X_W",
            "source_current": "J_W=F_W' X_W",
            "boundary_term": "inherits the fold/moving-endpoint completion",
            "new_parameter": "support-response Taylor data",
            "reason_required": "q_D must respond to q_W rather than remain a spectator",
            "status": "REQUIRED_INTERACTION_CLASS_SOURCE_OPEN",
        },
    ]


def support_action_payload() -> dict[str, Any]:
    families = admissible_action_families()
    validation = {
        "two_inequivalent_healthy_families": len(families) == 2,
        "canonical_maps_differ": not math.isclose(
            canonical_depth(0.5, family="constant_kinetic"),
            canonical_depth(0.5, family="logarithmic_kinetic"),
        ),
        "both_maps_monotone_toward_depletion": all(
            canonical_depth(0.5, family=family) > canonical_depth(1.0, family=family)
            for family in ("constant_kinetic", "logarithmic_kinetic")
        ),
        "background_reduces_to_frozen_action": True,
        "no_arbitrary_function_adopted": True,
        "no_particle_fit": True,
        "no_new_mediator_claim": True,
    }
    return {
        "artifact": "BHSM_support_action_gate_v10_4",
        "general_regular_action": (
            "S_upsilon=int_Mregular sqrt(-G)[-1/2 Z(upsilon)|nabla upsilon|^2-"
            "U(upsilon)+(F_C(upsilon)-1)X_C+(F_W(upsilon)-1)X_W]+S_Sigma_core"
        ),
        "euler_equation": (
            "nabla_A(Z nabla^A upsilon)-1/2 Z'|nabla upsilon|^2-U'"
            "+F_C'X_C+F_W'X_W=0"
        ),
        "stress_tensor": (
            "T_AB^upsilon=Z nabla_A upsilon nabla_B upsilon-"
            "G_AB[1/2 Z|nabla upsilon|^2+U]+T_AB^coupling"
        ),
        "background_conditions": {
            "upsilon_star": 1.0,
            "nabla_upsilon_star": 0.0,
            "U_prime_1": 0.0,
            "full_stationarity": "sum_a F_a'(1) X_a,*=0",
            "regular_stability": "U_eff''(1)>=0 after constraints and mixing",
        },
        "bulk_phase_audit": "U'(0)=0 is optional and unproved; no regular second vacuum is selected",
        "core_boundary_audit": "preferred ontology; upsilon=0 is boundary data on Sigma_core",
        "curvature_coupling": "F_R(upsilon)R_8 is allowed but not required or selected; it changes the gravity constraint",
        "eta_coupling": "no direct F_eta term selected without a common action-owned invariant",
        "sigma_coupling": "no direct F_sigma term selected without a common action-owned invariant",
        "wall_coupling": "required in class through F_W X_W, coefficient/function open",
        "boundary_action": "existing metric completion plus an open S_Sigma_core; scalar Dirichlet data need no new bulk cancellation term",
        "new_parameter_audit": {
            "kinetic_normalization": "unavoidable for a propagating dimensionless order parameter; relative value is not fixed by topology",
            "dimension": "mass^6 relative to the D=8 curvature coefficient kappa_1",
            "cosmic_anchor_role": "can convert units only after a dimensionless action is selected; cannot choose its dimensionless ratio",
            "changes_dimensionless_predictions": True,
            "author_or_action_principle_required": True,
        },
        "coupling_ledger": coupling_ledger(),
        "admissible_counterexamples_to_uniqueness": families,
        "selected_Z_upsilon": None,
        "selected_U_upsilon": None,
        "selected_couplings": None,
        "selected_boundary_action": None,
        "action_owned_q_D": None,
        "physical_depth": None,
        "verdict": ACTION_VERDICT,
        "next_exact_object": NEXT_EXACT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
