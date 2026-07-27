"""BHSM v6.11.0 scalar-wall fold Morse and sheet-selection theorem.

The stored Puiseux branch and Feynman--Hellmann identity determine the
fixed-mu reduced potential through cubic order.  They imply opposite reduced
Hessian signs: the upper/exterior branch is negative and the lower/core
branch is positive sufficiently close to the fold.  A physical negative-mode
certificate is nevertheless unavailable because the complete gauge-reduced
four-dimensional kinetic norm of the scalar--metric--endpoint collective
vector has not been derived.  No new action term or primitive is introduced.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp


VERSION = "v6.11.0"
SPRINT = "bhsm-scalar-wall-fold-morse-sheet-selection-v6-11-0"
SOURCE_MAIN_SHA = "3e5b8069d8f06852dfdc7d9c8023b441b7486a8b"
V610_HEAD_SHA = "ea79f96b07bc9ca0cee30c42fb5c2e5b2ee1fc0f"

PRIMARY_RESULT = "BHSM_TWO_FOLD_SHEETS_HAVE_OPPOSITE_REDUCED_HESSIAN_SIGN"
KINETIC_RESULT = (
    "BHSM_FOLD_PHYSICAL_KINETIC_NORM_REQUIRES_GRAVITY_CONSTRAINT_REDUCTION"
)
CORE_RESULT = "BHSM_CORE_FACING_SHEET_PHYSICAL_NEGATIVE_MODE_NOT_CERTIFIED"
EXTERIOR_RESULT = "BHSM_EXTERIOR_FOLD_REDUCED_CURVATURE_IS_NEGATIVE"
STRUCTURAL_CASE = 6

ARTIFACT_FILES = {
    "tangent": "BHSM_fold_physical_tangent_and_constraint_quotient_v6_11_0.json",
    "kinetic": "BHSM_fold_collective_kinetic_norm_v6_11_0.json",
    "reduction": "BHSM_fixed_parameter_Lyapunov_Schmidt_reduction_v6_11_0.json",
    "sheet_map": "BHSM_fold_branch_to_sheet_map_v6_11_0.json",
    "morse": "BHSM_fold_Morse_negative_mode_test_v6_11_0.json",
    "report": "BHSM_v6_11_0_hidden_input_and_final_report.json",
}

GUARDS = {
    "tau_J_introduced": False,
    "phenomenological_junction_action_added": False,
    "new_primitive_introduced": False,
    "neutral_transport_used": False,
    "fermion_loop_introduced": False,
    "measured_inputs_used": False,
    "physical_bulk_Dirac_law_introduced": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "lambda_geom_changed": False,
    "global_stability_claimed": False,
}

Q = sp.symbols("q", nonnegative=True, real=True)
DELTA_MU = sp.symbols("delta_mu", real=True)
CHI_1 = sp.symbols("chi_1", positive=True, real=True)
NU_1 = sp.symbols("nu_1", positive=True, real=True)
K_SCALAR = sp.symbols("k_q_scalar", positive=True, real=True)
K_GRAV_RED = sp.symbols("k_q_grav_red", real=True)

CHI_1_DECIMAL = "5.268307871542"
NU_1_DECIMAL = "109.666681740423"
MU_C_DECIMAL = "29.430918352947"
U1_CAP_DECIMAL = "8.923902707116"
U1_JUNCTION_DERIVATIVE_DECIMAL = "-9.124976903426"


def exact_fold_relations() -> dict[str, sp.Expr]:
    """Symbolic relations retained independently of rounded regressions."""
    return {
        "nu_from_chi": sp.Rational(3, 4) * CHI_1**3,
        "cusp_A": NU_1 / 12,
        "FH_coefficient": sp.Rational(1, 4),
    }


def puiseux_derivatives(tau: int) -> dict[str, sp.Expr]:
    """Leading derivatives along one nonlinear solution sheet."""
    if tau not in (-1, 1):
        raise ValueError("tau must be +/-1")
    return {
        "d_mu_dr": tau * NU_1,
        "d_X_dr": tau * CHI_1,
        "d_sigma_dr": sp.Symbol("s") * sp.Symbol("u_1"),
    }


def branch_control_ledger() -> dict[str, Any]:
    return {
        "r": "|epsilon|>=0",
        "scalar_sign": "s=sign(epsilon)=+/-1",
        "sheet": "tau=+/-1",
        "mu": "mu_c+tau nu_1 r+O(r^2)",
        "X": "2+tau chi_1 r+O(r^2)",
        "d_mu_dr": {"tau_plus": "nu_1", "tau_minus": "-nu_1"},
        "d_X_dr": {"tau_plus": "chi_1", "tau_minus": "-chi_1"},
        "action_control": "mu=-A5/Z5",
        "solved_geometry": ["X", "a(rho)", "N(rho)", "rho_J"],
        "fixed_action_coefficients": [
            "kappa_0",
            "kappa_1",
            "Z5",
            "G5",
            "C_partial",
            "all B1 coefficients",
        ],
        "branch_tangent_parameter_changing": True,
        "reason": "d_mu_tau/dr=tau nu_1 is nonzero",
        "d2_onshell_Gamma_dr2_used_as_physical_Hessian": False,
    }


def direction_classification() -> list[dict[str, Any]]:
    """Keep the four displacement/amplitude notions disjoint."""
    return [
        {
            "id": "A",
            "direction": "isolated infinite-wall translation -sigma_0' delta b",
            "classification": "not available at sigma_c=0 and not an exact finite-cap zero mode",
            "gauge": False,
            "parameter_changing": False,
            "boundary_condition_changing": True,
            "admissible_physical": False,
        },
        {
            "id": "B",
            "direction": "finite endpoint displacement delta rho_J",
            "classification": "coordinate dependent until combined with trace and lapse corrections",
            "gauge": "contains a normal-diffeomorphism component",
            "parameter_changing": False,
            "boundary_condition_changing": "unless transversality conditions are imposed",
            "admissible_physical": False,
        },
        {
            "id": "C",
            "direction": "d Phi_tau(r)/dr",
            "classification": "solution-branch tangent",
            "gauge": False,
            "parameter_changing": True,
            "boundary_condition_changing": False,
            "admissible_physical": False,
        },
        {
            "id": "D",
            "direction": "fixed-mu fold amplitude after constraint and gauge projection",
            "classification": "candidate physical one-sided collective vector",
            "gauge": False,
            "parameter_changing": False,
            "boundary_condition_changing": False,
            "admissible_physical": "kinematically yes; positive kinetic norm unresolved",
        },
    ]


def field_constraint_ledger() -> dict[str, Any]:
    """Smallest actual scalar-gravity field and quotient space."""
    return {
        "raw_vector": [
            "delta sigma(t)",
            "delta a(t)",
            "delta N(t)",
            "delta rho_J",
            "delta X",
            "delta mu",
        ],
        "dynamical_or_solved": ["sigma", "a", "X", "rho_J"],
        "constraints": [
            "delta_N L1D=0: linearized normal/Hamiltonian constraint",
            "delta sigma_J=0",
            "delta a_J=0",
            "delta[a'_J-X/2]=0 including endpoint displacement",
            "regular pole traces",
        ],
        "gauge": "radial reparameterization generated by xi(t)",
        "gauge_action": {
            "delta_xi_sigma": "xi sigma_0'=0 at the critical sigma_0=0",
            "delta_xi_a": "xi a_0'",
            "delta_xi_N": "(N_0 xi)'",
            "delta_xi_rho_J": "-xi_J",
            "delta_xi_X": 0,
        },
        "physical_space": "T_phys=ker C/im G",
        "fixed_domain_gauge": "t in [0,1], rho=ell(X)t, delta rho_J=0",
        "moving_endpoint_gauge": "proper-normal coordinate with explicit delta rho_J",
        "gauge_equivalence": (
            "v6.1.7 proves fixed/moving agreement after matching physical endpoint data"
        ),
        "gauge_kernel_inverted": False,
    }


def finite_cap_tangent_ledger() -> dict[str, Any]:
    """Leading finite-cap vector after removing the parameter component."""
    return {
        "critical_background": {
            "a_0": "sqrt(2) sin(pi t/4)",
            "N_0": "ell_0=pi/4",
            "sigma_0": 0,
            "X_c": 2,
        },
        "raw_branch_tangent": (
            "Z_branch=(s u_1, tau a_1, tau N_1, 0, "
            "tau chi_1; tau nu_1)"
        ),
        "parameter_component": "delta mu=tau nu_1",
        "fixed_control_projection": (
            "discard the external delta-mu component; differentiate fields "
            "with the action coefficient mu held fixed"
        ),
        "a_1": (
            "chi_1[a_0/4-sqrt(2)t cos(pi t/4)/4]"
        ),
        "N_1": "-chi_1/4",
        "ell_1": "-chi_1/4",
        "delta_X": "tau chi_1",
        "scalar_component": "s u_1",
        "endpoint_trace": {
            "u_1(rho_J)": 0,
            "a_1(rho_J)": 0,
            "junction_derivative": "delta a'_J=delta X/2 after domain correction",
        },
        "constraint_correction": (
            "a_1,N_1,ell_1 and the endpoint/domain term are the stored "
            "linearized gravity/lapse correction"
        ),
        "constraint_satisfied": True,
        "non_gauge_witness": "delta X=tau chi_1 changes intrinsic R4 curvature",
        "normal_diffeomorphism_removed": True,
        "final_candidate": (
            "Z_q^phys=[s u_1,tau a_1,tau N_1,0,tau chi_1] mod im G"
        ),
        "coordinate": "q=r=|epsilon| on each sheet; s records the Z2 scalar sign",
        "literal_wall_displacement_b": False,
    }


def scalar_kinetic_ledger() -> dict[str, Any]:
    """Exact positive scalar part and the named missing reduced gravity part."""
    return {
        "metric": "ds5^2=N^2 d rho^2+a^2 h_mu_nu dx^mu dx^nu",
        "two_cap_scalar_formula": (
            "k_q^scalar=2 Z5 integral_0^rhoJ N a^2 "
            "(partial_q sigma)^2 d rho"
        ),
        "critical_formula": "2 integral_0^(pi/4) a_0^2 u_1^2 d rho",
        "normalization": "integral a_0^4 u_1^2 d rho=1 per cap",
        "bound": (
            "0<a_0^2<=1 implies a_0^2>=a_0^4, hence k_q^scalar>=2"
        ),
        "scalar_sign": "strictly positive",
        "gravity_raw": (
            "P1 kinetic form on delta a and the four-dimensional metric "
            "representative carrying delta X"
        ),
        "constraint_correction": (
            "lapse/shift Schur complement after radial gauge removal"
        ),
        "boundary_contribution": (
            "GHY+B1 derivative terms under x-dependent endpoint/metric variation"
        ),
        "endpoint_contribution": (
            "transversality contribution for the moving endpoint representation"
        ),
        "known_zero": (
            "Z_partial does not contribute: sigma_partial is a distinct B1 "
            "field and no action/domain map identifies it with q"
        ),
        "missing_exact_term": (
            "k_q^grav,red=<Z_g,K_P1+GHY+B1 Z_g>"
            "-<Z_g,K_gC K_CC^-1 K_Cg Z_g>"
        ),
        "missing_symbol": "k_q_grav_red",
        "total": "k_q=k_q^scalar+k_q^grav,red",
        "total_sign": None,
        "k_q_set_to_one": False,
        "ghost_status": "unresolved until k_q^grav,red is computed",
        "result": KINETIC_RESULT,
    }


def reduced_action(tau: int) -> sp.Expr:
    """Fixed-mu Lyapunov--Schmidt action through cubic order."""
    if tau not in (-1, 1):
        raise ValueError("tau must be +/-1")
    return sp.Rational(1, 4) * DELTA_MU * Q**2 - tau * NU_1 * Q**3 / 6


def reduced_stationarity(tau: int) -> sp.Expr:
    return sp.factor(sp.diff(reduced_action(tau), Q))


def branch_substitution(tau: int) -> dict[sp.Symbol, sp.Expr]:
    if tau not in (-1, 1):
        raise ValueError("tau must be +/-1")
    return {DELTA_MU: tau * NU_1 * Q}


def onshell_cusp(tau: int) -> sp.Expr:
    return sp.simplify(reduced_action(tau).subs(branch_substitution(tau)))


def fixed_control_hessian(tau: int) -> sp.Expr:
    """Second q derivative at fixed mu, then evaluated on the branch."""
    return sp.simplify(
        sp.diff(reduced_action(tau), Q, 2).subs(branch_substitution(tau))
    )


def lyapunov_schmidt_ledger() -> dict[str, Any]:
    return {
        "kernel": "u_1, normalized by integral a_0^4 u_1^2=1",
        "amplitude": "q=r=|epsilon|; scalar signs +/- share one reduced action",
        "orthogonal_correction": "w(q,mu) with <u_1,w>_(a0^4)=0",
        "complement_equation": (
            "Q_perp delta_Gamma/delta_Phi=0 eliminates w and the solved "
            "metric/endpoint variables order by order"
        ),
        "fixed_control": "mu; all action and B1 coefficients fixed",
        "X_status": "solved induced-curvature variable, eliminated separately on tau sheets",
        "Feynman_Hellmann": (
            "partial_mu Gamma_hat=X^-2 integral a^4 sigma^2 d rho"
        ),
        "critical_FH": "partial_mu Gamma_hat=q^2/4+O(q^3)",
        "unfolding_coefficient": "coefficient of delta_mu q^2 is 1/4",
        "reduced_action": (
            "Gamma_red,tau=Gamma_c+(delta_mu/4)q^2"
            "-tau(nu_1/6)q^3+O(q^4,delta_mu q^3)"
        ),
        "stationarity": (
            "partial_q Gamma_red=(q/2)(delta_mu-tau nu_1 q)+O(q^3)"
        ),
        "branch_equation": "delta_mu=tau nu_1 q+O(q^2)",
        "onshell_cusp": "tau(nu_1/12)q^3+O(q^4)",
        "cusp_A": "nu_1/12",
        "cubic_source": (
            "one-sided elimination of the double-root X constraint; it is "
            "not an odd term in signed epsilon"
        ),
        "fixed_mu_hessian": "-tau(nu_1/2)q+O(q^2)",
        "d2_onshell_dr2_substituted": False,
        "remainder": "O(q^4,delta_mu q^3)",
    }


def sheet_map_ledger() -> dict[str, Any]:
    return {
        "tau_plus": {
            "X": "2+chi_1 q+O(q^2)>2",
            "mu": "mu_c+nu_1 q+O(q^2)",
            "curvature_root": "upper/high-curvature",
            "BHSM_sheet": "exterior/spacetime-facing (adopted v6.2 map)",
        },
        "tau_minus": {
            "X": "2-chi_1 q+O(q^2)<2",
            "mu": "mu_c-nu_1 q+O(q^2)",
            "curvature_root": "lower/low-curvature",
            "BHSM_sheet": "core-facing (adopted v6.2 map)",
        },
        "normal_reversal": (
            "flips signed K and sigma normal derivative but leaves intrinsic X "
            "and tau unchanged"
        ),
        "rho_reversal": (
            "exchanges coordinate orientation and endpoint representation but "
            "does not exchange X>2 with X<2"
        ),
        "orientation_invariant_classifier": "sign(X-2)=tau",
        "map_status": (
            "geometric upper/lower map derived from X; exterior/core naming "
            "inherits the explicit v6.2 BHSM sheet axiom"
        ),
    }


def schur_complement(
    h_pp: sp.MatrixBase,
    h_pc: sp.MatrixBase,
    h_cc: sp.MatrixBase,
) -> sp.ImmutableMatrix:
    """Constraint reduction only after the supplied block is invertible."""
    if h_cc.det() == 0:
        raise ValueError("gauge kernels must be removed before H_CC inversion")
    return sp.ImmutableMatrix(
        sp.simplify(h_pp - h_pc * h_cc.inv() * h_pc.T.conjugate())
    )


def formal_physical_hessian() -> sp.ImmutableMatrix:
    hqq, hqx, hxx = sp.symbols("h_qq h_qx h_xx", real=True)
    c1, c2, hc = sp.symbols("c_1 c_2 h_c", real=True, nonzero=True)
    h_pp = sp.ImmutableMatrix([[hqq, hqx], [hqx, hxx]])
    h_pc = sp.ImmutableMatrix([[c1], [c2]])
    h_cc = sp.ImmutableMatrix([[hc]])
    return schur_complement(h_pp, h_pc, h_cc)


def morse_ledger() -> dict[str, Any]:
    return {
        "reduced_hessians": {
            "tau_plus_exterior": "-(nu_1/2)q+O(q^2)",
            "tau_minus_core": "+(nu_1/2)q+O(q^2)",
        },
        "asymptotic_sign": {
            "exterior": "negative for sufficiently small q>0",
            "core": "positive for sufficiently small q>0",
        },
        "kinetic_norm": "k_q=k_q^scalar+k_q^grav,red",
        "kinetic_sign": None,
        "Rayleigh_quotients": {
            "exterior": "[-nu_1 q/2+O(q^2)]/k_q",
            "core": "[+nu_1 q/2+O(q^2)]/k_q",
        },
        "physical_tachyon_certified": False,
        "ghost_certified": False,
        "modulus_certified": False,
        "Morse_index_lower_bound": None,
        "reason_no_minmax_certificate": (
            "Rayleigh--Ritz requires the unresolved positive total kinetic norm"
        ),
        "core_negative_mode": False,
        "core_result": CORE_RESULT,
        "exterior_result": EXTERIOR_RESULT,
        "upper_stability": (
            "not certified; only one reduced potential direction is negative "
            "and its kinetic norm is unresolved"
        ),
        "global_stability": False,
        "result": PRIMARY_RESULT,
    }


def closure_ledger() -> dict[str, Any]:
    return {
        "existing_action_cusp": True,
        "fixed_parameter_potential_curvature": True,
        "complete_kinetic_norm": False,
        "sheet_map": True,
        "core_rejection": False,
        "tau_J_needed": False,
        "tau_J_reason": (
            "the potential result follows from P1+GHY+B1+scalar; the remaining "
            "task is a reduction of existing kinetic terms, not a new source"
        ),
        "existing_action_sufficient_in_principle": True,
        "repository_calculation_complete": False,
        "exact_active_construction": (
            "derive k_q^grav,red from the x-dependent P1+GHY+B1 scalar-sector "
            "quadratic action after lapse/shift elimination and gauge quotient"
        ),
        "neutral_statement": (
            "static junction mixing remains rejected; propagation-dependent "
            "compact-mode transport is a separate future target"
        ),
        "structural_case": STRUCTURAL_CASE,
    }


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[sp.sstr(entry) for entry in row] for row in matrix.tolist()]


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "v6_10_head_sha": V610_HEAD_SHA,
        "primary_result": PRIMARY_RESULT,
        "preserved_results": [
            "BHSM_Y_SIGMA_EXP_MINUS_BETA_REJECTED_BY_CANONICAL_NORMALIZATION",
            "BHSM_AVAILABLE_C_BHSM_HAS_ZERO_LIGHT_HEAVY_COUPLING",
            "BHSM_AUXILIARY_INDEX_ONE_CERTIFIED",
            "BHSM_MINIMAL_WELL_POSED_ACTION_HAS_NO_JUNCTION_MIXING_TERM",
        ],
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "tangent": {
            **_common("BHSM_fold_physical_tangent_and_constraint_quotient_v6_11_0"),
            "status": "BHSM_FOLD_FIXED_CONTROL_TANGENT_CLASSIFIED",
            "frozen_coefficients": {
                "chi_1": CHI_1_DECIMAL,
                "nu_1": NU_1_DECIMAL,
                "mu_c": MU_C_DECIMAL,
                "u1_cap": U1_CAP_DECIMAL,
                "u1_junction_derivative": U1_JUNCTION_DERIVATIVE_DECIMAL,
                "exact_relation": "nu_1=3 chi_1^3/4",
            },
            "branches": branch_control_ledger(),
            "directions": direction_classification(),
            "field_constraints": field_constraint_ledger(),
            "finite_cap_tangent": finite_cap_tangent_ledger(),
        },
        "kinetic": {
            **_common("BHSM_fold_collective_kinetic_norm_v6_11_0"),
            "status": KINETIC_RESULT,
            "kinetic": scalar_kinetic_ledger(),
        },
        "reduction": {
            **_common("BHSM_fixed_parameter_Lyapunov_Schmidt_reduction_v6_11_0"),
            "status": "BHSM_FIXED_MU_FOLD_REDUCED_ACTION_DERIVED_TO_CUBIC_ORDER",
            "reduction": lyapunov_schmidt_ledger(),
            "exact": {
                "Gamma_plus": sp.sstr(reduced_action(1)),
                "Gamma_minus": sp.sstr(reduced_action(-1)),
                "stationarity_plus": sp.sstr(reduced_stationarity(1)),
                "stationarity_minus": sp.sstr(reduced_stationarity(-1)),
                "cusp_plus": sp.sstr(onshell_cusp(1)),
                "cusp_minus": sp.sstr(onshell_cusp(-1)),
                "B_plus": sp.sstr(fixed_control_hessian(1)),
                "B_minus": sp.sstr(fixed_control_hessian(-1)),
            },
        },
        "sheet_map": {
            **_common("BHSM_fold_branch_to_sheet_map_v6_11_0"),
            "status": "BHSM_FOLD_BRANCH_TO_GEOMETRIC_SHEET_MAP_DERIVED",
            "map": sheet_map_ledger(),
        },
        "morse": {
            **_common("BHSM_fold_Morse_negative_mode_test_v6_11_0"),
            "status": PRIMARY_RESULT,
            "formal_H_phys": _matrix_strings(formal_physical_hessian()),
            "morse": morse_ledger(),
        },
        "report": {
            **_common("BHSM_v6_11_0_hidden_input_and_final_report"),
            "status": PRIMARY_RESULT,
            "central_answer": (
                "Feynman--Hellmann matching converts the on-shell cusp into a "
                "fixed-mu reduced action and proves opposite leading Hessian "
                "signs. The exterior/upper branch is negative and the "
                "core/lower branch positive. No physical negative mode is "
                "certified because k_q^grav,red is not yet derived."
            ),
            "closure": closure_ledger(),
            "hidden_inputs": [],
            "missing_calculation_not_primitive": (
                "x-dependent gravitational scalar constraint reduction for "
                "k_q^grav,red"
            ),
        },
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def artifact_bytes() -> dict[str, bytes]:
    payloads = artifact_payloads()
    return {
        ARTIFACT_FILES[key]: deterministic_json(payload).encode("utf-8")
        for key, payload in payloads.items()
    }


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for filename, content in artifact_bytes().items():
        path = target / filename
        path.write_bytes(content)
        paths.append(path)
    return paths
