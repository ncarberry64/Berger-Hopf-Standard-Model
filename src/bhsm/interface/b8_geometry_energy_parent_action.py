"""BHSM v6.0.2 minimal B8 geometry-energy parent-action audit.

The finite Lovelock classification is used as mathematics under explicit
locality, covariance, metric-only, and second-order-equation hypotheses.  No
coefficient, signature, domain, or confinement invariant is promoted to a
BHSM-derived physical input.
"""

from __future__ import annotations

import json
from math import factorial, sqrt
from pathlib import Path
from typing import Any


VERSION = "v6.0.2"
SPRINT = "bhsm-b8-geometric-action-construction-v6-0-2"
PRIMARY_RESULT = "BHSM_B8_MINIMAL_ACTION_FAMILY_IDENTIFIED"
PHYSICALITY_RESULT = "BHSM_ENERGY_GEOMETRY_PHYSICALITY_SOURCE_NOT_DERIVED"

ARTIFACT_FILES = {
    "parent_matrix": "BHSM_b8_parent_action_candidate_matrix_v6_0_2.json",
    "geometry_minimality": "BHSM_b8_geometry_term_minimality_v6_0_2.json",
    "lovelock": "BHSM_b8_lovelock_topological_density_audit_v6_0_2.json",
    "confinement": "BHSM_energy_geometry_confinement_invariant_v6_0_2.json",
    "physicality_action": "BHSM_energy_geometry_physicality_order_parameter_action_v6_0_2.json",
    "bulk_equations": "BHSM_b8_bulk_equations_conservation_v6_0_2.json",
    "signature": "BHSM_b8_parent_action_time_signature_v6_0_2.json",
    "boundary": "BHSM_b8_s7_variational_boundary_completion_v6_0_2.json",
    "collar": "BHSM_b8_s7_collar_action_no_double_counting_v6_0_2.json",
    "nested_hopf": "BHSM_b8_s7_nested_hopf_curvature_reduction_v6_0_2.json",
    "stationarity": "BHSM_b8_reduced_metric_action_stationarity_v6_0_2.json",
    "hessian": "BHSM_b8_coupled_physical_phase_hessian_v6_0_2.json",
    "thresholds": "BHSM_b8_three_threshold_distinction_v6_0_2.json",
    "reduction": "BHSM_b8_lower_dimensional_reduction_readiness_v6_0_2.json",
    "hidden_minimality": "BHSM_b8_parent_action_hidden_input_minimality_v6_0_2.json",
    "report": "BHSM_b8_geometry_energy_parent_action_report_v6_0_2.json",
}

GUARDS = {
    "empirical_inputs_used": False,
    "measured_mass_coupling_or_cosmology_scale_used": False,
    "einstein_hilbert_imported_as_bhsm_fact": False,
    "unspecified_wick_rotation_used": False,
    "signature_emergence_claimed": False,
    "surface_tension_derived": False,
    "scalar_vacuum_physically_localized": False,
    "absolute_unit_generated": False,
    "shared_black_hole_core_claimed": False,
    "singularity_resolution_claimed": False,
    "information_paradox_solved": False,
    "expansion_mechanism_derived": False,
    "alpha_derived": False,
    "particle_masses_derived": False,
    "full_bhsm_completion_claimed": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "existing_numerical_predictions_changed": False,
}

OPEN_GATES = (
    "OPEN_MISSING_ENERGY_GEOMETRY_CONFINEMENT_INVARIANT_SELECTION",
    "OPEN_MISSING_PHYSICALITY_COEFFICIENT_SOURCES",
    "OPEN_MISSING_B8_DOMAIN_AND_SIGNATURE_SELECTION",
    "OPEN_MISSING_B8_LOVEL0_AND_LOVEL1_COEFFICIENT_SOURCES",
    "OPEN_MISSING_LOVELLOCK_BRANCH_SELECTION",
    "OPEN_MISSING_ACTION_SELECTED_S7_METRIC_AND_SQUASHING",
    "OPEN_MISSING_PHYSICAL_COLLAR_SCALE_AND_INTERFACE_SOURCE",
    "OPEN_MISSING_PARENT_MATTER_ACTION",
    "OPEN_MISSING_PARENT_TO_V5_REDUCTION_THEOREM",
    "OPEN_MISSING_PHYSICAL_PHASE_STATIONARY_STABLE_SOLUTION",
    "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR",
    "FULL_BHSM_NOT_COMPLETE",
)


def _common(artifact: str) -> dict[str, Any]:
    return {"artifact":artifact,"version":VERSION,"sprint":SPRINT,"primary_result":PRIMARY_RESULT,"physicality_result":PHYSICALITY_RESULT,"preserved_results":["BHSM_S7_ARCHITECTURE_AMBIGUOUS","BHSM_B8_S7_PARENT_ACTION_SOURCE_MISSING"],"claim_boundary":"v6.0.2 identifies the smallest finite parent-action families permitted by explicit covariance and differential-order assumptions. BHSM does not select their coefficients, signature, confinement invariant, or a stable physical phase.",**GUARDS}


def lovelock_max_order(dimension: int) -> int:
    if dimension < 1:
        raise ValueError("dimension must be positive")
    return dimension // 2


def lovelock_classification(dimension: int, order: int) -> str:
    if dimension < 1 or order < 0:
        raise ValueError("invalid dimension or order")
    if 2 * order > dimension:
        return "IDENTICALLY_ZERO"
    if 2 * order == dimension and order > 0:
        return "EULER_TOPOLOGICAL_IN_BULK"
    return "DYNAMICAL_OR_VOLUME"


def coefficient_length_power(dimension: int, curvature_order: int) -> int:
    if dimension < 1 or curvature_order < 0:
        raise ValueError("invalid dimension or order")
    return 2 * curvature_order - dimension


def scale_weight(dimension: int, curvature_order: int) -> int:
    return dimension - 2 * curvature_order


def action_dimension_closes(dimension: int, curvature_order: int, coefficient_power: int) -> bool:
    return coefficient_power + dimension - 2 * curvature_order == 0


def constant_curvature_lovelock_density(dimension: int, order: int, sectional_curvature: float) -> float:
    if order < 0 or 2 * order > dimension:
        raise ValueError("Lovelock density does not exist at this order")
    return factorial(dimension) / factorial(dimension - 2 * order) * sectional_curvature**order


def sigma_potential(sigma: float, quadratic: float, quartic: float) -> float:
    return 0.5 * quadratic * sigma**2 + 0.25 * quartic * sigma**4


def sigma_stationary_branches(quadratic: float, quartic: float) -> dict[str, Any]:
    if quartic <= 0:
        raise ValueError("a bounded quartic truncation requires G>0")
    nonzero = [] if quadratic >= 0 else [-sqrt(-quadratic / quartic), sqrt(-quadratic / quartic)]
    return {"zero_hessian":quadratic,"zero_stability":"STABLE" if quadratic>0 else "THRESHOLD" if quadratic==0 else "UNSTABLE","nonzero_branches":nonzero,"nonzero_hessian":None if not nonzero else -2.0*quadratic}


def reduced_scale_term(radius: float, coefficient: float, weight: int) -> float:
    if radius <= 0:
        raise ValueError("radius must be positive")
    return coefficient * radius**weight


def reduced_scale_first_derivative(radius: float, coefficient: float, weight: int) -> float:
    if radius <= 0:
        raise ValueError("radius must be positive")
    return coefficient * weight * radius ** (weight - 1)


def parent_matrix_payload() -> dict[str, Any]:
    families = [
        {"id":"P0","action":"volume plus physicality/matter only","geometry":"(1/2)kappa_0 integral dmu_G","differential_order":0,"boundary_completion":"none for metric derivatives","physicality_support":"potential coupling possible but no propagating geometry","status":"INSUFFICIENT_GEOMETRIC_DYNAMICS"},
        {"id":"P1","action":"minimal two-derivative metric-sigma family","geometry":"(1/2) integral dmu_G[kappa_0+kappa_1 R]","differential_order":2,"boundary_completion":"kappa_1 integral_boundary epsilon_n K dmu_h","physicality_support":"sigma kinetic plus U_sigma(sigma,C_EG)","status":"SMALLEST_COHERENT_VARIATIONAL_FAMILY_COEFFICIENTS_UNSOURCED"},
        {"id":"P2","action":"P1 plus Gauss-Bonnet L2","geometry":"P1+(1/2)kappa_2 integral dmu_G L2","differential_order":2,"boundary_completion":"P1 plus Lovelock-Myers B2","physicality_support":"same unsourced C_EG sector","status":"FINITE_SECOND_ORDER_EXTENSION_NOT_REQUIRED"},
        {"id":"P3","action":"full dynamical 8D Lovelock through L3","geometry":"(1/2)sum_{k=0}^3 kappa_k integral dmu_G L_k","differential_order":2,"boundary_completion":"sum_{k=1}^3(kappa_k/2)B_k","physicality_support":"same unsourced C_EG sector","status":"MAXIMAL_SECOND_ORDER_LOCAL_METRIC_FAMILY"},
        {"id":"P4","action":"8D Euler L4 alone or appended","geometry":"(1/2)kappa_4 integral dmu_G L4","differential_order":"bulk variation zero in D=8","boundary_completion":"Euler transgression B4","physicality_support":"none by itself","status":"TOPOLOGICAL_NOT_GEOMETRIC_DYNAMICS"},
        {"id":"PX","action":"generic independent R2,R_AB2,R_ABCD2","geometry":"arbitrary quadratic curvature","differential_order":4,"boundary_completion":"higher-derivative boundary data required","physicality_support":"not mission-essential","status":"REJECTED_FROM_MINIMAL_SET_GHOST_OR_EXTRA_MODE_RISK"},
    ]
    term_ledger=[
        {"term":"S_geom,volume","formula":"(1/2)kappa_0 integral_M dmu_G","domain":"8D parent M","measure":"sqrt|G|d8x","signature":"Riemannian or Lorentzian absolute determinant","coefficient":"kappa_0","coefficient_dimension":"[A]L^-8","fields":["G_AB"],"variation":"-(kappa_0/2)G_AB contribution to the geometry equation after the common convention","boundary_term":"none","source_status":"COVARIANT_OPTION_UNSOURCED"},
        {"term":"S_geom,curvature","formula":"(1/2)kappa_1 integral_M dmu_G R","domain":"8D parent M","measure":"sqrt|G|d8x","signature":"Riemannian or Lorentzian","coefficient":"kappa_1","coefficient_dimension":"[A]L^-6","fields":["G_AB"],"variation":"kappa_1 EinsteinTensor_AB plus normal derivative boundary variation","boundary_term":"kappa_1 integral_boundary epsilon_n K dmu_h","source_status":"LOWEST_ORDER_TEST_TERM_NOT_BHSM_SELECTED"},
        {"term":"S_sigma,kinetic","formula":"integral_M dmu_G s_signature(1/2)Z_sigma G^AB partial_A sigma partial_B sigma","domain":"8D parent M","measure":"sqrt|G|d8x","signature":"s_signature=+1 Euclidean action; conventional Lorentzian action has -1/2 kinetic density","coefficient":"Z_sigma","coefficient_dimension":"[A]L^-6 for dimensionless sigma","fields":["G_AB","sigma"],"variation":"signed covariant sigma wave/Laplace operator and T_AB^(sigma)","boundary_term":"sigma normal flux; Dirichlet or natural Neumann data required","source_status":"CONDITIONAL_UNSOURCED"},
        {"term":"S_sigma,potential","formula":"integral_M dmu_G[1/2 A(C_EG)sigma^2+1/4 G(C_EG)sigma^4+...] with Lorentzian sign carried by the action convention","domain":"8D parent M","measure":"sqrt|G|d8x","signature":"potential contribution to stress depends on Euclidean/Lorentzian action convention","coefficient":"A(C_EG),G(C_EG)","coefficient_dimension":"[A]L^-8","fields":["G_AB","sigma","fields entering C_EG"],"variation":"A sigma+G sigma^3 plus C_EG variations","boundary_term":"inherits boundary terms of C_EG if it contains derivatives or interface data","source_status":"ARCHITECTURE_IDENTIFIED_SOURCE_NOT_DERIVED"},
        {"term":"S_boundary,completion","formula":"kappa_1 integral_partialM epsilon_n K dmu_h","domain":"7D boundary S7 only in applicable branches","measure":"sqrt|h|d7y","signature":"epsilon_n and induced signature explicit","coefficient":"kappa_1 fixed by bulk","coefficient_dimension":"[A]L^-6","fields":["h_ab","embedding normal"],"variation":"cancels normal derivatives of delta h for Dirichlet h_ab","boundary_term":"this is the boundary completion","source_status":"REQUIRED_IF_P1_IS_CHOSEN_NOT_PHYSICAL_TENSION"},
        {"term":"S_collar","formula":"no independent term in minimal P1; Gaussian-normal rewrite of bulk plus one boundary completion","domain":"S7x[0,1] coordinate neighborhood","measure":"ell_c J d rho dmu_h when rewritten","signature":"epsilon_n explicit","coefficient":None,"coefficient_dimension":None,"fields":["h_ab(rho)","sigma/matter traces"],"variation":"same bulk equations and endpoint terms; no duplicate Euler-Lagrange source","boundary_term":"already counted once","source_status":"NO_INDEPENDENT_COLLAR_SOURCE"},
        {"term":"S_constraint","formula":"zero as an independent covariant P1 term; diffeomorphism constraints arise from gauge symmetry","domain":"bulk/canonical split if performed","measure":None,"signature":"canonical constraints only after time split","coefficient":None,"coefficient_dimension":None,"fields":["metric and momenta after split"],"variation":"normal projections of the metric equation","boundary_term":"ensemble dependent","source_status":"NO_EXTRA_MULTIPLIER_RETAINED"},
        {"term":"S_matter,candidate","formula":"integral_M dmu_G L_matter only after a parent lift is supplied","domain":"8D parent M","measure":"sqrt|G|d8x","signature":"must be declared","coefficient":"parent kinetic/interaction coefficients","coefficient_dimension":"term dependent","fields":["T/Phi","gauge","fermion","optional top form"],"variation":"parent matter equations and conserved stress","boundary_term":"field-specific flux completion","source_status":"MISSING_NOT_FILLED_BY_V5_DOMAIN_REASSIGNMENT"},
    ]
    return {**_common("BHSM_b8_parent_action_candidate_matrix_v6_0_2"),"status":"FINITE_MINIMAL_ACTION_FAMILY_IDENTIFIED","families":families,"minimal_action_architecture":{"S_geom":"P1 volume plus scalar curvature","S_phys":"sigma kinetic and U_sigma(sigma,C_EG)","S_boundary":"coefficient-locked GHY completion","S_collar":"Gaussian-normal rewrite only","S_constraint":"no independent term; diffeomorphism constraints","S_matter_candidate":"missing parent lift; may be zero in the pure metric-sigma test family"},"P1_term_ledger":term_ledger,"minimal_retained_family":"P1 as the lowest-order test family","optional_second_order_extensions":["P2","P3"],"topological_appendix":"P4","selected_physical_family":None,"candidate_domains":["A","B_s","B_t"],"domain_not_covered_without_reformulation":["D is 9D canonical","E has product-dimension variants"]}


def geometry_minimality_payload() -> dict[str, Any]:
    terms = [
        {"term":"L0=1","required_by_covariance":False,"required_by_variation":False,"role":"volume/vacuum density","bulk_order":0,"coefficient":"kappa_0","dimension":"[A]L^-8","primitive":"ratio with another kappa can introduce a length","retained":"optional in P1"},
        {"term":"L1=R","required_by_covariance":False,"required_by_variation":"if chosen, GHY completion required","role":"lowest-derivative propagating metric dynamics","bulk_order":2,"coefficient":"kappa_1","dimension":"[A]L^-6","primitive":"unsourced","retained":True},
        {"term":"L2=Riem2-4Ric2+R2","required_by_covariance":False,"required_by_variation":"Myers B2 if chosen","role":"second-order Gauss-Bonnet extension","bulk_order":2,"coefficient":"kappa_2","dimension":"[A]L^-4","primitive":"unsourced","retained":"optional branch"},
        {"term":"L3 cubic Lovelock","required_by_covariance":False,"required_by_variation":"Myers B3 if chosen","role":"maximal dynamical Lovelock extension below Euler order","bulk_order":2,"coefficient":"kappa_3","dimension":"[A]L^-2","primitive":"unsourced","retained":"optional branch"},
        {"term":"L4 Euler8","required_by_covariance":False,"required_by_variation":"transgression B4 for boundary topology","role":"topological bulk invariant","bulk_order":0,"coefficient":"kappa_4","dimension":"[A]","primitive":"not quantized by current data","retained":"topological optional only"},
    ]
    return {**_common("BHSM_b8_geometry_term_minimality_v6_0_2"),"status":"P1_LOWEST_ORDER_P2_P3_FINITE_EXTENSIONS","assumptions":["local scalar density","diffeomorphism invariance","metric-only geometry","no more than second-order metric equations"],"terms":terms,"massless_EH_polarizations_in_D8":20,"lovelock_mode_warning":"generic nondegenerate Lovelock vacua carry the massless graviton count, but the effective kinetic sign can be ghostlike and degenerate roots can change the mode analysis","topology_fixes_coefficient":False}


def lovelock_payload() -> dict[str, Any]:
    rows=[]
    for k in range(6):
        classification=lovelock_classification(8,k)
        rows.append({"order":k,"density":f"L_{k}","curvature_power":k,"classification":classification,"bulk_equations":"nonzero second-order" if k<4 else "zero for k=4; density vanishes for k>4","scale_weight":scale_weight(8,k),"coefficient_dimension":f"[A] L^{coefficient_length_power(8,k)}","boundary":"none" if k==0 else f"generalized Lovelock boundary/transgression B_{k}" if k<=4 else "none"})
    return {**_common("BHSM_b8_lovelock_topological_density_audit_v6_0_2"),"status":"D8_LOVELLOCK_ORDERS_CLASSIFIED","definition":"L_k=(1/2^k)delta^(A1B1...AkBk)_(C1D1...CkDk) product_j R^(CjDj)_(AjBj)","rows":rows,"Euler_order_in_D8":4,"Euler_bulk_variation":0,"Euler_boundary_role":"Chern form/transgression supplies the boundary representative","coefficient_quantized":False,"quantization_missing":"global exp(iS/hbar) phase and normalized integral lattice argument","nested_Hopf_selects_combination":False}


def confinement_payload() -> dict[str, Any]:
    candidates=[
        {"name":"stress_trace","formula":"T^A_A","domain":"bulk","covariance":"scalar","locality":"local","dimension":"[A]L^-8","sign":"indefinite","scale":"depends on sourced stress","obstruction":"requires parent matter action and cannot alone encode enclosure"},
        {"name":"stress_square","formula":"T_AB T^AB","domain":"bulk","covariance":"scalar","locality":"local","dimension":"[A]^2L^-16","sign":"signature dependent; nonnegative only in restricted Euclidean cases","scale":"lambda^-16 if stress has canonical density weight","obstruction":"needs a dimensional conversion coefficient"},
        {"name":"normal_pressure_jump","formula":"Delta p=n^A n^B(T_AB^in-T_AB^out)","domain":"interface","covariance":"boundary scalar after normal selection","locality":"interface-local","dimension":"[A]L^-8","sign":"orientation/inside-outside convention","scale":"stress scaling","obstruction":"requires selected interface, two states, and junction law"},
        {"name":"extrinsic_confinement","formula":"K^2-Tr(K^2)","domain":"boundary","covariance":"boundary scalar","locality":"local","dimension":"L^-2","sign":"indefinite","scale":"lambda^-2","obstruction":"geometric but not an energy invariant"},
        {"name":"collar_strain","formula":"Tr[(h_rho^-1 partial_rho h_rho)^2]","domain":"collar","covariance":"foliation scalar","locality":"local after collar choice","dimension":"L^-2 for physical rho","sign":"nonnegative for Riemannian h","scale":"lambda^-2","obstruction":"depends on collar gauge and physical ell_c"},
        {"name":"enclosed_energy","formula":"integral_Omega T_AB u^A u^B dmu_slice","domain":"chosen spatial region","covariance":"requires unit timelike u and slice","locality":"controlled nonlocal/quasilocal","dimension":"energy/action per time convention","sign":"energy-condition dependent","scale":"volume and stress dependent","obstruction":"requires Lorentzian branch, time orientation, and region"},
        {"name":"current_norm","formula":"J_A J^A","domain":"bulk","covariance":"scalar","locality":"local","dimension":"current dependent","sign":"signature dependent","scale":"source dependent","obstruction":"no conserved parent current stored"},
        {"name":"top_form_flux","formula":"F_8^2 or fixed integrated Q","domain":"B8","covariance":"scalar/global","locality":"local F2; Q global","dimension":"normalization dependent","sign":"signature dependent","scale":"fixed-F and fixed-Q differ","obstruction":"v5.12 top-form action and source are not adopted"},
    ]
    return {**_common("BHSM_energy_geometry_confinement_invariant_v6_0_2"),"status":"FINITE_CANDIDATE_LEDGER_NO_INVARIANT_SELECTED","candidates":candidates,"selected_C_EG":None,"minimum_mathematical_meaning_of_envelopment":"a sourced, conserved stress distribution with a selected closed interface, nonzero junction/normal-stress data, and a stable coupled solution","analogy_prescription_used":False}


def physicality_action_payload() -> dict[str, Any]:
    return {**_common("BHSM_energy_geometry_physicality_order_parameter_action_v6_0_2"),"status":"PHYSICALITY_ACTION_ARCHITECTURE_CONDITIONAL_SOURCE_OPEN","sigma":{"dimension":"dimensionless parent candidate","zero":"undifferentiated candidate","nonzero":"differentiated candidate only after coupled stability"},"lorentzian_action":"S_sigma=integral sqrt(-G)[-1/2 Z_sigma G^AB partial_A sigma partial_B sigma-U_sigma(sigma,C_EG)]d8x","euclidean_action":"S_sigma,E=integral sqrt(G)[+1/2 Z_sigma |grad sigma|^2+U_sigma(sigma,C_EG)]d8x","coefficient_dimensions":{"Z_sigma":"[A]L^-6","A(C_EG)":"[A]L^-8","G(C_EG)":"[A]L^-8 for dimensionless sigma"},"potential":"U_sigma=1/2 A(C_EG) sigma^2+1/4 G(C_EG) sigma^4+O(sigma^6)","threshold":"A(C_EG,c)=0","phase_rules":{"A_positive":"sigma=0 locally stable","A_negative_G_positive":"sigma_vac^2=-A/G; physical only if full coupled Hessian and stress close"},"negative_quadratic_source":None,"A_ST_minus_2_imported":False,"G_ST_8_imported":False,"v5_target_reduction":"A_ST=-2,G_ST=8,sigma=+/-1/2 can be recovered numerically only after a normalized mode projection proves the parent-to-v5 coefficient map","physicality_result":PHYSICALITY_RESULT}


def bulk_equations_payload() -> dict[str, Any]:
    return {**_common("BHSM_b8_bulk_equations_conservation_v6_0_2"),"status":"VARIATIONAL_EQUATION_FAMILY_DERIVED_CONDITIONALLY","parent_action":"S=(1/2)sum_k kappa_k integral_M dmu_G L_k+S_sigma+S_matter+S_boundary+S_constraints","stress_definition":"T_AB=-2/sqrt|G| delta(S_sigma+S_matter)/delta G^AB","geometry_equation":"sum_k kappa_k H_AB^(k)=T_AB, with H^(0)_AB=-1/2 G_AB, H^(1)_AB=EinsteinTensor_AB, and higher H^(k) the Lovelock tensors","sigma_equations":{"Lorentzian":"nabla_A(Z_sigma nabla^A sigma)-partial U_sigma/partial sigma=0, including derivatives of field-dependent Z","Euclidean":"-nabla_A(Z_sigma nabla^A sigma)+partial U_sigma/partial sigma=0"},"other_field_equations":"delta S_matter/delta psi_i=0; not evaluable until parent matter terms are supplied","bianchi":"nabla^A H_AB^(k)=0 identically for every Lovelock order","conservation":"nabla^A T_AB=0 follows on shell from diffeomorphism invariance when all matter equations and boundary flux balance hold","constraints":{"Lorentzian":"normal-normal and normal-tangential projections are Hamiltonian/momentum constraints","Euclidean":"elliptic boundary-value constraints","canonical":"requires lapse, shift, momenta, and a separate Hamiltonian formulation"},"initial_value_requirements":"Lorentzian metric and extrinsic data satisfying constraints plus sigma/matter data and boundary conditions","not_called_Einstein_equation":"only the P1 kappa_1 term is proportional to the Einstein tensor; full equation is Lovelock"}


def signature_payload() -> dict[str, Any]:
    rows=[
        {"branch":"A","signature":"Riemannian (0,8)","equation_character":"elliptic after gauge fixing","time":None,"energy_current":"no physical timelike energy current","stability":"Euclidean bounded-action test","accepted_by_action":True,"selected":False},
        {"branch":"B_s/B_t","signature":"Lorentzian (1,7)","equation_character":"hyperbolic evolution plus constraints after gauge fixing","time":"one metric coordinate; normal or tangent to S7 by branch","energy_current":"requires chosen time orientation and stress","stability":"Hamiltonian/ghost and boundary flux tests","accepted_by_action":True,"selected":False},
        {"branch":"D","signature":"Lorentzian (1,8) on R_t x B8","equation_character":"canonical 8+1, not the same D=8 Lovelock action","time":"external canonical","energy_current":"canonical","stability":"requires 9D reformulation","accepted_by_action":False,"selected":False},
        {"branch":"E","signature":"Lorentzian M3,1 times Riemannian K","equation_character":"dimension depends on K","time":"M3,1","energy_current":"four-dimensional factor","stability":"Kaluza-Klein reduction required","accepted_by_action":"only after dimension-specific reformulation","selected":False},
    ]
    return {**_common("BHSM_b8_parent_action_time_signature_v6_0_2"),"status":"ACTION_ACCEPTS_EUCLIDEAN_OR_LORENTZIAN_BRANCHES_SIGNATURE_NOT_SELECTED","branches":rows,"signature_change":{"considered":False,"degeneracy_surface":None,"matching_conditions":None,"regularity":None,"reason":"the nondegenerate metric action has disconnected signature sectors unless a degenerate-metric extension is defined"},"time_orientation_selected":False,"causal_evolution_derived":False}


def boundary_payload() -> dict[str, Any]:
    rows=[
        {"bulk":"L1=R","completion":"B1=2 epsilon_n K before the common bulk factor 1/2; S_B1=kappa_1 integral epsilon_n K dmu_h","required":"cancels normal derivatives of delta h for Dirichlet induced metric","coefficient_relation":"fixed by kappa_1","boundary_data":"h_ab fixed","classification":"variational completion, not tension"},
        {"bulk":"L2 Gauss-Bonnet","completion":"generalized Myers B2","required":"Dirichlet Lovelock variation","coefficient_relation":"(kappa_2/2)B2","boundary_data":"h_ab fixed","classification":"variational completion"},
        {"bulk":"L3 cubic Lovelock","completion":"generalized Myers B3","required":"Dirichlet Lovelock variation","coefficient_relation":"(kappa_3/2)B3","boundary_data":"h_ab fixed","classification":"variational completion"},
        {"bulk":"L4 Euler8","completion":"Euler transgression/Chern form B4","required":"topological boundary representative","coefficient_relation":"(kappa_4/2)B4","boundary_data":"connection/metric convention","classification":"topological boundary term"},
    ]
    return {**_common("BHSM_b8_s7_variational_boundary_completion_v6_0_2"),"status":"LOVELOCK_DIRICHLET_BOUNDARY_COMPLETIONS_IDENTIFIED_CONDITIONALLY","general_formula":"B_k=2k integral_0^1 dt delta K product_{j=1}^{k-1}[1/2 R(h)-t^2 K K] with generalized-index contractions","rows":rows,"normal_convention":"G(n,n)=epsilon_n; orientation(M)=outward normal followed by orientation(boundary)","physical_surface_stress":"tau_ab=-2/sqrt|h| delta S_boundary,physical/delta h^ab; no physical boundary-energy action is sourced","free_K_K2_terms":"not added; required Lovelock polynomials have fixed bulk-coefficient relations","surface_tension":None}


def collar_payload() -> dict[str, Any]:
    return {**_common("BHSM_b8_s7_collar_action_no_double_counting_v6_0_2"),"status":"GAUSSIAN_NORMAL_REWRITE_IDENTIFIED_NO_INDEPENDENT_COLLAR_ACTION_SOURCED","embedding":"X:S7x[0,1]->B8, u=ell_c rho, X(Y,rho)=exp_Y(u n)","metric":"ds2=epsilon_n du2+h_ab(u,Y)dY^a dY^b","extrinsic":"K_ab=(1/2)partial_u h_ab in the declared convention","jacobian":"J=sqrt(|det h_u|/|det h_0|), partial_u log J=K","scale":{"ell_c":None,"dimension":"L","rho":"dimensionless"},"minimal_action":"bulk action rewritten in Gaussian-normal variables plus its single required boundary completion","independent_collar_term":None,"when_allowed":"only if a new interface material/transition field with its own source is derived","matching":"continuity/jump conditions follow from the single varied action","double_counting":{"bulk_rewrite_plus_duplicate_integral":False,"standalone_log_J":False,"v5_collar_promoted":False}}


def nested_hopf_payload() -> dict[str, Any]:
    return {**_common("BHSM_b8_s7_nested_hopf_curvature_reduction_v6_0_2"),"status":"NESTED_CURVATURE_REDUCTION_ARCHITECTURE_CONDITIONAL","topology":["S3->S7->S4","S1->S7->CP3","S2->CP3->S4","U(1) subset Sp(1)","p_H=tau o p_C"],"metric":"4+2+1 split: g_S7=L4^2 g_H4+L2^2 g_V2,cov+L1^2 eta^2; vertical dimensions 2+1 avoid double-counting S3 and S1","volume":"Vol(S7)=pi^4 L4^4 L2^2 L1/3 in the compatible standard convention","scalar_curvature":"R7=L4^-2 R4+L2^-2 R2+connection/O'Neill curvature terms depending on L2^2/L4^4 and L1^2/(...) ; exact constants require fixed connection normalization","action_reduction":"the L1 term conditionally yields base curvature, fiber curvature, connection-curvature kinetic terms, and scale-modulus gradients after integration","characteristic_forms":"c1,c2 and Euler/Pontryagin representatives are topological after trace/orientation normalization; they do not choose kappa_k","fiber_scale_dependence":"explicit and distinct for L4,L2,L1","selected_fibration":None,"complex_selected_for_U1":False,"quaternionic_selected_for_SU2":False,"squashing_selected":False}


def stationarity_payload() -> dict[str, Any]:
    return {**_common("BHSM_b8_reduced_metric_action_stationarity_v6_0_2"),"status":"SYMBOLIC_STATIONARITY_ARCHITECTURE_COEFFICIENTS_AND_INVARIANT_OPEN","ansatz":"S_red(L,r2,r1,sigma,ell_c)=sum_{k=0}^3 kappa_k L^(8-2k)F_k(r2,r1)+L^8 U_sigma(sigma,C_EG)+S_interface","coordinates":["overall L","r2=L2/L4","r1=L1/L4","sigma","ell_c/L"],"stationarity":{"L":"sum_k(8-2k)kappa_k L^(7-2k)F_k+physicality/interface terms=0","r2":"sum_k kappa_k L^(8-2k)partial_r2 F_k+...=0","r1":"sum_k kappa_k L^(8-2k)partial_r1 F_k+...=0","sigma":"A sigma+G sigma^3+...=0","collar":"no independent equation without interface action"},"hessian":"second derivatives of the displayed S_red; entries not numerical","ratio_fixing":"possible from dimensionless F_k competition even at one scale weight","absolute_scale":"requires competing weights and dimensionful kappa ratios such as kappa_1/kappa_0; those are unsourced primitives","flat_direction":"if only one homogeneous weight is nonzero, the overall scaling equation cannot select an isolated finite L without additional zero/constraint structure","stationary_solution":None}


def hessian_payload() -> dict[str, Any]:
    return {**_common("BHSM_b8_coupled_physical_phase_hessian_v6_0_2"),"status":"COUPLED_HESSIAN_DEFINED_NOT_EVALUABLE","order":["ln L","r2","r1","sigma","ell_c/L"],"definition":"H_phys,ij=partial_i partial_j S_red evaluated at a solution of every stationary equation","sigma_zero_entry":"H_sigma_sigma=A(C_EG)","sigma_formed_entry":"H_sigma_sigma=-2A for sigma^2=-A/G with A<0,G>0 before mixing","mixed_entries":"contain partial_C A, partial_C G and metric/stress dependence of C_EG","zero_modes":None,"negative_modes":None,"unprojected_physical_modes_checked":False,"physical_branch":None,"candidate_requirements":["valid selected domain","all stationary equations","sigma nonzero","conserved stress","no unprojected negative physical mode or declared metastability","well-posed boundary problem"]}


def thresholds_payload() -> dict[str, Any]:
    return {**_common("BHSM_b8_three_threshold_distinction_v6_0_2"),"status":"THREE_MECHANISMS_SEPARATED_NONE_PHYSICALLY_DERIVED","thresholds":[
        {"name":"physicality_formation","background":"prephysical sigma=0","operator":"coupled sigma/geometry Hessian","criterion":"lowest physical eigenvalue through A_eff=0","outcome":"formed sigma!=0 branch if full stability closes","current":PHYSICALITY_RESULT},
        {"name":"primordial_surface_release","background":"already formed boundary","operator":"normal-displacement surface Hessian","criterion":"lambda_surface=0","outcome":"loss of normal stability","current":"v5.12 source not closed"},
        {"name":"black_hole_de_enveloping","background":"localized enclosed state","operator":"unknown throat/core/interface Hessian","criterion":"unknown","outcome":"loss of enclosure","current":"not constructed"},
    ],"one_eigenvalue_reused":False,"shared_core_compatibility":{"one_connected_bulk":"topologically permitted","multiple_throat_embeddings":"permitted but not selected","conserved_flux":"requires sourced current and junction laws","shared_global_constraint":"possible in top-form candidate, unsourced","regular_matching":"not proved","many_throats_one_core":"future conditional architecture only"},"singularity_or_information_claim":False}


def reduction_payload() -> dict[str, Any]:
    rows=[
        {"target":"Berger S3 engine","map":"choose a quaternionic fiber or independent K=S3, select its metric, integrate other directions, and prove consistent truncation","classification":"DOMAIN_RECLASSIFIED_REDUCTION_UNTESTED"},
        {"target":"v5 scalar/topographic","map":"identify parent sigma/T/Phi modes and normalize their fiber profiles","classification":"RECOVERED_ONLY_AS_TARGET_FORM_A_ST_G_ST_MAP_OPEN"},
        {"target":"v5 boundary action","map":"reduce S7 boundary completion plus any separately sourced physical boundary energy","classification":"NOT_RECOVERED_VARIATIONAL_COMPLETION_IS_NOT_V5_PHYSICAL_BOUNDARY_ACTION"},
        {"target":"v5 collar","map":"Gaussian-normal reduction and dimensional truncation","classification":"ABSTRACT_JACOBIAN_RECOVERED_CONDITIONALLY_PHYSICAL_SCALE_OPEN"},
        {"target":"conditional gauge action","map":"connection-curvature terms and invariant fiber trace","classification":"UNTESTED_TRACE_AND_COEFFICIENT_OPEN"},
        {"target":"conditional fermion operator","map":"spin structure, vertical Dirac modes, and horizontal spin connection","classification":"UNTESTED"},
    ]
    return {**_common("BHSM_b8_lower_dimensional_reduction_readiness_v6_0_2"),"status":"REDUCTION_MAPS_IDENTIFIED_NO_FULL_RECOVERY","rows":rows,"historical_artifacts_altered":False,"scalar_pushforward_localization_ready":False}


def hidden_minimality_payload() -> dict[str, Any]:
    retained=[
        {"term":"kappa_1 R","role":"lowest-order propagating geometry","independently_adjustable":True,"source":None},
        {"term":"kappa_0","role":"optional volume density/constant-curvature competition","independently_adjustable":True,"source":None},
        {"term":"Z_sigma kinetic","role":"physicality propagation/stiffness","independently_adjustable":True,"source":None},
        {"term":"A(C_EG),G(C_EG)","role":"formation threshold and bounded branch","independently_adjustable":True,"source":None},
        {"term":"GHY B1","role":"required P1 Dirichlet completion","independently_adjustable":False,"source":"fixed by kappa_1"},
    ]
    return {**_common("BHSM_b8_parent_action_hidden_input_minimality_v6_0_2"),"status":"SMALLEST_TEST_FAMILY_P1_IDENTIFIED_PHYSICAL_INPUTS_UNSOURCED","retained":retained,"optional_not_minimal":["Gauss-Bonnet L2/Myers B2","cubic Lovelock L3/Myers B3","Euler8/transgression"],"removed":["independent generic R2,Ric2,Riem2 coefficients","arbitrary K,K2,TrK2 boundary energy","duplicate collar integral","unspecified signature-change sector"],"hidden_inputs":["domain","signature","time orientation","kappa_0","kappa_1","Z_sigma","C_EG choice","A and G functions","S7 metric ratios","connection normalization","ell_c","matter action","boundary ensemble"],"hidden_inputs_derived":False,"exact_missing_first_principle":"a BHSM rule selecting the conserved confinement invariant C_EG and its coupling to sigma, together with coefficient normalization and domain/signature"}


def report_payload() -> dict[str, Any]:
    return {**_common("BHSM_b8_geometry_energy_parent_action_report_v6_0_2"),"status":PRIMARY_RESULT,"central_answer":"Under explicit locality, diffeomorphism-invariance, metric-only, and second-order-equation assumptions, the eight-dimensional geometry sector is the finite Lovelock family and P1 is its smallest propagating Dirichlet test action. BHSM still supplies no principle selecting C_EG, A(C_EG), G(C_EG), coefficient normalizations, signature, or a stationary stable phase; therefore the physicality source is not derived.","minimal_parent_family":"P1: (1/2)integral(kappa_0+kappa_1R)+S_sigma+S_matter+kappa_1 integral epsilon_n K, with every coefficient and matter/confinement source explicit and unresolved","optional_finite_extensions":["Gauss-Bonnet P2","cubic Lovelock P3","Euler8 topological P4"],"selected_domain":None,"selected_action":None,"selected_C_EG":None,"derived":["D8 Lovelock order, topology, scale-weight, and coefficient-dimension classification","smallest well-posed two-derivative metric-sigma Dirichlet action shape","bulk Lovelock equation, sigma equation, Bianchi/conservation implication","required versus physical boundary-term separation","three-threshold separation","no-double-counting collar rule"],"derived_conditionally":["formal A=0 physicality threshold and sigma^2=-A/G branch","standard Lovelock boundary completions","nested Hopf reduction architecture","symbolic stationarity and coupled Hessian"],"invalidated":["Euler8 as bulk dynamics","generic curvature-squared terms as minimal ghost-safe additions","A_ST=-2 and G_ST=8 as parent coefficients","energy enclosure language as a sourced invariant","a nonzero current as Lorentzian-signature creation","GHY/Myers completion as physical surface tension","one Hessian eigenvalue for formation, release, and de-enveloping"],"still_requiring_new_mathematics":list(OPEN_GATES),"completion_gate_status":"V6_0_2_STOP_MINIMAL_FAMILY_IDENTIFIED_PHYSICALITY_SOURCE_OPEN","full_closure_sequence":"paused before scalar localization","recommended_next_branch":"bhsm-energy-geometry-confinement-invariant-v6-0-3"}


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _=repo_root
    return {"parent_matrix":parent_matrix_payload(),"geometry_minimality":geometry_minimality_payload(),"lovelock":lovelock_payload(),"confinement":confinement_payload(),"physicality_action":physicality_action_payload(),"bulk_equations":bulk_equations_payload(),"signature":signature_payload(),"boundary":boundary_payload(),"collar":collar_payload(),"nested_hopf":nested_hopf_payload(),"stationarity":stationarity_payload(),"hessian":hessian_payload(),"thresholds":thresholds_payload(),"reduction":reduction_payload(),"hidden_minimality":hidden_minimality_payload(),"report":report_payload()}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=False)+"\n"


def materialize_artifacts(root: Path) -> list[Path]:
    target=root/"artifacts"; target.mkdir(parents=True,exist_ok=True); payloads=build_artifact_payloads(root); written=[]
    for key,name in ARTIFACT_FILES.items():
        path=target/name; path.write_text(deterministic_json(payloads[key]),encoding="utf-8"); written.append(path)
    return written


def b8_parent_action_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    _=repo_root; report=report_payload(); report["artifacts"]={key:f"artifacts/{name}" for key,name in ARTIFACT_FILES.items()}; return report


def b8_parent_action_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join(["# BHSM v6.0.2 B8 Geometry-Energy Parent Action","",f"Primary result: `{report['primary_result']}`.",f"Physicality result: `{report['physicality_result']}`.","",report["central_answer"],"",f"Completion gate: `{report['completion_gate_status']}`.","","## Open gates","",*[f"- `{gate}`" for gate in report["still_requiring_new_mathematics"]]])+"\n"
