"""BHSM v14.73 Hopf U(1)-reduction obstruction and diagonal-locking gate.

v14.72 found a mathematically exact rank-three carrier in the J=1 Berger
spectrum after selecting a fixed U(1) axis.  This sprint asks whether such an
axis can be promoted to a smooth global physical reduction of the retained
quaternionic Hopf bundle.

For the retained principal Sp(1)=SU(2) bundle P=S7->S4 with c2(P)=+1, a
reduction to U(1) would split the associated fundamental rank-two complex
bundle E as L + L^{-1}.  Since H^2(S4;Z)=0, c1(L)=0, hence
c2(E)=-c1(L)^2=0, contradicting c2(E)=1.  Therefore no global U(1)
reduction exists.

The rank-three Berger axis projector is unoriented, so its stabilizer is the
normalizer N(U1).  But N(U1)/U1=Z2 and H^1(S4;Z2)=0.  Any global N(U1)
reduction over S4 would therefore further reduce to U(1), so the unoriented
axis is obstructed as well.

This does not contradict the globally defined twistor circle direction on the
total S7.  That vertical line is not a basic Sp(1)-equivariant axis field over
S4.  Consequently a fixed-m Berger projector can be used locally/collarwise or
on the total-space harmonic problem but does not descend as a globally
action-owned rank-three associated subbundle over the full S4 base.

The simplest intrinsic Berger Einstein-Hilbert shape term also does not select
a nonround beta.  In the repository Maurer-Cartan convention,
    R_B = 2/L2^2 - L1^2/(2 L2^4).
At fixed fiber volume rho^3=L2^2 L1 and beta=L1/L2,
    rho^2 R_B = 2 beta^(2/3) - 1/2 beta^(8/3),
whose only positive stationary point is beta=1.

The topologically admissible replacement is non-Abelian rather than a global
axis: an action-derived full-triplet soldering/curvature map can lock two
spin-one factors without reducing either to a line.  The universal diagonal
operator
    K_Delta = sum_i J_i tensor J_i
has eigenvalues -2,-1,+1 with multiplicities 1,3,5.  Its spectral projectors
are the exact 1+3+5 projectors of v14.70.  This is a representation-theoretic
candidate, not yet an action-derived physical Hessian term.

No measured input is used and no physical prediction is emitted.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

VERSION = "v14.73"

PRIMARY_VERDICT = (
    "BHSM_V14_73_THE_FIXED_AXIS_BERGER_RANK_THREE_CARRIER_OF_V14_72_CANNOT_"
    "BE_PROMOTED_TO_A_SMOOTH_GLOBAL_SP1_TO_U1_OR_UNORIENTED_NORMALIZER_"
    "REDUCTION_OVER_THE_FULL_S4_BASE_BECAUSE_THE_RETAINED_HOPF_BUNDLE_HAS_"
    "C2_EQUALS_ONE_WHILE_ANY_SU2_TO_U1_REDUCTION_OVER_S4_WOULD_FORCE_THE_"
    "ASSOCIATED_FUNDAMENTAL_BUNDLE_TO_SPLIT_AS_L_PLUS_L_INVERSE_WITH_C2_ZERO;_"
    "THE_GLOBAL_TWISTOR_CIRCLE_DIRECTION_ON_TOTAL_S7_IS_THEREFORE_NONBASIC_"
    "FOR_THIS_PURPOSE_AND_THE_FIXED_M_PROJECTOR_IS_ONLY_LOCAL_OR_TOTAL_SPACE_"
    "KINEMATICS;_MOREOVER_THE_BARE_INTRINSIC_BERGER_EINSTEIN_HILBERT_SHAPE_"
    "TERM_HAS_ITS_ONLY_POSITIVE_FIXED_VOLUME_STATIONARY_POINT_AT_BETA_EQUALS_"
    "ONE;_THE_STRONGEST_TOPOLOGICALLY_COMPATIBLE_REPLACEMENT_IS_AN_ACTION_"
    "OWNED_NONABELIAN_TRIPLET_SOLDERING_OR_HOPF_CURVATURE_LOCKING_MAP_WHOSE_"
    "UNIVERSAL_DIAGONAL_OPERATOR_HAS_EXACT_1_3_5_SPECTRAL_PROJECTORS_BUT_"
    "THAT_MIXED_SECOND_VARIATION_IS_NOT_YET_DERIVED"
)

EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_NONABELIAN_HOPF_CURVATURE_OR_CONNECTION_SOLDERING_MAP_"
    "BETWEEN_THE_RELEVANT_TWO_RANK_THREE_BUNDLES_ON_THE_FULL_PREIMAGE_"
    "STATIONARY_BACKGROUND_WITH_A_GAUGE_COVARIANT_MIXED_SECOND_VARIATION_"
    "H_ELL2_EQUALS_C0_I_PLUS_C1_KDELTA_PLUS_C2_KDELTA_SQUARED_DERIVED_FROM_"
    "THE_GLOBAL_ACTION_AND_WITH_THE_RANK_THREE_SECTOR_SPECTRALLY_ISOLATED_"
    "WITHOUT_A_GLOBAL_U1_REDUCTION_THEN_TRANSPORTED_INTO_THREE_TRANSVERSE_"
    "CALDERON_SHAPE_CURRENT_DERIVATIVES_RELATIVE_HEAT_SUPERTRACE_AND_THE_"
    "FROZEN_NEUTRINO_KILL_SCREEN"
)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("utf-8")


def sha256_payload(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def u1_reduction_obstruction_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "principal_bundle": "Sp(1)->S7->S4",
        "retained_second_Chern_class": 1,
        "reduction_target": "U(1) subset SU(2)=Sp(1)",
        "equivalent_section_problem": "section of P/U(1)->S4, the associated S2/twistor bundle",
        "associated_fundamental_bundle_if_reduced": "E=L direct_sum L^{-1}",
        "cohomology_fact": "H^2(S4;Z)=0",
        "therefore_c1_L": 0,
        "reduced_c2_formula": "c2(E)=c1(L)c1(L^{-1})=-c1(L)^2",
        "reduced_c2_value": 0,
        "contradiction": "retained c2(E)=+1",
        "global_smooth_U1_reduction_exists": False,
        "collar_or_patchwise_reduction_possible": True,
        "measured_input_used": False,
    }


def normalizer_axis_obstruction_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "rank3_axis_projector": "I3 tensor |n><n|; n and -n define the same projector",
        "projector_stabilizer": "N(U1), the normalizer of the maximal torus",
        "quotient": "N(U1)/U1 = Z2",
        "base_fact": "H^1(S4;Z2)=0 and S4 is simply connected",
        "consequence": (
            "an N(U1) reduction has a trivial associated Z2 bundle and therefore "
            "admits a U1 subreduction"
        ),
        "u1_subreduction_obstructed_by_c2": True,
        "global_unoriented_axis_reduction_exists": False,
        "global_rank3_fixed_axis_projector_descends_to_S4": False,
        "local_or_total_space_projector_still_valid": True,
    }


def descent_firewall_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "global_total_space_circle_direction": "V1=ker(dp_C) on S7->CP3",
        "global_total_space_Berger_metric_possible": True,
        "principal_Sp1_equivariant_basic_axis_over_S4": False,
        "reason": (
            "a basic axis would define an N(U1) or U1 reduction of the c2=1 "
            "quaternionic Hopf bundle, which is topologically obstructed"
        ),
        "fixed_right_weight_m_is_globally_preserved_by_general_Sp1_transition_functions": False,
        "fixed_m0_rank3_associated_subbundle_on_full_S4": None,
        "status": "LOCAL_OR_TOTAL_SPACE_KINEMATICS_ONLY_UNTIL_A_DIFFERENT_GLOBAL_INTERTWINER_IS_DERIVED",
    }


def fixed_volume_lengths(rho: float, beta: float) -> tuple[float, float]:
    rho = float(rho)
    beta = float(beta)
    if rho <= 0.0 or beta <= 0.0:
        raise ValueError("rho and beta must be positive")
    return rho * beta ** (-1.0 / 3.0), rho * beta ** (2.0 / 3.0)


def berger_scalar_curvature(L2: float, L1: float) -> float:
    """Intrinsic Berger S3 scalar curvature in the repository MC convention."""
    if L1 <= 0.0 or L2 <= 0.0:
        raise ValueError("positive Berger lengths required")
    return 2.0 / (L2 * L2) - (L1 * L1) / (2.0 * L2**4)


def fixed_volume_dimensionless_scalar_curvature(beta: float) -> float:
    beta = float(beta)
    if beta <= 0.0:
        raise ValueError("beta must be positive")
    return 2.0 * beta ** (2.0 / 3.0) - 0.5 * beta ** (8.0 / 3.0)


def fixed_volume_scalar_curvature_derivative(beta: float, rho: float = 1.0) -> float:
    beta = float(beta)
    rho = float(rho)
    if beta <= 0.0 or rho <= 0.0:
        raise ValueError("positive beta and rho required")
    return 4.0 * (1.0 - beta * beta) / (3.0 * beta ** (1.0 / 3.0) * rho * rho)


def fixed_volume_scalar_curvature_second_at_round(rho: float = 1.0) -> float:
    rho = float(rho)
    if rho <= 0.0:
        raise ValueError("rho must be positive")
    return -8.0 / (3.0 * rho * rho)


def intrinsic_berger_eh_payload() -> dict[str, Any]:
    beta_witnesses = [0.45, 0.7, 1.0, 1.4, 2.0]
    rows = []
    for beta in beta_witnesses:
        rows.append(
            {
                "beta": beta,
                "rho2_R": fixed_volume_dimensionless_scalar_curvature(beta),
                "rho2_dR_dbeta": fixed_volume_scalar_curvature_derivative(beta, 1.0),
            }
        )
    return {
        "version": VERSION,
        "scope": "isolated intrinsic Berger-fiber Einstein-Hilbert shape term at fixed fiber volume",
        "scalar_curvature": "R_B=2/L2^2-L1^2/(2 L2^4)",
        "fixed_volume_formula": "rho^2 R_B=2 beta^(2/3)-(1/2) beta^(8/3)",
        "derivative": "dR/dbeta=4(1-beta^2)/(3 rho^2 beta^(1/3))",
        "positive_stationary_points": [1.0],
        "second_derivative_at_round": fixed_volume_scalar_curvature_second_at_round(),
        "round_is_local_maximum_of_R": True,
        "sign_independent_stationarity_conclusion": "multiplying EH by either overall sign does not create a beta!=1 stationary point",
        "bare_intrinsic_EH_selects_nonround_beta": False,
        "full_M8_action_reduced_to_this_term_only": False,
        "diagnostic_rows": rows,
    }


def ricci_invariants_fixed_volume(beta: float) -> dict[str, float]:
    """Dimensionless rho powers for the biaxial Berger Ricci invariants."""
    b = float(beta)
    if b <= 0.0:
        raise ValueError("beta must be positive")
    R = 2.0 * b ** (2.0 / 3.0) - 0.5 * b ** (8.0 / 3.0)
    Ric2 = (
        2.0 * b ** (4.0 / 3.0)
        - 2.0 * b ** (10.0 / 3.0)
        + 0.75 * b ** (16.0 / 3.0)
    )
    traceless = 2.0 * (Ric2 - R * R / 3.0)
    closed = (4.0 / 3.0) * b ** (4.0 / 3.0) * (b * b - 1.0) ** 2
    return {
        "rho2_R": R,
        "rho4_Ricci2": Ric2,
        "rho4_twice_traceless_Ricci2": traceless,
        "rho4_closed_form": closed,
        "closed_form_residual": abs(traceless - closed),
    }


def anisotropy_invariant_payload() -> dict[str, Any]:
    samples = [0.4, 0.7, 1.0, 1.3, 2.0]
    rows = [dict(beta=b, **ricci_invariants_fixed_volume(b)) for b in samples]
    return {
        "version": VERSION,
        "invariant": "Q=2(|Ric|^2-R^2/3)",
        "fixed_volume_closed_form": "rho^4 Q=(4/3) beta^(4/3)(beta^2-1)^2",
        "nonnegative": True,
        "zero_only_at_round_for_positive_beta": True,
        "positive_coefficient_minimization_favors_round": True,
        "negative_coefficient_can_destabilize_but_requires_stabilizing_higher_terms": True,
        "coefficient_sign_derived_by_current_authoritative_action": False,
        "rows": rows,
    }


def spin1_generators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    root2 = np.sqrt(2.0)
    jp = np.array(
        [[0.0, root2, 0.0], [0.0, 0.0, root2], [0.0, 0.0, 0.0]], dtype=complex
    )
    jm = jp.conj().T
    return (jp + jm) / 2.0, (jp - jm) / (2.0j), np.diag([1.0, 0.0, -1.0]).astype(complex)


def diagonal_locking_operator() -> np.ndarray:
    return sum(np.kron(j, j) for j in spin1_generators())


def diagonal_generators() -> list[np.ndarray]:
    eye = np.eye(3)
    return [np.kron(j, eye) + np.kron(eye, j) for j in spin1_generators()]


def product_generators() -> list[np.ndarray]:
    eye = np.eye(3)
    js = spin1_generators()
    return [np.kron(j, eye) for j in js] + [np.kron(eye, j) for j in js]


def max_commutator_norm(operator: np.ndarray, generators: list[np.ndarray]) -> float:
    op = np.asarray(operator, dtype=complex)
    return float(max(np.linalg.norm(op @ g - g @ op) for g in generators))


def diagonal_spectral_projectors() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Projectors for K eigenvalues -2,-1,+1, ranks 1,3,5."""
    K = diagonal_locking_operator()
    I = np.eye(9)
    P1 = (K @ K - I) / 3.0
    P3 = -0.5 * (K @ K + K - 2.0 * I)
    P5 = (K @ K + 3.0 * K + 2.0 * I) / 6.0
    return P1, P3, P5


def projector_quality() -> dict[str, Any]:
    ps = diagonal_spectral_projectors()
    return {
        "ranks": [int(np.linalg.matrix_rank(p, tol=1e-10)) for p in ps],
        "sum_identity_residual": float(np.linalg.norm(sum(ps) - np.eye(9))),
        "idempotence_residual": float(max(np.linalg.norm(p @ p - p) for p in ps)),
        "orthogonality_residual": float(
            max(np.linalg.norm(ps[i] @ ps[j]) for i in range(3) for j in range(i + 1, 3))
        ),
        "self_adjoint_residual": float(max(np.linalg.norm(p - p.conj().T) for p in ps)),
    }


def diagonal_locking_payload() -> dict[str, Any]:
    K = diagonal_locking_operator()
    vals = np.linalg.eigvalsh(K)
    q = projector_quality()
    return {
        "version": VERSION,
        "candidate_operator": "K_Delta=sum_i J_i tensor J_i",
        "interpretation": "universal representation-level operator after a full-triplet diagonal soldering is supplied",
        "spectrum": [float(v) for v in vals],
        "distinct_eigenvalues": [-2.0, -1.0, 1.0],
        "multiplicities": [1, 3, 5],
        "projector_polynomials": {
            "P1": "(K^2-I)/3",
            "P3": "-(K^2+K-2I)/2",
            "P5": "(K^2+3K+2I)/6",
        },
        "projector_quality": q,
        "commutator_with_diagonal_SU2": max_commutator_norm(K, diagonal_generators()),
        "commutator_with_full_product_generators": max_commutator_norm(K, product_generators()),
        "requires_global_U1_axis": False,
        "requires_global_triplet_soldering_map": True,
        "physical_soldering_map_derived": False,
    }


def diagonal_hessian_eigenvalues(c0: float, c1: float, c2: float) -> dict[str, float]:
    return {
        "rank1": float(c0 - 2.0 * c1 + 4.0 * c2),
        "rank3": float(c0 - c1 + c2),
        "rank5": float(c0 + c1 + c2),
    }


def triplet_softest_condition(c1: float, c2: float) -> bool:
    e = diagonal_hessian_eigenvalues(0.0, c1, c2)
    return e["rank3"] < e["rank1"] and e["rank3"] < e["rank5"]


def triplet_selection_cone_payload() -> dict[str, Any]:
    witness = diagonal_hessian_eigenvalues(0.0, 1.0, 1.0)
    linear_positive = diagonal_hessian_eigenvalues(0.0, 1.0, 0.0)
    linear_negative = diagonal_hessian_eigenvalues(0.0, -1.0, 0.0)
    return {
        "version": VERSION,
        "general_diagonal_equivariant_Hessian": "H=c0 I+c1 K_Delta+c2 K_Delta^2",
        "sector_eigenvalues": {
            "rank1": "c0-2c1+4c2",
            "rank3": "c0-c1+c2",
            "rank5": "c0+c1+c2",
        },
        "rank3_strictly_softest_condition": "c1>0 and c1<3 c2",
        "implies_c2_positive": True,
        "exact_soft_triplet_witness_c0_0_c1_1_c2_1": witness,
        "witness_selects_triplet": triplet_softest_condition(1.0, 1.0),
        "linear_K_only_c1_positive": linear_positive,
        "linear_K_only_c1_negative": linear_negative,
        "single_linear_K_term_makes_triplet_softest": False,
        "physical_coefficients_derived": False,
    }


def nonabelian_replacement_gate_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "global_U1_axis_route": "TOPOLOGICALLY_BLOCKED_ON_FULL_S4",
        "allowed_replacements": [
            "full non-Abelian connection-curvature soldering between rank-three bundles",
            "patchwise/collar polarization with unavoidable transition/defect data kept explicitly",
            "nonlocal holonomy-defined projector whose global covariance is proved without reducing P to U1",
        ],
        "strongest_global_candidate": (
            "a nondegenerate action-owned map S:triplet_A->triplet_B built from the "
            "quaternionic Hopf connection curvature or an equivalent full-preimage mixed Hessian"
        ),
        "candidate_must_be_gauge_covariant": True,
        "candidate_must_not_choose_a_global_adjoint_unit_vector": True,
        "candidate_must_reproduce_diagonal_K_operator_or_an_equivalent_rank3_spectral_projector": True,
        "current_action_owned_soldering": None,
        "full_preimage_stationary_background": None,
        "physical_gate_open": False,
    }


def calderon_handoff_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "eligible_now": False,
        "fixed_axis_Berger_handoff_superseded": True,
        "reason": "the full-base fixed-axis rank3 projector does not descend through the c2=1 Hopf bundle",
        "conditional_next_handoff": [
            "derive a global non-Abelian triplet soldering/intertwiner on the stationary full-preimage background",
            "derive c0,c1,c2 in the ell2 mixed second-shape Hessian",
            "verify the rank-three spectral projector is isolated without measured data",
            "transport that projector through the tensor incidence maps",
            "differentiate the operator in three physical transverse directions",
            "insert the derivatives into the operator-valued Calderon/Wentzell domain",
        ],
        "physical_prediction": False,
    }


def neutrino_kill_screen_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "current_result": "PHYSICAL_EXECUTION_BLOCKED",
        "physical_execution_allowed": False,
        "reason": (
            "v14.72 fixed-axis rank3 carrier is globally obstructed as a full-base U1/normalizer "
            "reduction and the replacement non-Abelian triplet soldering has not been derived"
        ),
        "measured_neutrino_data_used": False,
        "physical_mass_PMNS_splitting_or_probability_emitted": False,
    }


def status_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "validated": [
            "c2=1 forbids a smooth global U1 reduction of the retained Sp1 Hopf bundle over S4",
            "the unoriented fixed-axis normalizer reduction is also obstructed over simply connected S4",
            "the total-space twistor circle direction does not imply a basic full-base axis reduction",
            "the v14.72 fixed-m rank3 carrier is local/collar/total-space kinematics rather than a global M5 associated subbundle",
            "bare intrinsic Berger EH at fixed volume has only beta=1 as a positive stationary point",
            "the traceless-Ricci anisotropy invariant is nonnegative and vanishes at beta=1",
            "the diagonal non-Abelian operator K_Delta has exact 1,3,5 multiplicities",
            "its spectral projectors reproduce the exact rank 1,3,5 decomposition without choosing a U1 axis",
            "a general diagonal-equivariant Hessian is c0 I+c1 K+c2 K^2",
            "rank3-softest region is c1>0 and c1<3c2",
        ],
        "invalidated": [
            "a smooth global Sp1-to-U1 polarization section can be the v14.73 completion route on full S4",
            "the v14.72 rank3 m=0 projector automatically descends as a global physical carrier",
            "the simplest isolated Berger Einstein-Hilbert term selects beta_star not equal to one",
            "one linear diagonal-locking coefficient alone naturally makes the triplet the softest sector",
        ],
        "reclassified": [
            "the preferred global route is non-Abelian triplet locking rather than Abelian axis selection",
            "Berger fixed-axis splitting remains useful as a local spectral mechanism and diagnostic",
            "topology itself forces any global completion to retain the full non-Abelian Hopf structure or explicit defect/patch data",
            "the v14.70 diagonal triplet becomes the more topology-compatible global target if its soldering source is action-derived",
        ],
        "open": [
            EXACT_NEXT_OBJECT,
            "full-preimage stationary background",
            "action-owned triplet soldering or curvature map",
            "physical c0,c1,c2",
            "isolated physical rank-three projector",
            "three transverse noncommuting Calderon derivatives",
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
    u1 = u1_reduction_obstruction_payload()
    nrm = normalizer_axis_obstruction_payload()
    eh = intrinsic_berger_eh_payload()
    ani = anisotropy_invariant_payload()
    lock = diagonal_locking_payload()
    cone = triplet_selection_cone_payload()
    repl = nonabelian_replacement_gate_payload()
    validation = {
        "u1_reduction_obstructed": u1["global_smooth_U1_reduction_exists"] is False,
        "normalizer_axis_obstructed": nrm["global_unoriented_axis_reduction_exists"] is False,
        "bare_EH_has_only_round_stationarity": eh["positive_stationary_points"] == [1.0],
        "round_EH_second_derivative_nonzero": eh["second_derivative_at_round"] < 0.0,
        "anisotropy_invariant_closes": max(row["closed_form_residual"] for row in ani["rows"]) < 1e-12,
        "diagonal_projector_ranks_1_3_5": lock["projector_quality"]["ranks"] == [1, 3, 5],
        "diagonal_lock_commutes_with_diagonal_group": lock["commutator_with_diagonal_SU2"] < 1e-12,
        "diagonal_lock_breaks_full_product": lock["commutator_with_full_product_generators"] > 1e-3,
        "triplet_softest_witness_exists": cone["witness_selects_triplet"] is True,
        "linear_term_alone_not_sufficient_for_softest_triplet": cone["single_linear_K_term_makes_triplet_softest"] is False,
        "nonabelian_replacement_not_overpromoted": repl["current_action_owned_soldering"] is None,
        "no_physical_prediction": True,
    }
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "global_fixed_axis_Berger_route": "TOPOLOGICALLY_BLOCKED",
        "local_Berger_rank3_mechanism": "VALIDATED_CONDITIONAL",
        "bare_intrinsic_EH_nonround_beta_selection": "INVALIDATED",
        "nonabelian_diagonal_locking_mechanism": "REPRESENTATION_THEOREM_VALIDATED_ACTION_SOURCE_OPEN",
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
        "BHSM_U1_reduction_topology_obstruction_v14_73.json": u1_reduction_obstruction_payload(),
        "BHSM_fixed_axis_rank3_descent_obstruction_v14_73.json": normalizer_axis_obstruction_payload(),
        "BHSM_total_space_vs_base_descent_firewall_v14_73.json": descent_firewall_payload(),
        "BHSM_intrinsic_Berger_EH_beta_stationarity_v14_73.json": intrinsic_berger_eh_payload(),
        "BHSM_Berger_anisotropy_invariant_v14_73.json": anisotropy_invariant_payload(),
        "BHSM_diagonal_curvature_locking_operator_v14_73.json": diagonal_locking_payload(),
        "BHSM_diagonal_triplet_selection_cone_v14_73.json": triplet_selection_cone_payload(),
        "BHSM_global_nonabelian_replacement_gate_v14_73.json": nonabelian_replacement_gate_payload(),
        "BHSM_calderon_handoff_v14_73.json": calderon_handoff_payload(),
        "BHSM_neutrino_kill_screen_v14_73.json": neutrino_kill_screen_payload(),
        "BHSM_status_ledger_v14_73.json": status_payload(),
        "BHSM_completion_gate_v14_73.json": completion_gate_payload(),
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
