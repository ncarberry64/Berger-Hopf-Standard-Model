"""BHSM v6.10.0 action-selected junction-functional theorem.

The theorem distinguishes required variational completion from optional
junction invariants.  The currently adopted P1+GHY+B1+matter package contains
neither a codimension-two gravitational joint nor a first-order matter
boundary generator.  Consequently it selects no member of the v6.7 U(1)
domain family and generates no light-heavy junction block.  The exact
surviving family symmetry is C3; its Hermitian commutant is the circulant
algebra, so nonuniversal optional terms are permitted but introduce new
coefficients rather than being derived.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp


VERSION = "v6.10.0"
SPRINT = "bhsm-action-selected-junction-functional-v6-10-0"
SOURCE_MAIN_SHA = "9aec8bb759326e08e2215c0c8e11c3458f761ddd"
V690_SCIENTIFIC_SHA = "d2a084b39babff72550fb0eac3d00fbd01afc7aa"

PRIMARY_RESULT = "BHSM_MINIMAL_WELL_POSED_ACTION_HAS_NO_JUNCTION_MIXING_TERM"
BENDING_RESULT = "BHSM_JUNCTION_BENDING_REQUIRES_ONE_BOSONIC_CORNER_INVARIANT"
DOMAIN_RESULT = "BHSM_CURRENT_ACTION_SELECTS_NO_SELF_ADJOINT_JUNCTION_DOMAIN"
TRIALITY_RESULT = "BHSM_C3_HERMITIAN_COMMUTANT_IS_CIRCULANT"
STRUCTURAL_CASE = 7

ARTIFACT_FILES = {
    "invariants": "BHSM_junction_invariant_and_triality_commutant_v6_10_0.json",
    "variation": "BHSM_junction_variation_and_selected_domain_v6_10_0.json",
    "projection": "BHSM_junction_light_heavy_projection_v6_10_0.json",
    "dispersion": "BHSM_junction_dispersion_and_K_prop_v6_10_0.json",
    "bending": "BHSM_junction_bending_sheet_response_v6_10_0.json",
    "report": "BHSM_v6_10_0_hidden_input_and_final_report.json",
}

GUARDS = {
    "measured_inputs_used": False,
    "fitted_parameters_used": False,
    "sector_dependent_coupling_introduced": False,
    "physical_bulk_Dirac_parent_law_introduced": False,
    "fermion_loop_inserted": False,
    "junction_tension_assumed": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "lambda_geom_universality_changed": False,
    "full_BHSM_claimed": False,
}

P, M_H = sp.symbols("p M_H", positive=True, real=True)
A, X, Y = sp.symbols("a x y", real=True)
ALPHA = sp.symbols("alpha_J", real=True)
TAU_J = sp.symbols("tau_J", real=True)
K_B, B_PLUS, B_MINUS = sp.symbols(
    "k_b B_plus B_minus", real=True
)


def gamma_n() -> sp.ImmutableMatrix:
    """Repository Gamma_n=sigma_x."""
    return sp.ImmutableMatrix([[0, 1], [1, 0]])


def gamma_star() -> sp.ImmutableMatrix:
    """Repository beta-independent collar partner Gamma_star=sigma_y."""
    return sp.ImmutableMatrix([[0, -sp.I], [sp.I, 0]])


def collar_grading() -> sp.ImmutableMatrix:
    """K=i Gamma_n Gamma_star=-sigma_z in repository conventions."""
    return sp.ImmutableMatrix(sp.I * gamma_n() * gamma_star())


def green_form_matrix() -> sp.ImmutableMatrix:
    """Reduced v6.7 signature-(1,1) Green form."""
    return sp.ImmutableMatrix([[1, 0], [0, -1]])


def triality_cycle() -> sp.ImmutableMatrix:
    """Exact C3 family generator P0->P1->P2->P0."""
    return sp.ImmutableMatrix([[0, 0, 1], [1, 0, 0], [0, 1, 0]])


def triality_commutant_basis() -> tuple[sp.ImmutableMatrix, ...]:
    """Real Hermitian basis of Comm(C3)."""
    cycle = triality_cycle()
    return (
        sp.ImmutableMatrix(sp.eye(3)),
        sp.ImmutableMatrix(cycle + cycle**2),
        sp.ImmutableMatrix(sp.I * (cycle - cycle**2)),
    )


def triality_commutant() -> sp.ImmutableMatrix:
    """General Hermitian C3 commutant with three real coefficients."""
    basis = triality_commutant_basis()
    return sp.ImmutableMatrix(A * basis[0] + X * basis[1] + Y * basis[2])


def triality_fourier() -> sp.ImmutableMatrix:
    """Unitary exact Fourier diagonalizer, columns ordered (1,omega,omega^2)."""
    omega = sp.exp(2 * sp.pi * sp.I / 3).expand(complex=True)
    return sp.ImmutableMatrix(
        [
            [1, 1, 1],
            [1, omega**2, omega],
            [1, omega, omega**2],
        ]
    ) / sp.sqrt(3)


def triality_eigenvalues() -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    """Exact singlet and two complex-character eigenvalues."""
    return (
        A + 2 * X,
        A - X - sp.sqrt(3) * Y,
        A - X + sp.sqrt(3) * Y,
    )


def commutant_equations_hold(matrix: sp.MatrixBase) -> bool:
    """Test exact Hermiticity and commutation with the surviving generator."""
    cycle = triality_cycle()
    return bool(
        matrix == matrix.T.conjugate()
        and sp.simplify(matrix * cycle - cycle * matrix) == sp.zeros(3)
    )


def geometry_ledger() -> dict[str, Any]:
    """Classify the stored variational geometry before adding any invariant."""
    return {
        "bulk": "P1=(1/2) integral_M sqrt|G| (kappa_0+kappa_1 R)",
        "boundary_count": 1,
        "boundary": "one smooth oriented S7 boundary with a Gaussian-normal collar",
        "GHY": "kappa_1 integral_boundary epsilon_n K sqrt|h|",
        "GHY_coefficient": "fixed by kappa_1 when P1 is chosen",
        "GHY_classification": "required Dirichlet variational completion, not tension",
        "B1": "provisional intrinsic M4 boundary action/condition",
        "B1_parent_status": "not derived from P1",
        "cap_collar_joint": False,
        "intersecting_boundary_pieces": False,
        "codimension_two_corner": False,
        "joint_angle_eta": None,
        "normal_pair": None,
        "moving_endpoint": True,
        "moving_endpoint_status": (
            "v6.1.7 includes transversality/shape response in the fixed-B1 "
            "cap problem; it does not create a second boundary face"
        ),
        "junction_hypersurface": (
            "Sigma_J is the cap endpoint trace locus used by the reduced "
            "matter problem, not a declared nonsmooth gravitational corner"
        ),
        "sheet_orientation": (
            "upper/lower Puiseux branches have opposite leading orientation; "
            "orientation alone does not fix a second variation"
        ),
        "required_Hayward_joint_term": False,
        "reason_no_required_joint": (
            "a coefficient-locked gravitational joint term requires two "
            "declared boundary faces and their relative angle; neither exists"
        ),
    }


def trace_ledger() -> dict[str, Any]:
    """Define the available trace map and record missing mode data."""
    return {
        "junction": "Sigma_J",
        "induced_metric": "gamma_ab=X_J^* h_ab",
        "measure": "dmu_J=sqrt(|gamma|) d^(dim Sigma_J)y",
        "orientation": "outward cap normal n; n->-n reverses Gamma_n and Green form",
        "trace_map": "T_J:Dom(C_BHSM)->H_J=H^(1/2)(Sigma_J,E|Sigma_J)",
        "two_side_trace": "(T_cap Psi,T_collar Psi) only after a second side is declared",
        "inner_product": "<u,v>_J=integral_SigmaJ dmu_J u^dagger v",
        "symplectic_form": "omega(u,v)=<u,J_n v>_J; J_n=diag(1,-1)",
        "v6_7_zero_mode": {
            "normalization": "bulk cap L2 norm exported",
            "junction_probability": "quarter-cap integrated probability exported",
            "point_trace": False,
            "normal_derivative": False,
        },
        "v6_7_first_heavy": {
            "gap": True,
            "point_trace": False,
            "normal_derivative": False,
            "normalized_eigenvector": False,
        },
        "bulk_orthogonality_implies_trace_orthogonality": False,
        "trace_overlap_evaluable_for_optional_operator": False,
    }


def invariant_ledger() -> list[dict[str, Any]]:
    """Lowest-order local junction basis and its source classification."""
    return [
        {
            "id": "P1_GHY",
            "sector": "bosonic",
            "density": "epsilon_n K",
            "present": True,
            "required": True,
            "coefficient": "kappa_1",
            "coefficient_fixed": True,
            "junction_localized": False,
            "classification": "smooth-boundary variational completion",
        },
        {
            "id": "Hayward_joint",
            "sector": "bosonic",
            "density": "eta",
            "present": False,
            "required": False,
            "coefficient": "kappa_1 if a genuine P1 corner is declared",
            "coefficient_fixed": "conditional",
            "junction_localized": True,
            "classification": "inapplicable: no normal pair or joint angle",
        },
        {
            "id": "junction_volume",
            "sector": "bosonic",
            "density": "1",
            "present": False,
            "required": False,
            "coefficient": "tau_J",
            "coefficient_fixed": False,
            "junction_localized": True,
            "classification": "optional physical joint energy; new primitive",
        },
        {
            "id": "junction_shape_quadratic",
            "sector": "bosonic",
            "density": "K^2 or Tr(S^2)",
            "present": False,
            "required": False,
            "coefficient": "c_K2 or c_S",
            "coefficient_fixed": False,
            "junction_localized": True,
            "classification": "optional higher-derivative bending invariant",
        },
        {
            "id": "matter_scalar",
            "sector": "fermionic",
            "density": "bar(Psi)(I tensor J_C3)Psi",
            "present": False,
            "required": False,
            "coefficient": "a_I,x_I,y_I",
            "coefficient_fixed": False,
            "junction_localized": True,
            "classification": "optional same-kinetic-sector bilinear",
        },
        {
            "id": "matter_normal",
            "sector": "fermionic",
            "density": "bar(Psi)(Gamma_n tensor J_C3)Psi",
            "present": False,
            "required": False,
            "coefficient": "a_n,x_n,y_n",
            "coefficient_fixed": False,
            "junction_localized": True,
            "classification": "optional orientation-odd trace bilinear",
        },
        {
            "id": "matter_wall",
            "sector": "fermionic",
            "density": "bar(Psi)(sigma_J Gamma_star tensor J_C3)Psi",
            "present": False,
            "required": False,
            "coefficient": "a_star,x_star,y_star",
            "coefficient_fixed": False,
            "junction_localized": True,
            "classification": "optional wall-even product after paired Z2 transformation",
        },
        {
            "id": "matter_grading",
            "sector": "fermionic",
            "density": "bar(Psi)(K tensor J_C3)Psi",
            "present": False,
            "required": False,
            "coefficient": "a_K,x_K,y_K",
            "coefficient_fixed": False,
            "junction_localized": True,
            "classification": "optional grading bilinear",
        },
    ]


def no_duplicate_invariants() -> bool:
    ids = [row["id"] for row in invariant_ledger()]
    return len(ids) == len(set(ids))


def cayley_unitary(alpha: sp.Expr = ALPHA) -> sp.Expr:
    """Conditional scalar Cayley chart for an explicitly chosen polarization.

    This convention is *not* selected by the stored action.  It is fixed here
    by declaring the graph equation (1+i alpha)psi_-=(1-i alpha)psi_+.
    """
    value = sp.sympify(alpha)
    return sp.simplify((1 - sp.I * value) / (1 + sp.I * value))


def maximal_isotropic_trace(unitary: sp.Expr) -> sp.ImmutableMatrix:
    """Graph trace (psi_+,psi_-)=(1,U)/sqrt(2)."""
    return sp.ImmutableMatrix([1, unitary]) / sp.sqrt(2)


def green_flux(trace: sp.MatrixBase) -> sp.Expr:
    return sp.simplify((trace.T.conjugate() * green_form_matrix() * trace)[0])


def domain_ledger() -> dict[str, Any]:
    """First-variation result for the current and optional action packages."""
    return {
        "Green_identity": (
            "<Psi,D Phi>-<D Psi,Phi>=<T_J Psi,J_n T_J Phi>_J"
        ),
        "J_n": [["1", "0"], ["0", "-1"]],
        "trace_split": "H_J=H_+ direct_sum H_-",
        "maximal_isotropic_graph": "psi_-=U psi_+, U in U(1)",
        "current_S_J_F": 0,
        "current_first_variation": (
            "bulk Green form only; stationarity requires choosing a maximal-"
            "isotropic domain but supplies no graph unitary"
        ),
        "unique_domain_selected": False,
        "finite_family_selected": False,
        "remaining_family": "U(1)",
        "conditional_Cayley_convention": (
            "(1+i alpha_J)psi_-=(1-i alpha_J)psi_+, "
            "U=(1-i alpha_J)/(1+i alpha_J)"
        ),
        "Cayley_status": (
            "a chart after an extra boundary polarization and real alpha_J "
            "are declared; not a consequence of P1+GHY+B1+S_F"
        ),
        "normal_reversal": "J_n->-J_n, alpha_J->-alpha_J, U->U^-1",
        "flux_cancellation": "holds for every unitary U",
        "self_adjointness": "every maximal-isotropic graph is self-adjoint in the reduced problem",
        "ellipticity": "not established for the undeclared full tangential operator",
        "charge_preservation": "conditional U commutes with Q_em and Y_BH",
        "triality_covariance": "conditional U belongs to Comm(C3)",
        "conjugation": "U maps to conjugate U",
        "Callias_compatibility": (
            "index-one auxiliary orientation is compatible with the diagnostic "
            "member but does not select U"
        ),
        "result": DOMAIN_RESULT,
    }


def current_junction_operator() -> sp.ImmutableMatrix:
    """Action-derived family operator: absent exactly."""
    return sp.ImmutableMatrix(sp.zeros(3))


def optional_junction_operator() -> sp.ImmutableMatrix:
    """Most general symmetry-compatible family factor, coefficient dependent."""
    return triality_commutant()


def light_heavy_blocks(
    family_operator: sp.MatrixBase | None = None,
) -> dict[str, sp.ImmutableMatrix]:
    """First-heavy truncation using a junction trace insertion."""
    v_lh = current_junction_operator() if family_operator is None else sp.Matrix(family_operator)
    return {
        "H_LL": sp.ImmutableMatrix(P * sp.eye(3)),
        "H_HH": sp.ImmutableMatrix((P + M_H) * sp.eye(3)),
        "V_LH": sp.ImmutableMatrix(v_lh),
        "V_HL": sp.ImmutableMatrix(v_lh.T.conjugate()),
    }


def projection_ledger() -> dict[str, Any]:
    """Project only the term that the current action actually contains."""
    return {
        "definition": "j_01=(T_J f_0)^dagger M_J (T_J f_1)",
        "bulk_overlap_substituted": False,
        "current_M_J": "0",
        "current_j_01": 0,
        "current_V_LH": "0_3",
        "V_HL_equals_V_LH_adjoint": True,
        "zero_reason": "operator absence, not bulk L2 orthogonality",
        "parity_forces_all_optional_terms_zero": False,
        "optional_C3_factorization": "V_LH=j_01[a I+x(C+C^2)+iy(C-C^2)]",
        "optional_trace_status": (
            "not evaluable: v6.7 exports neither point trace nor normalized "
            "first-heavy eigenvector"
        ),
        "optional_coefficient_status": "the real coefficients a,x,y are not action fixed",
        "first_heavy_truncation": "same three-copy f1 level used in v6.9",
        "result": PRIMARY_RESULT,
    }


def kinetic_operator() -> sp.ImmutableMatrix:
    """Two-chirality algebra audit H0=p K, not a new bulk parent law."""
    return sp.ImmutableMatrix(P * collar_grading())


def commutator(left: sp.MatrixBase, right: sp.MatrixBase) -> sp.ImmutableMatrix:
    return sp.ImmutableMatrix(sp.simplify(left * right - right * left))


def anticommutator(left: sp.MatrixBase, right: sp.MatrixBase) -> sp.ImmutableMatrix:
    return sp.ImmutableMatrix(sp.simplify(left * right + right * left))


def mass_like_squared_dispersion(mass: sp.Expr = ALPHA) -> sp.ImmutableMatrix:
    """(p K+m Gamma_star)^2=(p^2+m^2)I."""
    h_eff = kinetic_operator() + sp.sympify(mass) * gamma_star()
    return sp.ImmutableMatrix(sp.simplify(h_eff**2))


def dispersion_ledger() -> dict[str, Any]:
    return {
        "algebra_audit": "H0=p K on the declared rank-two collar factor",
        "same_sector": {
            "operators": ["I", "K"],
            "commutator_with_H0": 0,
            "classification": "additive E^0 or kinetic-sign/velocity response",
            "K_prop": None,
        },
        "opposite_sector": {
            "operators": ["Gamma_n", "Gamma_star"],
            "anticommutator_with_H0": 0,
            "conditional_dispersion": "E_i^2=p^2+mu_i",
            "mu_i": "eigenvalues of M_eff M_eff^dagger",
            "high_energy": "E_i=p+mu_i/(2p)+O(p^-3)",
            "status": "symmetry permitted but absent and coefficient dependent",
        },
        "current_operator": 0,
        "current_energy_shift": 0,
        "current_K_prop": None,
        "relative_neutral_phase": 0,
        "mass_squared_classification": "not generated",
        "measured_input": [],
        "result": "BHSM_JUNCTION_K_PROP_REJECTED_FOR_CURRENT_ACTION",
    }


def constraint_reduced_hessian() -> sp.ImmutableMatrix:
    """Formal smallest Schur complement with exact symbolic entries."""
    h11, h12, h22 = sp.symbols("h11 h12 h22", real=True)
    c1, c2, hc = sp.symbols("c1 c2 h_c", real=True, nonzero=True)
    h_pp = sp.ImmutableMatrix([[h11, h12], [h12, h22]])
    h_pc = sp.ImmutableMatrix([[c1], [c2]])
    h_cc = sp.ImmutableMatrix([[hc]])
    return sp.ImmutableMatrix(sp.simplify(h_pp - h_pc * h_cc.inv() * h_pc.T))


def bending_ledger() -> dict[str, Any]:
    """Classify the classical sheet response without inserting B_sheet."""
    return {
        "background_matter_state": "Psi_background=0",
        "fermion_quadratic_tree_level_bending": 0,
        "fermion_loop_used": False,
        "current_S_J_bos": 0,
        "induced_measure_variation": "delta dmu_J=K_J xi_perp dmu_J",
        "shape_variation": (
            "delta K=-Delta_Sigma xi_perp-[Tr(S^2)+Ric(n,n)]xi_perp"
        ),
        "second_variation_status": (
            "no junction density exists to vary; P1 GHY belongs to the smooth "
            "boundary and B1 data do not export the constrained bending Hessian"
        ),
        "gauge_kernel": "must be removed before H_CC inversion",
        "H_phys": "H_PP-H_PC H_CC^(-1)H_CP",
        "H_phys_Hermitian": True,
        "k_b": None,
        "B_plus": None,
        "B_minus": None,
        "witness": "e_b=(0,0,1) after the gauge quotient",
        "lower_tachyon_certified": False,
        "lower_ghost_certified": False,
        "upper_stability_certified": False,
        "orientation_sign_is_second_variation": False,
        "minimal_missing_bosonic_invariant": (
            "S_J,bos^(0)=tau_J integral_SigmaJ sqrt(|gamma|)"
        ),
        "missing_coefficient": "tau_J",
        "tau_J_status": (
            "optional physical junction energy, not GHY and not fixed by "
            "well-posedness in the one-boundary geometry"
        ),
        "alternative_if_corner_declared": (
            "a Hayward joint integral kappa_1 integral sqrt|gamma| eta would "
            "be coefficient locked, but requires a new normal pair and angle"
        ),
        "result": BENDING_RESULT,
    }


def dependency_graph() -> dict[str, Any]:
    return {
        "current": {
            "S_J": 0,
            "domain_U": "unselected U(1)",
            "M_J": 0,
            "V_LH": 0,
            "energy_law": "no junction correction",
            "K_prop": None,
            "S_J_bos": 0,
            "B_plus": None,
            "B_minus": None,
        },
        "optional_fermion": (
            "alpha_J and C3 commutant coefficients -> conditional U/M_J -> "
            "trace data still required"
        ),
        "optional_boson": (
            "independent tau_J (or declared corner geometry) -> shape Hessian "
            "plus constraint response"
        ),
        "one_package_closes_all_targets": False,
        "independent_primitives_remain": ["fermion junction coefficients", "tau_J"],
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
        "v6_9_scientific_sha": V690_SCIENTIFIC_SHA,
        "primary_result": PRIMARY_RESULT,
        "preserved_results": [
            "BHSM_Y_SIGMA_EXP_MINUS_BETA_REJECTED_BY_CANONICAL_NORMALIZATION",
            "BHSM_AVAILABLE_C_BHSM_HAS_ZERO_LIGHT_HEAVY_COUPLING",
            "BHSM_LOWER_SHEET_KILL_SCREEN_REQUIRES_ONE_MISSING_HESSIAN_INVARIANT",
            "BHSM_AUXILIARY_INDEX_ONE_CERTIFIED",
        ],
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    basis = triality_commutant_basis()
    return {
        "invariants": {
            **_common("BHSM_junction_invariant_and_triality_commutant_v6_10_0"),
            "status": TRIALITY_RESULT,
            "geometry": geometry_ledger(),
            "invariants": invariant_ledger(),
            "triality": {
                "surviving_group": "C3",
                "generator": _matrix_strings(triality_cycle()),
                "full_S3_declared": False,
                "Hermitian_commutant_basis": [_matrix_strings(item) for item in basis],
                "general_matrix": "a I+x(C+C^2)+iy(C-C^2)",
                "equivalent_matrix": "a I+b C+b* C^2, b=x+iy",
                "real_coefficient_count": 3,
                "eigenvalues": [sp.sstr(item) for item in triality_eigenvalues()],
                "generic_multiplicities": [1, 1, 1],
                "nonuniversal_response_permitted": True,
                "nonuniversal_response_required": False,
                "coefficients_fixed": [],
            },
            "no_duplicate_invariant": no_duplicate_invariants(),
        },
        "variation": {
            **_common("BHSM_junction_variation_and_selected_domain_v6_10_0"),
            "status": DOMAIN_RESULT,
            "trace": trace_ledger(),
            "domain": domain_ledger(),
        },
        "projection": {
            **_common("BHSM_junction_light_heavy_projection_v6_10_0"),
            "status": PRIMARY_RESULT,
            "projection": projection_ledger(),
            "blocks": {
                key: _matrix_strings(value)
                for key, value in light_heavy_blocks().items()
            },
        },
        "dispersion": {
            **_common("BHSM_junction_dispersion_and_K_prop_v6_10_0"),
            "status": "BHSM_JUNCTION_K_PROP_REJECTED_FOR_CURRENT_ACTION",
            "Clifford": {
                "Gamma_n": _matrix_strings(gamma_n()),
                "Gamma_star": _matrix_strings(gamma_star()),
                "K": _matrix_strings(collar_grading()),
                "Gamma_star_beta_independent": True,
            },
            "dispersion": dispersion_ledger(),
        },
        "bending": {
            **_common("BHSM_junction_bending_sheet_response_v6_10_0"),
            "status": BENDING_RESULT,
            "bending": bending_ledger(),
            "formal_H_phys": _matrix_strings(constraint_reduced_hessian()),
        },
        "report": {
            **_common("BHSM_v6_10_0_hidden_input_and_final_report"),
            "status": PRIMARY_RESULT,
            "structural_case": STRUCTURAL_CASE,
            "central_answer": (
                "The current one-boundary well-posed action requires GHY but "
                "no gravitational joint and contains no matter junction "
                "generator. It therefore selects no U, gives V_LH=0, and "
                "cannot define K_prop or B_sheet. C3 permits optional "
                "nonuniversal circulant bilinears, while bending minimally "
                "requires the independent bosonic junction-volume coefficient tau_J."
            ),
            "dependency_graph": dependency_graph(),
            "hidden_inputs": [
                "fermion junction coefficient and Clifford grade",
                "point traces of f0 and normalized f1",
                "tau_J or a declared corner normal pair and joint angle",
                "constraint-reduced embedding Hessian and k_b",
            ],
            "next_construction": (
                "derive a two-face corner geometry from the parent action or "
                "derive tau_J from a localized bosonic source, then compute "
                "the gauge-quotiented second shape variation"
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
