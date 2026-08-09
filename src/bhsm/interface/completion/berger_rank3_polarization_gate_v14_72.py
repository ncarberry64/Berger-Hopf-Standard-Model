"""BHSM v14.72 Berger rank-three carrier / polarization gate.

v14.71 proved that a complete *round-equivariant* second-shape Hessian is
central on the nine-dimensional ell=2 scalar shape sector and therefore cannot
select the rank-three subspace found in v14.70.

This sprint tests the strongest pre-existing BHSM symmetry-breaking candidate:
the twistor/ Berger fiber modulus already present in the repository.

For
    g_B = L2^2 (sigma1^2 + sigma2^2) + L1^2 sigma3^2
the scalar Berger spectrum is
    lambda_(J,m) = J(J+1)/L2^2 + m^2(1/L1^2 - 1/L2^2).

On the round ell=2 sector one has J=1 and dimension 9.  A fixed Berger axis
therefore splits the space exactly as
    m=0:  rank 3,
    m=+/-1: combined rank 6,
whenever L1 != L2.

At fixed fiber volume define
    rho=(L2^2 L1)^(1/3), beta=L1/L2.
Then
    rho^2 lambda_0 = 2 beta^(2/3),
    rho^2 lambda_pm = beta^(2/3)+beta^(-4/3),
    rho^2 Delta = beta^(-4/3)-beta^(2/3).
The first-order split at beta=1 is traceless:
    d lambda_0/d beta = 4/(3 rho^2),
    d lambda_pm/d beta = -2/(3 rho^2).

This is a genuine kinematic rank-three carrier mechanism.  It is not yet a
physical BHSM selector.  The authoritative current action has not selected a
global Sp(1)->U(1) polarization or a stationary beta != 1.  If the axis is not
physically selected, averaging its rank-three projector over orientations gives
I_9/3 and restores the centrality no-go.

The fixed-axis Berger rank-three carrier is also not the same object as the
v14.70 diagonal-SU(2) antisymmetric triplet.  In an aligned Cartesian
representative the two rank-three projectors have zero-dimensional
intersection, trace overlap 1, and Frobenius distance 2.

Finally, axisymmetric Berger squashing only isolates a three-dimensional
carrier.  It retains an internal SU(2) degeneracy and does not by itself create
three distinct noncommuting wake channels, CKM/PMNS mixing, or a neutrino
observable.

No measured particle/flavor input is used and no physical prediction is
emitted.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

VERSION = "v14.72"

PRIMARY_VERDICT = (
    "BHSM_V14_72_THE_PREEXISTING_TWISTOR_BERGER_GEOMETRY_CONTAINS_AN_EXACT_"
    "KINEMATIC_RANK_THREE_CARRIER_MECHANISM_ON_THE_ELL2_NINE_DIMENSIONAL_"
    "SHAPE_SPACE_BECAUSE_ANY_FIXED_AXIS_SQUASHING_BETA_NOT_EQUAL_ONE_SPLITS_"
    "THE_J1_BERGER_SPECTRUM_AS_3_PLUS_6_WITH_A_NONZERO_SCALE_FREE_GAP;_"
    "HOWEVER_THE_CURRENT_AUTHORITATIVE_ACTION_DOES_NOT_SELECT_A_GLOBAL_"
    "SP1_TO_U1_POLARIZATION_OR_A_STATIONARY_NONROUND_BETA_AND_ORIENTATION_"
    "AVERAGING_OF_AN_UNSELECTED_AXIS_RESTORES_THE_CENTRAL_I9_OVER3_RESPONSE;_"
    "MOREOVER_THE_BERGER_TRIPLET_IS_NOT_THE_V14_70_DIAGONAL_SU2_TRIPLET_AND_"
    "AXISYMMETRIC_SQUASHING_ALONE_DOES_NOT_GENERATE_THREE_NONCOMMUTING_"
    "CHANNELS_SO_PHYSICAL_EXECUTION_REMAINS_BLOCKED_AT_ACTION_SELECTED_"
    "POLARIZATION_BETA_STATIONARITY_AND_TRANSVERSE_CHANNEL_DYNAMICS"
)

EXACT_NEXT_OBJECT = (
    "GLOBAL_ACTION_DERIVATION_OF_A_PHYSICAL_SP1_TO_U1_POLARIZATION_SECTION_OR_"
    "EQUIVALENT_ADJOINT_CONNECTION_HOLONOMY_TOGETHER_WITH_A_GAUGE_REDUCED_"
    "STATIONARY_BERGER_SQUASHING_BETA_STAR_NOT_EQUAL_ONE_AND_POSITIVE_SCHUR_"
    "CURVATURE_THEN_ACTION_OWNED_TRANSPORT_OF_THE_RESULTING_RANK_THREE_"
    "SPECTRAL_PROJECTOR_INTO_THE_THREE_TRANSVERSE_CALDERON_SHAPE_DERIVATIVES_"
    "FOLLOWED_BY_NONCOMMUTING_WAKE_DYNAMICS_RELATIVE_HEAT_SUPERTRACE_AND_THE_"
    "FROZEN_NEUTRINO_KILL_SCREEN"
)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("utf-8")


def sha256_payload(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def fixed_volume_lengths(rho: float, beta: float) -> tuple[float, float]:
    """Return (L2,L1) with L2^2 L1 = rho^3 and beta=L1/L2."""
    rho = float(rho)
    beta = float(beta)
    if rho <= 0.0 or beta <= 0.0:
        raise ValueError("rho and beta must be positive")
    L2 = rho * beta ** (-1.0 / 3.0)
    L1 = rho * beta ** (2.0 / 3.0)
    return L2, L1


def berger_scalar_eigenvalue(J: int, m: int, L2: float, L1: float) -> float:
    """Repository Berger scalar formula restricted to integral J,m witnesses."""
    if not isinstance(J, int) or J < 0:
        raise ValueError("J must be a nonnegative integer in this reduced witness")
    if not isinstance(m, int) or abs(m) > J:
        raise ValueError("m must be an integral magnetic weight with |m|<=J")
    if L1 <= 0.0 or L2 <= 0.0:
        raise ValueError("Berger lengths must be positive")
    return J * (J + 1.0) / (L2 * L2) + m * m * (
        1.0 / (L1 * L1) - 1.0 / (L2 * L2)
    )


def ell2_spectrum(rho: float = 1.0, beta: float = 1.0) -> dict[str, Any]:
    """J=1 Berger splitting of the nine-dimensional round ell=2 sector."""
    L2, L1 = fixed_volume_lengths(rho, beta)
    lam0 = berger_scalar_eigenvalue(1, 0, L2, L1)
    lamp = berger_scalar_eigenvalue(1, 1, L2, L1)
    lamm = berger_scalar_eigenvalue(1, -1, L2, L1)
    return {
        "rho": float(rho),
        "beta": float(beta),
        "L2": L2,
        "L1": L1,
        "volume_shape_product_L2sqL1": L2 * L2 * L1,
        "m0_eigenvalue": lam0,
        "mplus_eigenvalue": lamp,
        "mminus_eigenvalue": lamm,
        "m0_multiplicity": 3,
        "mplus_multiplicity": 3,
        "mminus_multiplicity": 3,
        "combined_abs_m1_multiplicity": 6,
        "gap_abs_m1_minus_m0": lamp - lam0,
        "dimension_total": 9,
    }


def dimensionless_fixed_volume_spectrum(beta: float) -> dict[str, float]:
    beta = float(beta)
    if beta <= 0:
        raise ValueError("beta must be positive")
    lambda0 = 2.0 * beta ** (2.0 / 3.0)
    lambda_pm = beta ** (2.0 / 3.0) + beta ** (-4.0 / 3.0)
    return {
        "rho2_lambda_m0": lambda0,
        "rho2_lambda_abs_m1": lambda_pm,
        "rho2_gap": lambda_pm - lambda0,
    }


def analytic_round_derivatives(rho: float = 1.0) -> dict[str, float]:
    if rho <= 0:
        raise ValueError("rho must be positive")
    inv = 1.0 / (rho * rho)
    return {
        "d_lambda_m0_d_beta_at_1": (4.0 / 3.0) * inv,
        "d_lambda_abs_m1_d_beta_at_1": (-2.0 / 3.0) * inv,
        "d_gap_d_beta_at_1": -2.0 * inv,
        "multiplicity_weighted_trace_derivative": (
            3.0 * (4.0 / 3.0) + 6.0 * (-2.0 / 3.0)
        ) * inv,
    }


def finite_difference_round_derivatives(rho: float = 1.0, eps: float = 1e-6) -> dict[str, float]:
    if eps <= 0:
        raise ValueError("eps must be positive")
    p = ell2_spectrum(rho, 1.0 + eps)
    m = ell2_spectrum(rho, 1.0 - eps)
    return {
        "d_lambda_m0_d_beta_at_1": (p["m0_eigenvalue"] - m["m0_eigenvalue"]) / (2 * eps),
        "d_lambda_abs_m1_d_beta_at_1": (p["mplus_eigenvalue"] - m["mplus_eigenvalue"]) / (2 * eps),
        "d_gap_d_beta_at_1": (p["gap_abs_m1_minus_m0"] - m["gap_abs_m1_minus_m0"]) / (2 * eps),
    }


def spin1_generators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Hermitian spin-1 generators in the m=(+1,0,-1) basis."""
    root2 = np.sqrt(2.0)
    jp = np.array(
        [[0.0, root2, 0.0], [0.0, 0.0, root2], [0.0, 0.0, 0.0]], dtype=complex
    )
    jm = jp.conj().T
    jx = (jp + jm) / 2.0
    jy = (jp - jm) / (2.0j)
    jz = np.diag([1.0, 0.0, -1.0]).astype(complex)
    return jx, jy, jz


def berger_rank3_projector_m_basis() -> np.ndarray:
    """Project onto m_R=0 for each of the three left states."""
    p0 = np.diag([0.0, 1.0, 0.0])
    return np.kron(np.eye(3), p0)


def berger_rank6_projector_m_basis() -> np.ndarray:
    return np.eye(9) - berger_rank3_projector_m_basis()


def berger_ell2_operator(rho: float = 1.0, beta: float = 1.0) -> np.ndarray:
    spec = ell2_spectrum(rho, beta)
    p3 = berger_rank3_projector_m_basis()
    p6 = np.eye(9) - p3
    return spec["m0_eigenvalue"] * p3 + spec["mplus_eigenvalue"] * p6


def max_commutator_norm(operator: np.ndarray, generators: list[np.ndarray]) -> float:
    op = np.asarray(operator, dtype=complex)
    return float(max(np.linalg.norm(op @ g - g @ op) for g in generators))


def symmetry_breaking_payload(beta: float = 0.8) -> dict[str, Any]:
    """Show SU2_L x SU2_R -> SU2_L x U1_R for beta != 1."""
    if beta <= 0 or abs(beta - 1.0) < 1e-12:
        raise ValueError("use a positive nonround beta for the witness")
    jx, jy, jz = spin1_generators()
    left = [np.kron(g, np.eye(3)) for g in (jx, jy, jz)]
    right = [np.kron(np.eye(3), g) for g in (jx, jy, jz)]
    op = berger_ell2_operator(1.0, beta)
    return {
        "diagnostic_beta": float(beta),
        "diagnostic_beta_is_physical": False,
        "commutator_with_left_SU2": max_commutator_norm(op, left),
        "commutator_with_right_U1_Jz": max_commutator_norm(op, [right[2]]),
        "commutator_with_right_Jx_Jy": max_commutator_norm(op, right[:2]),
        "residual_symmetry": "SU(2)_L x U(1)_R",
        "full_round_SU2R_broken": True,
    }


def _matrix_space_projector(fn) -> np.ndarray:
    cols = []
    for i in range(3):
        for j in range(3):
            e = np.zeros((3, 3))
            e[i, j] = 1.0
            cols.append(np.asarray(fn(e)).reshape(-1))
    return np.column_stack(cols)


def diagonal_su2_triplet_projector() -> np.ndarray:
    """Rank-three antisymmetric piece in 3 tensor 3 = 1 + 3 + 5."""
    return _matrix_space_projector(lambda a: 0.5 * (a - a.T))


def berger_axis_projector_cartesian(axis=(0.0, 0.0, 1.0)) -> np.ndarray:
    """Cartesian representative I_3 tensor |n><n| of the Berger m=0 triplet."""
    n = np.asarray(axis, dtype=float)
    if n.shape != (3,) or np.linalg.norm(n) == 0:
        raise ValueError("axis must be a nonzero three-vector")
    n = n / np.linalg.norm(n)
    return np.kron(np.eye(3), np.outer(n, n))


def projector_intersection_dimension(p: np.ndarray, q: np.ndarray, tol: float = 1e-10) -> int:
    """Intersection dimension from eigenvalue-one directions of P Q P."""
    vals = np.linalg.eigvalsh((p @ q @ p + (p @ q @ p).T) / 2.0)
    return int(np.sum(vals > 1.0 - tol))


def aligned_triplet_comparison_payload() -> dict[str, Any]:
    pb = berger_axis_projector_cartesian((0, 0, 1))
    pd = diagonal_su2_triplet_projector()
    vals = np.linalg.eigvalsh((pb @ pd @ pb + (pb @ pd @ pb).T) / 2.0)
    nonzero = sorted(float(v) for v in vals if v > 1e-12)
    principal_angles = [float(np.degrees(np.arccos(np.sqrt(v)))) for v in nonzero]
    # include the orthogonal direction in the rank-three Berger space
    principal_angles.append(90.0)
    principal_angles = sorted(principal_angles)
    return {
        "frame": "aligned Cartesian left/right representative",
        "Berger_triplet_rank": int(np.linalg.matrix_rank(pb)),
        "diagonal_SU2_triplet_rank": int(np.linalg.matrix_rank(pd)),
        "intersection_dimension": projector_intersection_dimension(pb, pd),
        "trace_projector_overlap": float(np.trace(pb @ pd)),
        "frobenius_projector_distance": float(np.linalg.norm(pb - pd)),
        "principal_angles_degrees": principal_angles,
        "same_subspace": bool(np.linalg.norm(pb - pd) < 1e-12),
        "structural_reason_for_nonidentity": (
            "Berger carrier is a product subspace V_left tensor line_right; "
            "nonzero diagonal-triplet matrices are antisymmetric and have even rank, "
            "so the two carrier definitions cannot be identified without an intertwiner"
        ),
        "physical_intertwiner_derived": False,
    }


def orientation_average_payload() -> dict[str, Any]:
    """Exact six-axis spherical 2-design average of the unselected Berger axis."""
    axes = [
        (1, 0, 0), (-1, 0, 0),
        (0, 1, 0), (0, -1, 0),
        (0, 0, 1), (0, 0, -1),
    ]
    avg = sum(berger_axis_projector_cartesian(a) for a in axes) / len(axes)
    target = np.eye(9) / 3.0
    return {
        "axis_average_rule": "<n_i n_j> = delta_ij/3",
        "rank3_projector_average": "I9/3",
        "six_axis_2_design_residual": float(np.linalg.norm(avg - target)),
        "average_eigenvalues": [float(x) for x in np.linalg.eigvalsh(avg)],
        "central_under_full_product_group": True,
        "conclusion": (
            "without an action-selected physical axis/polarization the Berger "
            "rank-three carrier averages back to a central response and cannot evade v14.71"
        ),
    }


def fixed_volume_splitting_payload() -> dict[str, Any]:
    witness = ell2_spectrum(1.0, 0.8)
    deriv = analytic_round_derivatives(1.0)
    fd = finite_difference_round_derivatives(1.0)
    dimless = dimensionless_fixed_volume_spectrum(0.8)
    return {
        "metric": "g_B=L2^2(sigma1^2+sigma2^2)+L1^2 sigma3^2",
        "shape_variables": {
            "rho": "(L2^2 L1)^(1/3)",
            "beta": "L1/L2",
            "L2": "rho beta^(-1/3)",
            "L1": "rho beta^(2/3)",
        },
        "fixed_volume_identity": "L2^2 L1=rho^3",
        "J1_spectrum": {
            "rank3_m0": "lambda0=2/L2^2=2 beta^(2/3)/rho^2",
            "rank6_abs_m1": "lambda1=1/L2^2+1/L1^2=(beta^(2/3)+beta^(-4/3))/rho^2",
            "gap": "Delta=(beta^(-4/3)-beta^(2/3))/rho^2",
        },
        "round_beta": 1.0,
        "round_gap": dimensionless_fixed_volume_spectrum(1.0)["rho2_gap"],
        "linear_response_at_round": deriv,
        "finite_difference_check": fd,
        "max_derivative_residual": max(
            abs(fd[k] - deriv[k]) for k in fd
        ),
        "first_order_trace_shift_zero": abs(deriv["multiplicity_weighted_trace_derivative"]) < 1e-14,
        "diagnostic_beta_0p8": {
            "physical": False,
            "dimensionless_spectrum": dimless,
            "full_witness": witness,
        },
        "rank3_isolated_for_every_beta_not_equal_one": True,
        "which_branch_lower": "rank3 m=0 is lower for beta<1; rank6 |m|=1 is lower for beta>1",
        "absolute_scale_required_for_rank_split": False,
    }


def action_selection_contract_payload() -> dict[str, Any]:
    return {
        "selector_coordinates": [
            "rho overall fiber scale",
            "beta=L1/L2 dimensionless Berger squashing",
            "polarization/orientation reducing Sp(1) to U(1) or equivalent connection holonomy",
        ],
        "global_effective_action": "Gamma_eff[rho,beta,polarization,Phi_other]",
        "stationarity_conditions": [
            "delta Gamma/delta Phi_other = 0",
            "partial_beta Gamma_eff = 0",
            "polarization Euler/Gauss equation = 0 modulo gauge",
        ],
        "local_stability_condition": (
            "k_beta_eff=Gamma_beta_beta-Gamma_beta_I "
            "(Gamma_II_phys)^(-1) Gamma_I_beta > 0"
        ),
        "triplet_condition": "beta_star != 1",
        "global_requirement": "exhaust gauge-inequivalent competing stationary branches",
        "no_new_field_required_if": (
            "the selector is derived from already-owned metric/connection degrees "
            "rather than inserted as an external order parameter"
        ),
        "measured_particle_or_flavor_data_allowed_in_selection": False,
        "current_contract_executed_physically": False,
    }


def selector_provenance_payload() -> dict[str, Any]:
    rows = [
        {
            "candidate": "twistor-Berger metric modulus beta=L1/L2",
            "what_exists": "global mathematical Berger metric family and exact fiber spectrum",
            "action_status": "historical reduction uses a provisional parent; parent family physically selected = false",
            "global_axis_status": "no physical common-domain U1 reduction selected in the authoritative branch",
            "can_kinematically_isolate_rank3": True,
            "physically_selected_now": False,
        },
        {
            "candidate": "nested S7->CP3->S4 U1 direction",
            "what_exists": "global V1 direction on total S7 in the twistor construction",
            "action_status": "mathematical geometry; no twistor section / physical base polarization promoted",
            "global_axis_status": "authoritative Sp1 transport does not assert a preferred U1 axis",
            "can_kinematically_isolate_rank3": True,
            "physically_selected_now": False,
        },
        {
            "candidate": "degree-one eta texture",
            "what_exists": "conditional static cohomogeneity-one p2+p8 solution",
            "action_status": "derived only in reduced flat-R7 theorem class",
            "global_axis_status": "not a degree-one full Hopf-preimage stationary background",
            "can_kinematically_isolate_rank3": False,
            "physically_selected_now": False,
        },
        {
            "candidate": "G2/SU3 eta-wall polarization",
            "what_exists": "conditional local associated-bundle/coset construction",
            "action_status": "common physical SU3 bundle and parent-to-collar action ownership remain open",
            "global_axis_status": "does not yet provide the required seam Berger polarization",
            "can_kinematically_isolate_rank3": False,
            "physically_selected_now": False,
        },
        {
            "candidate": "independent M4 gauge connection / holonomy",
            "what_exists": "independent localized gauge field in the stratified action",
            "action_status": "physical eta/common-domain coupling and stationary selector not derived",
            "global_axis_status": "round reference vacuum does not select the needed polarization",
            "can_kinematically_isolate_rank3": "possible in principle",
            "physically_selected_now": False,
        },
    ]
    return {
        "rows": rows,
        "strongest_current_candidate": "twistor-Berger beta plus a physical Sp1->U1 polarization",
        "rank3_carrier_already_available_mathematically": True,
        "action_selected_rank3_carrier_available": False,
        "no_candidate_promoted_by_v14_72": True,
    }


def transverse_channel_firewall_payload() -> dict[str, Any]:
    return {
        "Berger_fixed_axis_residual_symmetry": "SU(2)_L x U(1)_R",
        "rank3_carrier_dimension": 3,
        "operator_on_rank3_from_pure_axisymmetric_Berger_squashing": "lambda0 I3",
        "internal_triplet_split": False,
        "three_noncommuting_generators_derived": False,
        "CKM_or_PMNS_generated": False,
        "neutrino_three_wake_dynamics_generated": False,
        "interpretation": (
            "Berger squashing can select the carrier subspace but cannot by itself "
            "supply the three transverse noncommuting shape/current operators required downstream"
        ),
        "downstream_requirement": (
            "action-owned transverse moving-seam harmonics / shape-current vertices "
            "inside the selected carrier"
        ),
    }


def calderon_handoff_payload() -> dict[str, Any]:
    return {
        "eligible_now": False,
        "conditional_handoff_if_selector_closes": [
            "derive beta_star and physical polarization before comparison",
            "form spectral projector P_B(beta_star) onto isolated rank-three branch",
            "transport P_B through the action-owned tensor incidence/intertwiner",
            "differentiate the physical operator in three transverse carrier directions",
            "insert those three derivatives into the operator-valued Calderon/Wentzell domain",
            "compute relative heat/zeta derivatives with complete zero-mode/gauge/ghost projectors",
        ],
        "current_blockers": [
            "physical global polarization absent",
            "beta_star absent",
            "physical carrier-to-seam intertwiner absent",
            "three transverse noncommuting derivatives absent",
        ],
        "physical_prediction": False,
    }


def neutrino_kill_screen_payload() -> dict[str, Any]:
    return {
        "current_result": "PHYSICAL_EXECUTION_BLOCKED",
        "physical_execution_allowed": False,
        "reason": (
            "a mathematical Berger rank-three carrier exists but neither its global "
            "polarization nor beta_star nor the three transverse physical derivatives "
            "are action-selected"
        ),
        "measured_PMNS_or_mass_splitting_used": False,
        "physical_neutrino_output_emitted": False,
    }


def status_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "validated": [
            "exact J=1 Berger splitting of the nine-dimensional ell=2 space",
            "nonround fixed-axis squashing gives rank 3 plus rank 6",
            "fixed-volume gap is dimensionless and independent of absolute scale",
            "round first-order split is nonzero and multiplicity-traceless",
            "Berger operator preserves SU2_L x U1_R and breaks the remaining right generators",
            "unselected-axis orientation averaging returns I9/3 and restores centrality",
            "Berger rank-three carrier is not the diagonal-SU2 antisymmetric triplet",
            "pure axisymmetric Berger squashing remains scalar inside the selected rank-three carrier",
            "existing BHSM geometry contains the kinematic mechanism without measured input",
        ],
        "invalidated": [
            "every useful rank-three selector must specifically be the v14.70 diagonal-SU2 triplet",
            "a fiberwise Berger split is automatically a globally action-owned physical selector",
            "a mathematically distinguished U1 direction can be used without proving physical polarization/gauge provenance",
            "axisymmetric Berger squashing alone closes the three noncommuting wake/flavor channels",
        ],
        "reclassified": [
            "the symmetry-breaker search now has a concrete pre-existing candidate: the Berger modulus",
            "the missing object is action selection and global polarization, not invention of a rank-three spectral mechanism",
            "absolute scale is downstream of the rank3-vs-rank6 split because beta controls the dimensionless gap",
            "diagonal-SU2 triplet and Berger m=0 carrier are distinct possible three-dimensional mechanisms",
        ],
        "open": [
            EXACT_NEXT_OBJECT,
            "physical stationary beta_star",
            "physical Sp1->U1 polarization or equivalent holonomy",
            "carrier-to-seam intertwiner",
            "three transverse noncommuting shape/current derivatives",
            "physical operator-valued Calderon blocks",
            "relative heat supertrace",
            "frozen neutrino execution",
        ],
        "FULL_BHSM_COMPLETE": False,
        "MARK_III": "NOT_REACHED",
        "physical_prediction_emitted": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "USB_touched": False,
    }


def completion_gate_payload() -> dict[str, Any]:
    split = fixed_volume_splitting_payload()
    orient = orientation_average_payload()
    compare = aligned_triplet_comparison_payload()
    sym = symmetry_breaking_payload(0.8)
    provenance = selector_provenance_payload()
    firewall = transverse_channel_firewall_payload()
    validation = {
        "rank3_plus_rank6_exact": (
            split["diagnostic_beta_0p8"]["full_witness"]["m0_multiplicity"] == 3
            and split["diagnostic_beta_0p8"]["full_witness"]["combined_abs_m1_multiplicity"] == 6
        ),
        "nonround_gap_nonzero": abs(split["diagnostic_beta_0p8"]["dimensionless_spectrum"]["rho2_gap"]) > 1e-6,
        "round_derivative_check": split["max_derivative_residual"] < 1e-8,
        "first_order_trace_shift_zero": split["first_order_trace_shift_zero"],
        "residual_symmetry_correct": (
            sym["commutator_with_left_SU2"] < 1e-12
            and sym["commutator_with_right_U1_Jz"] < 1e-12
            and sym["commutator_with_right_Jx_Jy"] > 1e-4
        ),
        "orientation_average_restores_centrality": orient["six_axis_2_design_residual"] < 1e-12,
        "Berger_and_diagonal_triplets_distinct": (
            compare["same_subspace"] is False and compare["intersection_dimension"] == 0
        ),
        "action_selected_carrier_not_claimed": provenance["action_selected_rank3_carrier_available"] is False,
        "axisymmetric_internal_split_not_claimed": firewall["internal_triplet_split"] is False,
        "no_physical_prediction": True,
    }
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "rank3_carrier_mechanism": "KINEMATICALLY_DERIVED",
        "global_physical_selector": "OPEN",
        "stationary_beta_star": None,
        "physical_transverse_triplet_dynamics": "OPEN",
        "full_BHSM_complete": False,
        "mark_III": "NOT_REACHED",
        "physical_execution_allowed": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "usb_touched": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def artifact_payloads() -> dict[str, Any]:
    return {
        "BHSM_berger_ell2_splitting_v14_72.json": fixed_volume_splitting_payload(),
        "BHSM_berger_symmetry_breaking_v14_72.json": symmetry_breaking_payload(0.8),
        "BHSM_berger_triplet_projector_comparison_v14_72.json": aligned_triplet_comparison_payload(),
        "BHSM_unselected_axis_average_v14_72.json": orientation_average_payload(),
        "BHSM_berger_action_selection_contract_v14_72.json": action_selection_contract_payload(),
        "BHSM_selector_candidate_provenance_v14_72.json": selector_provenance_payload(),
        "BHSM_transverse_channel_firewall_v14_72.json": transverse_channel_firewall_payload(),
        "BHSM_calderon_handoff_v14_72.json": calderon_handoff_payload(),
        "BHSM_neutrino_kill_screen_v14_72.json": neutrino_kill_screen_payload(),
        "BHSM_status_ledger_v14_72.json": status_payload(),
        "BHSM_completion_gate_v14_72.json": completion_gate_payload(),
    }


def materialize(outdir: Path) -> list[Path]:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for name, payload in sorted(artifact_payloads().items()):
        path = out / name
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        written.append(path)
    return written
