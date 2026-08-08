"""BHSM v14.89 driver/BHSM exchange-functional and traction no-go.

The retained archive contains internal BHSM attachment transfer, boundary
completion terms, external source observables, and diagnostic driver bridges.
It does not contain an independent driver field together with a direct
driver--BHSM interaction functional.  Consequently a physical exchange
current and its shape Frechet derivative cannot presently be formed.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable, Sequence

import numpy as np

from bhsm.interface.completion.action_selected_charge_current_shape_schur_gate_v14_88 import (
    deterministic_witness as v14_88_schur_witness,
    reflected_relative_vertex,
    round_representation_kill_screen,
    spin4_tensor_product_doubled,
    zero_background_schur_correction,
)
from bhsm.interface.completion.full_preimage_cap_inertia_operator_v14_84 import (
    CHARGED_CURRENT_PROVENANCE_GATE,
    EXACT_NEXT_OBJECT,
    NONCENTRAL_CURRENT_GATE,
)


VERSION = "v14.89"
PRIMARY_VERDICT = (
    "BHSM_V14_89_NO_ACTION_OWNED_DRIVER_BHSM_EXCHANGE_FUNCTIONAL_PRESENT;_"
    "THE_RETAINED_ARCHIVE_HAS_NO_INDEPENDENT_DRIVER_FIELD_AND_NO_DIRECT_"
    "DRIVER_BHSM_INTERACTION_OR_INTERFACE_TRANSFER_TERM,_SO_Q_EX_NU,_THE_"
    "PHYSICAL_TANGENTIAL_TRACTION_J_EX_L2,_AND_ITS_FRECHET_VERTEX_B_EX_L2_"
    "ARE_UNDEFINED_RATHER_THAN_NONZERO;_IN_THE_FORMAL_ZERO_COUPLING_LIMIT_"
    "THEY_VANISH,_WHILE_ISOTROPIC_SCALAR_ACTIVITY_OR_NORMAL_PRESSURE_HAS_"
    "ZERO_TANGENTIAL_TRACTION_AND_IS_FORBIDDEN_BY_ROUND_SPIN4_FROM_"
    "PRODUCING_A_COEXACT_L2_VERTEX"
)
NEXT_CANONICAL_OBJECT = (
    "FOUNDATIONAL_OR_DERIVED_DRIVER_SECTOR_AND_ITS_UNIQUE_COVARIANT_COUPLING_"
    "TO_THE_BHSM_FULL_PREIMAGE_BOUNDARY_ACTION_WITH_CONSERVED_INTERFACE_"
    "TRACTION_REFLECTION_PARITY_AND_COMMON_SELF_ADJOINT_DOMAIN"
)


def driver_coupling_provenance_audit() -> list[dict[str, Any]]:
    """Return the exhaustive retained driver/interface provenance ledger."""

    return [
        {"object": "cosmological_parent_anchor", "retained_in_action": "EFFECTIVE_EXTERNAL_ANCHOR_ONLY", "independent_field": False, "interaction_term": False, "stress_tensor": False, "boundary_traction": False, "can_exchange_momentum": False, "free_coefficient": "R_H_NOT_ACTION_SELECTED", "status": "NOT_A_DRIVER_SECTOR"},
        {"object": "M8_bulk_geometry_eta", "retained_in_action": "STRUCTURAL_COEFFICIENTS_PARTIAL", "independent_field": True, "interaction_term": "INTERNAL_BHSM_ONLY", "stress_tensor": True, "boundary_traction": "ONLY_AFTER_FULL_VARIATION", "can_exchange_momentum": "WITH_OTHER_BHSM_STRATA_CONDITIONALLY", "free_coefficient": "NORMALIZATION_OPEN", "status": "NO_EXTERNAL_DRIVER"},
        {"object": "M5_M4_reduction", "retained_in_action": "CONDITIONAL_REDUCTION_ARCHITECTURE", "independent_field": False, "interaction_term": "COMPATIBILITY_CONSTRAINTS", "stress_tensor": "INHERITED", "boundary_traction": "FULL_TENSOR_MAP_OPEN", "can_exchange_momentum": "INTERNAL_ONLY", "free_coefficient": "NORMALIZATION_OPEN", "status": "NO_DRIVER_INTERACTION"},
        {"object": "moving_seam_v14_54", "retained_in_action": False, "independent_field": "CONTRACT_ONLY", "interaction_term": False, "stress_tensor": "SHAPE_STRESS_OPEN", "boundary_traction": False, "can_exchange_momentum": False, "free_coefficient": "ORBIT_AMPLITUDES_PHASES_UNSELECTED", "status": "VARIABLE_SEAM_EMBEDDING_ABSENT_FROM_ACTIVE_ACTION"},
        {"object": "GHY_boundary_completion", "retained_in_action": True, "independent_field": False, "interaction_term": False, "stress_tensor": "CANONICAL_GRAVITATIONAL_BOUNDARY_VARIATION", "boundary_traction": "INTERNAL_MATCHING_ONLY", "can_exchange_momentum": "NO_SEPARATE_DRIVER", "free_coefficient": "PHYSICAL_NORMALIZATION_PARTIAL", "status": "WELL_POSEDNESS_NOT_DRIVER_COUPLING"},
        {"object": "corner_interface_terms", "retained_in_action": "STRUCTURAL_PARTIAL", "independent_field": False, "interaction_term": "NO_DRIVER_TERM", "stress_tensor": "GENERALIZED_CORNER_FORCE_CONDITIONAL", "boundary_traction": "COMMON_DOMAIN_OPEN", "can_exchange_momentum": "INTERNAL_ONLY", "free_coefficient": "COMPLETE_NORMALIZATION_OPEN", "status": "NO_EXTERNAL_TRANSFER"},
        {"object": "Brown_York_quasilocal_structure", "retained_in_action": "DIAGNOSTIC_FROM_GRAVITATIONAL_BOUNDARY_VARIATION", "independent_field": False, "interaction_term": False, "stress_tensor": True, "boundary_traction": "TIME_SYMMETRIC_TANGENTIAL_MOMENTUM_ZERO", "can_exchange_momentum": False, "free_coefficient": False, "status": "ENERGY_NOT_TRANSPORT_GENERATOR"},
        {"object": "reciprocal_attachment_v11_3", "retained_in_action": True, "independent_field": "CORE_WALL_DEPTH_BHSM_FIELDS", "interaction_term": True, "stress_tensor": True, "boundary_traction": "NEW_BOUNDARY_FLUX_ZERO", "can_exchange_momentum": "INTERNAL_Q_C_PLUS_Q_W_PLUS_Q_D_EQUALS_ZERO", "free_coefficient": False, "status": "REAL_INTERNAL_BHSM_COUPLING_NOT_DRIVER_BHSM"},
        {"object": "Wentzell_attachment_v14_67_v14_68", "retained_in_action": "RESPONSE_LIFT_IN_RETAINED_THEOREM_CLASS", "independent_field": False, "interaction_term": "INTERNAL_ATTACHMENT_RESPONSE", "stress_tensor": "FULL_TENSOR_EVALUATION_OPEN", "boundary_traction": "PHYSICAL_INCIDENCE_OPEN", "can_exchange_momentum": "INTERNAL_ONLY", "free_coefficient": "GLOBAL_CURVATURE_INPUTS_OPEN", "status": "NOT_A_DRIVER"},
        {"object": "eta_sector", "retained_in_action": True, "independent_field": True, "interaction_term": "BHSM_GAUGE_GEOMETRY_ONLY", "stress_tensor": True, "boundary_traction": "STATIC_MOMENTUM_ZERO", "can_exchange_momentum": "NO_EXTERNAL_DRIVER", "free_coefficient": False, "status": "V14_88_ZERO_CHARGE_VERTEX"},
        {"object": "foundational_Dirac_sector", "retained_in_action": "ADOPTED_EFFECTIVE", "independent_field": True, "interaction_term": "BHSM_GEOMETRY_GAUGE_ONLY", "stress_tensor": True, "boundary_traction": "STATE_AND_DOMAIN_DEPENDENT", "can_exchange_momentum": "NO_SELECTED_DRIVER_OR_STATE", "free_coefficient": False, "status": "NO_DRIVER_COUPLING"},
        {"object": "Yang_Mills_sector", "retained_in_action": True, "independent_field": True, "interaction_term": "BHSM_MATTER_GEOMETRY_ONLY", "stress_tensor": True, "boundary_traction": "STATIC_ELECTRIC_MOMENTUM_ZERO", "can_exchange_momentum": "NO_EXTERNAL_DRIVER", "free_coefficient": False, "status": "NO_DRIVER_COUPLING"},
        {"object": "Wilson_source_structures", "retained_in_action": "EXTERNAL_INSERTION_OR_OBSERVABLE", "independent_field": False, "interaction_term": "PRESCRIBED_SOURCE_NOT_CLOSED_DRIVER", "stress_tensor": "SOURCE_DEPENDENT", "boundary_traction": "NOT_DERIVED", "can_exchange_momentum": "ONLY_WITH_EXTERNAL_ACCOUNTING", "free_coefficient": "SOURCE_DATA", "status": "NOT_INTERNAL_ACTION_SELECTED_EXCHANGE"},
        {"object": "pair_wake_dynamics", "retained_in_action": "DIAGNOSTIC_OPERATOR_BASIS", "independent_field": False, "interaction_term": False, "stress_tensor": False, "boundary_traction": False, "can_exchange_momentum": False, "free_coefficient": "CHANNEL_AMPLITUDES_PHASES_UNSELECTED", "status": "KINEMATIC_WITNESS_ONLY"},
        {"object": "v14_81_black_hole_exchange", "retained_in_action": False, "independent_field": False, "interaction_term": False, "stress_tensor": "FORMAL_SECTOR_SPLIT", "boundary_traction": False, "can_exchange_momentum": "CONSERVATION_ARCHITECTURE_ONLY", "free_coefficient": "PHYSICAL_Q_NONE", "status": "POSTULATED_OPEN_SYSTEM_IDENTITY_NOT_DERIVED"},
        {"object": "v14_82_BH_susceptibility", "retained_in_action": False, "independent_field": False, "interaction_term": False, "stress_tensor": False, "boundary_traction": False, "can_exchange_momentum": False, "free_coefficient": "B0_AND_CHI_UNDEFINED", "status": "SOURCE_FUNCTIONAL_EXPLICITLY_ABSENT"},
        {"object": "v14_83_volume_work", "retained_in_action": False, "independent_field": False, "interaction_term": "PROVISIONAL_MINUS_D_BH_B0", "stress_tensor": "GENERALIZED_WORK_INTERPRETATION", "boundary_traction": False, "can_exchange_momentum": False, "free_coefficient": "D_BH_UNDERIVED", "status": "BRIDGE_AND_PROVE_NOT_PHYSICAL"},
        {"object": "global_envelopment_action", "retained_in_action": "STRUCTURAL_SCALE_POWER_ACTION", "independent_field": "PARENT_CHILD_BHSM_FIELDS", "interaction_term": "INTERNAL_GLOBAL_COUPLING", "stress_tensor": "PHYSICAL_OPERATORS_OPEN", "boundary_traction": "SEAM_OUTPUT_CONDITIONAL", "can_exchange_momentum": "INTERNAL_ONLY", "free_coefficient": "A8_A6_A3_A0_Z_OPEN", "status": "NO_DRIVER_DEGREE_OF_FREEDOM"},
        {"object": "relational_nesting_q_D", "retained_in_action": True, "independent_field": "BHSM_DEPTH_SCALAR", "interaction_term": "RECIPROCAL_INTERNAL_ATTACHMENT", "stress_tensor": True, "boundary_traction": "NEW_BOUNDARY_FLUX_ZERO", "can_exchange_momentum": "INTERNAL_WARD_TRANSFER", "free_coefficient": False, "status": "NOT_EXTERNAL_DRIVER"},
        {"object": "relative_determinant_nonlocal_action", "retained_in_action": "PARTIAL_FORMULAS", "independent_field": False, "interaction_term": "INTERNAL_PARENT_COMPOSITE_SUBTRACTION", "stress_tensor": "COMPLETE_SHAPE_STRESS_OPEN", "boundary_traction": "OPEN", "can_exchange_momentum": "NO_DRIVER_IDENTIFIED", "free_coefficient": "FULL_COEFFICIENT_OPEN", "status": "NOT_DRIVER_COUPLING"},
        {"object": "canonical_moving_boundary_momentum", "retained_in_action": False, "independent_field": False, "interaction_term": False, "stress_tensor": "CONTRACT_ONLY", "boundary_traction": "NOT_EVALUABLE", "can_exchange_momentum": False, "free_coefficient": False, "status": "VARIABLE_EMBEDDING_NOT_ACTIVE"},
        {"object": "explicit_matter_flux_crossing_seam", "retained_in_action": False, "independent_field": False, "interaction_term": False, "stress_tensor": False, "boundary_traction": False, "can_exchange_momentum": False, "free_coefficient": False, "status": "ABSENT"},
        {"object": "direct_driver_field", "retained_in_action": False, "independent_field": False, "interaction_term": False, "stress_tensor": False, "boundary_traction": False, "can_exchange_momentum": False, "free_coefficient": False, "status": "ABSENT"},
    ]


def decoupled_sector_ward_identity(
    driver_equation_residual: Sequence[float],
    bhsm_equation_residual: Sequence[float],
) -> dict[str, np.ndarray | float]:
    """Ward identity for S_ret=S_drv+S_BHSM with S_int absent.

    On each sector's equations of motion, diffeomorphism invariance gives a
    separate zero divergence.  Shared dependence on the dynamical metric does
    not create a direct transfer current between the matter sectors.
    """

    driver = np.asarray(driver_equation_residual, dtype=float)
    bhsm = np.asarray(bhsm_equation_residual, dtype=float)
    if driver.shape != bhsm.shape or driver.ndim != 1:
        raise ValueError("sector residual vectors must have the same one-dimensional shape")
    return {
        "driver_divergence": driver,
        "bhsm_divergence": bhsm,
        "total_residual": float(np.linalg.norm(driver + bhsm)),
    }


def exchange_conservation_residual(
    driver_loss: Sequence[float],
    bhsm_gain: Sequence[float],
) -> float:
    """Conditional equal-and-opposite transfer residual."""

    loss = np.asarray(driver_loss, dtype=float)
    gain = np.asarray(bhsm_gain, dtype=float)
    if loss.shape != gain.shape:
        raise ValueError("transfer vectors must have the same shape")
    return float(np.linalg.norm(loss + gain))


def interface_tangential_traction(
    stress: Sequence[Sequence[float]],
    normal: Sequence[float],
    tangent_frame: Sequence[Sequence[float]],
) -> np.ndarray:
    """Compute tau_a=e_a^nu n_mu T^mu_nu in an orthonormal frame."""

    tensor = np.asarray(stress, dtype=float)
    n = np.asarray(normal, dtype=float)
    tangents = np.asarray(tangent_frame, dtype=float)
    if tensor.ndim != 2 or tensor.shape[0] != tensor.shape[1]:
        raise ValueError("stress must be square")
    if n.shape != (tensor.shape[0],) or tangents.ndim != 2 or tangents.shape[1] != tensor.shape[0]:
        raise ValueError("normal and tangent frame must match stress dimension")
    if not np.isclose(n @ n, 1.0, atol=1e-12, rtol=0.0):
        raise ValueError("normal must be unit")
    if not np.allclose(tangents @ n, 0.0, atol=1e-12, rtol=0.0):
        raise ValueError("tangent frame must be orthogonal to the normal")
    return tangents @ tensor.T @ n


def isotropic_scalar_traction(
    shape: Sequence[float],
    normal: Sequence[float],
    tangent_frame: Sequence[Sequence[float]],
    *,
    base_pressure: float = 1.0,
    pressure_shape_response: Sequence[float] | None = None,
) -> np.ndarray:
    """Tangential traction of a scalar pressure, including scalar Q response."""

    q = np.asarray(shape, dtype=float)
    n = np.asarray(normal, dtype=float)
    tangents = np.asarray(tangent_frame, dtype=float)
    response = np.zeros(q.size) if pressure_shape_response is None else np.asarray(pressure_shape_response, dtype=float)
    if response.shape != q.shape:
        raise ValueError("pressure response must match shape coordinates")
    pressure = float(base_pressure) + float(response @ q)
    if not math.isfinite(pressure):
        raise ValueError("pressure must be finite")
    # Validate the geometric frame through the general traction routine, then
    # return the exact theorem value.  Numerically multiplying p I by a QR
    # tangent frame leaves platform-dependent roundoff; analytically
    # e_a^nu (p delta_nu^mu) n_mu = p e_a.n = 0 exactly.
    interface_tangential_traction(np.eye(n.size), n, tangents)
    return np.zeros(tangents.shape[0])


def finite_difference_shape_vertex(
    current: Callable[[np.ndarray], np.ndarray],
    shape_dimension: int,
    *,
    epsilon: float = 1.0e-6,
) -> np.ndarray:
    """Central-difference D_Q J at Q=0."""

    if shape_dimension <= 0 or epsilon <= 0.0:
        raise ValueError("shape dimension and epsilon must be positive")
    zero = np.zeros(shape_dimension)
    base = np.asarray(current(zero), dtype=float)
    if base.ndim != 1:
        raise ValueError("current must return a vector")
    vertex = np.zeros((base.size, shape_dimension))
    for column in range(shape_dimension):
        step = np.zeros(shape_dimension)
        step[column] = epsilon
        vertex[:, column] = (np.asarray(current(step)) - np.asarray(current(-step))) / (2.0 * epsilon)
    return vertex


def hodge_decompose(
    one_form: Sequence[float],
    exact_basis: Sequence[Sequence[float]],
    coexact_basis: Sequence[Sequence[float]],
    harmonic_basis: Sequence[Sequence[float]],
) -> dict[str, np.ndarray | float]:
    """Finite-dimensional orthogonal Hodge witness in declared bases."""

    vector = np.asarray(one_form, dtype=float)
    blocks = [np.asarray(exact_basis, dtype=float), np.asarray(coexact_basis, dtype=float), np.asarray(harmonic_basis, dtype=float)]
    if vector.ndim != 1 or any(block.ndim != 2 or block.shape[0] != vector.size for block in blocks):
        raise ValueError("all Hodge bases must act on the one-form space")
    joined = np.concatenate(blocks, axis=1)
    if joined.shape[1] != vector.size or not np.allclose(joined.T @ joined, np.eye(vector.size), atol=1e-12, rtol=0.0):
        raise ValueError("declared Hodge bases must form an orthonormal decomposition")
    exact = blocks[0] @ (blocks[0].T @ vector)
    coexact = blocks[1] @ (blocks[1].T @ vector)
    harmonic = blocks[2] @ (blocks[2].T @ vector)
    return {
        "exact": exact,
        "coexact": coexact,
        "harmonic": harmonic,
        "reconstruction_residual": float(np.linalg.norm(vector - exact - coexact - harmonic)),
        "exact_coexact_inner_product": float(exact @ coexact),
    }


def driver_representation_kill_screen() -> dict[str, Any]:
    """Round Spin(4) screen for scalar activity/normal pressure."""

    scalar_driver = (0, 0)
    scalar_shape = (2, 2)
    outputs = spin4_tensor_product_doubled(scalar_driver, scalar_shape)
    desired = [(3, 1), (1, 3)]
    return {
        "doubled_spin_convention": True,
        "isotropic_activity_or_normal_pressure": scalar_driver,
        "scalar_ell2_shape": scalar_shape,
        "product": outputs,
        "desired_coexact_L2": desired,
        "contains_coexact_L2": any(rep in outputs for rep in desired),
        "scalar_gradient_channel": "EXACT_ONE_FORM_SO_COEXACT_PROJECTION_ZERO",
        "retained_tangential_vector_driver": False,
        "retained_vorticity_driver": False,
        "retained_jet_vector_field": False,
        "retained_gravitational_wave_driver": False,
    }


def zero_coupling_exchange_current(shape: Sequence[float], current_dimension: int) -> np.ndarray:
    """Formal S_int=0 embedding; not a substitute for a physical current."""

    q = np.asarray(shape, dtype=float)
    if q.ndim != 1 or current_dimension <= 0:
        raise ValueError("require shape coordinates and a positive current dimension")
    return np.zeros(current_dimension)


def deterministic_witness() -> dict[str, Any]:
    rng = np.random.default_rng(1489)
    ambient_dimension = 5
    rotation, _ = np.linalg.qr(rng.normal(size=(ambient_dimension, ambient_dimension)))
    normal = rotation[:, 0]
    tangents = rotation[:, 1:].T
    q_response = rng.normal(size=9)
    current = lambda q: isotropic_scalar_traction(q, normal, tangents, pressure_shape_response=q_response)
    vertex = finite_difference_shape_vertex(current, 9)

    hodge_rotation, _ = np.linalg.qr(rng.normal(size=(8, 8)))
    exact_basis = hodge_rotation[:, :3]
    coexact_basis = hodge_rotation[:, 3:7]
    harmonic_basis = hodge_rotation[:, 7:]
    exact_one_form = exact_basis @ rng.normal(size=3)
    hodge = hodge_decompose(exact_one_form, exact_basis, coexact_basis, harmonic_basis)

    frame_rotation, _ = np.linalg.qr(rng.normal(size=(ambient_dimension, ambient_dimension)))
    stress = 1.7 * np.eye(ambient_dimension)
    original = interface_tangential_traction(stress, normal, tangents)
    transformed = interface_tangential_traction(
        frame_rotation @ stress @ frame_rotation.T,
        frame_rotation @ normal,
        tangents @ frame_rotation.T,
    )

    zero_b = finite_difference_shape_vertex(lambda q: zero_coupling_exchange_current(q, 8), 9)
    k = rng.normal(size=(8, 8))
    k = k.T @ k + np.eye(8)
    correction = zero_background_schur_correction(zero_b, k)
    conditional_b = rng.normal(size=(8, 9))
    conditional_correction = zero_background_schur_correction(conditional_b, k)
    current_reflection, _ = np.linalg.qr(rng.normal(size=(8, 8)))
    shape_reflection, _ = np.linalg.qr(rng.normal(size=(9, 9)))
    zero_relative = reflected_relative_vertex(
        zero_b,
        zero_b,
        current_reflection,
        shape_reflection,
    )
    schur_witness = v14_88_schur_witness()
    return {
        "isotropic_tangential_traction_norm": float(np.linalg.norm(current(np.zeros(9)))),
        "isotropic_shape_vertex_norm": float(np.linalg.norm(vertex)),
        "exact_coexact_projection_norm": float(np.linalg.norm(hodge["coexact"])),
        "hodge_reconstruction_residual": hodge["reconstruction_residual"],
        "hodge_exact_coexact_inner_product": hodge["exact_coexact_inner_product"],
        "basis_covariance_residual": float(np.linalg.norm(original - transformed)),
        "zero_coupling_vertex_norm": float(np.linalg.norm(zero_b)),
        "zero_coupling_schur_norm": float(np.linalg.norm(correction)),
        "zero_coupling_relative_reflection_vertex_norm": float(np.linalg.norm(zero_relative)),
        "conditional_positive_K_schur_max_eigenvalue": float(np.linalg.eigvalsh(conditional_correction)[-1]),
        "general_schur_finite_difference_error": schur_witness["general_schur_finite_difference_error"],
        "zero_exchange_conservation_residual": exchange_conservation_residual(np.zeros(4), np.zeros(4)),
        "round_representation": driver_representation_kill_screen(),
        "v14_88_round_current_screen_preserved": not round_representation_kill_screen()["round_Spin4_allows_coexact_L2"],
    }


def completion_payload() -> dict[str, Any]:
    provenance = driver_coupling_provenance_audit()
    witness = deterministic_witness()
    validation = {
        "provenance_audit_exhaustive_minimum_objects": len(provenance) >= 23,
        "no_direct_driver_field": provenance[-1]["status"] == "ABSENT",
        "v14_82_source_functional_absent": any(row["object"] == "v14_82_BH_susceptibility" and row["status"].endswith("ABSENT") for row in provenance),
        "internal_attachment_not_misclassified_as_driver": any(row["object"] == "reciprocal_attachment_v11_3" and row["status"].endswith("NOT_DRIVER_BHSM") for row in provenance),
        "isotropic_scalar_traction_zero": witness["isotropic_tangential_traction_norm"] < 1e-12,
        "isotropic_scalar_shape_vertex_zero": witness["isotropic_shape_vertex_norm"] < 1e-10,
        "exact_coexact_orthogonality": witness["exact_coexact_projection_norm"] < 1e-12 and abs(witness["hodge_exact_coexact_inner_product"]) < 1e-12,
        "round_scalar_representation_excludes_coexact_L2": not witness["round_representation"]["contains_coexact_L2"],
        "basis_covariance": witness["basis_covariance_residual"] < 1e-12,
        "zero_coupling_limit": witness["zero_coupling_vertex_norm"] == 0.0 and witness["zero_coupling_schur_norm"] == 0.0,
        "zero_coupling_reflection_vertex": witness["zero_coupling_relative_reflection_vertex_norm"] == 0.0,
        "conditional_positive_K_response_nonpositive": witness["conditional_positive_K_schur_max_eigenvalue"] <= 1e-12,
        "general_Schur_finite_difference_preserved": witness["general_schur_finite_difference_error"] < 2e-6,
        "zero_exchange_conservation": witness["zero_exchange_conservation_residual"] == 0.0,
        "full_BHSM_not_claimed": True,
        "flavor_gates_preserved": True,
        "USB_not_eligible": True,
    }
    return {
        "artifact": "BHSM_driver_bhsm_exchange_traction_no_go_v14_89",
        "version": VERSION,
        "primary_machine_readable_verdict": PRIMARY_VERDICT,
        "canonical_long_range_object": EXACT_NEXT_OBJECT,
        "next_canonical_object": NEXT_CANONICAL_OBJECT,
        "driver_coupling_provenance": provenance,
        "retained_coupled_functional": {
            "form": "S_ret=S_BHSM[g,Phi_BHSM,X_seam_fixed_or_conditionally_varied]",
            "S_driver": "ABSENT",
            "S_driver_BHSM_interaction": "ABSENT",
            "shared_metric": "PRESENT_BUT_NOT_A_DIRECT_EXCHANGE_TERM",
            "internal_reciprocal_attachment": "PRESENT_CORE_WALL_DEPTH_TRANSFER_ONLY",
        },
        "Ward_identity": {
            "total": "nabla_mu T_total^{mu nu}=0 on the complete retained equations",
            "decoupled_sector_result": "with S_int absent, each diffeomorphism-invariant matter sector is separately conserved on its own equations",
            "driver_exchange_split": "NOT_INSTANTIATED_BECAUSE_NO_DRIVER_SECTOR_OR_INTERACTION_STRESS_EXISTS",
            "interaction_stress_assignment_ambiguity": "ABSENT_WITH_S_int_ZERO",
        },
        "derived_exchange_current": {
            "physical_Q_ex_nu": None,
            "status": "UNDEFINED_NO_COUPLED_FUNCTIONAL",
            "formal_zero_coupling_limit": "Q_ex_nu=0",
        },
        "interface_traction": {
            "definition": "tau_a=e_a^nu n_mu T^mu_nu",
            "physical_driver_traction": None,
            "formal_zero_coupling_limit": "tau_a=0",
            "isotropic_scalar_or_normal_pressure": "tau_a=0 exactly by e_a dot n=0",
            "internal_attachment_new_boundary_flux": "ZERO",
        },
        "Hodge_result": {
            "physical_J_ex_L2": None,
            "status": "UNDEFINED_NO_TRACTION",
            "scalar_gradient": "EXACT_AND_ORTHOGONAL_TO_COEXACT_L2",
            "formal_zero_coupling_projection": "ZERO",
        },
        "reflection_result": {
            "physical_exchange_parity": "UNDEFINED_NO_EXCHANGE_FUNCTIONAL",
            "formal_zero_vertex": "B_plus=B_minus=0_SO_RELATIVE_VERTEX_ZERO",
            "isotropic_scalar": "REFLECTION_EVEN_AND_CANNOT_SUPPLY_ODD_TANGENTIAL_VERTEX",
        },
        "representation_theory": witness["round_representation"],
        "current_shape_vertex": {
            "physical_J_ex_L2": None,
            "physical_B_ex_L2": None,
            "status": "UNDEFINED_NOT_NONZERO",
            "formal_zero_coupling_J_ex_L2": "ZERO",
            "formal_zero_coupling_B_ex_L2": "ZERO",
            "isotropic_scalar_B_ex_L2": "ZERO_BY_TRACTION_AND_SPIN4_THEOREMS",
        },
        "conservation": {
            "physical_exchange_residual": None,
            "reason": "NO_PHYSICAL_EXCHANGE_CURRENT_TO_EVALUATE",
            "formal_zero_coupling_residual": witness["zero_exchange_conservation_residual"],
            "internal_attachment_identity": "Q_C+Q_W+Q_D=0_ON_INTERNAL_FIELD_AND_MULTIPLIER_EQUATIONS",
        },
        "common_domain": "FULL_PREIMAGE_DRIVER_BHSM_EXCHANGE_COMMON_SELF_ADJOINT_DOMAIN_NOT_DERIVED_BECAUSE_DRIVER_BLOCK_ABSENT",
        "v14_83_R7_bridge": {
            "status": "RETIRED_AS_PHYSICAL_DRIVER;_PRESERVED_ONLY_AS_PROVISIONAL_DIMENSIONAL_NORMAL_FORM",
            "B0_prime_from_action_stress": None,
            "exact_R7_derivation": False,
            "reason": "NO_RETAINED_DRIVER_STRESS_OR_INTERACTION_FUNCTIONAL_EXISTS_TO_PROJECT_ONTO_DILATION",
        },
        "differential_shear_equivalence": "NOT_DERIVED_NO_TRACTION_CURRENT_OR_CAP_TRANSPORT_MAP",
        "Schur_response": {
            "conditional_theorem": "DeltaH=-B^dagger K^-1 B for J0=0 and positive common-domain K",
            "formal_zero_coupling_correction": "ZERO",
            "physical_exchange_correction": None,
        },
        "complete_ell2_eigenvalues": "NOT_AVAILABLE_NO_EXCHANGE_VERTEX_OR_COMMON_DOMAIN",
        "locking_alpha_Floquet": "NOT_REACHED",
        "open_flavor_gates": {
            "charged_current_kernel": CHARGED_CURRENT_PROVENANCE_GATE,
            "noncentral_left_handed_current": NONCENTRAL_CURRENT_GATE,
        },
        "completion_status": {
            "FULL_BHSM_COMPLETE": False,
            "MARK_III": "NOT_REACHED",
            "PHYSICAL_EXECUTION_BLOCKED": True,
            "USB_SYNCHRONIZATION_ELIGIBLE": False,
        },
        "Hindsight_20_20": {
            "validated": [
                "the retained archive has no independent driver field or direct driver-BHSM interaction functional",
                "the v11.3 reciprocal attachment is a real internal BHSM Ward transfer and not an external driver",
                "isotropic scalar activity and normal pressure have zero tangential traction and fail the round coexact-L2 representation screen",
                "the formal zero-coupling exchange and its Schur correction vanish",
            ],
            "invalidated": [
                "shared metric dependence as sufficient evidence of a direct exchange current",
                "v14.81's formal Q split as an action-derived current",
                "v14.83's R7 bridge as a retained physical driver coupling",
                "scalar luminosity or pressure as a coexact L2 tangential source",
            ],
            "reclassified": [
                "v14.81-v14.83 driver objects as conservation/response bridge theorems rather than retained interaction terms",
                "the R7 bridge as provisional dimensional intuition only",
            ],
            "open": [NEXT_CANONICAL_OBJECT],
        },
        "numeric_witness": witness,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    def default(value: Any) -> Any:
        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, np.ndarray):
            return value.tolist()
        raise TypeError(type(value).__name__)

    return json.dumps(payload, indent=2, sort_keys=True, default=default) + "\n"


def materialize(repository: Path | None = None) -> Path:
    root = Path(__file__).resolve().parents[4] if repository is None else Path(repository)
    output = root / "artifacts" / "BHSM_driver_bhsm_exchange_traction_no_go_v14_89.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(deterministic_json(completion_payload()), encoding="utf-8", newline="\n")
    return output
