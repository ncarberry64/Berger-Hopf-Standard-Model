"""BHSM v6.0.5 immutable minimal-parent-theory kill test."""

from __future__ import annotations

import hashlib
import json
from math import sqrt
from pathlib import Path
from typing import Any


VERSION = "v6.0.5"
SPRINT = "bhsm-minimal-parent-theory-freeze-kill-test-v6-0-5"
PRIMARY_RESULT = "BHSM_MINIMAL_PARENT_THEORY_FAILS_PHYSICALITY_TRIGGER"
COHERENT_TRIGGER_RESULT = "BHSM_MINIMAL_FREE_SCALAR_COHERENT_TRIGGER_FAILED"
HARMONIC_ENVELOPMENT_RESULT = "BHSM_HARMONIC_ENVELOPMENT_SELECTION_NOT_DERIVED"
GENERAL_ENVELOPMENT_RESULT = "BHSM_GENERAL_ENERGY_GEOMETRY_ENVELOPMENT_REMAINS_OPEN"

FREEZE_SPEC = {
    "parent_domain": "M8=R_t x S7_L with round closed spatial S7",
    "signature": "Lorentzian (-,+,+,+,+,+,+,+)",
    "parent_family": "P1 volume plus Einstein-Hilbert",
    "energy_carrier": "one real massless scalar chi",
    "sigma_domain": "real Z2-even bulk scalar on M8",
    "action": "integral sqrt(-G)[kappa1 R/2-kappa0/2-Zchi(1+g sigma^2)(nabla chi)^2/2-Zsigma(nabla sigma)^2/2-A0 sigma^2/2-G0 sigma^4/4], with coefficient-locked P1 GHY completion if temporal regulation introduces endpoints",
    "sigma_coupling": "only -Zchi g sigma^2 (nabla chi)^2/2",
    "boundary_conditions": "smooth normalizable fields on closed S7; compactly supported temporal variations, or fixed endpoint metric with coefficient-locked P1 GHY completion; no collar or spatial boundary term",
    "raw_primitives": ["kappa0", "kappa1", "Zchi", "Zsigma", "A0", "G0", "g"],
    "terms_may_be_added_after_freeze": False,
    "alternative_fields_may_be_searched": False,
}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


FREEZE_ID = hashlib.sha256(deterministic_json(FREEZE_SPEC).encode("utf-8")).hexdigest()

ARTIFACT_FILES = {
    "freeze": "BHSM_minimal_parent_theory_freeze_v6_0_5.json",
    "action": "BHSM_minimal_parent_action_equations_stress_v6_0_5.json",
    "spectrum": "BHSM_minimal_parent_linear_spectrum_v6_0_5.json",
    "interaction": "BHSM_minimal_parent_nonlinear_resonance_kill_v6_0_5.json",
    "shift": "BHSM_minimal_parent_coherent_sigma_shift_kill_v6_0_5.json",
    "branch": "BHSM_minimal_parent_nonlinear_sigma_branch_v6_0_5.json",
    "hessian": "BHSM_minimal_parent_coupled_hessian_kill_v6_0_5.json",
    "v5_map": "BHSM_minimal_parent_to_v5_kill_v6_0_5.json",
    "primitives": "BHSM_minimal_parent_primitive_count_v6_0_5.json",
    "report": "BHSM_minimal_parent_theory_kill_test_report_v6_0_5.json",
}

GUARDS = {
    "freeze_id": FREEZE_ID,
    "post_freeze_terms_added": False,
    "alternative_parent_fields_searched": False,
    "empirical_inputs_used": False,
    "A_ST_minus_2_imported": False,
    "G_ST_8_imported": False,
    "sigma_half_target_fitted": False,
    "absolute_unit_generated": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "existing_numerical_predictions_changed": False,
    "full_bhsm_completion_claimed": False,
}


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "coherent_trigger_result": COHERENT_TRIGGER_RESULT,
        "harmonic_envelopment_result": HARMONIC_ENVELOPMENT_RESULT,
        "general_envelopment_result": GENERAL_ENVELOPMENT_RESULT,
        "physicality_doctrine": "physicality is an action-supported localized or propagating energy-geometry differential or envelope at any scale",
        "harmonic_role": "constructive interference is one possible envelope-forming or envelope-reinforcing mechanism, not a universal definition or necessary trigger",
        "sigma_role": "sigma is a candidate persistent-envelopment response or order parameter, not a necessary condition for every physical differential",
        "objecthood_boundary": "persistent physical objecthood additionally requires localization, conservation, self-support, and stability",
        "claim_boundary": "v6.0.5 tests only an autonomous, harmonically selected, stable sigma!=0 transition in one immutable provisional P1+free-chi+sigma theory. Its failure does not falsify transient localized energy differentials or general energy-geometry envelopment.",
        **GUARDS,
    }


def s7_eigenvalue(level: int, radius: float) -> float:
    if level < 0 or radius <= 0:
        raise ValueError("level must be nonnegative and radius positive")
    return level * (level + 6) / radius**2


def effective_sigma_quadratic(A0: float, Zchi: float, g: float, chi_kinetic_invariant: float) -> float:
    return A0 + Zchi * g * chi_kinetic_invariant


def sigma_branches(Aeff: float, G0: float) -> dict[str, Any]:
    if G0 <= 0:
        raise ValueError("bounded quartic truncation requires G0>0")
    values = [] if Aeff >= 0 else [-sqrt(-Aeff / G0), sqrt(-Aeff / G0)]
    return {"zero_stability":"stable" if Aeff>0 else "marginal" if Aeff==0 else "unstable","nonzero":values,"formed_hessian":None if not values else -2*Aeff}


def normalized_primitive_combinations() -> tuple[str, ...]:
    return ("kappa0", "kappa1", "A0/Zsigma", "G0/Zsigma^2", "g/Zsigma")


def freeze_payload() -> dict[str, Any]:
    return {**_common("BHSM_minimal_parent_theory_freeze_v6_0_5"),"status":"IMMUTABLE_PROVISIONAL_THEORY_FROZEN","freeze":FREEZE_SPEC,"raw_primitive_count":7,"field_normalized_invariant_count":5,"selection_rationale":"smallest P1 theory with a stress-carrying parent scalar and the single v6.0.3 kinetic sigma coupling; selected provisionally, not derived","derived_by_geometry":False}


def action_payload() -> dict[str, Any]:
    return {**_common("BHSM_minimal_parent_action_equations_stress_v6_0_5"),"status":"PROVISIONAL_ACTION_WELL_DEFINED_NOT_GEOMETRICALLY_DERIVED","chi_equation":"nabla_A[(1+g sigma^2)nabla^A chi]=0","sigma_equation":"Zsigma Box sigma-A0 sigma-G0 sigma^3-Zchi g sigma (nabla chi)^2=0","metric_equation":"kappa1 Einstein_AB+(kappa0/2)G_AB=T_AB^chi+T_AB^sigma","chi_stress_at_sigma_zero":"T_AB^chi=Zchi[partial_A chi partial_B chi-(1/2)G_AB(nabla chi)^2]","stress_conservation":"nabla^A T_AB^total=0 on the coupled equations; chi stress is separately conserved at sigma=0","geometric_reduction_source":"none; the canonical chi action is the explicit provisional axiom","boundary_variation":"closed spatial S7; compact temporal variations, or the coefficient-locked P1 GHY completion for regulated endpoints","boundary_completion_new_primitive":False,"kill_tests":{"field_exists_at_sigma_zero":"PASS","action_follows_from_geometric_reduction":"FAIL","conserved_stress_well_defined":"PASS_WITHIN_STIPULATED_ACTION"}}


def spectrum_payload() -> dict[str, Any]:
    return {**_common("BHSM_minimal_parent_linear_spectrum_v6_0_5"),"status":"FREE_CHI_SPECTRUM_EXACT_ON_FROZEN_BACKGROUND","decomposition":"chi(t,y)=sum_lI q_lI(t)Y_lI(y)","spatial_operator":"-Delta_S7","eigenvalue":"l(l+6)/L^2","frequency":"omega_l^2=l(l+6)/L^2","inner_product":"integral_S7 dmu conjugate(Y_lI)Y_l'J=delta_ll'delta_IJ","boundary_conditions":"smooth on closed S7","field_at_sigma_zero":True,"quadratic_phase_selection":False,"octave_pair":"l=4,10 remains commensurate but has no chi self-interaction"}


def interaction_payload() -> dict[str, Any]:
    return {**_common("BHSM_minimal_parent_nonlinear_resonance_kill_v6_0_5"),"status":"PARENT_COHERENCE_INTERACTION_ABSENT","chi_action_at_sigma_zero":"purely quadratic","third_chi_derivative":0,"fourth_chi_derivative":0,"mixed_tensor":"delta^4 S/(delta sigma delta sigma delta chi delta chi) is proportional to Zchi g derivative-mode overlap","mixed_tensor_role":"shifts sigma on a prescribed chi background but does not phase-lock the free chi modes","representation_allowed_commensurability":"round l=10 to l=4+l=4 frequency relation exists","nonzero_resonant_parent_channel":False,"kill_tests":{"action_derived_nonlinear_parent_interaction":"FAIL","nonzero_representation_allowed_resonant_channel":"FAIL"}}


def shift_payload() -> dict[str, Any]:
    return {**_common("BHSM_minimal_parent_coherent_sigma_shift_kill_v6_0_5"),"status":"NEGATIVE_COHERENCE_SHIFT_NOT_DERIVED","sigma_shift":"Delta H_sigma=Zchi g (nabla chi)^2","lorentzian_sign":"(nabla chi)^2=-dot(chi)^2+|grad chi|^2 is indefinite","coupling_sign":"g is an unsourced primitive","equal_energy_global_average":"orthogonal free modes remove cross terms in the integrated quadratic invariant; phases are not dynamically selected","local_interference":"can be phase dependent and time dependent, but is initial data rather than a stable coherent solution","delta_lambda_coherent_minus_incoherent":None,"kill_test":"FAIL"}


def branch_payload() -> dict[str, Any]:
    return {**_common("BHSM_minimal_parent_nonlinear_sigma_branch_v6_0_5"),"status":"NONZERO_SIGMA_BRANCH_ONLY_CONDITIONAL_NOT_TRIGGERED","Aeff":"A0+Zchi g (nabla chi)^2","condition":"Aeff<0 and G0>0","sigma_vac":"+/-sqrt(-Aeff/G0)","sigma_hessian":"-2 Aeff","obstruction":"Aeff is Lorentzian-sign-indefinite and no stable coherent chi background or coefficient signs are selected","stable_nonlinear_branch_derived":False,"kill_test":"CONDITIONAL_FORMULA_TRIGGER_FAILS"}


def hessian_payload() -> dict[str, Any]:
    return {**_common("BHSM_minimal_parent_coupled_hessian_kill_v6_0_5"),"status":"ACCEPTABLE_COUPLED_PHYSICAL_SPECTRUM_NOT_ESTABLISHED","background":"round R_t x S7 with sigma=0 and arbitrary free chi solution","blocks":["metric-metric P1 gauge-fixed block unavailable","chi-chi free hyperbolic block","sigma-sigma shifted block","chi-sigma mixed block vanishes at sigma=0","metric-matter mixing background dependent"],"gauge_quotient":"missing","constraint_reduction":"missing","negative_modes":None,"Floquet_problem":"required for time-dependent chi interference","acceptable_physical_spectrum":False,"kill_test":"FAIL"}


def v5_payload() -> dict[str, Any]:
    return {**_common("BHSM_minimal_parent_to_v5_kill_v6_0_5"),"status":"V5_SCALAR_TOPOGRAPHIC_STRUCTURE_NOT_RECOVERED","required_map":["B8 mode normalization and pushforward","Aeff projection to A_ST","quartic overlap to G_ST","local-to-reduced amplitude map"],"A_ST_minus_2":None,"G_ST_8":None,"sigma_half":None,"reverse_engineering_used":False,"kill_test":"FAIL"}


def primitives_payload() -> dict[str, Any]:
    rows = [
        {"name":"kappa0","dimension":"[A]L^-8","role":"volume density"},{"name":"kappa1","dimension":"[A]L^-6","role":"Einstein-Hilbert coefficient"},{"name":"Zchi","dimension":"[A]L^-6","role":"dimensionless-chi kinetic normalization"},{"name":"Zsigma","dimension":"[A]L^-6","role":"dimensionless-sigma kinetic normalization"},{"name":"A0","dimension":"[A]L^-8","role":"sigma quadratic density"},{"name":"G0","dimension":"[A]L^-8","role":"sigma quartic density for dimensionless sigma"},{"name":"g","dimension":"dimensionless","role":"kinetic sigma coupling inside 1+g sigma^2"},
    ]
    return {**_common("BHSM_minimal_parent_primitive_count_v6_0_5"),"status":"SEVEN_RAW_FIVE_FIELD_NORMALIZED_PRIMITIVES_ALL_UNSOURCED","rows":rows,"raw":{"dimensional":6,"dimensionless":1,"total":7},"field_normalized_combinations":list(normalized_primitive_combinations()),"field_normalized_count":5,"internally_sourced_count":0,"absolute_scale":None,"kill_test":"PASS_COUNT_EXPLICIT"}


def report_payload() -> dict[str, Any]:
    tests = [
        {"id":1,"question":"parent field exists at sigma=0","result":"PASS"},
        {"id":2,"question":"action follows from chosen geometric reduction","result":"FAIL"},
        {"id":3,"question":"conserved stress tensor well defined","result":"PASS_WITHIN_STIPULATED_ACTION"},
        {"id":4,"question":"action-derived nonlinear parent interaction","result":"FAIL"},
        {"id":5,"question":"nonzero representation-allowed resonant channel","result":"FAIL"},
        {"id":6,"question":"negative coherent sigma-Hessian shift at equal energy","result":"FAIL"},
        {"id":7,"question":"stable nonlinear nonzero sigma branch","result":"CONDITIONAL_FORMULA_ONLY_TRIGGER_FAILS"},
        {"id":8,"question":"acceptable coupled physical Hessian spectrum","result":"FAIL"},
        {"id":9,"question":"v5 structure recovered without reverse engineering","result":"FAIL"},
        {"id":10,"question":"primitive count explicit","result":"PASS_7_RAW_5_NORMALIZED_ALL_UNSOURCED"},
    ]
    return {
        **_common("BHSM_minimal_parent_theory_kill_test_report_v6_0_5"),
        "status": PRIMARY_RESULT,
        "frozen_theory": FREEZE_SPEC,
        "kill_tests": tests,
        "first_decisive_trigger_failure": "the chi sector is free at sigma=0, so it has no action-derived nonlinear phase-locking interaction",
        "central_answer": "The immutable provisional P1+free-chi+sigma theory fails to generate an autonomous, harmonically selected, stable sigma!=0 transition. Its scalar nevertheless exists at sigma=0, has conserved stress within the stipulated action, and can carry transient localized energy differentials. The action is not derived by the current geometric reduction, the free carrier cannot select coherence, no invariant negative sigma shift follows, and the coupled stable phase and v5 reduction do not close. General energy-geometry envelopment remains open.",
        "failure_scope": "frozen free-scalar coherent sigma-transition trigger only",
        "not_falsified": [
            "compression or converging-flow envelopment",
            "explosion-like or outgoing propagation",
            "curvature confinement",
            "topological stabilization",
            "transient free-scalar localized energy differentials",
            "general energy-geometry envelopment",
        ],
        "foundational_axiom_that_must_change": "The axiom that current P1 geometric reduction plus a free canonical energy carrier and one quadratic kinetic sigma coupling is sufficient for an autonomous harmonically selected stable sigma transition must be abandoned. Progress on that trigger requires an independently justified parent matter/action axiom or a derivation of nonlinear matter dynamics from geometry; adding such structure is outside this frozen sprint.",
        "alternative_candidate_proposed": False,
        "completion_gate_status": "V6_0_5_STOP_FROZEN_MINIMAL_PARENT_FAILS_TRIGGER",
        "recommended_next_branch": None,
    }


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _=repo_root
    return {"freeze":freeze_payload(),"action":action_payload(),"spectrum":spectrum_payload(),"interaction":interaction_payload(),"shift":shift_payload(),"branch":branch_payload(),"hessian":hessian_payload(),"v5_map":v5_payload(),"primitives":primitives_payload(),"report":report_payload()}


def materialize_artifacts(root: Path) -> list[Path]:
    target=root/"artifacts"; target.mkdir(parents=True,exist_ok=True); payloads=build_artifact_payloads(root); written=[]
    for key,name in ARTIFACT_FILES.items():
        path=target/name; path.write_text(deterministic_json(payloads[key]),encoding="utf-8"); written.append(path)
    return written


def minimal_parent_kill_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    _=repo_root; report=report_payload(); report["artifacts"]={key:f"artifacts/{name}" for key,name in ARTIFACT_FILES.items()}; return report


def minimal_parent_kill_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join(["# BHSM v6.0.5 Minimal Parent Theory Freeze and Kill Test","",f"Primary result: `{report['primary_result']}`.","",report["central_answer"],"",f"Freeze ID: `{report['freeze_id']}`.",f"Completion gate: `{report['completion_gate_status']}`."])+"\n"
