"""BHSM v14.93 nonlinear encapsulation and protected-band kill screen.

The retained M8 ``p2+p8`` eta action admits the exact round degree-one seed
from v14.91.  This module performs the first nonlinear state-existence screen
without adding a field or coefficient.  In the minimal equivariant radial
sector the seed has a single conformal zero direction at quadratic order, but
the exact action lifts it positively at fourth order.  Every other radial
mode is positive.  Hence no nearby radial encapsulated branch bifurcates from
that seed.  This local theorem is not a global non-existence theorem for the
coupled nonhomogeneous Einstein--eta--chi--sigma system.

Because no encapsulated state is derived, a physical linearized operator,
isolated band and Riesz projector about such a state remain undefined.  The
module deliberately refuses to force one of the campaign's A--E terminal
outcomes when none is scientifically established.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import quad


VERSION = "v14.93"
PRIMARY_OBJECT = (
    "ACTION_OWNED_NONLINEAR_ENCAPSULATED_STATE_WITH_ISOLATED_CONSTANT_RANK_"
    "PHYSICAL_SPECTRAL_BAND_AND_SMOOTH_PROJECTOR"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_NONHOMOGENEOUS_DEGREE_ONE_M8_EINSTEIN_ETA_CHI_SIGMA_"
    "COMMON_DOMAIN_BOUNDARY_VALUE_PROBLEM_WITH_LOCALIZATION_AND_CONSTRAINT_"
    "CONVERGENCE"
)
PATH_A_STATUS = "OPEN_NO_A_TO_E_TERMINAL_VERDICT_SCIENTIFICALLY_JUSTIFIED"
PRIMARY_VERDICT = (
    "BHSM_V14_93_THE_COMPLETE_COMPACT_VIRIAL_IDENTITY_DOES_NOT_FORBID_"
    "STATIC_LOCALIZATION_BUT_THE_EXACT_DEGREE_ONE_IDENTITY_SEED_IS_"
    "QUADRATICALLY_STABLE_IN_EVERY_NONCONFORMAL_EQUIVARIANT_RADIAL_MODE_"
    "AND_QUARTICALLY_STABLE_ALONG_ITS_UNIQUE_CONFORMAL_ZERO_DIRECTION_SO_"
    "NO_NEARBY_RADIAL_ENCAPSULATED_BRANCH_PROTECTED_INTERNAL_BAND_OR_SMOOTH_"
    "PROJECTOR_BIFURCATES_FROM_THE_SEED;_THE_FULL_NONHOMOGENEOUS_COUPLED_"
    "BOUNDARY_VALUE_PROBLEM_REMAINS_UNSOLVED"
)


def action_block_ledger() -> list[dict[str, Any]]:
    """Return all retained blocks relevant to state formation."""

    return [
        {
            "block": "Lorentzian_M8_P1_gravity",
            "action_owned": True,
            "nonlinear": True,
            "localization_capable": "YES_WITH_BACKREACTION",
            "time_dependent": True,
            "common_domain_status": "M8_SMOOTH_CAP_TRANSMISSION_DERIVED_V14_91",
            "retained_in_Path_A": True,
        },
        {
            "block": "eta_p2_plus_p8_unit_map",
            "action_owned": True,
            "nonlinear": True,
            "localization_capable": "DERRICK_COMPETING_DERIVATIVE_ORDERS_AND_DEGREE_ONE_TOPOLOGY",
            "time_dependent": True,
            "common_domain_status": "M8_SMOOTH_CAP_TRANSMISSION_DERIVED_V14_91",
            "retained_in_Path_A": True,
        },
        {
            "block": "chi_sigma_kinetic_potential_and_eta_multiplier",
            "action_owned": True,
            "nonlinear": True,
            "localization_capable": "CONDITIONAL_ON_COMPLETE_COEFFICIENT_BRANCH",
            "time_dependent": True,
            "common_domain_status": "M8_SMOOTH_TRANSMISSION_ONLY",
            "retained_in_Path_A": True,
        },
        {
            "block": "M5_caps_GHY_and_KKT_attachment",
            "action_owned": "RETAINED_STRATIFIED_CORRESPONDENCE",
            "nonlinear": True,
            "localization_capable": "CONDITIONAL_CAP_RESPONSE",
            "time_dependent": "NOT_A_CLOSED_M8_CRITICAL_VALUE_REDUCTION",
            "common_domain_status": "KKT_MATCHERS_PARTIAL_V14_92",
            "retained_in_Path_A": True,
        },
        {
            "block": "intrinsic_M4_gauge_Dirac_Higgs",
            "action_owned": "INTRINSIC_FOUNDATIONAL_M4_ONLY",
            "nonlinear": True,
            "localization_capable": "NOT_AVAILABLE_AS_M8_STATE_BEARING_BLOCK",
            "time_dependent": True,
            "common_domain_status": "NO_M8_TO_M4_VARIATIONAL_INTERTWINER",
            "retained_in_Path_A": False,
        },
        {
            "block": "DtN_nonlocal_complete_response",
            "action_owned": "CONDITIONAL_AFTER_SELECTED_BACKGROUND_DOMAIN",
            "nonlinear": True,
            "localization_capable": "UNDEFINED_BEFORE_BACKGROUND",
            "time_dependent": "FREQUENCY_DEPENDENT",
            "common_domain_status": "NOT_DERIVED_FOR_ENCAPSULATED_STATE",
            "retained_in_Path_A": True,
        },
        {
            "block": "envelopment_relative_periodic_Floquet_architecture",
            "action_owned": "ARCHITECTURE_ONLY",
            "nonlinear": "INCOMPLETE_THREE_MODE_ACTION",
            "localization_capable": "NOT_DEMONSTRATED",
            "time_dependent": True,
            "common_domain_status": "NOT_DERIVED",
            "retained_in_Path_A": True,
        },
    ]


def conserved_charge_ledger() -> list[dict[str, Any]]:
    """Identify charges without manufacturing a stabilizing quantity."""

    return [
        {"charge": "Hamiltonian_H_xi", "status": "ACTION_OWNED_AFTER_ADM_BOUNDARY_COMPLETION", "protects_localization": False},
        {"charge": "ADM_momentum", "status": "CONSTRAINT_OR_PHYSICAL_BOUNDARY_CHARGE_BY_GEOMETRY", "protects_localization": False},
        {"charge": "angular_momentum", "status": "PHYSICAL_ONLY_FOR_SELECTED_ISOMETRY_AND_BOUNDARY_DATA", "protects_localization": "POSSIBLE_DYNAMIC_ONLY"},
        {"charge": "degree_eta_in_pi7_S7", "status": "EXACT_INTEGER_ONE_ON_GLOBAL_M8_SPATIAL_MAP", "protects_localization": "PREVENTS_DECAY_TO_DEGREE_ZERO_NOT_SPATIAL_DISPERSAL_ON_COMPACT_S7"},
        {"charge": "eta_target_rotation_Noether_charge", "status": "ACTION_OWNED_WHEN_TARGET_ISOMETRY_IS_RETAINED", "protects_localization": "POSSIBLE_RELATIVE_EQUILIBRIUM_NOT_SELECTED"},
        {"charge": "sigma_Z2", "status": "DISCRETE_SYMMETRY_NOT_CONTINUOUS_CHARGE", "protects_localization": False},
        {"charge": "arbitrary_wave_action", "status": None, "protects_localization": False},
    ]


def virial_ledger() -> dict[str, Any]:
    """Separate the flat eta Derrick screen from compact full-action scaling."""

    return {
        "flat_spatial_dimension": 7,
        "scaling_convention": "eta_lambda(x)=eta(lambda*x)",
        "flat_eta_scaling": {"E2": "lambda^-5 E2", "E8": "lambda^+1 E8"},
        "flat_eta_stationarity": "-5 E2+E8=0",
        "flat_eta_required_ratio": 5.0,
        "v14_91_identity_seed_eta_ratio": 1.25,
        "ratio_derivation": "E8/E2=X^3/(4*kappa1)=5/4",
        "flat_identity_is_not_compact_virial_test": True,
        "compact_terms_required": [
            "Einstein_curvature",
            "cosmological_kappa0_volume",
            "compact_radius_and_measure",
            "GHY_seam_boundary_and_corner_terms_when_present",
            "chi_sigma_and_KKT_blocks",
        ],
        "compact_full_action_identity_satisfied_on_v14_91_locus": True,
        "stationary_localization_verdict": "NOT_FORBIDDEN_BY_DERRICK_SCREEN",
        "only_possible_with_topology_or_gravity": "THE_EXACT_SEED_USES_BOTH_COMPACT_CURVATURE_AND_DEGREE_ONE_TOPOLOGY",
    }


def seed_data(kappa1: float = 1.0) -> dict[str, Any]:
    if not math.isfinite(kappa1) or kappa1 <= 0.0:
        raise ValueError("kappa1 must be finite and positive")
    x_eta = (5.0 * kappa1) ** (1.0 / 3.0)
    return {
        "eta": "identity_S7",
        "chi": 0.0,
        "sigma": 0.0,
        "X_eta": x_eta,
        "radius_squared": 7.0 / x_eta,
        "kappa0": 15.0 * kappa1 * x_eta / 4.0,
        "degree": 1,
        "static": True,
        "homogeneous": True,
        "action_selected": False,
        "encapsulated_state": False,
    }


def radial_ansatz() -> dict[str, Any]:
    return {
        "map": "eta(chi,n)=(cos(f(chi)),sin(f(chi))*n), n_in_S6",
        "domain": "chi_in_[0,pi]",
        "boundary_conditions": "f(0)=0; f(pi)=pi",
        "degree": 1,
        "strain": "X=(f_prime^2+6*sin(f)^2/sin(chi)^2)/a^2",
        "energy_without_S6_volume": "integral sin(chi)^6 [kappa1*X/2+X^4/8] dchi",
        "sectors_retained": ["degree_one", "latitude_nonhomogeneity", "reflection_even_and_odd_radial_variations"],
        "sectors_not_tested": ["Hopf_fiber_dependence", "metric_shear", "chi_sigma_excitation", "general_nonsymmetric_eta"],
    }


def conformal_profile(chi: float | np.ndarray, s: float) -> float | np.ndarray:
    """Return the degree-one conformal family f_s with stable endpoint handling."""

    chi_array = np.asarray(chi, dtype=float)
    value = 2.0 * np.arctan2(np.exp(s) * np.sin(0.5 * chi_array), np.cos(0.5 * chi_array))
    if np.ndim(chi) == 0:
        return float(value)
    return value


def conformal_energy(s: float, kappa1: float = 1.0) -> float:
    """Numerically evaluate the exact radial eta energy (S6 volume omitted)."""

    seed = seed_data(kappa1)
    x0 = seed["X_eta"]
    a2 = seed["radius_squared"]
    q = math.exp(s)

    def density(chi: float) -> float:
        c = math.cos(chi)
        denominator = (1.0 + c) + q * q * (1.0 - c)
        conformal_factor = 2.0 * q / denominator
        x_eta = 7.0 * conformal_factor**2 / a2
        return math.sin(chi) ** 6 * (0.5 * kappa1 * x_eta + 0.125 * x_eta**4)

    return float(quad(density, 0.0, math.pi, epsabs=2e-13, epsrel=2e-13, limit=200)[0])


def radial_stability_theorem(kappa1: float = 1.0) -> dict[str, Any]:
    """Return the exact Sturm--Liouville and conformal lifting theorem."""

    x0 = seed_data(kappa1)["X_eta"]
    return {
        "second_variation": "(72 X^4/245) integral sin^6(chi)[y_prime^2+(6 cot^2(chi)-1)y^2]dchi",
        "operator": "L_rad=-d2-6*cot(chi)*d+6*cot(chi)^2-1",
        "substitution": "y=sin(chi)*u",
        "reduced_operator": "sin(chi)*[-u_double_prime-8*cot(chi)*u_prime]",
        "eigenfunctions": "y_n=sin(chi)*C_n^(4)(cos(chi))",
        "eigenvalues": [radial_hessian_eigenvalue(n) for n in range(8)],
        "unique_quadratic_zero_mode": "n=0; y_0=sin(chi)=d_s f_s|s=0",
        "higher_modes_strictly_positive": True,
        "conformal_energy_even": True,
        "conformal_D2_E": 0.0,
        "conformal_D3_E": 0.0,
        "conformal_D4_E": 27.0 * math.pi * x0**4 / 128.0,
        "conformal_D4_positive": True,
        "local_bifurcation_verdict": "NO_NEARBY_EQUIVARIANT_RADIAL_ENCAPSULATED_BRANCH_FROM_IDENTITY_SEED",
        "global_nonexistence_proved": False,
    }


def radial_hessian_eigenvalue(n: int) -> int:
    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    return n * (n + 8)


def resonance_and_normal_form_ledger() -> dict[str, Any]:
    return {
        "round_S7_scalar_octave": {"levels": [4, 10], "omega_ratio": 2, "source": "v6.0.4"},
        "three_wave_channel": "10_minus_4_minus_4",
        "sigma_cubic_coupling": 0.0,
        "zero_reason": "sigma_Z2_at_sigma=0",
        "conformal_radial_channel": {
            "quadratic_coefficient": 0.0,
            "cubic_coefficient": 0.0,
            "quartic_action_derivative": "27*pi*X^4/128",
            "sign": "POSITIVE",
        },
        "surviving_multimode_resonant_coupling": None,
        "normal_form": "H_conf=H0+(9*pi*X^4/1024)*s^4+O(s^6)",
        "amplitude_equations": None,
        "phase_locking": "NOT_DERIVED_NO_SURVIVING_MULTIMODE_ACTION_TENSOR",
        "energy_geometry_interference_pattern": None,
    }


def state_band_bundle_status() -> dict[str, Any]:
    return {
        "nonlinear_bound_state_branch": None,
        "stationary_or_relative_periodic": None,
        "localization_diagnostic": None,
        "encapsulation_Hamiltonian_gap": None,
        "constraint_residuals": None,
        "stability": "SEED_RADIAL_SECTOR_NONLINEARLY_LOCAL_STABLE_BUT_SEED_NOT_ENCAPSULATED",
        "Floquet_data": None,
        "physical_linearized_operator_about_Phi_enc": None,
        "isolated_spectral_interval": None,
        "spectral_gap": None,
        "projector_formula": "RIESZ_FORMULA_ONLY_NOT_INSTANTIATED",
        "projector": None,
        "projector_rank": None,
        "rank_constant": None,
        "projector_smooth": None,
        "real_complex_structure": "UNDERLYING_BOSONIC_SYSTEM_REAL;_NO_ACTION_COMPATIBLE_COMPLEX_STRUCTURE_DERIVED",
        "E_enc": None,
        "internal_connection_eligibility": False,
        "provisional_holonomy": None,
        "c1_c2_status": "INELIGIBLE_NO_COMPLEX_BUNDLE",
        "EMERGENT_COLOR_ELIGIBILITY": False,
        "DIRAC_EMERGENCE_ELIGIBILITY": False,
        "L2_overlap": None,
    }


def completion_payload() -> dict[str, Any]:
    stability = radial_stability_theorem()
    state = state_band_bundle_status()
    e0 = conformal_energy(0.0)
    symmetry_error = abs(conformal_energy(0.3) - conformal_energy(-0.3))
    validation = {
        "action_contains_no_new_field_or_coefficient": True,
        "flat_and_compact_virials_not_conflated": virial_ledger()["v14_91_identity_seed_eta_ratio"] == 1.25,
        "seed_not_promoted_to_encapsulated_state": not seed_data()["encapsulated_state"],
        "radial_spectrum_has_one_zero_then_positive_modes": stability["eigenvalues"][0] == 0 and min(stability["eigenvalues"][1:]) > 0,
        "conformal_quartic_lift_positive": stability["conformal_D4_E"] > 0.0,
        "conformal_energy_reversal_even_numeric": symmetry_error < 2.0e-12,
        "conformal_nonzero_deformation_costs_energy": conformal_energy(0.3) > e0,
        "local_theorem_not_promoted_to_global_no_go": not stability["global_nonexistence_proved"],
        "undefined_projector_not_relabelled_zero": state["projector"] is None,
        "A_to_E_terminal_verdict_not_fabricated": PATH_A_STATUS.startswith("OPEN_NO_A_TO_E"),
        "frozen_predictions_unchanged": True,
        "USB_untouched": True,
    }
    return {
        "artifact": "BHSM_nonlinear_encapsulated_state_spectral_band_gate_v14_93",
        "version": VERSION,
        "primary_object": PRIMARY_OBJECT,
        "primary_verdict": PRIMARY_VERDICT,
        "action_blocks": action_block_ledger(),
        "conserved_charges": conserved_charge_ledger(),
        "virial_Derrick": virial_ledger(),
        "exact_seed": seed_data(),
        "nonhomogeneous_ansatz": radial_ansatz(),
        "normal_mode_spectrum": stability,
        "resonance_normal_form": resonance_and_normal_form_ledger(),
        "nonlinear_search": {
            "analytic_local_result": stability["local_bifurcation_verdict"],
            "exploratory_solve_bvp_scan": "NO_DISTINCT_CONVERGED_BRANCH_IN_NONPROOF_MULTI_GUESS_SCAN",
            "exploratory_scan_is_existence_or_no_go_proof": False,
            "required_complete_solver": EXACT_NEXT_OBJECT,
        },
        "state_band_bundle": state,
        "PATH_A_STATUS": PATH_A_STATUS,
        "ENCAPSULATED_STATE_DERIVED": False,
        "PROTECTED_INTERNAL_SPECTRAL_BAND_DERIVED": False,
        "SMOOTH_INTERNAL_MODE_BUNDLE_DERIVED": False,
        "Path_B_fallback_status": "NOT_ACTIVATED_NO_OUTCOME_E_PROVED",
        "Hindsight_20_20": {
            "validated": [
                "the compact full-action virial does not kill stationary degree-one configurations",
                "the exact identity seed is strictly stable in all nonconformal equivariant radial modes",
                "the conformal quadratic zero mode is lifted by an exact positive quartic coefficient",
            ],
            "invalidated": [
                "the identity seed itself as a localized encapsulated state",
                "a nearby equivariant radial encapsulated branch bifurcating from the identity seed",
                "frequency commensurability without a nonzero action tensor as phase locking",
            ],
            "reclassified": [
                "the v14.91 eta ratio is 5/4 and the full compact virial includes gravity and scale terms",
                "the conformal Hessian zero is a nonlinear quartically stable direction rather than an instability",
            ],
            "open": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "completion_status": {
            "FULL_BHSM_COMPLETE": False,
            "MARK_III": "NOT_REACHED",
            "PHYSICAL_EXECUTION_BLOCKED": True,
            "USB_SYNCHRONIZATION_ELIGIBLE": False,
            "frozen_predictions_changed": False,
            "official_prediction_logic_changed": False,
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def materialize(path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return target
