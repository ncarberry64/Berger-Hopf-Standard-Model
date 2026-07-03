"""Shared contracts for the BHSM v4.4 Berger Hodge component audit."""

from copy import deepcopy

REQUIRED_STATEMENTS = (
    "An explicit Berger Hodge-star component map is distinct from selecting the gauge-action coframe basis.",
    "The orthonormal coframe e^a absorbs Berger metric scale factors, while raw sigma_a components retain anisotropic Hodge factors.",
    "A component Hodge map does not by itself imply equal gauge-frame coefficients.",
    "Equal coefficients do not by themselves imply average normalization by 1/3.",
    "Gauge trace Hodge expansion does not by itself derive gauge couplings.",
    "The denominator 1/[3 Vol(S^3)] remains open unless frame averaging, unit volume normalization, and gauge-action attachment are all supported.",
    "alpha_i, g2_BH, CKM coefficient value, CKM exponent, and full BHSM completion remain open unless downstream gates close.",
)
GUARD = {
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
ORTHO = "*(e1 wedge e2)=e3; *(e2 wedge e3)=e1; *(e3 wedge e1)=e2"
RAW = "*(sigma1 wedge sigma2)=(r_fiber/r_base^2)sigma3; *(sigma2 wedge sigma3)=(1/r_fiber)sigma1; *(sigma3 wedge sigma1)=(1/r_fiber)sigma2"


def _gate(status, formula, boundary, evidence_for, evidence_against, dependencies, blockers, **extra):
    return {
        "status": status,
        "candidate_formula": formula,
        "orthonormal_map": ORTHO,
        "raw_berger_map": RAW,
        "orthonormal_formula": ORTHO,
        "raw_berger_formula": RAW,
        "orientation_convention": "positive e1 wedge e2 wedge e3; reversing orientation flips all Hodge signs",
        "sign_convention": "epsilon_123=+1 in the selected orientation",
        "scale_factors": {"e1": "r_base sigma1", "e2": "r_base sigma2", "e3": "r_fiber sigma3"},
        "evidence_for": evidence_for,
        "evidence_against": evidence_against,
        "dependencies": dependencies,
        "blocking_conditions": blockers,
        "claim_boundary": boundary,
        **GUARD,
        **extra,
    }


GATES = {
    "hodge_component_map": _gate("CONDITIONAL_BERGER_HODGE_COMPONENT_MAP", RAW, "The map is a conditional geometric consequence of the artifact-backed Berger metric and a chosen orientation; it does not select the gauge basis.", ["Berger metric and raw coframe are artifact-backed", "orthonormal Hodge identities are exact once orientation is chosen"], ["BHSM does not independently fix the gauge orientation or action basis"], ["positive radii", "orientation", "Berger metric"], ["gauge-action basis selection"]),
    "coframe_basis_selection": _gate("OPEN_MISSING_GAUGE_ACTION_COFRAME_SELECTION", "raw sigma_a or orthonormal e^a", "An available orthonormal coframe does not mean the gauge action uses it.", ["both raw and orthonormal component descriptions are available"], ["the gauge skeleton names neither basis"], ["gauge action", "component expansion"], ["explicit action basis declaration"]),
    "gauge_trace_hodge_expansion": _gate("CONDITIONAL_GAUGE_TRACE_HODGE_COMPONENT_EXPANSION", "raw: Tr(F wedge *F)=[(r_fiber/r_base^2)Tr(f12^2)+(1/r_fiber)Tr(f23^2+f31^2)] sigma1 wedge sigma2 wedge sigma3", "The component expansion is conditional on the chosen raw decomposition and orientation and does not attach coupling normalization.", ["explicit conditional Hodge map", "schematic Tr(F wedge *F) is artifact-backed"], ["gauge basis and field-component identification remain unspecified"], ["Hodge map", "gauge component decomposition"], ["action-selected basis", "component identification"]),
    "equal_coefficient_update": _gate("OPEN_MISSING_EQUAL_ORTHONORMAL_GAUGE_FRAME_COEFFICIENTS", "c1=c2=c3 in e^a basis", "The Hodge map does not force equal independent action coefficients.", ["orthonormal expansion has unit geometric Hodge factors"], ["no action symmetry fixes coefficient equality"], ["selected orthonormal gauge basis", "action coefficients"], ["coefficient equality theorem"], raw_frame_weights_status="CONDITIONAL_RAW_BERGER_FRAME_WEIGHTS"),
    "frame_average_update": _gate("OPEN_MISSING_FRAME_AVERAGE_NORMALIZATION", "(1/3) sum_a X_a", "A component sum does not imply division by three.", ["three components exist"], ["no action factor 1/3"], ["equal coefficients", "normalization"], ["action-selected division by three"]),
    "gauge_attachment_update": _gate("OPEN_MISSING_GAUGE_TRACE_FRAME_AVERAGE_ATTACHMENT", "[3 Vol(S^3)]^-1 sum_a int Tr(F_a wedge *F_a)", "The expansion does not attach an average or unit-volume normalization to gauge couplings.", ["conditional component expansion exists"], ["same-term average, volume, and coupling coefficient are absent"], ["frame average", "unit volume", "gauge action"], ["normalized action attachment"]),
    "denominator_update": _gate("OPEN_MISSING_GAUGE_COUPLING_VOLUME_DENOMINATOR", "1/[3 Vol(S^3_unit)]=1/(6*pi^2)", "The denominator remains open without averaging, unit volume, and action attachment.", ["component map is conditionally closed"], ["all denominator normalization gates remain open"], ["frame average", "unit volume", "gauge attachment"], ["complete denominator conjunction"]),
    "downstream_update": _gate("OPEN_DOWNSTREAM_GAUGE_AND_CKM_COUPLING_GATES", "alpha_i=w_i/(6*pi^2); g2_BH and C_CKM conditional only", "No downstream coupling promotes from a component Hodge map.", ["registry forms remain artifact-backed"], ["denominator, weights, k, and attachment remain open"], ["gauge normalization chain"], ["all downstream action gates"], alpha_i_status="OPEN_MISSING_ALPHA_I_ACTION_DERIVATION", g2_status="OPEN_MISSING_G2_BH_ACTION_SOURCE", ckm_value_status="OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE", ckm_exponent_status="not_derived"),
    "full_completion_update": _gate("FULL_BHSM_NOT_COMPLETE", "BHSM_FULL_COMPLETION=conjunction(all gates)", "Conditional Hodge closure does not close gauge normalization or full BHSM.", ["explicit component factors are conditionally derived"], ["action selection and downstream gates remain open"], ["all completion gates"], ["open action, scale, and transport gates"], completion=False),
}


def build_gate(name):
    return deepcopy(GATES[name])
