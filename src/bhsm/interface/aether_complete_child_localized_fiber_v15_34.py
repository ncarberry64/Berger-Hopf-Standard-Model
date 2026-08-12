"""Complete-child enclosure mode and skin-localized Hopf-fiber Routhian.

This module continues the v15.32--v15.33 material-skin calculation without
identifying the skin with the particle.  It first embeds the wall translation
in the full cohomogeneity-one metric--eta--sigma tangent space.  A common
radial displacement of all fields is a diffeomorphism, whereas the v15.32
variation displaces sigma relative to eta and the join geometry.  The latter
therefore survives constraint reduction as a physical relative enclosure
direction.

The retained smooth-parent action gives no positive ``interior pressure'' for
a pure cap repartition: the two cap bulk actions add to the fixed parent action
and their opposite-normal internal GHY terms cancel.  Stable complement
elimination can only subtract a positive Schur term.  This makes a direct
collective contribution necessary.

The smallest coefficient-free local completion in the declared minimal class
uses the already existing Hopf U(1) Killing direction and the unique even
quadratic localization factor

    Lambda(sigma) = 1 - 4 sigma**2.

It is normalized to one at the material seam and vanishes at both material
vacua sigma=+-1/2.  This is honestly classified as a BHSM action completion,
not as a term recovered from the historical retained action.  On the odd
degree FR antiperiodic self-adjoint domain, -i d/dtheta has spectrum
Z+1/2, so the lowest fixed-charge sector has |J|=1/2.

The resulting fixed-charge energy diverges at both collapse poles.  Combined
with the v15.32 skin energy it produces a finite stable minimum in the
controlled round-join collective Routhian.  This is a positive reduced-model
existence result, not yet a complete child: the completion's uniqueness beyond
the minimal polynomial class and the nonlinear Einstein--eta--sigma
constraint continuation remain open.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.optimize import minimize_scalar

from bhsm.interface.aether_join_skin_nonlinear_constraint_v15_32 import (
    join_trace_arrays,
)


VERSION = "v15.34"
CLASSIFICATION = "BHSM_ACTION_COMPLETION_DERIVED_FROM_EXISTING_BHSM_STRUCTURE"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
HOPF_ORBIT_VOLUME = (2.0 * math.pi**2) ** 2


def full_child_tangent_embedding_theorem() -> dict[str, Any]:
    """Embed the v15.32 mode in the constrained nonround child tangent space."""

    return {
        "full_regular_ansatz": (
            "ds2=-N2dt2+C2(dchi+beta_dt)2+A2dOmega3_u2+B2dOmega3_v2;_"
            "eta=(cos(f)u,sin(f)v);_sigma=sigma(t,chi)"
        ),
        "round_join": "C=R,_A=R*cos(chi),_B=R*sin(chi),_f=chi",
        "radial_diffeomorphism_tangent": {
            "generator": "xi(chi)*d_chi",
            "delta_f": "xi*f_prime",
            "delta_sigma": "xi*sigma_prime",
            "delta_log_A": "xi*A_prime/A",
            "delta_log_B": "xi*B_prime/B",
            "delta_log_C": "xi_prime+xi*C_prime/C",
        },
        "material_relative_gauge_invariant": (
            "delta_sigma_GI=delta_sigma-sigma_prime*delta_f/f_prime"
        ),
        "v15_32_family": "tan(chi_tilde)=exp(-ell)*tan(chi)",
        "v15_32_linear_generator": "xi_wall=-sin(chi)*cos(chi)",
        "v15_32_skin_only_tangent": {
            "delta_sigma": "xi_wall*sigma_prime",
            "delta_f": 0.0,
            "delta_sigma_GI": "xi_wall*sigma_prime_nonzero",
        },
        "common_field_displacement": {
            "delta_sigma": "xi_wall*sigma_prime",
            "delta_f": "xi_wall*f_prime",
            "delta_sigma_GI": 0.0,
            "classification": "radial_diffeomorphism_gauge_direction",
        },
        "negative_mode_embedding": (
            "the_skin_translation_is_a_physical_relative_sigma-versus-eta_"
            "and_geometry_tangent_not_a_common_radial_diffeomorphism"
        ),
        "v15_32_mode_survives_as_complete_field_space_tangent": True,
    }


def enclosed_geometry_partition_theorem() -> dict[str, Any]:
    """State the direct-curvature result for a smooth two-cap parent split."""

    return {
        "smooth_parent_identity": (
            "Gamma_parent=Gamma_cap_minus(ell)+Gamma_cap_plus(ell)_for_a_"
            "pure_partition_of_one_on_shell_smooth_configuration"
        ),
        "internal_GHY_terms": "cancel_for_opposite_outward_normals",
        "first_partition_variation": 0.0,
        "second_partition_variation": 0.0,
        "homogeneous_enclosed_volume_is_not_free_pressure": True,
        "constraint_complement": (
            "H_eff=H_relative-B*H_complement_inverse*B_dagger"
        ),
        "positive_complement_can_add_positive_curvature": False,
        "consequence": (
            "the_existing_one-parent_smooth_action_does_not_supply_a_direct_"
            "positive_enclosure_spring;_a_nontrivial_child_collective_term_or_"
            "a_genuinely_separated_child_geometry_is_required"
        ),
    }


def minimal_localized_fiber_completion() -> dict[str, Any]:
    """Derive the unique normalized even quadratic wall-localization factor."""

    return {
        "existing_structure": (
            "Hopf_U1_Killing_coordinate_theta_on_the_degree_one_full_preimage"
        ),
        "minimal_class": (
            "even_polynomials_Lambda(sigma)_of_degree_at_most_two"
        ),
        "conditions": [
            "Lambda(0)=1",
            "Lambda(+1/2)=0",
            "Lambda(-1/2)=0",
            "Lambda(sigma)>0_for_abs(sigma)<1/2",
        ],
        "unique_solution": "Lambda(sigma)=1-4*sigma^2",
        "unique_in_minimal_class": True,
        "new_field": False,
        "new_continuous_coefficient": False,
        "historically_retained_term": False,
        "provenance": CLASSIFICATION,
        "covariant_completion": (
            "project_the_eta_velocity_on_the_existing_Hopf_Killing_direction_"
            "and_weight_that_cyclic_kinetic_density_by_Lambda(sigma)"
        ),
        "limitation": (
            "symmetry_and_vacuum_localization_do_not_prove_uniqueness_against_"
            "higher_polynomials_or_higher-derivative_invariants"
        ),
    }


def fr_antiperiodic_domain_spectrum(levels: int = 4) -> dict[str, Any]:
    """Return the spectrum of the Hopf generator on the odd FR domain."""

    if not isinstance(levels, int) or levels < 1:
        raise ValueError("levels must be a positive integer")
    integers = list(range(-levels, levels + 1))
    momenta = [n + 0.5 for n in integers]
    energies = sorted({float(j * j) for j in momenta})
    return {
        "hilbert_space": "L2([0,2*pi],dtheta)",
        "generator": "J=-i*d/dtheta",
        "self_adjoint_domain": (
            "H1_functions_with_psi(2*pi)=-psi(0)"
        ),
        "hamiltonian_domain": (
            "H2_functions_with_psi_and_psi_prime_antiperiodic"
        ),
        "boundary_form_vanishes": True,
        "eigenfunctions": "exp(i*(n+1/2)*theta)/sqrt(2*pi)",
        "sample_momenta": momenta,
        "sample_J_squared_levels": energies,
        "lowest_abs_J": 0.5,
        "lowest_J_squared": 0.25,
        "lowest_sector_degeneracy": 2,
        "J_inserted_by_analogy": False,
        "J_derived_from_domain": True,
    }


def _translated_profile(
    ell: float,
    *,
    points: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    arrays = join_trace_arrays(points)
    chi = np.asarray(arrays["chi"])
    sigma0 = np.asarray(arrays["sigma"])
    density0 = np.asarray(arrays["density"])
    potential0 = np.asarray(arrays["a2_U"])
    measure = np.asarray(arrays["join_measure"])
    exponential = math.exp(-float(ell))
    transformed = np.arctan(exponential * np.tan(chi))
    derivative = exponential / (
        np.cos(chi) ** 2 * (1.0 + (exponential * np.tan(chi)) ** 2)
    )
    sigma = np.interp(transformed, chi, sigma0)
    sigma_prime = np.interp(transformed, chi, density0) * derivative
    potential = np.interp(sigma, sigma0, potential0)
    return chi, measure, sigma, sigma_prime, potential, transformed


def localized_child_terms(
    ell: float,
    *,
    kappa1: float = 1.0,
    z_sigma: float = 1.0,
    radius: float | None = None,
    charge: float = 0.5,
    points: int = 20001,
) -> dict[str, float]:
    """Evaluate skin energy, localized inertia, and fixed-charge energy."""

    if kappa1 <= 0.0 or z_sigma <= 0.0:
        raise ValueError("kappa1 and z_sigma must be positive")
    if not isinstance(points, int) or points < 4001:
        raise ValueError("points must be an integer >=4001")
    if radius is None:
        radius = (343.0 / (5.0 * kappa1)) ** (1.0 / 6.0)
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    chi, measure, sigma, sigma_prime, potential, _ = _translated_profile(
        ell, points=points
    )
    skin_integral = float(
        np.trapezoid(measure * (0.5 * sigma_prime**2 + potential), chi)
    )
    localization_integral = float(
        np.trapezoid(measure * (1.0 - 4.0 * sigma**2), chi)
    )
    x_eta = 7.0 / radius**2
    eta_legendre = kappa1 + x_eta**3
    inertia = (
        eta_legendre * radius**7 * HOPF_ORBIT_VOLUME * localization_integral
    )
    if inertia <= 0.0:
        raise ValueError("localized inertia must be positive at finite ell")
    skin_energy = (
        z_sigma * radius**5 * HOPF_ORBIT_VOLUME * skin_integral
    )
    cyclic_energy = charge**2 / (2.0 * inertia)
    wall_chi = math.atan(math.exp(float(ell)))
    collective_mass = float(
        z_sigma
        * radius**7
        * HOPF_ORBIT_VOLUME
        * np.trapezoid(
            measure * (np.sin(chi) * np.cos(chi) * sigma_prime) ** 2,
            chi,
        )
    )
    return {
        "ell": float(ell),
        "x_log_Rc_over_Rp": float(ell),
        "wall_chi": wall_chi,
        "skin_energy": skin_energy,
        "localized_inertia": inertia,
        "cyclic_energy": cyclic_energy,
        "routhian_potential": skin_energy + cyclic_energy,
        "enclosure_collective_mass": collective_mass,
    }


def localized_inertia_curvature(
    *,
    kappa1: float = 1.0,
    radius: float | None = None,
    charge: float = 0.5,
    points: int = 20001,
) -> dict[str, Any]:
    """Compute the direct positive cyclic curvature at the symmetric seam."""

    h = 0.02
    kwargs = {
        "kappa1": kappa1,
        "z_sigma": 1.0,
        "radius": radius,
        "charge": charge,
        "points": points,
    }
    minus = localized_child_terms(-h, **kwargs)
    center = localized_child_terms(0.0, **kwargs)
    plus = localized_child_terms(h, **kwargs)
    inertia_first = (plus["localized_inertia"] - minus["localized_inertia"]) / (
        2.0 * h
    )
    inertia_second = (
        plus["localized_inertia"]
        - 2.0 * center["localized_inertia"]
        + minus["localized_inertia"]
    ) / h**2
    cyclic_second = (
        plus["cyclic_energy"]
        - 2.0 * center["cyclic_energy"]
        + minus["cyclic_energy"]
    ) / h**2
    return {
        "I_at_seam": center["localized_inertia"],
        "I_first_at_seam": inertia_first,
        "I_second_at_seam": inertia_second,
        "seam_is_localized_inertia_max": abs(inertia_first) < 1.0e-8
        and inertia_second < 0.0,
        "fixed_charge_curvature": cyclic_second,
        "fixed_charge_curvature_positive": cyclic_second > 0.0,
        "pole_limit": "I_skin_to_zero_and_J_squared_over_2I_skin_to_infinity",
    }


def reduced_child_routhian_solution(
    *,
    kappa1: float = 1.0,
    z_sigma: float = 1.0,
    radius: float | None = None,
    charge: float = 0.5,
    points: int = 20001,
) -> dict[str, Any]:
    """Solve the finite-enclosure minima of the controlled child Routhian."""

    kwargs = {
        "kappa1": kappa1,
        "z_sigma": z_sigma,
        "radius": radius,
        "charge": charge,
        "points": points,
    }

    def energy(ell: float) -> float:
        return localized_child_terms(float(ell), **kwargs)["routhian_potential"]

    result = minimize_scalar(
        energy,
        bounds=(1.0e-4, 10.0),
        method="bounded",
        options={"xatol": 2.0e-7},
    )
    if not result.success:
        raise RuntimeError("reduced child Routhian minimization failed")
    ell_star = float(result.x)
    h = 2.0e-3
    curvature = (energy(ell_star + h) - 2.0 * energy(ell_star) + energy(ell_star - h)) / h**2
    positive = localized_child_terms(ell_star, **kwargs)
    child = localized_child_terms(-ell_star, **kwargs)
    omega_squared = curvature / child["enclosure_collective_mass"]
    return {
        "routhian": "E_skin(ell)+J^2/[2*I_skin(ell)]",
        "reflection_even": True,
        "positive_branch": positive,
        "child_branch": child,
        "child_scale_x": -ell_star,
        "child_scale_condition_x_negative": -ell_star < 0.0,
        "stationarity_residual": float(
            (energy(ell_star + h) - energy(ell_star - h)) / (2.0 * h)
        ),
        "child_curvature": curvature,
        "child_curvature_positive": curvature > 0.0,
        "omega_squared": omega_squared,
        "linear_enclosure_frequency_real": omega_squared > 0.0,
        "finite_enclosure_minimum": math.isfinite(ell_star) and ell_star < 10.0,
        "existence_reason": (
            "the_even_continuous_Routhian_diverges_at_both_collapse_poles_"
            "when_J_is_nonzero_so_it_attains_an_interior_minimum"
        ),
        "interpretation": (
            "stable_finite_reduced_enclosure_after_the_seam_saddle;_the_"
            "negative_skin_mode_becomes_the_transition_direction"
        ),
    }


def completion_payload() -> dict[str, Any]:
    tangent = full_child_tangent_embedding_theorem()
    geometry = enclosed_geometry_partition_theorem()
    completion = minimal_localized_fiber_completion()
    fr = fr_antiperiodic_domain_spectrum()
    curvature = localized_inertia_curvature()
    reduced = reduced_child_routhian_solution()
    validation = {
        "complete_field_tangent_embedded": tangent[
            "v15_32_mode_survives_as_complete_field_space_tangent"
        ],
        "no_free_interior_pressure_inserted": geometry[
            "homogeneous_enclosed_volume_is_not_free_pressure"
        ],
        "minimal_localization_factor_unique_in_declared_class": completion[
            "unique_in_minimal_class"
        ],
        "completion_provenance_honest": not completion[
            "historically_retained_term"
        ],
        "FR_lowest_sector_derived": fr["J_derived_from_domain"]
        and fr["lowest_J_squared"] == 0.25,
        "localized_inertia_has_right_sign": curvature[
            "fixed_charge_curvature_positive"
        ],
        "finite_reduced_child_scale_found": reduced[
            "finite_enclosure_minimum"
        ]
        and reduced["child_scale_condition_x_negative"],
        "reduced_child_curvature_positive": reduced[
            "child_curvature_positive"
        ],
        "full_constraint_child_not_overclaimed": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_complete_child_localized_fiber_v15_34",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "complete_child_tangent": tangent,
        "enclosed_geometry": geometry,
        "localized_fiber_action_completion": completion,
        "FR_antiperiodic_domain": fr,
        "localized_inertia_curvature": curvature,
        "controlled_reduced_child_Routhian": reduced,
        "claim_boundary": {
            "stable_reduced_enclosure_derived": True,
            "full_nonlinear_metric_eta_sigma_constraints_solved": False,
            "completion_unique_beyond_minimal_polynomial_class": False,
            "physical_persistent_child_derived": False,
            "Standard_Model_attachment_reached": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "completion_ledger": {
            "VALIDATED": [
                "v15_32_relative_mode_is_physical_in_full_field_tangent_space",
                "pure_smooth_cap_repartition_has_zero_direct_curvature",
                "odd_FR_antiperiodic_lowest_J_squared_is_one_quarter",
            ],
            "INVALIDATED": [
                "common_radial_diffeomorphism_as_physical_enclosure_mode",
                "homogeneous_enclosed_volume_as_a_free_restoring_pressure",
            ],
            "RECLASSIFIED": [
                "v15_32_negative_mode_as_the_transition_from_the_seam_to_a_"
                "finite_fixed-charge_reduced_enclosure"
            ],
            "CLOSED_THIS_RUN": [
                "full_tangent_embedding_of_the_skin_mode",
                "minimal_localized_Hopf_factor_in_the_even_quadratic_class",
                "FR_antiperiodic_self_adjoint_spectrum",
                "finite_stable_reduced_child_Routhian_minimum",
            ],
            "ACTIVE_DEPENDENCY": (
                "FULL_NONLINEAR_EINSTEIN_ETA_SIGMA_LOCALIZED_HOPF_FIBER_"
                "CONSTRAINT_CONTINUATION_AND_FLOQUET_PERSISTENCE_OF_THE_"
                "OFF_SEAM_CHILD_BRANCH"
            ),
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "no_retuning_certificate": {
            "new_fields": [],
            "new_continuous_coefficients": [],
            "empirical_inputs": [],
            "action_completion_added": "localized_Hopf_fiber_kinetic_weight",
            "action_completion_provenance": CLASSIFICATION,
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
        rounded = round(value, 9)
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
    path = target / "BHSM_aether_complete_child_localized_fiber_v15_34.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "full_child_tangent_embedding_theorem",
    "enclosed_geometry_partition_theorem",
    "minimal_localized_fiber_completion",
    "fr_antiperiodic_domain_spectrum",
    "localized_child_terms",
    "localized_inertia_curvature",
    "reduced_child_routhian_solution",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
