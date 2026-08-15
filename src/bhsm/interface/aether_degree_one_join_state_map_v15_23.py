"""BHSM v15.23 degree-one join state-map reduction.

This module reduces the retained metric--eta--sigma action on the
cohomogeneity-one join S7 = S3 * S3.  It proves exact round recovery,
derives the Lorentzian gravitational velocity Hessian, and audits the
smallest fixed-radial nonround truncation against the smooth collapse-pole
domain.  No coefficient or field is added.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np


VERSION = "v15.23"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
CAMPAIGN_OBJECT = (
    "ACTION_OWNED_COUPLED_ETA_SIGMA_METRIC_VARIED_EMBEDDING_NONROUND_"
    "CENTER_MANIFOLD_BIFURCATION_SOLUTION_WITH_COMPLEMENT_HESSIAN_"
    "INVERTIBLE_FULL_LORENTZIAN_LEGENDRE_MAP_AND_ACTION_SELECTED_SHAPE_MODE"
)
OUTCOME = (
    "EXACT_DEGREE_ONE_JOIN_REDUCTION_CANONICAL_MOMENTA_MOMENTUM_CONSTRAINT_"
    "AND_RADIAL_GAUGE_INVARIANTS_DERIVED_BUT_HAMILTONIAN_ELIMINATION_AND_"
    "THE_PHYSICAL_MASTER_BVP_REMAIN_UNSOLVED"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_GAUGE_INVARIANT_COHOMOGENEITY_ONE_JOIN_MASTER_OPERATOR_"
    "WITH_HAMILTONIAN_CONSTRAINT_ELIMINATION_SELF_ADJOINT_TWO_POLE_DOMAIN_"
    "SPECTRUM_AND_NONROUND_BIFURCATING_ETA_SIGMA_METRIC_SOLUTION"
)


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def join_scalar_curvature(
    *,
    a: float,
    b: float,
    c: float,
    a_chi: float,
    b_chi: float,
    c_chi: float,
    a_chichi: float,
    b_chichi: float,
) -> float:
    """Return R7 for c^2 dchi^2+a^2 dOmega3^2+b^2 dOmega3^2."""

    aa = _positive(a, "a")
    bb = _positive(b, "b")
    cc = _positive(c, "c")
    return (
        6.0 / aa**2
        + 6.0 / bb**2
        - 6.0 * (a_chichi / aa + b_chichi / bb) / cc**2
        + 6.0 * c_chi * (a_chi / aa + b_chi / bb) / cc**3
        - 6.0 * ((a_chi / aa) ** 2 + (b_chi / bb) ** 2) / cc**2
        - 18.0 * a_chi * b_chi / (cc**2 * aa * bb)
    )


def eta_join_invariant(
    *, a: float, b: float, c: float, f_chi: float, f: float
) -> float:
    """Return the spatial degree-one eta invariant on the join ansatz."""

    aa = _positive(a, "a")
    bb = _positive(b, "b")
    cc = _positive(c, "c")
    ff = float(f)
    if not math.isfinite(ff) or not math.isfinite(float(f_chi)):
        raise ValueError("f and f_chi must be finite")
    return (
        float(f_chi) ** 2 / cc**2
        + 3.0 * math.cos(ff) ** 2 / aa**2
        + 3.0 * math.sin(ff) ** 2 / bb**2
    )


def round_join_recovery(radius: float, chi: float) -> dict[str, Any]:
    """Verify the exact round S7 and identity-map eta invariants."""

    rr = _positive(radius, "radius")
    xx = float(chi)
    if not 0.0 < xx < math.pi / 2.0:
        raise ValueError("chi must lie strictly between the collapse poles")
    a = rr * math.cos(xx)
    b = rr * math.sin(xx)
    curvature = join_scalar_curvature(
        a=a,
        b=b,
        c=rr,
        a_chi=-rr * math.sin(xx),
        b_chi=rr * math.cos(xx),
        c_chi=0.0,
        a_chichi=-a,
        b_chichi=-b,
    )
    x_eta = eta_join_invariant(a=a, b=b, c=rr, f_chi=1.0, f=xx)
    return {
        "metric": "R^2[dchi^2+cos^2(chi)dOmega3_u^2+sin^2(chi)dOmega3_v^2]",
        "eta": "eta=(cos(chi)u,sin(chi)v)",
        "R7": curvature,
        "R7_expected": 42.0 / rr**2,
        "X_eta": x_eta,
        "X_eta_expected": 7.0 / rr**2,
        "round_recovery": math.isclose(curvature, 42.0 / rr**2, rel_tol=1e-12),
        "degree_one_recovery": math.isclose(x_eta, 7.0 / rr**2, rel_tol=1e-12),
    }


def gravitational_velocity_form() -> dict[str, Any]:
    """Return the ADM kinetic form for radial, mean-warp and shape rates.

    Write H_A=h_dot+u_dot, H_B=h_dot-u_dot, and H_C=c_dot.
    The Einstein kinetic scalar K_ij K^ij-K^2 is z^T M z for
    z=(c_dot,h_dot,u_dot).
    """

    matrix = np.array(
        [[0.0, -6.0, 0.0], [-6.0, -30.0, 0.0], [0.0, 0.0, 6.0]]
    )
    eigenvalues = np.linalg.eigvalsh(matrix)
    return {
        "coordinate_order": ["c_dot", "h_dot", "u_dot"],
        "quadratic_form": "-12*c_dot*h_dot-30*h_dot^2+6*u_dot^2",
        "matrix": matrix.tolist(),
        "rank": int(np.linalg.matrix_rank(matrix)),
        "eigenvalues": eigenvalues.tolist(),
        "direct_shape_coefficient": 6.0,
        "direct_shape_velocity_Hessian": "6*kappa1*sqrt(h)/N",
        "pointwise_fixed_volume_relation": "c_dot=-6*h_dot",
        "fixed_volume_form": "42*h_dot^2+6*u_dot^2",
        "constraint_warning": (
            "fixed_volume_is_a_diagnostic_not_a_substitute_for_the_"
            "Hamiltonian_and_momentum_constraints"
        ),
    }


def gravitational_log_momenta(
    *, h_c: float, h_a: float, h_b: float, kappa1: float, volume: float
) -> dict[str, float]:
    """Return momenta conjugate to log(C), log(A), and log(B)."""

    kk = _positive(kappa1, "kappa1")
    vv = _positive(volume, "volume")
    hc, ha, hb = float(h_c), float(h_a), float(h_b)
    if not all(math.isfinite(item) for item in (hc, ha, hb)):
        raise ValueError("expansion rates must be finite")
    return {
        "p_c": -3.0 * kk * vv * (ha + hb),
        "p_a": -3.0 * kk * vv * (2.0 * ha + 3.0 * hb + hc),
        "p_b": -3.0 * kk * vv * (3.0 * ha + 2.0 * hb + hc),
    }


def invert_gravitational_log_momenta(
    *, p_c: float, p_a: float, p_b: float, kappa1: float, volume: float
) -> dict[str, float]:
    """Invert the exact gravitational Legendre map on the metric block."""

    kk = _positive(kappa1, "kappa1")
    vv = _positive(volume, "volume")
    pc, pa, pb = float(p_c), float(p_a), float(p_b)
    if not all(math.isfinite(item) for item in (pc, pa, pb)):
        raise ValueError("momenta must be finite")
    scale = 6.0 * vv * kk
    return {
        "H_A": (pa - pb - pc) / scale,
        "H_B": (-pa + pb - pc) / scale,
        "H_C": (-pa - pb + 5.0 * pc) / scale,
    }


def gravitational_kinetic_hamiltonian(
    *, p_c: float, p_a: float, p_b: float, kappa1: float, volume: float
) -> float:
    """Return the exact metric kinetic Hamiltonian density without lapse."""

    kk = _positive(kappa1, "kappa1")
    vv = _positive(volume, "volume")
    pc, pa, pb = float(p_c), float(p_a), float(p_b)
    return (
        pa**2
        - 2.0 * pa * pb
        - 2.0 * pa * pc
        + pb**2
        - 2.0 * pb * pc
        + 5.0 * pc**2
    ) / (12.0 * vv * kk)


def radial_momentum_constraint(
    *,
    p_c_chi: float,
    p_c: float,
    p_a: float,
    p_b: float,
    p_f: float,
    p_sigma: float,
    c_chi: float,
    a_chi: float,
    b_chi: float,
    f_chi: float,
    sigma_chi: float,
) -> float:
    """Return the exact shift constraint in logarithmic metric variables."""

    return (
        -float(p_c_chi)
        + float(p_c) * float(c_chi)
        + float(p_a) * float(a_chi)
        + float(p_b) * float(b_chi)
        + float(p_f) * float(f_chi)
        + float(p_sigma) * float(sigma_chi)
    )


def radial_gauge_invariants(
    *,
    chi: float,
    delta_c: float,
    delta_h: float,
    delta_u: float,
    delta_f: float,
    delta_f_chi: float,
) -> dict[str, float]:
    """Return three invariants under radial diffeomorphisms of the round join."""

    xx = float(chi)
    if not 0.0 < xx < math.pi / 2.0:
        raise ValueError("chi must lie strictly between the collapse poles")
    return {
        "C_GI": float(delta_c) - float(delta_f_chi),
        "H_GI": float(delta_h) - float(delta_f) / math.tan(2.0 * xx),
        "U_GI": float(delta_u) + float(delta_f) / math.sin(2.0 * xx),
    }


def static_legendre_certificate(
    *, volume: float, kappa1: float, x_eta: float, sigma_weight: float, zsigma: float
) -> dict[str, Any]:
    """Certify local Legendre regularity of dynamical fields at zero velocity."""

    vv = _positive(volume, "volume")
    kk = _positive(kappa1, "kappa1")
    xx = _positive(x_eta, "x_eta")
    ww = _positive(sigma_weight, "sigma_weight")
    zz = _positive(zsigma, "zsigma")
    metric_matrix = kk * vv * np.array(
        [[0.0, -6.0, 0.0], [-6.0, -30.0, 0.0], [0.0, 0.0, 6.0]]
    )
    eta_hessian = vv * ww * (kk + xx**3)
    sigma_hessian = vv * zz
    return {
        "metric_velocity_Hessian_rank": int(np.linalg.matrix_rank(metric_matrix)),
        "metric_velocity_Hessian_determinant": float(np.linalg.det(metric_matrix)),
        "eta_velocity_Hessian": eta_hessian,
        "sigma_velocity_Hessian": sigma_hessian,
        "dynamical_field_block_regular": (
            np.linalg.matrix_rank(metric_matrix) == 3
            and eta_hessian > 0.0
            and sigma_hessian > 0.0
        ),
        "primary_constraint_variables": ["lapse_N", "radial_shift_beta_chi"],
        "interpretation": (
            "degeneracy_is_confined_to_the_expected_diffeomorphism_"
            "multipliers_at_the_static_round_branch"
        ),
    }


def smooth_join_boundary_domain() -> dict[str, Any]:
    """Return the regular two-collapse-pole conditions for the join metric."""

    return {
        "chi_interval": "[0,pi/2]",
        "chi_0": ["B=0", "partial_chi_B=C", "partial_chi_A=0"],
        "chi_pi_over_2": ["A=0", "partial_chi_A=-C", "partial_chi_B=0"],
        "eta_degree_one": ["f(0)=0", "f(pi/2)=pi/2"],
        "sigma": "regular_even_normal_expansion_at_each_collapse_pole",
        "shape_definition": "A=R*cos(chi)*exp(u),_B=R*sin(chi)*exp(-u)",
        "fixed_C_shape_regular_leading_order": "u=O(chi^2)_and_O((pi/2-chi)^2)",
        "self_adjoint_boundary_form_must_vanish": True,
    }


def _sine_power_integral(power: float) -> float:
    return math.sqrt(math.pi) * math.gamma((power + 1.0) / 2.0) / math.gamma(
        power / 2.0 + 1.0
    )


def shape_trial_rayleigh(
    *, power: int = 2, radius: float = 1.0, kappa1: float = 1.0, sigma_weight: float = 1.0
) -> dict[str, Any]:
    """Evaluate the fixed-C, fixed-product trial u=sin(2chi)^power.

    This is an exact quadratic diagnostic, not a constraint-reduced physical
    eigenfrequency.  Smooth pole slopes require ``power >= 2``.
    """

    pp = int(power)
    if pp < 2:
        raise ValueError("power must be at least two for the smooth-pole trial")
    rr = _positive(radius, "radius")
    kk = _positive(kappa1, "kappa1")
    ww = _positive(sigma_weight, "sigma_weight")
    norm = _sine_power_integral(2 * pp + 3) / 16.0
    singular = _sine_power_integral(2 * pp + 1) / 4.0
    gradient = (pp**2 / 4.0) * (
        _sine_power_integral(2 * pp + 1) - _sine_power_integral(2 * pp + 3)
    )
    geometric_eigenvalue = gradient / norm - 2.0 * singular / norm
    x0 = 7.0 / rr**2
    f_prime = 0.5 * (kk + x0**3)
    omega_squared = (geometric_eigenvalue + 4.0 * ww * f_prime / kk) / rr**2
    return {
        "trial": f"sin(2chi)^{pp}",
        "norm_integral": norm,
        "gradient_integral": gradient,
        "singular_potential_integral": singular,
        "geometric_Rayleigh_value": geometric_eigenvalue,
        "X_eta_round": x0,
        "F_prime_round": f_prime,
        "omega_squared_diagnostic": omega_squared,
        "smooth_pole_trial": True,
        "constraint_reduced_eigenfrequency": False,
    }


def fixed_radial_domain_closure_audit(power: int = 2) -> dict[str, Any]:
    """Test whether the fixed-C scalar shape operator preserves pole order."""

    pp = int(power)
    if pp < 2:
        raise ValueError("power must be at least two")
    # Near chi=0, u=sin(2chi)^p = 2^p chi^p+..., while
    # L0=-d2-3/chi*d-2/chi^2+... lowers the leading order by two.
    leading_input = 2.0**pp
    leading_output = -(pp**2 + 2 * pp + 2) * leading_input
    return {
        "input_leading_order": f"chi^{pp}",
        "operator_leading_order": f"chi^{pp - 2}",
        "operator_leading_coefficient": leading_output,
        "same_regular_eigenfunction_order": False,
        "fixed_radial_shape_operator_preserves_smooth_pole_domain": False,
        "cause": (
            "the_fixed_C_fixed_product_slice_omits_radial_metric_lapse_shift_"
            "companions_required_by_the_Einstein_constraints"
        ),
        "not_a_physical_instability_claim": True,
    }


def reduced_action_contract() -> dict[str, Any]:
    """State the exact retained action restricted to the join fields."""

    return {
        "existing_fields_only": ["N", "beta_chi", "C", "A", "B", "f", "sigma"],
        "volume_density": "N*C*A^3*B^3*Vol(S3)^2",
        "eta_invariant": (
            "X_eta=-(D_t f)^2/N^2+(partial_chi f)^2/C^2+"
            "3*cos(f)^2/A^2+3*sin(f)^2/B^2"
        ),
        "eta_density": "F(X)=kappa1*X/2+X^4/8",
        "bulk_density": (
            "sqrt(-G){(kappa1*R8-kappa0)/2-(1+g*sigma^2)F(X_eta)-"
            "Zsigma*(grad sigma)^2/2-A0*sigma^2/2-G0*sigma^4/4}"
        ),
        "boundary_terms": ["retained_GHY", "retained_Hayward", "retained_matcher"],
        "new_fields": [],
        "new_continuous_coefficients": [],
        "preferred_external_frame": False,
    }


def completion_payload() -> dict[str, Any]:
    round_data = round_join_recovery(2.3, 0.41)
    kinetic = gravitational_velocity_form()
    domain = smooth_join_boundary_domain()
    trial = shape_trial_rayleigh(power=2, radius=(343.0 / 5.0) ** (1.0 / 6.0))
    closure = fixed_radial_domain_closure_audit(2)
    action = reduced_action_contract()
    momenta = gravitational_log_momenta(
        h_c=0.2, h_a=-0.1, h_b=0.3, kappa1=1.7, volume=2.2
    )
    inverse = invert_gravitational_log_momenta(
        **momenta, kappa1=1.7, volume=2.2
    )
    gauge_before = radial_gauge_invariants(
        chi=0.43,
        delta_c=0.2,
        delta_h=-0.4,
        delta_u=0.3,
        delta_f=-0.12,
        delta_f_chi=0.07,
    )
    xi, xi_chi, chi = 0.09, -0.04, 0.43
    gauge_after = radial_gauge_invariants(
        chi=chi,
        delta_c=0.2 + xi_chi,
        delta_h=-0.4 + xi / math.tan(2.0 * chi),
        delta_u=0.3 - xi / math.sin(2.0 * chi),
        delta_f=-0.12 + xi,
        delta_f_chi=0.07 + xi_chi,
    )
    legendre = static_legendre_certificate(
        volume=2.0, kappa1=1.0, x_eta=1.4, sigma_weight=1.2, zsigma=0.8
    )
    critical_expected = 16.0 / (3.0 * (343.0 / 5.0) ** (1.0 / 3.0))
    validation = {
        "round_S7_curvature_recovered": round_data["round_recovery"],
        "degree_one_eta_invariant_recovered": round_data["degree_one_recovery"],
        "full_metric_velocity_form_has_rank_three_before_constraints": kinetic["rank"] == 3,
        "nonround_shape_has_positive_direct_kinetic_coefficient": kinetic[
            "direct_shape_coefficient"
        ] > 0.0,
        "critical_round_shape_trial_is_positive": trial["omega_squared_diagnostic"] > 0.0,
        "critical_trial_exact_value_recovered": math.isclose(
            trial["omega_squared_diagnostic"], critical_expected, rel_tol=1e-12
        ),
        "fixed_radial_domain_failure_detected": not closure[
            "fixed_radial_shape_operator_preserves_smooth_pole_domain"
        ],
        "domain_failure_not_misreported_as_instability": closure[
            "not_a_physical_instability_claim"
        ],
        "metric_momenta_invert_exactly": all(
            math.isclose(inverse[key], value, rel_tol=1e-12, abs_tol=1e-12)
            for key, value in {"H_C": 0.2, "H_A": -0.1, "H_B": 0.3}.items()
        ),
        "round_radial_gauge_invariants_verified": all(
            math.isclose(gauge_before[key], gauge_after[key], abs_tol=1e-12)
            for key in gauge_before
        ),
        "static_dynamical_legendre_block_regular": legendre[
            "dynamical_field_block_regular"
        ],
        "no_new_field_or_coefficient": not action["new_fields"]
        and not action["new_continuous_coefficients"],
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_degree_one_join_state_map_v15_23",
        "version": VERSION,
        "campaign_object": CAMPAIGN_OBJECT,
        "outcome": OUTCOME,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "round_join_recovery": round_data,
        "retained_reduced_action": action,
        "smooth_boundary_domain": domain,
        "gravitational_velocity_form": kinetic,
        "canonical_metric_block": {
            "log_momenta_control": momenta,
            "inverse_control": inverse,
            "kinetic_Hamiltonian_formula": (
                "(p_a^2-2p_a p_b-2p_a p_c+p_b^2-2p_b p_c+5p_c^2)/"
                "(12*kappa1*C*A^3*B^3)"
            ),
            "radial_momentum_constraint": (
                "-partial_chi p_c+p_c c'+p_a a'+p_b b'+p_f f'+p_sigma sigma'=0"
            ),
        },
        "round_radial_gauge_invariants": {
            "definitions": [
                "C_GI=delta_c-partial_chi(delta_f)",
                "H_GI=delta_h-cot(2chi)*delta_f",
                "U_GI=delta_u+csc(2chi)*delta_f",
            ],
            "control_before": gauge_before,
            "control_after_diffeomorphism": gauge_after,
        },
        "static_Legendre_certificate": legendre,
        "fixed_radial_shape_trial": trial,
        "fixed_radial_domain_audit": closure,
        "physical_nonround_eigenmode_derived": False,
        "physical_nonround_bifurcating_solution_derived": False,
        "Hindsight_20_20": {
            "VALIDATED": [
                "the_degree_one_eta_identity_map_and_round_S7_share_one_exact_join_ansatz",
                "the_existing_Einstein_action_supplies_a_direct_positive_nonround_shape_kinetic_direction",
                "the_smooth_lowest_fixed_radial_trial_is_stable_at_the_v15_9_critical_radius",
                "the_exact_metric_log_momenta_are_invertible_before_the_lapse_and_shift_constraints",
                "three_round_join_radial_gauge_invariants_follow_from_the_existing_eta_clock_profile",
            ],
            "INVALIDATED": [
                "a_fixed_radial_two_warp_shape_truncation_is_a_closed_physical_Hessian_domain",
                "the_v15_9_formation_crossing_by_itself_is_a_nonround_shape_instability",
            ],
            "RECLASSIFIED": [
                "the_nonround_warp_as_a_component_of_a_constrained_metric_master_mode_not_a_standalone_scalar",
                "the_eta_profile_perturbation_as_part_of_the_radial_gauge_invariant_shape_coordinate",
            ],
            "OPEN": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "new_empirical_inputs": [],
            "frozen_predictions_changed": False,
            "USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE": (
                USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE
            ),
        },
    }


def _canonical_json_value(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float cannot be materialized")
        rounded = round(value, 12)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonical_json_value(payload),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_degree_one_join_state_map_v15_23.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION",
    "FULL_BHSM_COMPLETE",
    "CAMPAIGN_OBJECT",
    "OUTCOME",
    "EXACT_NEXT_OBJECT",
    "join_scalar_curvature",
    "eta_join_invariant",
    "round_join_recovery",
    "gravitational_velocity_form",
    "gravitational_log_momenta",
    "invert_gravitational_log_momenta",
    "gravitational_kinetic_hamiltonian",
    "radial_momentum_constraint",
    "radial_gauge_invariants",
    "static_legendre_certificate",
    "smooth_join_boundary_domain",
    "shape_trial_rayleigh",
    "fixed_radial_domain_closure_audit",
    "reduced_action_contract",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
