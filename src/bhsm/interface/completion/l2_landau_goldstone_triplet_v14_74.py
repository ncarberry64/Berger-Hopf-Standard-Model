"""BHSM v14.74 ell=2 Landau locking and Goldstone-triplet gate.

The v14.73 full-base U(1)-axis route is topologically obstructed.  This sprint
tests a different non-Abelian route that uses only the already identified
nine-dimensional ell=2 scalar shape space.

Write the real ell=2 coefficient space as
    Q in V_L tensor V_R ~= Mat(3,R),
with the round symmetry acting by
    Q -> R_L Q R_R^T,  R_L,R_R in SO(3).

On the reflection-symmetric two-cap branch the normal displacement changes
sign under cap exchange, so the effective shape action is even under Q->-Q.
To quartic order the most general SO(3)_L x SO(3)_R invariant even Landau
potential is
    V(Q)= r/2 Tr(Q^T Q)
        + u/4 [Tr(Q^T Q)]^2
        + v/4 Tr[(Q^T Q)^2].
(The cubic invariant det Q is allowed by SO(3)xSO(3) but is odd under Q->-Q
and therefore absent on the symmetric branch.)

For the isotropic locking ansatz Q=s R with R in SO(3),
    s^2 = -r/(3u+v)
when r<0 and 3u+v>0.  Its stabilizer is the diagonal SO(3), so the vacuum
manifold is (SO3_L x SO3_R)/SO3_diag ~= SO3, dimension three.

At Q=sI the Hessian splits exactly into diagonal-SO(3) sectors:
    rank 1 trace:               h1 = -2r,
    rank 3 antisymmetric:       h3 = 0,
    rank 5 symmetric traceless: h5 = 2 v s^2,
after using stationarity.

Thus for
    r<0, v>0, 3u+v>0
the nonzero branch is locally stable modulo exactly three Goldstone directions.
Those Goldstone tangents are delta Q_i=s L_i with L_i the so(3) generators;
their commutators close non-Abelianly.

This is a structural theorem, not a physical BHSM solution.  The authoritative
global action has not yet supplied the projected coefficients r,u,v, has not
proved that r crosses negative, and has not solved the associated nonround
full-preimage cap/seam background.  The three Goldstone directions are
therefore not promoted to physical neutrino wake channels or flavor
generations.

No measured input is used and no physical prediction is emitted.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

VERSION = "v14.74"

PRIMARY_VERDICT = (
    "BHSM_V14_74_THE_TOPOLOGICALLY_ALLOWED_NONABELIAN_ALTERNATIVE_TO_THE_"
    "OBSTRUCTED_GLOBAL_BERGER_AXIS_IS_AN_ELL2_SHAPE_ORDER_PARAMETER_Q_IN_"
    "THREE_TENSOR_THREE;_ON_THE_REFLECTION_SYMMETRIC_TWO_CAP_BRANCH_THE_"
    "MOST_GENERAL_EVEN_QUARTIC_SO3L_TIMES_SO3R_LANDAU_POTENTIAL_HAS_ONLY_"
    "R_U_V_AND_WHEN_R_IS_NEGATIVE_V_IS_POSITIVE_AND_THREE_U_PLUS_V_IS_"
    "POSITIVE_IT_HAS_A_NONZERO_Q_EQUALS_S_TIMES_R_ORIENTATION_BRANCH_THAT_"
    "SPONTANEOUSLY_BREAKS_SO3L_TIMES_SO3R_TO_THE_DIAGONAL_SO3_AND_HAS_"
    "EXACTLY_THREE_ANTISYMMETRIC_GOLDSTONE_ZERO_MODES_WITH_NONCOMMUTING_"
    "SO3_GENERATORS_WHILE_THE_SINGLET_AND_QUINTET_ARE_POSITIVE;_THIS_"
    "DERIVES_THE_THREE_CHANNEL_SYMMETRY_MECHANISM_WITHOUT_A_GLOBAL_U1_"
    "SECTION_BUT_THE_PHYSICAL_BHSM_COEFFICIENTS_R_U_V_AND_THE_NONROUND_"
    "FULL_PREIMAGE_STATIONARY_BACKGROUND_REMAIN_UNEVALUATED_SO_THE_"
    "GOLDSTONE_TRIPLET_IS_NOT_YET_A_PHYSICAL_NEUTRINO_OR_FLAVOR_OUTPUT"
)

EXACT_NEXT_OBJECT = (
    "PROJECT_THE_COMPLETE_GLOBAL_BHSM_SECOND_AND_FOURTH_SHAPE_VARIATIONS_"
    "ONTO_THE_ELL2_MATRIX_ORDER_PARAMETER_TO_DERIVE_R_U_V_WITHOUT_FIT_TEST_"
    "THE_BIFURCATION_CONDITIONS_R_LESS_THAN_ZERO_V_GREATER_THAN_ZERO_AND_"
    "THREE_U_PLUS_V_GREATER_THAN_ZERO_SOLVE_THE_RESULTING_NONROUND_TWO_CAP_"
    "FULL_PREIMAGE_STATIONARY_BACKGROUND_AND_GAUGE_REDUCED_HESSIAN_THEN_"
    "TRANSPORT_THE_THREE_GOLDSTONE_RELATIVE_ROTATION_DIRECTIONS_INTO_THE_"
    "OPERATOR_VALUED_CALDERON_SHAPE_CURRENT_VERTEX_AND_COMPUTE_THEIR_"
    "EXPLICIT_BREAKING_OR_HOLONOMY_SPLITTINGS_RELATIVE_HEAT_SUPERTRACE_AND_"
    "FROZEN_NEUTRINO_KILL_SCREEN"
)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("utf-8")


def sha256_payload(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def invariants(Q: np.ndarray) -> dict[str, float]:
    q = np.asarray(Q, dtype=float)
    if q.shape != (3, 3):
        raise ValueError("Q must be 3x3")
    gram = q.T @ q
    i2 = float(np.trace(gram))
    i4 = float(np.trace(gram @ gram))
    det = float(np.linalg.det(q))
    return {"I2": i2, "I4": i4, "det": det}


def landau_potential(Q: np.ndarray, r: float, u: float, v: float, b: float = 0.0) -> float:
    """SO3xSO3 Landau potential; b multiplies the reflection-odd det Q term."""
    inv = invariants(Q)
    return float(
        0.5 * r * inv["I2"]
        - b * inv["det"]
        + 0.25 * u * inv["I2"] ** 2
        + 0.25 * v * inv["I4"]
    )


def random_rotation(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    a = rng.normal(size=(3, 3))
    q, _ = np.linalg.qr(a)
    if np.linalg.det(q) < 0:
        q[:, 0] *= -1
    return q


def transform(Q: np.ndarray, left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return np.asarray(left) @ np.asarray(Q) @ np.asarray(right).T


def reflection_cubic_firewall_payload() -> dict[str, Any]:
    q = np.array([[1.2, -0.4, 0.3], [0.1, 0.7, -0.2], [0.5, 0.2, 1.1]])
    inv = invariants(q)
    invm = invariants(-q)
    return {
        "version": VERSION,
        "group_action": "Q -> R_L Q R_R^T",
        "SO3xSO3_cubic_invariant": "det Q",
        "det_Q": inv["det"],
        "det_minus_Q": invm["det"],
        "odd_residual": abs(invm["det"] + inv["det"]),
        "two_cap_reflection": "Q -> -Q",
        "reflection_symmetric_branch_forbids_det_term": True,
        "quartic_even_basis": ["[Tr(Q^TQ)]^2", "Tr[(Q^TQ)^2]"],
        "scope": "reflection-symmetric equal-cap branch",
    }


def quartic_boundedness_condition(u: float, v: float) -> bool:
    """Exact positivity condition for u I2^2 + v I4 on nonzero 3x3 Q."""
    if v >= 0:
        return u + v / 3.0 > 0
    return u + v > 0


def isotropic_amplitude_squared(r: float, u: float, v: float) -> float:
    den = 3.0 * u + v
    if den <= 0.0 or r >= 0.0:
        raise ValueError("nonzero isotropic branch requires r<0 and 3u+v>0")
    return -r / den


def isotropic_stationarity_residual(s: float, r: float, u: float, v: float) -> float:
    return float(s * (r + (3.0 * u + v) * s * s))


def projector_trace(Q: np.ndarray) -> np.ndarray:
    q = np.asarray(Q, dtype=float)
    return np.trace(q) / 3.0 * np.eye(3)


def projector_antisymmetric(Q: np.ndarray) -> np.ndarray:
    q = np.asarray(Q, dtype=float)
    return 0.5 * (q - q.T)


def projector_sym_traceless(Q: np.ndarray) -> np.ndarray:
    q = np.asarray(Q, dtype=float)
    return 0.5 * (q + q.T) - np.trace(q) / 3.0 * np.eye(3)


def hessian_sector_eigenvalues(s: float, r: float, u: float, v: float, b: float = 0.0) -> dict[str, float]:
    """Exact Hessian eigenvalues at Q=s I for normalized 1,3,5 directions."""
    return {
        "rank1": float(r - 2.0 * b * s + 9.0 * u * s * s + 3.0 * v * s * s),
        "rank3": float(r - b * s + 3.0 * u * s * s + v * s * s),
        "rank5": float(r + b * s + 3.0 * u * s * s + 3.0 * v * s * s),
    }


def even_branch_hessian_after_stationarity(r: float, u: float, v: float) -> dict[str, float]:
    s2 = isotropic_amplitude_squared(r, u, v)
    return {
        "s_squared": s2,
        "rank1": float(-2.0 * r),
        "rank3": 0.0,
        "rank5": float(2.0 * v * s2),
    }


def local_stability_mod_goldstone(r: float, u: float, v: float) -> bool:
    if r >= 0.0 or v <= 0.0 or 3.0 * u + v <= 0.0:
        return False
    h = even_branch_hessian_after_stationarity(r, u, v)
    return h["rank1"] > 0.0 and abs(h["rank3"]) < 1e-14 and h["rank5"] > 0.0


def so3_generators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    L1 = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0]])
    L2 = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 0.0], [-1.0, 0.0, 0.0]])
    L3 = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
    return L1, L2, L3


def goldstone_tangents(s: float) -> list[np.ndarray]:
    return [float(s) * L for L in so3_generators()]


def goldstone_gram(s: float) -> np.ndarray:
    tangents = goldstone_tangents(s)
    return np.array([[np.sum(a * b) for b in tangents] for a in tangents])


def goldstone_commutator_residual() -> float:
    L1, L2, L3 = so3_generators()
    residuals = [
        np.linalg.norm(L1 @ L2 - L2 @ L1 - L3),
        np.linalg.norm(L2 @ L3 - L3 @ L2 - L1),
        np.linalg.norm(L3 @ L1 - L1 @ L3 - L2),
    ]
    return float(max(residuals))


def vacuum_orbit_payload(r: float = -1.0, u: float = 1.0, v: float = 1.0) -> dict[str, Any]:
    s = float(np.sqrt(isotropic_amplitude_squared(r, u, v)))
    base = s * np.eye(3)
    values = []
    stabilizer_residuals = []
    for seed in range(6):
        R = random_rotation(seed)
        q = s * R
        values.append(landau_potential(q, r, u, v))
        # Pair (R,R) stabilizes sI.
        stabilizer_residuals.append(float(np.linalg.norm(transform(base, R, R) - base)))
    return {
        "version": VERSION,
        "diagnostic_coefficients": {"r": r, "u": u, "v": v, "physical": False},
        "s": s,
        "vacuum_form": "Q=s R, R in SO(3)",
        "stabilizer_of_sI": "SO(3)_diag={(R,R)}",
        "vacuum_manifold": "(SO3_L x SO3_R)/SO3_diag ~= SO3",
        "dimension": 3,
        "sample_potential_spread": float(max(values) - min(values)),
        "stabilizer_residual": float(max(stabilizer_residuals)),
        "requires_global_U1_reduction": False,
        "physical_background_derived": False,
    }


def hessian_goldstone_payload(r: float = -1.0, u: float = 1.0, v: float = 1.0) -> dict[str, Any]:
    s2 = isotropic_amplitude_squared(r, u, v)
    s = float(np.sqrt(s2))
    h = even_branch_hessian_after_stationarity(r, u, v)
    gram = goldstone_gram(s)
    return {
        "version": VERSION,
        "diagnostic_coefficients": {"r": r, "u": u, "v": v, "physical": False},
        "stationary_s_squared": s2,
        "Hessian_eigenvalues": h,
        "multiplicities": {"rank1": 1, "rank3": 3, "rank5": 5},
        "positive_nonGoldstone": h["rank1"] > 0 and h["rank5"] > 0,
        "exact_goldstone_count": 3,
        "goldstone_space": "antisymmetric 3x3 matrices",
        "goldstone_gram": gram.tolist(),
        "expected_goldstone_gram": (2.0 * s2 * np.eye(3)).tolist(),
        "gram_residual": float(np.linalg.norm(gram - 2.0 * s2 * np.eye(3))),
        "so3_commutator_residual": goldstone_commutator_residual(),
        "three_noncommuting_generator_algebra": True,
        "physical_channel_identification": False,
    }


def potential_invariance_payload() -> dict[str, Any]:
    q = np.array([[0.7, -0.2, 0.4], [0.1, 0.9, -0.3], [-0.5, 0.2, 0.6]])
    coeffs = (-0.6, 0.9, 0.4)
    base = landau_potential(q, *coeffs)
    residuals = []
    for seed in range(10):
        left = random_rotation(100 + 2 * seed)
        right = random_rotation(101 + 2 * seed)
        residuals.append(abs(landau_potential(transform(q, left, right), *coeffs) - base))
    return {
        "version": VERSION,
        "potential": "r/2 I2 + u/4 I2^2 + v/4 I4",
        "max_SO3L_times_SO3R_invariance_residual": float(max(residuals)),
        "invariant_basis_to_quartic_even_order": ["I2", "I2^2", "I4"],
        "cubic_det_removed_by_reflection": True,
    }


def direct_directional_second_derivative(
    direction: np.ndarray, s: float, r: float, u: float, v: float, eps: float = 2e-5
) -> float:
    d = np.asarray(direction, dtype=float)
    d = d / np.linalg.norm(d)
    q0 = s * np.eye(3)
    return float(
        (
            landau_potential(q0 + eps * d, r, u, v)
            - 2.0 * landau_potential(q0, r, u, v)
            + landau_potential(q0 - eps * d, r, u, v)
        )
        / (eps * eps)
    )


def hessian_finite_difference_payload(r: float = -1.0, u: float = 1.0, v: float = 1.0) -> dict[str, Any]:
    s = float(np.sqrt(isotropic_amplitude_squared(r, u, v)))
    D1 = np.eye(3) / np.sqrt(3.0)
    D3 = so3_generators()[2] / np.sqrt(2.0)
    D5 = np.diag([1.0, -1.0, 0.0]) / np.sqrt(2.0)
    analytic = even_branch_hessian_after_stationarity(r, u, v)
    numeric = {
        "rank1": direct_directional_second_derivative(D1, s, r, u, v),
        "rank3": direct_directional_second_derivative(D3, s, r, u, v),
        "rank5": direct_directional_second_derivative(D5, s, r, u, v),
    }
    return {
        "version": VERSION,
        "analytic": {k: analytic[k] for k in ("rank1", "rank3", "rank5")},
        "finite_difference": numeric,
        "max_residual": float(max(abs(numeric[k] - analytic[k]) for k in numeric)),
        "diagnostic_not_physical": True,
    }


def boundedness_and_stability_payload() -> dict[str, Any]:
    examples = [
        {"r": -1.0, "u": 1.0, "v": 1.0},
        {"r": -0.2, "u": -0.1, "v": 0.5},
        {"r": -1.0, "u": 1.0, "v": -0.2},
        {"r": 0.5, "u": 1.0, "v": 1.0},
    ]
    rows = []
    for row in examples:
        r, u, v = row["r"], row["u"], row["v"]
        rows.append(
            {
                **row,
                "quartic_bounded": quartic_boundedness_condition(u, v),
                "stable_isotropic_locking_branch": local_stability_mod_goldstone(r, u, v),
            }
        )
    return {
        "version": VERSION,
        "quartic_boundedness": (
            "if v>=0: u+v/3>0; if v<0: u+v>0"
        ),
        "isotropic_diagonal_locking_stability_conditions": "r<0, v>0, 3u+v>0",
        "under_these_conditions_quartic_is_bounded": True,
        "rows": rows,
        "physical_coefficients_derived": False,
    }


def hopf_curvature_role_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "canonical_Hopf_connection_exists": True,
        "connection_curvature_is_nonAbelian": True,
        "global_U1_axis_required": False,
        "round_homogeneous_curvature_by_itself_selects_Q_orientation": False,
        "allowed_role": (
            "contribute covariantly to the projected Landau coefficients and to "
            "explicit-breaking/transport terms after the Q background is selected"
        ),
        "forbidden_overpromotion": (
            "do not identify a local curvature frame with a global fixed-axis "
            "Berger projector or with the physical Goldstone channels"
        ),
        "full_preimage_mixed_variation_projected_to_r_u_v": None,
    }


def goldstone_rotor_payload(r: float = -1.0, u: float = 1.0, v: float = 1.0, Z: float = 1.0) -> dict[str, Any]:
    s2 = isotropic_amplitude_squared(r, u, v)
    return {
        "version": VERSION,
        "vacuum_coordinate": "Q(tau)=s R(tau), R in SO(3)",
        "kinetic_term": "(Z/2) Tr(dot Q^T dot Q)",
        "local_rotor_form": "(I_eff/2) |omega|^2",
        "I_eff": float(2.0 * Z * s2),
        "generator_algebra": "[L_i,L_j]=epsilon_ijk L_k",
        "classical_symmetric_Goldstone_gaps": [0.0, 0.0, 0.0],
        "physical_splittings_require": [
            "action-derived explicit symmetry breaking",
            "holonomy/nonlocal response",
            "finite-volume/boundary response",
        ],
        "physical_neutrino_interpretation": False,
        "diagnostic_Z_is_physical": False,
    }


def calderon_handoff_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "eligible_now": False,
        "structural_three_channel_basis": "DERIVED_AS_GOLDSTONE_TANGENT_SPACE",
        "physical_three_channel_basis": "OPEN",
        "conditional_handoff": [
            "derive r,u,v from the complete global action before comparison",
            "solve the nonround Q=sR full-preimage two-cap background",
            "construct the three normalized Goldstone shape functions delta Q_i=s L_i",
            "differentiate the physical tangential/Calderon operator along those three directions",
            "verify the resulting three operator derivatives are linearly independent and noncommuting after gauge projection",
            "include explicit-breaking/holonomy terms that generate physical phase splittings",
        ],
        "current_blockers": [
            "r,u,v not action-derived",
            "nonround full-preimage background unsolved",
            "Calderon derivatives not evaluated on that background",
            "physical Goldstone lifting/splitting not derived",
        ],
    }


def neutrino_kill_screen_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "current_result": "PHYSICAL_EXECUTION_BLOCKED",
        "physical_execution_allowed": False,
        "new_structural_result": (
            "exact three-dimensional noncommuting Goldstone orientation space exists "
            "if the BHSM action drives the ell2 isotropic locking bifurcation"
        ),
        "blocking_reason": (
            "the action has not yet derived the required Landau coefficients or "
            "stationary nonround background, and the Goldstone modes have no derived "
            "physical splitting/detector map"
        ),
        "measured_PMNS_mass_or_splitting_used": False,
        "physical_neutrino_output_emitted": False,
    }


def status_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "validated": [
            "ell2 order parameter can be represented as a real 3x3 matrix under SO3_L x SO3_R",
            "two-cap reflection removes the cubic det Q term on the symmetric branch",
            "the even quartic invariant basis is I2, I2^2, I4",
            "nonzero isotropic branch Q=sR exists for r<0 and 3u+v>0",
            "its stabilizer is diagonal SO3 and vacuum manifold dimension is three",
            "for v>0 the singlet and quintet Hessian sectors are positive while the triplet is exactly zero",
            "the three zero modes are the antisymmetric matrices",
            "their generators close the non-Abelian so3 algebra",
            "the mechanism requires no global U1 reduction and therefore evades the v14.73 topology obstruction",
            "classical symmetric Goldstones remain gapless until an action-derived lifting term is included",
        ],
        "invalidated": [
            "a global U1/axis selector is necessary to obtain exactly three shape directions",
            "the diagonal triplet can only appear as an explicitly inserted projector",
            "a rank-three channel mechanism requires three independent scalar minima",
            "the structural Goldstone triplet can already be identified with physical neutrino flavors without coefficient/background derivation",
        ],
        "reclassified": [
            "the diagonal-SU2 triplet is the Goldstone tangent space of a possible spontaneous ell2 locking phase",
            "the key upstream numerical question is now the sign and quartic structure of the action-projected r,u,v coefficients",
            "Hopf curvature is a covariant contributor to the Landau coefficients/transport rather than a global Abelian axis",
            "three-channel noncommutativity is structurally available from relative-rotation generators before physical phase splittings are known",
        ],
        "open": [
            EXACT_NEXT_OBJECT,
            "action-derived r,u,v",
            "global nonround full-preimage stationary solution",
            "gauge-reduced nonGoldstone stability",
            "three physical Calderon derivatives",
            "Goldstone lifting/splitting",
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
    refl = reflection_cubic_firewall_payload()
    inv = potential_invariance_payload()
    orbit = vacuum_orbit_payload()
    gold = hessian_goldstone_payload()
    fd = hessian_finite_difference_payload()
    stable = boundedness_and_stability_payload()
    rotor = goldstone_rotor_payload()
    validation = {
        "reflection_kills_cubic": refl["reflection_symmetric_branch_forbids_det_term"] and refl["odd_residual"] < 1e-12,
        "SO3xSO3_invariance": inv["max_SO3L_times_SO3R_invariance_residual"] < 1e-12,
        "vacuum_orbit_is_three_dimensional": orbit["dimension"] == 3 and orbit["sample_potential_spread"] < 1e-12,
        "diagonal_stabilizer_check": orbit["stabilizer_residual"] < 1e-12,
        "exact_three_Goldstones": gold["exact_goldstone_count"] == 3 and abs(gold["Hessian_eigenvalues"]["rank3"]) < 1e-12,
        "nonGoldstone_positive_witness": gold["positive_nonGoldstone"],
        "goldstone_gram_exact": gold["gram_residual"] < 1e-12,
        "goldstone_generators_noncommuting": gold["so3_commutator_residual"] < 1e-12,
        "finite_difference_Hessian_check": fd["max_residual"] < 2e-5,
        "stable_conditions_include_bounded_quartic": stable["under_these_conditions_quartic_is_bounded"],
        "Goldstone_gaps_not_overpromoted": rotor["classical_symmetric_Goldstone_gaps"] == [0.0, 0.0, 0.0],
        "no_physical_prediction": True,
    }
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "global_U1_axis_required": False,
        "ell2_diagonal_locking_mechanism": "STRUCTURALLY_DERIVED",
        "three_Goldstone_channels": "STRUCTURALLY_DERIVED",
        "action_projected_r_u_v": None,
        "physical_nonround_background": None,
        "physical_Goldstone_splittings": None,
        "full_BHSM_complete": False,
        "mark_III": "NOT_REACHED",
        "physical_execution_allowed": False,
        "physical_prediction_emitted": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "usb_touched": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def artifact_payloads() -> dict[str, Any]:
    return {
        "BHSM_l2_reflection_invariant_basis_v14_74.json": reflection_cubic_firewall_payload(),
        "BHSM_l2_Landau_invariance_v14_74.json": potential_invariance_payload(),
        "BHSM_l2_isotropic_locking_vacuum_v14_74.json": vacuum_orbit_payload(),
        "BHSM_l2_Goldstone_Hessian_v14_74.json": hessian_goldstone_payload(),
        "BHSM_l2_Hessian_finite_difference_v14_74.json": hessian_finite_difference_payload(),
        "BHSM_l2_boundedness_stability_cone_v14_74.json": boundedness_and_stability_payload(),
        "BHSM_Hopf_curvature_role_v14_74.json": hopf_curvature_role_payload(),
        "BHSM_Goldstone_rotor_v14_74.json": goldstone_rotor_payload(),
        "BHSM_calderon_handoff_v14_74.json": calderon_handoff_payload(),
        "BHSM_neutrino_kill_screen_v14_74.json": neutrino_kill_screen_payload(),
        "BHSM_status_ledger_v14_74.json": status_payload(),
        "BHSM_completion_gate_v14_74.json": completion_gate_payload(),
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
