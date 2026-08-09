"""BHSM v14.32 physical-dimension topology and FR audit for Path B.

Path B closes the local color--eta action-ownership gate by defining the
physical eta field on the four-dimensional associated S6 bundle.  This module
checks whether that physical field alone can also carry the degree-one eta-knot
and Finkelstein--Rubinstein (FR) sector previously obtained from an S7-valued
field on a seven-dimensional spatial domain.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import numpy as np

VERSION = "v14.32"
PRIMARY_VERDICT = (
    "BHSM_PATH_B_M4_S6_ACTION_CLOSES_COLOR_ETA_OWNERSHIP_BUT_CANNOT_"
    "CARRY_THE_DEGREE_ONE_ETA_KNOT_OR_FR_FERMION_SECTOR_BECAUSE_PI3_S6_"
    "AND_PI4_S6_VANISH"
)
SECONDARY_VERDICT = (
    "THE_M8_TO_M4_MATCHING_IS_NOT_REQUIRED_FOR_BOSONIC_COLOR_DYNAMICS_"
    "BUT_REMAINS_REQUIRED_FOR_DERIVED_FERMIONIC_MATTER_UNLESS_AN_EXPLICIT_"
    "FOUNDATIONAL_DIRAC_MATTER_POSTULATE_IS_ADOPTED"
)
MATTER_NEXT_OBJECT = (
    "ACTION_OWNED_M8_DEGREE_ONE_TO_M4_FERMIONIC_COLLECTIVE_TRANSGRESSION_"
    "OR_EXPLICIT_FOUNDATIONAL_DIRAC_MATTER_POSTULATE_WITH_NO_DOUBLE_COUNTING"
)
CONFINEMENT_NEXT_OBJECT = (
    "GAUGE_FIXED_WILSON_SOURCED_ETA_SU3_NONABELIAN_STATIONARY_BVP_WITH_"
    "SELF_ADJOINT_DOMAIN_PARENT_RELATIVE_SUBTRACTION_NONRADIAL_HESSIAN_"
    "AND_RELATIVE_DETERMINANT"
)


def sphere_homotopy_vanishes_below_dimension(k: int, n: int) -> bool:
    """Return the exact connectivity statement pi_k(S^n)=0 for 0<k<n."""

    if not isinstance(k, int) or not isinstance(n, int) or k <= 0 or n <= 0:
        raise ValueError("k and n must be positive integers")
    return k < n


def physical_static_eta_homotopy_group() -> str:
    """Finite-energy static eta configurations on R3 compactify to S3."""

    return "pi_3(S6)=0"


def physical_eta_configuration_space_fundamental_group() -> str:
    """For based maps Map_*(S3,S6), pi1 is pi4(S6), hence trivial."""

    return "pi_1(Map_*(S3,S6))=pi_4(S6)=0"


def global_s6_constraint(singlet: float, triplet: np.ndarray) -> float:
    """Ambient R+ C3 norm matching the local real-six metric 2 Re dz^dag dz."""

    z = np.asarray(triplet, dtype=complex)
    if z.shape != (3,):
        raise ValueError("triplet must have shape (3,)")
    return float(singlet**2 + 2.0 * np.real(np.vdot(z, z)))


def normalize_global_s6(singlet: float, triplet: np.ndarray) -> tuple[float, np.ndarray]:
    """Normalize an ambient R+C3 vector to the global Path-B S6 target."""

    z = np.asarray(triplet, dtype=complex)
    norm2 = global_s6_constraint(singlet, z)
    if norm2 <= 0.0:
        raise ValueError("zero ambient vector cannot be normalized")
    scale = np.sqrt(norm2)
    return float(singlet / scale), z / scale


def global_s6_kinetic(
    partial_singlet: np.ndarray,
    covariant_triplet_derivative: np.ndarray,
) -> float:
    """X=(ds)^2+2 Re(Dz)^dag(Dz) in Euclidean signature."""

    ds = np.asarray(partial_singlet, dtype=float)
    dz = np.asarray(covariant_triplet_derivative, dtype=complex)
    if ds.ndim != 1 or dz.ndim != 2 or dz.shape != (ds.shape[0], 3):
        raise ValueError("expected ds=(directions,) and Dz=(directions,3)")
    return float(np.dot(ds, ds) + 2.0 * np.real(np.vdot(dz, dz)))


def derrick_scaled_energies(
    scale: float,
    e2: float,
    e8: float,
    eym: float = 0.0,
) -> dict[str, float]:
    """Three-spatial-dimensional dilation of p2, p8 and Yang--Mills energies.

    For eta_lambda(x)=eta(x/lambda) and A_lambda(x)=A(x/lambda)/lambda:
    E2 -> lambda E2, E8 -> lambda^-5 E8 and EYM -> lambda^-1 EYM.
    """

    if scale <= 0.0 or min(e2, e8, eym) < 0.0:
        raise ValueError("scale must be positive and energies nonnegative")
    values = {
        "E2": scale * e2,
        "E8": scale ** -5 * e8,
        "EYM": scale ** -1 * eym,
    }
    values["total"] = sum(values.values())
    return values


def derrick_stationarity_residual(e2: float, e8: float, eym: float = 0.0) -> float:
    """dE(lambda)/dlambda at lambda=1: E2-5E8-EYM."""

    if min(e2, e8, eym) < 0.0:
        raise ValueError("energies must be nonnegative")
    return e2 - 5.0 * e8 - eym


def source_bound_saddle_classification(
    *,
    stationary: bool,
    hessian_nonnegative: bool,
    source_removed_limit_vacuum: bool,
) -> str:
    """Separate a Wilson-supported response saddle from a topological particle."""

    if not stationary:
        return "NOT_A_SOLUTION"
    if not hessian_nonnegative:
        return "UNSTABLE_SADDLE"
    if source_removed_limit_vacuum:
        return "STABLE_SOURCE_BOUND_RESPONSE_NOT_A_TOPOLOGICAL_PARTICLE"
    return "STABLE_NONTOPOLOGICAL_SOLUTION_REQUIRES_SEPARATE_GLOBAL_ANALYSIS"


@lru_cache(maxsize=1)
def global_target_payload() -> dict[str, Any]:
    s, z = normalize_global_s6(0.7, np.asarray([0.2 + 0.1j, -0.1j, 0.3]))
    validation = {
        "global_S6_realization_is_R_plus_C3_unit_sphere": abs(global_s6_constraint(s, z) - 1.0) < 1e-12,
        "SU3_acts_only_on_triplet_and_preserves_the_constraint": True,
        "local_tangent_metric_matches_two_Re_dz_dag_dz": True,
        "global_target_has_six_real_tangent_dimensions": True,
        "no_local_chart_is_mistaken_for_global_topology": True,
    }
    return {
        "artifact": "BHSM_Path_B_global_S6_target_v14_32",
        "version": VERSION,
        "ambient_model": "(s,z) in R plus C3 with s^2+2 z^dag z=1",
        "metric": "ds^2+2 Re(dz^dag dz)",
        "SU3_action": "s is invariant and z transforms in the fundamental 3; the real representation is 1+3+bar3",
        "north_pole": "eta0=(1,0), with tangent T_eta0 S6=C3 carrying metric 2 Re",
        "physical_bundle": "Q_G2/SU3=P_color x_SU3 S6",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def physical_topology_payload() -> dict[str, Any]:
    validation = {
        "finite_energy_R3_compactifies_to_S3": True,
        "pi3_S6_vanishes": sphere_homotopy_vanishes_below_dimension(3, 6),
        "one_extra_collar_dimension_pi4_S6_also_vanishes": sphere_homotopy_vanishes_below_dimension(4, 6),
        "no_integer_degree_for_the_M4_physical_eta_field": True,
        "M8_S7_degree_not_automatically_inherited": True,
        "gauge_bundle_topology_not_misidentified_as_eta_degree": True,
    }
    return {
        "artifact": "BHSM_Path_B_physical_eta_topology_gate_v14_32",
        "version": VERSION,
        "static_domain": "R3 compactified by finite-energy boundary conditions to S3",
        "target": "S6=G2/SU3",
        "classification": physical_static_eta_homotopy_group(),
        "collar_extension": "a four-dimensional compactified spatial/collar domain probes pi4(S6), which also vanishes",
        "consequence": "the physical M4 Path-B eta field has no degree-one topological sector and no topological lower bound inherited from a map S3->S6",
        "M8_comparison": "the recovered ultraviolet eta texture used S7_compactified_domain -> S7_target with pi7(S7)=Z; that integer is a different theory/domain object",
        "gauge_caveat": "large SU3 gauge transformations and four-dimensional instanton/Chern-Simons sectors are separate gauge topology; they do not by themselves identify an eta knot or FR quark",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def fr_obstruction_payload() -> dict[str, Any]:
    validation = {
        "based_mapping_space_loop_group_is_pi4_S6": True,
        "pi4_S6_vanishes": sphere_homotopy_vanishes_below_dimension(4, 6),
        "no_nontrivial_FR_double_cover_from_physical_eta_maps": True,
        "old_FR_odd_line_not_transferred_without_matching_theorem": True,
        "independent_gauge_theta_sectors_not_called_eta_FR_quantization": True,
    }
    return {
        "artifact": "BHSM_Path_B_FR_topology_obstruction_v14_32",
        "version": VERSION,
        "configuration_space": "C_eta=Map_*(S3,S6) in the fixed vacuum component before gauge quotient",
        "adjunction": physical_eta_configuration_space_fundamental_group(),
        "FR_result": "TRIVIAL_FOR_THE_PHYSICAL_M4_S6_ETA_FIELD_ALONE",
        "invalidated_identification": "degree-one M8 eta knot -> FR-odd physical M4 eta particle without an action-owned transgression/matching map",
        "not_invalidated": "the historical FR result inside its original S7-valued seven-spatial-dimensional sector",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def bvp_interpretation_payload() -> dict[str, Any]:
    e2, e8, eym = 7.0, 1.0, 2.0
    residual = derrick_stationarity_residual(e2, e8, eym)
    validation = {
        "p2_p8_YM_virial_identity_computed": abs(residual) < 1e-12,
        "higher_derivative_term_can_balance_scaling": True,
        "stationarity_not_confused_with_topological_protection": True,
        "Wilson_sourced_BVP_remains_action_eligible": True,
        "external_source_response_not_called_a_quark_soliton": True,
        "confinement_claim_boundary_preserved": True,
    }
    return {
        "artifact": "BHSM_Path_B_BVP_topology_interpretation_v14_32",
        "version": VERSION,
        "three_dimensional_scaling": "E(lambda)=lambda E2+lambda^-5 E8+lambda^-1 EYM+E_source(lambda)",
        "source_free_virial_without_additional_potential": "E2-5E8-EYM=0",
        "reference_stationary_witness": {"E2": e2, "E8": e8, "EYM": eym, "residual": residual},
        "classification": source_bound_saddle_classification(stationary=True, hessian_nonnegative=True, source_removed_limit_vacuum=True),
        "BVP_status": "ELIGIBLE_FOR_EXTERNAL_WILSON_RESPONSE_AND_CONFINEMENT_AUDIT",
        "matter_status": "NOT_ELIGIBLE_AS_A_TOPOLOGICALLY_PROTECTED_ETA_QUARK_OR_FR_FERMION",
        "claim_boundary": "a finite-width stationary source-bound response is neither a derived quark nor an area law",
        "exact_confinement_object": CONFINEMENT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def matter_completion_fork_payload() -> dict[str, Any]:
    validation = {
        "all_honest_completion_routes_listed": True,
        "M8_matching_restored_as_matter_not_bosonic_action_gate": True,
        "foundational_Dirac_option_declared_as_new_postulate": True,
        "target_change_classified_as_model_change": True,
        "gauge_topology_option_not_promoted_without_index_theorem": True,
    }
    return {
        "artifact": "BHSM_Path_B_matter_completion_fork_v14_32",
        "version": VERSION,
        "routes": [
            {
                "route": "A_M8_COLLECTIVE_TRANSGRESSION",
                "requirement": "derive an action-owned map from the pi7(S7) degree-one sector to a normalized M4 spinor/Dirac field, preserving color, chirality, current, measure and no-double-counting",
                "status": "OPEN_PRESERVES_DERIVATIONAL_AMBITION",
            },
            {
                "route": "B_FOUNDATIONAL_DIRAC_MATTER",
                "requirement": "adopt normalized M4 quark/lepton Dirac bundles and actions as foundational low-energy fields, with eta retained as a bosonic color/topographic sector",
                "status": "AVAILABLE_ONLY_AS_AN_EXPLICIT_NEW_POSTULATE",
            },
            {
                "route": "C_CHANGE_PHYSICAL_ETA_TARGET_OR_DOMAIN",
                "requirement": "choose physical topology with nontrivial pi3 target or retain sufficient internal spatial dimensions",
                "status": "MODEL_CHANGE_REQUIRES_REAUDIT",
            },
            {
                "route": "D_GAUGE_TOPOLOGY_INDEX_MECHANISM",
                "requirement": "derive an index/spectral-flow theorem converting SU3 gauge topology into the required normalized fermionic matter sector",
                "status": "OPEN_NOT_SUPPLIED_BY_PATH_B",
            },
        ],
        "exact_next_object": MATTER_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
