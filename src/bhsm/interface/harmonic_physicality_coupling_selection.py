"""BHSM v6.0.4 harmonic physicality coupling-selection audit.

The exact free and round-S7 results are separated from conditional nonlinear
normal forms.  No unsourced interaction, preferred ratio, or physical scale is
promoted.
"""

from __future__ import annotations

import json
from math import factorial, sqrt
from pathlib import Path
from typing import Any, Iterable, Sequence


VERSION = "v6.0.4"
SPRINT = "bhsm-physicality-coupling-selection-theorem-v6-0-4"
PRIMARY_RESULT = "BHSM_HARMONIC_SELECTION_SOURCE_NOT_DERIVED"
COUPLING_RESULT = "BHSM_PHYSICALITY_COUPLING_SELECTION_BLOCKED"

ARTIFACT_FILES = {
    "linear": "BHSM_harmonic_linear_no_selection_theorem_v6_0_4.json",
    "fields": "BHSM_harmonic_interfering_parent_field_ledger_v6_0_4.json",
    "spectrum": "BHSM_harmonic_exact_mode_representation_spectrum_v6_0_4.json",
    "tensors": "BHSM_harmonic_cubic_quartic_interaction_tensors_v6_0_4.json",
    "rules": "BHSM_harmonic_geometric_selection_rule_matrix_v6_0_4.json",
    "octave": "BHSM_harmonic_octave_discrete_scale_audit_v6_0_4.json",
    "resonance": "BHSM_harmonic_resonance_condition_registry_v6_0_4.json",
    "normal_form": "BHSM_harmonic_resonant_normal_form_v6_0_4.json",
    "locked": "BHSM_harmonic_phase_locked_solution_v6_0_4.json",
    "coherence": "BHSM_harmonic_basis_invariant_coherence_v6_0_4.json",
    "variational": "BHSM_harmonic_constrained_variational_selection_v6_0_4.json",
    "stress": "BHSM_harmonic_coherent_incoherent_stress_v6_0_4.json",
    "sigma_shift": "BHSM_harmonic_sigma_hessian_shift_v6_0_4.json",
    "threshold": "BHSM_harmonic_physicality_threshold_v6_0_4.json",
    "coupled": "BHSM_harmonic_coupled_coherent_sigma_hessian_v6_0_4.json",
    "metric": "BHSM_harmonic_geometric_modulus_selection_v6_0_4.json",
    "enclosure": "BHSM_harmonic_emergent_enclosure_test_v6_0_4.json",
    "v5_map": "BHSM_harmonic_parent_to_v5_compatibility_v6_0_4.json",
    "scale": "BHSM_harmonic_absolute_scale_hidden_input_audit_v6_0_4.json",
    "report": "BHSM_harmonic_physicality_coupling_selection_report_v6_0_4.json",
}

GUARDS = {
    "empirical_inputs_used": False,
    "preferred_harmonic_ratio_inserted": False,
    "base_ten_scaling_promoted": False,
    "A_ST_minus_2_imported": False,
    "G_ST_8_imported": False,
    "sigma_half_target_fitted": False,
    "particle_or_generation_identification_made": False,
    "signature_emergence_claimed": False,
    "emergent_enclosure_claimed": False,
    "primordial_release_claimed": False,
    "black_hole_de_enveloping_claimed": False,
    "absolute_unit_generated": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "existing_numerical_predictions_changed": False,
    "full_bhsm_completion_claimed": False,
}

OPEN_GATES = (
    "OPEN_MISSING_ACTION_SELECTED_INTERFERING_PARENT_FIELD",
    "OPEN_MISSING_EXACT_SELECTED_B8_S7_OPERATOR_DOMAIN",
    "OPEN_MISSING_PARENT_NONLINEAR_COEFFICIENT_SOURCES",
    "OPEN_MISSING_NESTED_HOPF_BRANCHING_AND_OVERLAP_TENSORS",
    "OPEN_MISSING_NONTRIVIAL_RESONANT_NORMAL_FORM",
    "OPEN_MISSING_STABLE_PHASE_LOCKED_COHERENT_SOLUTION",
    "OPEN_MISSING_INVARIANT_NEGATIVE_SIGMA_HESSIAN_SHIFT",
    "OPEN_MISSING_COUPLED_COHERENT_SIGMA_STABLE_PHASE",
    "OPEN_MISSING_DYNAMIC_ENCLOSURE_AND_JUNCTION",
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
        "coupling_selection_result": COUPLING_RESULT,
        "preserved_results": [
            "BHSM_ENERGY_GEOMETRY_FINITE_INVARIANT_FAMILY_IDENTIFIED",
            "BHSM_PHYSICALITY_THRESHOLD_ARCHITECTURE_IDENTIFIED",
        ],
        "claim_boundary": (
            "v6.0.4 proves linear phase no-selection and finds one exact round-S7 "
            "octave commensurability, but the accepted parent family does not supply "
            "the selected nonlinear field, coefficient, stable coherent solution, or "
            "negative invariant sigma-Hessian shift needed for physicality selection."
        ),
        **GUARDS,
    }


def quadratic_modal_action(eigenvalues: Sequence[float], amplitudes: Sequence[complex]) -> float:
    if len(eigenvalues) != len(amplitudes):
        raise ValueError("eigenvalues and amplitudes must have equal length")
    return 0.5 * sum(value * abs(amplitude) ** 2 for value, amplitude in zip(eigenvalues, amplitudes))


def symmetric_block_eigenvalues(d1: float, d2: float, mixing: float) -> tuple[float, float]:
    center = 0.5 * (d1 + d2)
    split = sqrt(0.25 * (d1 - d2) ** 2 + mixing**2)
    return center - split, center + split


def round_s7_scalar_eigenvalue(level: int, radius: float = 1.0) -> float:
    if level < 0 or radius <= 0:
        raise ValueError("level must be nonnegative and radius positive")
    return level * (level + 6) / radius**2


def round_s7_scalar_degeneracy(level: int) -> int:
    if level < 0:
        raise ValueError("level must be nonnegative")
    return (2 * level + 6) * factorial(level + 5) // (factorial(level) * factorial(6))


def exact_octave_pairs(max_level: int) -> list[tuple[int, int]]:
    if max_level < 0:
        raise ValueError("max_level must be nonnegative")
    return [
        (low, high)
        for low in range(1, max_level + 1)
        for high in range(low + 1, max_level + 1)
        if high * (high + 6) == 4 * low * (low + 6)
    ]


def u1_overlap_allowed(charges: Iterable[int]) -> bool:
    return sum(charges) == 0


def quartic_tensor(coefficient: float, overlap: float) -> float:
    """Fourth action derivative for S4=(g/4!) sum I_mnpq a_m...a_q."""

    return coefficient * overlap


def quartic_mode_action(amplitude: float, coefficient: float, overlap: float) -> float:
    """Single-mode normalization S4=(g I/4!) a^4."""

    return coefficient * overlap * amplitude**4 / factorial(4)


def sigma_self_hessian_shift(quartic: float, background_sigma: float) -> float:
    """Second derivative of G sigma^4/4 about a scalar background."""

    return 3.0 * quartic * background_sigma**2


def independent_field_sigma_shift(coupling: float, invariant: float) -> float:
    """Shift from S_int=(gamma/2) sigma^2 O_Psi."""

    return coupling * invariant


def projector_norm(state: Sequence[complex], orthonormal_basis: Sequence[Sequence[complex]]) -> float:
    """Return ||P_R state||^2 for an orthonormal basis of a subspace."""

    total = 0.0
    for vector in orthonormal_basis:
        if len(vector) != len(state):
            raise ValueError("basis and state dimensions differ")
        coefficient = sum(complex(v).conjugate() * complex(s) for v, s in zip(vector, state))
        total += abs(coefficient) ** 2
    return float(total)


def linear_payload() -> dict[str, Any]:
    return {**_common("BHSM_harmonic_linear_no_selection_theorem_v6_0_4"),"status":"LINEAR_ORTHONORMAL_MODES_HAVE_NO_PHASE_SELECTION","operator":"self-adjoint O f_n=lambda_n f_n","inner_product":"<f_m,f_n>=delta_mn","quadratic_action":"S2=(1/2)sum_n lambda_n |a_n|^2","relative_phase_dependence":False,"off_diagonal_rule":"a finite Hermitian quadratic block is diagonalized; its eigenvalues and spectral projectors are physical, while removable cross terms are basis choice rather than nonlinear interference","degenerate_rule":"operators and projectors restricted to a degenerate eigenspace transform unitarily; basis labels do not select coherence","C_mn_classification":"background or boundary-dependent quadratic mixing only after sourced; otherwise unsourced candidate","negative_theorem":"linear superposition of orthogonal modes cannot select a phase-locked binding state"}


def fields_payload() -> dict[str, Any]:
    rows = [
        {"field":"sigma","domain":"bulk M8","kinetic":"v6.0.3 conditional Laplace-type operator","spectrum":"unselected B8 domain; round S7 restriction known","nonlinearity":"parity-even quartic architecture, coefficient unsourced","stress":"standard scalar stress conditional on action/signature","conserved":"energy after Lorentzian time selection; Z2 is discrete","sigma_relation":"it is the order parameter itself","verdict":"CIRCULAR_AS_INDEPENDENT_TRIGGER"},
        {"field":"parent matter scalar","domain":"bulk M8 candidate","kinetic":"missing","spectrum":"missing","nonlinearity":"missing","stress":"missing parent action","conserved":"unknown","sigma_relation":"could couple through sigma^2 O_Psi","verdict":"PARENT_ACTION_MISSING"},
        {"field":"gauge curvature modes","domain":"parent bulk/boundary unresolved","kinetic":"parent gauge action missing","spectrum":"missing","nonlinearity":"would follow non-Abelian action","stress":"missing normalization","conserved":"gauge charge after action/domain","sigma_relation":"no selected coupling","verdict":"PARENT_ACTION_MISSING"},
        {"field":"metric or shape perturbations","domain":"bulk/interface","kinetic":"Lovelock family conditional; physical gauge/domain missing","spectrum":"full geometric Hessian missing","nonlinearity":"exists formally from geometry but tensors not derived on selected background","stress":"geometry equation rather than independent matter stress","conserved":"diffeomorphism constraints","sigma_relation":"curvature coupling conditional","verdict":"GEOMETRIC_RESONANCE_BRANCH_OPEN"},
        {"field":"nested Hopf connection modes","domain":"bundle candidate","kinetic":"not selected","spectrum":"branching and normalization missing","nonlinearity":"not derived","stress":"not derived","conserved":"fiber labels conditional","sigma_relation":"not derived","verdict":"ACTION_AND_BUNDLE_NORM_MISSING"},
        {"field":"top-form flux","domain":"bulk/global","kinetic":"candidate F_d^2","spectrum":"no local propagating polarizations","nonlinearity":"sigma-dependent normalization conditional","stress":"ensemble dependent","conserved":"global flux Q","sigma_relation":"conditional Z_F(sigma)","verdict":"NO_LOCAL_HARMONIC_INTERFERENCE"},
        {"field":"spinor bilinears","domain":"bulk/boundary unresolved","kinetic":"Dirac parent action missing","spectrum":"domain and eta data missing","nonlinearity":"not derived","stress":"not derived","conserved":"current only after action","sigma_relation":"not derived","verdict":"PARENT_ACTION_MISSING"},
    ]
    supplements = {
        "sigma": ("L2(M8,dmu_G) on a Riemannian spectral branch", "v6.0.3 Dirichlet/Neumann/real Robin options, none selected", "normalized projection to the existing scalar/topographic mode remains blocked"),
        "parent matter scalar": ("missing with its action", "missing", "no existing Berger-S3 matter lift"),
        "gauge curvature modes": ("gauge-fixed physical inner product missing", "gauge/ghost boundary complex missing", "Berger-S3 gauge attachment is not parent-derived"),
        "metric or shape perturbations": ("gauge-quotiented DeWitt-type product not selected", "metric/interface domain and shape data missing", "nested metric carries Berger-S3 fiber geometry but no completed physical spectrum"),
        "nested Hopf connection modes": ("bundle norm and trace missing", "bundle/collar conditions missing", "direct geometric relation, action normalization missing"),
        "top-form flux": ("global flux-sector pairing", "fixed-f and fixed-Q ensembles differ", "no local Berger-S3 harmonic carrier"),
        "spinor bilinears": ("Dirac inner product signature/domain dependent", "spin structure and self-adjoint boundary condition missing", "Berger-S3 spinor spectrum not lifted to the parent action"),
    }
    for row in rows:
        row["inner_product"], row["boundary_conditions"], row["berger_s3_relation"] = supplements[row["field"]]
    return {**_common("BHSM_harmonic_interfering_parent_field_ledger_v6_0_4"),"status":"NO_ACTION_SELECTED_NONCIRCULAR_INTERFERING_FIELD","rows":rows,"selected_parent_field":None,"unspecified_wave_field_added":False}


def spectrum_payload() -> dict[str, Any]:
    rows = [{"level":l,"eigenvalue_unit_radius":round_s7_scalar_eigenvalue(l),"degeneracy":round_s7_scalar_degeneracy(l),"SO8_representation":"scalar harmonic [l,0,0,0]","frequency_massless":f"sqrt({l}({l}+6))/L"} for l in range(0,11)]
    return {**_common("BHSM_harmonic_exact_mode_representation_spectrum_v6_0_4"),"status":"ROUND_S7_SCALAR_SUBSPECTRUM_EXACT_PARENT_SPECTRUM_OPEN","operator":"-Delta_S7 on round radius L","measure":"round dmu_S7","domain":"smooth scalar harmonics on closed round S7","eigenvalue":"l(l+6)/L^2","degeneracy":"(2l+6)(l+5)!/[l!6!]","rows":rows,"round_symmetry":"SO(8); Hopf-preserving subgroup descriptions do not replace the full isometry","quaternionic_Hopf":"S3 -> S7 -> S4 with Sp(2)xSp(1) structure subgroup","complex_Hopf":"S1 -> S7 -> CP3 with SU(4)xU(1) structure subgroup","twistor":"S2 -> CP3 -> S4","squashed_branch":"exact isometry and branching depend on the unselected squashing convention","fiber_labels":None,"winding":None,"B8_operator_spectrum_complete":False,"standard_model_representations_inferred":False}


def tensors_payload() -> dict[str, Any]:
    return {**_common("BHSM_harmonic_cubic_quartic_interaction_tensors_v6_0_4"),"status":"SIGMA_TENSORS_FORMAL_COEFFICIENT_AND_MODES_UNSOURCED","expansion_background":"sigma=0","quadratic":"K_mn=<f_m,H_sigma^(0)f_n>","cubic":{"formula":"G_mnp=U'''(0) integral_M dmu f_m f_n f_p plus derivative terms","sigma_Z2_value":0,"permutation":"fully symmetric for nondifferentiated real-scalar potential","dimension":"action coefficient times normalized-mode dimensions"},"quartic":{"formula":"H_mnpq=G_0 integral_M dmu f_m f_n f_p f_q plus declared derivative interactions","permutation":"fully symmetric for nondifferentiated real-scalar potential","coefficient_source":None,"squashing_dependence":"measure and harmonics","fiber_scale_dependence":"normalization and overlap"},"derivative_interactions":"not present in the minimal constant-Z scalar truncation; possible only from declared field-dependent kinetic terms","exact_overlap_values":None,"action_derivative_identity":"G and H are respectively third and fourth derivatives of the same parent action"}


def rules_payload() -> dict[str, Any]:
    rows = [
        {"gate":"representation","condition":"R_m tensor R_n tensor R_p (or four factors) contains the trivial representation","status":"exact rule; branching inputs incomplete"},
        {"gate":"U1/fiber winding","condition":"signed charge sum is zero","status":"exact after charges and conjugations are declared"},
        {"gate":"sigma parity","condition":"odd sigma tensors vanish at sigma=0","status":"cubic sigma coupling excluded"},
        {"gate":"orientation/Hopf number","condition":"sector labels must close under the action integral","status":"no selected topological sector"},
        {"gate":"collar parity","condition":"normal-mode product must be even under declared collar reflection","status":"collar/domain not selected"},
        {"gate":"boundary","condition":"all modes obey one self-adjoint boundary/transmission domain","status":"open"},
    ]
    return {**_common("BHSM_harmonic_geometric_selection_rule_matrix_v6_0_4"),"status":"SELECTION_RULE_ARCHITECTURE_EXACT_OVERLAPS_OPEN","rows":rows,"survival":"nonzero invariant overlap AND frequency resonance are both required","commensurability_implies_coupling":False,"coupling_implies_resonance":False}


def octave_payload() -> dict[str, Any]:
    return {**_common("BHSM_harmonic_octave_discrete_scale_audit_v6_0_4"),"status":"ONE_EXACT_ROUND_S7_SCALAR_OCTAVE_PAIR_RATIO_ONLY","distinctions":{"harmonic_number":"integer mode label, not generally frequency multiple","octave":"frequency ratio 2","eigenvalue_ratio":"4 for Laplace dispersion omega^2=lambda","wavelength_ratio":"inverse frequency only in declared dispersion","amplitude_hierarchy":"state data","energy_hierarchy":"depends on occupation and normalization","log_interval":"log ratio, base convention unless dynamics selects q"},"round_S7_massless_octave_pairs_through_100":exact_octave_pairs(100),"exact_nonzero_pair":{"lower_l":4,"higher_l":10,"lambda_lower":"40/L^2","lambda_higher":"160/L^2","frequency_ratio":2},"derivation":"(l_high+3)^2-4(l_low+3)^2=-27; positive factor pairs give the unique nonzero solution (4,10)","dyadic_tower":False,"discrete_scale_factor":None,"base_ten_status":"bookkeeping only; no logarithmic action or spectral q=10 derived","absolute_scale_fixed":False}


def resonance_payload() -> dict[str, Any]:
    return {**_common("BHSM_harmonic_resonance_condition_registry_v6_0_4"),"status":"COMMENSURABILITY_FOUND_REQUIRED_INTERACTION_ABSENT_OR_OPEN","cubic":"s_m omega_m+s_n omega_n+s_p omega_p=0","quartic":"sum_i s_i omega_i=0","octave_pair":{"frequency":"omega_10=2 omega_4","cubic_channel":"would require a nonzero 10-4-4 tensor","sigma_Z2_cubic":"zero at sigma=0","verdict":"EXACT_FREQUENCY_RELATION_NO_SIGMA_THREE_WAVE_COUPLING"},"quartic_warning":"the 2:1 pair alone is not a four-wave resonance; omega_10-omega_4-omega_4+omega_0=0 uses a zero mode whose nonzero amplitude already leaves sigma=0","trivial_pairwise_quartets":"frequency identities with the same incoming/outgoing occupations do not select phase locking","near_resonance":"not ranked without a derived detuning scale","symmetry_protected_resonance":None}


def normal_form_payload() -> dict[str, Any]:
    return {**_common("BHSM_harmonic_resonant_normal_form_v6_0_4"),"status":"NORMAL_FORM_ARCHITECTURE_ONLY_NO_RETAINED_NONTRIVIAL_CHANNEL","ansatz":"psi=sum_n[A_n(t)e^-iomega_nt conjugate+cc] f_n","resonant_Hamiltonian":"H_res=sum omega_n |A_n|^2 + retained action-derived resonant tensor contractions","equation":"i dot A_n=partial H_res/partial conjugate(A_n)","averaging_regime":"slow amplitudes and detuning small relative to carrier frequencies; not established for BHSM","conserved":{"energy":"yes for autonomous conservative reduction","exact_parent_charge":"field dependent and not supplied","wave_action":"only approximate when rotating-wave U1 symmetry emerges","winding":"only after declared representation labels"},"dissipation_added":False,"manley_rowe_relations":None}


def locked_payload() -> dict[str, Any]:
    return {**_common("BHSM_harmonic_phase_locked_solution_v6_0_4"),"status":"NO_ACTION_DERIVED_PHASE_LOCKED_SOLUTION","stationary_ansatz":"A_n=r_n exp[i(theta_n-Omega_n t)]","amplitude_equations":"partial constrained H_res/partial r_n=0","phase_equations":"partial H_res/partial theta_n=0","phases_prescribed":False,"aligned_selected":False,"alternating_selected":False,"quaternionic_phase_selected":False,"holonomy_phase_selected":False,"stability_matrix":None,"reason":"no nontrivial retained tensor with sourced coefficient and selected resonant channel"}


def coherence_payload() -> dict[str, Any]:
    return {**_common("BHSM_harmonic_basis_invariant_coherence_v6_0_4"),"status":"BASIS_INVARIANT_ARCHITECTURE_PHASE_SELECTION_OPEN","projector":"P_R=sum_a |e_a><e_a| for an orthonormal basis of the geometrically selected resonant subspace","quadratic_functional":"C2=<Psi,P_R Psi>=||P_R Psi||^2","basis_independent":True,"positivity":"C2>=0","phase_sensitivity":"C2 is phase blind; a phase-sensitive invariant requires the action-derived restricted interaction energy S_int[P_R Psi]","stress_cross_term":"not defined until the geometry distinguishes the spectral decomposition","arbitrary_basis_subtraction_used":False}


def variational_payload() -> dict[str, Any]:
    return {**_common("BHSM_harmonic_constrained_variational_selection_v6_0_4"),"status":"CONSTRAINED_SELECTION_PROBLEM_UNEVALUATED","principle":"delta(E-sum_i mu_i Q_i)=0 using only actual conserved Q_i","candidate_constraints":["energy","action-derived gauge/global charge","topological number","approximate wave action only within justified normal form"],"arbitrary_coherence_maximized":False,"first_variation":None,"second_constrained_variation":None,"branch_classification":None}


def stress_payload() -> dict[str, Any]:
    return {**_common("BHSM_harmonic_coherent_incoherent_stress_v6_0_4"),"status":"EQUAL_INVARIANT_COMPARISON_BLOCKED","fixed_quantities_required":["total energy","all exact charges","topological number","mode occupations","boundary data"],"energy_difference":None,"stress_difference":None,"normal_pressure_difference":None,"sigma_eigenvalue_difference":None,"quadratic_free_result":"relative phases give identical quadratic action and invariant averaged stress after eigenmode averaging","nonlinear_result":"requires a geometrically selected decomposition and sourced interaction tensor","constructive_binding_claimed":False}


def sigma_shift_payload() -> dict[str, Any]:
    return {**_common("BHSM_harmonic_sigma_hessian_shift_v6_0_4"),"status":"NEGATIVE_INVARIANT_SHIFT_NOT_DERIVED","independent_field_candidate":"S_int=(gamma/2) integral sigma^2 O_Psi","shift":"Delta H_sigma=gamma O_Psi[Psi_coh]","coefficient_gamma":None,"sign":None,"self_sigma_quartic":{"action":"G sigma^4/4","shift_about_background":"3G sigma_bg^2","shift_at_sigma_zero":0,"stable_G_positive_sign":"nonnegative","circularity":"sigma_bg nonzero is already outside the undifferentiated branch"},"coherent_incoherent_difference":None,"actual_selected_interaction":None}


def threshold_payload() -> dict[str, Any]:
    return {**_common("BHSM_harmonic_physicality_threshold_v6_0_4"),"status":"HARMONIC_PHYSICALITY_THRESHOLD_BLOCKED","operator":"H_sigma,vac^(0)+Delta H_sigma[Psi_coh]","lambda_phys":"lowest non-gauge normalizable eigenvalue in selected self-adjoint domain","control_variable":None,"critical_value":None,"crossing_direction":None,"finite_size":"retains Z q0^2/L^2 plus boundary/collar shifts","squashing_dependence":"spectrum and overlaps depend on unselected ratios","reason":"no stable coherent source or derived negative shift"}


def coupled_payload() -> dict[str, Any]:
    return {**_common("BHSM_harmonic_coupled_coherent_sigma_hessian_v6_0_4"),"status":"COUPLED_FORMED_PHASE_NOT_CONSTRUCTED","reduced_action":"S_red=lambda_sigma(A)q_sigma^2/2+g_sigma q_sigma^4/4+H_res(A)+higher terms","stationarity":["partial_q S_red=0","partial_A S_red=0","metric and interface equations"],"hessian_sectors":["sigma amplitude","resonant amplitudes","resonant phases","overall scale","nested squashing","collar/interface displacement"],"sigma":None,"coherent_amplitudes":None,"geometry":None,"negative_modes":None,"enclosure":None}


def metric_payload() -> dict[str, Any]:
    return {**_common("BHSM_harmonic_geometric_modulus_selection_v6_0_4"),"status":"ROUND_RATIO_DIAGNOSTIC_ONLY_NO_METRIC_SELECTION","L4_over_L2":None,"L2_over_L1":None,"squashing":None,"round_octave_compatibility":"l=4,10 relation is independent of overall L on the round S7 diagnostic","resonance_surface":"conditional equations in dimensionless squashing ratios if exact spectra become available","action_stationarity_satisfied":False,"interaction_nonzero_proved":False,"coherent_stability_proved":False,"overall_scale":None}


def enclosure_payload() -> dict[str, Any]:
    return {**_common("BHSM_harmonic_emergent_enclosure_test_v6_0_4"),"status":"EMERGENT_ENCLOSURE_NOT_DERIVED","finite_container":{"standing_waves":"require a selected bulk radial operator","Robin_phase_shift":"depends on unsourced real Robin endomorphism","collar_phase":"requires physical collar length and propagation operator","critical_radius":None,"mode_spacing":"scales as 1/L only after geometry/domain selection","boundary_detuning":"must enter the resonance equation and is not evaluated"},"requirements":["sigma profile","coherent-field localization","nonzero normal gradient","finite wall tension","stress matching","induced metric","junction conditions","translation and shape stability"],"requirements_closed":False,"round_S7_container":"externally specified spectral diagnostic","container_supported_state_found":False,"container_called_emergent":False}


def v5_payload() -> dict[str, Any]:
    return {**_common("BHSM_harmonic_parent_to_v5_compatibility_v6_0_4"),"status":"STRUCTURAL_COMPATIBILITY_ONLY_SELECTION_INDEPENDENTLY_BLOCKED","admissible_1_2_3":"not identified with resonant channels","sigma_half":"not parent-derived","A_ST":"not parent-derived","G_ST":"not parent-derived","Berger_S3":"existing engine supplies proxy mode labels, not the selected B8/S7 nonlinear field spectrum","mass_ratios_from_octaves":False,"particle_generations_identified":False}


def scale_payload() -> dict[str, Any]:
    return {**_common("BHSM_harmonic_absolute_scale_hidden_input_audit_v6_0_4"),"status":"DIMENSIONLESS_OCTAVE_RATIO_NO_ABSOLUTE_SCALE","ratios_fixed":["omega_10/omega_4=2 on the massless round-S7 scalar diagnostic"],"base_frequency":None,"absolute_radius":None,"primitive_coefficients":["Z_0","A_0","quartic G_0","independent-field gamma","Lovelock coefficients","boundary/collar data"],"hidden_inputs":["selected parent field","signature/time","mode normalization","squashing","interaction coefficient","detuning tolerance","conserved control quantity","container radius"],"one_scale_theorem":False,"unit_status":"BHSM_ABSOLUTE_UNIT_ANCHOR_NOT_GENERATED"}


def report_payload() -> dict[str, Any]:
    return {**_common("BHSM_harmonic_physicality_coupling_selection_report_v6_0_4"),"status":PRIMARY_RESULT,"central_answer":"Linear orthogonal modes have no invariant relative-phase selection energy. The massless round-S7 scalar spectrum contains the exact octave pair l=4,10, but sigma parity kills the required cubic 10-4-4 interaction at sigma=0, and the accepted parent family supplies no selected noncircular field, sourced nonlinear tensor, stable phase-locked solution, or negative invariant sigma-Hessian shift. Harmonic physicality coupling selection is therefore blocked, not derived.","selected_parent_field":None,"selected_coupling":None,"derived":["linear orthogonal phase no-selection theorem","finite-block diagonalization and degenerate-projector invariance","round-S7 scalar spectrum and unique nonzero octave pair l=4,10","sigma cubic tensor vanishes at sigma=0 by parity","sigma self-quartic gives zero shift at sigma=0 and nonnegative shift for G>0 away from zero","dimensionless resonance ratios do not fix overall scale"],"derived_conditionally":["quartic overlap tensor and representation/charge selection rules","resonant normal-form and spectral-projector architectures","independent-field sigma shift gamma O_Psi when an action supplies both"],"invalidated":["linear superposition as binding selection","removable quadratic off-diagonal terms as constructive interference","frequency commensurability as proof of coupling","the round l=4,10 octave as a parity-even sigma three-wave trigger","base-ten magnitude grouping as geometric law","top-form flux as local harmonic wave field","resonant channels as particle generations","ratio selection as absolute-unit generation"],"still_requiring_new_mathematics":list(OPEN_GATES),"completion_gate_status":"V6_0_4_STOP_LINEAR_NO_SELECTION_EXACT_OCTAVE_SOURCE_BLOCKED","recommended_next_branch":"bhsm-parent-matter-conserved-stress-action-v6-0-5"}


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    return {"linear":linear_payload(),"fields":fields_payload(),"spectrum":spectrum_payload(),"tensors":tensors_payload(),"rules":rules_payload(),"octave":octave_payload(),"resonance":resonance_payload(),"normal_form":normal_form_payload(),"locked":locked_payload(),"coherence":coherence_payload(),"variational":variational_payload(),"stress":stress_payload(),"sigma_shift":sigma_shift_payload(),"threshold":threshold_payload(),"coupled":coupled_payload(),"metric":metric_payload(),"enclosure":enclosure_payload(),"v5_map":v5_payload(),"scale":scale_payload(),"report":report_payload()}


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


def harmonic_selection_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    _ = repo_root
    report = report_payload()
    report["artifacts"] = {key: f"artifacts/{name}" for key, name in ARTIFACT_FILES.items()}
    return report


def harmonic_selection_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join(["# BHSM v6.0.4 Harmonic Physicality Coupling Selection","",f"Primary result: `{report['primary_result']}`.",f"Coupling-selection result: `{report['coupling_selection_result']}`.","",report["central_answer"],"",f"Completion gate: `{report['completion_gate_status']}`.","","## Open gates","",*[f"- `{gate}`" for gate in report["still_requiring_new_mathematics"]]]) + "\n"
