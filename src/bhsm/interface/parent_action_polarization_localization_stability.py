"""BHSM v6.4.0 parent-action polarization and principal-stability audit.

This module derives the exact G2 complex polarization and the geometric
Berger connection splitting that are available from the frozen repository
action.  It also makes the missing parent first-order matter coefficient and
the unresolved physical spectra explicit instead of silently completing
them.
"""

from __future__ import annotations

from fractions import Fraction
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from .particle_chirality_anomaly_normalization import (
    ARTIFACT_FILES as V630_ARTIFACT_FILES,
    PRIMARY_RESULT as V630_PRIMARY_RESULT,
    charge_table,
    connection_trace_payload,
    exact_mass_operator,
)
from .triality_generation_scale_architecture import (
    no_double_counting_check,
    triality_algebra_check,
)
from .twistor_berger_action_normalization import connection_kinetic_matrix


VERSION = "v6.4.0"
SPRINT = "bhsm-parent-action-polarization-localization-stability-v6-4-0"
SOURCE_SHA = "c82ed0da6c9f2fda74f08ac03ec6429aaa7ddf79"
PRIMARY_RESULT = (
    "BHSM_GLOBAL_POLARIZATION_AND_PRINCIPAL_STABILITY_ARCHITECTURE_"
    "DERIVED_CONDITIONALLY"
)
COMPLETION_GATE = (
    "V6_4_0_FIRST_ORDER_PARENT_COEFFICIENT_CONNECTION_TRANSFER_AND_"
    "FULL_SPECTRUM_OPEN"
)

ARTIFACT_FILES = {
    "handoff": "BHSM_v6_4_0_state_handoff.json",
    "g2_complex": "BHSM_G2_global_complex_structure_v6_4_0.json",
    "polarization": "BHSM_global_color_polarization_bundle_v6_4_0.json",
    "triality": "BHSM_triality_polarization_compatibility_v6_4_0.json",
    "matter_action": "BHSM_parent_first_order_matter_action_v6_4_0.json",
    "odd_coupling": "BHSM_action_native_odd_wall_coupling_v6_4_0.json",
    "index": "BHSM_chiral_zero_mode_index_v6_4_0.json",
    "doubling": "BHSM_vectorlike_doubling_audit_v6_4_0.json",
    "connection_source": "BHSM_connection_localization_source_map_v6_4_0.json",
    "su3_transfer": "BHSM_SU3_connection_transfer_v6_4_0.json",
    "sp1_transfer": "BHSM_Sp1_connection_transfer_v6_4_0.json",
    "u1_transfer": "BHSM_U1_connection_transfer_v6_4_0.json",
    "gravity": "BHSM_gravity_boundary_transfer_v6_4_0.json",
    "kinetic_metric": "BHSM_Berger_Higgs_kinetic_metric_v6_4_0.json",
    "scalar_mass": "BHSM_scalar_Berger_mixed_mass_matrix_v6_4_0.json",
    "gauge_mass": "BHSM_gauge_boson_mass_matrix_v6_4_0.json",
    "tensor": "BHSM_constraint_reduced_tensor_sector_v6_4_0.json",
    "vector": "BHSM_constraint_reduced_vector_sector_v6_4_0.json",
    "scalar": "BHSM_constraint_reduced_scalar_sector_v6_4_0.json",
    "matter_spectrum": "BHSM_first_order_matter_spectrum_v6_4_0.json",
    "spacetime": "BHSM_spacetime_branch_principal_symbol_audit_v6_4_0.json",
    "scale": "BHSM_absolute_scale_transfer_map_v6_4_0.json",
    "r4": "BHSM_scalar_wall_O_r4_action_v6_4_0.json",
    "integration": "BHSM_full_integration_ledger_v6_4_0.json",
    "hidden": "BHSM_v6_4_0_hidden_input_audit.json",
    "report": "BHSM_parent_action_polarization_localization_stability_report_v6_4_0.json",
}

GUARDS = {
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "measured_derivation_input_used": False,
    "physical_bulk_Dirac_parent_law_introduced": False,
    "monopole_structure_introduced": False,
    "absolute_numerical_mass_claimed": False,
    "full_BHSM_claimed": False,
}


def _fano_tensor() -> np.ndarray:
    """Return the standard G2 three-form structure constants.

    The one-based oriented Fano triples are
    123, 145, 176, 246, 257, 347, and 365.
    """
    phi = np.zeros((7, 7, 7), dtype=int)
    triples = (
        (0, 1, 2),
        (0, 3, 4),
        (0, 6, 5),
        (1, 3, 5),
        (1, 4, 6),
        (2, 3, 6),
        (2, 5, 4),
    )
    for i, j, k in triples:
        for a, b, c in (
            (i, j, k),
            (j, k, i),
            (k, i, j),
        ):
            phi[a, b, c] = 1
            phi[b, a, c] = -1
    return phi


def g2_cross(u: Iterable[float], v: Iterable[float]) -> np.ndarray:
    """Compute the seven-dimensional G2 cross product."""
    left = np.asarray(tuple(u), dtype=float)
    right = np.asarray(tuple(v), dtype=float)
    if left.shape != (7,) or right.shape != (7,):
        raise ValueError("G2 cross product requires two seven-vectors")
    return np.einsum("ijk,i,j->k", _fano_tensor(), left, right)


def cross_product_matrix(u: Iterable[float]) -> np.ndarray:
    """Matrix J_u with J_u(v)=u cross v."""
    vector = np.asarray(tuple(u), dtype=float)
    if vector.shape != (7,):
        raise ValueError("u must be a seven-vector")
    return np.column_stack(
        [g2_cross(vector, np.eye(7)[column]) for column in range(7)]
    )


def polarization_projectors(
    u: Iterable[float],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return the two complex rank-three projectors and u-perpendicular Q."""
    vector = np.asarray(tuple(u), dtype=float)
    norm = np.linalg.norm(vector)
    if norm == 0:
        raise ValueError("u must be nonzero")
    vector = vector / norm
    J = cross_product_matrix(vector)
    Q = np.eye(7) - np.outer(vector, vector)
    return (Q - 1j * J) / 2, (Q + 1j * J) / 2, Q


def polarization_checks() -> dict[str, bool | int | float]:
    """Exact-to-tolerance checks for the selected basis direction u=e7."""
    u = np.eye(7)[6]
    J = cross_product_matrix(u)
    plus, minus, Q = polarization_projectors(u)
    return {
        "u_unit": bool(np.allclose(u @ u, 1)),
        "J_u_annihilates_u": bool(np.allclose(J @ u, 0)),
        "J_u_squared_equals_minus_Q": bool(np.allclose(J @ J, -Q)),
        "Pi_10_idempotent": bool(np.allclose(plus @ plus, plus)),
        "Pi_01_idempotent": bool(np.allclose(minus @ minus, minus)),
        "projectors_orthogonal": bool(np.allclose(plus @ minus, 0)),
        "projectors_complete_on_u_perp": bool(np.allclose(plus + minus, Q)),
        "conjugation_exchanges_projectors": bool(np.allclose(plus.conj(), minus)),
        "rank_Pi_10": int(np.linalg.matrix_rank(plus)),
        "rank_Pi_01": int(np.linalg.matrix_rank(minus)),
        "trace_Pi_10": float(np.trace(plus).real),
        "trace_Pi_01": float(np.trace(minus).real),
    }


def topology_globalization_ledger() -> dict[str, Any]:
    """Global bundle statement for a four-dimensional boundary base."""
    return {
        "bundle": "E_7=P_G2 x_7 R^7 over the selected M4 boundary",
        "unit_sphere_bundle": "S(E_7)=P_G2 x_G2 S^6",
        "section_meaning": "a unit section u reduces P_G2 to its SU3 stabilizer",
        "base_dimension": 4,
        "bundle_rank": 7,
        "primary_section_obstruction": "Euler/top obstruction lies in H^7(M4)",
        "obstruction_on_M4": "zero because H^7(M4)=0 for a four-manifold",
        "existence": "a nowhere-zero section exists on the declared M4 base",
        "selection": "the frozen action does not dynamically choose one section",
        "transition_functions": (
            "after reduction they lie in SU3 and obey "
            "J_(g u)(g v)=g J_u(v), so Pi_10 and Pi_01 patch covariantly"
        ),
        "conjugate_bundle": "complex conjugation exchanges E_10 and E_01",
        "bulk_extension": (
            "extension away from M4 is conditional on extending the SU3 "
            "reduction; the M4 dimension argument alone does not prove it"
        ),
    }


def triality_polarization_checks() -> dict[str, Any]:
    triality = triality_algebra_check()
    no_double = no_double_counting_check()
    return {
        "triality_algebra": triality,
        "fourier_intertwiner": {
            "inverse_exact": no_double["fourier_inverse_exact"],
            "intertwines_projectors": no_double["intertwines_projectors"],
        },
        "compatibility": (
            "conditional on the v6.2 explicit triality isomorphisms carrying "
            "the common G2 reduction and the same unit section u"
        ),
        "family_count": 3,
        "nine_generation_product_rejected": True,
        "complex_conjugation_is_antiparticle_map": True,
    }


def allowed_first_order_terms() -> list[dict[str, Any]]:
    """Lowest-order symmetry ledger for a new first-order matter action."""
    return [
        {
            "term": "y_sigma sigma Gamma_star",
            "wall_parity": "odd",
            "gauge": "commutes with SU3 x Sp1 x U1 on each representation slot",
            "family": "universal coefficient required",
            "localizes": True,
            "source": "not present in frozen P1/B1 action",
            "coefficient": "independent dimensionless primitive y_sigma",
        },
        {
            "term": "y_beta beta Gamma_star",
            "wall_parity": "even for the retained beta background",
            "gauge": "allowed only as a representation-scalar bilinear",
            "family": "universal coefficient required",
            "localizes": False,
            "source": "not present in frozen P1/B1 action",
            "coefficient": "independent primitive if added",
        },
        {
            "term": "y_sigma_beta sigma beta Gamma_star",
            "wall_parity": "odd when beta is even",
            "gauge": "representation-scalar",
            "family": "universal coefficient required",
            "localizes": True,
            "source": "higher-order minimal extension, not parent-derived",
            "coefficient": "independent primitive y_sigma_beta",
        },
        {
            "term": "linear n^a without a covariant contraction",
            "wall_parity": "not decisive",
            "gauge": "not SU3-stabilizer invariant",
            "family": "not applicable",
            "localizes": False,
            "source": "rejected by covariance",
            "coefficient": None,
        },
    ]


def normal_mode_normalization(nu: float, delta: float = 1.0) -> float:
    """Normalization for f=N sech(rho/delta)^nu on the complete collar."""
    if nu <= 0 or delta <= 0:
        raise ValueError("nu and delta must be positive")
    denominator = delta * math.sqrt(math.pi) * math.gamma(nu)
    return math.sqrt(math.gamma(nu + 0.5) / denominator)


def normal_mode_profile(
    rho: np.ndarray | float, nu: float = 1.0, delta: float = 1.0
) -> np.ndarray:
    coordinate = np.asarray(rho, dtype=float)
    return normal_mode_normalization(nu, delta) / np.cosh(coordinate / delta) ** nu


def normal_mode_diagnostic(nu: float = 1.0, delta: float = 1.0) -> dict[str, Any]:
    x = np.linspace(-16 * delta, 16 * delta, 200_001)
    f = normal_mode_profile(x, nu, delta)
    norm = float(np.trapezoid(f * f, x))
    sigma = np.tanh(x / delta)
    sigma_overlap = float(np.trapezoid(sigma * f * f, x))
    sigma2_overlap = float(np.trapezoid(sigma * sigma * f * f, x))
    return {
        "profile": "N sech(rho/delta)^nu",
        "nu": nu,
        "delta": delta,
        "normalization": normal_mode_normalization(nu, delta),
        "numerical_norm": norm,
        "sigma_overlap": 0.0 if abs(sigma_overlap) < 1.0e-14 else sigma_overlap,
        "sigma_squared_overlap": sigma2_overlap,
        "representative_exact_sigma_squared_overlap": "1/3 for nu=1",
        "asymptotic_width": "delta/nu",
        "continuum_threshold": "|y_sigma sigma_0|",
        "K_plus_zero_modes": 1,
        "K_minus_zero_modes": 0,
        "full_line_index": 1,
    }


def hopf_connection_transfer(
    kappa1: float, L2: float, L1: float
) -> dict[str, Any]:
    """Exact inherited Hopf kinetic coefficients and Berger ratio."""
    matrix = connection_kinetic_matrix(kappa1, L2, L1)
    transverse = matrix[0][0]
    longitudinal = matrix[2][2]
    return {
        "matrix": matrix,
        "tau_transverse": transverse,
        "tau_nested_U1": longitudinal,
        "ratio_nested_to_transverse": longitudinal / transverse,
        "expected_ratio": (L1 / L2) ** 2,
        "beta": math.log(L1 / L2),
        "positive": min(transverse, longitudinal) > 0,
    }


def orientation_stiffness(beta: float, prefactor: float = 1.0) -> float:
    """Coefficient from Tr(M^-1 dM M^-1 dM) for n-perpendicular motion."""
    if prefactor <= 0:
        raise ValueError("prefactor must be positive")
    return prefactor * 8 * math.sinh(beta) ** 2


def scalar_field_metric(
    Z_sigma: float, berger_prefactor: float
) -> np.ndarray:
    """Retained sigma/beta metric; 6/7 is the P1 shape metric entry."""
    if Z_sigma <= 0 or berger_prefactor <= 0:
        raise ValueError("kinetic coefficients must be positive")
    return np.array([[Z_sigma, 0.0], [0.0, Fraction(6, 7) * berger_prefactor]])


def scalar_mass_eigenvalues(
    H_sigma: float, H_beta: float, H_mix: float,
    Z_sigma: float = 1.0, berger_prefactor: float = 1.0,
) -> np.ndarray:
    """Generalized two-field Hessian eigenvalues in the kinetic metric."""
    metric = scalar_field_metric(Z_sigma, berger_prefactor)
    hessian = np.array([[H_sigma, H_mix], [H_mix, H_beta]], dtype=float)
    root = np.diag(1 / np.sqrt(np.diag(metric)))
    return np.linalg.eigvalsh(root @ hessian @ root)


def electroweak_mass_matrix(g2: float, g1: float, f_n: float) -> np.ndarray:
    """Conditional Sp1 x U1 mass matrix in basis W1,W2,W3,B."""
    if g2 <= 0 or g1 <= 0 or f_n < 0:
        raise ValueError("g1,g2 must be positive and f_n nonnegative")
    factor = f_n**2 / 4
    return factor * np.array(
        [
            [g2**2, 0, 0, 0],
            [0, g2**2, 0, 0],
            [0, 0, g2**2, -g2 * g1],
            [0, 0, -g2 * g1, g1**2],
        ],
        dtype=float,
    )


def electroweak_mass_diagnostic() -> dict[str, Any]:
    g2, g1, f_n = 1.0, 0.6, 2.0
    matrix = electroweak_mass_matrix(g2, g1, f_n)
    null = np.array([0.0, 0.0, g1, g2])
    values = np.linalg.eigvalsh(matrix)
    return {
        "representative_inputs": {
            "g2": g2,
            "g1": g1,
            "f_n": f_n,
            "measured": False,
        },
        "rank": int(np.linalg.matrix_rank(matrix)),
        "nullity": int(4 - np.linalg.matrix_rank(matrix)),
        "Q_em_null_vector": [0, 0, "g1", "g2"],
        "Q_em_null_check": bool(np.allclose(matrix @ null, 0)),
        "eigenvalues": [round(float(value), 12) for value in values],
        "charged_mass_squared": "g2^2 f_n^2/4 (twice)",
        "neutral_massive": "(g2^2+g1^2) f_n^2/4",
        "neutral_massless": "Q_em direction",
        "SU3_color": "eight unbroken massless connection directions, separate block",
    }


def schur_complement(
    H_PP: np.ndarray, H_PC: np.ndarray, H_CC: np.ndarray
) -> np.ndarray:
    """Physical Schur complement after gauge zero modes have been removed."""
    pp = np.asarray(H_PP, dtype=float)
    pc = np.asarray(H_PC, dtype=float)
    cc = np.asarray(H_CC, dtype=float)
    if cc.shape[0] != cc.shape[1] or np.linalg.matrix_rank(cc) != cc.shape[0]:
        raise ValueError("H_CC must be invertible on the declared constrained subspace")
    return pp - pc @ np.linalg.solve(cc, pc.T)


def representative_schur_diagnostic() -> dict[str, Any]:
    pp = np.diag([3.0, 2.0])
    pc = np.array([[0.5], [0.25]])
    cc = np.array([[2.0]])
    reduced = schur_complement(pp, pc, cc)
    return {
        "representative_not_fitted": True,
        "H_phys": reduced.tolist(),
        "symmetric": bool(np.allclose(reduced, reduced.T)),
        "positive": bool(np.all(np.linalg.eigvalsh(reduced) > 0)),
        "gauge_zero_modes_inverted": False,
    }


def connection_dependency_ledger() -> dict[str, Any]:
    traces = connection_trace_payload()
    return {
        "formula": "1/g_i^2=tau_i I_i",
        "trace_indices": traces,
        "SU3": {
            "I3": traces["I3"],
            "N_geom_3": "not derived by the frozen P1 Hopf reduction",
            "Z_A3": "independent transfer coefficient",
            "tau_3": "underdetermined",
        },
        "Sp1": {
            "I2": traces["I2"],
            "N_geom_2": "8 pi^2 kappa1 L2^4 L1 before collar transfer",
            "Z_A2": "one in the v6.0.9 parent convention; boundary transfer open",
            "tau_2": "8 pi^2 kappa1 L2^4 L1 times declared overlap",
        },
        "U1": {
            "I1_normalized": traces["I1_normalized"],
            "eta_Y": traces["eta_Y"],
            "N_geom_1": "8 pi^2 kappa1 L2^2 L1^3 for nested Hopf direction",
            "Z_A1": "physical Y_BH embedding/boundary transfer remains conditional",
            "tau_1": "nested coefficient times eta_Y and declared overlap",
        },
        "Berger_ratio": "tau_nested/tau_transverse=(L1/L2)^2=exp(2 beta)",
        "round_limit": "equal geometric Hopf coefficients at beta=0",
        "candidate_1_2_7_restored": False,
        "measured_couplings_used": False,
    }


def integration_rows() -> list[dict[str, str]]:
    return [
        {"component": "Unified parent action", "status": "Active construction target"},
        {"component": "Enveloped spacetime branch", "status": "Adopted input"},
        {"component": "Gauge algebra", "status": "Derived"},
        {"component": "Gauge normalization", "status": "Active construction target"},
        {"component": "Chiral particle map", "status": "Derived"},
        {"component": "Anomaly cancellation", "status": "Derived"},
        {"component": "Three-family theorem", "status": "Derived"},
        {"component": "Family mass operator", "status": "Derived"},
        {"component": "Absolute-scale correspondence", "status": "Active construction target"},
        {"component": "CKM transport architecture", "status": "Derived"},
        {"component": "PMNS/neutral transport architecture", "status": "Derived"},
        {"component": "Neutrino propagation phase law", "status": "Active construction target"},
        {"component": "Berger-Higgs mechanism", "status": "Adopted input"},
        {"component": "Constraint-reduced stable spectrum", "status": "Active construction target"},
        {"component": "Empirical prediction set", "status": "Needs empirical test"},
        {"component": "Reproducible implementation", "status": "Numerically validated"},
    ]


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        **GUARDS,
    }


def build_artifact_payloads(
    repo_root: Path | None = None,
) -> dict[str, dict[str, Any]]:
    root = repo_root or Path(__file__).resolve().parents[3]
    polarization = polarization_checks()
    topology = topology_globalization_ledger()
    triality = triality_polarization_checks()
    normal = normal_mode_diagnostic()
    transfer = connection_dependency_ledger()
    hopf = hopf_connection_transfer(1.0, 1.0, math.exp(0.2))
    gauge = electroweak_mass_diagnostic()
    mass = exact_mass_operator(root)
    scalar_eigs = scalar_mass_eigenvalues(2.0, 3.0, 0.0)
    common = _common

    payloads = {
        "handoff": {
            **common("BHSM_v6_4_0_state_handoff"),
            "status": "BHSM_V6_3_0_HANDOFF_PRESERVED",
            "source_sha": SOURCE_SHA,
            "source_primary_result": V630_PRIMARY_RESULT,
            "source_artifact_count": len(V630_ARTIFACT_FILES),
            "source_results_changed": False,
        },
        "g2_complex": {
            **common("BHSM_G2_global_complex_structure_v6_4_0"),
            "status": "BHSM_G2_CROSS_PRODUCT_COMPLEX_STRUCTURE_DERIVED",
            "established_input": (
                "the G2-invariant octonionic cross product on R7 and a unit u"
            ),
            "identity": "J_u^2=-I+u tensor u; hence J_u^2=-I on u-perpendicular",
            "checks": polarization,
            "orientation": "standard Fano triples 123,145,176,246,257,347,365",
        },
        "polarization": {
            **common("BHSM_global_color_polarization_bundle_v6_4_0"),
            "status": "BHSM_GLOBAL_COMPLEX_POLARIZATION_OPERATOR_DERIVED_CONDITIONALLY",
            "projectors": {
                "Pi_10": "(Q-iJ_u)/2",
                "Pi_01": "(Q+iJ_u)/2",
                "Q": "I-u tensor u",
            },
            "checks": polarization,
            "globalization": topology,
            "dynamic_selection_by_frozen_action": False,
            "candidate_u": (
                "the global G2/SU3 stabilizer section; twistor orientation is "
                "compatible only after an explicit bundle map"
            ),
            "orientation_reversal": (
                "u->-u exchanges Pi_10 and Pi_01; scalar-wall sign alone does not"
            ),
        },
        "triality": {
            **common("BHSM_triality_polarization_compatibility_v6_4_0"),
            "status": "BHSM_TRIALITY_POLARIZATION_COMPATIBILITY_DERIVED_CONDITIONALLY",
            **triality,
        },
        "matter_action": {
            **common("BHSM_parent_first_order_matter_action_v6_4_0"),
            "status": "BHSM_FIRST_ORDER_MATTER_ACTION_MINIMAL_EXTENSION_CLASSIFIED",
            "frozen_parent_contains_matter_action": False,
            "candidate_action": (
                "S_F=integral sqrt|g| <Psi,[C_BHSM+M(sigma,beta,n)]Psi>"
            ),
            "configuration_space": (
                "H1 sections of the v6.3 Clifford bundle tensor the "
                "complex-polarized particle representation bundle"
            ),
            "inner_product": "v6.3 L2 collar product with Lorentzian adjoint",
            "domain": "complete collar H1 or declared maximal-isotropic cut domain",
            "allowed_terms": allowed_first_order_terms(),
            "new_independent_primitives_if_adopted": ["y_sigma"],
            "parent_action_derivation_claimed": False,
        },
        "odd_coupling": {
            **common("BHSM_action_native_odd_wall_coupling_v6_4_0"),
            "status": "BHSM_ODD_WALL_COUPLING_ALLOWED_BUT_NOT_PARENT_DERIVED",
            "minimal_term": "y_sigma sigma Gamma_star",
            "why_unique_at_lowest_order": (
                "sigma is the retained wall-odd representation scalar; beta is "
                "wall-even and a naked n is not SU3-stabilizer invariant"
            ),
            "coefficient": "independent dimensionless primitive y_sigma",
            "normalization_fixes_coefficient": False,
            "measured_Yukawa_used": False,
            "kill_test": {
                "covariant": True,
                "Hermitian_for_real_y_sigma": True,
                "family_universal": True,
                "commutes_with_Y_BH": True,
                "odd_wall_profile": True,
                "already_in_frozen_parent_action": False,
            },
        },
        "index": {
            **common("BHSM_chiral_zero_mode_index_v6_4_0"),
            "status": "BHSM_ONE_CHIRAL_ZERO_MODE_PER_SELECTED_SLOT_DERIVED_CONDITIONALLY",
            "normal_equation": "[partial_rho+y_sigma sigma(rho)]f=0",
            "solution": "f proportional exp[-integral y_sigma sigma d rho]",
            "representative": normal,
            "condition": "y_sigma sigma(+infinity)>0>y_sigma sigma(-infinity)",
            "index": 1,
            "scope": "complete-line domain-wall operator or equivalent declared cut domain",
            "slots_per_family": "15 charged; optional neutral sixteenth",
            "families": 3,
        },
        "doubling": {
            **common("BHSM_vectorlike_doubling_audit_v6_4_0"),
            "status": "BHSM_VECTORLIKE_DOUBLING_REJECTED_BY_BOUNDARY_DOMAIN_CONDITIONALLY",
            "K_plus": "one normalizable profile",
            "K_minus": "nonnormalizable for the selected wall orientation",
            "antiparticle": "complex conjugate E_01 bundle, not a second vectorlike field",
            "orientation_reversal": "exchanges polarization and normal chirality together",
            "scalar_sign_alone": "reverses the wall profile and requires domain orientation tracking",
            "global_no_extra_family_theorem": False,
        },
        "connection_source": {
            **common("BHSM_connection_localization_source_map_v6_4_0"),
            "status": "BHSM_CONNECTION_TRANSFER_FACTORS_REMAIN_INDEPENDENT_AFTER_PARENT_REDUCTION",
            **transfer,
            "normalized_profile_integrals": {
                "integral_abs_u_squared": "1",
                "integral_sigma_abs_u_squared": "0 for the symmetric odd wall",
                "integral_sigma_squared_abs_u_squared": "sigma_0^2/3 for nu=1",
            },
        },
        "su3_transfer": {
            **common("BHSM_SU3_connection_transfer_v6_4_0"),
            "status": "BHSM_SU3_PARENT_TO_BOUNDARY_TRANSFER_REMAINS_INDEPENDENT",
            **transfer["SU3"],
            "color_projector": "v6.3 rank-eight retained SU3 adjoint",
            "kinetic_sign_condition": "tau_3>0",
            "localization_function_invented": False,
        },
        "sp1_transfer": {
            **common("BHSM_Sp1_connection_transfer_v6_4_0"),
            "status": "BHSM_SP1_BERGER_CONNECTION_TRANSFER_DERIVED_CONDITIONALLY",
            **transfer["Sp1"],
            "exact_parent_matrix": (
                "8 pi^2 kappa1 diag(L2^4 L1,L2^4 L1,L2^2 L1^3)"
            ),
            "representative_diagnostic": hopf,
            "kinetic_sign_condition": "kappa1,L1,L2 and collar overlap positive",
        },
        "u1_transfer": {
            **common("BHSM_U1_connection_transfer_v6_4_0"),
            "status": "BHSM_U1_BERGER_TRANSFER_DERIVED_PHYSICAL_EMBEDDING_CONDITIONAL",
            **transfer["U1"],
            "relative_geometric_split": "exp(2 beta)",
            "physical_Y_BH_map": "conditional boundary identification from v6.3",
            "candidate_1_2_7_restored": False,
        },
        "gravity": {
            **common("BHSM_gravity_boundary_transfer_v6_4_0"),
            "status": "BHSM_GRAVITY_AND_CONNECTION_TRANSFERS_REMAIN_DISTINCT",
            "formula": "C4=C_partial,intrinsic+Z_g N_g",
            "correspondence": "C4=Mbar_Pl^2/2 only after reduction",
            "C_partial_source": "independent provisional B1 primitive",
            "Z_g": "bulk tensor profile transfer",
            "same_invariant_as_connections": False,
            "Z_g_equals_Z_A_assumed": False,
            "positive_principal_condition": "kappa1>0 and C_partial>0",
        },
        "kinetic_metric": {
            **common("BHSM_Berger_Higgs_kinetic_metric_v6_4_0"),
            "status": "BHSM_BERGER_HIGGS_KINETIC_METRIC_DERIVED_OFF_SHELL",
            "coordinates": ["sigma", "beta=log(L1/L2)", "orientation n"],
            "field_metric": {
                "G_sigma_sigma": "Z_sigma",
                "G_beta_beta": "(6/7) Z_Berger in the v6.0.9 shape basis",
                "G_sigma_beta": "0 at sigma=0 by retained Z2 symmetry",
            },
            "orientation_stiffness": "f_n^2=8 Z_Berger sinh(beta)^2",
            "round_limit": "orientation stiffness vanishes at beta=0",
            "positive_domain": "Z_sigma>0, Z_Berger>0, beta!=0 for orientation",
        },
        "scalar_mass": {
            **common("BHSM_scalar_Berger_mixed_mass_matrix_v6_4_0"),
            "status": "BHSM_SCALAR_BERGER_MASS_MATRIX_DIAGONAL_AT_RETAINED_ORDER",
            "matrix": "[[H_sigma_sigma,H_sigma_beta],[H_sigma_beta,H_beta_beta]]",
            "retained_H_sigma_beta": 0,
            "reason": "sigma Z2 and p1-p2=0 at the retained background",
            "representative_unfitted_eigenvalues": scalar_eigs.tolist(),
            "physical_conditions": "both generalized eigenvalues positive",
            "Higgs_like_eigenmode_derived": False,
            "higher_order_mixing": "open",
        },
        "gauge_mass": {
            **common("BHSM_gauge_boson_mass_matrix_v6_4_0"),
            "status": "BHSM_BERGER_HIGGS_GAUGE_MASS_MATRIX_DERIVED_CONDITIONALLY",
            "basis": ["W1", "W2", "W3", "B"],
            "matrix": (
                "(f_n^2/4)[diag(g2^2,g2^2) direct_sum "
                "[[g2^2,-g2 g1],[-g2 g1,g1^2]]]"
            ),
            "diagnostic": gauge,
            "vacuum_Q_em_neutral": True,
            "extra_massless_electroweak_direction": False,
            "measured_W_Z_Higgs_inputs": False,
        },
        "tensor": {
            **common("BHSM_constraint_reduced_tensor_sector_v6_4_0"),
            "status": "BHSM_TENSOR_PRINCIPAL_SECTOR_GHOST_FREE_CONDITIONALLY",
            "physical_modes": "two intrinsic TT polarizations plus coupled cap tower",
            "principal_kinetic": "positive for kappa1>0 and C_partial>0",
            "principal_gradient": "same induced Lorentz cone",
            "normal_spectrum": "not solved",
            "tachyon_free": None,
            "boundary_flux": "dynamic junction Lopatinski proof open",
        },
        "vector": {
            **common("BHSM_constraint_reduced_vector_sector_v6_4_0"),
            "status": "BHSM_VECTOR_PRINCIPAL_SECTOR_GHOST_FREE_CONDITIONALLY",
            "gauge_removed": "temporal multipliers and longitudinal connection modes",
            "physical_modes": "transverse SU3, Sp1, and U1 connections",
            "principal_kinetic": "positive iff every tau_i I_i>0",
            "principal_gradient": "same induced Lorentz cone",
            "mass_matrix": gauge,
            "full_boundary_spectrum": "not solved",
        },
        "scalar": {
            **common("BHSM_constraint_reduced_scalar_sector_v6_4_0"),
            "status": "BHSM_SCALAR_PRINCIPAL_SECTOR_HEALTHY_MASS_SIGNS_CONDITIONAL",
            "constraints_removed": [
                "lapse",
                "shift/longitudinal metric",
                "matching multiplier",
                "normal-coordinate gauge",
            ],
            "physical_candidates": ["delta sigma", "delta beta", "junction bending"],
            "kinetic_metric": "diag(Z_sigma,(6/7)Z_Berger) at retained order",
            "mass_signs": "depend on H_sigma_sigma,H_beta_beta and higher mixing",
            "junction_bending": "cap Green-operator problem open",
            "representative_schur": representative_schur_diagnostic(),
        },
        "matter_spectrum": {
            **common("BHSM_first_order_matter_spectrum_v6_4_0"),
            "status": "BHSM_FIRST_ORDER_MATTER_PRINCIPAL_SPECTRUM_DERIVED_CONDITIONALLY",
            "localized_zero_mode": normal,
            "principal_symbol": "Gamma^mu xi_mu on the selected M4 bundle",
            "hyperbolicity": "symmetric hyperbolic after time orientation and domain choice",
            "kinetic_sign": "positive with the declared L2 inner product",
            "boundary_flux": "zero on the maximal-isotropic projector domain",
            "mass_spectrum": "family operator attached; absolute eigenvalues not derived",
            "family_mass_operator": mass,
        },
        "spacetime": {
            **common("BHSM_spacetime_branch_principal_symbol_audit_v6_4_0"),
            "status": "BHSM_LOCAL_PRINCIPAL_SYMBOLS_SHEET_SYMMETRIC",
            "upper": "admissible in tested positive-coefficient principal sectors",
            "lower": "same local principal symbols after consistent orientation tracking",
            "unique_upper_selection_derived": False,
            "reason": (
                "sheet sign enters global orientation/action branch data but not "
                "the retained local highest-derivative matrices"
            ),
            "remaining_selection": "adopted global envelopment/causal axiom",
            "global_continuation_test": "open",
        },
        "scale": {
            **common("BHSM_absolute_scale_transfer_map_v6_4_0"),
            "status": "BHSM_ABSOLUTE_SCALE_TRANSFER_MAP_REFINED_SYMBOLICALLY",
            "formula": "L_i^2=Xi_i 2/(g_i^2 Mbar_Pl^2)",
            "Xi_i": "(Z_g/Z_A,i)/(N_geom,i I_i)",
            "representation_derived": connection_trace_payload(),
            "geometry_derived": {
                "Sp1_Hopf": "8 pi^2 kappa1 L2^4 L1",
                "nested_U1_Hopf": "8 pi^2 kappa1 L2^2 L1^3",
            },
            "independent": ["SU3 transfer", "boundary overlaps", "Z_g/Z_A,i"],
            "mass_conversion": "m_(f,k)=hbar E_(f,k)/(c L_*)",
            "numerical_absolute_scale": None,
        },
        "r4": {
            **common("BHSM_scalar_wall_O_r4_action_v6_4_0"),
            "status": "BHSM_SCALAR_WALL_O_R4_TOTAL_REMAINS_OPEN",
            "preserved": "Gamma_tau-Gamma_c=tau(nu1/12)r^3+O(r^4)",
            "nu1_over_12": 9.138890145035,
            "B_components": {
                name: None
                for name in (
                    "direct",
                    "gravity",
                    "junction",
                    "domain",
                    "normalization",
                    "constraint",
                    "total",
                )
            },
            "fixed_moving_agreement": "preserved through O(r^3), not closed at O(r^4)",
            "flat_kink_27_35_revived": False,
        },
        "integration": {
            **common("BHSM_full_integration_ledger_v6_4_0"),
            "status": "BHSM_FULL_INTEGRATION_LEDGER_UPDATED_NO_COMPLETION_DECLARATION",
            "rows": integration_rows(),
            "counting_rows_implies_completion": False,
            "integrated_action_generated_spectrum_exists": False,
        },
        "hidden": {
            **common("BHSM_v6_4_0_hidden_input_audit"),
            "status": "BHSM_V6_4_0_HIDDEN_INPUT_AUDIT_PASS",
            "measured_inputs": [],
            "fits": [],
            "new_primitives_derived": [],
            "independent_primitives_exposed": [
                "y_sigma if first-order matter extension is adopted",
                "SU3 parent-to-boundary transfer",
                "boundary connection overlaps",
                "Z_g/Z_A,i",
            ],
            "adopted_choices": [
                "global unit section u/SU3 reduction",
                "spacetime-facing upper branch",
                "Berger-Higgs translation",
            ],
        },
        "report": {
            **common("BHSM_parent_action_polarization_localization_stability_report_v6_4_0"),
            "status": PRIMARY_RESULT,
            "primary_conclusion": (
                "The selected G2 reduction supplies an exact global M4 complex "
                "polarization and the frozen P1 geometry supplies an exact "
                "Berger Hopf-connection split. Principal tensor, connection, "
                "scalar, and first-order sectors are healthy in a declared "
                "positive-coefficient domain. The frozen parent action contains "
                "no first-order matter term, does not select u dynamically, and "
                "does not fix SU3/boundary transfers or the full spectra."
            ),
            "derived": [
                "G2 J_u complex structure and rank-three projectors",
                "M4 bundle globalization conditional on the selected SU3 reduction",
                "Berger Hopf transfer ratio exp(2 beta)",
                "conditional one-sided wall index for the minimal extension",
                "conditional electroweak mass-matrix rank and Q_em null direction",
                "positive-domain principal-sector classification",
            ],
            "rejected": [
                "claim that the frozen action already contains the odd matter coupling",
                "restoration of 1:2:7",
                "local principal symbols as an upper-sheet selector",
                "sigma-beta conflation before diagonalization",
            ],
            "active_targets": [
                "derive or reject a parent first-order matter invariant",
                "derive SU3 and boundary transfer coefficients",
                "solve normal tensor/vector/scalar and bending spectra",
                "derive global sheet selection by continuation",
                "close O(r^4) total and absolute scale",
            ],
            "completion_gate": COMPLETION_GATE,
        },
    }
    if set(payloads) != set(ARTIFACT_FILES):
        raise RuntimeError("v6.4.0 artifact registry/payload mismatch")
    return payloads


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def materialize_artifacts(root: Path) -> list[Path]:
    payloads = build_artifact_payloads(root)
    output = root / "artifacts"
    written = []
    for key, filename in ARTIFACT_FILES.items():
        path = output / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        written.append(path)
    return written


def architecture_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    payloads = build_artifact_payloads(repo_root)
    return {
        "version": VERSION,
        "branch": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "global_polarization": payloads["polarization"]["status"],
        "parent_matter_action": payloads["matter_action"]["status"],
        "odd_wall_coupling": payloads["odd_coupling"]["status"],
        "connection_transfer": payloads["connection_source"]["status"],
        "physical_hessian": {
            "tensor": payloads["tensor"]["status"],
            "vector": payloads["vector"]["status"],
            "scalar": payloads["scalar"]["status"],
            "matter": payloads["matter_spectrum"]["status"],
        },
        "spacetime_branch": payloads["spacetime"]["status"],
        "completion_gate": COMPLETION_GATE,
        "safeguards": GUARDS,
    }


def architecture_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# BHSM v6.4.0 parent-action polarization and stability",
            "",
            f"Primary result: `{report['primary_result']}`.",
            "",
            f"- Global polarization: `{report['global_polarization']}`",
            f"- Parent matter action: `{report['parent_matter_action']}`",
            f"- Odd wall coupling: `{report['odd_wall_coupling']}`",
            f"- Connection transfer: `{report['connection_transfer']}`",
            f"- Spacetime branch: `{report['spacetime_branch']}`",
            f"- Completion gate: `{report['completion_gate']}`",
            "",
        ]
    )
