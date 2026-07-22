"""BHSM v6.1.4 intrinsic-M4 junction-supported background closure."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


VERSION = "v6.1.4"
SPRINT = "bhsm-intrinsic-m4-junction-background-closure-v6-1-4"
PRIMARY_RESULT = "BHSM_INTRINSIC_M4_JUNCTION_BACKGROUND_DERIVED_CONDITIONALLY"
COMPLETION_GATE = "V6_1_4_Z2_TWO_CAP_BACKGROUND_DERIVED_MIXED_STABILITY_AND_COEFFICIENT_SOURCE_OPEN"

ARTIFACT_FILES = {
    "action": "BHSM_frozen_bulk_boundary_total_action_v6_1_4.json",
    "variation": "BHSM_exact_bulk_boundary_variation_v6_1_4.json",
    "matching": "BHSM_matching_multiplier_elimination_theorem_v6_1_4.json",
    "residual": "BHSM_smooth_K0_equator_residual_v6_1_4.json",
    "ansatz": "BHSM_gaussian_normal_junction_ansatz_v6_1_4.json",
    "bulk_equations": "BHSM_bulk_P1_gaussian_normal_field_equations_v6_1_4.json",
    "junction": "BHSM_one_sided_extrinsic_curvature_junction_v6_1_4.json",
    "constant_curvature": "BHSM_constant_curvature_bulk_junction_branch_v6_1_4.json",
    "caps": "BHSM_Z2_two_cap_regularity_audit_v6_1_4.json",
    "frw": "BHSM_boundary_FRW_constraint_v6_1_4.json",
    "branches": "BHSM_boundary_static_bounce_dynamic_classification_v6_1_4.json",
    "coefficient": "BHSM_boundary_gravity_coefficient_background_relation_v6_1_4.json",
    "primitives": "BHSM_junction_background_primitive_count_v6_1_4.json",
    "connection": "BHSM_junction_background_connection_vacuum_v6_1_4.json",
    "sigma": "BHSM_junction_background_sigma_vacuum_v6_1_4.json",
    "missing": "BHSM_junction_background_minimal_missing_term_gate_v6_1_4.json",
    "conservation": "BHSM_bulk_boundary_conservation_identity_v6_1_4.json",
    "stability": "BHSM_junction_constraint_reduced_stability_matrix_v6_1_4.json",
    "tensor": "BHSM_junction_supported_tensor_sector_v6_1_4.json",
    "lorentz": "BHSM_junction_background_Lorentz_hyperbolicity_v6_1_4.json",
    "sources": "BHSM_boundary_coefficient_source_readiness_v6_1_4.json",
    "parent_map": "BHSM_junction_background_parent_to_v5_v4_map_v6_1_4.json",
    "fermionic": "BHSM_junction_first_order_fermionic_readiness_v6_1_4.json",
    "scale_hidden": "BHSM_junction_background_scale_hidden_input_audit_v6_1_4.json",
    "report": "BHSM_intrinsic_M4_junction_background_report_v6_1_4.json",
}

GUARDS = {
    "boundary_axiom_parent_derived": False,
    "preferred_equator_invented": False,
    "frozen_v6_1_3_action_changed": False,
    "boundary_vacuum_term_added": False,
    "post_freeze_term_added": False,
    "physical_Dirac_equation_assumed": False,
    "magnetic_monopole_sector_used": False,
    "observed_particle_charge_mass_or_coupling_assigned": False,
    "alpha_evaluated": False,
    "absolute_unit_claimed": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "existing_numerical_predictions_changed": False,
    "full_bhsm_completion_claimed": False,
}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _positive(*values: float) -> None:
    if not values or any(value <= 0 for value in values):
        raise ValueError("all declared kinetic coefficients and radii must be positive")


def p1_constant_curvature(kappa_0: float, kappa_1: float) -> dict[str, float]:
    _positive(kappa_0, kappa_1)
    cosmological_coefficient = kappa_0 / (2 * kappa_1)
    sectional_curvature = cosmological_coefficient / 6
    return {
        "lambda_5": cosmological_coefficient,
        "q_5": sectional_curvature,
        "bulk_radius": 1 / math.sqrt(sectional_curvature),
    }


def junction_coupling(C_partial: float, kappa_1: float, *, z2: bool = True) -> float:
    _positive(C_partial, kappa_1)
    bulk_sides = 2 if z2 else 1
    return 2 * C_partial / (bulk_sides * kappa_1)


def boundary_curvature_branches(
    kappa_0: float,
    kappa_1: float,
    C_partial: float,
    *,
    z2: bool = True,
) -> list[float]:
    q_5 = p1_constant_curvature(kappa_0, kappa_1)["q_5"]
    eta = junction_coupling(C_partial, kappa_1, z2=z2)
    discriminant = 1 - 4 * eta**2 * q_5
    if discriminant < -1e-14:
        return []
    root = math.sqrt(max(0.0, discriminant))
    values = [(1 - root) / (2 * eta**2), (1 + root) / (2 * eta**2)]
    return sorted(set(values))


def junction_extrinsic_curvature(
    boundary_curvature: float,
    acceleration: float,
    C_partial: float,
    kappa_1: float,
    *,
    z2: bool = True,
) -> dict[str, float]:
    _positive(boundary_curvature, C_partial, kappa_1)
    eta = junction_coupling(C_partial, kappa_1, z2=z2)
    k_s = -eta * boundary_curvature
    k_t = eta * (boundary_curvature - 2 * acceleration)
    return {
        "eta": eta,
        "k_t": k_t,
        "k_s": k_s,
        "K_trace": k_t + 3 * k_s,
        "jump_k_t": 2 * k_t if z2 else k_t,
        "jump_k_s": 2 * k_s if z2 else k_s,
    }


def smooth_equator_residual(
    C_partial: float,
    radius: float,
    H: float,
    dot_H_over_lapse: float,
) -> dict[str, float]:
    _positive(C_partial, radius)
    X = H**2 + 1 / radius**2
    acceleration = dot_H_over_lapse + H**2
    Y = 2 * acceleration + X
    return {
        "X": X,
        "acceleration": acceleration,
        "G_t_t": -3 * X,
        "G_i_j": -Y,
        "junction_residual_t_t": -6 * C_partial * X,
        "junction_residual_i_j": -2 * C_partial * Y,
    }


def constant_curvature_branch_geometry(
    kappa_0: float,
    kappa_1: float,
    C_partial: float,
    branch: int,
) -> dict[str, float]:
    branches = boundary_curvature_branches(kappa_0, kappa_1, C_partial, z2=True)
    if branch not in range(len(branches)):
        raise ValueError("branch must select an available Z2 curvature root")
    bulk = p1_constant_curvature(kappa_0, kappa_1)
    X = branches[branch]
    q_5 = bulk["q_5"]
    eta = junction_coupling(C_partial, kappa_1, z2=True)
    k = -eta * X
    return {
        **bulk,
        "boundary_curvature": X,
        "boundary_radius": 1 / math.sqrt(X),
        "one_sided_k": k,
        "gauss_residual": X - q_5 - k**2,
        "hyperplane_offset_abs": bulk["bulk_radius"] * math.sqrt(1 - q_5 / X),
        "reconstructed_C_partial": kappa_1 * math.sqrt(X - q_5) / X,
    }


def closed_de_sitter_trajectory(boundary_curvature: float, proper_time: float) -> dict[str, float]:
    _positive(boundary_curvature)
    root = math.sqrt(boundary_curvature)
    radius = math.cosh(root * proper_time) / root
    H = root * math.tanh(root * proper_time)
    return {
        "a": radius,
        "H": H,
        "X": H**2 + 1 / radius**2,
        "acceleration": boundary_curvature,
    }


def coefficient_bound(kappa_0: float, kappa_1: float, *, z2: bool = True) -> float:
    q_5 = p1_constant_curvature(kappa_0, kappa_1)["q_5"]
    bulk_sides = 2 if z2 else 1
    return bulk_sides * kappa_1 / (4 * math.sqrt(q_5))


def critical_static_geometry(kappa_0: float, kappa_1: float, C_partial: float) -> dict[str, Any]:
    _positive(kappa_0, kappa_1, C_partial)
    bulk = p1_constant_curvature(kappa_0, kappa_1)
    bound = coefficient_bound(kappa_0, kappa_1, z2=True)
    exists = math.isclose(C_partial, bound, rel_tol=1e-12, abs_tol=1e-14)
    if not exists:
        return {"exists": False, "required_C_partial": bound}
    q_5 = bulk["q_5"]
    radius = bulk["bulk_radius"] / math.sqrt(2)
    return {
        **bulk,
        "exists": True,
        "required_C_partial": bound,
        "boundary_radius": radius,
        "hyperbola_radius": radius,
        "X": 2 * q_5,
        "acceleration": 0.0,
        "k_t": math.sqrt(q_5),
        "k_s": -math.sqrt(q_5),
    }


def _common(name: str) -> dict[str, Any]:
    return {
        "artifact": name,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "claim_boundary": "The exact Z2 double-cap constant-curvature background is conditional on provisional Boundary Axiom B1 and positive unsourced coefficients. It derives a branch-dependent background relation, not a universal value of C_partial. Full mixed bulk-boundary perturbative stability and the remaining coefficient sources stay open.",
        **GUARDS,
    }


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    c = _common
    return {
        "action": {
            **c("BHSM_frozen_bulk_boundary_total_action_v6_1_4"),
            "status": "BHSM_V6_1_3_TOTAL_ACTION_FROZEN_FOR_JUNCTION_TEST",
            "bulk": "(1/2) integral_M5 sqrt(-g)[kappa_1 R5-kappa_0]",
            "GHY": "kappa_1 integral_boundary sqrt(-h) K for each oriented cap",
            "boundary": "integral_M4 sqrt(-h)[C_partial R4-tau_A Tr(F^2)/4-Z_partial(partial sigma_partial)^2/2-U_partial]+S_match",
            "vacuum": {"A_mu": 0, "sigma_partial": 0, "U_partial": 0, "sourced_constant": False},
            "terms_added": [],
            "pr156_merge_commit": "e4302e1f0fd2cdd597257c1afec9a8a34c90e082",
        },
        "variation": {
            **c("BHSM_exact_bulk_boundary_variation_v6_1_4"),
            "status": "BHSM_EXACT_BULK_BOUNDARY_VARIATION_DERIVED",
            "bulk_equation": "kappa_1 G_AB+(kappa_0/2)g_AB=0",
            "GHY_cancellation": "normal derivatives of delta g cancel independently on every cap",
            "canonical_momentum": "Pi_mu_nu=(kappa_1/2)(K_mu_nu-K h_mu_nu) in the unmultiplied variation; the doubled junction uses kappa_1[Q_mu_nu]",
            "junction": "kappa_1[Q_mu_nu]+2C_partial G_mu_nu^(4)=T_A,mu_nu+T_sigma,mu_nu",
            "one_cap": "kappa_1 Q_mu_nu+2C_partial G_mu_nu^(4)=T_partial,mu_nu",
            "Z2": "[Q_mu_nu]=2Q_mu_nu^+ in the declared common-normal convention",
            "orientation": "K_mu_nu=(1/2)L_n h_mu_nu; reversing n reverses K and Q",
        },
        "matching": {
            **c("BHSM_matching_multiplier_elimination_theorem_v6_1_4"),
            "status": "BHSM_EXACT_MATCHING_MULTIPLIER_ELIMINATED",
            "action": "integral_M4 sqrt(-h) Lambda^{mu nu}(h_mu nu-iota^*g_mu nu)",
            "variation_order": ["vary independent g", "vary independent h", "vary Lambda", "impose h=iota^*g", "eliminate Lambda"],
            "multiplier_equation": "h_mu nu=iota^*g_mu nu",
            "elimination": "the bulk boundary condition and intrinsic metric equation contain Lambda with opposite constraint forces and combine into the junction equation",
            "tunable_matching_coefficient": None,
            "propagating_multiplier_mode": False,
            "hidden_physical_stress": False,
            "overconstraint": "no algebraic overconstraint; existence is decided by the resulting junction system",
        },
        "residual": {
            **c("BHSM_smooth_K0_equator_residual_v6_1_4"),
            "status": "BHSM_SMOOTH_K0_EQUATOR_INTRINSIC_GRAVITY_RESIDUAL_DERIVED",
            "definitions": {"X": "H^2+a^-2", "A": "N^-1 dot(H)+H^2", "Y": "2A+X"},
            "intrinsic_Einstein_mixed": {"G_t_t": "-3X", "G_i_j": "-Y delta_i_j"},
            "K": 0,
            "vacuum_residual": {"temporal": "-6C_partial X", "spatial": "-2C_partial Y delta_i_j"},
            "failed_equation": "kappa_1[Q]+2C_partial G^(4)=0",
            "classification": "nonzero at every finite radius for C_partial>0 because X>0",
        },
        "ansatz": {
            **c("BHSM_gaussian_normal_junction_ansatz_v6_1_4"),
            "status": "BHSM_GAUSSIAN_NORMAL_Z2_JUNCTION_ANSATZ_FIXED",
            "metric": "ds5^2=dy^2-n(y,t)^2dt^2+r(y,t)^2dOmega3^2",
            "boundary": "y=0; n(0,t)=N_partial(t); r(0,t)=a_partial(t)",
            "normal_lapse": 1,
            "normal_shift": 0,
            "one_sided": {"k_t": "n_y/n at 0+", "k_s": "r_y/r at 0+"},
            "Z2": "n and r are even functions of |y| while their one-sided derivatives are opposite",
            "distinctions": ["Z2 does not imply K^+=0", "K^+=0 differs from [K]=0", "the fixed junction may have a cusp"],
        },
        "bulk_equations": {
            **c("BHSM_bulk_P1_gaussian_normal_field_equations_v6_1_4"),
            "status": "BHSM_BULK_P1_GAUSSIAN_NORMAL_EQUATIONS_DERIVED",
            "equation": "G_AB+lambda_5 g_AB=0; lambda_5=kappa_0/(2kappa_1)",
            "warped_product_form": {"G_ab": "-3 r^-1 nabla_a nabla_b r+3g_ab box_2 r/r+3g_ab(nabla r)^2/r^2-3g_ab/r^2", "G_i_j": "[-R2/2+2box_2 r/r+(nabla r)^2/r^2-r^-2]delta_i_j"},
            "tt": "3[(dot r/(nr))^2+r^-2-r_yy/r-(r_y/r)^2]-lambda_5=0 after division by n^2",
            "yy": "3[(r_y/r)(r_y/r+n_y/n)-A_ytime-r^-2]+lambda_5=0, with A_ytime=ddot r/(n^2r)+dot r^2/(n^2r^2)-dot n dot r/(n^3r)",
            "ty": "3[(n_y/n)(dot r/r)-dot(r_y)/r]=0",
            "angular": "-R2/2+2box_2 r/r+(nabla r)^2/r^2-r^-2+lambda_5=0",
            "two_dimensional_identities": {"R2": "-2n_yy/n", "box_2_r": "-ddot r/n^2+dot n dot r/n^3+(n_y/n)r_y+r_yy", "gradient_r_squared": "-dot r^2/n^2+r_y^2"},
            "Bianchi": "the angular equation follows from the constraints and one evolution equation where gradients are regular",
            "constraint_propagation": "nabla^A(G_AB+lambda_5 g_AB)=0",
        },
        "junction": {
            **c("BHSM_one_sided_extrinsic_curvature_junction_v6_1_4"),
            "status": "BHSM_ONE_SIDED_EXTRINSIC_CURVATURE_JUNCTION_DERIVED",
            "definitions": {"X": "H_partial^2+a_partial^-2", "A": "N_partial^-1 dot(H_partial)+H_partial^2", "Y": "2A+X", "eta_m": "2C_partial/(m kappa_1)"},
            "bulk_side_count": {"one_cap": 1, "Z2_double": 2},
            "temporal": "k_s=-eta_m X in intrinsic vacuum",
            "spatial": "k_t=eta_m(X-2A)",
            "trace": "m kappa_1[-3k_t-9k_s]+2C_partial[-6(A+X)]=T_trace in mixed convention",
            "Z2_jump": "[k_t]=2k_t^+ and [k_s]=2k_s^+",
            "matter": "add T_A and T_sigma on the right; both vanish in the retained vacuum",
        },
        "constant_curvature": {
            **c("BHSM_constant_curvature_bulk_junction_branch_v6_1_4"),
            "status": "BHSM_Z2_CONSTANT_CURVATURE_JUNCTION_BRANCH_DERIVED",
            "bulk": {"q_5": "kappa_0/(12kappa_1)", "R_AB": "4q_5 g_AB", "R5": "20q_5"},
            "Gauss": {"spatial": "X=q_5+k_s^2", "temporal": "A=q_5+k_t k_s"},
            "Codazzi": "N^-1 dot(k_s)=H(k_t-k_s)",
            "Z2_vacuum": {"eta": "C_partial/kappa_1", "k_t": "k_s=-eta X", "constraint": "eta^2 X^2-X+q_5=0"},
            "roots": "X_pm=[1 plus/minus sqrt(1-4eta^2q_5)]/(2eta^2)",
            "existence": "0<C_partial/kappa_1<=1/(2sqrt(q_5))",
            "trajectory": "a_partial=L4 cosh((tau-tau0)/L4), L4=X^-1/2",
            "critical_degeneracy": "at eta=1/(2sqrt(q_5)) and X=2q_5, a separate static R x S3 embedding also solves the full constant-curvature Gauss and junction equations",
            "classification": "exact background equations on each root; conditional on B1 and positive-curvature P1 branch",
        },
        "caps": {
            **c("BHSM_Z2_two_cap_regularity_audit_v6_1_4"),
            "status": "BHSM_REGULAR_Z2_TWO_CAP_GLOBALIZATION_DERIVED_CONDITIONALLY",
            "embedding": "dS5(q_5) in R^(1,5), cut by the timelike hyperplane X5=c",
            "boundary": "dS4 radius L4=sqrt(L5^2-c^2), so X=(L5^2-c^2)^-1 and k^2=X-q_5",
            "offset": "|c|=L5 sqrt(1-q_5/X)<L5",
            "construction": "retain one regular cap and glue an identical copy across the hyperplane",
            "poles": "each retained cap contains a regular pole inherited from smooth dS5; curvature invariants remain constant",
            "second_junction": False,
            "spatial_topology": "piecewise-smooth S4 after doubling; the only distributional hypersurface is M4",
            "non_Z2_original_caps": "the two unequal complementary caps do not provide the required jump without a cusp",
            "critical_static_embedding": "X0=b sinh(t/b), X1=b cosh(t/b), (X2,...,X5)=a Omega3 with a=b=L5/sqrt(2); doubling either regular spatial cap gives the static critical junction",
            "scope": "global background geometry; full perturbative boundary-value stability remains open",
        },
        "frw": {
            **c("BHSM_boundary_FRW_constraint_v6_1_4"),
            "status": "BHSM_BOUNDARY_FRW_CONSTRAINT_DERIVED",
            "lapse_policy": "N_partial is varied before proper-time gauge N_partial=1",
            "Hamiltonian": "X=q_5+eta^2X^2, X=H^2+a^-2, eta=C_partial/kappa_1 for Z2",
            "square_root": "epsilon sqrt(X-q_5)=-eta X; positive coefficients select epsilon=-1 in the declared normal orientation",
            "acceleration": "A=X on every retained nonstatic constant-curvature root",
            "conservation": "dot rho+3NH(rho+p)=normal flux; both sides vanish in the retained vacuum",
            "sign_branches": ["low-curvature X_minus", "high-curvature X_plus", "normal-orientation sign", "time reversal"],
        },
        "branches": {
            **c("BHSM_boundary_static_bounce_dynamic_classification_v6_1_4"),
            "status": "BHSM_SHIFTED_BOUNCE_AND_CRITICAL_STATIC_BRANCHES_RETAINED",
            "static": "at C_partial=kappa_1/(2sqrt(q_5)), a=L5/sqrt(2), H=A=0, k_t=sqrt(q_5), and k_s=-sqrt(q_5) give an exact R x S3 junction with a regular constant-curvature cap embedding",
            "bounce": "retained exact solution; H=0 and a=L4 at tau=tau0",
            "expansion": "tau>tau0 half of the retained solution",
            "contraction": "tau<tau0 half of the retained solution",
            "monotonic_global": False,
            "old_cosh": "X=q_5 and k=0 fails for C_partial>0",
            "shifted_cosh": "X_pm>q_5 and nonzero one-sided k; both algebraic roots globalize as Z2 double caps",
            "singular": False,
        },
        "coefficient": {
            **c("BHSM_boundary_gravity_coefficient_background_relation_v6_1_4"),
            "status": "BHSM_BOUNDARY_GRAVITY_COEFFICIENT_BACKGROUND_RELATION_DERIVED",
            "Z2_relation": "C_partial=kappa_1 sqrt(X-q_5)/X",
            "bound": "0<C_partial<=kappa_1/(2sqrt(q_5))",
            "branch_dependence": "two X roots below the critical bound; one double root at X=2q_5",
            "universal_coefficient_derivation": False,
            "reason": "the equations relate C_partial to the chosen embedding curvature but do not select one X or source C_partial",
            "primitive_status": "C_partial remains independent; background consistency restricts its domain and determines X conditionally",
        },
        "primitives": {
            **c("BHSM_junction_background_primitive_count_v6_1_4"),
            "status": "BHSM_JUNCTION_BACKGROUND_DOES_NOT_LOCK_ALL_BOUNDARY_PRIMITIVES",
            "parent": ["kappa_0", "kappa_1"],
            "boundary_raw": ["C_partial", "tau_A", "Z_partial"],
            "background_relation": "one equation between C_partial and branch curvature X; X is then fixed on either root for supplied primitives",
            "C_partial_removed": False,
            "tau_A_constrained_by_vacuum": False,
            "Z_partial_constrained_by_vacuum": False,
            "potential_primitives": 0,
            "integration_constants": ["bounce time tau0", "normal orientation", "curvature-root branch"],
            "continuous_physical_coefficient_combinations": 4,
            "count_explanation": "kappa_0/kappa_1 fixes q_5, an overall parent normalization remains, C_partial sets the junction root, tau_A controls connection normalization, and free-scalar Z_partial is a field convention until a scalar source appears",
        },
        "connection": {
            **c("BHSM_junction_background_connection_vacuum_v6_1_4"),
            "status": "BHSM_BOUNDARY_CONNECTION_VACUUM_COMPATIBLE",
            "background": "A_mu=0",
            "equation": "tau_A D_nu F^(nu mu)=0",
            "stress": 0,
            "Gauss_constraint": "D_i E^i=0",
            "repair_junction_with_connection": False,
            "nonzero_homogeneous_configuration_inserted": False,
            "monopole_status": "excluded",
        },
        "sigma": {
            **c("BHSM_junction_background_sigma_vacuum_v6_1_4"),
            "status": "BHSM_BOUNDARY_SIGMA_ZERO_VACUUM_COMPATIBLE_POTENTIAL_OPEN",
            "background": "sigma_partial=0",
            "potential": "U_partial=0 in the frozen primary test; no sourced constant contribution",
            "equation": "Z_partial box_h sigma_partial=0",
            "energy_density": 0,
            "pressure": 0,
            "junction_contribution": 0,
            "rolling_branch_used": False,
            "v5_values_imported": False,
        },
        "missing": {
            **c("BHSM_junction_background_minimal_missing_term_gate_v6_1_4"),
            "status": "BHSM_BOUNDARY_VACUUM_TERM_NOT_REQUIRED_FOR_BACKGROUND_EXISTENCE",
            "required_term": None,
            "reason": "nonzero one-sided extrinsic curvature balances intrinsic G_mu_nu on both exact Z2 roots",
            "boundary_tension_added": False,
            "parent_potential_constant_added": False,
            "future_trigger": "only if the retained branches fail the unresolved full mixed stability problem",
            "candidate_if_triggered": {"term": "-Lambda_partial integral sqrt(-h)", "dimension": "Lambda_partial has L^-4", "stress": "-Lambda_partial h_mu_nu", "coefficient_assigned": False},
        },
        "conservation": {
            **c("BHSM_bulk_boundary_conservation_identity_v6_1_4"),
            "status": "BHSM_BULK_BOUNDARY_CONSERVATION_IDENTITY_DERIVED",
            "identity": "D^mu(T_partial,mu nu-2C_partial G_mu nu)=-[T_bulk,n nu]",
            "bulk_Bianchi": "nabla^A(G_AB+lambda_5 g_AB)=0",
            "connection_identity": "D_mu D_nu F^(nu mu)=0 on the gauge equations",
            "scalar_identity": "(Z_partial box sigma-U')D_nu sigma=0",
            "matching": "multiplier forces cancel after h=iota^*g and Lambda elimination",
            "retained_vacuum": "T_partial=0, constant-curvature bulk has zero normal flux, and conservation holds identically",
        },
        "stability": {
            **c("BHSM_junction_constraint_reduced_stability_matrix_v6_1_4"),
            "status": "BHSM_JUNCTION_BACKGROUND_PRINCIPAL_SECTORS_HEALTHY_FULL_MIXED_STABILITY_OPEN",
            "constraints_removed": ["bulk diffeomorphism gauge", "boundary time reparameterization", "bulk and boundary lapse/shift", "matching multiplier", "connection gauge zero modes"],
            "principal_diagonal": {"bulk_tensor": "kappa_1>0", "boundary_TT": "C_partial>0", "connection_transverse": "tau_A I_R>0", "sigma": "Z_partial>0"},
            "homogeneous_background": "the algebraic curvature roots are exact but are not by themselves a reduced fluctuation spectrum",
            "junction_bending": "requires the second variation plus the cap bulk Green operator",
            "negative_modes": None,
            "open": ["normalizable mixed scalar metric modes", "junction displacement eigenvalue", "root-branch radion/bending sign", "complete tensor normal spectrum"],
        },
        "tensor": {
            **c("BHSM_junction_supported_tensor_sector_v6_1_4"),
            "status": "BHSM_JUNCTION_SUPPORTED_TENSOR_SECTOR_DERIVED_CONDITIONALLY",
            "boundary_principal": "(C_partial/4) integral a^3[dot gamma_TT^2-a^-2(nabla gamma_TT)^2]",
            "bulk": "five-dimensional TT equation on each constant-curvature cap",
            "junction_condition": "kappa_1[delta Q_TT]+2C_partial delta G_TT=0",
            "classification": "mixed bulk-boundary, not exactly intrinsic after coupling",
            "leakage": "encoded by the cap normal Green operator",
            "normal_spectrum": "not solved",
            "stability": "principal kinetic signs are positive; spectral stability unresolved",
            "observed_graviton_status": None,
        },
        "lorentz": {
            **c("BHSM_junction_background_Lorentz_hyperbolicity_v6_1_4"),
            "status": "BHSM_SHIFTED_INTRINSIC_M4_LORENTZ_PRINCIPAL_STRUCTURE_PRESERVED",
            "gravity": "intrinsic TT characteristic cone equals the induced h cone for C_partial>0",
            "connection": "Yang-Mills principal cone equals the induced h cone after gauge reduction",
            "sigma": "box_h principal cone equals the induced h cone",
            "bulk": "P1 metric perturbations are normally hyperbolic after a valid bulk gauge",
            "matching": "dynamic junction boundary conditions require a separate Lopatinski/well-posedness proof",
            "speeds_squared": {"intrinsic_tensor": 1, "connection": 1, "sigma": 1},
            "superluminal_claim": None,
            "acausal_claim": None,
        },
        "sources": {
            **c("BHSM_boundary_coefficient_source_readiness_v6_1_4"),
            "status": "BHSM_BOUNDARY_COEFFICIENT_SOURCE_PROBLEM_REFINED",
            "C_partial": "independent positive primitive with a branch-dependent existence bound and background-curvature relation",
            "tau_A": "independent; vacuum background gives no equation for it",
            "Z_partial": "free-field normalization convention; becomes physical when a scalar source is derived",
            "U_partial": "absent in the primary freeze; no vacuum constant required for background existence",
            "next_exact_target": "common parent boundary action or representation/normalization theorem for tau_A and scalar source",
            "broad_survey_performed": False,
        },
        "parent_map": {
            **c("BHSM_junction_background_parent_to_v5_v4_map_v6_1_4"),
            "status": "BHSM_JUNCTION_BACKGROUND_PARENT_MAP_ADVANCED_CONDITIONALLY",
            "map": {"background": "junction-derived constant-curvature Z2 double cap", "gravity": "B1-derived intrinsic action plus branch-dependent background relation", "gauge": "B1-derived kinetic action; physical map unresolved", "nested_U1": "constrained representation data", "scalar_kinetic": "B1-derived free normalization", "scalar_quadratic": "unresolved", "scalar_quartic": "unresolved", "charged": "unresolved physical current/aperture", "neutral": "zero free-scalar vacuum only", "boundary": "provisional B1 with exact metric matching", "scale": "radii in terms of kappa_0,kappa_1,C_partial", "recycling": "unchanged"},
            "v5_coefficients_changed": False,
            "reverse_engineered_from_v5": False,
        },
        "fermionic": {
            **c("BHSM_junction_first_order_fermionic_readiness_v6_1_4"),
            "status": "BHSM_FIRST_ORDER_FERMIONIC_ACTION_READINESS_ADVANCED",
            "frame": "stable background frame exists at the exact classical level; fluctuation stability remains open",
            "spin_structure": "I_t x S3 is spin",
            "Clifford_bundle": "defined by the induced Lorentzian metric",
            "spin_connection": "intrinsic connection plus a mathematically defined extrinsic Gauss term",
            "connection_representation": "parent associated-bundle representation data available",
            "sigma_background": 0,
            "conserved_inner_product": "candidate on closed de Sitter slices after an action and domain are derived",
            "self_adjoint_domain": "not selected",
            "physical_first_order_action": None,
            "physical_Dirac_equation": None,
            "monopole_dependence": None,
        },
        "scale_hidden": {
            **c("BHSM_junction_background_scale_hidden_input_audit_v6_1_4"),
            "status": "BHSM_JUNCTION_RADII_DERIVED_FROM_PRIMITIVES_ABSOLUTE_UNIT_OPEN",
            "bulk_radius": "L5=sqrt(12kappa_1/kappa_0)",
            "boundary_radius": "L4=X_pm^-1/2",
            "cap_offset": "|c|=L5 sqrt(1-q_5/X_pm)",
            "junction_curvature": "|k|=sqrt(X_pm-q_5)",
            "inputs": ["kappa_0", "kappa_1", "C_partial", "root branch", "normal orientation", "bounce-time origin"],
            "derived": ["dimensionless bound 4(C_partial/kappa_1)^2q_5<=1", "radius ratios for a supplied coefficient ratio"],
            "not_imported": ["Planck length", "Hubble rate", "CMB temperature", "masses", "gauge couplings", "alpha", "CKM", "PMNS", "cosmological parameters"],
            "absolute_unit": None,
        },
        "report": {
            **c("BHSM_intrinsic_M4_junction_background_report_v6_1_4"),
            "status": PRIMARY_RESULT,
            "central_answer": "The frozen B1 intrinsic action admits exact positive-curvature P1 backgrounds without added tension: an offset de Sitter-4 hyperplane can Z2-double one regular de Sitter-5 cap, and at the critical coefficient a separate static R x S3 embedding exists. Nonzero one-sided extrinsic curvature balances the intrinsic Einstein tensor. The dynamic junction gives eta^2 X^2-X+q_5=0 with eta=C_partial/kappa_1, yielding two shifted closed-de-Sitter bounce roots below the coefficient bound. This is a branch-dependent background relation, not a universal derivation of C_partial. The construction is conditional because B1 and the coefficients remain unsourced and the complete constraint-reduced mixed bulk-boundary bending/tensor spectrum is not yet solved.",
            "subsidiary_results": ["BHSM_SMOOTH_K0_EQUATOR_INTRINSIC_GRAVITY_RESIDUAL_DERIVED", "BHSM_ONE_SIDED_EXTRINSIC_CURVATURE_JUNCTION_DERIVED", "BHSM_BOUNDARY_FRW_CONSTRAINT_DERIVED", "BHSM_REGULAR_Z2_TWO_CAP_GLOBALIZATION_DERIVED_CONDITIONALLY", "BHSM_BOUNDARY_GRAVITY_COEFFICIENT_BACKGROUND_RELATION_DERIVED", "BHSM_BULK_BOUNDARY_CONSERVATION_IDENTITY_DERIVED", "BHSM_JUNCTION_SUPPORTED_TENSOR_SECTOR_DERIVED_CONDITIONALLY", "BHSM_FIRST_ORDER_FERMIONIC_ACTION_READINESS_ADVANCED"],
            "derived": ["exact variation and matching-multiplier elimination", "smooth-equator residual", "one-sided and jump junction factors", "constant-curvature roots", "regular Z2 double-cap embeddings", "boundary FRW shifted bounces and critical static branch", "branch-dependent C_partial relation", "vacuum conservation"],
            "conditional": ["background physical-domain interpretation", "global Z2 cap use of provisional B1", "principal-sector health", "tensor-sector readiness"],
            "open": ["parent derivation of B1", "source of C_partial and tau_A", "scalar potential and physical Z_partial", "full constraint-reduced bending and tensor spectrum", "physical gauge and fermionic maps", "absolute unit", "Standard Model limit"],
            "missing_vacuum_term": None,
            "completion_gate": COMPLETION_GATE,
            "recommended_next_branch": "bhsm-junction-mixed-stability-closure-v6-1-5",
            "full_bhsm_status": "FULL_BHSM_NOT_COMPLETE",
        },
    }


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    payloads = build_artifact_payloads(root)
    paths: list[Path] = []
    for key, filename in ARTIFACT_FILES.items():
        path = target / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        paths.append(path)
    return paths


def junction_background_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    report = build_artifact_payloads(repo_root)["report"]
    report["artifacts"] = {key: f"artifacts/{name}" for key, name in ARTIFACT_FILES.items()}
    return report


def junction_background_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# BHSM v6.1.4 Intrinsic M4 Junction-Supported Background Closure",
        "",
        f"Primary result: `{report['primary_result']}`.",
        "",
        report["central_answer"],
        "",
        f"Completion gate: `{report['completion_gate']}`.",
        "",
        "`FULL_BHSM_NOT_COMPLETE`.",
    ]) + "\n"
