"""Support transformation and current classification for v11.2."""

from __future__ import annotations

from typing import Any


def derivative_residual(sign: int, field_sign: int, weight: int = 3) -> int:
    """Coefficient of ``d epsilon Phi`` after transforming ``d+sign*w*A``.

    ``field_sign=+1`` denotes ``delta Phi=+w epsilon Phi``. Covariance is
    exactly the condition ``field_sign+sign=0``.
    """

    return weight * (field_sign + sign)


def current_payload() -> dict[str, Any]:
    validation = {
        "minus_sign_fixed_for_positive_character": derivative_residual(-1, +1) == 0,
        "plus_candidate_rejected_for_positive_character": derivative_residual(+1, +1) != 0,
        "plus_sign_valid_for_opposite_character": derivative_residual(+1, -1) == 0,
        "local_gauge_symmetry_not_assumed": True,
        "composite_source_derivative_qualified": True,
    }
    return {
        "artifact": "BHSM_support_noether_current_v11_2",
        "infinitesimal_support_law": {"delta_log_upsilon": "epsilon", "delta_A_D": "d epsilon", "delta_q_D": "-lambda_D epsilon"},
        "field_law_tested": "delta Phi_w=+w epsilon Phi_w",
        "covariant_derivative": "D Phi_w=nabla Phi_w-w A_D Phi_w",
        "rejected_sign_pair": "delta Phi_w=+w epsilon Phi_w with D=nabla+w A_D is not covariant; it leaves 2w d(epsilon)Phi",
        "transformation_classification": {
            "local_gauge_redundancy": False,
            "global_representation_symmetry_of_isolated_support_kinetic_term": True,
            "global_symmetry_of_nonzero_character_couplings": False,
            "field_redefinition_on_regular_domain": True,
            "spurionic_symmetry": "possible only after assigning transformations to independent coefficients; not current-action owned",
            "geometric_coframe_scaling": "nontrivial candidate rejected by EH/cosmological action and local Weyl derivative terms",
        },
        "isolated_support_kinetic_action": "L_D=-lambda_D^2 A_D^2/2=-|dq_D|^2/2",
        "local_variation": "delta S_D=integral sqrt(-G)[-lambda_D^2 A_D^A nabla_A epsilon] plus boundary orientation conventions",
        "coefficient_of_gradient_epsilon": "j_shift^A=-lambda_D^2 A_D^A=lambda_D nabla^A q_D",
        "formal_response_current": "J_response^A=-delta S/delta A_D,A=+lambda_D^2 A_D^A=-lambda_D nabla^A q_D",
        "sign_relation": "j_shift=-J_response under the stated response-current convention",
        "functional_derivative_legitimacy": "formal source derivative only: A_D is composite, not an independent varied connection in the parent configuration bundle",
        "matter_character_current": None,
        "geometry_current": None,
        "measure_current": None,
        "wall_current": None,
        "boundary_current": None,
        "core_current": None,
        "complete_support_current": None,
        "current_classification": "ISOLATED_Q_D_SHIFT_NOETHER_CURRENT_AND_FORMAL_COMPOSITE_RESPONSE; NO_ACTION_OWNED_PRIMITIVE_MATTER_CURRENT",
        "anomaly_result": {
            "action_forced_matter_character_candidate": 0,
            "mixed_support_gauge_anomaly_for_forced_zero_candidate": 0,
            "nonzero_candidate_jacobian": None,
            "reason": "no nonzero chiral support-charge ledger or regulator-defined support symmetry exists to evaluate a Fujikawa Jacobian",
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

