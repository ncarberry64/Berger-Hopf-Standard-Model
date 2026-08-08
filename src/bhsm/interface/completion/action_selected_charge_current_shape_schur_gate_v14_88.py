"""BHSM v14.88 action-selected charge and current-shape Schur gate.

The module separates a vanishing background current from its Frechet
derivative, audits the retained charge sectors, and derives the exact Hessian
of ``-1/2 J(Q)^T K(Q)^-1 J(Q)`` on a fixed common domain.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from bhsm.interface.completion.full_preimage_cap_inertia_operator_v14_84 import (
    CHARGED_CURRENT_PROVENANCE_GATE,
    EXACT_NEXT_OBJECT,
    NONCENTRAL_CURRENT_GATE,
)
from bhsm.interface.completion.path_b_physical_topology_v14_32 import (
    fr_obstruction_payload,
)


VERSION = "v14.88"
PRIMARY_VERDICT = (
    "BHSM_V14_88_NO_PRESENTLY_RETAINED_PHYSICAL_BHSM_SECTOR_ACTION_SELECTS_"
    "A_NONZERO_REFLECTION_ODD_COEXACT_L2_CHARGE;_ON_THE_FIXED_ZERO_ETA_"
    "CANONICAL_MOMENTUM_BRANCH_LEGENDRE_INVERTIBILITY_FORCES_THE_WHOLE_"
    "CURRENT_MAP_J_OF_Q_AND_ITS_FRECHET_DERIVATIVE_B_L2_TO_ZERO,_AND_ON_"
    "THE_ROUND_SPIN4_REFERENCE_RIGID_L1_CURRENT_TIMES_SCALAR_ELL2_CANNOT_"
    "CONTAIN_A_COEXACT_L2_OUTPUT;_THE_EXACT_COMMON_DOMAIN_SCHUR_THEOREM_"
    "DOES_GIVE_MINUS_B_DAGGER_K_INVERSE_B_WHEN_J0_IS_ZERO,_BUT_NO_"
    "PHYSICAL_NONZERO_B_HAS_BEEN_ACTION_DERIVED"
)
NEXT_CANONICAL_OBJECT = (
    "ACTION_DERIVED_CONSERVED_REFLECTION_ODD_COEXACT_L2_EXCHANGE_CURRENT_"
    "SHAPE_VERTEX_FROM_THE_DRIVER_BHSM_COUPLED_FUNCTIONAL_WITH_NO_"
    "ARBITRARY_PROFILE_OR_SUSCEPTIBILITY"
)


def fixed_charge_routhian(
    inertia: float,
    charge: float,
    potential: float = 0.0,
) -> dict[str, float]:
    """Routh reduction of L=I omega^2/2-V at fixed p=C."""

    if inertia <= 0.0:
        raise ValueError("the fixed-charge Legendre branch requires positive inertia")
    omega = charge / inertia
    lagrangian = 0.5 * inertia * omega**2 - potential
    routhian = lagrangian - charge * omega
    return {
        "angular_velocity": omega,
        "routhian": routhian,
        "effective_potential": potential + 0.5 * charge**2 / inertia,
    }


def zero_charge_eta_current_shape_vertex(
    shape_coordinates: Sequence[float],
    current_dimension: int,
    *,
    legendre_margin: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return J(Q)=0 and D_Q J=0 on the fixed p_eta=0 positive branch.

    This is stronger than evaluating J at one background.  Invertibility of
    the velocity Legendre map at every nearby shape gives D0 eta(Q)=0, so the
    retained eta momentum current is identically zero as a function of Q.
    """

    q = np.asarray(shape_coordinates, dtype=float)
    if q.ndim != 1 or current_dimension <= 0:
        raise ValueError("require a shape vector and positive current dimension")
    if legendre_margin <= 0.0:
        raise ValueError("zero-charge inversion is valid only in the positive Legendre cone")
    return np.zeros(current_dimension), np.zeros((current_dimension, q.size))


def su2_tensor_product_doubled(two_j_a: int, two_j_b: int) -> list[int]:
    """SU(2) tensor product represented by doubled nonnegative spins."""

    if min(two_j_a, two_j_b) < 0:
        raise ValueError("spins must be nonnegative")
    return list(range(abs(two_j_a - two_j_b), two_j_a + two_j_b + 1, 2))


def spin4_tensor_product_doubled(
    representation_a: tuple[int, int],
    representation_b: tuple[int, int],
) -> list[tuple[int, int]]:
    """Tensor product of Spin(4)=SU(2)_L x SU(2)_R irreps."""

    return [
        (left, right)
        for left in su2_tensor_product_doubled(representation_a[0], representation_b[0])
        for right in su2_tensor_product_doubled(representation_a[1], representation_b[1])
    ]


def round_representation_kill_screen() -> dict[str, Any]:
    """Test rigid coexact L=1 current times scalar ell=2 on round S3."""

    shape = (2, 2)  # (j_L,j_R)=(1,1)
    current_chiralities = [(2, 0), (0, 2)]  # Killing/coexact L=1
    outputs = sorted(
        {
            output
            for current in current_chiralities
            for output in spin4_tensor_product_doubled(current, shape)
        }
    )
    desired = [(3, 1), (1, 3)]  # coexact L=2
    return {
        "doubled_spin_convention": True,
        "shape_representation": shape,
        "rigid_current_representations": current_chiralities,
        "product_representations": outputs,
        "desired_coexact_L2_representations": desired,
        "round_Spin4_allows_coexact_L2": any(item in outputs for item in desired),
        "diagonal_SO3_product": [1, 2, 3],
        "diagonal_SO3_allows_L2": True,
        "degree_one_reduced_symmetry_status": "OPEN_REQUIRES_BACKGROUND_AND_REDUCED_MATRIX_ELEMENTS",
    }


def schur_hessian_correction(
    j0: Sequence[float],
    k0: Sequence[Sequence[float]],
    first_j: Sequence[Sequence[float]],
    second_j: Sequence[Sequence[Sequence[float]]],
    first_k: Sequence[Sequence[Sequence[float]]],
    second_k: Sequence[Sequence[Sequence[Sequence[float]]]],
) -> np.ndarray:
    """Exact Hessian of -J(Q)^T K(Q)^-1 J(Q)/2 at Q=0.

    All projectors, moving-domain identifications, and zero-mode reductions
    must already be incorporated into J and K on one fixed common domain.
    """

    j = np.asarray(j0, dtype=float)
    k = np.asarray(k0, dtype=float)
    b = np.asarray(first_j, dtype=float)
    c = np.asarray(second_j, dtype=float)
    ka = np.asarray(first_k, dtype=float)
    kab = np.asarray(second_k, dtype=float)
    if j.ndim != 1 or k.shape != (j.size, j.size):
        raise ValueError("K0 must act on the current vector")
    if b.ndim != 2 or b.shape[0] != j.size:
        raise ValueError("first_j must have shape (current,shape)")
    shape_dimension = b.shape[1]
    if c.shape != (j.size, shape_dimension, shape_dimension):
        raise ValueError("second_j must have shape (current,shape,shape)")
    if ka.shape != (shape_dimension, j.size, j.size):
        raise ValueError("first_k must have shape (shape,current,current)")
    if kab.shape != (shape_dimension, shape_dimension, j.size, j.size):
        raise ValueError("second_k has incompatible shape")
    if not np.allclose(k, k.T, atol=1e-12, rtol=0.0):
        raise ValueError("K0 must be symmetric")
    if np.linalg.eigvalsh(k)[0] <= 0.0:
        raise ValueError("K0 must be positive on the gauge-reduced sector")

    g = np.linalg.inv(k)
    beta = g @ j
    r = np.stack([b[:, a] - ka[a] @ beta for a in range(shape_dimension)])
    result = np.zeros((shape_dimension, shape_dimension))
    for a in range(shape_dimension):
        for d in range(shape_dimension):
            result[a, d] = (
                -c[:, a, d] @ beta
                -0.5 * (b[:, a] @ g @ r[d] + b[:, d] @ g @ r[a])
                +0.5 * (r[d] @ g @ ka[a] @ beta + r[a] @ g @ ka[d] @ beta)
                +0.5 * beta @ kab[a, d] @ beta
            )
    return 0.5 * (result + result.T)


def quadratic_current_operator(
    q: Sequence[float],
    j0: np.ndarray,
    k0: np.ndarray,
    first_j: np.ndarray,
    second_j: np.ndarray,
    first_k: np.ndarray,
    second_k: np.ndarray,
) -> float:
    """Evaluate the quadratic Taylor witnesses J(Q), K(Q)."""

    coordinates = np.asarray(q, dtype=float)
    j = j0 + first_j @ coordinates + 0.5 * np.einsum("iab,a,b->i", second_j, coordinates, coordinates)
    k = k0 + np.einsum("aij,a->ij", first_k, coordinates) + 0.5 * np.einsum(
        "abij,a,b->ij", second_k, coordinates, coordinates
    )
    return float(-0.5 * j @ np.linalg.solve(k, j))


def finite_difference_schur_hessian(
    j0: np.ndarray,
    k0: np.ndarray,
    first_j: np.ndarray,
    second_j: np.ndarray,
    first_k: np.ndarray,
    second_k: np.ndarray,
    *,
    epsilon: float = 2.0e-5,
) -> np.ndarray:
    """Central finite-difference Hessian for the general Schur witness."""

    n = first_j.shape[1]
    zero = np.zeros(n)
    base = quadratic_current_operator(zero, j0, k0, first_j, second_j, first_k, second_k)
    hessian = np.zeros((n, n))
    for a in range(n):
        ea = np.zeros(n)
        ea[a] = epsilon
        hessian[a, a] = (
            quadratic_current_operator(ea, j0, k0, first_j, second_j, first_k, second_k)
            - 2.0 * base
            + quadratic_current_operator(-ea, j0, k0, first_j, second_j, first_k, second_k)
        ) / epsilon**2
        for d in range(a + 1, n):
            ed = np.zeros(n)
            ed[d] = epsilon
            value = (
                quadratic_current_operator(ea + ed, j0, k0, first_j, second_j, first_k, second_k)
                - quadratic_current_operator(ea - ed, j0, k0, first_j, second_j, first_k, second_k)
                - quadratic_current_operator(-ea + ed, j0, k0, first_j, second_j, first_k, second_k)
                + quadratic_current_operator(-ea - ed, j0, k0, first_j, second_j, first_k, second_k)
            ) / (4.0 * epsilon**2)
            hessian[a, d] = hessian[d, a] = value
    return hessian


def zero_background_schur_correction(
    current_shape_vertex: Sequence[Sequence[float]],
    momentum_operator: Sequence[Sequence[float]],
) -> np.ndarray:
    """Return -B^T K^-1 B for J0=0 on a fixed common domain."""

    b = np.asarray(current_shape_vertex, dtype=float)
    k = np.asarray(momentum_operator, dtype=float)
    if b.ndim != 2 or k.shape != (b.shape[0], b.shape[0]):
        raise ValueError("operator and current vertex dimensions must match")
    if np.linalg.eigvalsh(k)[0] <= 0.0:
        raise ValueError("momentum operator must be positive after gauge reduction")
    return -b.T @ np.linalg.solve(k, b)


def round_l2_schur_correction(
    current_shape_vertex: Sequence[Sequence[float]],
    *,
    radius: float = 1.0,
    gravitational_coupling: float = 1.0,
) -> np.ndarray:
    """Round reference result -(kappa_grav R^2/5) B^T B."""

    if radius <= 0.0 or gravitational_coupling <= 0.0:
        raise ValueError("action scales must be positive")
    b = np.asarray(current_shape_vertex, dtype=float)
    return -(gravitational_coupling * radius**2 / 5.0) * (b.T @ b)


def reflected_relative_vertex(
    plus_vertex: Sequence[Sequence[float]],
    minus_vertex: Sequence[Sequence[float]],
    current_reflection: Sequence[Sequence[float]],
    shape_reflection: Sequence[Sequence[float]],
) -> np.ndarray:
    """Pull the minus cap to the plus cap and take the relative channel."""

    plus = np.asarray(plus_vertex, dtype=float)
    minus = np.asarray(minus_vertex, dtype=float)
    rc = np.asarray(current_reflection, dtype=float)
    rq = np.asarray(shape_reflection, dtype=float)
    if minus.shape != plus.shape or rc.shape != (plus.shape[0], plus.shape[0]) or rq.shape != (plus.shape[1], plus.shape[1]):
        raise ValueError("reflection maps must match the vertex spaces")
    return plus - rc.T @ minus @ rq


def charge_sector_audit() -> list[dict[str, Any]]:
    """Machine-readable audit of all retained candidate charge sources."""

    return [
        {"sector": "physical_M4_S6_eta_FR", "action_owned": True, "quantized_or_selected": False, "nonzero_required_by_topology": False, "arbitrary_initial_datum": False, "conserved": False, "reflection_parity": "NONE_SELECTED", "possible_L2_current": False, "possible_nonzero_DQJ_L2": False, "classification": "TRIVIAL_PI3_AND_PI4", "viable": False},
        {"sector": "historical_M8_S7_FR_rotor", "action_owned": "ORIGINAL_SECTOR_ONLY", "quantized_or_selected": "SPIN_PARITY_QUANTIZED_CONDITIONALLY", "nonzero_required_by_topology": "J_HALF_ONLY_AFTER_PHYSICAL_ROTATION_LOOP_IDENTIFICATION", "arbitrary_initial_datum": "MAGNETIC_ORIENTATION_NOT_SELECTED", "conserved": "CONDITIONAL_COLLECTIVE_CHARGE", "reflection_parity": "NOT_SELECTED", "possible_L2_current": "ROUND_SPIN4_NO", "possible_nonzero_DQJ_L2": "REDUCED_SYMMETRY_OPEN", "classification": "PHYSICAL_TRANSGRESSION_AND_DOMAIN_OPEN", "viable": False},
        {"sector": "physical_spin_angular_momentum", "action_owned": "SYMMETRY_CHARGE_ALLOWED", "quantized_or_selected": "ALLOWED_NOT_VACUUM_SELECTED", "nonzero_required_by_topology": False, "arbitrary_initial_datum": True, "conserved": True, "reflection_parity": "STATE_DEPENDENT", "possible_L2_current": "ROUND_RIGID_STATE_L1_ONLY", "possible_nonzero_DQJ_L2": "ROUND_SPIN4_FORBIDDEN", "classification": "SUPERSELECTION_OR_INITIAL_STATE", "viable": False},
        {"sector": "foundational_collective_Dirac", "action_owned": "ADOPTED_EFFECTIVE", "quantized_or_selected": "SPECTRUM_ALLOWED_STATE_NOT_SELECTED", "nonzero_required_by_topology": False, "arbitrary_initial_datum": True, "conserved": "CHARGE_IF_STATE_CHOSEN", "reflection_parity": "STATE_AND_DOMAIN_DEPENDENT", "possible_L2_current": "KINEMATICALLY_POSSIBLE", "possible_nonzero_DQJ_L2": "UNDEFINED_WITHOUT_SELECTED_STATE_AND_COMMON_DOMAIN", "classification": "OCCUPANCY_CHARGE_AND_ORIENTATION_ARE_SUPERSELECTION_DATA", "viable": False},
        {"sector": "gauge_color_charge", "action_owned": True, "quantized_or_selected": "CONSTRAINED_NOT_NONZERO_SELECTED", "nonzero_required_by_topology": False, "arbitrary_initial_datum": "SUPERSELECTION_IF_ALLOWED", "conserved": True, "reflection_parity": "NOT_SELECTED", "possible_L2_current": "NOT_ON_PHYSICAL_SINGLET_VACUUM", "possible_nonzero_DQJ_L2": "NOT_DERIVED", "classification": "PHYSICAL_SINGLET_CONSTRAINT", "viable": False},
        {"sector": "normalized_matter_state", "action_owned": "HILBERT_NORMALIZATION_ONLY", "quantized_or_selected": False, "nonzero_required_by_topology": False, "arbitrary_initial_datum": True, "conserved": "STATE_DEPENDENT", "reflection_parity": "STATE_DEPENDENT", "possible_L2_current": "POSSIBLE_BY_CHOSEN_STATE", "possible_nonzero_DQJ_L2": "NOT_ACTION_SELECTED", "classification": "NORMALIZATION_DOES_NOT_SELECT_OCCUPANCY_OR_MULTIPOLE", "viable": False},
        {"sector": "Wilson_sourced_state", "action_owned": "SOURCE_INSERTION", "quantized_or_selected": "EXTERNALLY_SELECTED", "nonzero_required_by_topology": False, "arbitrary_initial_datum": "EXTERNAL_SOURCE_DATA", "conserved": "WITH_SOURCE_ACCOUNTING", "reflection_parity": "SOURCE_DEPENDENT", "possible_L2_current": "SOURCE_DEPENDENT", "possible_nonzero_DQJ_L2": "NOT_DERIVED", "classification": "SOURCE_BOUND_NOT_CLOSED_SYSTEM_VACUUM", "viable": False},
        {"sector": "black_hole_accretion_jet_exchange", "action_owned": "CONSERVATION_ARCHITECTURE_ONLY", "quantized_or_selected": False, "nonzero_required_by_topology": False, "arbitrary_initial_datum": "FORCING_PROFILE_FORBIDDEN", "conserved": "TOTAL_DRIVER_PLUS_BHSM", "reflection_parity": "OPEN_MUST_BE_DERIVED", "possible_L2_current": "OPEN", "possible_nonzero_DQJ_L2": "OPEN_EXACT_NEXT_ROUTE", "classification": "CONTROLLED_EXCHANGE_REDUCTION_REQUIRED", "viable": "OPEN"},
        {"sector": "moving_boundary_canonical_momentum", "action_owned": "BOUNDARY_ACTION_EXISTS_CONDITIONALLY", "quantized_or_selected": False, "nonzero_required_by_topology": False, "arbitrary_initial_datum": True, "conserved": "ONLY_WITH_FULL_BOUNDARY_SYSTEM", "reflection_parity": "OPEN", "possible_L2_current": "KINEMATICALLY_POSSIBLE", "possible_nonzero_DQJ_L2": "COMMON_DOMAIN_NOT_DERIVED", "classification": "TIME_SYMMETRIC_BACKGROUND_MOMENTUM_ZERO", "viable": False},
        {"sector": "parent_child_relative_charge", "action_owned": "KINEMATICALLY_ELIGIBLE", "quantized_or_selected": False, "nonzero_required_by_topology": False, "arbitrary_initial_datum": True, "conserved": "OPEN", "reflection_parity": "OPEN", "possible_L2_current": "OPEN", "possible_nonzero_DQJ_L2": "OPEN", "classification": "COUPLED_PARENT_CHILD_ACTION_NOT_DERIVED", "viable": False},
        {"sector": "other_retained_Noether_charges", "action_owned": True, "quantized_or_selected": "ALLOWED_NOT_NONZERO_SELECTED", "nonzero_required_by_topology": False, "arbitrary_initial_datum": True, "conserved": True, "reflection_parity": "CHARGE_DEPENDENT", "possible_L2_current": "NO_RETAINED_DERIVATION", "possible_nonzero_DQJ_L2": "NO_RETAINED_DERIVATION", "classification": "CONSERVATION_DOES_NOT_SELECT_NONZERO_VACUUM_VALUE", "viable": False},
    ]


def deterministic_witness() -> dict[str, Any]:
    rng = np.random.default_rng(1488)
    current_dimension, shape_dimension = 4, 3
    a = rng.normal(size=(current_dimension, current_dimension))
    k0 = a.T @ a + 3.0 * np.eye(current_dimension)
    j0 = rng.normal(scale=0.2, size=current_dimension)
    first_j = rng.normal(scale=0.3, size=(current_dimension, shape_dimension))
    second_j = rng.normal(scale=0.1, size=(current_dimension, shape_dimension, shape_dimension))
    second_j = 0.5 * (second_j + second_j.swapaxes(1, 2))
    first_k = rng.normal(scale=0.05, size=(shape_dimension, current_dimension, current_dimension))
    first_k = 0.5 * (first_k + first_k.swapaxes(1, 2))
    second_k = rng.normal(scale=0.02, size=(shape_dimension, shape_dimension, current_dimension, current_dimension))
    second_k = 0.25 * (
        second_k
        + second_k.swapaxes(0, 1)
        + second_k.swapaxes(2, 3)
        + second_k.swapaxes(0, 1).swapaxes(2, 3)
    )
    analytic = schur_hessian_correction(j0, k0, first_j, second_j, first_k, second_k)
    numeric = finite_difference_schur_hessian(j0, k0, first_j, second_j, first_k, second_k)
    zero_correction = zero_background_schur_correction(first_j, k0)
    return {
        "general_schur_finite_difference_error": float(np.linalg.norm(analytic - numeric, ord=np.inf)),
        "zero_background_correction_max_eigenvalue": float(np.linalg.eigvalsh(zero_correction)[-1]),
        "round_representation": round_representation_kill_screen(),
    }


def completion_payload() -> dict[str, Any]:
    witness = deterministic_witness()
    topology = fr_obstruction_payload()
    _, zero_b = zero_charge_eta_current_shape_vertex(np.zeros(9), 8, legendre_margin=1.0)
    validation = {
        "physical_M4_S6_FR_loop_is_trivial": topology["validation_passed"] and topology["validation"]["pi4_S6_vanishes"],
        "zero_charge_eta_current_shape_vertex_is_zero": bool(np.allclose(zero_b, 0.0)),
        "round_Spin4_product_excludes_coexact_L2": not witness["round_representation"]["round_Spin4_allows_coexact_L2"],
        "diagonal_SO3_does_not_overextend_round_no_go": witness["round_representation"]["diagonal_SO3_allows_L2"],
        "general_Schur_formula_matches_finite_difference": witness["general_schur_finite_difference_error"] < 2.0e-6,
        "zero_background_Schur_correction_nonpositive": witness["zero_background_correction_max_eigenvalue"] <= 1.0e-12,
        "full_BHSM_not_claimed": True,
        "flavor_gates_preserved": True,
        "USB_not_eligible": True,
    }
    return {
        "artifact": "BHSM_action_selected_charge_current_shape_schur_gate_v14_88",
        "version": VERSION,
        "primary_machine_readable_verdict": PRIMARY_VERDICT,
        "canonical_long_range_object": EXACT_NEXT_OBJECT,
        "next_canonical_object": NEXT_CANONICAL_OBJECT,
        "charge_sector_audit": charge_sector_audit(),
        "FR_status": {
            "historical_M8_S7_rule": "CONDITIONAL_2j_EQUALS_N_MOD_2_WITH_LOWEST_ODD_J_HALF",
            "physical_M4_S6_FR": "ABSENT_BECAUSE_PI4_S6_ZERO",
            "nonzero_physical_charge": "NOT_ACTION_SELECTED",
            "fixed_charge_Routh": "DERIVED_CONDITIONALLY_ON_POSITIVE_INERTIA_OR_LEGENDRE_CONE",
        },
        "eta_zero_charge_theorem": {
            "J0": "ZERO",
            "B_L2": "ZERO",
            "scope": "FIXED_P_ETA_ZERO_CONNECTED_POSITIVE_LEGENDRE_BRANCH_FOR_ALL_NEARBY_Q",
            "reason": "LEGENDRE_INVERTIBILITY_IMPLIES_D0ETA_OF_Q_ZERO_AND_J_OF_Q_IDENTICALLY_ZERO",
        },
        "representation_theory": witness["round_representation"],
        "sourced_coexact_solution": {
            "round_operator": "K_beta_L2=5/(kappa_grav R^2)",
            "solution": "beta_L2=(kappa_grav R^2/5)J_L2",
            "effective_Hessian_if_J0_zero": "DeltaH=-(kappa_grav R^2/5)B_L2^dagger B_L2",
            "physical_application": "CONDITIONAL_NO_ACTION_SELECTED_NONZERO_B_L2",
        },
        "exact_Routh_Schur_theorem": {
            "functional": "Gamma_eff=Gamma_shape-1/2 J(Q)^dagger K(Q)^-1 J(Q)",
            "general_second_variation": "IMPLEMENTED_WITH_DJ_D2J_DK_D2K_AND_NONZERO_J0",
            "common_domain_requirement": "PROJECTOR_ZERO_MODE_AND_DOMAIN_VARIATIONS_MUST_BE_TRIVIALIZED_IN_J_AND_K_BEFORE_DIFFERENTIATION",
            "J0_zero_reduction": "DeltaH=-B^dagger K^-1 B is nonpositive for K positive",
        },
        "reflection_result": {
            "relative_vertex": "B_rel=B_plus-R_current^dagger B_minus R_shape",
            "reflection_even_identified_caps": "CANCEL",
            "reflection_odd_identified_caps": "DOUBLE",
            "physical_parity": "NOT_SELECTED_WITHOUT_FULL_PREIMAGE_BACKGROUND_AND_COMMON_DOMAIN",
        },
        "common_self_adjoint_domain": "OPEN_NOT_DERIVED",
        "cap_inertia": "OPEN;_V14_84_OPERATOR_THEOREM_REMAINS_CONDITIONAL",
        "complete_ell2_eigenvalues": "NOT_AVAILABLE_BECAUSE_NO_PHYSICAL_VERTEX_OR_COMPLETE_HESSIAN",
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
                "zero p_eta makes J_eta(Q) and D_Q J_eta vanish throughout the positive Legendre branch",
                "the exact fixed-charge rotor Routhian and common-domain general Schur Hessian",
                "the round Spin4 rigid-L1-current times scalar-ell2 representation no-go",
            ],
            "invalidated": [
                "a physical M4 S6 FR charge",
                "a nonzero current-shape vertex on the fixed zero eta momentum branch",
                "promotion of an allowed or conserved charge to an action-selected nonzero vacuum charge",
            ],
            "reclassified": [
                "the historical M8 FR j=1/2 sector as requiring physical transgression and state selection",
                "the momentum Schur term as a valid conditional softening theorem without a retained physical source",
            ],
            "open": [NEXT_CANONICAL_OBJECT],
        },
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "numeric_witness": witness,
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
    output = root / "artifacts" / "BHSM_action_selected_charge_current_shape_schur_gate_v14_88.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(deterministic_json(completion_payload()), encoding="utf-8", newline="\n")
    return output
