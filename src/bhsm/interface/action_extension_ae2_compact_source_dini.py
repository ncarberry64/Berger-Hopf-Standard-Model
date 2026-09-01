"""Tail-independent source-Dini control for factorized AE2 channels.

The proof stays in the first-order transfer system.  It never differentiates
the far-tail superpotential and it does not assume a limiting-absorption
normalization bound.
"""

from __future__ import annotations

import cmath
import math


def compact_source_dini_trace_norm_bound(
    *,
    source_interval_length: float,
    exp_minus_primitive_abs_upper: float,
    weighted_source_endpoint_abs: float,
    weighted_source_total_variation: float,
) -> dict[str, float | bool | str]:
    """Bound the exact source-Dini integral by a trace norm.

    Put ``S(t)=integral_0^t s``, ``b=exp(-S)``, ``g=delta s`` and
    ``F=exp(2*S)*g`` on a compact source interval ``[0,L]``.  The natural
    factorized graph gives, on a spectral fiber of ``K=A* A`` at
    ``lambda>0``,

    ``A u=-lambda*T_s u``,
    ``T_s=M_exp(S) V M_exp(-S)``.

    Hence the first form vertex divided by ``lambda`` is the diagonal of
    ``C=-(T_s* M_g+M_g T_s)``.  After conjugation by ``M_b``, its scalar
    kernel is ``-b(t) F(max(t,r)) b(r)``.  If ``F`` is of bounded variation,
    this kernel is a rank-one Stieltjes integral and

    ``||C||_1 <= ||b||_infinity^2*(L*|F(L)|+integral t d|F|(t))``.

    The supplied total variation gives the conservative final bound with
    ``t<=L``.  Compactly supported retained directions have ``F(L)=0``.
    No datum beyond ``L`` enters, so the estimate is independent of every
    positive admissible far tail.
    """

    length = float(source_interval_length)
    b_upper = float(exp_minus_primitive_abs_upper)
    endpoint = float(weighted_source_endpoint_abs)
    variation = float(weighted_source_total_variation)
    values = (length, b_upper, endpoint, variation)
    if not all(math.isfinite(value) and value >= 0.0 for value in values):
        raise ValueError("finite nonnegative compact-source inputs required")
    if length == 0.0 or b_upper == 0.0:
        raise ValueError("positive source length and exponential bound required")
    rank_one_endpoint_bound = length * endpoint
    stieltjes_rank_one_bound = length * variation
    trace_norm = b_upper**2 * (
        rank_one_endpoint_bound + stieltjes_rank_one_bound
    )
    return {
        "source_interval_length": length,
        "exp_minus_primitive_abs_upper": b_upper,
        "weighted_source_endpoint_abs": endpoint,
        "weighted_source_total_variation": variation,
        "rank_one_endpoint_trace_norm_upper": rank_one_endpoint_bound,
        "stieltjes_rank_one_trace_norm_upper": stieltjes_rank_one_bound,
        "quotient_operator_trace_norm_upper": trace_norm,
        "source_Dini_integral_upper": trace_norm,
        "weighted_source_BV_required": True,
        "far_tail_datum_used": False,
        "strict_gap_required": False,
        "threshold_normalization_supremum_required": False,
    }


def smooth_compact_source_dini_bound(
    *,
    superpotential_abs_upper: float,
    source_interval_length: float,
    source_abs_l1: float,
    source_derivative_abs_l1: float,
    source_endpoint_abs: float = 0.0,
) -> dict[str, float | bool | str]:
    """Specialize the BV theorem to a smooth compact source.

    With ``|s|<=S0``, the oscillation of its primitive on an interval of
    length ``L`` is at most ``S0*L``.  For ``F=exp(2S)g``,
    ``Var(F)<=exp(2 max S)*(||g'||_1+2*S0*||g||_1)``.  A common exponential
    factor then gives the stated completely local majorant.
    """

    s_upper = float(superpotential_abs_upper)
    length = float(source_interval_length)
    g_l1 = float(source_abs_l1)
    dg_l1 = float(source_derivative_abs_l1)
    endpoint = float(source_endpoint_abs)
    values = (s_upper, length, g_l1, dg_l1, endpoint)
    if not all(math.isfinite(value) and value >= 0.0 for value in values):
        raise ValueError("finite nonnegative smooth-source inputs required")
    if length == 0.0:
        raise ValueError("positive source interval length required")
    oscillation_factor = math.exp(2.0 * s_upper * length)
    local_bv_quantity = endpoint + dg_l1 + 2.0 * s_upper * g_l1
    bound = length * oscillation_factor * local_bv_quantity
    return {
        "superpotential_abs_upper": s_upper,
        "source_interval_length": length,
        "source_abs_l1": g_l1,
        "source_derivative_abs_l1": dg_l1,
        "source_endpoint_abs": endpoint,
        "primitive_oscillation_exponential_upper": oscillation_factor,
        "local_weighted_source_BV_majorant": local_bv_quantity,
        "quotient_operator_trace_norm_upper": bound,
        "source_Dini_integral_upper": bound,
        "far_tail_datum_used": False,
    }


def action_radius_regularity_audit() -> dict[str, object]:
    """Record the weakest radius regularity actually owned by the action."""

    return {
        "global_tests_in_increasing_strength": {
            "bounded_logarithmic_derivative": False,
            "eventual_one_sided_monotonicity": False,
            "bounded_variation_of_x_or_x_prime": False,
            "doubling_or_regular_variation": False,
            "asymptotic_power_law": False,
        },
        "why_not_global": (
            "the exact x(q) projection has bounded coordinate derivatives, "
            "but the retained maximal-flow theorem has no global state-speed, "
            "acceleration, coercive-S2, or uniform domain-margin bound"
        ),
        "weakest_recovered_class": (
            "x is regular on every compact admissible flow interval; therefore "
            "the compact first-variation coefficient F=exp(2S)*delta_s is BV"
        ),
        "tail_regularization_needed_for_source_Dini": False,
    }


def holonomy_transfer_denominator_audit(angle_radians: float) -> dict[str, object]:
    """Test a common unitary phase on trace, conormal, and admittance.

    A common reset-frame phase multiplies both ``u`` and ``v=A u``.  Their
    ratio and every norm/Wronskian denominator are unchanged.  This does not
    attach an independent phase to the AE2 domain.
    """

    angle = float(angle_radians)
    if not math.isfinite(angle):
        raise ValueError("finite holonomy angle required")
    phase = cmath.exp(1j * angle)
    sample_trace = 2.0 - 0.5j
    sample_conormal = -0.75 + 1.25j
    admittance = sample_conormal / sample_trace
    transformed_admittance = (phase * sample_conormal) / (phase * sample_trace)
    pair = (sample_trace, sample_conormal)
    transformed_pair = (phase * sample_trace, phase * sample_conormal)
    denominator = math.sqrt(sum(abs(value) ** 2 for value in pair))
    transformed_denominator = math.sqrt(
        sum(abs(value) ** 2 for value in transformed_pair)
    )
    return {
        "angle_radians": angle,
        "phase_real": phase.real,
        "phase_imag": phase.imag,
        "admittance_residual": abs(transformed_admittance - admittance),
        "norm_denominator_residual": abs(transformed_denominator - denominator),
        "common_phase_changes_threshold_denominator": False,
        "independent_AE2_Cayley_phase_present": False,
        "holonomy_regularizes_threshold": False,
    }


__all__ = [
    "action_radius_regularity_audit",
    "compact_source_dini_trace_norm_bound",
    "holonomy_transfer_denominator_audit",
    "smooth_compact_source_dini_bound",
]
