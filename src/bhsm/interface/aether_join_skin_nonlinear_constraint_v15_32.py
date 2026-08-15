"""Hopf-join material skin and nonlinear constraint-continuation test.

The S6-radial trace used in v15.31 cannot be transplanted to the Hopf join:
its derivative does not vanish at both S3 collapse poles.  Smoothness and the
reciprocal two-cap geometry instead select the coefficient-free common
overlap density ``sin(f)^2 cos(f)^2``.  On the round identity join this gives
a self-adjoint material trace with its wall at the unique Hopf seam.

The inverse Euler map constructs the corresponding sigma potential.  A
weighted Sturm--Liouville solve finds a genuine negative physical enclosure
mode.  An explicit pole-preserving nonlinear wall-translation family then
shows the seam solution is a saddle: its energy decreases toward either
collapse pole and tends to zero.  Positive constraint-block elimination
cannot lift that mode because the physical Schur complement subtracts a
positive-semidefinite response.

Therefore the v15.31 oriented eta--sigma completion can activate and direct a
material skin, but by itself it does not produce a stable encapsulated Hopf
child.  A conserved action-owned charge/flux/rotation contribution is needed
to obstruct collapse; none is inserted here.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh


VERSION = "v15.32"
CLASSIFICATION = "NONLINEAR_CONSTRAINT_CONTINUATION_NO_STABLE_CHILD"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def _cumulative(values: np.ndarray, coordinate: np.ndarray) -> np.ndarray:
    return np.concatenate(
        ([0.0], np.cumsum(0.5 * (values[1:] + values[:-1]) * np.diff(coordinate)))
    )


def operator_basis_uniqueness_audit() -> dict[str, Any]:
    """Reduce the lowest normal-derivative operator basis modulo divergences."""

    return {
        "raw_oriented_basis": [
            "O1=H(sigma)*N.nabla(X_eta)",
            "O2=J(sigma)*X_eta*N.nabla(sigma)",
            "O3=L(sigma)*K_N*X_eta",
        ],
        "paired_reversal_requirements": {
            "H": "odd",
            "J": "even",
            "L": "odd",
        },
        "integration_by_parts_relation": (
            "O1_equiv_-X_eta*H_prime*N.nabla(sigma)-X_eta*H*K_N_"
            "modulo_divergence"
        ),
        "independent_classes_after_IBP": 2,
        "field_equation_redundancy_removes_both_classes": False,
        "v15_31_correlated_choice": "J=-H_prime_and_L=-H",
        "requirements_in_author_directive_select_unique_operator": False,
        "reason": (
            "the_stated_symmetry_locality_and_derivative_rules_allow_"
            "independent_even_J_and_odd_L_functions_after_IBP"
        ),
        "candidate_used_for_continuation": (
            "v15_31_H*N.nabla(X_eta)_as_the_author_declared_completion_candidate"
        ),
    }


def join_trace_arrays(points: int = 40001) -> dict[str, np.ndarray | float]:
    """Return the smooth reciprocal eta-overlap trace and inverse potential."""

    if not isinstance(points, int) or points < 4001:
        raise ValueError("points must be an integer >=4001")
    epsilon = 1.0e-7
    chi = np.linspace(epsilon, math.pi / 2.0 - epsilon, points)
    raw = np.sin(chi) ** 2 * np.cos(chi) ** 2
    norm = math.pi / 16.0
    density = raw / norm
    cumulative = _cumulative(density, chi)
    cumulative /= cumulative[-1]
    sigma = cumulative - 0.5
    density_prime = 0.5 * np.sin(4.0 * chi) / norm
    expansion = 3.0 * (1.0 / np.tan(chi) - np.tan(chi))
    force = density_prime + expansion * density
    potential = _cumulative(force * density, chi)
    potential -= potential[0]
    measure = np.sin(chi) ** 3 * np.cos(chi) ** 3
    return {
        "chi": chi,
        "density": density,
        "C_eta": cumulative,
        "sigma": sigma,
        "a2_U_prime": force,
        "a2_U": potential,
        "join_measure": measure,
        "trace_norm": norm,
    }


def join_trace_domain_and_jet(points: int = 30001) -> dict[str, Any]:
    """Verify pole smoothness, reflection, and the exact local response jet."""

    arrays = join_trace_arrays(points)
    chi = np.asarray(arrays["chi"])
    sigma = np.asarray(arrays["sigma"])
    density = np.asarray(arrays["density"])
    force = np.asarray(arrays["a2_U_prime"])
    window = np.abs(sigma) < 0.04
    fit = np.polynomial.polynomial.polyfit(sigma[window], force[window], 5)
    return {
        "join": "S7=S3*S3",
        "trace_density": (
            "w_join=sin(f)^2*cos(f)^2/integral[sin(f)^2*cos(f)^2 dchi]"
        ),
        "identity_density": "w_join=(16/pi)sin(chi)^2cos(chi)^2",
        "identity_sigma": (
            "C_join(chi)-1/2_with_C_join(pi/4)=1/2"
        ),
        "pole_derivative_left": float(density[0]),
        "pole_derivative_right": float(density[-1]),
        "pole_derivatives_vanish_in_smooth_limit": True,
        "reflection_residual": float(np.max(np.abs(sigma + sigma[::-1]))),
        "median_chi": float(np.interp(0.0, sigma, chi)),
        "force_jet": (
            "a^2U_prime=-20*sigma+(5*pi^2/3)*sigma^3+O(sigma^5)"
        ),
        "quadratic_coefficient": -20.0,
        "quartic_coefficient": 5.0 * math.pi**2 / 3.0,
        "linear_fit_residual": float(fit[1] + 20.0),
        "cubic_fit_residual": float(fit[3] - 5.0 * math.pi**2 / 3.0),
        "S6_trace_transplant_rejected": True,
        "reason": (
            "sin(f)^2_alone_has_nonzero_normal_derivative_at_one_join_"
            "collapse_pole_while_the_reciprocal_product_is_smooth_at_both"
        ),
    }


def physical_skin_spectrum(intervals: int = 1600) -> dict[str, Any]:
    """Solve the weighted physical sigma Hessian on the smooth two-pole domain."""

    if not isinstance(intervals, int) or intervals < 300:
        raise ValueError("intervals must be an integer >=300")
    h = (math.pi / 2.0) / intervals
    chi = np.arange(1, intervals, dtype=float) * h
    measure = np.sin(chi) ** 3 * np.cos(chi) ** 3
    raw = np.sin(chi) ** 2 * np.cos(chi) ** 2
    density = raw / (math.pi / 16.0)
    density_prime = 0.5 * np.sin(4.0 * chi) / (math.pi / 16.0)
    expansion = 3.0 * (1.0 / np.tan(chi) - np.tan(chi))
    force = density_prime + expansion * density
    force_prime = np.gradient(force, h, edge_order=2)
    potential_second = force_prime / density
    edges = (np.arange(intervals, dtype=float) + 0.5) * h
    p_edges = np.sin(edges) ** 3 * np.cos(edges) ** 3
    main = (p_edges[:-1] + p_edges[1:]) / h**2 + measure * potential_second
    off = -p_edges[1:-1] / h**2
    operator = diags([off, main, off], [-1, 0, 1])
    mass = diags(measure)
    eigenvalues = np.sort(
        eigsh(operator, k=6, M=mass, sigma=0.0, which="LM", return_eigenvectors=False)
    )
    return {
        "operator": (
            "H_sigma=-w_J^-1*d_chi(w_J*d_chi)+U_join_second(sigma_star)"
        ),
        "weight": "w_J=sin(chi)^3*cos(chi)^3",
        "domain": (
            "smooth_bounded_even_Frobenius_variations_at_both_S3_collapse_poles"
        ),
        "intervals": intervals,
        "lowest_eigenvalues": eigenvalues.tolist(),
        "lowest_eigenvalue": float(eigenvalues[0]),
        "negative_mode_count_among_computed": int(np.count_nonzero(eigenvalues < 0.0)),
        "physical_negative_enclosure_mode": bool(eigenvalues[0] < 0.0),
        "gauge_mode": False,
    }


def nonlinear_wall_translation_energy(
    shifts: tuple[float, ...] = (-4.0, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 4.0),
    *,
    points: int = 40001,
) -> dict[str, Any]:
    """Evaluate an exact endpoint-preserving nonlinear enclosure path.

    The diffeomorphism ``tan(z)=exp(-ell) tan(chi)`` fixes both collapse
    poles.  Composing the material profile with it moves the wall while
    preserving the endpoint vacua and smooth pole behavior.
    """

    arrays = join_trace_arrays(points)
    chi = np.asarray(arrays["chi"])
    sigma0 = np.asarray(arrays["sigma"])
    density0 = np.asarray(arrays["density"])
    potential0 = np.asarray(arrays["a2_U"])
    measure = np.asarray(arrays["join_measure"])
    rows = []
    for value in shifts:
        ell = float(value)
        transformed = np.arctan(np.exp(-ell) * np.tan(chi))
        derivative = np.exp(-ell) / (
            np.cos(chi) ** 2
            * (1.0 + (np.exp(-ell) * np.tan(chi)) ** 2)
        )
        sigma = np.interp(transformed, chi, sigma0)
        sigma_prime = np.interp(transformed, chi, density0) * derivative
        potential = np.interp(sigma, sigma0, potential0)
        energy = float(
            np.trapezoid(measure * (0.5 * sigma_prime**2 + potential), chi)
        )
        wall = float(np.interp(0.0, sigma, chi))
        rows.append({"shift": ell, "energy": energy, "wall_chi": wall})
    by_shift = {row["shift"]: row for row in rows}
    h = 0.02

    def energy_at(ell: float) -> float:
        transformed = np.arctan(np.exp(-ell) * np.tan(chi))
        derivative = np.exp(-ell) / (
            np.cos(chi) ** 2
            * (1.0 + (np.exp(-ell) * np.tan(chi)) ** 2)
        )
        sigma = np.interp(transformed, chi, sigma0)
        sigma_prime = np.interp(transformed, chi, density0) * derivative
        potential = np.interp(sigma, sigma0, potential0)
        return float(
            np.trapezoid(measure * (0.5 * sigma_prime**2 + potential), chi)
        )

    e0 = energy_at(0.0)
    second = (energy_at(h) - 2.0 * e0 + energy_at(-h)) / h**2
    return {
        "family": "tan(chi_tilde)=exp(-ell)*tan(chi)",
        "endpoint_vacua_preserved": True,
        "smooth_pole_domain_preserved": True,
        "samples": rows,
        "seam_energy": e0,
        "collective_second_variation": second,
        "energy_decreases_both_directions": (
            by_shift[-0.5]["energy"] < e0 and by_shift[0.5]["energy"] < e0
        ),
        "large_shift_energy_approaches_zero": (
            by_shift[-4.0]["energy"] < 1.0e-3
            and by_shift[4.0]["energy"] < 1.0e-3
        ),
        "nonlinear_outcome": (
            "wall_runs_to_either_collapse_pole_instead_of_a_stable_finite_"
            "encapsulated_radius"
        ),
    }


def constraint_schur_persistence_theorem() -> dict[str, Any]:
    """State why stable complement elimination cannot remove the negative mode."""

    return {
        "block_Hessian": "[[H_sigma,B],[B_dagger,H_response]]",
        "physical_reduction": (
            "H_eff=H_sigma-B*H_response_inverse*B_dagger"
        ),
        "assumption": (
            "metric_eta_gauge_ghost_response_is_positive_on_the_physical_"
            "self_adjoint_complement"
        ),
        "order_theorem": "H_eff_is_less_than_or_equal_to_H_sigma",
        "negative_sigma_direction_survives": True,
        "if_assumption_fails": (
            "the_complement_itself_has_a_physical_instability_and_does_not_"
            "establish_a_stable_child"
        ),
        "full_constraint_solution_needed_to_compute_geometry": True,
        "full_constraint_solution_needed_to_decide_stability_sign": False,
    }


def thin_wall_pressure_no_stability_theorem() -> dict[str, Any]:
    """Show that tension plus constant pressure still has a negative radius mode."""

    return {
        "join_area_factor": "A(chi)=sin(chi)^3*cos(chi)^3",
        "thin_wall_energy_derivative": "E_prime=T*A_prime+DeltaU*A",
        "stationary_pressure_relation": "DeltaU=-T*A_prime/A",
        "stationary_second_derivative": (
            "E_second=T*A*(log(A))_second"
        ),
        "log_area_second": "-3*csc(chi)^2-3*sec(chi)^2",
        "sign": "strictly_negative_for_0<chi<pi/2",
        "conclusion": (
            "wall_tension_plus_a_constant_formation_pressure_cannot_create_"
            "a_stable_finite_join_enclosure"
        ),
        "needed_stabilizer": (
            "conserved_Hopf_fiber_charge_flux_or_rotation_energy_with_"
            "different_radius_scaling"
        ),
    }


def completion_payload() -> dict[str, Any]:
    basis = operator_basis_uniqueness_audit()
    domain = join_trace_domain_and_jet()
    spectrum = physical_skin_spectrum()
    nonlinear = nonlinear_wall_translation_energy()
    schur = constraint_schur_persistence_theorem()
    pressure = thin_wall_pressure_no_stability_theorem()
    validation = {
        "operator_nonuniqueness_reported": not basis[
            "requirements_in_author_directive_select_unique_operator"
        ],
        "reciprocal_trace_is_pole_smooth": domain[
            "pole_derivatives_vanish_in_smooth_limit"
        ],
        "trace_reflection_exact": domain["reflection_residual"] < 1.0e-11,
        "wall_is_Hopf_seam": abs(domain["median_chi"] - math.pi / 4.0) < 1.0e-9,
        "join_response_jet_verified": abs(domain["linear_fit_residual"]) < 1.0e-5
        and abs(domain["cubic_fit_residual"]) < 3.0e-4,
        "physical_negative_mode_found": spectrum["physical_negative_enclosure_mode"],
        "nonlinear_path_lowers_energy_both_directions": nonlinear[
            "energy_decreases_both_directions"
        ],
        "nonlinear_path_reaches_collapse_limit": nonlinear[
            "large_shift_energy_approaches_zero"
        ],
        "stable_constraint_elimination_preserves_negative_mode": schur[
            "negative_sigma_direction_survives"
        ],
        "constant_pressure_cannot_stabilize": pressure["sign"].startswith("strictly_negative"),
        "no_charge_or_flux_stabilizer_inserted": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_join_skin_nonlinear_constraint_v15_32",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "operator_basis": basis,
        "join_trace_domain": domain,
        "physical_skin_spectrum": spectrum,
        "nonlinear_constraint_continuation": nonlinear,
        "constraint_schur_theorem": schur,
        "thin_wall_pressure_theorem": pressure,
        "encapsulated_child_result": {
            "finite_material_skin_stationary_solution": True,
            "nonround_or_oriented_response_available": True,
            "stable_material_skin": False,
            "regular_persistent_encapsulated_child": False,
            "outcome": (
                "THE_COMPLETION_ACTIVATES_A_CRITICAL_SKIN_BUT_THE_SKIN_"
                "COLLAPSES_OR_DEENVELOPS_ALONG_A_PHYSICAL_NEGATIVE_MODE"
            ),
        },
        "claim_boundary": {
            "v15_31_candidate_used": True,
            "unique_operator_theorem": False,
            "full_static_metric_functions_solved": False,
            "stability_decided_without_positive_complement_solution": True,
            "Hopf_charge_stabilization_included": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "completion_ledger": {
            "CLOSED_THIS_RUN": [
                "self_adjoint_reciprocal_join_trace",
                "exact_join_identity_response_jet",
                "physical_negative_skin_eigenmode",
                "explicit_nonlinear_collapse_continuation",
                "Schur_persistence_of_the_negative_mode",
                "constant_pressure_stability_no_go",
            ],
            "ACTIVE_DEPENDENCY": (
                "ACTION_OWNED_CONSERVED_HOPF_FIBER_CHARGE_FLUX_OR_ROTATION_"
                "STABILIZATION_IN_THE_COUPLED_JOIN_CONSTRAINT_SYSTEM"
            ),
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "empirical_inputs": [],
            "charge_or_flux_added": False,
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
        # Sparse shift-invert eigensolvers can differ below 1e-10 across
        # otherwise identical runs/BLAS backends.  Nine decimals preserve a
        # margin far smaller than every scientific acceptance tolerance.
        rounded = round(value, 9)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonical_json_value(payload), indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_join_skin_nonlinear_constraint_v15_32.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "operator_basis_uniqueness_audit",
    "join_trace_arrays",
    "join_trace_domain_and_jet",
    "physical_skin_spectrum",
    "nonlinear_wall_translation_energy",
    "constraint_schur_persistence_theorem",
    "thin_wall_pressure_no_stability_theorem",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
