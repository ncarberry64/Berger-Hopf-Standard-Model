"""Shared contracts for the BHSM v4.1 boundary/collar measure audit."""

from __future__ import annotations

from copy import deepcopy


REQUIRED_STATEMENTS = (
    "The mathematical identity Vol(S³_unit)=2π² is not by itself a gauge-coupling derivation.",
    "The candidate denominator 6π² = 3 Vol(S³_unit) is not action-derived unless BHSM supplies an action-selected three-frame boundary average.",
    "A three-frame decomposition does not by itself imply a frame average.",
    "A frame average does not derive gauge couplings unless attached to gauge trace densities in the normalized action.",
    "The gauge coupling quantum λ_gauge = 1/(6π²) remains open unless the denominator is action-attached.",
    "The α_i values remain open unless the gauge quantum, sector weights, and action coefficient are attached by the normalized action.",
    "g2_BH remains open unless α2_BH is action-derived and the weak convention applies.",
    "The CKM coefficient value remains open unless g2_BH is action-derived.",
    "The CKM exponent remains not derived.",
    "Full BHSM remains not complete unless all action-normalization and scale gates close.",
)

REJECTED_CLAIMS = (
    "REJECTED_S3_VOLUME_IDENTITY_AS_COUPLING_DERIVATION",
    "REJECTED_THREE_FRAME_COUNT_AS_FRAME_AVERAGE",
    "REJECTED_FRAME_AVERAGE_WITHOUT_ACTION_ATTACHMENT",
    "REJECTED_DENOMINATOR_WITHOUT_GAUGE_ATTACHMENT",
    "REJECTED_REGISTRY_PATTERN_AS_ACTION_DERIVATION",
    "REJECTED_COUPLING_QUANTUM_AS_ALPHA_DERIVATION_WITHOUT_WEIGHTS",
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


def _gate(status: str, claim_boundary: str, candidate_formula: str, evidence_for: list[str],
          evidence_against: list[str], dependencies: list[str], blocking_conditions: list[str],
          promoted_from: str | None = None, not_promoted_because: list[str] | None = None,
          **extra: object) -> dict[str, object]:
    return {
        "status": status,
        "claim_boundary": claim_boundary,
        "candidate_formula": candidate_formula,
        "evidence_for": evidence_for,
        "evidence_against": evidence_against,
        "dependencies": dependencies,
        "blocking_conditions": blocking_conditions,
        "promoted_from": promoted_from,
        "not_promoted_because": not_promoted_because or blocking_conditions,
        **INPUT_GUARD,
        **extra,
    }


GATES: dict[str, dict[str, object]] = {
    "boundary_collar_measure_source": _gate(
        "CONDITIONAL_BOUNDARY_COLLAR_MEASURE_SOURCE",
        "Standard smooth-collar geometry supplies the symbolic measure formula, but BHSM-specific metric, shape, and orientation data remain open.",
        "dV_collar = J(Y,rho) dA d rho; J=det(I +/- rho S)=sqrt(det h(Y,rho)/det h(Y,0))",
        ["the collar Jacobian identity is DERIVED_CONDITIONAL", "induced-metric and first-order curvature forms are localized"],
        ["the complete BHSM collar action, evaluated h_AB, S(Y), and orientation are not derived"],
        ["smooth boundary embedding", "induced metric", "shape operator", "normal orientation"],
        ["BHSM-specific boundary geometry", "complete normalized collar action"],
        promoted_from="CONDITIONAL_BOUNDARY_MEASURE_SOURCE",
    ),
    "unit_s3_volume_normalization": _gate(
        "OPEN_MISSING_UNIT_S3_VOLUME_NORMALIZATION",
        "Vol(S^3_unit)=2*pi^2 is a mathematical identity, not evidence that BHSM selects the unit-S^3 measure.",
        "Vol(S^3_unit)=2*pi^2",
        ["the unit three-sphere volume identity is mathematically available"],
        ["Berger measure artifacts explicitly avoid assuming unit S^3 or normalized Maurer-Cartan volume coefficients"],
        ["boundary topology", "radius convention", "Maurer-Cartan normalization", "action measure"],
        ["action-selected unit-S^3 normalization"],
    ),
    "three_boundary_frame_directions": _gate(
        "ARTIFACT_BACKED_THREE_BOUNDARY_FRAME_DIRECTIONS",
        "The Berger metric records three coframe directions; this does not select an equal frame average.",
        "g_Berger = r_base^2(sigma_1^2+sigma_2^2)+r_fiber^2 sigma_3^2",
        ["the repository explicitly records sigma_1, sigma_2, and sigma_3 in the Berger metric"],
        ["base/fiber anisotropy means equal averaging is not implied"],
        ["Berger/Hopf coframe"],
        ["action-selected averaging rule"],
        promoted_from="Berger metric and measure artifacts",
    ),
    "boundary_frame_averaging": _gate(
        "OPEN_MISSING_BOUNDARY_FRAME_AVERAGING",
        "A three-frame decomposition does not imply an average; the action must choose averaging rather than summing or anisotropic weighting.",
        "FrameAvg_B[X]=(1/3) sum_{a=1}^3 X_a",
        ["diagnostic coframe-average candidates exist", "three coframe directions are artifact-backed"],
        ["diagnostic candidates are not adopted", "no action term selects the factor 1/3"],
        ["three frame directions", "normalized action", "frame weights"],
        ["action-selected factor 1/3", "equal frame weighting theorem"],
        promoted_from="OPEN_MISSING_BOUNDARY_FRAME_AVERAGING",
    ),
    "gauge_trace_frame_average_attachment": _gate(
        "OPEN_MISSING_GAUGE_TRACE_FRAME_AVERAGE_ATTACHMENT",
        "Even a geometric frame average would not normalize gauge couplings unless the gauge action applies it to trace densities.",
        "S_gauge proportional to [3 Vol(S^3)]^-1 sum_a int Tr(F_a^2) dmu_B",
        ["a conditional gauge action skeleton and trace normalization exist"],
        ["no normalized action attaches the boundary/frame average to Tr(F_a^2)"],
        ["frame average", "gauge trace", "normalized gauge action"],
        ["same-term gauge trace-density attachment"],
    ),
    "gauge_denominator_source": _gate(
        "OPEN_MISSING_GAUGE_COUPLING_VOLUME_DENOMINATOR",
        "The denominator cannot promote while unit-S^3 normalization, frame averaging, and gauge attachment are open.",
        "1/[3 Vol(S^3_unit)] = 1/(6*pi^2)",
        ["the registry uses 6*pi^2", "the conditional collar measure and three coframe directions are localized"],
        ["unit S^3, action-selected averaging, and gauge trace attachment do not pass"],
        ["boundary measure", "unit S3 volume", "three frames", "frame average", "gauge attachment"],
        ["all denominator theorem dependencies"],
        promoted_from="OPEN_MISSING_GAUGE_COUPLING_VOLUME_DENOMINATOR",
    ),
    "universal_gauge_quantum_update": _gate(
        "OPEN_MISSING_UNIVERSAL_GAUGE_COUPLING_QUANTUM",
        "The candidate gauge quantum remains a registry pattern until its denominator is action-attached.",
        "lambda_gauge=1/(6*pi^2)",
        ["the exact registry pattern is artifact-backed"],
        ["the gauge denominator and action attachment remain open"],
        ["gauge denominator source", "gauge action attachment"],
        ["action-attached denominator"],
        promoted_from="OPEN_MISSING_UNIVERSAL_GAUGE_COUPLING_QUANTUM",
    ),
    "gauge_action_attachment_update": _gate(
        "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
        "Neither the registry nor the geometric candidates attach lambda_gauge as a normalized action coefficient.",
        "S_gauge = k sum_i w_i lambda_gauge Tr(F_i^2)",
        ["the gauge skeleton, candidate weights, and registry quantum are inventoried"],
        ["frame/trace attachment and overall coefficient k remain open"],
        ["gauge trace average", "sector weights", "coefficient k"],
        ["normalized gauge action attachment"],
        promoted_from="OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
    ),
    "alpha_i_update": _gate(
        "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
        "alpha_i cannot promote without the action-attached quantum, sector weights, and coefficient normalization.",
        "alpha_i=w_i/(6*pi^2), w=(1,2,7)",
        ["the alpha_i registry pattern is artifact-backed"],
        ["quantum, weights, k, and action attachment do not all pass"],
        ["universal gauge quantum", "sector weights", "coefficient k", "gauge action attachment"],
        ["all alpha_i action gates"],
        promoted_from="OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
        candidate_values={"alpha1": "1/(6*pi^2)", "alpha2": "2/(6*pi^2)", "alpha3": "7/(6*pi^2)"},
    ),
    "g2_update": _gate(
        "OPEN_MISSING_G2_BH_ACTION_SOURCE",
        "g2_BH remains open because alpha2 is not action-derived.",
        "g2_BH=2/sqrt(3*pi), conditional only",
        ["the weak convention g2_BH^2/(4*pi)=alpha2 is conditional"],
        ["alpha2 action derivation is open"],
        ["alpha_i action derivation", "weak convention"],
        ["action-derived alpha2"],
        promoted_from="OPEN_MISSING_G2_BH_ACTION_SOURCE",
    ),
    "ckm_value_update": _gate(
        "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
        "The artifact-backed CKM coefficient form does not provide a value while g2_BH remains open.",
        "C_CKM=g2_BH/sqrt(2)=sqrt(2/(3*pi)), conditional only",
        ["C_CKM=g2_BH/sqrt(2) is artifact-backed"],
        ["g2_BH is not action-derived"],
        ["g2 action source", "normalized CKM action"],
        ["action-derived g2_BH"],
        promoted_from="OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
        ckm_exponent_status="not_derived",
    ),
    "full_completion_update": _gate(
        "FULL_BHSM_NOT_COMPLETE",
        "Conditional measure localization and three coframe directions do not close the full action-normalization conjunction.",
        "BHSM_FULL_COMPLETION = conjunction(all completion gates)",
        ["the collar measure formula and three coframe directions are now explicitly classified"],
        ["unit S3 normalization, frame averaging, gauge attachment, k, downstream coupling, scale, and transport gates remain open"],
        ["all completion gates"],
        ["every unresolved action-normalization and scale gate"],
        promoted_from="FULL_BHSM_NOT_COMPLETE",
        completion=False,
    ),
}


def build_gate(name: str) -> dict[str, object]:
    return deepcopy(GATES[name])
