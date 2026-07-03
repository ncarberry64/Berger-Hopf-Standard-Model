"""Shared contracts for the BHSM v4.3 gauge coframe/Hodge audit."""

from copy import deepcopy

REQUIRED_STATEMENTS = (
    "Equal frame coefficients in an orthonormal coframe are distinct from equal coefficients in the raw Berger coframe.",
    "Hodge-star metric factors may absorb Berger anisotropy, but this does not by itself imply frame averaging by 1/3.",
    "Equal orthonormal coefficients do not imply average normalization.",
    "Average normalization does not imply gauge trace attachment.",
    "Gauge couplings, CKM coefficient value, and full BHSM completion remain open unless downstream gates close.",
)
GUARD = {"empirical_inputs_used": False, "pdg_reference_values_used": False, "w_calibration_used": False, "charged_mass_fitting_used": False, "ckm_fitting_used": False, "neutrino_limits_used": False, "legacy_threshold_tables_used": False, "frozen_predictions_changed": False, "official_prediction_logic_changed": False}

def _gate(status, formula, boundary, evidence_for, evidence_against, dependencies, blockers, **extra):
    return {"status": status, "candidate_formula": formula, "claim_boundary": boundary, "evidence_for": evidence_for, "evidence_against": evidence_against, "dependencies": dependencies, "blocking_conditions": blockers, **GUARD, **extra}

GATES = {
    "gauge_coframe_basis": _gate(
        "OPEN_MISSING_GAUGE_COFRAME_BASIS",
        "raw: sigma_a; orthonormal candidate: e^1=r_base sigma_1, e^2=r_base sigma_2, e^3=r_fiber sigma_3",
        "The repository does not state whether gauge-field components use the raw Berger coframe or its orthonormal rescaling.",
        ["raw left-invariant sigma_a and the Berger metric are explicit"],
        ["the gauge skeleton has no sigma_a or e^a frame index"],
        ["Berger metric", "gauge field-strength decomposition"],
        ["action-selected gauge coframe basis"],
    ),
    "hodge_star_metric_factors": _gate(
        "CONDITIONAL_HODGE_STAR_METRIC_FACTORS",
        "S_gauge contains Tr(F wedge *F); * depends on g_Berger and its volume form",
        "The schematic Hodge star is metric-dependent, but BHSM does not evaluate its Berger base/fiber factors in the gauge action.",
        ["the normalized gauge skeleton explicitly uses F wedge *F", "g_Berger and sqrt(det g_Berger) are localized"],
        ["no explicit Hodge map or component coefficients in r_base,r_fiber are supplied"],
        ["gauge coframe basis", "Berger metric", "orientation", "volume form"],
        ["explicit Berger Hodge-star component map"],
    ),
    "anisotropy_compatibility_update": _gate(
        "CONDITIONAL_BERGER_ANISOTROPY_COMPATIBILITY",
        "equal coefficients may be compatible in e^a if all anisotropic factors are carried by e^a and *",
        "Compatibility remains conditional because the gauge basis and Hodge factors are not fixed.",
        ["orthonormalization is mathematically compatible with the Berger metric"],
        ["the action does not select that basis or prove factor absorption"],
        ["gauge coframe basis", "Hodge metric factors"],
        ["basis selection", "explicit factor cancellation"],
    ),
    "equal_orthonormal_coefficients": _gate(
        "OPEN_MISSING_EQUAL_ORTHONORMAL_GAUGE_FRAME_COEFFICIENTS",
        "c1=c2=c3 in orthonormal e^a components",
        "An orthonormal basis, even if selected, would not by itself force equal action coefficients.",
        ["a conditional orthonormal compatibility route exists"],
        ["no gauge symmetry or action term fixes c1=c2=c3"],
        ["orthonormal gauge basis", "gauge action coefficients"],
        ["action-selected coefficient equality"],
    ),
    "frame_average_update": _gate(
        "OPEN_MISSING_FRAME_AVERAGE_NORMALIZATION",
        "FrameAvg=(1/3) sum_a X_a",
        "Equal orthonormal coefficients would define a sum, not division by three.",
        ["diagnostic 1/3 candidates exist"],
        ["no normalized action selects the factor 1/3"],
        ["equal coefficients", "action normalization"],
        ["action-selected division by three"],
    ),
    "gauge_trace_attachment_update": _gate(
        "OPEN_MISSING_GAUGE_TRACE_FRAME_AVERAGE_ATTACHMENT",
        "[3 Vol(S^3)]^-1 sum_a int Tr(F_a wedge *F_a)",
        "Neither conditional Hodge dependence nor a candidate average attaches the normalization to gauge trace densities.",
        ["gauge trace terms and Hodge notation exist"],
        ["no same-term frame average or unit-volume factor exists"],
        ["frame average", "Hodge map", "unit volume"],
        ["normalized same-term attachment"],
    ),
    "denominator_update": _gate(
        "OPEN_MISSING_GAUGE_COUPLING_VOLUME_DENOMINATOR",
        "1/[3 Vol(S^3_unit)]=1/(6*pi^2)",
        "The denominator remains open without unit volume, action averaging, and gauge attachment.",
        ["conditional measure and Hodge dependence are localized"],
        ["unit S3, 1/3 normalization, and gauge attachment remain open"],
        ["unit volume", "frame average", "gauge trace attachment"],
        ["complete denominator conjunction"],
    ),
    "downstream_update": _gate(
        "OPEN_DOWNSTREAM_GAUGE_AND_CKM_COUPLING_GATES",
        "alpha_i=w_i/(6*pi^2); g2_BH=2/sqrt(3*pi); C_CKM=g2_BH/sqrt(2), all conditional only",
        "No downstream coupling value promotes while the gauge normalization chain remains open.",
        ["registry forms remain artifact-backed"],
        ["denominator, weights, k, and action attachment remain open"],
        ["gauge denominator", "sector weights", "k", "gauge attachment"],
        ["all downstream action gates"],
        alpha_i_status="OPEN_MISSING_ALPHA_I_ACTION_DERIVATION", g2_status="OPEN_MISSING_G2_BH_ACTION_SOURCE", ckm_value_status="OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE", ckm_exponent_status="not_derived",
    ),
    "full_completion_update": _gate(
        "FULL_BHSM_NOT_COMPLETE",
        "BHSM_FULL_COMPLETION=conjunction(all completion gates)",
        "Conditional Hodge dependence does not close gauge normalization or full completion.",
        ["the coframe/Hodge ambiguity is now explicitly localized"],
        ["gauge basis, explicit Hodge factors, frame normalization, couplings, CKM, scale, and transport remain open"],
        ["all completion gates"],
        ["every open action-normalization and scale gate"],
        completion=False,
    ),
}

def build_gate(name): return deepcopy(GATES[name])
