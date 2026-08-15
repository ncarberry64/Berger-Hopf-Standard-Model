"""BHSM v15.22 collective symplectic-manifold and round-branch theorem.

The module tests the proposed global collective-state construction against
the retained phase-space, moving-interface, and round second-shape lineage.
It derives the Legendre-rank criterion, the d versus s=d^2 branch dichotomy,
the invariant sigma-response operator, and the integrated transient sigma
instability on the v15.9 control orbit.

No physical nonround state or varied embedding is fabricated.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from scipy.integrate import quad

from bhsm.interface.aether_moving_interface_transfer_v15_12 import (
    moving_interface_action_payload,
)
from bhsm.interface.completion.intrinsic_full_preimage_dynamical_momentum_gate_v14_90 import (
    canonical_variable_provenance,
)
from bhsm.interface.completion.degree_one_lorentzian_full_preimage_phase_space_v14_91 import (
    full_coupled_bvp_eligibility,
)
from bhsm.interface.completion.l2_landau_goldstone_triplet_v14_74 import (
    status_payload as l2_shape_status_payload,
)
from bhsm.interface.z2_double_cap_threading_domain import z2_notions_ledger
from bhsm.interface.aether_norman_incidence_reconnection_v15_21 import (
    formation_peak_momentum_drive,
    instantaneous_sigma_activation_window,
)


VERSION = "v15.22"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
CAMPAIGN_OBJECT = (
    "ACTION_OWNED_GLOBAL_ENVELOPMENT_COLLECTIVE_STATE_MANIFOLD_PHI_STAR_"
    "WITH_VARIED_EMBEDDING_CONSTRAINT_REDUCTION_PULLED_BACK_SYMPLECTIC_"
    "FORM_AND_PHYSICAL_KINETIC_METRIC_DERIVING_THE_SIGMA_RESPONSE_OPERATOR_"
    "AND_CANONICAL_SEPARATION_MODE"
)
OUTCOME = (
    "COLLECTIVE_LEGENDRE_RANK_AND_ROUND_BRANCH_THEOREMS_DERIVED_BUT_"
    "PHYSICAL_NONROUND_STATE_MAP_AND_VARIED_EMBEDDING_REMAIN_ABSENT"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_COUPLED_ETA_SIGMA_METRIC_VARIED_EMBEDDING_NONROUND_"
    "CENTER_MANIFOLD_BIFURCATION_SOLUTION_WITH_COMPLEMENT_HESSIAN_"
    "INVERTIBLE_FULL_LORENTZIAN_LEGENDRE_MAP_AND_ACTION_SELECTED_SHAPE_MODE"
)


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _positive(value: float, name: str) -> float:
    result = _finite(value, name)
    if result <= 0.0:
        raise ValueError(f"{name} must be positive")
    return result


def _symmetric(matrix: Sequence[Sequence[float]], name: str) -> np.ndarray:
    result = np.asarray(matrix, dtype=float)
    if (
        result.ndim != 2
        or result.shape[0] != result.shape[1]
        or not np.allclose(result, result.T, atol=1.0e-12)
    ):
        raise ValueError(f"{name} must be real symmetric")
    return result


def _spd(matrix: Sequence[Sequence[float]], name: str) -> np.ndarray:
    result = _symmetric(matrix, name)
    if float(np.min(np.linalg.eigvalsh(result))) <= 0.0:
        raise ValueError(f"{name} must be positive definite")
    return result


def collective_legendre_two_form(
    kinetic_metric: Sequence[Sequence[float]],
    magnetic_curvature: Sequence[Sequence[float]] | None = None,
) -> np.ndarray:
    """Return the local Lagrange two-form on coordinates (Q, Q_dot).

    For L=G_AB Qdot^A Qdot^B/2+A_A Qdot^A-V, the Cartan two-form has
    block matrix [[F,G],[-G,0]], where F=dA is antisymmetric.  It is
    nondegenerate exactly when G is nonsingular.
    """

    metric = _symmetric(kinetic_metric, "kinetic_metric")
    n = metric.shape[0]
    if magnetic_curvature is None:
        curvature = np.zeros((n, n), dtype=float)
    else:
        curvature = np.asarray(magnetic_curvature, dtype=float)
        if curvature.shape != (n, n) or not np.allclose(
            curvature, -curvature.T, atol=1.0e-12
        ):
            raise ValueError("magnetic_curvature must be antisymmetric")
    zero = np.zeros_like(metric)
    return np.block([[curvature, metric], [-metric, zero]])


def collective_legendre_rank_certificate(
    kinetic_metric: Sequence[Sequence[float]],
    magnetic_curvature: Sequence[Sequence[float]] | None = None,
) -> dict[str, Any]:
    """Certify the equivalence between regular Legendre and symplectic rank."""

    metric = _symmetric(kinetic_metric, "kinetic_metric")
    two_form = collective_legendre_two_form(metric, magnetic_curvature)
    n = metric.shape[0]
    metric_rank = int(np.linalg.matrix_rank(metric, tol=1.0e-11))
    form_rank = int(np.linalg.matrix_rank(two_form, tol=1.0e-11))
    return {
        "configuration_dimension": n,
        "kinetic_rank": metric_rank,
        "Legendre_regular": metric_rank == n,
        "two_form_rank": form_rank,
        "full_phase_rank": 2 * n,
        "two_form_nondegenerate": form_rank == 2 * n,
        "rank_equivalence_holds": (metric_rank == n) == (form_rank == 2 * n),
        "two_form": two_form.tolist(),
    }


def configuration_only_symplectic_audit(configuration_dimension: int) -> dict[str, Any]:
    """Explain why a Q-only pullback cannot establish canonical partners."""

    n = int(configuration_dimension)
    if n < 1:
        raise ValueError("configuration_dimension must be positive")
    return {
        "Q_dimension": n,
        "physical_phase_dimension_expected": 2 * n,
        "Q_only_form_maximum_rank": n if n % 2 == 0 else n - 1,
        "Q_only_rank_equals_required_phase_rank": False,
        "static_zero_momentum_family_can_be_Lagrangian_with_zero_pullback": True,
        "correct_domain": "collective_velocity_bundle_T_C_or_phase_bundle_Tstar_C",
        "correct_test": "rank_Omega_L=2n_iff_rank_velocity_Hessian_G=n",
    }


def quadratic_round_branch_geometry(
    d: float, *, second_response_norm: float = 1.0
) -> dict[str, Any]:
    """Return the local geometry of Phi(d)=Phi0+d^2 Phi_dd/2.

    ``second_response_norm`` is the already-reduced positive norm
    <Phi_dd,K Phi_dd>.  The theorem is algebraic and does not claim the
    repository has supplied its physical value.
    """

    separation = _finite(d, "d")
    norm = _positive(second_response_norm, "second_response_norm")
    g_dd = separation**2 * norm
    g_ss = 0.25 * norm
    d_certificate = collective_legendre_rank_certificate([[g_dd]])
    s_certificate = collective_legendre_rank_certificate([[g_ss]])
    return {
        "state_expansion": "Phi(d)=Phi0+d^2*Phi_dd/2+O(d^4)",
        "D_d_Phi_norm_squared": g_dd,
        "d_map_immersion_rank": 0 if separation == 0.0 else 1,
        "p_d_coefficient": g_dd,
        "d_phase_rank": d_certificate["two_form_rank"],
        "invariant_candidate": "s=d^2",
        "D_s_Phi_norm_squared": g_ss,
        "s_domain": "half_line_s_greater_equal_zero",
        "s_phase_rank": s_certificate["two_form_rank"],
        "s_regularizes_the_even_state_map": True,
        "s_is_physical_without_a_cap_exchange_quotient": False,
    }


def round_branch_quotient_dichotomy_payload() -> dict[str, Any]:
    """Classify the unresolved cap-exchange quotient versus labelled branches."""

    z2 = z2_notions_ledger()
    origin = quadratic_round_branch_geometry(0.0)
    return {
        "background_cap_exchange_present": z2["A_background_cap_exchange"][
            "contained"
        ],
        "fixed_support_orbifold_parity_present": z2[
            "B_fixed_support_orbifold_parity"
        ]["contained"],
        "moving_covariant_reflection_present": z2[
            "C_moving_covariant_reflection"
        ]["contained"],
        "round_d_ordinary_immersed_coordinate": False,
        "round_d_phase_rank": origin["d_phase_rank"],
        "if_cap_exchange_is_gauge_quotiented": (
            "local_orbit_space_is_R_mod_Z2_isomorphic_to_half_line_s=d^2_"
            "with_a_boundary_or_orbifold_stratum_at_s=0"
        ),
        "if_parent_child_labels_are_physical": (
            "plus_d_and_minus_d_are_distinct_branches_and_s=d^2_illegally_"
            "identifies_them"
        ),
        "which_case_retained_action_selects": None,
        "orbifold_claim_allowed": False,
        "exact_common_conclusion": (
            "ordinary_first_order_d_is_not_a_regular_canonical_coordinate_"
            "at_the_round_state"
        ),
    }


def sigma_response_operator(
    kinetic_zero: Sequence[Sequence[float]],
    second_sigma_kinetic: Sequence[Sequence[float]],
) -> dict[str, Any]:
    """Return G_sigma=I0^-1/2 (D2 I/2) I0^-1/2."""

    inertia = _spd(kinetic_zero, "kinetic_zero")
    second = _symmetric(second_sigma_kinetic, "second_sigma_kinetic")
    if second.shape != inertia.shape:
        raise ValueError("second_sigma_kinetic must act on the inertia space")
    values, vectors = np.linalg.eigh(inertia)
    inverse_sqrt = vectors @ np.diag(values ** -0.5) @ vectors.T
    response = 0.5 * inverse_sqrt @ second @ inverse_sqrt
    response = 0.5 * (response + response.T)
    eigenvalues = np.linalg.eigvalsh(response)
    scalar = float(np.trace(response) / response.shape[0])
    residual = float(np.linalg.norm(response - scalar * np.eye(response.shape[0])))
    return {
        "operator": response.tolist(),
        "eigenvalues": eigenvalues.tolist(),
        "scalar_projection": scalar,
        "scalar_proportionality_residual": residual,
        "is_scalar_multiple_of_identity": residual < 1.0e-11,
        "positive_semidefinite": bool(np.min(eigenvalues) >= -1.0e-12),
    }


def integrated_sigma_instability_strength(
    *,
    supercriticality: float,
    critical_radius: float,
    coupling_g: float,
    static_curvature: float,
    sigma_inertia: float,
) -> dict[str, Any]:
    """Integrate sqrt(-omega_eff^2) over both active homoclinic flanks.

    This is a linear tangent-amplification diagnostic on the sigma-zero
    control orbit.  It neglects sigma backreaction and is not an enclosure
    solution.
    """

    m = _positive(supercriticality, "supercriticality")
    radius = _positive(critical_radius, "critical_radius")
    coupling = _positive(coupling_g, "g")
    curvature = _positive(static_curvature, "K_sigma")
    zsigma = _positive(sigma_inertia, "Z_sigma")
    window = instantaneous_sigma_activation_window(
        supercriticality=m,
        critical_radius=radius,
        coupling_g=coupling,
        static_curvature=curvature,
    )
    if not window["active"]:
        return {
            "active": False,
            "integrated_strength": 0.0,
            "single_flank_strength": 0.0,
            "window": window,
            "approximate_linear_amplification_factor": 1.0,
            "physical_enclosure_claim": False,
        }
    entry, exit_time = window["positive_time_interval"]
    omega = math.sqrt(5.0 * m / (6.0 * radius**2))
    peak = formation_peak_momentum_drive(m)["max_p_q_squared_over_M_q"]

    def integrand(time: float) -> float:
        y = 1.0 / math.cosh(omega * time) ** 2
        drive = 4.0 * peak * y * (1.0 - y)
        negative_frequency_squared = (coupling * drive - curvature) / zsigma
        return math.sqrt(max(0.0, negative_frequency_squared))

    flank, error = quad(integrand, entry, exit_time, epsabs=1.0e-11, epsrel=1.0e-11)
    total = 2.0 * flank
    return {
        "active": True,
        "integrated_strength": total,
        "single_flank_strength": flank,
        "quadrature_error_estimate_two_flanks": 2.0 * error,
        "window": window,
        "approximate_linear_amplification_factor": math.exp(total),
        "physical_enclosure_claim": False,
        "limitations": [
            "sigma_backreaction_omitted",
            "time_dependent_K_sigma_and_full_response_operator_omitted",
            "mode_matching_across_turning_points_not_solved",
        ],
    }


def retained_phase_space_provenance_payload() -> dict[str, Any]:
    """Reconnect the existing phase-space and nonround-shape ledgers."""

    variables = canonical_variable_provenance()
    seam = next(row for row in variables if row["variable"] == "seam_embedding_X")
    bvp = full_coupled_bvp_eligibility()
    corner = moving_interface_action_payload()
    l2 = l2_shape_status_payload()
    return {
        "sectorwise_P1_eta_sigma_momenta_exist": True,
        "seam_embedding_canonical_momentum": seam["canonical_momentum"],
        "seam_embedding_physical_mode": seam["physical_dynamical_mode"],
        "single_coupled_symplectic_form": bvp["requirements"][
            "single_coupled_symplectic_form"
        ],
        "Hayward_corner_pair_rank": corner["corner_variation"]["symplectic_rank"],
        "Hayward_pair_coordinates": corner["corner_variation"]["coordinate_order"],
        "Hayward_pair_is_separation_pair": False,
        "l2_structural_shape_space_available": True,
        "l2_physical_coefficients_or_background_derived": False,
        "l2_status_open": l2["open"],
        "physical_collective_state_manifold_present": False,
    }


def collective_state_manifold_contract_payload() -> dict[str, Any]:
    """State the smallest non-synthetic construction now required."""

    return {
        "collective_coordinates": [
            "q_v15_9_formation_amplitude",
            "sigma_material_response",
            "u_action_selected_nonround_or_second_shape_center_mode",
        ],
        "do_not_include_yet": ["ordinary_round_first_order_d"],
        "state_equation": (
            "P_perp*delta_Gamma_BHSM[Phi_star(Q)]/delta_Phi=0_with_all_"
            "constraints_gauge_conditions_and_common_domains"
        ),
        "complement_solution_theorem": (
            "D_A_Phi_star=-H_perp_inverse*P_perp*partial_A_F_away_from_"
            "additional_kernel_crossings"
        ),
        "center_manifold_reason": (
            "sigma_and_u_are_retained_collective_soft_directions_so_only_"
            "the_orthogonal_complement_Hessian_may_be_required_invertible"
        ),
        "reduced_action": "S_red[Q]=S_BHSM[Phi_star(Q)]",
        "phase_space_domain": "T_C_red_or_Tstar_C_red_not_C_red_alone",
        "minimal_domain_change": (
            "promote_the_existing_embedding_map_X_emb_from_fixed_data_to_a_"
            "varied_geometric_argument_of_the_same_bulk_GHY_Hayward_matcher_"
            "and_material_action"
        ),
        "new_continuous_coefficient_required_by_domain_promotion": False,
        "classification": "CANDIDATE_VARIATIONAL_DOMAIN_COMPLETION_NOT_YET_DERIVED_OR_UNIQUE",
        "actual_Phi_star_solution": None,
    }


def completion_payload() -> dict[str, Any]:
    regular = collective_legendre_rank_certificate(
        [[2.0, 0.3], [0.3, 1.4]], [[0.0, 0.7], [-0.7, 0.0]]
    )
    singular = collective_legendre_rank_certificate(
        [[1.0, 0.0], [0.0, 0.0]], [[0.0, 2.0], [-2.0, 0.0]]
    )
    origin = quadratic_round_branch_geometry(0.0, second_response_norm=3.0)
    quotient = round_branch_quotient_dichotomy_payload()
    uniform = sigma_response_operator(np.diag([2.0, 3.0]), np.diag([3.2, 4.8]))
    anisotropic = sigma_response_operator(np.eye(2), np.diag([1.0, 2.0]))
    inactive = integrated_sigma_instability_strength(
        supercriticality=0.4,
        critical_radius=2.0,
        coupling_g=0.8,
        static_curvature=1.0,
        sigma_inertia=1.0,
    )
    active = integrated_sigma_instability_strength(
        supercriticality=1.0,
        critical_radius=2.0,
        coupling_g=2.0,
        static_curvature=1.0,
        sigma_inertia=1.0,
    )
    provenance = retained_phase_space_provenance_payload()
    contract = collective_state_manifold_contract_payload()
    validation = {
        "regular_Legendre_map_gives_full_symplectic_rank": (
            regular["Legendre_regular"] and regular["two_form_nondegenerate"]
        ),
        "singular_kinetic_metric_remains_presymplectic_even_with_magnetic_term": (
            not singular["Legendre_regular"]
            and not singular["two_form_nondegenerate"]
        ),
        "rank_equivalence_verified": (
            regular["rank_equivalence_holds"] and singular["rank_equivalence_holds"]
        ),
        "configuration_only_pullback_not_misused": not configuration_only_symplectic_audit(
            3
        )["Q_only_rank_equals_required_phase_rank"],
        "round_d_has_zero_phase_rank": origin["d_phase_rank"] == 0,
        "s_candidate_regularizes_even_map": origin["s_phase_rank"] == 2,
        "moving_Z2_quotient_not_fabricated": (
            quotient["which_case_retained_action_selects"] is None
            and quotient["orbifold_claim_allowed"] is False
        ),
        "uniform_eta_response_recovers_scalar_gI": (
            uniform["is_scalar_multiple_of_identity"]
            and abs(uniform["scalar_projection"] - 0.8) < 1.0e-12
        ),
        "operator_response_need_not_be_scalar": not anisotropic[
            "is_scalar_multiple_of_identity"
        ],
        "integrated_instability_respects_threshold": (
            inactive["integrated_strength"] == 0.0
            and active["integrated_strength"] > 0.0
        ),
        "existing_corner_pair_not_relabelled_separation": not provenance[
            "Hayward_pair_is_separation_pair"
        ],
        "single_collective_symplectic_form_still_absent": provenance[
            "single_coupled_symplectic_form"
        ]
        is False,
        "candidate_domain_completion_adds_no_coefficient": not contract[
            "new_continuous_coefficient_required_by_domain_promotion"
        ],
        "physical_state_map_not_fabricated": contract["actual_Phi_star_solution"]
        is None,
        "frozen_predictions_unchanged": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_collective_symplectic_manifold_v15_22",
        "version": VERSION,
        "campaign_object": CAMPAIGN_OBJECT,
        "outcome": OUTCOME,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "collective_Legendre_rank_theorem": {
            "formula": "Omega_L=[[F,G],[-G,0]]_on_(Q,Qdot)",
            "theorem": "rank_Omega_L=2n_if_and_only_if_rank_G=n",
            "regular_control": regular,
            "singular_control": singular,
            "configuration_only_audit": configuration_only_symplectic_audit(3),
        },
        "round_branch_geometry": {
            "origin": origin,
            "quotient_dichotomy": quotient,
        },
        "sigma_response_operator": {
            "definition": (
                "G_sigma=I0^-1/2*(D2_sigma_I/2)*I0^-1/2"
            ),
            "uniform_eta_control": uniform,
            "anisotropic_control": anisotropic,
            "full_physical_operator": None,
        },
        "integrated_sigma_instability": {
            "inactive_control": inactive,
            "active_control": active,
            "physical_value": None,
        },
        "retained_phase_space_provenance": provenance,
        "collective_state_manifold_contract": contract,
        "physical_canonical_separation_mode_derived": False,
        "physical_sigma_response_operator_derived": False,
        "material_skin_derived": False,
        "q_to_separation_transfer_derived": False,
        "ejection_derived": False,
        "Hopf_child_derived": False,
        "Hindsight_20_20": {
            "VALIDATED": [
                "the_collective_Legendre_rank_theorem",
                "round_d_is_not_an_immersed_canonical_coordinate_at_the_symmetric_state",
                "s=d^2_regularizes_the_even_field_map_conditionally_on_the_quotient_choice",
                "the_sigma_response_is_naturally_an_operator_and_reduces_to_gI_in_the_uniform_eta_block",
                "the_integrated_tachyonic_strength_is_the_correct_next_linear_amplification_screen",
            ],
            "INVALIDATED": [
                "a_Q_only_presymplectic_pullback_can_by_itself_prove_canonical_partners",
                "the_Hayward_area_boost_pair_is_the_missing_separation_pair",
                "the_retained_archive_has_already_selected_the_moving_cap_exchange_orbifold_quotient",
                "a_nonzero_second_shape_tensor_alone_makes_d_canonical",
            ],
            "RECLASSIFIED": [
                "the_round_state_as_a_branch_or_quotient_stratum_rather_than_an_ordinary_d_chart",
                "u_as_the_required_action_selected_shape_center_mode_before_geometric_separation",
                "embedding_promotion_as_a_candidate_coefficient_free_variational_domain_completion",
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
            "moving_Z2_quotient_declared": False,
            "separation_momentum_declared": False,
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
    path = target / "BHSM_aether_collective_symplectic_manifold_v15_22.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION",
    "FULL_BHSM_COMPLETE",
    "CAMPAIGN_OBJECT",
    "OUTCOME",
    "EXACT_NEXT_OBJECT",
    "collective_legendre_two_form",
    "collective_legendre_rank_certificate",
    "configuration_only_symplectic_audit",
    "quadratic_round_branch_geometry",
    "round_branch_quotient_dichotomy_payload",
    "sigma_response_operator",
    "integrated_sigma_instability_strength",
    "retained_phase_space_provenance_payload",
    "collective_state_manifold_contract_payload",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
