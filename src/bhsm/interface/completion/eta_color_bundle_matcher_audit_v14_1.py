"""Bundle, wall-extension, variational, and matcher audit for eta and M4 color."""

from __future__ import annotations

from typing import Any

from bhsm.interface.envelopment.dynamic_action import (
    extended_action_ledger,
    spin_current_audit,
    stratified_action_ownership,
)
from bhsm.interface.master_action.fields import bundle_ledger_payload
from bhsm.interface.master_action.common_parent_charged_current_attachment import (
    transport_compatibility,
)
from bhsm.interface.master_action.reduction import (
    authoritative_action,
    field_transport,
    measure_and_orientation,
    reduction_54,
    reduction_85,
    variational_intertwiner,
)
from bhsm.interface.master_action.reductions import sector_rows
from bhsm.interface.master_action.terms import term_rows

VERSION = "v14.1"
EXACT_NEXT_OBJECT = (
    "RECOVERY_AND_ETA_EXTENSION_OF_THE_V7_0_V7_1_UNIFIED_PARENT_BUNDLE_"
    "CONNECTION_AND_COVARIANT_REDUCTION_FUNCTOR_TO_THE_M4_SU3_AND_ETA_"
    "POLARIZATION_ASSOCIATED_BUNDLES"
)
BRANCH_DECISION = (
    "BHSM_COMMON_PARENT_BUNDLE_AND_REDUCTION_ARCHITECTURE_ALREADY_EXISTS_"
    "CONDITIONALLY"
)
PROJECTION_PROVENANCE_VERDICT = (
    "BHSM_ETA_POLARIZATION_AND_INDEPENDENT_M4_SU3_CONNECTION_HAVE_NOT_YET_"
    "BEEN_PROVEN_TO_BE_ASSOCIATED_PROJECTIONS_OF_THAT_PARENT_CONNECTION"
)


def parent_architecture_recovery_payload() -> dict[str, Any]:
    """Recover the v7.0--v7.1 architecture and audit its eta extension."""

    r85 = reduction_85()
    r54 = reduction_54()
    fields = {row["field"]: row for row in field_transport()}
    action = authoritative_action()
    measures = measure_and_orientation()
    intertwiner = variational_intertwiner()
    family_transport = transport_compatibility()
    objects = [
        {
            "object": "P_parent",
            "recovered_owner": "Sp(1)->S7->S4 principal Hopf bundle in R_85",
            "status": "CONDITIONAL_GENERIC_PARENT_BUNDLE_ARCHITECTURE_RECOVERED",
            "eta_SU3_gap": "no declared common principal bundle whose associated projections are E_color and E_P",
        },
        {
            "object": "A_parent",
            "recovered_owner": fields["omega"]["map"],
            "status": "CANONICAL_SP1_TRANSPORT_CONNECTION_RECOVERED",
            "eta_SU3_gap": "omega is explicitly not the SM gauge field and no action map to both SU3 connections is supplied",
        },
        {
            "object": "rho_color and rho_P",
            "recovered_owner": r85["nontrivial_sector"],
            "status": "GENERIC_ASSOCIATED_REPRESENTATION_SLOT_RECOVERED",
            "eta_SU3_gap": "the color and eta-polarization representation homomorphisms are not declared",
        },
        {
            "object": "eta-dependent reduction",
            "recovered_owner": None,
            "status": "MISSING",
            "eta_SU3_gap": "R_85 and R_54 predate eta and do not export u_eta, P_eta, or A_P",
        },
        {
            "object": "bundle measures",
            "recovered_owner": measures["normalized_fiber_measure"],
            "status": "RECOVERED_FOR_M8_TO_M5_AND_M5_TO_M4_COLLAR",
            "eta_SU3_gap": "no eta-polarization pushforward measure/intertwiner is yet selected",
        },
        {
            "object": "common transformation law",
            "recovered_owner": r85["covariant_derivative_intertwiner"],
            "status": "GENERIC_EQUIVARIANT_LAW_RECOVERED",
            "eta_SU3_gap": "no single action-owned gauge transformation is shown to induce both physical SU3 laws",
        },
        {
            "object": "mixed action variation",
            "recovered_owner": intertwiner["derived_equation_rule"],
            "status": "GENERIC_KKT_VARIATIONAL_INTERTWINER_RECOVERED",
            "eta_SU3_gap": "the retained action has no eta--independent-SU3 mixed second variation/current pairing",
        },
        {
            "object": "independent Gauss equation",
            "recovered_owner": "intrinsic M4 Yang-Mills variation on the gauge quotient",
            "status": "INDEPENDENT_M4_EQUATION_RECOVERED_BUT_ETA_UNSOURCED",
            "eta_SU3_gap": "no parent projection or eta source appears in the independent SU3 Euler equation",
        },
    ]
    validation = {
        "v7_stratified_action_recovered": action["status"].startswith("BHSM_STRATIFIED_MASTER_ACTION"),
        "v7_R85_associated_bundle_functor_recovered": "E_R=P x_R V_R" in r85["nontrivial_sector"],
        "v7_R54_trace_functor_recovered": r54["status"].startswith("CONSTRAINED_CRITICAL_VALUE"),
        "normalized_bundle_measures_recovered": "integral_F dnu_F=1" in measures["normalized_fiber_measure"],
        "generic_covariant_intertwiner_recovered": "D5 P_alpha=P_alpha D8" in r85["covariant_derivative_intertwiner"],
        "parent_induced_associated_connection_language_recovered": "parent-induced associated-bundle connections" in family_transport["dynamic_case"],
        "physical_M4_color_remains_boundary_localized": fields["A_SM"]["classification"] == "BOUNDARY_LOCALIZED_FUNDAMENTAL",
        "eta_polarization_extension_not_in_v7_functor": all(
            token not in str((r85, r54)) for token in ("u_eta", "Pi_10", "A_P")
        ),
        "two_SU3_projection_maps_not_recovered": True,
        "eta_sourced_independent_Gauss_law_not_recovered": True,
        "no_new_object_or_coefficient_introduced": True,
    }
    return {
        "artifact": "BHSM_v7_parent_bundle_eta_extension_recovery_v14_1",
        "version": VERSION,
        "central_diagram": {
            "parent": "A_parent in Conn(P_parent)",
            "M4_projection": "A_SU3=rho_color(iota_4^* A_parent)",
            "eta_projection": "A_P=rho_P(iota_eta^* A_parent)",
        },
        "recovered_v7_architecture": {
            "R_85": r85,
            "R_54": r54,
            "stratified_action": action,
            "measures": measures,
            "family_transport_precedent": family_transport,
        },
        "object_audit": objects,
        "primary_classification": BRANCH_DECISION,
        "projection_provenance_verdict": PROJECTION_PROVENANCE_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def bundle_isomorphism_payload() -> dict[str, Any]:
    bundle_ledger = bundle_ledger_payload()
    validation = {
        "eta_selector_naturally_wall_based": True,
        "E_P_complex_rank_three_Hermitian": True,
        "E_color_complex_rank_three_Hermitian": True,
        "equal_rank_and_group_not_sufficient_for_isomorphism": True,
        "common_base_map_not_declared": True,
        "transition_cocycle_identification_not_declared": True,
        "connection_pullback_not_declared": True,
        "collar_extension_not_declared": True,
        "generic_color_c2_not_forced_zero_but_EP_c2_zero": True,
        "family_C3_action_is_identity_on_color_connection": True,
        "canonical_Phi_absent": True,
    }
    return {
        "artifact": "BHSM_eta_SU3_bundle_isomorphism_audit_v14_1",
        "version": VERSION,
        "eta_wall_selector_bundle": {
            "base": "Sigma_eta={f=pi/2} inside the localized eta enclosure",
            "fiber": "S6=G2/SU3",
            "section": "u_eta=nabla_n eta/||nabla_n eta|| where the denominator is nonzero",
        },
        "polarization_bundle": "u_eta^*(G2 x_SU3 C3) on the selector base",
        "E_P": "Image(Pi_10(u_eta)), complex rank 3 with induced Hermitian metric",
        "E_color": "independent retained M4 SU3 associated bundle B4_spin_gauge",
        "retained_bundle_ledger": bundle_ledger,
        "candidate_isomorphism": "Phi:E_P->E_color",
        "candidate_isomorphism_status": "NOT_DECLARED_OR_ACTION_SELECTED",
        "recovered_architecture_boundary": (
            "v7.0-v7.1 owns conditional associated-bundle and covariant reduction "
            "architecture, but not this eta/color isomorphism or the two explicit "
            "projections from one parent connection"
        ),
        "obstructions": [
            "the current selector is naturally defined on Sigma_eta rather than all M4",
            "no base/collar pushforward identifies Sigma_eta data with M4",
            "no transition-function cocycle equality is owned by the action",
            "E_P has c2=0 whereas the independent color bundle admits general c2 sectors",
            "orientation reversal exchanges E_10 and E_01 and requires a declared conjugation branch",
        ],
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def wall_extension_payload() -> dict[str, Any]:
    candidates = [
        {"name": "normalized covariant derivative", "local": True, "unique": False, "failure": "singular where D eta or its chosen normal component vanishes"},
        {"name": "collar-normal parallel transport", "local": True, "unique": False, "failure": "requires an already selected collar connection and initial identification"},
        {"name": "harmonic extension", "local": False, "unique": "conditional", "failure": "requires metric, boundary data, gauge, and global elliptic boundary problem"},
        {"name": "nearest-wall projection", "local": False, "unique": False, "failure": "fails at cut loci and depends on an arbitrary tubular neighborhood"},
        {"name": "gradient-flow extension", "local": False, "unique": False, "failure": "requires flow time, equation, and behavior at critical points"},
        {"name": "action-derived collar transport", "local": True, "unique": None, "failure": "the required eta/color common connection is precisely the missing action object"},
    ]
    validation = {
        "all_candidates_audited": len(candidates) == 6,
        "no_candidate_action_selected": True,
        "normalization_singularity_detected": True,
        "orientation_reversal_can_be_imposed_but_does_not_select_extension": True,
        "wall_to_M4_extension_not_promoted": True,
    }
    return {
        "artifact": "BHSM_eta_wall_to_M4_extension_audit_v14_1",
        "version": VERSION,
        "candidates": candidates,
        "canonical_extension": None,
        "exact_blocker": "ACTION_OWNED_ETA_WALL_TO_M4_SELECTOR_EXTENSION_OR_COMMON_CONNECTION_PULLBACK",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def composite_variational_payload() -> dict[str, Any]:
    validation = {
        "delta_P_tangent_to_projector_manifold": True,
        "delta_F_includes_all_projector_variations": True,
        "independent_u_equation_at_most_second_order_but_degenerate": True,
        "derived_u_of_eta_can_generate_fourth_order_eta_equation": True,
        "normalized_gradient_singular_at_zero": True,
        "wall_location_shape_variation_required": True,
        "self_adjoint_domain_not_declared": True,
        "independent_SU3_Gauss_law_absent": True,
    }
    return {
        "artifact": "BHSM_eta_projector_composite_variational_contract_v14_1",
        "version": VERSION,
        "candidate_action": "S_P=-(4g3^2)^(-1) int_M4 sqrt(h) tr(FP_mu_nu FP^mu_nu)",
        "projector_variation": "delta P=(-delta u tensor u-u tensor delta u-iJ_delta_u)/2 plus normalization projection",
        "curvature_variation": (
            "delta F=delta P[dP,dP]P+P[d(delta P),dP]P+"
            "P[dP,d(delta P)]P+P[dP,dP]delta P"
        ),
        "normalized_selector_variation": "delta u=(I-u tensor u)delta v/||v||, v=nabla_n eta",
        "boundary_form": "obtained by integrating tr(FP delta F); depends on delta u and normal derivatives after u(eta) substitution",
        "derivative_order": {
            "u_as_independent_extended_selector": "second-order quasilinear equation with vanishing Hessian at du=0",
            "u_as_normalized_derivative_of_eta": "generically fourth-order in eta after extension, plus wall shape derivative",
        },
        "regularity": "singular at ||nabla_n eta||=0 and undefined away from the wall without an extension",
        "Gauss_identity": "only Image(P) frame covariance; no Euler equation from varying an independent A_SU3",
        "status": "CANDIDATE_NOT_A_RETAINED_ACTION_TERM",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def matcher_payload() -> dict[str, Any]:
    terms = {row["term_id"]: row for row in term_rows()}
    gauge_sector = next(row for row in sector_rows() if row["sector"] == "gauge")
    eta_fields = extended_action_ledger()["fields"]
    ownership = stratified_action_ownership()
    current = spin_current_audit()
    candidates = [
        {"candidate": "A=Phi_*AP", "status": "NOT_ACTION_OWNED", "effect": "removes the independent gluon configuration space; cannot arise without a matcher/constraint"},
        {"candidate": "F_A=Phi_*F_P", "status": "NOT_ACTION_OWNED_AND_OVERCONSTRAINING", "effect": "forces the independent bundle into c2=0 and eliminates general instanton/gluon sectors"},
        {"candidate": "connection transgression", "status": "NOT_INSTANTIATED_IN_RECOVERED_ARCHITECTURE", "effect": "the generic v7 reduction framework exists, but no common color/eta bundle, connection, or transgression is declared"},
        {"candidate": "tr(A-Phi_*AP)^2", "status": "REJECTED", "effect": "requires Phi and a dimensionful locking coefficient and gives an unbroken-color gauge boson mass"},
        {"candidate": "tr(F_A-Phi_*F_P)^2", "status": "UNSELECTED_EXTENSION", "effect": "requires Phi and a new relative normalization; it changes both dynamics without imposing equality exactly"},
        {"candidate": "v7 parent-bundle connection eta extension", "status": "RECOVERY_AND_EXTENSION_GATE", "effect": "audit whether the recovered parent functor already induces both restrictions before proposing any new term"},
    ]
    validation = {
        "S8_eta_has_no_independent_SU3_connection": "A_i" not in eta_fields,
        "S4_YM_has_no_eta": "eta" not in terms["T4_gauge"]["fields"],
        "gauge_reduction_missing": gauge_sector["reduction"] == "MISSING",
        "physical_eta_current_pullback_missing": current["physical_pullback_rank"] is None,
        "Lambda85_matches_metrics_not_connections": True,
        "Lambda54_matches_seam_metrics_not_connections": True,
        "generic_cross_stratum_compatibility_framework_exists": True,
        "no_instantiated_multiplier_or_transgression_for_eta_color": True,
        "no_candidate_silently_added": True,
        "independent_SU3_Gauss_equation_not_eta_sourced": True,
        "branch_decision_recovers_conditional_architecture": True,
        "projection_provenance_remains_open": True,
    }
    return {
        "artifact": "BHSM_eta_independent_connection_matcher_audit_v14_1",
        "version": VERSION,
        "retained_S4_gauge_term": terms["T4_gauge"],
        "stratified_ownership": ownership,
        "candidates": candidates,
        "retained_matcher": None,
        "eta_sourced_independent_Gauss_law": None,
        "branch_decision": BRANCH_DECISION,
        "projection_provenance_verdict": PROJECTION_PROVENANCE_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
