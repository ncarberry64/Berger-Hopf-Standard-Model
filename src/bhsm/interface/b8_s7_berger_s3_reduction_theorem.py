"""BHSM v6.0.7 B8/S7-to-Berger-S3 reduction and obstruction theorem."""

from __future__ import annotations

import json
from math import pi
from pathlib import Path
from typing import Any, Sequence


VERSION = "v6.0.7"
SPRINT = "bhsm-b8-s7-to-berger-s3-reduction-theorem-v6-0-7"
PRIMARY_RESULT = "BHSM_B8_S7_TO_BERGER_S3_REDUCTION_OBSTRUCTED"
U1_RESULT = "BHSM_SP1_TO_U1_REDUCTION_TOPOLOGICALLY_OBSTRUCTED"
GLOBALIZATION_RESULT = "BHSM_BERGER_MODE_ASSOCIATED_BUNDLE_MAP_DERIVED"
TRUNCATION_RESULT = "BHSM_BERGER_CONSISTENT_TRUNCATION_FAILED"

ARTIFACT_FILES = {
    "bundle": "BHSM_quaternionic_hopf_bundle_convention_ledger_v6_0_7.json",
    "metric": "BHSM_global_4_2_1_metric_audit_v6_0_7.json",
    "u1": "BHSM_sp1_to_u1_reduction_theorem_v6_0_7.json",
    "fiber": "BHSM_fiber_restriction_berger_metric_v6_0_7.json",
    "global": "BHSM_local_global_berger_fiber_classification_v6_0_7.json",
    "measure": "BHSM_berger_measure_orientation_reduction_v6_0_7.json",
    "hodge": "BHSM_berger_hodge_star_decomposition_v6_0_7.json",
    "operators": "BHSM_berger_differential_operator_decomposition_v6_0_7.json",
    "modes": "BHSM_berger_fiber_mode_globalization_theorem_v6_0_7.json",
    "truncation": "BHSM_berger_consistent_truncation_test_v6_0_7.json",
    "branching": "BHSM_so8_hopf_berger_representation_branching_v6_0_7.json",
    "ledgers": "BHSM_existing_berger_mode_ledger_parent_map_v6_0_7.json",
    "scalar": "BHSM_berger_scalar_action_reduction_v6_0_7.json",
    "gauge": "BHSM_berger_gauge_reduction_readiness_v6_0_7.json",
    "dirac": "BHSM_berger_dirac_reduction_readiness_v6_0_7.json",
    "boundary": "BHSM_berger_boundary_collar_role_firewall_v6_0_7.json",
    "lovelock": "BHSM_lovelock_berger_action_reduction_map_v6_0_7.json",
    "coefficients": "BHSM_parent_to_v5_coefficient_map_v6_0_7.json",
    "scale": "BHSM_berger_reduction_scale_hidden_input_audit_v6_0_7.json",
    "report": "BHSM_b8_s7_to_berger_s3_reduction_report_v6_0_7.json",
}

GUARDS = {
    "v6_0_6_firewall_preserved": True,
    "established_physics_claimed_novel": False,
    "new_parent_field_added": False,
    "new_interaction_added": False,
    "measured_mass_coupling_or_scale_used": False,
    "v5_values_used_as_parent_inputs": False,
    "target_fitting_used": False,
    "frozen_mode_ledgers_changed": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "existing_numerical_predictions_changed": False,
    "absolute_unit_generated": False,
    "standard_model_gauge_fields_derived": False,
    "particle_generations_derived": False,
    "full_bhsm_completion_claimed": False,
}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "sp1_to_u1_result": U1_RESULT,
        "mode_globalization_result": GLOBALIZATION_RESULT,
        "consistent_truncation_result": TRUNCATION_RESULT,
        "claim_boundary": (
            "v6.0.7 proves the global U(1)-reduction obstruction and the "
            "associated-bundle globalization rule. A local Berger fiber metric "
            "does not close the operator, action, coefficient, or physical-boundary reduction."
        ),
        **GUARDS,
    }


def nested_dimensions() -> tuple[int, int, int]:
    return (4, 2, 1)


def sp1_to_u1_reduction_possible(c2: int, h2_base_rank: int = 0) -> bool:
    """Return the splitting-test result for an SU(2) bundle over the declared base."""

    if h2_base_rank < 0:
        raise ValueError("H2 rank must be nonnegative")
    if h2_base_rank == 0:
        return c2 == 0
    raise ValueError("nonzero H2 requires an explicit intersection form and Chern class")


def fiber_volume(L2: float, L1: float) -> float:
    """Volume in the repository sigma_i convention and full SU(2) Euler ranges."""

    if L2 <= 0 or L1 <= 0:
        raise ValueError("fiber scales must be positive")
    return 16.0 * pi**2 * L2**2 * L1


def berger_ricci_eigenvalues(L2: float, L1: float) -> tuple[float, float, float]:
    """Ricci eigenvalues for d sigma_i=-epsilon_ijk sigma_j wedge sigma_k."""

    if L2 <= 0 or L1 <= 0:
        raise ValueError("fiber scales must be positive")
    horizontal = 1.0 / L2**2 - L1**2 / (2.0 * L2**4)
    vertical = L1**2 / (2.0 * L2**4)
    return (horizontal, horizontal, vertical)


def berger_scalar_curvature(L2: float, L1: float) -> float:
    return sum(berger_ricci_eigenvalues(L2, L1))


def hodge_scale(
    horizontal_degree: int,
    vertical_indices: Sequence[int],
    L4: float,
    L2: float,
    L1: float,
) -> dict[str, Any]:
    """Scale/sign for star on an unscaled ordered product-coframe monomial."""

    if not 0 <= horizontal_degree <= 4:
        raise ValueError("horizontal degree must lie in [0,4]")
    indices = tuple(vertical_indices)
    if len(set(indices)) != len(indices) or any(index not in (1, 2, 3) for index in indices):
        raise ValueError("vertical indices must be distinct members of {1,2,3}")
    if min(L4, L2, L1) <= 0:
        raise ValueError("metric scales must be positive")
    lengths = {1: L2, 2: L2, 3: L1}
    q = len(indices)
    factor = L4 ** (4 - 2 * horizontal_degree) * (L2**2 * L1)
    for index in indices:
        factor /= lengths[index] ** 2
    return {
        "sign": -1 if (q * (4 - horizontal_degree)) % 2 else 1,
        "scale": factor,
        "vertical_complement": [index for index in (1, 2, 3) if index not in indices],
    }


def associated_transition(coefficients: Sequence[complex], matrix: Sequence[Sequence[complex]]) -> tuple[complex, ...]:
    """Apply the associated-representation transition law phi_b=R(g_ab)^-1 phi_a."""

    vector = tuple(coefficients)
    rows = tuple(tuple(row) for row in matrix)
    if len(rows) != len(vector) or any(len(row) != len(vector) for row in rows):
        raise ValueError("transition matrix must be square and match the coefficient vector")
    return tuple(sum(row[j] * vector[j] for j in range(len(vector))) for row in rows)


def low_level_branching() -> list[dict[str, Any]]:
    """Exact low-level SO(8) scalar-harmonic branching dimension checks."""

    return [
        {"ell": 0, "so8": "[0,0,0,0]", "so8_dimension": 1, "sp2_x_sp1": [{"representation": "(1,1)", "dimension": 1, "u1_weights": [0]}], "dimension_sum": 1},
        {"ell": 1, "so8": "[1,0,0,0]", "so8_dimension": 8, "sp2_x_sp1": [{"representation": "(4,2)", "dimension": 8, "u1_weights": [-1, 1]}], "dimension_sum": 8},
        {"ell": 2, "so8": "[2,0,0,0]", "so8_dimension": 35, "sp2_x_sp1": [{"representation": "(10,3)", "dimension": 30, "u1_weights": [-2, 0, 2]}, {"representation": "(5,1)", "dimension": 5, "u1_weights": [0]}], "dimension_sum": 35},
    ]


def bundle_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_quaternionic_hopf_bundle_convention_ledger_v6_0_7"),
        "status": "QUATERNIONIC_HOPF_BUNDLE_CONVENTIONS_FIXED",
        "principal_bundle": "Sp(1)->S7->S4 with c2=+1 after the declared generator orientation; reversing orientation changes the sign, not nonvanishing",
        "nested_fibrations": ["S3->S7->S4", "S1->S7->CP3", "S2->CP3->S4"],
        "composition": "p_H=tau o p_C",
        "distributions": {"H": "ker(omega)", "V": "ker(dp_H), rank 3", "nested": "H4 plus m2 plus u1, dimensions 4+2+1"},
        "connection": "global sp(1)-valued principal connection omega; R_g^*omega=Ad(g^-1)omega",
        "components": "eta_i are components only after a Lie-algebra frame/local gauge is declared; local pullbacks obey A_b=g_ab^-1 A_a g_ab+g_ab^-1 d g_ab",
        "curvature": "Omega=d omega+(1/2)[omega,omega], transforming by Ad",
        "orientation": "or(S7)=or(H4) wedge eta_1 wedge eta_2 wedge eta_3; the c2 sign follows the base/fiber orientation convention",
        "fiber_volume_form": "eta_1 wedge eta_2 wedge eta_3 in the oriented local frame",
        "vertical_double_counting": False,
    }


def metric_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_global_4_2_1_metric_audit_v6_0_7"),
        "status": "GLOBAL_TOTAL_SPACE_METRIC_WITH_EXTRA_U1_CHOICE_NOT_SP1_NATURAL",
        "ansatz": "g7=L4^2 g_H+L2^2(eta_1^2+eta_2^2)+L1^2 eta_3^2",
        "dimensions": list(nested_dimensions()),
        "overall_jacobian": "L4^4 L2^2 L1 relative to the declared reference coframe",
        "berger_ratio": "b=L1/L2",
        "global_total_space_statement": "A fixed subgroup U(1) subset Sp(1) gives global U(1)-orbit and complementary distributions on S7, so the tensor is definable on the total space.",
        "principal_bundle_statement": "For L1!=L2 the vertical quadratic form is not Ad(Sp(1))-invariant and does not define a gauge-independent metric on ad(P) over S4.",
        "invariance": "right U(1) (and the corresponding Hopf-preserving subgroup), not full right Sp(1), when L1!=L2",
        "round_case": "L1=L2 restores Ad(Sp(1)) invariance",
        "known_geometry": "a two-step homogeneous/nested squashing candidate after normalization; no parent stationarity theorem selects it",
        "local_gauge_dependence": "the named eta_3 component rotates under general Sp(1) transition functions",
        "no_double_counting_proof": "V=span(eta_1,eta_2,eta_3)=m2 direct-sum u1; ranks 2+1=3, while H has rank 4",
    }


def u1_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_sp1_to_u1_reduction_theorem_v6_0_7"),
        "status": U1_RESULT,
        "equivalences": ["principal U(1) reduction Q subset P", "section of P/U(1)=P x_Ad S2", "unit section of the adjoint S2 bundle", "splitting ad(P)=R n direct-sum n-perp", "globally distinguished imaginary-quaternion axis"],
        "associated_complex_bundle": "E=P x_Sp(1) C2 with c1(E)=0 and c2(E)=+1",
        "reduction_consequence": "E=L direct-sum L^-1, hence c2(E)=-c1(L)^2",
        "base_cohomology": "H2(S4;Z)=0, so c1(L)=0 for every complex line bundle L",
        "contradiction": "a U(1) reduction would force c2(E)=0, contradicting c2(E)=+1",
        "instanton_number": 1,
        "global_section_exists": False,
        "twistor_relation": "CP3=P/U(1) is the associated S2 bundle over S4; S7->CP3 is a quotient, while CP3->S4 supplies no section",
        "fixed_subgroup_choice": "A fixed U(1) acts globally on total S7 but is not a reduction subbundle over S4.",
        "additional_field": "A nowhere-zero adjoint unit field would be precisely the forbidden section; any such field must have zeros/defects or change the bundle topology.",
    }


def fiber_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_fiber_restriction_berger_metric_v6_0_7"),
        "status": "BERGER_FIBER_METRIC_FORM_DERIVED_CONVENTION_NORMALIZATION_OPEN",
        "restriction": "g_F=L2^2(eta_1^2+eta_2^2)+L1^2 eta_3^2",
        "repository_map": {"r_base": "L2", "r_fiber": "L1", "status": "EXACT_COEFFICIENT_FORM_IN_STORED_SIGMA_CONVENTION"},
        "maurer_cartan": "d sigma_1=-sigma_2 wedge sigma_3 cyclically",
        "euler_ranges": "theta in [0,pi], phi in [0,2pi), psi in [0,4pi) for one full SU(2) cover",
        "orientation": "sigma_1 wedge sigma_2 wedge sigma_3=sin(theta)dtheta wedge dphi wedge dpsi",
        "volume": "16 pi^2 L2^2 L1 in that full-cover convention",
        "ricci_orthonormal_eigenvalues": ["1/L2^2-L1^2/(2L2^4)", "1/L2^2-L1^2/(2L2^4)", "L1^2/(2L2^4)"],
        "scalar_curvature": "2/L2^2-L1^2/(2L2^4)",
        "round_limit": "L1=L2=R/2 gives Ric=2/R^2 and scalar curvature 6/R^2",
        "degenerate_limits": "L1->0 or L2->0 leaves the positive-definite Berger domain and degenerates the metric",
        "normalization_blocker": "legacy artifacts also contain normalized/author-axiom radius conventions; none is promoted to the parent physical fiber normalization",
    }


def global_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_local_global_berger_fiber_classification_v6_0_7"),
        "status": "ASSOCIATED_FAMILY_NOT_GLOBAL_FIXED_BERGER_AXIS",
        "each_fiber": "After a local frame or fixed total-space U(1) choice, every fiber has the same Berger coefficient form.",
        "transport": "Sp(1) holonomy rotates the anisotropy axis; a nonzero instanton bundle has no globally parallel/preferred axis over S4.",
        "canonical_case": "Only the round L1=L2 vertical metric is Ad(Sp(1))-invariant and bundle-natural without extra structure.",
        "strongest_interpretation": "local/gauge-fixed fiber diagnostic or section-dependent associated family; a symmetry-broken global phase would require defects/topology change",
        "existing_engine_role": "independent homogeneous effective model until an associated-bundle field theory and controlled reduction are supplied",
        "one_chart_sufficient": False,
    }


def measure_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_berger_measure_orientation_reduction_v6_0_7"),
        "status": "LOCAL_PRODUCT_JACOBIAN_DERIVED_GLOBAL_NORMALIZATION_NOT_MATCHED",
        "orientation": "vol7=vol_H4 wedge eta_1 wedge eta_2 wedge eta_3",
        "local_volume_form": "dmu7=L4^4 L2^2 L1 p_H^*(dmu_H,ref) wedge eta_1 wedge eta_2 wedge eta_3",
        "fiber_physical_measure": "dmu_F=L2^2 L1 eta_1 wedge eta_2 wedge eta_3",
        "fiber_physical_volume_repository_convention": "16 pi^2 L2^2 L1",
        "normalized_fiber_measure": "dmu_F/Vol(F); using it removes the physical fiber-volume factor and is not physical integration",
        "pushforward": "(p_H)_* alpha is defined by integral_S4 beta wedge (p_H)_*alpha=integral_S7 p_H^*beta wedge alpha with declared orientations",
        "global_factorization": "valid for invariant integrands after the connection, total metric, orientation, and fiber normalization are fixed; nontrivial representation components push forward to zero or bundle-valued pairings, not scalar averages",
        "existing_parent_volume_formula": "pi^4 L4^4 L2^2 L1/3 uses a separate compatible standard normalization",
        "repository_match": "blocked because the explicit sigma_i full-cover volume and the parent normalized reference volume have not been related by an action-selected convention",
        "restriction_equals_pushforward": False,
        "normalized_equals_physical": False,
    }


def hodge_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_berger_hodge_star_decomposition_v6_0_7"),
        "status": "PRODUCT_COFRAME_HODGE_FORMULA_DERIVED_V5_NORMALIZATION_OPEN",
        "formula": "star7(alpha_p wedge beta_q)=(-1)^[q(4-p)] star_H alpha_p wedge star_V beta_q for orientation vol_H wedge vol_V",
        "unscaled_horizontal_factor": "L4^(4-2p)",
        "unscaled_vertical_factor": "(L2^2 L1)/product_{i in I} L_i^2 for beta=eta_I, with (L_1,L_2,L_3)=(L2,L2,L1)",
        "checks": {"function": "L4^4 L2^2 L1 vol_ref", "horizontal_one_form": "L4^2 L2^2 L1 times complementary form", "eta_1": "L4^4 L1 times complementary form", "eta_3": "L4^4 L2^2/L1 times complementary form", "top_form": "inverse volume scale times 1"},
        "connection_caveat": "the algebraic Hodge split is pointwise exact for the declared orthogonal metric; exterior derivatives still mix horizontal and vertical sectors through curvature",
        "v5_vertical_recovery": "the stored Berger Hodge factors are recovered in coefficient form after orientation/coframe choice, but the physical normalization and parent role remain open",
    }


def operators_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_berger_differential_operator_decomposition_v6_0_7"),
        "status": "COUPLED_ASSOCIATED_BUNDLE_OPERATOR_ARCHITECTURE_DERIVED_SIMPLE_SUM_INVALIDATED",
        "exterior_derivative": "d=d_V+D_H+curvature insertion/degree-changing terms in a connection-adapted bicomplex",
        "coderivative": "delta follows from the scaled star7 and contains connection/O'Neill/mean-curvature corrections",
        "scalar_laplacian": "Delta7=D_H^*D_H+Delta_V+O'Neill/connection-curvature terms; for invariant zero modes on a minimal homogeneous fiber it can simplify, but not universally",
        "hodge_laplacian": "contains horizontal-vertical curvature commutators and representation action",
        "connection_laplacian": "nontrivial vertical representations use the induced associated-bundle connection",
        "curl": "the vertical Berger curl is a fiber operator component, not the full S7 curl",
        "dirac": "D7=D_H^E+Gamma_H D_V+spin-connection/O'Neill corrections after spinor and Clifford conventions",
        "naive_delta_sum_valid": False,
        "existing_berger_operator_status": "exact intrinsic fiber operator locally; coupled associated-bundle component globally; not an exact standalone parent restriction",
    }


def modes_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_berger_fiber_mode_globalization_theorem_v6_0_7"),
        "status": GLOBALIZATION_RESULT,
        "local_expansion": "Phi_a(x,y)=sum_r phi_a^r(x)Y_r(y)",
        "transition": "Y_b=R(g_ab)Y_a implies phi_b=R(g_ab)^-1 phi_a",
        "trivial_representation": "R=1 globalizes as a scalar/base zero mode",
        "nontrivial_representation": "does not define a global scalar coefficient; phi is a section of E_R=P x_R V_R",
        "associated_bundle": "E_R over S4 with covariant derivative induced by omega",
        "global_total_space_scalar": "the contracted equivariant combination can be a scalar on P/S7 even though neither local factor is separately global",
        "gauge_covariant_multiplet": True,
        "nontrivial_fiber_mode_automatically_scalar": False,
    }


def truncation_payload() -> dict[str, Any]:
    gates = [
        {"id": 1, "gate": "global 4+2+1 metric", "result": "PASS_TOTAL_SPACE_WITH_EXTRA_U1_CHOICE_FAIL_SP1_NATURALITY"},
        {"id": 2, "gate": "preferred global U1 reduction", "result": "FAIL_TOPOLOGICALLY_OBSTRUCTED"},
        {"id": 3, "gate": "fiber restriction matches repository Berger metric", "result": "PASS_COEFFICIENT_FORM_NORMALIZATION_OPEN"},
        {"id": 4, "gate": "measure and orientation conventions agree", "result": "FAIL_NORMALIZATION_MAP_OPEN"},
        {"id": 5, "gate": "Hodge star reduces", "result": "PASS_POINTWISE_FORM_V5_PHYSICAL_NORMALIZATION_OPEN"},
        {"id": 6, "gate": "retained operators match", "result": "FAIL_CONNECTION_MIXING_AND_DOMAIN_MAP_OPEN"},
        {"id": 7, "gate": "nontrivial modes globalize", "result": "PASS_ONLY_AS_ASSOCIATED_BUNDLE_SECTIONS"},
        {"id": 8, "gate": "retained sector consistently truncates", "result": "FAIL_EXISTING_SCALAR_ONLY_ENGINE"},
        {"id": 9, "gate": "representation labels match", "result": "FAIL_GENERAL_BRANCHING_AND_INTERTWINER_OPEN"},
        {"id": 10, "gate": "parent action reduces to v5", "result": "FAIL_ACTION_AND_COEFFICIENT_MAP_OPEN"},
        {"id": 11, "gate": "coefficients sourced", "result": "FAIL_PARENT_COEFFICIENTS_UNSOURCED"},
        {"id": 12, "gate": "boundary/internal/spacetime roles distinct", "result": "PASS_FIREWALL"},
    ]
    return {
        **_common("BHSM_berger_consistent_truncation_test_v6_0_7"),
        "status": TRUNCATION_RESULT,
        "definition": "every reduced solution must lift to a parent solution with all discarded-mode equations satisfied",
        "retained_ansatz": "legacy Berger-S3 labels treated as standalone scalar/internal modes",
        "discarded_mode_sources": ["connection curvature", "base covariant derivatives", "stress backreaction", "nonlinear harmonic products", "metric/squashing modes"],
        "nonlinear_closure": False,
        "gauge_covariance": False,
        "exact_scalar_only_truncation": False,
        "associated_bundle_effective_reduction": "OPEN",
        "kill_tests": gates,
    }


def branching_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_so8_hopf_berger_representation_branching_v6_0_7"),
        "status": "LOW_LEVEL_BRANCHING_DERIVED_GENERAL_LEDGER_MAP_OPEN",
        "chain": "SO(8) [ell,0,0,0] -> Sp(2)xSp(1) -> Sp(2)xU(1)",
        "low_levels": low_level_branching(),
        "u1_normalization": "Sp(1) doublet weights +/-1; spin-j weights -2j,-2j+2,...,2j",
        "berger_squashing": "splits states by vertical representation/weight only after the noncanonical U1 axis and operator normalization are declared",
        "parity_orientation": "weight signs reverse with the U1 orientation convention",
        "general_branching_formula": None,
        "normalized_intertwiner": None,
        "eigenvalue_coincidence_sufficient": False,
    }


def ledgers_payload() -> dict[str, Any]:
    rows = [
        {"sector": "leptons", "labels": ["heavy (0,0)", "(5,2)", "(9,3)"], "possible_role": "effective Berger labels q=k-2j and j", "status": "STRUCTURALLY_COMPATIBLE_PARENT_MAP_UNRESOLVED"},
        {"sector": "up", "labels": ["heavy (0,0)", "(6,0)", "(10,1)"], "possible_role": "effective Berger labels q and j", "status": "STRUCTURALLY_COMPATIBLE_PARENT_MAP_UNRESOLVED"},
        {"sector": "down", "labels": ["heavy (0,0)", "(6,3)", "(8,2)"], "possible_role": "effective Berger labels q and j", "status": "STRUCTURALLY_COMPATIBLE_PARENT_MAP_UNRESOLVED"},
        {"sector": "heavy modes", "labels": ["(0,0)"], "possible_role": "trivial vertical representation candidate", "status": "CONDITIONALLY_MAPPABLE_OPERATOR_MAP_OPEN"},
        {"sector": "charged currents", "labels": ["incidence/projector/transport labels"], "possible_role": "associated-bundle intertwiner candidate", "status": "UNRESOLVED"},
        {"sector": "neutral modes", "labels": ["neutral response/projector labels"], "possible_role": "trivial or twisted associated-bundle sector", "status": "UNRESOLVED"},
        {"sector": "scalar/topographic", "labels": ["sigma and profile modes"], "possible_role": "zero mode or associated scalar section", "status": "STRUCTURALLY_COMPATIBLE_PARENT_MAP_UNRESOLVED"},
    ]
    return {
        **_common("BHSM_existing_berger_mode_ledger_parent_map_v6_0_7"),
        "status": "EXISTING_MODE_LEDGERS_REMAIN_EFFECTIVE_NOT_PARENT_DERIVED",
        "rows": rows,
        "operator_map_proved": False,
        "representation_map_proved": False,
        "ledger_values_changed": False,
        "particle_interpretation_promoted": False,
    }


def scalar_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_berger_scalar_action_reduction_v6_0_7"),
        "status": "SCALAR_ASSOCIATED_BUNDLE_REDUCTION_FORM_DERIVED_V5_COEFFICIENT_RECOVERY_BLOCKED",
        "expansion": "Phi=sum_alpha phi_alpha(x)Y_alpha(y), with phi_alpha in E_Ralpha for nontrivial Ralpha",
        "normalization": "N_alpha_beta=integral_F conjugate(Y_alpha)Y_beta dmu_F",
        "base_kinetic": "Z_Phi N_alpha_beta <D phi_alpha,D phi_beta>",
        "vertical_mass_matrix": "Z_Phi integral_F conjugate(Y_alpha) Delta_V Y_beta dmu_F plus curvature/mixing corrections",
        "connection_coupling": "D=d+rho_R(omega)",
        "quartic_overlap": "C_alpha_beta_gamma_delta=integral_F Y_alpha Y_beta Y_gamma Y_delta dmu_F",
        "boundary_terms": "none on closed fiber; base/parent temporal or physical boundary terms remain separate",
        "v5_recovery": "STRUCTURALLY_COMPATIBLE_BUT_BLOCKED",
        "A_ST_parent_formula": "parent mass/curvature terms plus vertical eigenvalue and normalized overlaps; unevaluated",
        "G_ST_parent_formula": "parent quartic coefficient times C_alpha_alpha_alpha_alpha after normalization; unevaluated",
        "A_ST_minus_2_derived": False,
        "G_ST_8_derived": False,
        "sigma_half_derived": False,
    }


def gauge_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_berger_gauge_reduction_readiness_v6_0_7"),
        "status": "NESTED_CONNECTION_GAUGE_ARCHITECTURE_IDENTIFIED_NORMALIZATION_BLOCKED",
        "connection": "omega supplies an Sp(1) connection on associated bundles; the fixed U1 nested quotient is not a global reduction over S4",
        "curvature": "Omega=d omega+omega wedge omega",
        "lower_dimensional_terms": ["horizontal connection kinetic term", "vertical metric moduli", "covariant derivatives of associated modes", "symmetry-breaking anisotropy data"],
        "kinetic_normalization": "sum_k kappa_k times fiber integral, curvature normalization, and representation trace; not evaluated",
        "L1_not_equal_L2": "breaks full right Sp(1) isometry to a Hopf-preserving subgroup but does not derive Standard Model symmetry breaking",
        "geometric_aperture_ready": False,
        "gauge_coupling_derived": False,
        "alpha_calculated": False,
    }


def dirac_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_berger_dirac_reduction_readiness_v6_0_7"),
        "status": "DIRAC_ASSOCIATED_BUNDLE_ARCHITECTURE_IDENTIFIED_SPECTRUM_MAP_BLOCKED",
        "spin_structures": {"S7": "spin, unique", "S4": "spin, unique", "S3": "spin, unique", "associated_bundles": "require chosen Sp(1)/U1 representation and twisting"},
        "formal_decomposition": "D7=D_H^E+Gamma_H D_Berger+spin-connection/O'Neill/curvature corrections",
        "vertical_spectrum": "depends on L1/L2, orientation, and self-adjoint operator convention",
        "chirality": "odd-dimensional S7/S3 have no intrinsic Weyl chirality; lower-dimensional chirality requires the full product/reduction",
        "eta_invariant": "Berger spectral asymmetry is convention- and squashing-dependent and is not evaluated here",
        "boundary_domain": "closed S7/S3 have no boundary; any temporal/physical boundary domain is separate",
        "v5_dirac_pairing": "structurally compatible symbolic target only",
        "fermion_spectrum_derived": False,
        "fermion_masses_derived": False,
    }


def boundary_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_berger_boundary_collar_role_firewall_v6_0_7"),
        "status": "INTERNAL_FIBER_PHYSICAL_BOUNDARY_CONFLATION_REJECTED",
        "hopf_fiber": "closed codimension-four internal orbit with no intrinsic boundary",
        "fiber_normal": "normal bundle inside S7 is horizontal rank four; there is no canonical single outward normal",
        "B8_boundary_normal": "normal to S7 if S7 is selected as a codimension-one B8 boundary",
        "spacetime_normal": "normal in a Lorentzian/canonical physical spacetime interface",
        "objects_distinct": ["internal horizontal normal bundle", "B8 boundary normal", "physical spacetime normal", "collar coordinate"],
        "second_fundamental_form": "fiber embedding data is not the B8 boundary shape operator",
        "collar": "v5 collar cannot be identified with a Hopf fiber coordinate",
        "surface_action_recovered": False,
        "physical_boundary_role": "OPEN",
    }


def lovelock_payload() -> dict[str, Any]:
    rows = [
        {"family": "P1", "terms": ["fiber-volume-weighted base curvature", "fiber curvature/squashing potential", "connection curvature kinetic term", "modulus gradients", "lower-dimensional volume term"], "boundary_completion": "GHY after an actual boundary/domain selection", "status": "STRUCTURE_CONDITIONAL_COEFFICIENTS_OPEN"},
        {"family": "P2", "terms": ["Gauss-Bonnet combinations of base/fiber/connection curvature", "higher polynomial squashing potential", "modulus/connection cross terms"], "boundary_completion": "Myers/Gauss-Bonnet completion after boundary selection", "status": "STRUCTURE_CONDITIONAL_COEFFICIENTS_OPEN"},
        {"family": "P3", "terms": ["cubic Lovelock base/fiber/connection invariants", "higher squashing/modulus interactions"], "boundary_completion": "cubic Lovelock completion after boundary selection", "status": "STRUCTURE_CONDITIONAL_COEFFICIENTS_OPEN"},
    ]
    return {
        **_common("BHSM_lovelock_berger_action_reduction_map_v6_0_7"),
        "status": "LOVELOCK_REDUCTION_STRUCTURE_IDENTIFIED_EXACT_V5_ACTION_NOT_RECOVERED",
        "rows": rows,
        "reduction_measure": "physical fiber integration, not normalized averaging",
        "total_derivatives": "must be combined with the correct parent boundary completion; no fiber boundary term on closed S3",
        "parent_family_selected": None,
        "selected_by_v5_matching": False,
        "v5_action_exactly_recovered": False,
    }


def coefficients_payload() -> dict[str, Any]:
    rows = [
        {"v5_coefficient": "kappa_geom", "parent_formula": "sum_k kappa_k C_geom^(k)(L4,L2,L1,Omega) Vol_F", "missing": ["selected k", "curvature normalization", "boundary role"], "dimension_status": "symbolic", "independently_adjustable": None, "classification": "OPEN"},
        {"v5_coefficient": "kappa_g_i=1/lambda_i", "parent_formula": "sum_k kappa_k C_conn^(k) Vol_F Tr_R(T_i T_i)", "missing": ["selected connection sector", "trace", "mode normalization"], "dimension_status": "symbolic", "independently_adjustable": None, "classification": "OPEN"},
        {"v5_coefficient": "zeta_psi", "parent_formula": "Z_Psi integral_F conjugate(chi_alpha)chi_alpha dmu_F", "missing": ["parent fermion action", "spinor mode", "normalization"], "dimension_status": "symbolic", "independently_adjustable": None, "classification": "OPEN"},
        {"v5_coefficient": "kappa_phi", "parent_formula": "Z_Phi N_alpha_alpha", "missing": ["parent scalar normalization", "selected mode"], "dimension_status": "symbolic", "independently_adjustable": None, "classification": "OPEN"},
        {"v5_coefficient": "A_ST", "parent_formula": "parent mass/curvature projection plus Z_Phi lambda_alpha and mixing terms", "missing": ["parent potential", "operator map", "mode normalization"], "dimension_status": "symbolic", "independently_adjustable": None, "classification": "OPEN_NOT_MINUS_2"},
        {"v5_coefficient": "G_ST", "parent_formula": "G_parent C_alpha_alpha_alpha_alpha after canonical normalization", "missing": ["parent quartic", "overlap tensor", "normalization"], "dimension_status": "symbolic", "independently_adjustable": None, "classification": "OPEN_NOT_8"},
        {"v5_coefficient": "g_ch", "parent_formula": "g_parent integral_F conjugate(chi_a)rho(T)chi_b Y_c dmu_F", "missing": ["parent gauge-spinor coupling", "representations", "intertwiner"], "dimension_status": "symbolic", "independently_adjustable": None, "classification": "OPEN"},
        {"v5_coefficient": "g_neu", "parent_formula": "g_parent times normalized neutral overlap/trace", "missing": ["parent neutral field", "operator", "normalization"], "dimension_status": "symbolic", "independently_adjustable": None, "classification": "OPEN"},
        {"v5_coefficient": "kappa_scale", "parent_formula": "Hessian of reduced Lovelock/modulus effective action", "missing": ["selected parent coefficients", "stationary modulus", "quantum completion"], "dimension_status": "symbolic", "independently_adjustable": None, "classification": "OPEN"},
    ]
    return {
        **_common("BHSM_parent_to_v5_coefficient_map_v6_0_7"),
        "status": "ALL_REDUCED_COEFFICIENT_SOURCES_EXPLICITLY_OPEN",
        "inputs": ["kappa_k", "L4", "L2", "L1", "fiber volume", "connection normalization", "representation traces", "mode normalizations", "overlap tensors"],
        "rows": rows,
        "coefficients_omitted": False,
        "numerical_v5_values_on_parent_side": False,
        "reverse_engineering_used": False,
    }


def scale_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_berger_reduction_scale_hidden_input_audit_v6_0_7"),
        "status": "DIMENSIONLESS_RATIO_ARCHITECTURE_ONLY_COMMON_SCALE_MODULUS_OPEN",
        "dimensionless": ["b=L1/L2", "L2/L4", "L1/L4", "representation labels", "eigenvalue ratios after metric selection"],
        "not_fixed": ["b stationarity", "fiber/base radius ratios", "parent coefficient ratios", "overall common scale L", "absolute unit"],
        "common_rescaling": "(L4,L2,L1)->lambda(L4,L2,L1) leaves all listed radius ratios invariant",
        "curvature_scaling": "R->lambda^-2 R",
        "fiber_volume_scaling": "Vol_F->lambda^3 Vol_F",
        "total_volume_scaling": "Vol_7->lambda^7 Vol_7",
        "operator_eigenvalue_scaling": "lambda_operator->lambda^-2 lambda_operator",
        "unit_radius_physical": False,
        "hidden_inputs": ["fixed U1 subgroup choice", "local gauge/frame", "Euler-angle cover", "orientation", "parent reference metric", "connection normalization", "mode representation", "trace", "action coefficients"],
    }


def report_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_b8_s7_to_berger_s3_reduction_report_v6_0_7"),
        "status": PRIMARY_RESULT,
        "central_answer": "The nested topology and local Berger fiber restriction are exact, and nontrivial fiber modes globalize as associated-bundle sections. However the charge-one Sp(1) Hopf bundle over S4 admits no global U(1) reduction: such a reduction would split E as L plus L^-1, but H2(S4)=0 would force c2(E)=0, contradicting c2(E)=1. Consequently a distinguished Berger axis is not a gauge-independent global field over S4. The legacy scalar-only Berger mode engine also fails the exact consistent-truncation gate because connection, base, stress, nonlinear, representation, action, normalization, and coefficient maps remain open. The full B8/S7-to-Berger-S3 reduction is therefore obstructed.",
        "derived": ["4+2+1 rank split without double counting", "Sp(1)-to-U(1) characteristic-class obstruction", "repository-coframe Berger fiber metric, volume, Ricci, scalar-curvature, and round-limit formulas", "pointwise scaled Hodge product formula", "fiber-mode associated-bundle globalization theorem", "exact low-level ell=0,1,2 branching dimension checks", "boundary/fiber/normal firewall"],
        "derived_conditionally": ["global total-space anisotropic metric after a fixed U1 subgroup choice", "measure pushforward and Hodge decomposition after orientation/normalization", "scalar, gauge, Dirac, and Lovelock reduction structures"],
        "reclassified": ["legacy Berger-S3 engine as an independent homogeneous effective model or future associated-bundle sector", "nontrivial fiber labels as local representation data rather than global scalar labels", "nested CP3 twistor space as P/U1, not a U1 reduction section"],
        "invalidated": ["eta_3 as a globally preferred adjoint direction by coordinate choice", "local fiber restriction as proof of a lower-dimensional theory", "Delta_S7=Delta_S4+Delta_S3 without correction terms", "numeric eigenvalue matching as representation branching", "Hopf fiber as physical B8 boundary", "v5 coefficient recovery by target matching", "absolute-scale generation from unit radius"],
        "still_requiring_new_mathematics": ["associated-bundle field/mode theorem with normalized intertwiners", "general SO8-to-Hopf branching", "controlled effective rather than exact truncation", "selected parent Lovelock action and stationary metric", "parent scalar/gauge/fermion sources", "physical measure and coefficient normalization", "parent-to-v5 action/domain map"],
        "completion_gate_status": "V6_0_7_STOP_GLOBAL_U1_OBSTRUCTION_ASSOCIATED_BUNDLE_REQUIRED",
        "recommended_next_branch": "bhsm-berger-associated-bundle-mode-theorem-v6-0-8",
    }


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    return {
        "bundle": bundle_payload(), "metric": metric_payload(), "u1": u1_payload(),
        "fiber": fiber_payload(), "global": global_payload(), "measure": measure_payload(),
        "hodge": hodge_payload(), "operators": operators_payload(), "modes": modes_payload(),
        "truncation": truncation_payload(), "branching": branching_payload(), "ledgers": ledgers_payload(),
        "scalar": scalar_payload(), "gauge": gauge_payload(), "dirac": dirac_payload(),
        "boundary": boundary_payload(), "lovelock": lovelock_payload(),
        "coefficients": coefficients_payload(), "scale": scale_payload(), "report": report_payload(),
    }


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    payloads = build_artifact_payloads(root)
    written = []
    for key, filename in ARTIFACT_FILES.items():
        path = target / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        written.append(path)
    return written


def reduction_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    report = report_payload()
    report["artifacts"] = {key: f"artifacts/{name}" for key, name in ARTIFACT_FILES.items()}
    return report


def reduction_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# BHSM v6.0.7 B8/S7-to-Berger-S3 Reduction Theorem",
        "",
        f"Primary result: `{report['primary_result']}`.",
        f"Structure-group result: `{report['sp1_to_u1_result']}`.",
        f"Mode result: `{report['mode_globalization_result']}`.",
        f"Truncation result: `{report['consistent_truncation_result']}`.",
        "",
        report["central_answer"],
        "",
        f"Completion gate: `{report['completion_gate_status']}`.",
    ]) + "\n"
