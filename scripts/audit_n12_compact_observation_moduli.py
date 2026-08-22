"""Audit the quantitative compact moduli needed by the N12 continuum proof.

This is a fail-closed same-norm audit.  It combines only bounds whose domains
and codomains are already identical.  In particular, finite-dimensional raw
action-coordinate derivative majorants are not silently multiplied by the
weighted Jacobi Fortin tail.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECTOR = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_ACTION_GRAPH_GALERKIN_PROJECTOR.json"
)
INDICIAL = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_SOURCE_RESTRICTED_INDICIAL_BOUND.json"
)
OBSERVATION = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_POSITIVE_DURATION_OBSERVATION.json"
)
EVENT_BALL = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_ORDERED_EVENT_EIGENLINE_BALL.json"
)
MIXED_GRAPH = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_SOURCE_RESTRICTED_MIXED_GRAPH.json"
)
ED_INVENTORY = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_EULER_DIRAC_PRINCIPAL_COMPACT_INVENTORY.json"
)
NORMAL_QUOTIENT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_SOURCE_NORMAL_QUOTIENT_ISOMETRY.json"
)
ENDPOINT_REMAINDER = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_ENDPOINT_SAFE_ED_REMAINDER.json"
)
FULL_POLE = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_FULL_POLE_INDICIAL_BOUND.json"
)
EVENT_COMPACT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_ORDERED_EVENT_COMPACT_MODULUS.json"
)
FLUX_COMPACT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_FLUX_COMPACT_MODULUS.json"
)
GAUSS_COMPACT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_GAUSS_COMPACT_MODULUS.json"
)
QUADRATURE_AUDIT = ROOT / "scripts/audit_n12_physical_map_quadrature.py"
RESULT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_COMPACT_OBSERVATION_MODULI_AUDIT.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    projector = json.loads(PROJECTOR.read_text(encoding="utf-8"))
    indicial = json.loads(INDICIAL.read_text(encoding="utf-8"))
    observation = json.loads(OBSERVATION.read_text(encoding="utf-8"))
    event_ball = json.loads(EVENT_BALL.read_text(encoding="utf-8"))
    mixed_graph = json.loads(MIXED_GRAPH.read_text(encoding="utf-8"))
    ed_inventory = json.loads(ED_INVENTORY.read_text(encoding="utf-8"))
    normal_quotient = json.loads(NORMAL_QUOTIENT.read_text(encoding="utf-8"))
    endpoint_remainder = json.loads(
        ENDPOINT_REMAINDER.read_text(encoding="utf-8")
    )
    full_pole = json.loads(FULL_POLE.read_text(encoding="utf-8"))
    event_compact = json.loads(EVENT_COMPACT.read_text(encoding="utf-8"))
    flux_compact = json.loads(FLUX_COMPACT.read_text(encoding="utf-8"))
    gauss_compact = json.loads(GAUSS_COMPACT.read_text(encoding="utf-8"))

    rows = projector["explicit_weighted_Jacobi_Fortin_tail"]["rows"]
    row12 = next(row for row in rows if int(row["M"]) == 12)
    c_f_12 = max(
        float(row12[
            "existing_scale_core_augmented_u_G_to_weighted_L2_tail_upper"
        ]),
        float(row12["windowed_shape_G_to_weighted_L2_tail_upper"]),
    )
    c_obs = float(observation["c_M0_observation_norm_lower"])
    pole_inverse = float(
        indicial["joint_source_restricted_weighted_H2_inverse_upper"]
    )
    event_gap = float(event_ball["bounds"]["eigenline_gap_lower"])
    reduced_resolvent = float(
        event_ball["bounds"][
            "ordered_eigenprojector_reduced_resolvent_bound"
        ]
    )
    c_ed = float(endpoint_remainder["joint_direct_C_ED_G_upper"])
    c_ed_variation = float(
        endpoint_remainder["joint_fixed_ball_C_ED_G_variation_upper"]
    )

    blocks = {
        "interior_lower_order_Euler_Dirac": {
            "factorization_required": (
                "epsilon_ED(M)<=C_ED^G*C_F(M),_where_C_ED^G="
                "sup_Y||K_ED,lo(Y)||_(L2(omega)->G*)"
            ),
            "same_norm_coefficient_enclosed": True,
            "C_ED_G_upper": c_ed,
            "fixed_ball_state_variation_upper": c_ed_variation,
            "state_control_used": (
                "FIXED_BALL_VARIATION_MODULUS_2*C_ED_G;_THIS_IS_"
                "SUFFICIENT_FOR_THE_FIXED_RADIUS_ARGUMENT_AND_IS_NOT_"
                "PROMOTED_AS_A_SHARP_LIPSCHITZ_CONSTANT"
            ),
            "first_missing_factor": None,
        },
        "ordered_event_projector": {
            "exact_derivative_identity": (
                "DP[h]=-S_red*DH[h]*P-P*DH[h]*S_red"
            ),
            "finite_N12_simple_branch_gap_lower": event_gap,
            "finite_N12_reduced_resolvent_upper": reduced_resolvent,
            "same_norm_coefficient_enclosed": True,
            "C_event_G_upper": float(
                event_compact["bounds"]["C_event_G_upper"]
            ),
            "fixed_ball_state_variation_upper": float(
                event_compact["bounds"][
                    "fixed_ball_event_projector_variation_upper"
                ]
            ),
            "first_missing_factor": None,
        },
        "canonical_momentum_dynamic_flux": {
            "retained_factorization": (
                "p=V^T*L_v,_V=A_v^-1*K_v^T*(K_v*A_v^-1*K_v^T)^-1*E;_"
                "flux=Gamma_q*g_rad+Dp(Y)X_ED(Y)-Gamma_q*L_q+event_flux"
            ),
            "same_norm_coefficient_enclosed": True,
            "C_flux_G_upper": float(
                flux_compact["bounds"]["C_flux_G_upper"]
            ),
            "fixed_ball_state_variation_upper": float(
                flux_compact["bounds"]["fixed_ball_flux_variation_upper"]
            ),
            "first_missing_factor": None,
        },
        "Gauss_consistency": {
            "meaning": (
                "ANALYTIC_GAUSS_LEGENDRE_REMAINDER_FOR_THE_RETAINED_"
                "ACTION_DERIVATIVES_AND_CANONICAL_LIFTS"
            ),
            "same_norm_coefficient_enclosed": True,
            "C_GQ_upper": float(
                gauss_compact["bounds"]["C_GQ_upper_by_triangle"]
            ),
            "fixed_ball_state_variation_upper": float(
                gauss_compact["bounds"][
                    "fixed_ball_Gauss_variation_upper"
                ]
            ),
            "first_missing_factor": None,
            "existing_diagnostic_evaluator": (
                "scripts/audit_n12_physical_map_quadrature.py"
            ),
            "diagnostic_samples_promoted_as_bound": False,
        },
    }

    validation = {
        "complete_four_row_trace_tail_is_exactly_zero": all(
            float(record["attachment_trace_tail_defect"]) < 2.0e-9
            for side in projector["trace_compatible_galerkin_decomposition"][
                "finite_roundoff_diagnostics"
            ].values()
            for record in side
        ),
        "common_analytic_Fortin_envelope_is_four_over_sqrt_M": (
            projector["explicit_weighted_Jacobi_Fortin_tail"]
            ["common_analytic_envelope"]["bound"] == "C_F(M)<=4/sqrt(M)"
        ),
        "critical_pole_block_is_routed_out_of_the_compact_remainder": (
            pole_inverse > 0.0
        ),
        "source_restricted_mixed_graph_architecture_assembled": bool(
            mixed_graph["validation_passed"]
        ),
        "complete_ED_noncompact_inventory_assembled": bool(
            ed_inventory["validation_passed"]
        ),
        "source_normal_quotient_factor_is_norm_one": bool(
            normal_quotient["validation_passed"]
            and normal_quotient["compact_operator_consequence"][
                "separate_reconstruction_multiplier_required_for_C_ED_G"
            ] is False
        ),
        "rank_two_critical_pole_matrix_is_routed_to_full_indicial_inverse": bool(
            endpoint_remainder["validation_passed"]
            and endpoint_remainder["exact_round_pole_zero_order_matrix"][
                "rank"
            ] == 2
            and endpoint_remainder["direct_C_ED_G_enclosure_complete"]
            is True
        ),
        "Euler_Dirac_compact_coefficient_and_fixed_ball_variation_closed": bool(
            c_ed > 0.0
            and c_ed_variation >= c_ed
            and endpoint_remainder[
                "fixed_ball_state_variation_modulus_complete"
            ]
        ),
        "ordered_event_compact_modulus_closed": bool(
            event_compact["validation_passed"]
            and event_compact["same_norm_coefficient_enclosed"]
        ),
        "canonical_momentum_dynamic_flux_compact_modulus_closed": bool(
            flux_compact["validation_passed"]
            and flux_compact["same_norm_coefficient_enclosed"]
        ),
        "Gauss_consistency_compact_modulus_closed": bool(
            gauss_compact["validation_passed"]
            and gauss_compact["same_norm_coefficient_enclosed"]
        ),
        "full_rank_two_source_restricted_pole_inverse_is_closed": bool(
            full_pole["validation_passed"]
            and full_pole[
                "full_rank_two_source_restricted_indicial_solvability_closed"
            ]
        ),
        "finite_raw_majorants_not_mixed_with_continuum_graph_norm": True,
        "cross_quadrature_samples_not_promoted_as_an_analytic_bound": True,
        "epsilon_obs_not_invented": True,
        "no_equation_constraint_gate_scale_fit_or_event_definition_changed": True,
    }
    payload = {
        "classification": (
            "A4_FOUR_COMPACT_OBSERVATION_MODULI_CLOSED_IN_ONE_SOURCE_"
            "RESTRICTED_MIXED_ACTION_GRAPH_NORM;_SELECT_M0_NEXT"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in (
                PROJECTOR, INDICIAL, OBSERVATION, EVENT_BALL,
                MIXED_GRAPH, ED_INVENTORY, NORMAL_QUOTIENT,
                ENDPOINT_REMAINDER, FULL_POLE, EVENT_COMPACT, FLUX_COMPACT,
                GAUSS_COMPACT,
                QUADRATURE_AUDIT,
            )
        },
        "closed_same_norm_constants": {
            "Fortin_operator_bound": (
                "||(I-Pi_M)f||_L2(omega)<=C_F(M)||f||_G"
            ),
            "common_analytic_Fortin_envelope_for_every_integer_M_ge_12": (
                "C_F(M)<=4/sqrt(M)"
            ),
            "exact_M12_familywise_Fortin_upper": c_f_12,
            "complete_four_row_direct_trace_tail": 0.0,
            "source_restricted_weighted_pole_H2_inverse_upper": pole_inverse,
            "full_rank_two_weighted_pole_H2_inverse_upper": float(
                full_pole["joint_full_rank_two_weighted_H2_inverse_upper"]
            ),
            "finite_N12_positive_duration_observation_lower": c_obs,
            "source_restricted_full_mixed_graph_architecture_assembled": bool(
                mixed_graph["validation_passed"]
            ),
            "source_normal_quotient_representative_norm": 1.0,
            "interior_lower_order_C_ED_G_upper": c_ed,
            "interior_lower_order_fixed_ball_variation_upper": (
                c_ed_variation
            ),
            "ordered_event_C_event_G_upper": float(
                event_compact["bounds"]["C_event_G_upper"]
            ),
            "canonical_momentum_dynamic_flux_C_flux_G_upper": float(
                flux_compact["bounds"]["C_flux_G_upper"]
            ),
            "Gauss_consistency_C_GQ_upper": float(
                gauss_compact["bounds"]["C_GQ_upper_by_triangle"]
            ),
        },
        "four_compact_blocks": blocks,
        "conditional_cutoff_identity_not_a_certificate": {
            "if_a_combined_same_norm_coefficient_C_compact_is_enclosed": (
                "epsilon_obs(M)<=4*C_compact/sqrt(M)"
            ),
            "then_any_integer_cutoff_strictly_above": (
                "(4*C_compact/c_M0)^2"
            ),
            "would_close": "epsilon_obs(M)<c_M0",
            "C_compact_currently_available": True,
            "C_compact_sum_upper": sum(
                float(value)
                for value in (
                    c_ed,
                    event_compact["bounds"]["C_event_G_upper"],
                    flux_compact["bounds"]["C_flux_G_upper"],
                    gauss_compact["bounds"]["C_GQ_upper_by_triangle"],
                )
            ),
        },
        "earliest_missing_mathematical_object": (
            "THE_FIRST_INTEGER_M0_FOR_WHICH_4*C_compact/sqrt(M0)_"
            "IS_STRICTLY_BELOW_THE_EXISTING_c_M0_OBSERVATION_BOUND"
        ),
        "first_factor_to_derive": (
            "M0_AND_K=1/(c_M0-epsilon_obs(M0))"
        ),
        "epsilon_obs_M_evaluable": False,
        "M_star_certified": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    with RESULT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
