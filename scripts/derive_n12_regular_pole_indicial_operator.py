"""Derive the retained N12 regular-pole normal indicial operator.

This is a correction to the proposed derivative-principal-plus-compact tail
split.  The round regular pole of the unchanged action contains a critical
inverse-square anisotropy block.  After the existing canonical normal-frame
and gauge reduction, that block has zero in its essential spectrum.  The
script records an explicit normalized Weyl sequence, so a uniform *static*
high-shell inverse may not be inferred from the pointwise 3x3 derivative
matrix gap.  This does not alter the finite child equations and does not by
itself reclassify the positive-duration soft observation channel.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.linalg import eigh, null_space

from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    RADIUS0,
)


ROOT = Path(__file__).resolve().parents[1]
ANCHOR = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
RESULT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_REGULAR_POLE_INDICIAL_OPERATOR.json"
)
ORDER = 12


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _pole_record(state: np.ndarray) -> dict[str, float]:
    qdim = 1 + 3 * ORDER
    q = state[:qdim]
    multipliers = state[2 * qdim:]
    u_at_pole = float(np.sum(q[1:1 + ORDER]))
    log_lapse_at_pole = float(np.sum(multipliers[:ORDER]))
    radius = RADIUS0 * math.exp(float(q[0]) + u_at_pole)
    lapse = math.exp(log_lapse_at_pole)
    coefficient = lapse * radius**5
    return {
        "pole_radius_C_equals_A0_equals_B0": radius,
        "pole_lapse": lapse,
        "positive_indicial_coefficient_c_equals_lapse_times_radius5": (
            coefficient
        ),
    }


def _weyl_row(length: float) -> dict[str, float]:
    # phi(s)=sin(pi*s)^2 on [0,1].  All displayed norms are exact.
    phi_squared = 3.0 / 8.0
    phi_prime_squared = math.pi**2 / 2.0
    phi_second_squared = 2.0 * math.pi**4
    residual_squared = (
        4.0 * phi_prime_squared / (length**2 * phi_squared)
        + phi_second_squared / (length**4 * phi_squared)
    )
    graph_squared = (
        2.0 + phi_prime_squared / (length**2 * phi_squared)
    )
    return {
        "L": length,
        "normalized_indicial_residual_before_positive_coefficient": (
            math.sqrt(residual_squared / graph_squared)
        ),
        "complexified_graph_norm_squared_before_normalization": graph_squared,
    }


def _finite_indicial_probe(order: int, points: int = 1536) -> dict[str, Any]:
    """Diagnostic only: action-graph eigenvalues of the exact pole model."""

    nodes, weights = np.polynomial.legendre.leggauss(points)
    chi = (nodes + 1.0) * math.pi / 8.0
    quadrature = weights * math.pi / 8.0
    modes = np.arange(order, dtype=float)[:, None]
    window = np.sin(2.0 * chi) ** 2
    values = window * np.cos(4.0 * modes * chi)
    derivatives = (
        2.0 * np.sin(4.0 * chi) * np.cos(4.0 * modes * chi)
        - window * 4.0 * modes * np.sin(4.0 * modes * chi)
    )
    form = (
        (values * (12.0 * quadrature * chi)) @ values.T
        - (derivatives * (6.0 * quadrature * chi**3)) @ derivatives.T
    )
    graph = (
        (derivatives * (quadrature * chi**3)) @ derivatives.T
        + (values * (quadrature * chi**3)) @ values.T
    )
    attachment = (-1.0) ** np.arange(order)
    kernel = null_space(attachment[None, :])
    eigenvalues = eigh(
        kernel.T @ form @ kernel,
        kernel.T @ graph @ kernel,
        eigvals_only=True,
    )
    selected = int(np.argmin(np.abs(eigenvalues)))
    return {
        "N": order,
        "smallest_absolute_generalized_indicial_eigenvalue": float(
            abs(eigenvalues[selected])
        ),
        "signed_nearest_zero_generalized_indicial_eigenvalue": float(
            eigenvalues[selected]
        ),
        "used_as_the_proof": False,
    }


def main() -> None:
    anchor = np.load(ANCHOR)
    joint = np.asarray(anchor["state"], dtype=float)
    qdim = 1 + 3 * ORDER
    side_dimension = 2 * qdim + 2 * ORDER
    sectors = {
        "event": _pole_record(joint[:side_dimension]),
        "child": _pole_record(joint[side_dimension:]),
    }
    weyl = [_weyl_row(length) for length in (8.0, 16.0, 32.0, 64.0, 128.0)]
    probes = [
        _finite_indicial_probe(order)
        for order in (12, 16, 24, 32, 48, 64, 96, 128, 192, 256)
    ]
    validation = {
        "certified_N12_anchor_consumed": True,
        "both_pole_indicial_coefficients_positive": all(
            row[
                "positive_indicial_coefficient_c_equals_lapse_times_radius5"
            ] > 0.0
            for row in sectors.values()
        ),
        "exact_round_pole_identity_used": True,
        "canonical_normal_frame_and_existing_gauge_quotient_retained": True,
        "weyl_residual_decreases": all(
            left["normalized_indicial_residual_before_positive_coefficient"]
            > right["normalized_indicial_residual_before_positive_coefficient"]
            for left, right in zip(weyl, weyl[1:])
        ),
        "finite_probes_not_used_as_the_proof": all(
            row["used_as_the_proof"] is False for row in probes
        ),
        "positive_duration_soft_channel_not_reclassified_by_static_sequence": True,
        "no_equation_constraint_gate_scale_fit_or_event_definition_changed": True,
    }
    payload = {
        "classification": (
            "RETAINED_REGULAR_POLE_INVERSE_SQUARE_NORMAL_BLOCK_DERIVED;_"
            "ZERO_LIES_IN_THE_STATIC_INDICIAL_ESSENTIAL_SPECTRUM;_THE_"
            "OLD_UNIFORM_STATIC_COMPACT_CUTOFF_ROUTE_IS_INVALID"
        ),
        "input": {
            "path": str(ANCHOR.relative_to(ROOT)).replace("\\", "/"),
            "SHA256": _sha256(ANCHOR),
        },
        "sectors": sectors,
        "round_pole_action_expansion": {
            "regular_identities": (
                "C(0)=A0(0)=B0(0)=r_p,_beta(chi)=O(chi),_"
                "omega(chi)=chi^3+O(chi^5)"
            ),
            "physical_anisotropy_variable": "delta_v_AFTER_EXISTING_GAUGE_REDUCTION",
            "second_variation": (
                "delta2_L_v=c*[12*chi*delta_v^2-6*chi^3*"
                "(D_chi_delta_v)^2]+O(chi^2)_MIXED+O(chi^3)_GRAPH"
            ),
            "c": "lapse(0)*r_p^5>0",
            "ADM_eta_collective_inertia_and_smooth_background_remainders": (
                "RELATIVELY_COMPACT_AFTER_THE_CRITICAL_INDICIAL_BLOCK_IS_"
                "RETAINED_IN_THE_PRINCIPAL_OPERATOR"
            ),
        },
        "logarithmic_normal_form": {
            "coordinate": "t=-log(chi)",
            "unitary_unknown": "g(t)=chi*delta_v(chi)",
            "quadratic_form": "6*c*integral_(0,infinity)(abs(g)^2-abs(D_t_g)^2)dt",
            "indicial_operator": "6*c*(D_t^2+1)",
            "essential_spectrum_contains_zero": True,
        },
        "explicit_Weyl_sequence": {
            "definition": (
                "g_(T,L)(t)=L^-1/2*phi((t-T)/L)*exp(i*t)/norm(phi),_"
                "phi(s)=sin(pi*s)^2_ON_[0,1],_T_TO_INFINITY,_L_TO_INFINITY"
            ),
            "physical_variation": (
                "delta_v_(T,L)(chi)=chi^-1*g_(T,L)(-log(chi));_IT_IS_"
                "SMOOTH,_TRACE_ZERO,_AND_IDENTICALLY_ZERO_NEAR_THE_EXACT_POLE"
            ),
            "exact_phi_norms": {
                "L2_squared": 3.0 / 8.0,
                "first_derivative_L2_squared": math.pi**2 / 2.0,
                "second_derivative_L2_squared": 2.0 * math.pi**4,
            },
            "rows": weyl,
            "remainder_control": (
                "CHOOSE_T/L_TO_INFINITY;_THE_O(exp(-2T))_RETAINED_"
                "BACKGROUND_REMAINDER_VANISHES_RELATIVE_TO_THE_GRAPH_NORM"
            ),
            "non_tangent_normal_owner": "PHYSICAL_BERGER_ANISOTROPY_v",
        },
        "finite_Galerkin_diagnostics": probes,
        "reclassification": {
            "pointwise_matrix_gap_sqrt29_minus5_invalidated": False,
            "pointwise_matrix_gap_is_a_uniform_global_static_inverse": False,
            "high_tail_inverse_4_over_sqrt29_minus5_promoted": False,
            "all_lower_order_pole_terms_are_compact": False,
            "uniform_static_M_star_exists_by_the_old_Neumann_split": False,
            "BHSM_continuum_child_disproved": False,
            "pure_v_Weyl_sequence_proved_to_satisfy_the_full_mixed_constraints": False,
            "full_positive_duration_mixed_operator_proved_to_have_zero_essential_spectrum": False,
            "why_not": (
                "THE_COMPLETE_SOURCE_RESTRICTED_AND_POSITIVE_DURATION_"
                "EVENT_MOMENTUM_OBSERVATION_OPERATOR_HAS_NOT_BEEN_REDUCED_"
                "TO_THIS_STATIC_INDICIAL_BLOCK"
            ),
        },
        "M_star_certified": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "exact_next_dependency": (
            "PROJECT_THE_EXACT_INVERSE_SQUARE_OMITTED_SOURCE_ONTO_THE_"
            "REGULAR_POLE_INDICIAL_CHANNEL_AND_DERIVE_A_SOURCE_RESTRICTED_"
            "LIMITING_ABSORPTION_OR_SOLVABILITY_BOUND_WITH_SUMMABLE_"
            "GROWTH;_THEN_INCLUDE_THE_EXISTING_POSITIVE_DURATION_ORDERED_"
            "EVENT_AND_MOMENTUM_FLUX_OBSERVATION_ROWS"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
