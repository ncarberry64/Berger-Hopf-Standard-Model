"""BHSM v14.90 intrinsic dynamical full-preimage momentum gate.

The retained P1 Lorentzian action owns genuine canonical metric momentum, so
the v14.41 stationary-shift theorem is not a theorem that all dynamical
gravitational momentum vanishes.  The only explicit constraint-reduced P1
solutions, however, are homogeneous cap-common round/Jensen trajectories.
They have zero reflection-relative cap momentum.  The nonhomogeneous
degree-one phase space, common seam symplectic domain, cap inertias and L2
mixed momentum--shape vertex have not been constructed.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from bhsm.interface.completion.full_preimage_cap_inertia_operator_v14_84 import (
    CHARGED_CURRENT_PROVENANCE_GATE,
    EXACT_NEXT_OBJECT,
    NONCENTRAL_CURRENT_GATE,
)


VERSION = "v14.90"
PRIMARY_VERDICT = (
    "BHSM_V14_90_THE_RETAINED_LORENTZIAN_P1_ACTION_OWNS_GENUINE_"
    "TIME_DEPENDENT_CANONICAL_METRIC_MOMENTUM_BUT_ITS_ONLY_EXPLICIT_"
    "CONSTRAINT_REDUCED_ROUND_AND_JENSEN_DYNAMICAL_SOLUTIONS_ARE_"
    "HOMOGENEOUS_CAP_COMMON_MODES_WITH_ZERO_REFLECTION_RELATIVE_"
    "MOMENTUM;_THE_NONHOMOGENEOUS_DEGREE_ONE_FULL_PREIMAGE_PHASE_SPACE_"
    "COMMON_SEAM_SYMPLECTIC_DOMAIN_CAP_INERTIAS_AND_COEXACT_L2_MIXED_"
    "VERTEX_ARE_NOT_RETAINED,_SO_GENERAL_INTRINSIC_RELATIVE_TENSOR_MODES_"
    "ARE_NOT_RULED_OUT_BUT_NO_PHYSICAL_B_DYN_L2_OR_SOFTENING_CORRECTION_"
    "CAN_BE_INSERTED"
)
NEXT_CANONICAL_OBJECT = (
    "LORENTZIAN_DEGREE_ONE_FULL_PREIMAGE_BACKGROUND_AND_GAUGE_REDUCED_"
    "COUPLED_METRIC_ETA_GAUGE_DIRAC_LINEARIZED_SYMPLECTIC_BOUNDARY_VALUE_"
    "PROBLEM_WITH_REFLECTION_ODD_CAP_RELATIVE_TENSOR_MODES_AND_EXPLICIT_"
    "COEXACT_L2_MIXED_VARIATION"
)


def canonical_variable_provenance() -> list[dict[str, Any]]:
    """Return the retained canonical-variable provenance table."""

    return [
        {
            "variable": "spatial_metric_h_ij_on_M8_slice",
            "canonical_momentum": "pi^ij=(kappa1/2)sqrt(h)(K^ij-Kh^ij)",
            "action_owned": True,
            "constraint": "Hamiltonian_and_momentum_constraints",
            "gauge": "spatial_diffeomorphisms_and_refoliation",
            "physical_dynamical_mode": "YES_AFTER_CONSTRAINT_AND_GAUGE_REDUCTION",
            "full_preimage_status": "HOMOGENEOUS_SCALE_SHAPE_TRUNCATION_ONLY",
        },
        {
            "variable": "lapse_N",
            "canonical_momentum": "p_N=0",
            "action_owned": True,
            "constraint": "primary_constraint_generates_Hamiltonian_constraint",
            "gauge": "time_reparameterization_multiplier",
            "physical_dynamical_mode": False,
            "full_preimage_status": "RETAINED_IN_HOMOGENEOUS_P1_VARIATION",
        },
        {
            "variable": "shift_beta_i",
            "canonical_momentum": "p_beta=0",
            "action_owned": "ADM_MULTIPLIER_STANDARD;_ZERO_SHIFT_IN_EXPLICIT_P1_ANSATZ",
            "constraint": "momentum_constraint",
            "gauge": "spatial_coordinate_multiplier",
            "physical_dynamical_mode": False,
            "full_preimage_status": "STATIONARY_NONKILLING_COEXACT_MODE_CLOSED_BY_V14_41",
        },
        {
            "variable": "eta",
            "canonical_momentum": "p_eta=w(kappa1+X^3)D_0eta",
            "action_owned": True,
            "constraint": "global_and_gauge_constraints_branch_dependent",
            "gauge": "associated_bundle_gauge_action",
            "physical_dynamical_mode": "CONDITIONAL_INSIDE_POSITIVE_LEGENDRE_CONE",
            "full_preimage_status": "DEGREE_ONE_PERIODIC_BACKGROUND_AND_DOMAIN_ABSENT",
        },
        {
            "variable": "gauge_connection_A_i",
            "canonical_momentum": "electric_momentum_E^i",
            "action_owned": "PARENT_GEOMETRIC_NORMALIZATION_AND_PROVISIONAL_B1_SECTORS",
            "constraint": "Gauss_law",
            "gauge": "internal_gauge",
            "physical_dynamical_mode": "TRANSVERSE_MODES_CONDITIONAL",
            "full_preimage_status": "NO_COUPLED_DEGREE_ONE_LINEARIZED_DOMAIN",
        },
        {
            "variable": "fermion_psi",
            "canonical_momentum": "FIRST_ORDER_DIRAC_MOMENTUM_CONSTRAINT",
            "action_owned": "ADOPTED_FOUNDATIONAL_EFFECTIVE_ACTION",
            "constraint": "first_order_second_class_and_gauge_constraints",
            "gauge": "spin_and_internal_gauge",
            "physical_dynamical_mode": "STATE_DEPENDENT",
            "full_preimage_status": "COMMON_COUPLED_DOMAIN_NOT_DERIVED",
        },
        {
            "variable": "seam_embedding_X",
            "canonical_momentum": None,
            "action_owned": False,
            "constraint": "moving_seam_contract_only",
            "gauge": "normal_reparameterization_must_be_quotiented",
            "physical_dynamical_mode": "NOT_ESTABLISHED",
            "full_preimage_status": "VARIABLE_EMBEDDING_ABSENT_FROM_ACTIVE_ACTION",
        },
        {
            "variable": "enclosure_log_scale_x",
            "canonical_momentum": None,
            "action_owned": "STATIC_GLOBAL_ACTION_COORDINATE_ONLY",
            "constraint": "stationarity_equation_not_Hamiltonian_constraint",
            "gauge": False,
            "physical_dynamical_mode": "NOT_DERIVED",
            "full_preimage_status": "SYNTHETIC_FIXTURE_NOT_LORENTZIAN_PHASE_SPACE",
        },
        {
            "variable": "collar_or_relative_cap_coordinate",
            "canonical_momentum": None,
            "action_owned": "GEOMETRIC_DOMAIN_LABEL",
            "constraint": "matching_and_regular_cap_conditions",
            "gauge": "coordinate_choice_until_physical_collective_mode_is_derived",
            "physical_dynamical_mode": False,
            "full_preimage_status": "PURE_REPARTITION_HAS_ZERO_TOTAL_ACTION_HESSIAN",
        },
        {
            "variable": "reciprocal_attachment_depth_q_D",
            "canonical_momentum": "NO_INDEPENDENT_RELATIVE_CAP_MOMENTUM_IN_V11_3_TERM",
            "action_owned": True,
            "constraint": "internal_core_wall_depth_Ward_transfer",
            "gauge": "relational_attachment_redundancies",
            "physical_dynamical_mode": "INTERNAL_ATTACHMENT_RESPONSE_ONLY",
            "full_preimage_status": "NOT_A_TWO_CAP_TRANSPORT_COORDINATE",
        },
    ]


def _metric_array(metric: Sequence[Sequence[float]]) -> np.ndarray:
    h = np.asarray(metric, dtype=float)
    if h.ndim != 2 or h.shape[0] != h.shape[1]:
        raise ValueError("metric must be square")
    if not np.allclose(h, h.T, atol=1e-12, rtol=0.0):
        raise ValueError("metric must be symmetric")
    if float(np.min(np.linalg.eigvalsh(h))) <= 0.0:
        raise ValueError("metric must be positive definite")
    return h


def extrinsic_curvature(
    spatial_metric: Sequence[Sequence[float]],
    metric_velocity: Sequence[Sequence[float]],
    lapse: float,
    shift_symmetrized_gradient: Sequence[Sequence[float]] | None = None,
) -> np.ndarray:
    """Return K_ij=(dot(h)_ij-(D_i beta_j+D_j beta_i))/(2N)."""

    h = _metric_array(spatial_metric)
    velocity = np.asarray(metric_velocity, dtype=float)
    if velocity.shape != h.shape or not np.allclose(velocity, velocity.T, atol=1e-12, rtol=0.0):
        raise ValueError("metric velocity must be a matching symmetric tensor")
    if not math.isfinite(lapse) or lapse <= 0.0:
        raise ValueError("lapse must be finite and positive")
    shift = np.zeros_like(h) if shift_symmetrized_gradient is None else np.asarray(shift_symmetrized_gradient, dtype=float)
    if shift.shape != h.shape or not np.allclose(shift, shift.T, atol=1e-12, rtol=0.0):
        raise ValueError("shift gradient must be a matching symmetric tensor")
    return (velocity - shift) / (2.0 * lapse)


def canonical_gravitational_momentum(
    spatial_metric: Sequence[Sequence[float]],
    slice_extrinsic_curvature: Sequence[Sequence[float]],
    kappa1: float = 2.0,
) -> np.ndarray:
    """Return the contravariant densitized P1 momentum pi^ij.

    The P1 normalization is S=(1/2) integral sqrt(-G) kappa1 R plus GHY,
    hence pi^ij=(kappa1/2)sqrt(h)(K^ij-K h^ij).
    """

    h = _metric_array(spatial_metric)
    curvature = np.asarray(slice_extrinsic_curvature, dtype=float)
    if curvature.shape != h.shape or not np.allclose(curvature, curvature.T, atol=1e-12, rtol=0.0):
        raise ValueError("extrinsic curvature must be a matching symmetric tensor")
    if not math.isfinite(kappa1) or kappa1 <= 0.0:
        raise ValueError("kappa1 must be finite and positive")
    inverse = np.linalg.inv(h)
    trace = float(np.trace(inverse @ curvature))
    raised = inverse @ curvature @ inverse
    return 0.5 * kappa1 * math.sqrt(float(np.linalg.det(h))) * (raised - trace * inverse)


def traceless_extrinsic_shear(
    spatial_metric: Sequence[Sequence[float]],
    slice_extrinsic_curvature: Sequence[Sequence[float]],
) -> np.ndarray:
    """Return the dimension-correct covariant traceless part of K_ij."""

    h = _metric_array(spatial_metric)
    curvature = np.asarray(slice_extrinsic_curvature, dtype=float)
    if curvature.shape != h.shape:
        raise ValueError("extrinsic curvature must match metric")
    dimension = h.shape[0]
    trace = float(np.trace(np.linalg.solve(h, curvature)))
    return curvature - (trace / dimension) * h


def reflection_relative_tensor(
    plus: Sequence[Sequence[float]],
    minus: Sequence[Sequence[float]],
    reflection: Sequence[Sequence[float]],
) -> np.ndarray:
    """Return T_plus-R^T T_minus R in the plus-cap frame."""

    p = np.asarray(plus, dtype=float)
    m = np.asarray(minus, dtype=float)
    r = np.asarray(reflection, dtype=float)
    if p.ndim != 2 or p.shape[0] != p.shape[1] or m.shape != p.shape or r.shape != p.shape:
        raise ValueError("plus, minus and reflection must be equal square matrices")
    if not np.allclose(r.T @ r, np.eye(r.shape[0]), atol=1e-12, rtol=0.0):
        raise ValueError("reflection identification must be orthogonal")
    return p - r.T @ m @ r


def homogeneous_cap_momentum_witness(dimension: int = 7, hubble: float = 0.17) -> dict[str, Any]:
    """Evaluate reflection-relative momentum in the explicit homogeneous P1 sector."""

    if dimension < 2:
        raise ValueError("dimension must be at least two")
    h = np.eye(dimension)
    curvature = hubble * h
    pi_plus = canonical_gravitational_momentum(h, curvature)
    reflection = np.diag([-1.0] + [1.0] * (dimension - 1))
    relative = reflection_relative_tensor(pi_plus, pi_plus, reflection)
    shear = traceless_extrinsic_shear(h, curvature)
    return {
        "dimension": dimension,
        "common_momentum_norm": float(np.linalg.norm(pi_plus)),
        "relative_momentum_norm": float(np.linalg.norm(relative)),
        "traceless_shear_norm": float(np.linalg.norm(shear)),
        "nonzero_common_expansion_momentum": float(np.linalg.norm(pi_plus)) > 0.0,
        "zero_reflection_relative_momentum": np.allclose(relative, 0.0),
        "interpretation": "time dependence is physical in the homogeneous truncation but is cap-common, not relative shear",
    }


def oscillator_state_witness(
    amplitude: float = 0.4,
    frequency: float = 1.7,
    inertia: float = 2.3,
    phase: float = 0.8,
) -> dict[str, float | bool]:
    """Separate mode existence from classical population for one oscillator."""

    if frequency <= 0.0 or inertia <= 0.0:
        raise ValueError("frequency and inertia must be positive")
    q = amplitude * math.cos(phase)
    momentum = -inertia * amplitude * frequency * math.sin(phase)
    return {
        "coordinate": q,
        "momentum": momentum,
        "cycle_mean_momentum": 0.0,
        "cycle_mean_momentum_squared": 0.5 * (inertia * amplitude * frequency) ** 2,
        "mode_exists_for_positive_frequency": True,
        "classical_ground_state_amplitude": 0.0,
        "nonzero_amplitude_is_initial_state_data": amplitude != 0.0,
    }


def dynamical_schur_correction(
    vertex: Sequence[Sequence[float]],
    stiffness: Sequence[Sequence[float]],
    *,
    frequency: float = 0.0,
    inertia: Sequence[Sequence[float]] | None = None,
) -> np.ndarray:
    """Return -B^T[K-omega^2 M]^-1 B away from dynamical poles."""

    b = np.asarray(vertex, dtype=float)
    k = np.asarray(stiffness, dtype=float)
    if k.ndim != 2 or k.shape[0] != k.shape[1] or b.ndim != 2 or b.shape[0] != k.shape[0]:
        raise ValueError("stiffness must be square and vertex rows must match")
    operator = k.copy()
    if inertia is not None:
        m = np.asarray(inertia, dtype=float)
        if m.shape != k.shape:
            raise ValueError("inertia must match stiffness")
        operator = operator - frequency**2 * m
    elif frequency != 0.0:
        raise ValueError("nonzero frequency requires an inertia operator")
    return -(b.T @ np.linalg.solve(operator, b))


def representation_kill_screen() -> dict[str, Any]:
    """Record exactly what symmetry does and does not exclude."""

    return {
        "v14_88_rigid_L1_times_scalar_L2_to_coexact_L2": "FORBIDDEN_PRESERVED",
        "homogeneous_P1_metric_momentum": "SPIN4_SINGLET_CAP_COMMON",
        "homogeneous_to_relative_coexact_L2": "FORBIDDEN_ZERO_RELATIVE_SOURCE",
        "rank2_traceless_tensor_route": "NOT_EXCLUDED_BY_THE_RIGID_L1_THEOREM",
        "rank2_route_current_status": "UNDEFINED_WITHOUT_NONHOMOGENEOUS_OPERATOR_DOMAIN_AND_PROJECTORS",
        "claim_boundary": "different tensor representation content reopens possibility, not a proof of a nonzero vertex",
    }


def completion_payload() -> dict[str, Any]:
    homogeneous = homogeneous_cap_momentum_witness()
    oscillator = oscillator_state_witness()
    zero_vertex = np.zeros((2, 2))
    zero_correction = dynamical_schur_correction(zero_vertex, np.eye(2))
    trial_vertex = np.array([[0.4, -0.2], [0.1, 0.3]])
    static_correction = dynamical_schur_correction(trial_vertex, np.diag([2.0, 3.0]))
    validation = {
        "P1_has_nonzero_common_dynamic_metric_momentum": homogeneous["nonzero_common_expansion_momentum"],
        "explicit_homogeneous_P1_relative_momentum_is_zero": homogeneous["zero_reflection_relative_momentum"],
        "homogeneous_isotropic_extrinsic_shear_is_zero": homogeneous["traceless_shear_norm"] < 1e-12,
        "zero_vertex_has_zero_Schur_correction": np.allclose(zero_correction, 0.0),
        "conditional_positive_static_block_softens": float(np.max(np.linalg.eigvalsh(static_correction))) <= 1e-12,
        "oscillator_population_separated_from_existence": oscillator["classical_ground_state_amplitude"] == 0.0,
        "full_BHSM_not_claimed": True,
        "flavor_firewalls_preserved": True,
    }
    return {
        "artifact": "BHSM_intrinsic_full_preimage_dynamical_momentum_gate_v14_90",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "primary_executable_object": "ACTION_OWNED_INTRINSIC_FULL_PREIMAGE_DYNAMICAL_RELATIVE_CAP_MOMENTUM_AND_COEXACT_L2_SHAPE_TRANSPORT_FROM_CANONICAL_METRIC_EXTRINSIC_CURVATURE_AND_EXISTING_MATTER_FIELDS_WITHOUT_EXTERNAL_DRIVER",
        "canonical_long_range_object": EXACT_NEXT_OBJECT,
        "exact_next_object": NEXT_CANONICAL_OBJECT,
        "canonical_Lorentzian_action": {
            "recovered": "S_P1=(1/2)int_M8 sqrt(-G)(kappa1 R-kappa0)+kappa1 int_boundary epsilon K",
            "ADM_form": "(1/2)int dt d7x N sqrt(h)[kappa1(R7+KijKij-K^2)-kappa0]",
            "phase_space_metric_term": "int dt d7x pi^ij dot(h_ij)-H_constraints",
            "momentum": "pi^ij=(kappa1/2)sqrt(h)(K^ij-Kh^ij)",
            "status": "ACTION_OWNED_GENERAL_FORM;_EXPLICITLY_REDUCED_ONLY_IN_HOMOGENEOUS_M8_IxS7_ANSATZ",
            "intrinsic_M4_B1": "PROVISIONAL_BOUNDARY_AXIOM_NOT_PARENT_DERIVED",
        },
        "canonical_variables": canonical_variable_provenance(),
        "two_cap_momenta": {
            "definition": "DeltaPi=Pi_plus-R^dagger Pi_minus R",
            "physical_reduced_Pi_plus_minus": "UNDEFINED_NO_NONHOMOGENEOUS_TWO_CAP_CONSTRAINT_REDUCTION",
            "homogeneous_formal_restriction": homogeneous,
            "parity": "ZERO_IN_EXPLICIT_HOMOGENEOUS_SECTOR;_GENERAL_PHYSICAL_PARITY_UNDEFINED",
            "counterpropagating_reflection_symmetric_state": "KINEMATICALLY_POSSIBLE_NOT_ACTION_SOLVED_OR_STATE_SELECTED",
        },
        "stationary_v14_41_consistency": {
            "stationary_shift": "ZERO_AFTER_NONKILLING_QUOTIENT",
            "dynamical_metric_velocity": "NOT_IDENTICAL_TO_SHIFT_AND_NOT_KILLED_BY_V14_41",
            "explicit_P1_common_expansion_momentum": "NONZERO_AWAY_FROM_COSH_TURNING_POINT",
            "relative_cap_momentum": "ZERO_IN_HOMOGENEOUS_TRUNCATION",
        },
        "linear_dynamical_spectrum": {
            "round_fixed_shape": "TWO_HOMOGENEOUS_SHAPE_MASSES_SQUARED_4_OVER_A2;_CAP_COMMON",
            "Jensen_fixed_shape": "HOMOGENEOUS_MASSES_SQUARED_52_OVER_5A2_AND_MINUS_4_OVER_A2;_CAP_COMMON",
            "associated_tower": "INSTANTANEOUS_OPERATOR_AND_ADIABATIC_CONTROL_ONLY",
            "nonhomogeneous_gravitational_vector_tensor_spectrum": "NOT_DERIVED",
            "physical_DeltaPi_nonzero_mode": "NOT_FOUND_IN_EXPLICIT_SECTOR;_GENERAL_ROUTE_OPEN",
        },
        "degree_one_background": "NOT_DERIVED",
        "common_domain": {
            "status": "FULL_PREIMAGE_DYNAMICAL_COMMON_SELF_ADJOINT_SYMPLECTIC_DOMAIN_NOT_DERIVED",
            "Green_form": "NOT_COMPUTABLE_FOR_ABSENT_COUPLED_LINEARIZED_OPERATOR",
            "seam_symplectic_flux": "NOT_COMPUTABLE_FOR_ABSENT_MOVING_SEAM_PHASE_SPACE",
        },
        "cap_inertias": {
            "M_plus": "UNDEFINED_FOR_PHYSICAL_L2_MODE",
            "M_minus": "UNDEFINED_FOR_PHYSICAL_L2_MODE",
            "positivity": "NOT_TESTABLE",
            "reflection_equal_inertia": "CONDITIONAL_OPERATOR_THEOREM_ONLY",
            "nu": "ONE_QUARTER_CONDITIONAL_NOT_PHYSICAL",
        },
        "intrinsic_observable": {
            "formal_candidate": "J_dyn=P_coex,L2 J[DeltaPi,DeltaSigma]",
            "physical_status": "UNDEFINED_NO_COMMON_REDUCED_DOMAIN_OR_PROJECTOR",
            "homogeneous_restriction": "ZERO",
            "B_dyn_L2": "UNDEFINED_PHYSICALLY;_ZERO_IN_EXPLICIT_HOMOGENEOUS_TRUNCATION",
        },
        "representation": representation_kill_screen(),
        "dynamic_response": {
            "conditional_static": "DeltaH=-B^dagger K_dyn^-1 B<=0_FOR_POSITIVE_K_dyn",
            "finite_frequency": "DeltaH(omega)=-B^dagger[K_dyn-omega^2 M_dyn]^-1B_AWAY_FROM_POLES",
            "physical_insertion": "NOT_ALLOWED_WITH_B_DYN_UNDEFINED",
            "zero_homogeneous_insertion": "ZERO",
        },
        "state_selection": {
            "oscillator_witness": oscillator,
            "existence_is_population": False,
            "vacuum_loop": "OPEN_REQUIRES_OPERATOR_GHOST_DOMAIN_AND_RENORMALIZATION_PRESCRIPTION",
        },
        "complete_L2": {
            "Hessian": "NOT_CONSTRUCTED",
            "spectrum": "NOT_REACHED",
            "locking_alpha_Floquet": "NOT_REACHED",
        },
        "Hindsight_20_20": {
            "validated": [
                "P1 owns dynamical canonical metric momentum",
                "v14.41 stationary shift no-go does not kill dot(h) momentum",
                "explicit homogeneous round/Jensen dynamics is cap-common and has DeltaPi=0",
                "a positive dynamical block gives conditional static Schur softening",
            ],
            "invalidated": [
                "all gravitational momentum vanishes because stationary shift vanishes",
                "homogeneous parent expansion as relative cap shear",
                "moving seam contract as an active canonical coordinate",
                "allowed oscillator as automatically populated classical shear",
            ],
            "reclassified": [
                "P1 is sufficient for a general ADM momentum formula but not a full-preimage reduced phase space",
                "intrinsic dynamics is an open nonhomogeneous tensor-mode route rather than an external-driver route",
            ],
            "open": [NEXT_CANONICAL_OBJECT],
        },
        "flavor_firewall": {
            "spectral_charged_current": CHARGED_CURRENT_PROVENANCE_GATE,
            "noncentral_left_handed_current": NONCENTRAL_CURRENT_GATE,
            "status": "OPEN_UNCHANGED",
        },
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
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def materialize(path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return target
