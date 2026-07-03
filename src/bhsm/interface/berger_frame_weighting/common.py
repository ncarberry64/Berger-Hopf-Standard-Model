"""Shared contracts for the BHSM v4.2 Berger frame-weighting audit."""

from copy import deepcopy


REQUIRED_STATEMENTS = (
    "Three artifact-backed Berger frame directions do not by themselves imply equal weighting.",
    "Equal weighting does not by itself imply average normalization by 1/3.",
    "Average normalization does not by itself attach to gauge trace densities.",
    "Berger anisotropy must be checked before equal frame averaging can be promoted.",
    "The denominator 1/[3 Vol(S³)] remains open unless equal frame averaging, unit-volume normalization, and gauge-trace attachment are supported.",
    "The gauge coupling quantum remains open unless the denominator is action-attached.",
    "α_i, g2_BH, CKM coefficient value, and CKM exponent remain open unless downstream action gates close.",
    "Full BHSM remains not complete.",
)

REJECTED_CLAIMS = (
    "REJECTED_THREE_FRAME_COUNT_AS_EQUAL_WEIGHTING",
    "REJECTED_EQUAL_WEIGHTING_AS_AVERAGE_NORMALIZATION",
    "REJECTED_AVERAGE_WITHOUT_GAUGE_TRACE_ATTACHMENT",
    "REJECTED_BERGER_FRAME_AVERAGE_IF_ANISOTROPIC_ACTION_WEIGHTS_FOUND",
    "REJECTED_DENOMINATOR_WITHOUT_UNIT_VOLUME_AND_GAUGE_ATTACHMENT",
    "REJECTED_DOWNSTREAM_COUPLING_PROMOTION_FROM_DENOMINATOR_ONLY",
)

INPUT_GUARD = {
    "empirical_inputs_used": False,
    "pdg_reference_values_used": False,
    "w_calibration_used": False,
    "charged_mass_fitting_used": False,
    "ckm_fitting_used": False,
    "neutrino_limits_used": False,
    "legacy_threshold_tables_used": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
}


def _gate(status, claim_boundary, candidate_formula, evidence_for, evidence_against,
          dependencies, blocking_conditions, promoted_from=None, **extra):
    return {
        "status": status,
        "claim_boundary": claim_boundary,
        "candidate_formula": candidate_formula,
        "evidence_for": evidence_for,
        "evidence_against": evidence_against,
        "dependencies": dependencies,
        "blocking_conditions": blocking_conditions,
        "promoted_from": promoted_from,
        "not_promoted_because": blocking_conditions,
        **INPUT_GUARD,
        **extra,
    }


GATES = {
    "equal_frame_weighting": _gate(
        "OPEN_MISSING_EQUAL_FRAME_WEIGHTING",
        "Three coframe directions do not imply c1=c2=c3, especially when the Berger metric distinguishes base and fiber lengths.",
        "c1=c2=c3",
        ["sigma_1 and sigma_2 share the horizontal Berger coefficient", "three coframe directions are artifact-backed"],
        ["sigma_3 carries a distinct fiber coefficient", "no gauge action or symmetry fixes all three coefficients equally"],
        ["Berger coframe", "gauge action basis", "frame symmetry"],
        ["action-selected equal coefficients", "resolved anisotropy basis"],
        "ARTIFACT_BACKED_THREE_BOUNDARY_FRAME_DIRECTIONS",
    ),
    "frame_average_normalization": _gate(
        "OPEN_MISSING_FRAME_AVERAGE_NORMALIZATION",
        "Equal coefficients would still define a sum unless the action supplies the separate factor 1/3.",
        "FrameAvg_B[X]=(1/3) sum_a X_a",
        ["diagnostic triplet coframe-average candidates use 1/3"],
        ["the candidates are explicitly diagnostic and no normalized action selects division by three"],
        ["equal frame weights", "normalization convention", "normalized action"],
        ["action-selected factor 1/3"],
        "OPEN_MISSING_BOUNDARY_FRAME_AVERAGING",
    ),
    "berger_anisotropy_compatibility": _gate(
        "CONDITIONAL_BERGER_ANISOTROPY_COMPATIBILITY",
        "Equal gauge-frame coefficients are compatible with Berger anisotropy only if field strengths are expressed in an orthonormal coframe and metric factors are handled separately.",
        "e^1=r_base sigma_1, e^2=r_base sigma_2, e^3=r_fiber sigma_3; candidate c1=c2=c3 in e^a basis",
        ["the Berger metric explicitly separates base and fiber scales", "orthonormalization provides a mathematically coherent compatibility route"],
        ["the normalized BHSM gauge action does not identify its frame basis or prove cancellation of anisotropic metric factors"],
        ["r_base", "r_fiber", "orthonormal gauge coframe", "Hodge star", "action measure"],
        ["action-level basis selection", "anisotropic factor accounting"],
        "ARTIFACT_BACKED_THREE_BOUNDARY_FRAME_DIRECTIONS",
    ),
    "gauge_trace_frame_average_attachment": _gate(
        "OPEN_MISSING_GAUGE_TRACE_FRAME_AVERAGE_ATTACHMENT",
        "No located normalized action applies an equal 1/3 frame average to Tr(F_a^2).",
        "S_gauge proportional to [3 Vol(S^3)]^-1 sum_a int Tr(F_a^2) dmu_B",
        ["relative gauge kinetic and trace skeletons exist"],
        ["the skeleton separates gauge sectors, not Berger frame components, and supplies no factor 1/3"],
        ["equal weighting", "frame-average normalization", "gauge trace", "normalized measure"],
        ["same-term gauge frame-average attachment"],
        "OPEN_MISSING_GAUGE_TRACE_FRAME_AVERAGE_ATTACHMENT",
    ),
    "denominator_update": _gate(
        "OPEN_MISSING_GAUGE_COUPLING_VOLUME_DENOMINATOR",
        "The denominator remains open because equal weighting, average normalization, unit-S3 normalization, and gauge attachment do not all pass.",
        "1/[3 Vol(S^3_unit)]=1/(6*pi^2)",
        ["conditional collar measure and three coframe directions are available"],
        ["equal weighting and averaging are open", "unit volume and gauge trace attachment are open"],
        ["boundary measure", "three frames", "equal weights", "1/3 normalization", "unit S3 volume", "gauge attachment"],
        ["complete denominator dependency conjunction"],
        "OPEN_MISSING_GAUGE_COUPLING_VOLUME_DENOMINATOR",
    ),
    "universal_quantum_update": _gate(
        "OPEN_MISSING_UNIVERSAL_GAUGE_COUPLING_QUANTUM",
        "The registry candidate is not an action-attached universal gauge quantum.",
        "lambda_gauge=1/(6*pi^2)",
        ["the exact registry pattern remains artifact-backed"],
        ["denominator and action attachment remain open"],
        ["denominator update", "gauge action attachment"],
        ["action-attached denominator"],
        "OPEN_MISSING_UNIVERSAL_GAUGE_COUPLING_QUANTUM",
    ),
    "gauge_action_attachment_update": _gate(
        "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
        "The gauge skeleton does not attach frame averaging, unit volume, sector weights, and k in one normalized term.",
        "S_gauge=k sum_i w_i lambda_gauge Tr(F_i^2)",
        ["relative gauge kinetic and trace normalization exist"],
        ["frame attachment, unit normalization, sector-weight attachment, and k remain open"],
        ["gauge trace frame average", "unit volume", "sector weights", "coefficient k"],
        ["normalized gauge coupling action term"],
        "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
    ),
    "alpha_i_update": _gate(
        "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
        "alpha_i remain registered values because their action dependencies remain open.",
        "alpha_i=w_i/(6*pi^2), w=(1,2,7)",
        ["the 1:2:7 registry pattern is artifact-backed"],
        ["quantum, weights, k, and action attachment do not all pass"],
        ["universal quantum", "sector weights", "coefficient k", "gauge attachment"],
        ["all alpha_i action gates"],
        "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
        candidate_values={"alpha1": "1/(6*pi^2)", "alpha2": "2/(6*pi^2)", "alpha3": "7/(6*pi^2)"},
    ),
    "g2_update": _gate(
        "OPEN_MISSING_G2_BH_ACTION_SOURCE",
        "g2_BH remains open because alpha2 is not action-derived.",
        "g2_BH=2/sqrt(3*pi), conditional only",
        ["the weak convention is conditional"],
        ["alpha2 action derivation remains open"],
        ["alpha_i update", "weak convention"],
        ["action-derived alpha2"],
        "OPEN_MISSING_G2_BH_ACTION_SOURCE",
    ),
    "ckm_value_update": _gate(
        "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
        "The CKM coefficient form does not provide a value while g2_BH remains open.",
        "C_CKM=g2_BH/sqrt(2)=sqrt(2/(3*pi)), conditional only",
        ["the CKM coefficient form is artifact-backed"],
        ["g2_BH is not action-derived"],
        ["g2 action source", "normalized CKM action"],
        ["action-derived g2_BH"],
        "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
        ckm_exponent_status="not_derived",
    ),
    "full_completion_update": _gate(
        "FULL_BHSM_NOT_COMPLETE",
        "A conditional anisotropy compatibility route does not close frame weighting, gauge normalization, or full completion.",
        "BHSM_FULL_COMPLETION=conjunction(all completion gates)",
        ["Berger anisotropy and the orthonormal-frame compatibility route are explicitly audited"],
        ["equal weighting, averaging, gauge attachment, couplings, CKM, scale, and transport gates remain open"],
        ["all completion gates"],
        ["every unresolved action-normalization and scale gate"],
        "FULL_BHSM_NOT_COMPLETE",
        completion=False,
    ),
}


def build_gate(name):
    return deepcopy(GATES[name])
