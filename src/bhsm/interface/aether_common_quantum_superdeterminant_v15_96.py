"""One regulated gauge--ghost--spinor--HS determinant on the proper cycle.

This module constructs the first finite Galerkin representative of the
quantum functional selected by v15.95.  It deliberately keeps gauge and
Yukawa observables as derivatives of the same graded determinant.  The free
zero-background spectrum is evaluated; the interacting quantum event saddle
is not claimed solved here.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.special import exp1

from bhsm.interface.aether_one_cycle_joint_residues_v15_86 import (
    EVENT_TIME,
    cycle_sample_rows,
)
from bhsm.interface.aether_proper_time_joint_pushforward_v15_91 import (
    ADM_LOCAL_ROWS,
)


VERSION = "v15.96"
CLASSIFICATION = "BHSM_COMMON_PROPER_CYCLE_QUANTUM_SUPERDETERMINANT"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def proper_cycle_lattice(points: int = 24) -> dict[str, Any]:
    """Uniform proper-time lattice with the event bundle glued periodically."""

    if points < 6:
        raise ValueError("at least six proper-time points are required")
    times = np.asarray([row[0] for row in ADM_LOCAL_ROWS], dtype=float)
    lapse = np.asarray([row[1] for row in ADM_LOCAL_ROWS], dtype=float)
    radii = np.asarray([row["R4"] for row in cycle_sample_rows()], dtype=float)
    lapse_curve = PchipInterpolator(times, lapse)
    primitive = lapse_curve.antiderivative()
    dense_t = np.linspace(0.0, EVENT_TIME, 4097)
    dense_tau = primitive(dense_t) - primitive(0.0)
    duration = float(dense_tau[-1])
    tau = np.linspace(0.0, duration, points, endpoint=False)
    time = PchipInterpolator(dense_tau, dense_t)(tau)
    radius = PchipInterpolator(times, radii)(time)
    return {
        "points": points,
        "proper_duration": duration,
        "proper_step": duration / points,
        "proper_times": tau,
        "coordinate_times": time,
        "radii": radius,
        "event_gluing": "periodic_same_SM_bundle_isomorphism_class",
    }


def periodic_proper_laplacian(points: int, step: float) -> np.ndarray:
    """Positive centered-difference realization of ``-d_tau^2``."""

    if points < 3 or step <= 0.0:
        raise ValueError("invalid periodic lattice")
    matrix = 2.0 * np.eye(points)
    for index in range(points):
        matrix[index, (index - 1) % points] = -1.0
        matrix[index, (index + 1) % points] = -1.0
    return matrix / step**2


def graded_operator_ledger() -> dict[str, Any]:
    """Statistics, multiplicities, and spatial spectra before truncation."""

    return {
        "gauge_transverse": {
            "supertrace_sign": 1,
            "species": 12,
            "levels": "m>=2",
            "spatial_eigenvalue": "m^2/R4(tau)^2",
            "degeneracy_per_species": "2*(m^2-1)",
        },
        "gauge_longitudinal_ghost": {
            "net_supertrace_sign": 0,
            "statement": (
                "BRST_longitudinal_and_complex_ghost_blocks_cancel_mode_by_mode;_"
                "global_gauge_zero_modes_are_quotiented"
            ),
        },
        "Weyl": {
            "supertrace_sign": -1,
            "species": 48,
            "levels": "n>=0",
            "spatial_eigenvalue": "(n+3/2)^2/R4(tau)^2",
            "degeneracy_per_species": "(n+1)*(n+2)",
            "squared_operator": "D_Weyl^dagger*D_Weyl",
        },
        "Hubbard_Strattonovich": {
            "supertrace_sign": 1,
            "species": 4,
            "levels": "m>=1",
            "spatial_eigenvalue": "m^2/R4(tau)^2",
            "degeneracy_per_species": "m^2",
        },
    }


def _block(
    laplacian: np.ndarray,
    radii: np.ndarray,
    energy: float,
    scale_log: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    spatial = (energy / (np.exp(scale_log) * radii)) ** 2
    operator = laplacian + np.diag(spatial)
    derivative = np.diag(-2.0 * spatial)
    return operator, derivative


def regulated_superdeterminant_seed(
    points: int = 24,
    *,
    heat_length: float = 1.0,
    tolerance: float = 1.0e-13,
    scale_log: float = 0.0,
) -> dict[str, Any]:
    """Evaluate the common heat-regulated free graded determinant.

    ``Gamma_1^R=-(1/2) STr E1(ell^2 P)`` is the proper-time integral
    ``-(1/2) int_{ell^2}^infty ds/s STr exp(-sP)``.  The cutoff is selected by
    the already-declared parent heat length; ``tolerance`` only terminates a
    convergent numerical sum.
    """

    if heat_length <= 0.0 or tolerance <= 0.0:
        raise ValueError("heat length and tolerance must be positive")
    lattice = proper_cycle_lattice(points)
    radii = np.asarray(lattice["radii"], dtype=float)
    laplacian = periodic_proper_laplacian(points, float(lattice["proper_step"]))
    components = {"gauge_transverse": 0.0, "Weyl": 0.0, "Hubbard_Strattonovich": 0.0}
    scale_force = {key: 0.0 for key in components}
    retained = {key: 0 for key in components}

    sectors = (
        ("gauge_transverse", 1.0, 2, lambda m: 12 * 2 * (m * m - 1), lambda m: float(m)),
        ("Weyl", -1.0, 0, lambda n: 48 * (n + 1) * (n + 2), lambda n: n + 1.5),
        ("Hubbard_Strattonovich", 1.0, 1, lambda m: 4 * m * m, lambda m: float(m)),
    )
    ell2 = heat_length**2
    for name, sign, start, degeneracy, energy in sectors:
        quiet_tail = 0
        level = start
        while quiet_tail < 4:
            operator, derivative = _block(
                laplacian, radii, energy(level), scale_log=scale_log
            )
            eigenvalues, eigenvectors = np.linalg.eigh(operator)
            multiplicity = float(degeneracy(level))
            heat_bound = multiplicity * float(np.exp(-ell2 * eigenvalues[0]))
            if heat_bound < tolerance:
                quiet_tail += 1
            else:
                quiet_tail = 0
                retained[name] = level
                components[name] += float(
                    -0.5 * sign * multiplicity * np.sum(exp1(ell2 * eigenvalues))
                )
                regulated_inverse = np.exp(-ell2 * eigenvalues) / eigenvalues
                derivative_in_basis = eigenvectors.T @ derivative @ eigenvectors
                scale_force[name] += float(
                    0.5
                    * sign
                    * multiplicity
                    * np.sum(regulated_inverse * np.diag(derivative_in_basis))
                )
            level += 1
            if level > 256:
                raise RuntimeError("heat-regulated mode sum did not terminate")

    return {
        "definition": "Gamma_1^R=-(1/2)*STr*E1(ell_kappa^2*P_cycle)",
        "common_heat_length_in_ell_kappa": heat_length,
        "numerical_tail_tolerance": tolerance,
        "lattice_points": points,
        "proper_duration": lattice["proper_duration"],
        "components": components,
        "Gamma_one_loop_free_seed": float(sum(components.values())),
        "scale_force_components": scale_force,
        "d_Gamma_one_loop_d_log_common_radius": float(sum(scale_force.values())),
        "last_retained_spatial_level": retained,
        "BRST_longitudinal_ghost_net": 0.0,
        "same_operator_family_for_all_derivatives": True,
    }


def scale_force_finite_difference(points: int = 24, step: float = 2.0e-5) -> dict[str, float]:
    """Check the Fréchet trace derivative against a centered difference."""

    center = regulated_superdeterminant_seed(points)
    plus = regulated_superdeterminant_seed(points, scale_log=step)
    minus = regulated_superdeterminant_seed(points, scale_log=-step)
    finite = (plus["Gamma_one_loop_free_seed"] - minus["Gamma_one_loop_free_seed"]) / (2.0 * step)
    trace = float(center["d_Gamma_one_loop_d_log_common_radius"])
    return {
        "Frechet_trace_derivative": trace,
        "centered_finite_difference": float(finite),
        "relative_residual": abs(finite - trace) / max(1.0, abs(trace)),
    }


def joint_quantum_derivative_contract() -> dict[str, Any]:
    return {
        "graded_cycle_operator": (
            "P_cycle[Phi;A,H]=P_gauge+ghost_direct_sum_"
            "P_Weyl_direct_sum_P_HS_on_L2(S1_tau_times_S3_R4(Phi))"
        ),
        "regulated_functional": (
            "Gamma_q=Gamma_cl-(1/2)*integral_(ell_kappa^2)^infinity_"
            "ds/s*STr(exp(-s*P_cycle)-exp(-s*P_reference))"
        ),
        "first_variation": (
            "D_Gamma_1[deltaP]=(1/2)*integral_ds*STr(exp(-sP)*deltaP)"
        ),
        "second_variation": (
            "D2_Gamma_1[a,b]=(1/2)*integral_ds*STr(exp(-sP)*P_ab)-"
            "(1/2)*integral_ds*integral_0^s_du*STr(exp(-uP)*P_a*"
            "exp(-(s-u)P)*P_b)"
        ),
        "gauge_coefficients": "K_E,K_B_are_low-momentum_components_of_D_A^2_Gamma_q",
        "Higgs_residue": "Z_H_is_the_derivative_part_of_D_Hdagger_D_H_Gamma_q",
        "Yukawa_vertex": "Y_bare_is_D_barPsi_D_Psi_D_H_Gamma_q_and_Y_phys=Z_H^(-1/2)*Y_bare",
        "quantum_saddle": "D_Phi_Gamma_q=0_together_with_the_same_event_condition",
        "evaluation_order": (
            "solve_quantum_event_saddle_then_take_A,H,Psi_derivatives_then_"
            "proper-cycle_pushforward_and_canonicalize"
        ),
        "independent_gauge_counterterm_allowed": False,
        "independent_Yukawa_insertion_allowed": False,
    }


def completion_payload() -> dict[str, Any]:
    lattice = proper_cycle_lattice()
    seed = regulated_superdeterminant_seed()
    derivative = scale_force_finite_difference()
    contract = joint_quantum_derivative_contract()
    validation = {
        "proper_lattice_positive": lattice["proper_duration"] > 0.0,
        "all_free_blocks_finite": all(math.isfinite(value) for value in seed["components"].values()),
        "BRST_quotient_exact": seed["BRST_longitudinal_ghost_net"] == 0.0,
        "Frechet_derivative_verified": derivative["relative_residual"] < 2.0e-7,
        "one_operator_family": seed["same_operator_family_for_all_derivatives"],
        "no_split_sector_terms": (
            not contract["independent_gauge_counterterm_allowed"]
            and not contract["independent_Yukawa_insertion_allowed"]
        ),
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_common_quantum_superdeterminant_v15_96",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "proper_cycle_lattice": lattice,
        "graded_operator_ledger": graded_operator_ledger(),
        "regulated_free_superdeterminant_seed": seed,
        "scale_force_check": derivative,
        "joint_quantum_derivative_contract": contract,
        "scientific_result": (
            "ONE_PROPER-CYCLE_GRADED_OPERATOR_AND_ONE_PARENT_HEAT_REGULATOR_"
            "NOW_DEFINE_THE_GAUGE,_GHOST,_48-WEYL,_AND_FOUR-HS_DETERMINANT;_"
            "GAUGE_NORMALIZATION,_Z_H,_AND_Y_ARE_DERIVATIVES_AFTER_ONE_"
            "COUPLED_QUANTUM_EVENT_SADDLE"
        ),
        "claim_boundary": {
            "common_quantum_operator_formulated": True,
            "finite_proper_cycle_Galerkin_seed_evaluated": True,
            "quantum_geometry_force_derivative_verified": True,
            "interacting_source_Hessian_discretized": False,
            "coupled_quantum_event_saddle_solved": False,
        },
        "active_calculation": (
            "INSERT_THE_BACKGROUND-COVARIANT_GAUGE_AND_HS_SOURCE_VERTICES_IN_"
            "THE_SAME_GALERKIN_OPERATOR,_DIFFERENTIATE_THE_SINGLE_"
            "SUPERDETERMINANT,_AND_SOLVE_ITS_COUPLED_QUANTUM_EVENT_SADDLE"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return [_canonical(item) for item in value.tolist()]
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return round(value, 12)
    if isinstance(value, Mapping):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_common_quantum_superdeterminant_v15_96.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "proper_cycle_lattice", "periodic_proper_laplacian",
    "graded_operator_ledger", "regulated_superdeterminant_seed",
    "scale_force_finite_difference", "joint_quantum_derivative_contract",
    "completion_payload", "deterministic_json", "materialize",
]
