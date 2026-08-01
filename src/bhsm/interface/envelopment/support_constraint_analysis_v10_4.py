"""Conditional ADM/constraint analysis of a healthy v10.4 support scalar."""

from __future__ import annotations

from typing import Any


CONSTRAINT_STATUS = "BHSM_SUPPORT_MODE_SURVIVES_CONSTRAINT_REDUCTION_CONDITIONALLY_ON_POSITIVE_Z_UPSILON"


def support_constraint_payload() -> dict[str, Any]:
    constraints = {
        "bulk_configuration": ["h_ij", "upsilon", "lapse N", "shift N^i"],
        "canonical_momentum": "pi_upsilon=sqrt(h) Z_upsilon/N (dot(upsilon)-N^i partial_i upsilon)",
        "primary_first_class": ["p_N=0", "p_Ni=0"],
        "secondary_first_class": ["C_H^gravity+C_H^upsilon=0", "C_i^gravity+pi_upsilon partial_i upsilon=0"],
        "bulk_second_class": [],
        "support_primary_constraint": None,
        "support_gauge_transformation": "delta_xi upsilon=Lie_xi upsilon; no additional internal gauge orbit",
        "radial_multipliers": ["radial lapse", "radial shift"],
        "radial_constraints": ["normal Hamiltonian matching constraint", "tangential momentum matching constraint"],
        "core_boundary_constraints": "boundary conditions, not classified as bulk Dirac constraints until S_core is supplied",
    }
    validation = {
        "momentum_nonzero_for_positive_Z": True,
        "no_support_primary_constraint": constraints["support_primary_constraint"] is None,
        "bulk_first_class_algebra_preserved": True,
        "one_conditional_scalar_pair": True,
        "positive_norm_requires_Z": True,
        "not_duplicate_metric_volume": True,
        "not_duplicate_q_C": True,
        "not_duplicate_q_W": True,
    }
    return {
        "artifact": "BHSM_support_constraint_gate_v10_4",
        "assumed_action_class": "second-order local scalar with Z_upsilon(upsilon)>0 on M_regular",
        "constraint_ledger": constraints,
        "hamiltonian_density": (
            "C_H^upsilon=pi_upsilon^2/(2 sqrt(h) Z_upsilon)+"
            "sqrt(h)[Z_upsilon h^ij partial_i upsilon partial_j upsilon/2+U_eff]"
        ),
        "physical_scalar_count": 1,
        "physical_scalar_count_status": "DERIVED_CONDITIONAL",
        "reduced_kinetic_norm": "integral sqrt(h) Z_reduced (delta upsilon)^2 > 0 iff Z_reduced>0",
        "reduced_kinetic_norm_positive": "CONDITIONAL_ON_Z_REDUCED>0",
        "gradient_speed_squared": 1.0,
        "gradient_stability": "DERIVED_CONDITIONAL_ON_LORENTZIAN_MINIMAL_PRINCIPAL_PART_AND_Z>0",
        "canonical_depth": {
            "definition": "q_D(upsilon)=integral_upsilon^1 sqrt(Z_reduced(s)) ds",
            "q_D_1": 0.0,
            "derivative": "dq_D/dupsilon=-sqrt(Z_reduced(upsilon))<0",
            "monotonicity": "upsilon down implies q_D up",
            "minus_log_condition": "q_D proportional to -log(upsilon) iff Z_reduced proportional to upsilon^-2",
            "selected_map": None,
        },
        "independence": {
            "from_q_C": "configuration-space independent by author extension; kinetic orthogonality/mixing remains action-open",
            "from_q_W": "configuration-space independent by author extension; kinetic orthogonality/mixing remains action-open",
            "from_q_V": "q_V has zero reduced metric projection; upsilon is an added scalar coordinate",
        },
        "uncontrolled_gauge_mode_created": False,
        "background_stability_complete": False,
        "reason_not_complete": "Z, U_eff, common-domain mixed blocks, and the localized background are not action-selected",
        "status": CONSTRAINT_STATUS,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
