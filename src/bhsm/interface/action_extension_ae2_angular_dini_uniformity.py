"""Angular-uniformity audit for factorized AE2 source-Dini bounds."""

from __future__ import annotations

import math


def integrable_optical_tail_dini_coefficient_lower(
    *,
    angular_eigenvalue: float,
    reciprocal_radius_integral: float,
    initial_reciprocal_radius_upper: float,
    initial_interval_length: float,
    positive_source_reciprocal_integral: float,
) -> dict[str, float | bool]:
    """Lower-bound the positive-chirality threshold coefficient.

    Let ``r=1/R4``, ``I=int_0^infinity r``, ``s=mu*r`` and let the retained
    log-radius direction be nonnegative on a compact interval after
    ``delta``.  Delta-normalizing the exact zero transfer state contributes
    ``N_mu^2=(2/pi)*exp(2*mu*I)``.  If ``r<=r_max`` on ``[0,delta]`` and
    ``mu>=1/(2*r_max*delta)``, then

    ``int_0^t exp(-2*mu*int_0^q r)dq``
    ``>= (1-exp(-1))/(2*mu*r_max)``

    for every source point ``t>=delta``.  Substitution in the exact transfer
    derivative gives the lower bound returned here.  It concerns the angular
    direct sum only; every fixed channel remains source-Dini finite.
    """

    mu = float(angular_eigenvalue)
    optical = float(reciprocal_radius_integral)
    r_upper = float(initial_reciprocal_radius_upper)
    delta = float(initial_interval_length)
    source_integral = float(positive_source_reciprocal_integral)
    values = (mu, optical, r_upper, delta, source_integral)
    if not all(math.isfinite(value) and value > 0.0 for value in values):
        raise ValueError("finite positive angular-uniformity inputs required")
    threshold = 1.0 / (2.0 * r_upper * delta)
    if mu < threshold:
        raise ValueError("angular eigenvalue below the proved lower-bound range")
    prefactor = (2.0 / math.pi) * (1.0 - math.exp(-1.0))
    log_lower = (
        math.log(prefactor * source_integral / r_upper)
        + 2.0 * mu * optical
    )
    lower = math.exp(log_lower) if log_lower < math.log(float.fromhex("0x1.fffffffffffffp+1023")) else math.inf
    return {
        "angular_eigenvalue": mu,
        "reciprocal_radius_integral": optical,
        "initial_reciprocal_radius_upper": r_upper,
        "initial_interval_length": delta,
        "positive_source_reciprocal_integral": source_integral,
        "minimum_angular_eigenvalue_for_bound": threshold,
        "log_threshold_coefficient_lower": log_lower,
        "threshold_coefficient_lower": lower,
        "grows_exponentially_in_angular_level": True,
        "fixed_channel_source_Dini_finite": True,
    }


def exponential_radius_angular_counterexample(
    maximum_level: int = 12,
    *,
    source_start: float = 0.25,
    source_end: float = 0.75,
) -> dict[str, object]:
    """Return a smooth positive non-power angular-divergence witness.

    The history ``R4(tau)=exp(tau)`` has bounded logarithmic derivative,
    eventual monotonicity, smooth coefficients, and finite optical length
    ``int exp(-tau)d_tau=1``.  A unit nonnegative source on
    ``[source_start,source_end]`` has the exact reciprocal-radius integral
    used below.  Weyl levels have ``mu_n=n+3/2`` and degeneracy
    ``48(n+1)(n+2)``.
    """

    count = int(maximum_level)
    start = float(source_start)
    end = float(source_end)
    if count < 2 or not (0.0 < start < end):
        raise ValueError("at least two levels and a positive source interval required")
    source_integral = math.exp(-start) - math.exp(-end)
    rows = []
    for level in range(1, count + 1):
        mu = level + 1.5
        coefficient = integrable_optical_tail_dini_coefficient_lower(
            angular_eigenvalue=mu,
            reciprocal_radius_integral=1.0,
            initial_reciprocal_radius_upper=1.0,
            initial_interval_length=start,
            positive_source_reciprocal_integral=source_integral,
        )
        degeneracy = 48 * (level + 1) * (level + 2)
        log_term = math.log(float(degeneracy)) + float(
            coefficient["log_threshold_coefficient_lower"]
        )
        rows.append(
            {
                "level": level,
                "positive_Dirac_eigenvalue": mu,
                "Weyl_degeneracy": degeneracy,
                "log_channel_Dini_coefficient_lower": coefficient[
                    "log_threshold_coefficient_lower"
                ],
                "log_degeneracy_weighted_term_lower": log_term,
            }
        )
    increments = [
        later["log_degeneracy_weighted_term_lower"]
        - earlier["log_degeneracy_weighted_term_lower"]
        for earlier, later in zip(rows, rows[1:])
    ]
    return {
        "radius_history": "R4(tau)=exp(tau)",
        "log_radius_derivative": 1.0,
        "eventually_monotone": True,
        "smooth_positive_non_power_tail": True,
        "reciprocal_radius_integral": 1.0,
        "source_interval": [start, end],
        "source_reciprocal_integral": source_integral,
        "rows": rows,
        "minimum_successive_log_term_increment": min(increments),
        "degeneracy_weighted_terms_tend_to_zero": False,
        "absolute_angular_source_Dini_sum_finite": False,
        "fixed_channel_source_Dini_finite_for_every_level": True,
    }


def angular_uniformity_requirement() -> dict[str, object]:
    """State the sharp requirement exposed by the counterexample."""

    return {
        "bounded_logarithmic_derivative_sufficient": False,
        "eventual_monotonicity_sufficient": False,
        "smoothness_or_local_BV_sufficient": False,
        "factorization_and_compact_source_sufficient_per_channel": True,
        "factorization_and_compact_source_sufficient_after_angular_sum": False,
        "finite_optical_length_excluded_by_angular_finiteness": True,
        "necessary_geometric_exclusion": "integral_0^infinity d_tau/R4(tau)=infinity",
        "optical_completeness_alone_proved_sufficient": False,
        "remaining_sufficient_route": (
            "quantitative optical-completeness/barrier estimate uniform in the "
            "angular level, or an already action-owned relative trace"
        ),
    }


__all__ = [
    "angular_uniformity_requirement",
    "exponential_radius_angular_counterexample",
    "integrable_optical_tail_dini_coefficient_lower",
]
