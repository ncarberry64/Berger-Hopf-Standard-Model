"""BHSM v5.11 full quadratic-operator construction audit.

The stored action closes only the homogeneous scalar/topographic Hessian.
All other formulas below are either action-supported symbolic slots or clearly
marked conventional candidates.  The finite model tests gauge bookkeeping;
it is not a field-theory determinant or a Casimir calculation.
"""

from __future__ import annotations

import json
from math import sqrt
from pathlib import Path
from typing import Any


VERSION = "v5.11"
SPRINT = "bhsm-full-geometric-gauge-fixed-hessian-v5-11"
PRIMARY_RESULT = "BHSM_QUADRATIC_OPERATOR_COMPLEX_PARTIAL"
SIGMA_SCALE = 0.5

ARTIFACT_FILES = {
    "field_symmetry": "BHSM_full_hessian_field_gauge_symmetry_ledger_v5_11.json",
    "background_stationarity": "BHSM_full_hessian_background_stationarity_v5_11.json",
    "second_variation": "BHSM_full_hessian_second_variation_block_map_v5_11.json",
    "geometric_gauge_ghost": "BHSM_full_hessian_geometric_gauge_ghost_v5_11.json",
    "boundary_tension_surface": "BHSM_full_hessian_primordial_boundary_tension_surface_mode_v5_11.json",
    "internal_gauge_ghost": "BHSM_full_hessian_internal_gauge_ghost_v5_11.json",
    "fermion": "BHSM_full_hessian_fermion_dirac_domain_eta_v5_11.json",
    "scalar": "BHSM_full_hessian_scalar_topographic_v5_11.json",
    "charged_neutral": "BHSM_full_hessian_charged_neutral_classification_v5_11.json",
    "boundary_self_adjoint": "BHSM_full_hessian_boundary_self_adjointness_v5_11.json",
    "principal_ellipticity": "BHSM_full_hessian_principal_symbol_ellipticity_v5_11.json",
    "zero_negative": "BHSM_full_hessian_zero_negative_modes_v5_11.json",
    "heat_kernel": "BHSM_full_hessian_heat_kernel_readiness_v5_11.json",
    "reduced_complex": "BHSM_full_hessian_reduced_operator_complex_v5_11.json",
    "construction_report": "BHSM_full_geometric_gauge_fixed_hessian_report_v5_11.json",
}

GUARDS = {
    "empirical_inputs_used": False,
    "measured_masses_or_couplings_used": False,
    "planck_hubble_cmb_or_cosmology_used": False,
    "boundary_condition_selected_from_phenomenology": False,
    "physical_casimir_energy_claimed": False,
    "absolute_unit_anchor_claimed": False,
    "particle_masses_derived": False,
    "gauge_couplings_derived": False,
    "ckm_completion_claimed": False,
    "rare_b_predictions_claimed": False,
    "full_bhsm_completion_claimed": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "existing_numerical_predictions_changed": False,
}

OPEN_GATES = (
    "OPEN_MISSING_ACTION_DERIVED_GEOMETRIC_HESSIAN",
    "OPEN_MISSING_GEOMETRIC_FLUCTUATION_GAUGE_AND_DOMAIN",
    "OPEN_MISSING_FULL_GAUGE_FIXED_DOMAIN",
    "OPEN_MISSING_ACTION_DERIVED_GEOMETRIC_GAUGE_FUNCTIONAL",
    "OPEN_MISSING_ABSOLUTE_BOUNDARY_TENSION_DENSITY_SOURCE",
    "OPEN_MISSING_BOUNDARY_SHAPE_COEFFICIENT_VALUES",
    "OPEN_MISSING_NORMAL_DISPLACEMENT_DOMAIN_AND_SPECTRUM",
    "OPEN_MISSING_COMPATIBLE_GEOMETRIC_GHOST_BOUNDARY_CONDITIONS",
    "OPEN_MISSING_ACTION_DERIVED_INTERNAL_GAUGE_FIXING",
    "OPEN_MISSING_FADDEEV_POPOV_GHOST_OPERATOR",
    "OPEN_MISSING_FULL_LOWER_ORDER_OPERATOR_TERMS",
    "OPEN_MISSING_FERMION_DIRAC_OPERATOR_ACTION_SOURCE",
    "OPEN_MISSING_FERMION_SELF_ADJOINT_DOMAIN",
    "OPEN_MISSING_FERMION_DETERMINANT_PHASE_ETA_INVARIANT",
    "OPEN_MISSING_NONHOMOGENEOUS_BERGER_PROFILE_SOLUTION",
    "OPEN_MISSING_COUPLED_SCALAR_COLLAR_DOMAIN",
    "OPEN_MISSING_CHARGED_CURRENT_QUADRATIC_OPERATOR",
    "OPEN_MISSING_NEUTRAL_RESPONSE_NORMALIZATION",
    "OPEN_MISSING_STRONG_ELLIPTICITY_WITH_BOUNDARY",
    "OPEN_MISSING_COMPLETE_ZERO_MODE_JACOBIANS",
    "OPEN_MISSING_GEOMETRIC_NEGATIVE_MODE_CLASSIFICATION",
    "OPEN_MISSING_FIELD_THEORETIC_HEAT_KERNEL_COEFFICIENTS",
    "OPEN_MISSING_COMPLETE_BERGER_HOPF_SPECTRAL_LEDGER",
    "OPEN_MISSING_GLOBAL_SCALE_MODULUS_ACTION_SOURCE",
    "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR",
    "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
    "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
    "OPEN_MISSING_G2_BH_ACTION_SOURCE",
    "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
    "CKM_EXPONENT_NOT_DERIVED",
    "OPEN_MISSING_NEUTRAL_SCALE",
    "FULL_BHSM_NOT_COMPLETE",
)


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "claim_boundary": (
            "v5.11 constructs the strongest source-qualified operator architecture and a "
            "finite gauge-bookkeeping diagnostic. Missing action sources, gauges, domains, "
            "boundary conditions, and eta data prevent a determinant-ready full complex."
        ),
        **GUARDS,
    }


def field_symmetry_payload() -> dict[str, Any]:
    def field(name: str, space: str, statistics: str, reality: str, dimension: str,
              projector: str, gauge: str, background: str, fluctuation: str,
              inner: str, domain: str, boundary: str, ownership: str) -> dict[str, str]:
        return locals()

    fields = [
        field("metric/collar geometry", "Berger-Hopf boundary metrics plus collar embeddings", "bosonic", "real symmetric plus real normal displacement", "0 metric convention; xi_perp has length before normalization", "geometric", "diffeomorphism pullback; normal embedding variation must be separated from pure gauge", "g0=L^2 ghat(a0), collar normalized", "h_AB and xi_perp n^A", "DeWitt-type pairing plus surface L2 normalization unresolved", "metric/embedding perturbations modulo boundary-preserving diffeomorphisms", "not derived", "retained collective L,a,rho; local xi_perp determinant ownership open"),
        field("internal gauge connections", "Omega^1(ad U(1) oplus ad SU(2) oplus ad SU(3))", "bosonic", "anti-Hermitian connection convention", "1", "P_i", "delta a_i=D_i epsilon_i", "A_i0=0 conditionally", "a_i", "symbolic lambda_i-weighted L2", "gauge-fixed/coexact domain open", "absolute/relative candidates not selected", "local determinant candidate"),
        field("fermions", "spinor-generation-sector module", "Grassmann", "complex with Hermitian adjoint", "3/2 in 4D convention", "P_i,P_gen,chiral candidates", "internal representation and spin lift", "psi0=0 conditionally", "chi", "Hermitian spinor pairing", "Dirac domain open", "bag/APS/collar candidates not selected", "local determinant source open"),
        field("T", "real collar scalar", "bosonic", "real", "symbolic", "scalar/topographic", "none", "1/(2 sqrt(2))", "delta T(Y,rho)", "collar L2", "H1/H2 realization open beyond homogeneous mode", "v5.7 Robin zero-flux only in reduced domain", "parallel collective plus local modes"),
        field("Phi", "real Berger-boundary scalar", "bosonic", "real", "symbolic", "scalar/topographic", "none", "1/(2 sqrt(2))", "delta Phi(Y)", "Berger L2", "H1/H2 realization open beyond homogeneous mode", "v5.7 reduced Robin rule", "parallel collective plus local modes"),
        field("charged current", "fermion bilinear/projected interaction", "composite", "Hermitian paired current", "3 current convention", "P_ch,P_gen", "covariant composite transformation", "J_ch0=0 when psi0=0", "delta J_ch induced by chi", "inherited bilinear pairing", "no independent field space derived", "not independently defined", "no independent determinant"),
        field("neutral response", "symbolic neutral-response space", "bosonic/auxiliary unresolved", "real candidate", "symbolic", "P_neu", "no independent gauge law established", "N0=0 only conditionally", "delta N", "K_neu pairing", "response cone/domain conditional", "neutral flux conditional", "determinant ownership unresolved"),
        field("collective moduli", "R_+ x A_Berger x R x R_+", "bosonic collective", "real", "mixed", "none", "not gauge unless proven", "(L,a0,sigma=1/2,rho_star)", "(delta L,delta a,delta sigma,delta rho)", "v5.9 dL/L and d sigma; other entries open", "collective-coordinate manifold", "primordial condition open", "excluded from local determinant"),
        field("geometric ghosts", "vector gauge-parameter bundle", "Grassmann", "cbar independent Euclidean", "symbolic", "diffeomorphism", "FP representation", "0", "(c^A,cbar_A)", "vector L2", "undefined until gauge/domain selected", "must match h boundary rule", "ghost determinant candidate"),
        field("internal ghosts", "ad(U1 oplus SU2 oplus SU3) scalars", "Grassmann", "cbar independent Euclidean", "symbolic", "P_i", "adjoint", "0", "(c_i,cbar_i)", "adjoint L2", "undefined until gauge/domain selected", "must match a_i boundary rule", "ghost determinant candidate"),
        field("gauge-fixing auxiliaries", "Nakanishi-Lautrup candidate", "bosonic auxiliary", "real/adjoint", "symbolic", "gauge sectors", "BRST candidate not action-derived", "0", "B_geom,B_i", "algebraic", "not introduced in v5.4 action", "not applicable", "not part of current action"),
    ]
    symmetries = [
        {"name": "diffeomorphisms", "law": "delta_xi g=L_xi g; induced Lie derivatives on fields", "source": "covariant action architecture", "status": "PRESENT_BUT_GAUGE_FIXING_NOT_DERIVED"},
        {"name": "local internal gauge", "law": "delta_epsilon A_i=D_i epsilon_i with covariant matter transformation", "source": "U(1),SU(2),SU(3) connection sectors", "status": "PRESENT_BUT_GAUGE_FIXING_NOT_DERIVED"},
        {"name": "scalar shift", "law": None, "source": "v5.6/v5.7 potential breaks a constant shift", "status": "ABSENT"},
        {"name": "collar/embedding redundancy", "law": None, "source": "not separately specified by stored action", "status": "NOT_ESTABLISHED_NO_NEW_GAUGE_INTRODUCED"},
        {"name": "residual global/internal and Berger isometries", "law": "kernel transformations preserving B0", "source": "candidate background stabilizer", "status": "ZERO_MODE_PROJECTION_OPEN"},
    ]
    return {**_common("BHSM_full_hessian_field_gauge_symmetry_ledger_v5_11"), "status": "COMPLETE_FIELD_INVENTORY_OPERATOR_SOURCES_PARTIAL", "fields": fields, "gauge_symmetries": symmetries}


def background_stationarity_payload() -> dict[str, Any]:
    rows = [
        {"component": "geometry", "value": "g0=L^2 ghat(a0), xi_perp=0", "domain": "compact Berger-Hopf boundary plus normalized collar and its normal bundle", "boundary_data": "outward collar convention; detailed geometric data open", "equation": "delta S/delta g=0 and normal shape equation E_perp=0", "stationarity": "UNRESOLVED_OFF_SHELL", "source": "v5.4 symbolic geometric slot plus v5.6 boundary/collar action"},
        {"component": "Berger squashing", "value": "a0 retained symbolic", "domain": "positive Berger metrics", "boundary_data": "open", "equation": "partial S/partial a=0", "stationarity": "UNRESOLVED_OFF_SHELL", "source": "retained v5.8-v5.10 modulus"},
        {"component": "collar", "value": "rho_star normalized and retained", "domain": "collar interval", "boundary_data": "v5.7 reduced Robin rule only", "equation": "partial S/partial rho_star=0", "stationarity": "ZERO_ONLY_IN_REDUCED_TRUNCATION", "source": "v5.7-v5.10"},
        {"component": "T,Phi,sigma", "value": "T0=Phi0=1/(2 sqrt(2)); sigma=1/2", "domain": "v5.7 homogeneous reduced space", "boundary_data": "Robin zero-flux", "equation": "reduced scalar EOM", "stationarity": "ZERO_EXACTLY_IN_DECLARED_REDUCED_MODEL", "source": "v5.7"},
        {"component": "gauge", "value": "A_i0=0", "domain": "trivial-connection candidate", "boundary_data": "open", "equation": "delta S/delta A_i=0", "stationarity": "ZERO_CONDITIONALLY_IF_ALL_CURRENTS_VANISH", "source": "v5.4 gauge slot"},
        {"component": "fermion", "value": "psi0=0", "domain": "spinor domain open", "boundary_data": "open", "equation": "D_BHSM psi=0", "stationarity": "ZERO_CONDITIONALLY_FOR_BILINEAR_ACTION", "source": "conditional v5.4 fermion slot"},
        {"component": "charged", "value": "J_ch0=0", "domain": "composite of psi0", "boundary_data": "inherited", "equation": "no independent Euler-Lagrange equation", "stationarity": "NOT_AN_INDEPENDENT_FIELD", "source": "charged bilinear"},
        {"component": "neutral", "value": "N0=0 candidate", "domain": "conditional response cone", "boundary_data": "open", "equation": "K_neu N+source=0", "stationarity": "ZERO_CONDITIONALLY_IF_SOURCE_VANISHES_AND_K_NEU_DEFINED", "source": "symbolic neutral slot"},
        {"component": "global scale", "value": "L>0 arbitrary", "domain": "positive half-line", "boundary_data": "primordial selection open", "equation": "partial S/partial L=0", "stationarity": "FLAT_CLASSICALLY_NOT_FIXED", "source": "v5.8"},
    ]
    return {**_common("BHSM_full_hessian_background_stationarity_v5_11"), "status": "CONTROLLED_REDUCED_ON_SHELL_FULL_BACKGROUND_OFF_SHELL", "background_symbol": "B0=(g0,a0,collar,T0,Phi0,sigma=1/2,A0=0,psi0=0,Jch0=0,N0=0)", "rows": rows, "full_background_on_shell": False, "tadpole_rule": "Retain unresolved first variations explicitly; do not interpret off-shell quadratic eigenvalues as physical masses or stability data."}


def _block(row: str, col: str, formula: str, order: str, symbol: str, reason: str, status: str) -> dict[str, Any]:
    return {"row": row, "column": col, "formula": formula, "differential_order": order, "leading_symbol": symbol, "domain_codomain": f"delta {col} -> dual(delta {row})", "adjoint_relation": f"H_{row},{col}=H_{col},{row}^dagger where a common domain exists", "coefficient_source": reason, "status": status}


def second_variation_payload() -> dict[str, Any]:
    groups = ["g", "A", "psi", "ST", "ch", "nu"]
    specs = {
        ("g","g"): ("kappa_geom L_geom plus H_surface[xi_perp] plus matter stress variations", "2 or higher candidate", "tensor and normal-shape symbols; c_K2/c_S can increase boundary order", "v5.4 symbolic slot and v5.6 boundary/collar action", "SOURCE_OPEN_SURFACE_MODE_EXPLICIT"),
        ("g","A"): ("0 at A0=0 if source-free", "<=1", "conditional zero", "background argument", "CONDITIONAL_ZERO"),
        ("g","psi"): ("0 at psi0=0 for bilinear action", "<=1", "conditional zero", "background argument", "CONDITIONAL_ZERO"),
        ("g","ST"): ("delta_g delta_ST S_ST (stress mixing)", "<=2", "mixed", "v5.4 scalar/topographic action", "NONZERO_FORMULA_OPEN"),
        ("g","ch"): ("0 at psi0=Jch0=0 conditionally", "0", "conditional zero", "composite-background argument", "CONDITIONAL_ZERO"),
        ("g","nu"): ("delta_g delta_N S_neu", "open", "open", "symbolic neutral response", "UNRESOLVED"),
        ("A","A"): ("(1/lambda_i)L_i(rho) before gauge fixing", "2", "adjoint one-form Laplace-type candidate", "v5.4/v4.6 conditional gauge slot", "SYMBOLIC_SOURCE_SUPPORTED_DOMAIN_OPEN"),
        ("A","psi"): ("0 at psi0=0", "0", "conditional zero", "background argument", "CONDITIONAL_ZERO"),
        ("A","ST"): ("0 only for absence of explicit direct term in stored candidate", "0", "zero", "v5.4 term inventory", "SOURCE_LEDGER_ZERO"),
        ("A","ch"): ("delta_A delta_ch S_ch", "<=1", "projected mixed", "charged interaction", "NONZERO_SOURCE_NORMALIZATION_OPEN"),
        ("A","nu"): ("0 for no explicit direct term in stored candidate", "0", "zero", "v5.4 term inventory", "SOURCE_LEDGER_ZERO"),
        ("psi","psi"): ("zeta_psi D_BHSM", "1", "i gamma^A k_A", "conditional v5.4 fermion slot", "ACTION_SOURCE_AND_DOMAIN_OPEN"),
        ("psi","ST"): ("no closed Yukawa/topographic mass block", "open", "open", "source audit", "UNRESOLVED_NOT_SET_ZERO"),
        ("psi","ch"): ("charged projected bilinear variation", "0", "algebraic", "charged interaction", "NONZERO_SOURCE_NORMALIZATION_OPEN"),
        ("psi","nu"): ("neutral projected bilinear variation", "0", "algebraic", "neutral interaction", "NONZERO_SOURCE_NORMALIZATION_OPEN"),
        ("ST","ST"): ("diag(-partial_rho^2+5,-Delta_B+5)+offdiag(-1)", "2", "diag(k_rho^2,|k_B|^2)", "v5.7 homogeneous potential plus formal kinetic slots", "HOMOGENEOUS_CLOSED_FULL_DOMAIN_OPEN"),
        ("ST","ch"): ("no independent ch field; induced composite variation", "open", "open", "classification", "NOT_INDEPENDENT_BLOCK"),
        ("ST","nu"): ("delta_ST delta_N S_neu", "open", "open", "neutral response slot", "NONZERO_FORMULA_OPEN"),
        ("ch","ch"): ("none as independent operator", "n/a", "n/a", "composite classification", "NO_INDEPENDENT_DETERMINANT"),
        ("ch","nu"): ("not fixed by stored action", "open", "open", "source audit", "UNRESOLVED"),
        ("nu","nu"): ("K_neu symbolic", "open", "open", "neutral response slot", "NORMALIZATION_DOMAIN_OPEN"),
    }
    blocks = []
    for i, row in enumerate(groups):
        for j, col in enumerate(groups):
            key = (row, col) if i <= j else (col, row)
            formula, order, symbol, source, status = specs[key]
            if i > j:
                formula = f"({formula})^dagger"
            blocks.append(_block(row, col, formula, order, symbol, source, status))
    return {**_common("BHSM_full_hessian_second_variation_block_map_v5_11"), "status": "ALL_36_BLOCKS_CLASSIFIED_COMPLETE_FORMULAS_PARTIAL", "field_order": groups, "shape": [6, 6], "blocks": blocks, "hessian_equals_second_variation": "EXACT only for v5.7 homogeneous ST block; symbolic/source-qualified elsewhere", "full_second_variation_derived": False}


def reduced_vacuum_value(sigma: float = SIGMA_SCALE) -> float:
    """v5.7 normalized total reduced action, not a physical surface density."""
    return -(sigma * sigma) + 2.0 * sigma**4


def surface_scaling_eigenvalue(
    L: float,
    tau: float,
    c_K: float,
    c_K2: float,
    c_S: float,
    q_tau: float = 1.0,
    q_K: float = 1.0,
    q_K2: float = 1.0,
    q_S: float = 1.0,
) -> float:
    """Symbolic scaling diagnostic, not a physical BHSM surface spectrum."""
    if L <= 0.0:
        raise ValueError("L must be positive")
    return (
        tau * q_tau / L**2
        + c_K * q_K / L**3
        + (c_K2 * q_K2 + c_S * q_S) / L**4
    )


def surface_scaling_critical_lengths(
    tau: float,
    c_K: float,
    c_K2: float,
    c_S: float,
    q_tau: float = 1.0,
    q_K: float = 1.0,
    q_K2: float = 1.0,
    q_S: float = 1.0,
) -> list[float]:
    """Positive roots of the reduced scaling polynomial after multiplying by L^4."""
    a = tau * q_tau
    b = c_K * q_K
    c = c_K2 * q_K2 + c_S * q_S
    roots: list[float] = []
    if abs(a) < 1.0e-15:
        if abs(b) >= 1.0e-15:
            root = -c / b
            if root > 0.0:
                roots.append(root)
        return roots
    discriminant = b * b - 4.0 * a * c
    if discriminant < 0.0:
        return roots
    root_disc = sqrt(discriminant)
    for root in ((-b - root_disc) / (2.0 * a), (-b + root_disc) / (2.0 * a)):
        if root > 0.0 and all(abs(root - prior) > 1.0e-12 for prior in roots):
            roots.append(root)
    return sorted(roots)


def boundary_tension_surface_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_full_hessian_primordial_boundary_tension_surface_mode_v5_11"),
        "status": "PRIMORDIAL_SURFACE_RELEASE_THRESHOLD_SCALE_COVARIANT_SOURCE_OPEN",
        "normal_displacement": {
            "embedding_variation": "delta X^A=xi_perp n^A",
            "field": "xi_perp(Y)",
            "reality": "real",
            "domain": "normal bundle over the Berger-Hopf boundary; self-adjoint domain open",
            "gauge_separation": "boundary-preserving tangential diffeomorphisms are gauge; physical normal motion requires a declared embedding/boundary rule",
            "background": "xi_perp=0",
        },
        "boundary_tension_candidate": {
            "definition": "T_boundary=U_boundary(T_vac,Phi_vac)+C_collar,vac",
            "collar_contribution": "C_collar,vac=integral_0^rho_star B_threshold[T_vac,Phi_vac,K,S,J;rho] J drho",
            "normalized_total_reduced_vacuum_value": reduced_vacuum_value(),
            "normalized_value_formula": "V_red(1/2)=-(1/2)^2+2(1/2)^4=-1/8",
            "normalized_value_automatically_subtracted": False,
            "U_boundary_identified_with_entire_reduced_value": False,
            "reason": "v5.7 evaluates the total normalized reduced action, not the local U_boundary density or its area normalization",
            "absolute_density_value": None,
            "dimension": "energy per boundary area (or action per boundary volume) only after the action measure and units are fixed",
            "physical_sign": "unresolved; the normalized -1/8 is not by itself a signed physical tension",
        },
        "coefficient_provenance": {
            "c_K": "symbolic v5.6 boundary-action coefficient; v5.7 zero meant no scalar variation on fixed normalized geometry, not a geometric zero",
            "c_K2": "symbolic v5.6 boundary-action coefficient; not set to zero in normal shape variation",
            "c_S": "symbolic v5.6 boundary-action coefficient; not set to zero in normal shape variation",
            "c_J": "no separate log J term in v5.7 to avoid double counting; the action-derived collar Jacobian inside S_collar remains active",
            "coefficients_used_in_surface_equation": "c_K,c_K2,c_S retained symbolically",
        },
        "variation_convention": {
            "area": "delta(dA)=K xi_perp dA",
            "mean_curvature": "D_K xi_perp=-Delta_Sigma xi_perp-(Tr(S^2)+Ric(n,n))xi_perp",
            "shape_norm": "D_Q xi_perp=delta_xi Tr(S^2), computed from delta S_ab and delta gamma_ab in the selected collar orientation",
            "collar_jacobian": "delta log J=Tr[(I+rho S)^(-1) rho delta S] for J=det(I+rho S), with sign-equivalent opposite-normal convention",
        },
        "boundary_stress_tensor": {
            "definition": "T_Sigma^ab=-(2/sqrt(gamma)) delta(S_boundary+S_collar)/delta gamma_ab",
            "pure_tension_piece": "-T_boundary gamma^ab under the declared stress convention",
            "K_piece": "c_K times the orientation-dependent Brown-York combination (K^ab-K gamma^ab), plus embedding terms when the hypersurface moves",
            "K2_and_shape_pieces": "functional metric/embedding variations of c_K2 K^2 and c_S Tr(S^2), including derivative stresses generated by delta K and delta S_ab",
            "collar_piece": "functional variation of B_threshold J with respect to gamma_ab and S_ab",
            "scalar_topographic_piece": "on-shell boundary stress/pressure from U_boundary and collar threshold terms",
            "quantum_piece": "not a local stress tensor from v5.10; only a controlled uniform-mode diagnostic exists",
            "fully_evaluated": False,
        },
        "normal_shape_equation": {
            "boundary_density": "F_boundary=T_boundary+c_K K+c_K2 K^2+c_S Tr(S^2)",
            "formula": "E_perp=K F_boundary+D_K^dagger(c_K+2 c_K2 K)+D_Q^dagger(c_S)+E_J+E_collar+p_ST+E_quantum-Delta p=0",
            "generalized_balance": "Delta p=K F_boundary+D_K^dagger(c_K+2 c_K2 K)+D_Q^dagger(c_S)+E_J+E_collar+p_ST+E_quantum",
            "tension": "K T_boundary",
            "K": "c_K K^2+D_K^dagger c_K",
            "K2": "c_K2 K^3+D_K^dagger(2 c_K2 K)",
            "TrS2": "c_S K Tr(S^2)+D_Q^dagger c_S",
            "collar_jacobian": "E_J from delta J in the collar measure, not discarded with c_J=0",
            "scalar_topographic_pressure": "p_ST from normal variation of on-shell U_boundary and threshold support",
            "external_pressure_jump": "Delta p retained symbolically; no cosmological input",
            "stationarity": "OPEN_OFF_SHELL_UNTIL_ALL_TERMS_AND_BOUNDARY_DATA_CLOSE",
        },
        "quadratic_operator": {
            "definition": "H_surface=delta E_perp/delta xi_perp at B0",
            "decomposition": "H_tension+c_K H_K+c_K2 H_K2+c_S H_S+H_J+H_collar+H_ST+H_quantum",
            "tension_piece_on_stationary_fixed_pressure_background": "T_boundary[-Delta_Sigma-Tr(S^2)-Ric(n,n)] plus balance-dependent lower terms",
            "principal_order": "second order for pure tension/K architecture; K^2 and Tr(S^2) variations can produce fourth-order boundary terms",
            "boundary_form": "requires the xi_perp domain and edge/collar matching; not closed",
            "self_adjoint": False,
            "strongly_elliptic": False,
        },
        "lowest_mode": {
            "definition": "lambda_surface(L,a,sigma,rho_star)=inf spec'(H_surface) after proven tangential-gauge and Killing kernels are removed",
            "scaling_architecture": "tau q_tau(a,sigma,rho)/L^2+c_K q_K/L^3+(c_K2 q_K2+c_S q_S)/L^4+lambda_collar+lambda_ST+lambda_quantum",
            "mode_functions": "q_tau,q_K,q_K2,q_S require the Berger/collar embedding and normal-mode domain",
            "value": None,
            "release_condition": "lambda_surface(L_c,a,sigma,rho_star)=0",
            "L_c": None,
        },
        "quantum_term": {
            "valid_v5_10_scope": "Gamma_perp=1/2 log[6/(mu^2 L^2)] for one homogeneous scalar mode",
            "uniform_scale_derivatives": {"dGamma_dL": "-1/L", "d2Gamma_dL2": "1/L^2"},
            "normal_projection": "H_quantum=J_L^dagger L^-2 J_L plus connection/tadpole terms only if a uniform xi_perp-to-delta L map is derived",
            "local_shape_stress_available": False,
            "included_in_official_surface_operator": False,
            "reason": "v5.10 is a renormalization-scale-dependent partial diagnostic, not a local quantum stress tensor",
        },
        "critical_scale_classification": {
            "fixed_completely_by_current_action": False,
            "fixed_in_terms_of_one_primitive_tension_or_breaking_energy": "possible only conditionally after an absolute density and remaining relative coefficients/mode functions are sourced",
            "current_result": "STILL_SCALE_COVARIANT",
            "reason": "-1/8 and the v5.7 coefficient zeros are normalized scalar-reduction data; they do not provide dimensionful surface density or geometric shape coefficients",
            "absolute_scale_claimed": False,
        },
        "preserved_primordial_interpretation": [
            {"stage": "stable compact state", "status": "candidate; positive lowest physical surface eigenvalue required"},
            {"stage": "lambda_surface reaches zero", "status": "candidate release threshold; not yet solved"},
            {"stage": "outward instability", "status": "conditional on a negative crossing and correct negative-mode treatment"},
            {"stage": "guided compact-to-expanding trajectory", "status": "v5.9 conditional guidance architecture"},
            {"stage": "primordial hot plasma", "status": "interpretive downstream state, not derived or observationally validated here"},
        ],
    }


def geometric_gauge_ghost_payload() -> dict[str, Any]:
    return {**_common("BHSM_full_hessian_geometric_gauge_ghost_v5_11"), "status": "GEOMETRIC_GAUGE_GHOST_CANDIDATE_NOT_ACTION_DERIVED", "decomposition": ["TT candidate", "longitudinal vector", "trace/conformal", "boundary-tangential embedding variation", "boundary-normal xi_perp physical/candidate shape mode", "Berger squashing", "global scale", "collar modes"], "normal_displacement_artifact": ARTIFACT_FILES["boundary_tension_surface"], "decomposition_compatible_with_full_boundary_proved": False, "gauge_condition": "F_A(h)=nabla^B h_AB-gamma nabla_A h", "gamma": "1/2 conventional de Donder candidate; not BHSM-derived", "gauge_action": "<F,F>/(2 xi_g)", "xi_g": "positive symbolic gauge parameter", "ghost_operator": "M_A^B=-nabla^2 delta_A^B-R_A^B for gamma=1/2 up to declared curvature/sign convention", "ghost_derivation": "delta_xi h_AB=nabla_A xi_B+nabla_B xi_A inserted into delta F", "field_space": "vector ghosts", "boundary_condition": None, "residual_modes": "Killing-vector kernel requires determinant-prime projection", "conformal_mode": "unresolved; not hidden or discarded", "normal_mode": "xi_perp retained; not removed as gauge without a boundary-preserving diffeomorphism/embedding proof", "boundary_form": "geometry, surface-shape, and gauge-fixing boundary form not closed", "gauge_parameter_independence_full": False, "determinant_ready": False}


def internal_gauge_ghost_payload() -> dict[str, Any]:
    sectors = [{"group": "U(1)", "raw_adjoint_rank": 1}, {"group": "SU(2)", "raw_adjoint_rank": 3}, {"group": "SU(3)", "raw_adjoint_rank": 8}]
    return {**_common("BHSM_full_hessian_internal_gauge_ghost_v5_11"), "status": "INTERNAL_GAUGE_GHOST_ARCHITECTURE_SYMBOLIC_DOMAIN_OPEN", "sectors": sectors, "background": "A_i0=0 conditionally source-free", "unfixed_operator": "(1/lambda_i)L_i(rho), lower-order terms open", "numerical_gauge_couplings": None, "gauge_condition": "G_i(a)=D_i^dagger a_i conventional background-covariant candidate", "gauge_action": "<G_i,G_i>/(2 xi_i)", "ghost_operator": "M_i=D_i^dagger D_i from delta a_i=D_i epsilon_i once the candidate gauge is selected", "ghost_multiplicity": "1,3,8 raw adjoint ranks", "boundary_candidates": ["absolute", "relative", "mixed normal/tangential"], "selected_boundary_condition": None, "residual_modes": "covariantly constant/global gauge parameters", "zero_mode_projection": "required, not constructed in full geometry", "gauge_parameter_independence_full": False, "determinant_ready": False}


def fermion_payload() -> dict[str, Any]:
    return {**_common("BHSM_full_hessian_fermion_dirac_domain_eta_v5_11"), "status": "FERMION_OPERATOR_ARCHITECTURE_SOURCE_AND_DOMAIN_OPEN", "strongest_formula": "D_BHSM=gamma^A(nabla_A^spin+sum_i A_A^(i) P_i)", "action_coefficient": "zeta_psi symbolic", "bare_dirac_kinetic": "conditional v5.4 slot", "spin_structure": "required but not selected for complete Berger/collar geometry", "spin_connection": "Levi-Civita spin lift candidate", "chiral_projectors": "sector architecture conditional", "yukawa_like_coupling": None, "topographic_mass_coupling": None, "charged_coupling": "projected bilinear interaction; normalization open", "neutral_coupling": "projected bilinear/response interaction; normalization open", "boundary_dirac_term": None, "principal_symbol": "i gamma^A k_A", "formal_adjoint": "D_BHSM^dagger after Hermitian connection and boundary pairing", "square": "D^dagger D Laplace type conditionally; E and connection curvature incomplete", "boundary_form": "integral_boundary chi_bar gamma(n) psi", "boundary_candidates": ["local bag-type", "chirality-compatible projector", "APS spectral", "collar matching"], "selected_boundary_condition": None, "normal_current_controlled": False, "essential_self_adjoint": False, "fredholm": False, "spectral_asymmetry": "possible", "zero_modes_and_index": "unresolved", "eta_invariant": None, "determinant_phase_controlled": False, "determinant_ready": False}


def scalar_payload() -> dict[str, Any]:
    return {**_common("BHSM_full_hessian_scalar_topographic_v5_11"), "status": "HOMOGENEOUS_HESSIAN_EXACT_FULL_NONHOMOGENEOUS_DOMAIN_OPEN", "formal_full_hessian": [["-partial_rho^2+5", "-I_mix"], ["-I_mix^dagger", "-Delta_B+5"]], "mixing_issue": "T lives on collar while Phi lives on Berger boundary; I_mix and its adjoint require a trace/extension map not derived", "background": "T0=Phi0=1/(2 sqrt(2)), sigma=1/2", "homogeneous_hessian": [[5, -1], [-1, 5]], "parallel_mode": {"vector": "(1,1)/sqrt(2)", "eigenvalue": "4/L^2", "ownership": "retained sigma_scale collective coordinate"}, "orthogonal_mode": {"vector": "(1,-1)/sqrt(2)", "eigenvalue": "6/L^2", "ownership": "v5.10 finite reduced determinant"}, "v5_10_eigenvalue_recovered": True, "nonhomogeneous_berger_modes": "operator architecture only", "collar_radial_modes": "operator architecture only", "mixed_berger_collar_modes": "trace/extension domain open", "metric_stress_mixing": "nonzero formula open", "homogeneous_zero_modes": [], "homogeneous_negative_modes": [], "complete_zero_negative_mode_structure": False, "full_self_adjoint_domain": None, "full_determinant_ready": False}


def charged_neutral_payload() -> dict[str, Any]:
    return {**_common("BHSM_full_hessian_charged_neutral_classification_v5_11"), "status": "CHARGED_COMPOSITE_NEUTRAL_RESPONSE_SOURCE_OPEN", "charged": {"classification": "current-current/projected fermion bilinear; not an independent propagating field", "independent_field_space": None, "quadratic_operator": None, "mixing": ["A-ch", "psi-ch"], "normalization": "open", "physical_degrees_of_freedom": "inherited from constituent fields", "determinant_ownership": "NO_INDEPENDENT_ZERO_POINT_DETERMINANT", "mediator_invented": False}, "neutral": {"classification": "symbolic response/auxiliary candidate; action does not decide independent versus effective", "quadratic_operator": "K_neu symbolic", "auxiliary_elimination": "conditional on an invertible normalized K_neu and a closed domain", "mixing": ["g-nu", "psi-nu", "ST-nu"], "normalization": "open", "determinant_ownership": "UNRESOLVED", "dimensionless_structure_separated_from_physical_neutrino_scale": True, "ev_values_inserted": False}}


def boundary_self_adjoint_payload() -> dict[str, Any]:
    rows = [
        {"sector": "geometry+geometric ghost", "boundary_form": "Green form from L_geom plus F boundary terms", "candidate": "mixed normal/tangential projector", "variation_vanishes": False, "gauge_preserved": False, "ghost_compatible": False, "dense_domain": "unproved", "adjoint_domain_matches": False, "selected": None},
        {"sector": "normal displacement xi_perp", "boundary_form": "Green form of H_surface; fourth-order pieces require two edge/collar conditions", "candidate": "physical normal-mode domain with collar matching", "variation_vanishes": False, "gauge_preserved": "normal/tangential decomposition not closed", "ghost_compatible": "xi_perp must not be paired with a ghost unless proven pure gauge", "dense_domain": "unproved", "adjoint_domain_matches": False, "selected": None},
        {"sector": "internal gauge+ghost", "boundary_form": "<a,D_n b>-<D_n a,b> plus ghost scalar form", "candidate": "absolute or relative paired conditions", "variation_vanishes": "candidate-dependent", "gauge_preserved": "candidate-dependent", "ghost_compatible": "candidate-dependent", "dense_domain": "standard candidate only, BHSM selection open", "adjoint_domain_matches": False, "selected": None},
        {"sector": "fermion", "boundary_form": "integral_boundary chi_bar gamma(n) psi", "candidate": "bag/chiral/APS/collar", "variation_vanishes": "candidate-dependent", "gauge_preserved": "candidate-dependent", "ghost_compatible": "n/a", "dense_domain": "candidate-dependent", "adjoint_domain_matches": False, "selected": None},
        {"sector": "scalar homogeneous", "boundary_form": "delta T partial_n delta T-delta T' partial_n delta T plus Phi analogue", "candidate": "v5.7 Robin zero-flux", "variation_vanishes": True, "gauge_preserved": "no scalar gauge symmetry", "ghost_compatible": "n/a", "dense_domain": True, "adjoint_domain_matches": True, "selected": "only on declared homogeneous reduced domain"},
        {"sector": "neutral", "boundary_form": "depends on K_neu", "candidate": "neutral flux", "variation_vanishes": False, "gauge_preserved": "unresolved", "ghost_compatible": "n/a", "dense_domain": "unproved", "adjoint_domain_matches": False, "selected": None},
    ]
    return {**_common("BHSM_full_hessian_boundary_self_adjointness_v5_11"), "status": "REDUCED_SCALAR_SELF_ADJOINT_FULL_BOUNDARY_COMPLEX_OPEN", "rows": rows, "minimal_maximal_domains_computed_for_full_system": False, "extension_ambiguity": "multiple standard candidate families; none selected using phenomenology", "full_self_adjoint_operator_complex": False}


def principal_ellipticity_payload() -> dict[str, Any]:
    rows = [
        {"sector": "geometry", "order": 2, "principal_symbol": "|k|^2 times tensor identity only after candidate de Donder fixing", "elliptic": "formal candidate", "strong_ellipticity_with_boundary": False, "status": "SOURCE_AND_BOUNDARY_OPEN"},
        {"sector": "normal displacement xi_perp", "order": "2 with tension/K; potentially 4 with K^2/Tr(S^2)", "principal_symbol": "T_boundary |k_parallel|^2 plus symbolic c_K2/c_S fourth-order shape symbol", "elliptic": "undecidable until coefficient signs and the shape domain close", "strong_ellipticity_with_boundary": False, "status": "BOUNDARY_TENSION_AND_SHAPE_COEFFICIENTS_OPEN"},
        {"sector": "internal gauge", "order": 2, "principal_symbol": "|k|^2 times adjoint one-form identity after candidate D^dagger a gauge", "elliptic": "formal candidate", "strong_ellipticity_with_boundary": False, "status": "LOWER_TERMS_AND_BOUNDARY_OPEN"},
        {"sector": "geometric/internal ghosts", "order": 2, "principal_symbol": "|k|^2 identity", "elliptic": "formal candidate", "strong_ellipticity_with_boundary": False, "status": "BOUNDARY_OPEN"},
        {"sector": "fermion D", "order": 1, "principal_symbol": "i gamma^A k_A", "elliptic": "symbolically invertible for k!=0 in Euclidean signature", "strong_ellipticity_with_boundary": False, "status": "DOMAIN_OPEN"},
        {"sector": "fermion D^dagger D", "order": 2, "principal_symbol": "|k|^2 identity", "elliptic": "formal", "strong_ellipticity_with_boundary": False, "status": "SOURCE_DOMAIN_ETA_OPEN"},
        {"sector": "scalar/topographic", "order": 2, "principal_symbol": "diag(k_rho^2,|k_B|^2)", "elliptic": "separately formal; coupled operator class unresolved", "strong_ellipticity_with_boundary": False, "status": "MIXED_DOMAIN_OPEN"},
        {"sector": "charged", "order": None, "principal_symbol": None, "elliptic": False, "strong_ellipticity_with_boundary": False, "status": "NO_INDEPENDENT_OPERATOR"},
        {"sector": "neutral", "order": None, "principal_symbol": None, "elliptic": False, "strong_ellipticity_with_boundary": False, "status": "SOURCE_OPEN"},
    ]
    return {**_common("BHSM_full_hessian_principal_symbol_ellipticity_v5_11"), "status": "FORMAL_SYMBOLS_CLASSIFIED_NO_FULL_STRONG_ELLIPTICITY", "rows": rows, "closed_bosonic_differential_operators": [], "full_block_invertibility": False, "determinant_ready": False}


def zero_negative_payload() -> dict[str, Any]:
    zero = [
        {"mode": "diffeomorphism directions", "type": "pure gauge", "treatment": "candidate FP quotient; boundary-compatible projection open"},
        {"mode": "internal D_i epsilon_i", "type": "pure gauge", "treatment": "candidate FP quotient; residual global kernel prime needed"},
        {"mode": "Killing/Berger isometry stabilizer", "type": "residual gauge/isometry", "treatment": "group-volume/Jacobian open"},
        {"mode": "global L", "type": "physical classical modulus/collective coordinate", "treatment": "retain; v5.9 measure dL/L"},
        {"mode": "a_Berger,rho_star", "type": "candidate collective moduli", "treatment": "retain; metrics/Jacobians open"},
        {"mode": "sigma_scale", "type": "retained collective coordinate but not zero of v5.7 Hessian", "treatment": "not determinant-owned in v5.10 hierarchy"},
        {"mode": "fermion/index/topological", "type": "unresolved", "treatment": "index and eta ledger required"},
        {"mode": "lowest xi_perp surface mode", "type": "physical boundary-shape candidate", "treatment": "retain; lambda_surface crossing is a candidate release threshold, not a gauge deletion"},
    ]
    negative = [
        {"sector": "geometry conformal", "count": None, "interpretation": "Euclidean conformal issue versus off-shell instability unresolved", "discarded": False},
        {"sector": "normal displacement xi_perp", "count": None, "interpretation": "stable/zero/negative classification requires T_boundary, shape coefficients, embedding, and domain", "discarded": False},
        {"sector": "Berger squashing/collar", "count": None, "interpretation": "off-shell background and boundary data unresolved", "discarded": False},
        {"sector": "scalar homogeneous", "count": 0, "interpretation": "eigenvalues 4,6 positive in reduced domain", "discarded": False},
        {"sector": "scalar nonhomogeneous", "count": None, "interpretation": "domain/spectrum open", "discarded": False},
        {"sector": "charged/neutral", "count": None, "interpretation": "operator sources open", "discarded": False},
    ]
    return {**_common("BHSM_full_hessian_zero_negative_modes_v5_11"), "status": "ZERO_NEGATIVE_LEDGER_EXPLICIT_TREATMENT_PARTIAL", "zero_modes": zero, "negative_modes": negative, "determinant_prime_prescription": "remove only proven gauge kernels; retain physical collective coordinates and include their Jacobians", "collective_metric": {"L": "dL^2/L^2", "sigma_scale": "d sigma^2", "a_Berger": None, "rho_star": None}, "jacobian": {"L_sigma": "dL/L d sigma_scale", "a_Berger": None, "rho_star": None}, "negative_modes_silently_removed": False}


def heat_kernel_payload() -> dict[str, Any]:
    rows = [
        {"sector": "geometry", "laplace_form": "candidate", "connection_curvature": None, "E": None, "bundle_rank": None, "boundary_projector": None, "Robin_endomorphism": None, "sign": 1, "multiplicity": None, "readiness": "OPERATOR_SOURCE_OPEN"},
        {"sector": "internal gauge", "laplace_form": "candidate -(nabla^2+E_i)", "connection_curvature": "background F_i candidate", "E": None, "bundle_rank": "adjoint one-form ranks 1,3,8 times geometry", "boundary_projector": None, "Robin_endomorphism": None, "sign": 1, "multiplicity": "symbolic", "readiness": "OPERATOR_SOURCE_OPEN"},
        {"sector": "ghosts", "laplace_form": "candidate -(nabla^2+E_FP)", "connection_curvature": "candidate", "E": None, "bundle_rank": "vector plus 1+3+8", "boundary_projector": None, "Robin_endomorphism": None, "sign": -1, "multiplicity": "complex Grassmann convention open", "readiness": "OPERATOR_SOURCE_OPEN"},
        {"sector": "fermion square", "laplace_form": "conditional D^dagger D=-(nabla^2+E_D)", "connection_curvature": None, "E": None, "bundle_rank": None, "boundary_projector": None, "Robin_endomorphism": None, "sign": -1, "multiplicity": None, "readiness": "OPERATOR_SOURCE_OPEN"},
        {"sector": "scalar/topographic homogeneous", "laplace_form": "finite 2x2 matrix; not a field heat-kernel operator", "connection_curvature": "n/a", "E": [[5,-1],[-1,5]], "bundle_rank": 2, "boundary_projector": "v5.7 reduced Robin", "Robin_endomorphism": "reduced zero-flux", "sign": 1, "multiplicity": 1, "readiness": "EXACT_FINITE_MATRIX_NOT_HEAT_KERNEL_READY"},
        {"sector": "normal displacement xi_perp", "laplace_form": "not generically Laplace type when K^2/Tr(S^2) generate fourth-order shape terms", "connection_curvature": "normal-bundle/induced connection open", "E": "tension, curvature, pressure, collar, scalar, and valid quantum lower terms open", "bundle_rank": 1, "boundary_projector": None, "Robin_endomorphism": None, "sign": 1, "multiplicity": 1, "readiness": "OPERATOR_SOURCE_OPEN"},
    ]
    return {**_common("BHSM_full_hessian_heat_kernel_readiness_v5_11"), "status": "HEAT_KERNEL_INPUT_LEDGER_PARTIAL_NO_TOTAL_COEFFICIENTS", "rows": rows, "requested_coefficients": ["a_0","a_1/2","a_1","a_3/2","a_2"], "total_coefficients_calculated": False, "reason": "No complete closed differential operator and compatible boundary complex exists."}


def raw_reduced_hessian(k_geom: float = 2.0, k_gauge: float = 3.0) -> list[list[float]]:
    """Finite consistency model in order h_phys,h_gauge,A_phys,A_gauge,T,Phi."""
    return [[k_geom,0,0,0,0,0],[0,0,0,0,0,0],[0,0,k_gauge,0,0,0],[0,0,0,0,0,0],[0,0,0,0,5,-1],[0,0,0,0,-1,5]]


def gauge_fixed_reduced_hessian(xi_geom: float, xi_internal: float, k_geom: float = 2.0, k_gauge: float = 3.0) -> list[list[float]]:
    if xi_geom <= 0 or xi_internal <= 0:
        raise ValueError("gauge parameters must be positive")
    matrix = raw_reduced_hessian(k_geom, k_gauge)
    matrix[1][1] = 1.0 / xi_geom
    matrix[3][3] = 1.0 / xi_internal
    return matrix


def physical_reduced_hessian(k_geom: float = 2.0, k_gauge: float = 3.0) -> list[list[float]]:
    return [[k_geom,0,0,0],[0,k_gauge,0,0],[0,0,5,-1],[0,0,-1,5]]


def physical_reduced_eigenvalues(k_geom: float = 2.0, k_gauge: float = 3.0) -> list[float]:
    return sorted([k_geom, k_gauge, 4.0, 6.0])


def reduced_quadratic_action(vector: list[float], xi_geom: float, xi_internal: float) -> float:
    """Return 1/2 x^T H_gf x for the declared finite diagnostic."""
    if len(vector) != 6:
        raise ValueError("reduced vector must have six components")
    matrix = gauge_fixed_reduced_hessian(xi_geom, xi_internal)
    return 0.5 * sum(
        vector[i] * matrix[i][j] * vector[j]
        for i in range(6)
        for j in range(6)
    )


def reduced_determinant_quotient(xi_geom: float, xi_internal: float, k_geom: float = 2.0, k_gauge: float = 3.0) -> float:
    """Normalized finite FP quotient; both diagnostic ghost matrices equal [1]."""
    if xi_geom <= 0 or xi_internal <= 0:
        raise ValueError("gauge parameters must be positive")
    det_gf = k_geom * (1/xi_geom) * k_gauge * (1/xi_internal) * 24.0
    return xi_geom * xi_internal * det_gf


def reduced_complex_payload() -> dict[str, Any]:
    xi_g, xi_i = 2.0, 3.0
    return {**_common("BHSM_full_hessian_reduced_operator_complex_v5_11"), "status": "FINITE_GAUGE_GHOST_CONSISTENCY_MODEL_EXACT_NOT_PHYSICAL_DETERMINANT", "field_order": ["h_phys","h_gauge","A_phys","A_gauge","T","Phi"], "included_fields": ["one diagnostic physical geometric coordinate", "one geometric gauge coordinate", "one diagnostic physical internal-gauge coordinate", "one internal gauge coordinate", "full homogeneous T/Phi block", "matching unit FP ghosts"], "excluded_fermion_reason": "D_BHSM action source/domain not closed", "sample_coefficients": {"k_geom": 2.0, "k_gauge": 3.0, "meaning": "positive algebraic diagnostic conventions, not action-derived spectra or physical values"}, "raw_hessian": raw_reduced_hessian(), "raw_zero_modes": ["h_gauge","A_gauge"], "gauge_fixed_hessian": gauge_fixed_reduced_hessian(xi_g,xi_i), "gauge_parameters": {"xi_geom":xi_g,"xi_internal":xi_i}, "ghost_matrices": {"geometric":[[1.0]],"internal":[[1.0]]}, "ghost_derivation": "finite F=x_gauge with delta x_gauge/d epsilon=1", "physical_projector_indices": [0,2,4,5], "physical_hessian": physical_reduced_hessian(), "physical_eigenvalues": physical_reduced_eigenvalues(), "zero_modes_after_projection": [], "negative_modes": [], "determinant_ready_eigenvalues": physical_reduced_eigenvalues(), "physical_determinant": 144.0, "normalized_gauge_ghost_quotient": reduced_determinant_quotient(xi_g,xi_i), "gauge_parameter_independence": "exact in this finite diagnostic", "physical_casimir_assigned": False}


def construction_report_payload() -> dict[str, Any]:
    return {**_common("BHSM_full_geometric_gauge_fixed_hessian_report_v5_11"), "status": PRIMARY_RESULT, "background": background_stationarity_payload(), "field_content": field_symmetry_payload(), "second_variation": second_variation_payload(), "geometric_sector": geometric_gauge_ghost_payload(), "boundary_tension_surface_mode": boundary_tension_surface_payload(), "gauge_sectors": internal_gauge_ghost_payload(), "fermion_sector": fermion_payload(), "scalar_topographic_sector": scalar_payload(), "charged_neutral": charged_neutral_payload(), "boundary_adjoint": boundary_self_adjoint_payload(), "principal_symbol": principal_ellipticity_payload(), "zero_negative": zero_negative_payload(), "heat_kernel": heat_kernel_payload(), "reduced_model": reduced_complex_payload(), "v5_10_update": {"historical_result": "BHSM_QUANTUM_EFFECTIVE_ACTION_PARTIAL", "historical_one_mode_determinant_preserved": True, "promoted_to_official_effective_action": False, "determinant_ready_sectors": ["finite homogeneous scalar/topographic diagnostic only"], "matter_only_one_loop_permitted": False, "gauge_plus_ghost_one_loop_permitted": False, "scalar_gauge_fermion_one_loop_permitted": False, "full_one_loop_permitted": False}, "preserved_relative_results": {"sigma_scale": "1/2", "M_BH_over_M_star": "1/2", "R_BH_over_ell_star": "2"}, "derived": ["canonical full field/symmetry and all-36-block source-status maps", "conditional geometric/internal FP formulas from explicitly conventional gauges", "normal shape equation and surface-Hessian decomposition with tension, K, K^2, Tr(S^2), collar, scalar pressure, and controlled quantum slots", "exact homogeneous T/Phi Hessian eigenvalues 4/L^2 and 6/L^2", "charged current has no independent determinant in the stored composite classification", "finite gauge/ghost consistency model with gauge-parameter-independent physical Hessian and normalized quotient"], "conditionally_established": ["the normalized -1/8 vacuum value is retained as a candidate boundary/collar contribution but is not identified with an absolute surface density", "a finite L_c can arise from ratios of independently sourced dimensionful tension/shape coefficients and mode functions", "formal principal symbols become elliptic under conventional gauges before boundary completion", "D_BHSM and D^dagger D have Dirac/Laplace principal symbols if the missing source and domain close", "neutral auxiliary elimination requires an invertible normalized K_neu"], "invalidated_or_ruled_out": ["v5.7 c_K=c_K2=c_S=0 in a fixed scalar reduction does not prove the geometric coefficients vanish", "the normalized vacuum value -1/8 cannot by itself be promoted to a physical boundary tension", "the current surface release condition does not fix an absolute L_c", "the present repository does not support a full determinant-ready operator complex", "standard gauge or boundary candidates cannot be relabeled BHSM-derived", "the v5.10 one-mode determinant is not the official or full one-loop action", "the earlier curvature-threshold mass-gap theorem remains invalidated", "unresolved negative and zero modes cannot be silently removed"], "still_requiring_new_mathematics": list(OPEN_GATES), "claim_safe_conclusion": "BHSM v5.11 retains the vacuum boundary/collar value as a candidate tension source and derives a formal normal release equation, but the absolute density, shape coefficients, embedding, and spectrum remain open. The threshold is still scale covariant. No full one-loop action, Casimir energy, absolute unit, mass, coupling, CKM result, rare-B prediction, physical validation, or BHSM completion follows.", "recommended_next_construction_sprint": "bhsm-unified-action-coefficient-source-closure-v5-12", "next_sprint_priority": "derive the absolute boundary-tension density and c_K,c_K2,c_S sources before solving lambda_surface(L_c)=0"}


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    return {"field_symmetry": field_symmetry_payload(), "background_stationarity": background_stationarity_payload(), "second_variation": second_variation_payload(), "geometric_gauge_ghost": geometric_gauge_ghost_payload(), "boundary_tension_surface": boundary_tension_surface_payload(), "internal_gauge_ghost": internal_gauge_ghost_payload(), "fermion": fermion_payload(), "scalar": scalar_payload(), "charged_neutral": charged_neutral_payload(), "boundary_self_adjoint": boundary_self_adjoint_payload(), "principal_ellipticity": principal_ellipticity_payload(), "zero_negative": zero_negative_payload(), "heat_kernel": heat_kernel_payload(), "reduced_complex": reduced_complex_payload(), "construction_report": construction_report_payload()}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


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


def full_hessian_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    _ = repo_root
    report = construction_report_payload()
    report["artifacts"] = {key: f"artifacts/{name}" for key, name in ARTIFACT_FILES.items()}
    return report


def full_hessian_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join(["# BHSM v5.11 Full Geometric and Gauge-Fixed Hessian", "", f"Primary result: `{report['primary_result']}`.", "", "The complete field and 36-block architecture is classified, but missing action sources, gauges, domains, boundary conditions, and eta data prevent a full determinant-ready complex.", "", "The normalized vacuum value `-1/8` is retained as a candidate boundary/collar contribution, not identified with an absolute tension. The normal release condition `lambda_surface(L_c)=0` remains scale covariant because its density, shape coefficients, embedding, and spectrum are open.", "", "The exact inherited homogeneous scalar/topographic block has eigenvalues `4/L^2` and `6/L^2`; the finite gauge/ghost model is a bookkeeping test, not a Casimir calculation.", "", "## Open gates", "", *[f"- `{gate}`" for gate in report["still_requiring_new_mathematics"]]]) + "\n"
