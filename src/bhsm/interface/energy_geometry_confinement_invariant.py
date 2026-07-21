"""BHSM v6.0.3 energy--geometry confinement and sigma-Hessian audit.

The module derives the operator architecture implied by admissible local
quadratic couplings.  It deliberately does not select a coupling, coefficient,
signature, matter action, or physical phase.
"""

from __future__ import annotations

import json
from math import factorial, sqrt
from pathlib import Path
from typing import Any


VERSION = "v6.0.3"
SPRINT = "bhsm-energy-geometry-confinement-invariant-v6-0-3"
PRIMARY_RESULT = "BHSM_ENERGY_GEOMETRY_FINITE_INVARIANT_FAMILY_IDENTIFIED"
THRESHOLD_RESULT = "BHSM_PHYSICALITY_THRESHOLD_ARCHITECTURE_IDENTIFIED"

ARTIFACT_FILES = {
    "sigma_domain": "BHSM_sigma_domain_candidate_audit_v6_0_3.json",
    "couplings": "BHSM_action_native_sigma_coupling_ledger_v6_0_3.json",
    "admissibility": "BHSM_confinement_invariant_admissibility_matrix_v6_0_3.json",
    "locality": "BHSM_confinement_local_quasilocal_global_classification_v6_0_3.json",
    "operator": "BHSM_complete_sigma_quadratic_operator_v6_0_3.json",
    "spectrum": "BHSM_physicality_spectral_threshold_problem_v6_0_3.json",
    "finite": "BHSM_physicality_finite_enclosure_correction_v6_0_3.json",
    "nonlinear": "BHSM_physicality_nonlinear_formed_phase_v6_0_3.json",
    "wall": "BHSM_physicality_domain_wall_envelope_v6_0_3.json",
    "emergent": "BHSM_physicality_emergent_boundary_test_v6_0_3.json",
    "coupled": "BHSM_coupled_geometry_sigma_hessian_v6_0_3.json",
    "matter": "BHSM_parent_matter_dependency_audit_v6_0_3.json",
    "v5_map": "BHSM_parent_to_v5_sigma_reduction_map_v6_0_3.json",
    "thresholds": "BHSM_three_threshold_dependency_ledger_v6_0_3.json",
    "scale": "BHSM_physicality_scale_hidden_input_audit_v6_0_3.json",
    "report": "BHSM_energy_geometry_confinement_invariant_report_v6_0_3.json",
}

GUARDS = {
    "empirical_inputs_used": False,
    "measured_scale_mass_coupling_or_cosmology_used": False,
    "A_ST_minus_2_imported": False,
    "G_ST_8_imported": False,
    "sigma_half_reverse_engineered": False,
    "signature_emergence_claimed": False,
    "physical_spacetime_formation_claimed": False,
    "primordial_release_claimed": False,
    "black_hole_de_enveloping_claimed": False,
    "shared_core_claimed": False,
    "absolute_unit_generated": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "existing_numerical_predictions_changed": False,
    "full_bhsm_completion_claimed": False,
}

OPEN_GATES = (
    "OPEN_MISSING_SIGMA_COUPLING_SELECTION_PRINCIPLE",
    "OPEN_MISSING_PARENT_MATTER_ACTION",
    "OPEN_MISSING_PHYSICALITY_COEFFICIENT_SOURCES",
    "OPEN_MISSING_SIGNATURE_AND_PHYSICAL_DOMAIN_SELECTION",
    "OPEN_MISSING_SELF_ADJOINT_PHYSICAL_OPERATOR_DOMAIN",
    "OPEN_MISSING_NONLINEAR_COUPLED_STABLE_PHASE",
    "OPEN_MISSING_DYNAMIC_INTERFACE_AND_JUNCTION_SOURCE",
    "OPEN_MISSING_PARENT_TO_V5_REDUCTION_THEOREM",
    "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR",
    "FULL_BHSM_NOT_COMPLETE",
)


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "threshold_result": THRESHOLD_RESULT,
        "preserved_results": [
            "BHSM_B8_MINIMAL_ACTION_FAMILY_IDENTIFIED",
            "BHSM_ENERGY_GEOMETRY_PHYSICALITY_SOURCE_NOT_DERIVED",
        ],
        "claim_boundary": (
            "v6.0.3 derives the sigma quadratic-operator architecture and a finite "
            "family of admissible conditional sources. The parent action does not "
            "select their couplings, coefficients, physical signature, or a stable phase."
        ),
        **GUARDS,
    }


def interaction_coefficient_length_power(source_length_power: int) -> int:
    """Power of L for a coefficient multiplying dimensionless sigma^2 C.

    ``C`` has dimension L**source_length_power and the D=8 density must have
    dimension [A] L**-8, so the coefficient is [A] L**(-8-source_power).
    """

    return -8 - source_length_power


def hessian_eigenvalue(
    kinetic: float,
    laplacian_eigenvalue: float,
    baseline: float,
    *source_terms: float,
) -> float:
    if kinetic <= 0 or laplacian_eigenvalue < 0:
        raise ValueError("elliptic spectral diagnostic requires Z>0 and k^2>=0")
    return kinetic * laplacian_eigenvalue + baseline + sum(source_terms)


def quadratic_mode_action(amplitude: float, eigenvalue: float) -> float:
    """Quadratic action whose second amplitude variation is ``eigenvalue``."""

    return 0.5 * eigenvalue * amplitude**2


def symmetric_two_mode_eigenvalues(diagonal_1: float, diagonal_2: float, coherence: float) -> tuple[float, float]:
    """Eigenvalues of [[d1,c],[c,d2]], ordered from lowest to highest."""

    center = 0.5 * (diagonal_1 + diagonal_2)
    splitting = sqrt(0.25 * (diagonal_1 - diagonal_2) ** 2 + coherence**2)
    return center - splitting, center + splitting


def finite_radius_threshold(mode_number: float, kinetic: float, effective_mass: float) -> float | None:
    """Conditional L_c for k_0=mode_number/L and no extra surface shift."""

    if mode_number < 0 or kinetic <= 0:
        raise ValueError("mode number must be nonnegative and kinetic positive")
    if effective_mass >= 0 or mode_number == 0:
        return None
    return mode_number * sqrt(kinetic / -effective_mass)


def quartic_mode_branch(eigenvalue: float, quartic_overlap: float) -> dict[str, Any]:
    if quartic_overlap <= 0:
        raise ValueError("nonlinear stabilization requires a positive quartic overlap")
    amplitudes = [] if eigenvalue >= 0 else [
        -sqrt(-eigenvalue / quartic_overlap),
        sqrt(-eigenvalue / quartic_overlap),
    ]
    return {
        "amplitudes": amplitudes,
        "energy_shift": 0.0 if not amplitudes else -(eigenvalue**2) / (4.0 * quartic_overlap),
        "formed_mode_hessian": None if not amplitudes else -2.0 * eigenvalue,
    }


def planar_wall_diagnostics(kinetic: float, quadratic: float, quartic: float) -> dict[str, float]:
    """Flat one-dimensional Z2 wall for U=G/4(sigma^2-v^2)^2."""

    if kinetic <= 0 or quadratic >= 0 or quartic <= 0:
        raise ValueError("wall requires Z>0, A<0, and G>0")
    vacuum = sqrt(-quadratic / quartic)
    return {
        "vacuum": vacuum,
        "thickness": sqrt(2.0 * kinetic / -quadratic),
        "tension": (2.0 * sqrt(2.0) / 3.0) * sqrt(kinetic) * (-quadratic) ** 1.5 / quartic,
    }


def conformal_trace_hessian(log_metric_second_derivative: float, stress_trace: float) -> float:
    """Quadratic source from g_tilde=A(sigma)^2 g when A'(0)=0."""

    return log_metric_second_derivative * stress_trace


def top_form_hessian(
    coupling_second_derivative: float,
    invariant_or_charge_square: float,
    degree: int,
    ensemble: str,
    coupling_at_zero: float = 1.0,
) -> float:
    if degree < 1 or coupling_at_zero <= 0:
        raise ValueError("invalid form degree or background coupling")
    prefactor = invariant_or_charge_square / (2.0 * factorial(degree))
    if ensemble == "fixed_f":
        return coupling_second_derivative * prefactor
    if ensemble == "fixed_Q":
        return -coupling_second_derivative * prefactor / coupling_at_zero**2
    raise ValueError("ensemble must be fixed_f or fixed_Q")


def sigma_domain_payload() -> dict[str, Any]:
    rows = [
        {"id":"A","domain":"bulk scalar on M8","core_surface":"yes, through spatially varying solutions","dynamic_interface":"level set possible only after nonlinear solution","finite_wall":"yes conditionally","parent_matter":"local covariant coupling","v5_reduction":"structurally compatible by normalized mode projection","hopf_symmetry":"preserved for invariant/homogeneous modes","status":"STRONGEST_ADMISSIBLE_DOMAIN"},
        {"id":"B","domain":"boundary scalar on S7","core_surface":"surface only","dynamic_interface":"no; boundary is presupposed","finite_wall":"not a bulk enclosure wall","parent_matter":"pullback or junction source required","v5_reduction":"possible boundary target only","hopf_symmetry":"can be preserved","status":"CANNOT_GENERATE_ITS_OWN_BOUNDARY"},
        {"id":"C","domain":"collar scalar on S7 x [0,1]","core_surface":"yes within an imposed collar","dynamic_interface":"no without a parent embedding theorem","finite_wall":"conditional","parent_matter":"requires collar localization map","v5_reduction":"structurally compatible","hopf_symmetry":"can be preserved","status":"CONDITIONAL_IMPOSED_COLLAR"},
        {"id":"D","domain":"bulk scalar with boundary-localized eigenmode","core_surface":"yes","dynamic_interface":"possible only as a solution of A with boundary conditions","finite_wall":"conditional","parent_matter":"bulk plus boundary variation","v5_reduction":"structurally compatible","hopf_symmetry":"mode dependent","status":"SPECTRAL_SUBBRANCH_OF_A_NOT_INDEPENDENT_DOMAIN"},
        {"id":"E","domain":"associated-bundle or fiber-dependent scalar","core_surface":"fiber differential possible","dynamic_interface":"not established","finite_wall":"requires bundle connection and norm","parent_matter":"representation dependent","v5_reduction":"blocked pending pushforward","hopf_symmetry":"must be checked mode by mode","status":"UNDERDEFINED_BUNDLE_BRANCH"},
    ]
    return {**_common("BHSM_sigma_domain_candidate_audit_v6_0_3"),"status":"BULK_M8_STRONGEST_ADMISSIBLE_SIGMA_DOMAIN","rows":rows,"selected_for_operator_audit":"A with D treated as a boundary-localized spectral subbranch","physical_domain_selected_by_BHSM":False}


def coupling_payload() -> dict[str, Any]:
    rows = [
        {"family":"curvature","domain":"bulk M8","scalar_status":"R and Lovelock densities are diffeomorphism scalars","coefficient_dimension":"xi_k has [A]L^(2k-8) for dimensionless sigma","action_term":"(1/2)sigma^2[xi_1 R+xi_2 L_2+xi_3 L_3]","hessian":"xi_1 R+xi_2 L_2+xi_3 L_3","classification":"conditional geometric scalarization, not enclosed energy","parity":"even","source_status":"P1 permits xi_1; P2/P3 permit higher Lovelock couplings but do not require them"},
        {"family":"universal_conformal_metric","domain":"bulk M8","scalar_status":"T=G^AB T_AB is a scalar after parent matter variation","coefficient_dimension":"alpha_2 dimensionless for dimensionless sigma","action_term":"S_m[A(sigma)^2 G,Psi]","hessian":"alpha_2 T when A(0)=1 and A'(0)=0","classification":"local trace source","parity":"even metric function","source_status":"action-native if a parent matter action and A(sigma) are supplied"},
        {"family":"matter_lagrangian","domain":"bulk M8","scalar_status":"L_m is a scalar density representative but is not representation invariant","coefficient_dimension":"f dimensionless in the direct multiplicative convention","action_term":"f(sigma)L_m","hessian":"f''(0)L_m","classification":"representation dependent","parity":"f'(0)=0","source_status":"rejected unless additive/redefinition invariance is closed"},
        {"family":"current_or_disformal","domain":"bulk M8 after current/time-field declaration","scalar_status":"J_AJ^A and T_AB u^A u^B are scalars only after their fields are supplied","coefficient_dimension":"current and normalization dependent","action_term":"sigma^2 J_AJ^A or matter[A^2G+B^2 u u]","hessian":"coefficient times current invariant","classification":"branch dependent","parity":"can be even","source_status":"requires action-derived current/timelike field and normalization"},
        {"family":"interface_pressure","domain":"dynamic codimension-one interface","scalar_status":"Delta p_n is an interface scalar after normal and two sides are defined","coefficient_dimension":"interface action normalization required","action_term":"interface functional whose variation yields Delta p_n","hessian":"junction and normal-stress response","classification":"interface/quasilocal","parity":"model dependent","source_status":"blocked before a dynamic interface and normal exist"},
        {"family":"stress_invariants","domain":"bulk M8","scalar_status":"complete contractions/eigenvalue polynomials are scalars","coefficient_dimension":"T^2 coupling needs [A]^-1 L^8 for dimensionless sigma","action_term":"sigma^2 times T, T_ABT^AB, or trace-free square","hessian":"corresponding invariant times explicit coefficient","classification":"finite effective-operator family","parity":"even","source_status":"higher matter operators need new scales and a parent variational definition"},
        {"family":"top_form","domain":"bulk M8 locally or global charge sector","scalar_status":"F_d^2 is local scalar; Q is an integrated global invariant","coefficient_dimension":"depends on declared form normalization","action_term":"Z_F(sigma)F_d^2/(2 d!)","hessian":"opposite ensemble response for fixed f and fixed Q","classification":"local F^2 or global Q source","parity":"Z_F'(0)=0","source_status":"conditional; no BHSM top-form source selected"},
        {"family":"extrinsic_collar","domain":"declared boundary/interface/collar","scalar_status":"complete contractions are boundary scalars after embedding and foliation declaration","coefficient_dimension":"term dependent boundary density coefficient","action_term":"boundary/collar sigma^2 K, K^2, Tr(S^2), strain, or J terms","hessian":"Robin/endomorphism terms on declared interface","classification":"interface source only when independent action term exists","parity":"even","source_status":"variational completions are coefficient locked, not free tension"},
        {"family":"harmonic_coherence","domain":"mode space of the declared self-adjoint bulk/interface problem","scalar_status":"C_mn is basis-covariant matrix data derived by invariant inner products","coefficient_dimension":"same operator dimension as diagonal Hessian eigenvalues","action_term":"mode projection C_mn=<f_m,Xi_total f_n> derived from the same local parent action","hessian":"eigenvalues of diag(Z k_n^2+A_0)+C_mn","classification":"candidate spectral selection theorem, not an additional guessed local scalar","parity":"inherits the parent sigma parity","source_status":"requires derived spectrum, nonzero off-diagonal overlaps, phases/coherence, and a control variable"},
    ]
    return {**_common("BHSM_action_native_sigma_coupling_ledger_v6_0_3"),"status":"FINITE_CONDITIONAL_COUPLING_FAMILY","rows":rows,"selected_family":None,"minimal_threshold_capable_families":["curvature scalarization","universal conformal trace","top-form in a declared ensemble"],"selection_hypothesis":"constructive harmonic coherence may select an eigenchannel only if C_mn and its phase-sensitive off-diagonal entries follow from the parent action","selection_by_desired_threshold":False}


def admissibility_payload() -> dict[str, Any]:
    rows = [
        {"candidate":"R and Lovelock densities","domain":"bulk","action_native":"optional explicit sigma^2 coupling","dimension_closed":"with xi_k","conservation":"yes for full varied action","radiation_sensitive":"curvature only indirectly","verdict":"ADMISSIBLE_CONDITIONAL_GEOMETRIC_NOT_ENCLOSED_ENERGY"},
        {"candidate":"T","domain":"bulk with parent matter","action_native":"from conformal physical metric","dimension_closed":"alpha_2 dimensionless for dimensionless sigma","conservation":"frame exchange must be included","radiation_sensitive":"no when T=0","verdict":"ADMISSIBLE_CONDITIONAL_TRACE_SOURCE"},
        {"candidate":"L_m","domain":"bulk","action_native":"explicit f(sigma)L_m","dimension_closed":"yes","conservation":"modified","radiation_sensitive":"representation dependent","verdict":"REJECTED_WITHOUT_SHIFT_REDEFINITION_THEOREM"},
        {"candidate":"T_AB T^AB and trace-free square","domain":"bulk","action_native":"requires composite operator coupling","dimension_closed":"new inverse-density scale required","conservation":"full variation required","radiation_sensitive":"yes but Lorentzian sign indefinite","verdict":"CONDITIONAL_HIGHER_OPERATOR_UNSOURCED"},
        {"candidate":"J_AJ^A or T_AB u^A u^B","domain":"bulk","action_native":"only with current/u action","dimension_closed":"normalization required","conservation":"current equation required","radiation_sensitive":"branch dependent","verdict":"BLOCKED_UNDECLARED_TIMELIKE_STRUCTURE"},
        {"candidate":"Delta p_n","domain":"dynamic interface","action_native":"junction variation required","dimension_closed":"stress dimension","conservation":"junction conservation required","radiation_sensitive":"yes","verdict":"BLOCKED_INTERFACE_NOT_DERIVED"},
        {"candidate":"K, K^2, Tr(S^2), collar strain","domain":"boundary/collar","action_native":"only independent interface action terms","dimension_closed":"new boundary coefficients","conservation":"shape equation required","radiation_sensitive":"not intrinsically energy sensitive","verdict":"CONDITIONAL_GEOMETRIC_INTERFACE_FAMILY"},
        {"candidate":"F_d^2 or Q","domain":"bulk/global","action_native":"top-form action required","dimension_closed":"Z_F normalization required","conservation":"form equation","radiation_sensitive":"not a generic matter response","verdict":"CONDITIONAL_ENSEMBLE_DEPENDENT_FLUX_SOURCE"},
        {"candidate":"enclosed energy","domain":"region plus surface/normal/time flow","action_native":"boundary Hamiltonian or quasilocal definition required","dimension_closed":"normalization definition dependent","conservation":"flux law required","radiation_sensitive":"possibly","verdict":"NOT_A_LOCAL_SCALAR_BLOCKED_QUASILOCAL_DEFINITION"},
        {"candidate":"harmonic/octave constructive interference","domain":"mode space of a declared self-adjoint operator","action_native":"only when C_mn=<f_m,Xi f_n> is derived from the parent action","dimension_closed":"frequency/eigenvalue ratios are dimensionless; crossing magnitude still needs sourced operator coefficients","conservation":"inherits the full action if projection is complete","radiation_sensitive":"source-overlap dependent","verdict":"ADMISSIBLE_SELECTION_HYPOTHESIS_SPECTRUM_AND_COHERENCE_NOT_DERIVED"},
    ]
    return {**_common("BHSM_confinement_invariant_admissibility_matrix_v6_0_3"),"status":"MULTIPLE_INDEPENDENT_INVARIANTS_SURVIVE_CONDITIONALLY","axioms":["scalar on declared domain","action-native","dimensionally closed","coordinate independent","not an EOM residual","conservation compatible","signature audited","no arbitrary matter-Lagrangian shift","derived Hessian sign"],"rows":rows,"selected_C_EG":None,"single_scalar_reduction_proved":False,"finite_vector_C_EG":"(R,L2,L3,T,composite stress terms,interface data,F2/Q) with branch-specific domains"}


def locality_payload() -> dict[str, Any]:
    return {**_common("BHSM_confinement_local_quasilocal_global_classification_v6_0_3"),"status":"DOMAIN_CLASSES_SEPARATED","local":["R","L2","L3","T","T_AB T^AB","F_d^2","J_AJ^A when J exists"],"interface":["Delta p_n","K","K^2","Tr(S^2)","junction stress","collar strain after collar choice"],"quasilocal":["enclosed energy","boundary Hamiltonian","integrated surface flux"],"global":["total top-form flux Q","connected-core charge"],"illegal_mixing_rule":"quantities from different classes cannot be summed without measures, normalization, and variation rules"}


def operator_payload() -> dict[str, Any]:
    return {**_common("BHSM_complete_sigma_quadratic_operator_v6_0_3"),"status":"GENERAL_ACTION_NATIVE_OPERATOR_DERIVED_CONDITIONALLY","euclidean_operator":"H_sigma^(0)=-nabla_A(Z_0 nabla^A)+A_0+Xi_geom+Xi_matter+Xi_boundary+Xi_collar+Xi_flux+Xi_other","lorentzian_equation_operator":"nabla_A(Z_0 nabla^A)-A_0-Xi_total under the recorded conventional Lorentzian action sign; stability requires a selected spatial problem","principal_symbol":"Z_0 G^AB k_A k_B","ellipticity_condition":"Riemannian G and Z_0>0","hyperbolicity_condition":"Lorentzian G, Z_0>0, and a selected globally hyperbolic branch","components":{"baseline":"A_0=U_0''(0)","geometric":"xi_1 R+xi_2 L2+xi_3 L3","matter":"alpha_2 T for parity-even conformal metric, plus separately declared composite operators","boundary":"Robin endomorphism from independent boundary potential plus coefficient-locked nonminimal completion","collar":"only from an independent collar action, not a coordinate rewrite","flux":"Z_F''(0)F_d^2/(2d!) at fixed f; opposite response after fixed-Q elimination","other":"no EOM residual is admitted"},"reduced_diagnostics":{"homogeneous_bulk":"lambda=A_0+Xi_total for k_0=0","finite_region":"lambda_0=Z_0 q_0^2/L^2+A_eff+lambda_boundary+lambda_collar","collar_mode":"one-dimensional Sturm-Liouville operator -d_rho(Z d_rho)+A_eff with endpoint data","curvature_branch":"lambda_n=Z_0 k_n^2+A_0+xi_1 R (+xi_2 L2+xi_3 L3 when declared)","trace_branch":"lambda_n=Z_0 k_n^2+A_0+alpha_2 T; trace-free T gives no shift","top_form_fixed_f":"add +Z_F'' F_d^2/(2d!) in the recorded Euclidean convention","top_form_fixed_Q":"opposite quadratic response after eliminating F at fixed Q","harmonic_two_mode":"lambda_-=half(h11+h22)-sqrt[quarter(h11-h22)^2+|C12|^2]"},"domain":"H^2(M8) functions obeying Dirichlet, Neumann, or real Robin data on every boundary component","inner_product":"<f,g>=integral_M dmu_G conjugate(f) g, with positive Euclidean measure","boundary_form":"integral_boundary dmu_h Z_0[conjugate(f)n.g-(n.conjugate(f))g]","self_adjointness":"closed real Robin/Dirichlet/Neumann data make the boundary form vanish; interface transmission data require a matched junction form","pointwise_threshold_sufficient":False}


def spectrum_payload() -> dict[str, Any]:
    return {**_common("BHSM_physicality_spectral_threshold_problem_v6_0_3"),"status":"SPECTRAL_THRESHOLD_WELL_DEFINED_CONDITIONALLY","problem":"H_sigma^(0) f_n=lambda_n f_n","lambda_phys":"lowest non-gauge normalizable eigenvalue in the declared self-adjoint domain","stable":"lambda_phys>0","marginal":"lambda_phys=0","unstable":"lambda_phys<0","compact":"discrete spectrum with finite multiplicities for elliptic self-adjoint compact-domain problem","noncompact":"continuous spectrum may occur; threshold uses the spectral infimum and normalizable/bound-state qualification","zero_modes":"symmetry or collective zero modes must be projected before lambda_phys","crossing_direction":"d lambda_phys/dc=<f_0,(dH/dc)f_0> for a normalized simple eigenmode and action-derived control c","harmonic_selection_test":{"matrix":"H_mn=(Z k_n^2+A_0)delta_mn+C_mn","coherence":"constructive selection requires action-derived nonzero off-diagonal C_mn and a coherent phase relation","octave":"omega_m/omega_n=2^p is admissible only as a derived dimensionless spectral relation","order_of_magnitude":"base-10 grouping alone is representation/bookkeeping, not an action selection law","verdict":"CANDIDATE_SELECTION_THEOREM_NOT_DERIVED"},"control_variable":None,"threshold_derived":False,"reason":"coupling, background, domain, coherence matrix, and control source are not selected"}


def finite_payload() -> dict[str, Any]:
    return {**_common("BHSM_physicality_finite_enclosure_correction_v6_0_3"),"status":"FINITE_SIZE_CORRECTION_DERIVED_CONDITIONALLY","formula":"lambda_0(L)=Z_0 q_0^2/L^2+A_eff(L)+lambda_boundary(L)+lambda_collar(L)","q0":"dimensionless lowest wave number fixed only after geometry and boundary conditions","conditional_radius":"L_c=q_0 sqrt[Z_0/(-A_eff)] only for constant A_eff<0 and zero extra boundary/collar shift","homogeneous_neumann_warning":"q_0=0, so no universal finite-size barrier","absolute_unit":None,"reason":"Z_0/A_eff and q_0 are unsourced branch data"}


def nonlinear_payload() -> dict[str, Any]:
    return {**_common("BHSM_physicality_nonlinear_formed_phase_v6_0_3"),"status":"NONLINEAR_MODE_BRANCH_DERIVED_CONDITIONALLY","mode_action":"S(q)=lambda_phys q^2/2+g_eff q^4/4+...","existence":"lambda_phys<0 and g_eff>0","amplitudes":"q=+/-sqrt(-lambda_phys/g_eff)","energy_shift":"-lambda_phys^2/(4g_eff)","formed_mode_hessian":"-2 lambda_phys>0","local_homogeneous_limit":"sigma_vac^2=-A_eff/G_eff","stress":"obtained by metric variation of every kinetic, potential, and source coupling; not evaluated without a background","backreaction":"coupled Lovelock-matter-sigma equation required","physical_phase_derived":False,"unresolved":"other sigma, metric, collar, and matter Hessian modes"}


def wall_payload() -> dict[str, Any]:
    return {**_common("BHSM_physicality_domain_wall_envelope_v6_0_3"),"status":"PLANAR_DOMAIN_WALL_FORMULA_CONDITIONAL_FULL_ENVELOPE_OPEN","equation":"-Z sigma''+geometric friction+dU_eff/dsigma=source terms","flat_Z2_profile":"sigma(rho)=v tanh[(rho-rho0)/delta] for U=G(sigma^2-v^2)^2/4","v":"sqrt(-A/G)","thickness":"delta=sqrt(2Z/(-A))","tension":"tau=(2 sqrt(2)/3) sqrt(Z)(-A)^(3/2)/G","boundary_conditions":"opposite vacua at infinite normal distance for the planar solution; finite collar data remain open","orientation":"sigma_core=0 to sigma_surface!=0 is not the same Z2 kink and needs a phase-coexistence potential/source","stability":"translation zero mode expected in the planar idealization; full transverse/coupled spectrum not computed","collar_endpoint_selected":False,"envelope_solution_derived":False}


def emergent_payload() -> dict[str, Any]:
    return {**_common("BHSM_physicality_emergent_boundary_test_v6_0_3"),"status":"EMERGENT_BOUNDARY_NOT_DERIVED","candidate":"Sigma_phys={x|sigma(x)=sigma_*}","requirements":{"sigma_star":"must be action-derived","regular_value":"d sigma nonzero on the level set","induced_metric":"nondegenerate pullback","normal":"n_A=partial_A sigma/|d sigma| in a valid signature branch","extrinsic_curvature":"derived from that normal","junction":"stress localization and matching derived from one action"},"requirements_closed":False,"imposed_S7_relabelled_emergent":False}


def coupled_payload() -> dict[str, Any]:
    return {**_common("BHSM_coupled_geometry_sigma_hessian_v6_0_3"),"status":"COUPLED_HESSIAN_ARCHITECTURE_ONLY","geometry_equation":"sum_{k in selected P family} kappa_k H_AB^(k)=T_AB^matter+T_AB^sigma+interface terms","sigma_equation":"delta S/dsigma=0","families":{"P1":"L0+L1","P2":"P1+L2","P3":"P2+L3"},"collective_coordinates":["sigma modes","ln L","nested squashing variables","interface displacement","matter/flux collective modes"],"block_hessian":"[[H_GG,H_Gsigma,H_Gm],[H_sigmaG,H_sigmasigma,H_sigmam],[H_mG,H_msigma,H_mm]] plus interface rows","stationary_solution":None,"negative_modes":None,"physical_branch":None,"P_family_selected_for_threshold":False}


def matter_payload() -> dict[str, Any]:
    rows = [
        {"candidate":"curvature","needs":"metric background only","symbolic_T_sufficient":True,"full_Lm_required":False},
        {"candidate":"universal trace","needs":"conserved symbolic T_AB plus an action-level conformal metric map","symbolic_T_sufficient":"for background Hessian screen only","full_Lm_required":"for coupled variation and nonlinear phase"},
        {"candidate":"matter Lagrangian","needs":"representation-fixed L_m","symbolic_T_sufficient":False,"full_Lm_required":True},
        {"candidate":"stress square","needs":"matter composite-operator definition and metric variation","symbolic_T_sufficient":False,"full_Lm_required":True},
        {"candidate":"current/disformal","needs":"current or timelike-vector action and normalization","symbolic_T_sufficient":False,"full_Lm_required":True},
        {"candidate":"pressure jump","needs":"inside/outside actions, dynamic interface, normal, and junction source","symbolic_T_sufficient":False,"full_Lm_required":True},
        {"candidate":"top form","needs":"form action, ensemble, coefficient, and optional charged source","symbolic_T_sufficient":False,"full_Lm_required":"top-form sector only"},
    ]
    return {**_common("BHSM_parent_matter_dependency_audit_v6_0_3"),"status":"PARENT_MATTER_ACTION_INDISPENSABLE_FOR_ENERGY_TRIGGER_SELECTION","rows":rows,"minimal_next_action":"a covariant conserved parent matter action with declared signature and either a parity-even conformal metric map or another independently justified sigma coupling","fabricated_source_used":False}


def v5_map_payload() -> dict[str, Any]:
    return {**_common("BHSM_parent_to_v5_sigma_reduction_map_v6_0_3"),"status":"STRUCTURALLY_COMPATIBLE_REDUCTION_BLOCKED","map":[{"parent":"integral_M Z_0 (nabla sigma)^2/2","operation":"normalized mode projection and fiber/collar pushforward","target":"canonical reduced kinetic term","status":"conditional"},{"parent":"<f,H_sigma^(0)f>","operation":"divide by reduced kinetic normalization","target":"A_ST","status":"not evaluated"},{"parent":"projected quartic overlap","operation":"divide by kinetic normalization and amplitude scale","target":"G_ST","status":"not evaluated"},{"parent":"local sigma amplitude","operation":"mode normalization times sigma_scale","target":"physical local amplitude","status":"blocked"}],"A_ST_minus_2":"not parent-derived","G_ST_8":"not parent-derived","sigma_half":"not parent-derived","reverse_engineering_used":False}


def thresholds_payload() -> dict[str, Any]:
    rows = [
        {"name":"physicality formation","operator":"H_sigma^(0) about sigma=0","background":"undifferentiated parent phase","status":"architecture identified"},
        {"name":"primordial release","operator":"H_surface about formed compact phase","background":"compact enclosure with sourced boundary/interface","status":"not derived here"},
        {"name":"black-hole de-enveloping","operator":"coupled topology/envelope Hessian","background":"throat or core interface","status":"not derived here"},
    ]
    return {**_common("BHSM_three_threshold_dependency_ledger_v6_0_3"),"status":"THREE_HESSIAN_PROBLEMS_REMAIN_DISTINCT","rows":rows,"dependency":"formation -> nonlinear stable phase -> dynamic interface -> possible release analysis; black-hole branch additionally needs throat/core source and global matching","one_eigenvalue_reused":False,"shared_core":"structurally compatible only if multiple embeddings, conservation, orientation, matching, and regularity close"}


def scale_payload() -> dict[str, Any]:
    rows = [
        {"coupling":"xi_1 sigma^2 R","source_power":"L^-2","coefficient_dimension":"[A]L^-6"},
        {"coupling":"xi_2 sigma^2 L2","source_power":"L^-4","coefficient_dimension":"[A]L^-4"},
        {"coupling":"xi_3 sigma^2 L3","source_power":"L^-6","coefficient_dimension":"[A]L^-2"},
        {"coupling":"alpha_2 sigma^2 T","source_power":"[A]L^-8","coefficient_dimension":"dimensionless"},
        {"coupling":"gamma_T2 sigma^2 T_ABT^AB","source_power":"[A]^2L^-16","coefficient_dimension":"[A]^-1 L^8"},
        {"coupling":"boundary beta sigma^2","source_power":"boundary density","coefficient_dimension":"[A]L^-7"},
        {"coupling":"top-form Z_F sigma dependence","source_power":"normalization dependent","coefficient_dimension":"must follow declared form convention"},
    ]
    return {**_common("BHSM_physicality_scale_hidden_input_audit_v6_0_3"),"status":"MULTIPLE_UNSOURCED_NORMALIZATIONS_REMAIN","rows":rows,"hidden_inputs":["Z_0","A_0","quartic normalization","xi_k","conformal alpha_2","composite-stress scale","boundary Robin coefficient","collar length","top-form normalization and ensemble","mode normalization and q_0"],"one_common_parent_scale_proved":False,"absolute_unit":None,"arbitrary_function_A_CEG_used":False}


def report_payload() -> dict[str, Any]:
    return {**_common("BHSM_energy_geometry_confinement_invariant_report_v6_0_3"),"status":PRIMARY_RESULT,"central_answer":"The complete parity-even sigma Hessian admits a finite branch-organized vector of curvature, trace, composite-stress, interface, collar, flux, and mode-coherence sources. Several survive conditionally, but no BHSM parent-action principle yet selects one coupling or its sign and normalization. Constructive harmonic interference is a precise candidate selection theorem through the projected coherence matrix, not yet a derived trigger. Therefore no unique C_EG or physicality transition is derived.","sigma_domain":"bulk M8 is the strongest admissible audit domain; a boundary-localized mode is a spectral subbranch","selected_C_EG":None,"derived":["complete sigma quadratic-operator architecture","domain and self-adjointness conditions","finite-size and lowest-mode threshold formula","conditional quartic-mode and planar-wall formulas","local/interface/quasilocal/global separation","parent-matter dependency theorem for energy-trigger selection"],"derived_conditionally":["curvature, trace, top-form, and interface Hessian contributions when their actions exist","lambda_phys=0 crossing problem","nonzero stabilized mode for lambda_phys<0 and positive quartic overlap","harmonic-coherence selection test H_mn when the spectrum and overlap matrix are action-derived"],"invalidated":["boundary-only sigma as generator of its own boundary","matter Lagrangian coupling without shift/redefinition closure","enclosed energy as a local scalar","stress square as automatically positive in Lorentzian signature","variational completion as free tension","pointwise A_eff=0 as a universal finite-region threshold","base-10 magnitude grouping alone as an action selection law","reuse of formation eigenvalue for release or de-enveloping"],"still_requiring_new_mathematics":list(OPEN_GATES),"completion_gate_status":"V6_0_3_STOP_FINITE_INVARIANT_FAMILY_THRESHOLD_ARCHITECTURE_ONLY","recommended_next_branch":"bhsm-physicality-coupling-selection-theorem-v6-0-4"}


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    return {
        "sigma_domain": sigma_domain_payload(),
        "couplings": coupling_payload(),
        "admissibility": admissibility_payload(),
        "locality": locality_payload(),
        "operator": operator_payload(),
        "spectrum": spectrum_payload(),
        "finite": finite_payload(),
        "nonlinear": nonlinear_payload(),
        "wall": wall_payload(),
        "emergent": emergent_payload(),
        "coupled": coupled_payload(),
        "matter": matter_payload(),
        "v5_map": v5_map_payload(),
        "thresholds": thresholds_payload(),
        "scale": scale_payload(),
        "report": report_payload(),
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    payloads = build_artifact_payloads(root)
    written = []
    for key, name in ARTIFACT_FILES.items():
        path = target / name
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        written.append(path)
    return written


def confinement_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    _ = repo_root
    report = report_payload()
    report["artifacts"] = {key: f"artifacts/{name}" for key, name in ARTIFACT_FILES.items()}
    return report


def confinement_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# BHSM v6.0.3 Energy--Geometry Confinement Invariant",
        "",
        f"Primary result: `{report['primary_result']}`.",
        f"Threshold result: `{report['threshold_result']}`.",
        "",
        report["central_answer"],
        "",
        f"Completion gate: `{report['completion_gate_status']}`.",
        "",
        "## Open gates",
        "",
        *[f"- `{gate}`" for gate in report["still_requiring_new_mathematics"]],
    ]) + "\n"
