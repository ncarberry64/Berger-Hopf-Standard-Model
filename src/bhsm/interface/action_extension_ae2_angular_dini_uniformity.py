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


def at_most_linear_radius_agmon_bound(
    *,
    angular_eigenvalue: float,
    radius_upper_at_source_end: float,
    radius_speed_upper: float,
    threshold_wave_number: float,
    chirality: int = 1,
) -> dict[str, float | bool | str]:
    """Return the high-angular barrier from an at-most-linear radius envelope.

    Assume after the compact source that ``0<=R4'<=v``. Then
    ``R4(t)<=R_L+v(t-L)``. For positive chirality, ``s=mu/R4`` and
    ``K=A* A=-d2+s^2-s'`` has ``V_plus>=s^2``. For negative chirality,
    ``A A*`` has ``V_minus=s^2+s'>=s^2/2`` once ``mu>=2v``. Up to the
    envelope turning point ``R_L+v(t-L)=mu/(2k)``, one has ``s>=2k``.
    Thus the forbidden-region square roots are at least
    ``sqrt(3)*s/2`` and ``s/2``, respectively. Integrating the reciprocal
    linear envelope gives the stated ``mu*log(mu)`` actions.
    """

    mu = float(angular_eigenvalue)
    radius = float(radius_upper_at_source_end)
    speed = float(radius_speed_upper)
    k = float(threshold_wave_number)
    sign = int(chirality)
    values = (mu, radius, speed, k)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("finite angular barrier inputs required")
    if mu <= 0.0 or radius <= 0.0 or speed < 0.0 or k <= 0.0 or sign not in (-1, 1):
        raise ValueError(
            "positive mu, radius and k, nonnegative speed, and chirality +/-1 required"
        )
    ratio = mu / (2.0 * k * radius)
    if ratio <= 1.0:
        raise ValueError("angular level must place a barrier beyond the source")
    if speed == 0.0:
        return {
            "angular_eigenvalue": mu,
            "radius_upper_at_source_end": radius,
            "radius_speed_upper": speed,
            "threshold_wave_number": k,
            "chirality": sign,
            "envelope_turning_distance": "INFINITY",
            "agmon_action_lower": "INFINITY",
            "log_squared_amplitude_suppression_upper": "MINUS_INFINITY",
            "squared_amplitude_suppression_upper": 0.0,
            "asymptotic_action_class": "UNIFORM_POSITIVE_GAP_TO_INFINITY",
            "beats_every_fixed_polynomial_multiplicity": True,
            "beats_exp(C*mu)*mu^d_for_every_fixed_C_and_d": True,
            "reciprocal_linear_envelope_integral_diverges": True,
            "exact_power_law_assumed": False,
        }
    if sign == 1:
        action_factor = math.sqrt(3.0) / 2.0
        potential_lower = "V_plus>=s_mu^2"
    else:
        if mu < 2.0 * speed:
            raise ValueError("negative-chirality bound requires mu>=2*v")
        action_factor = 0.5
        potential_lower = "V_minus>=s_mu^2/2_FOR_mu>=2*v"
    action = action_factor * mu * math.log(ratio) / speed
    turning_distance = (mu / (2.0 * k) - radius) / speed
    log_suppression = -2.0 * action
    suppression = math.exp(log_suppression) if log_suppression > -745.0 else 0.0
    return {
        "angular_eigenvalue": mu,
        "radius_upper_at_source_end": radius,
        "radius_speed_upper": speed,
        "threshold_wave_number": k,
        "chirality": sign,
        "envelope_turning_distance": turning_distance,
        "agmon_action_lower": action,
        "log_squared_amplitude_suppression_upper": log_suppression,
        "squared_amplitude_suppression_upper": suppression,
        "potential_lower": potential_lower,
        "asymptotic_action_class": f"({action_factor}/v)*mu*log(mu)+O(mu)",
        "beats_every_fixed_polynomial_multiplicity": True,
        "beats_exp(C*mu)*mu^d_for_every_fixed_C_and_d": True,
        "reciprocal_linear_envelope_integral_diverges": True,
        "exact_power_law_assumed": False,
    }


def at_most_linear_angular_series_witness(
    *,
    first_level: int = 8,
    last_level: int = 24,
    radius_upper_at_source_end: float = 1.25,
    radius_speed_upper: float = 1.0,
    threshold_wave_number: float = 1.0,
    polynomial_degree: int = 4,
    source_exponential_rate: float = 2.0,
) -> dict[str, object]:
    """Demonstrate decay after local exponential and polynomial weights."""

    first = int(first_level)
    last = int(last_level)
    degree = int(polynomial_degree)
    exponential_rate = float(source_exponential_rate)
    if (
        first < 0
        or last <= first
        or degree < 0
        or not math.isfinite(exponential_rate)
        or exponential_rate < 0.0
    ):
        raise ValueError("valid angular level interval and polynomial degree required")
    rows = []
    for level in range(first, last + 1):
        mu = level + 1.5
        barrier = at_most_linear_radius_agmon_bound(
            angular_eigenvalue=mu,
            radius_upper_at_source_end=radius_upper_at_source_end,
            radius_speed_upper=radius_speed_upper,
            threshold_wave_number=threshold_wave_number,
            chirality=1,
        )
        partner = at_most_linear_radius_agmon_bound(
            angular_eigenvalue=mu,
            radius_upper_at_source_end=radius_upper_at_source_end,
            radius_speed_upper=radius_speed_upper,
            threshold_wave_number=threshold_wave_number,
            chirality=-1,
        )
        log_local_weight = exponential_rate * mu + degree * math.log1p(mu)
        positive_log = float(barrier["log_squared_amplitude_suppression_upper"])
        negative_log = float(partner["log_squared_amplitude_suppression_upper"])
        log_term = log_local_weight + max(positive_log, negative_log)
        rows.append(
            {
                "level": level,
                "angular_eigenvalue": mu,
                "log_local_exp_times_polynomial_weight": log_local_weight,
                "positive_chirality_log_suppression_upper": positive_log,
                "negative_chirality_log_suppression_upper": negative_log,
                "log_weighted_tail_term_upper": log_term,
                "nth_root_log_upper": log_term / (level + 1.0),
            }
        )
    return {
        "polynomial_degree": degree,
        "source_exponential_rate": exponential_rate,
        "rows": rows,
        "weighted_log_terms_strictly_decrease": all(
            later["log_weighted_tail_term_upper"]
            < earlier["log_weighted_tail_term_upper"]
            for earlier, later in zip(rows, rows[1:])
        ),
        "nth_root_logs_decrease": all(
            later["nth_root_log_upper"] < earlier["nth_root_log_upper"]
            for earlier, later in zip(rows, rows[1:])
        ),
        "analytic_root_test_limit": "minus_infinity",
        "local_weight_class": "exp(C*mu)*(1+mu)^d",
        "angular_series_absolutely_summable": True,
    }


__all__ = [
    "at_most_linear_angular_series_witness",
    "at_most_linear_radius_agmon_bound",
    "angular_uniformity_requirement",
    "exponential_radius_angular_counterexample",
    "integrable_optical_tail_dini_coefficient_lower",
]
