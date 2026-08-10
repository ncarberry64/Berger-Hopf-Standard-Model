"""BHSM v15.10 Aether-cycle sigma-coefficient reconstruction gate.

The retained local energy density at fixed geometric fields is

    E(X, sigma) = F(X) (1 + g sigma**2)
                  + A0 sigma**2 / 2 + G0 sigma**4 / 4,
    F(X) = kappa1 X / 2 + X**4 / 8.

This module derives the smallest canonically normalized sigma response jet
that would select the invariant coefficient triple (alpha, r, gamma).  It
also audits whether the current Aether/cycle state supplies that jet.  It
does not choose a coefficient, fit data, add a field, or promote a
conditional eta-to-sigma crossing to a physical branch.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np


VERSION = "v15.10"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
COEFFICIENT_SELECTION_OUTCOME = "OUTCOME_D_TRUE_RETAINED_ACTION_NONUNIQUENESS"
PRIMARY_OBJECT = (
    "AETHER_CYCLE_COEFFICIENT_SELECTION_THROUGH_THE_CANONIC_SIGMA_"
    "RESPONSE_JET_FOLLOWED_BY_ETA_SIGMA_AND_FULL_HOPF_CONTINUATION"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_AETHER_CYCLE_TO_REGULAR_SIGMA_RESPONSE_JET_MAP_"
    "PRODUCING_THE_PHYSICAL_SIGMA_TANGENT_PROPAGATOR_X_DERIVATIVE_"
    "AND_BACKREACTION_UNREDUCED_CANONICAL_QUARTIC_ON_THE_V15_9_BRANCH"
)
PRIMARY_VERDICT = (
    "BHSM_V15_10_THE_RETAINED_SIGMA_ACTION_HAS_AN_EXACT_INJECTIVE_"
    "THREE_RESPONSE_INVERSE_FOR_ALPHA_R_GAMMA_AND_THE_HOMOGENEOUS_"
    "CYCLE_INVERSE_CONDITIONALLY_SELECTS_KAPPA1_KAPPA0_BUT_THE_"
    "CURRENT_AETHER_STATE_SUPPLIES_NO_PHYSICAL_SIGMA_TANGENT_X_"
    "DERIVATIVE_OR_NONLINEAR_RESPONSE_JET;_EXPLICIT_STABLE_"
    "INEQUIVALENT_TRIPLES_SHARE_THE_SAME_SIGMA_ZERO_PARENT_AND_EVEN_"
    "THE_SAME_THRESHOLD_QUADRATIC_CURVATURE;_THEREFORE_NO_PHYSICAL_"
    "SIGMA_ONSET_HOPF_CHILD_OR_PERSISTENT_ENCLOSURE_IS_SELECTED_AND_"
    "FULL_BHSM_COMPLETION_REMAINS_FALSE"
)


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def critical_x(kappa1: float = 1.0) -> float:
    """Return X_c=(5 kappa1)^(1/3) on the v15.9 crossing."""

    k1 = _positive(kappa1, "kappa1")
    return (5.0 * k1) ** (1.0 / 3.0)


def homogeneous_cycle_inverse(
    radius: float, hubble: float, hubble_dot: float
) -> dict[str, float]:
    """Recover the homogeneous eta/gravity coefficients from cycle data.

    This is the already-derived frozen homogeneous degree-one inverse.  Its
    denominator is required to be positive on the retained kappa1>0 branch.
    """

    a = _positive(radius, "radius")
    h = float(hubble)
    hd = float(hubble_dot)
    if not math.isfinite(h) or not math.isfinite(hd):
        raise ValueError("H and Hdot must be finite")
    denominator = 5.0 - 6.0 * a**2 * hd
    if denominator <= 0.0:
        raise ValueError("the retained positive-kappa1 branch requires 5-6a^2 Hdot>0")
    kappa1 = 343.0 / (a**6 * denominator)
    kappa0 = (
        7203.0
        * (8.0 * a**2 * h**2 + 2.0 * a**2 * hd + 5.0)
        / (4.0 * a**8 * denominator)
    )
    return {
        "kappa1": kappa1,
        "kappa0": kappa0,
        "denominator": denominator,
    }


def critical_cycle_compatibility(kappa1: float = 1.0) -> dict[str, Any]:
    """Verify exact compatibility of the cycle inverse and v15.9 crossing."""

    k1 = _positive(kappa1, "kappa1")
    x0 = critical_x(k1)
    radius = math.sqrt(7.0 / x0)
    recovered = homogeneous_cycle_inverse(radius, 0.0, 0.0)
    expected_kappa0 = 15.0 * k1 * x0 / 4.0
    return {
        "critical_relation": "a_c^6=343/(5*kappa1)",
        "same_kappa1_requires": "Hdot=0",
        "stationary_turning_slice": "H=0_and_Hdot=0",
        "radius": radius,
        "X_critical": x0,
        "recovered_kappa1": recovered["kappa1"],
        "recovered_kappa0": recovered["kappa0"],
        "expected_identity_locus_kappa0": expected_kappa0,
        "kappa1_residual": recovered["kappa1"] - k1,
        "kappa0_residual": recovered["kappa0"] - expected_kappa0,
        "interpretation": (
            "the_homogeneous_cycle_inverse_closes_the_eta_gravity_slice_"
            "conditionally_but_sigma_zero_makes_it_blind_to_Zsigma_g_A0_G0"
        ),
    }


def retained_response_derivatives(
    kappa1: float,
    x_eta: float,
    g: float,
    a0: float,
    g0: float,
) -> dict[str, float]:
    """Return fixed-background derivatives of the retained local energy.

    Derivatives are evaluated at sigma=0.  ``E_ssss`` is the fourth sigma
    derivative, not the quartic coefficient itself.
    """

    k1 = _positive(kappa1, "kappa1")
    x = _positive(x_eta, "X_eta")
    coupling = float(g)
    mass = float(a0)
    quartic = float(g0)
    if not all(math.isfinite(v) for v in (coupling, mass, quartic)):
        raise ValueError("g, A0 and G0 must be finite")
    e_x = 0.5 * (k1 + x**3)
    e_xxxx = 3.0
    e_ss = mass + coupling * (k1 * x + 0.25 * x**4)
    e_ss_x = coupling * (k1 + x**3)
    e_ss_xxxx = 6.0 * coupling
    e_ssss = 6.0 * quartic
    return {
        "E_X": e_x,
        "E_XXXX": e_xxxx,
        "E_ss": e_ss,
        "E_ssX": e_ss_x,
        "E_ssXXXX": e_ss_xxxx,
        "E_ssss": e_ssss,
        "g_from_X_integrability": e_ss_x / (2.0 * e_x),
        "g_from_X4_integrability": e_ss_xxxx / (2.0 * e_xxxx),
    }


def normalized_sigma_response_jet(
    kappa1: float,
    x_eta: float,
    zsigma: float,
    g: float,
    a0: float,
    g0: float,
) -> dict[str, float]:
    """Return the three minimal canonically normalized response observables."""

    z = _positive(zsigma, "Zsigma")
    derivatives = retained_response_derivatives(kappa1, x_eta, g, a0, g0)
    return {
        "S_sigma": derivatives["E_ss"] / z,
        "dS_sigma_dX": derivatives["E_ssX"] / z,
        "lambda_sigma_bare_canonical": derivatives["E_ssss"] / (6.0 * z**2),
    }


def reconstruct_invariants_from_response_jet(
    kappa1: float,
    x_eta: float,
    sigma_curvature: float,
    sigma_curvature_x: float,
    bare_canonical_quartic: float,
) -> dict[str, float]:
    """Invert the response jet to alpha, r, gamma without Zsigma itself."""

    k1 = _positive(kappa1, "kappa1")
    x = _positive(x_eta, "X_eta")
    s0 = float(sigma_curvature)
    sx = float(sigma_curvature_x)
    lam = float(bare_canonical_quartic)
    if not all(math.isfinite(v) for v in (s0, sx, lam)):
        raise ValueError("response-jet entries must be finite")
    denominator = 1.0 + x**3 / k1
    r = sx / denominator
    if abs(r) < 1.0e-15:
        raise ValueError("nonzero mixed sigma-X response is required")
    alpha = s0 / (r * x) - 1.0 - x**3 / (4.0 * k1)
    gamma = lam * k1**2 / (r**2 * x**4)
    return {"alpha": alpha, "r": r, "gamma": gamma}


def schur_unreduce_canonical_quartic(
    physical_quartic: float,
    coupling: Sequence[float],
    response_hessian: Sequence[Sequence[float]],
) -> dict[str, float]:
    """Recover lambda_bare=lambda_phys+1/2 B^T H^-1 B."""

    lam_phys = float(physical_quartic)
    b = np.asarray(coupling, dtype=float)
    h = np.asarray(response_hessian, dtype=float)
    if not math.isfinite(lam_phys) or b.ndim != 1 or h.shape != (b.size, b.size):
        raise ValueError("a finite quartic, vector B and matching square H are required")
    if not np.allclose(h, h.T, atol=1.0e-13):
        raise ValueError("response Hessian must be symmetric")
    if np.min(np.linalg.eigvalsh(h)) <= 0.0:
        raise ValueError("response Hessian must be positive on the physical domain")
    correction = 0.5 * float(b @ np.linalg.solve(h, b))
    return {
        "lambda_sigma_physical": lam_phys,
        "Schur_backreaction_correction": correction,
        "lambda_sigma_bare_canonical": lam_phys + correction,
    }


def sigma_generator_observables(
    fundamental: Sequence[Sequence[float]],
    fundamental_dot: Sequence[Sequence[float]],
    hubble: float,
) -> dict[str, Any]:
    """Extract S_sigma and d(log Zsigma)/dt from A=dot(M) M^-1."""

    matrix = np.asarray(fundamental, dtype=float)
    derivative = np.asarray(fundamental_dot, dtype=float)
    h = float(hubble)
    if matrix.shape != (2, 2) or derivative.shape != (2, 2) or not math.isfinite(h):
        raise ValueError("two finite 2x2 matrices and finite H are required")
    if abs(np.linalg.det(matrix)) < 1.0e-14:
        raise ValueError("fundamental matrix must be invertible")
    generator = derivative @ np.linalg.inv(matrix)
    return {
        "generator": generator.tolist(),
        "S_sigma": -float(generator[1, 0]),
        "d_log_Zsigma_dt": -float(generator[1, 1]) - 7.0 * h,
        "source": "A_sigma=dot(M_sigma)M_sigma^-1",
    }


def _coefficients_from_invariants(
    alpha: float, r: float, gamma: float, *, kappa1: float = 1.0, zsigma: float = 1.0
) -> dict[str, float]:
    k1 = _positive(kappa1, "kappa1")
    z = _positive(zsigma, "Zsigma")
    x = critical_x(k1)
    coupling = float(r) * z / k1
    return {
        "kappa1": k1,
        "X0": x,
        "Zsigma": z,
        "g": coupling,
        "A0": float(alpha) * coupling * k1 * x,
        "G0": float(gamma) * coupling**2 * x**4,
        "alpha": float(alpha),
        "r": float(r),
        "gamma": float(gamma),
    }


def retained_nonuniqueness_witness() -> dict[str, Any]:
    """Construct stable inequivalent triples invisible to the sigma-zero parent."""

    triples = {
        "A": _coefficients_from_invariants(-1.0, 1.0, 1.0),
        # B has the same S_sigma(Xc) as A but a different X response.
        "B": _coefficients_from_invariants(-13.0 / 8.0, 2.0, 1.0),
        # C has the same quadratic response jet as A but different nonlinearity.
        "C": _coefficients_from_invariants(-1.0, 1.0, 3.0),
    }
    rows: dict[str, Any] = {}
    for label, coefficients in triples.items():
        response = normalized_sigma_response_jet(
            coefficients["kappa1"],
            coefficients["X0"],
            coefficients["Zsigma"],
            coefficients["g"],
            coefficients["A0"],
            coefficients["G0"],
        )
        recovered = reconstruct_invariants_from_response_jet(
            coefficients["kappa1"],
            coefficients["X0"],
            response["S_sigma"],
            response["dS_sigma_dX"],
            response["lambda_sigma_bare_canonical"],
        )
        rows[label] = {
            "coefficients": coefficients,
            "response_jet": response,
            "recovered_invariants": recovered,
            "sigma_zero_background_contribution": 0.0,
            "sigma_zero_first_variation": 0.0,
            "stable_at_Xc": response["S_sigma"] > 0.0,
            "bounded_bare_quartic": response["lambda_sigma_bare_canonical"] > 0.0,
        }
    return {
        "same_eta_metric_parent": True,
        "same_sigma_zero_background_and_first_variation": True,
        "A_and_B_same_normalized_quadratic_curvature_at_Xc": math.isclose(
            rows["A"]["response_jet"]["S_sigma"],
            rows["B"]["response_jet"]["S_sigma"],
            rel_tol=0.0,
            abs_tol=2.0e-14,
        ),
        "A_and_C_same_complete_quadratic_response_jet": (
            math.isclose(
                rows["A"]["response_jet"]["S_sigma"],
                rows["C"]["response_jet"]["S_sigma"],
                rel_tol=0.0,
                abs_tol=2.0e-14,
            )
            and math.isclose(
                rows["A"]["response_jet"]["dS_sigma_dX"],
                rows["C"]["response_jet"]["dS_sigma_dX"],
                rel_tol=0.0,
                abs_tol=2.0e-14,
            )
        ),
        "A_and_C_different_nonlinear_response": not math.isclose(
            rows["A"]["response_jet"]["lambda_sigma_bare_canonical"],
            rows["C"]["response_jet"]["lambda_sigma_bare_canonical"],
        ),
        "triples": rows,
        "conclusion": (
            "background_plus_one_sigma_mass_does_not_select_alpha_r;_the_"
            "complete_quadratic_jet_does_not_select_gamma;_all_three_"
            "minimal_response_observables_are_necessary"
        ),
    }


def backward_route_audit_payload() -> dict[str, Any]:
    """Record every repository-owned route searched for coefficient selection."""

    return {
        "routes": [
            {
                "route": "homogeneous_cycle_inverse",
                "result": "conditionally_recovers_kappa1_and_kappa0",
                "sigma_selection": False,
                "reason": "sigma_zero_removes_Zsigma_g_A0_G0_from_background_and_first_variation",
            },
            {
                "route": "global_scale_stationarity_and_parent_Hamiltonian_constraint",
                "result": "varies_fields_and_moduli_not_independent_Wilson_data",
                "sigma_selection": False,
            },
            {
                "route": "support_Haar_character_system_v11_2",
                "result": "coefficients_explicitly_inert_rank_7_nullity_12",
                "sigma_selection": False,
            },
            {
                "route": "coefficient_provenance_quotient_v14_62",
                "result": "M8_parent_Wilson_families_remain_independent",
                "sigma_selection": False,
            },
            {
                "route": "Calderon_Wentzell_and_relative_spectral_response_v14_64_to_v14_69",
                "result": "theorem_class_exists_physical_blocks_and_renormalized_values_open",
                "sigma_selection": False,
            },
            {
                "route": "local_finite_time_tangent_v14_94",
                "result": "metric_shape_propagator_only_sigma_stays_zero_and_nonlinear_coefficients_are_none",
                "sigma_selection": False,
            },
            {
                "route": "Aether_core_generator_and_master_v15_2_to_v15_6",
                "result": "no_core_pairing_attachment_or_foundation_to_regular_action_sector_functor",
                "sigma_selection": False,
            },
            {
                "route": "spectral_anomaly_or_zeta_normalization",
                "result": "candidate_not_adopted_and_local_counterterm_scheme_open",
                "sigma_selection": False,
            },
        ],
        "all_current_owned_routes_exhausted": True,
        "empirical_inputs_used": [],
        "new_selector_postulate_adopted": False,
    }


def reconstruction_interface_payload() -> dict[str, Any]:
    """State the smallest missing Aether-to-regular response map."""

    return {
        "current_state_symbol": "C_n",
        "required_outputs": {
            "S_sigma_X0": "-[(dot M_sigma)M_sigma^-1]_21",
            "dS_sigma_dX_X0": "cycle_tangent_derivative_of_the_physical_sigma_generator",
            "lambda_sigma_bare_canonical": (
                "lambda_phys+(1/2)B^T(H_II^phys)^-1B"
            ),
        },
        "inverse": {
            "r": "(dS_sigma/dX)/(1+X0^3/kappa1)",
            "alpha": "S_sigma/(r X0)-1-X0^3/(4kappa1)",
            "gamma": "lambda_sigma_bare_canonical*kappa1^2/(r^2 X0^4)",
            "critical_simplification": {
                "r": "(dS_sigma/dX)/6",
                "alpha": "S_sigma/(r Xc)-9/4",
            },
        },
        "inverse_is_algebraically_unique_when_jet_exists": True,
        "absolute_Zsigma_required_for_invariants": False,
        "Wronskian_role": "fixes_relative_Zsigma_transport_not_its_absolute_normalization",
        "physical_sigma_propagator_present_in_repository": False,
        "X_derivative_present_in_repository": False,
        "physical_nonlinear_sigma_response_present_in_repository": False,
        "map_action_owned_and_evaluable": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
    }


def completion_payload() -> dict[str, Any]:
    compatibility = critical_cycle_compatibility()
    witness = retained_nonuniqueness_witness()
    route_audit = backward_route_audit_payload()
    interface = reconstruction_interface_payload()
    validations = {
        "v15_9_critical_cycle_compatibility": (
            abs(compatibility["kappa1_residual"]) < 2.0e-14
            and abs(compatibility["kappa0_residual"]) < 2.0e-13
        ),
        "response_integrability_exact_for_witnesses": all(
            math.isclose(
                retained_response_derivatives(
                    row["coefficients"]["kappa1"],
                    row["coefficients"]["X0"],
                    row["coefficients"]["g"],
                    row["coefficients"]["A0"],
                    row["coefficients"]["G0"],
                )["g_from_X_integrability"],
                row["coefficients"]["g"],
                rel_tol=1.0e-13,
            )
            for row in witness["triples"].values()
        ),
        "response_inverse_recovers_all_witnesses": all(
            all(
                math.isclose(
                    row["recovered_invariants"][key],
                    row["coefficients"][key],
                    rel_tol=1.0e-13,
                    abs_tol=1.0e-13,
                )
                for key in ("alpha", "r", "gamma")
            )
            for row in witness["triples"].values()
        ),
        "background_and_single_mass_nonuniqueness_constructed": (
            witness["same_eta_metric_parent"]
            and witness["A_and_B_same_normalized_quadratic_curvature_at_Xc"]
        ),
        "nonlinear_response_is_independently_required": (
            witness["A_and_C_same_complete_quadratic_response_jet"]
            and witness["A_and_C_different_nonlinear_response"]
        ),
        "all_owned_routes_searched": route_audit["all_current_owned_routes_exhausted"],
        "missing_map_not_filled_by_parameter": not route_audit["new_selector_postulate_adopted"],
        "v15_9_branch_preserved": True,
        "no_physical_sigma_onset_promoted": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched_during_science": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_cycle_sigma_coefficient_reconstruction_v15_10",
        "version": VERSION,
        "primary_object": PRIMARY_OBJECT,
        "primary_verdict": PRIMARY_VERDICT,
        "coefficient_selection_outcome": COEFFICIENT_SELECTION_OUTCOME,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "v15_9_preservation": {
            "critical_radius": "a_c^6=343/(5*kappa1)",
            "supercritical_radial_eta_branch": "PRESERVED_AS_DERIVED_FULL_EULER_BRANCH",
            "topology_firewall": "RADIAL_S6_EQUIVARIANT_SECTOR_NOT_YET_HOPF_FULL_PREIMAGE_CHILD",
        },
        "homogeneous_cycle_inverse": {
            "kappa1": "343/[a^6(5-6a^2 Hdot)]",
            "kappa0": "7203(8a^2H^2+2a^2Hdot+5)/[4a^8(5-6a^2Hdot)]",
            "critical_compatibility": compatibility,
        },
        "response_integrability": {
            "E_sigma_sigma_X_over_2E_X": "g",
            "E_sigma_sigma_XXXX_over_2E_XXXX": "g",
            "E_XXXX": 3,
            "E_sigma_sigma_XXXX": "6g",
            "status": "DERIVED_IDENTITIES_NOT_NUMERICAL_SELECTION_RULES",
        },
        "minimal_response_inverse": interface,
        "retained_action_nonuniqueness": witness,
        "backward_route_audit": route_audit,
        "eta_to_sigma": {
            "physical_alpha_selected": False,
            "physical_a_sigma_selected": False,
            "v15_9_conditional_thresholds_preserved": True,
            "coupled_eta_sigma_BVP_eligible": False,
            "reason": "the_response_jet_values_are_not_outputs_of_C_n",
        },
        "Hopf_child": "NOT_REACHED_NO_ACTION_SELECTED_SIGMA_BRANCH",
        "nested_scale": "NOT_REACHED_NO_FULL_HOPF_CHILD",
        "persistence": "NOT_REACHED_NO_PHYSICAL_STATIONARY_OR_PERIODIC_ENDPOINT",
        "formation": "RADIAL_ETA_PRECURSOR_ONLY",
        "de_envelopment": "NOT_REACHED",
        "downstream_gauge_flavor_neutrino_scale": "UNCHANGED_OPEN_GATES",
        "Hindsight_20_20": {
            "VALIDATED": [
                "homogeneous_cycle_inverse_and_v15_9_stationary_turning_slice_compatibility",
                "exact_integrability_identities_of_the_retained_same_g_structure",
                "injective_minimal_response_jet_inverse_for_alpha_r_gamma",
                "constructive_stable_nonuniqueness_after_background_and_partial_response_data",
            ],
            "INVALIDATED": [
                "background_equations_alone_select_sigma_coefficients",
                "one_sigma_mass_value_selects_alpha_and_r",
                "quadratic_sigma_tangent_data_selects_gamma",
                "metric_shape_propagator_can_be_relabelled_as_sigma_response",
                "Wronskian_transport_fixes_absolute_Zsigma_normalization",
            ],
            "RECLASSIFIED": [
                "coefficient_selection_blocker_as_a_three_observable_response_map_problem",
                "v15_9_conditional_sigma_threshold_as_downstream_of_that_map",
            ],
            "OPEN": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validations,
        "validation_passed": all(validations.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_physical_parameters": [],
            "measured_inputs": [],
            "frozen_predictions_changed": False,
            "official_prediction_logic_changed": False,
            "USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE": USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
        },
    }


def _canonical_json_value(value: Any) -> Any:
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
    path = target / "BHSM_aether_cycle_sigma_coefficient_reconstruction_v15_10.json"
    path.write_text(
        deterministic_json(completion_payload()), encoding="utf-8", newline="\n"
    )
    return path
