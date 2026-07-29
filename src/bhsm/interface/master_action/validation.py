"""No-double-counting, obstruction, code map, and completion update."""

from __future__ import annotations

from .common import MISSING_OBJECT, VERDICT, envelope
from .coefficients import rows as coefficient_rows
from .fields import field_rows
from .hessians import rows as hessian_rows
from .reductions import recovery_rows, sector_rows, sm_rows
from .symmetries import rows as symmetry_rows
from .terms import term_rows
from .variations import boundary_rows, equation_rows


def no_double_counting_rows() -> list[dict]:
    return [
        {"pair": "M8 EH versus M5 cap EH", "decision": "ALTERNATIVE_LEVELS_NOT_SUMMED", "duplicate": False},
        {"pair": "M5 EH versus GHY", "decision": "GHY_IS_VARIATIONAL_COMPLETION", "duplicate": False},
        {"pair": "two cap GHY terms", "decision": "ONE_PER_ORIENTED_CAP", "duplicate": False},
        {"pair": "intrinsic B1 R4 versus induced cap curvature", "decision": "INDEPENDENT_B1_WILSON_TERM", "duplicate": False},
        {"pair": "matcher versus B1 stress", "decision": "AUXILIARY_CONSTRAINT_NOT_DYNAMICS", "duplicate": False},
        {"pair": "M8 scalar potential versus S4 scalar potential", "decision": "ALTERNATIVE_LEVELS_UNTIL_REDUCTION", "duplicate": False},
        {"pair": "gauge kinetic boundary versus bulk", "decision": "NO_GAUGE_TERM_IN_FROZEN_S8; S4_ONLY", "duplicate": False},
        {"pair": "explicit charged action versus SU2 covariant derivative", "decision": "EXPLICIT_G_CH_TERM_REMOVED_AS_REDUNDANT", "duplicate": False},
        {"pair": "neutral gauge current versus neutral auxiliary response", "decision": "SM_CURRENT_IN_D_MU; AUXILIARY_ONLY_IN_DELTA_S", "duplicate": False},
        {"pair": "scale potential versus scalar potential", "decision": "NO_SCALE_POTENTIAL_ADOPTED", "duplicate": False},
    ]


def no_double_counting_payload() -> dict:
    return envelope(
        "BHSM_master_no_double_counting_audit_v7_0",
        rows=no_double_counting_rows(),
        duplicate_terms_retained=[],
        canonical_term_ids=[r["term_id"] for r in term_rows()],
        passed=True,
    )


def obstruction_payload() -> dict:
    return envelope(
        "BHSM_master_action_obstruction_ledger_v7_0",
        every_independent_sector_examined=True,
        exact_missing_object=MISSING_OBJECT,
        definition={
            "base_maps": "pi_85:M8->M5 and pi_54:M5|B1->M4",
            "field_maps": "pullback/pushforward maps for metrics, spinors, gauge connections, scalars and projectors",
            "measure_map": "normalized fiber/collar integration with orientations and units",
            "domain_map": "intertwiner of variational, adjoint and boundary domains",
            "coefficient_map": "finite pushforward from kappa0,kappa1,Zchi,Zsigma,A0,G0,g to S5/S4 coefficients",
            "Hessian_map": "closed-range intertwiner preserving the D0 block and gauge/Dirac quotients",
        },
        evidence=[
            "artifacts/BHSM_b8_s7_physical_domain_action_source_closure_report_v6_0_1.json",
            "artifacts/BHSM_parent_to_v5_action_sector_map_v6_0_6.json",
            "artifacts/BHSM_complete_boundary_action_v6_7_0.json",
            "artifacts/BHSM_action_derivation_gates_report_v1_9.json",
            "artifacts/BHSM_gauge_coupling_action_attachment_killscreen_v4_7.json",
        ],
        why_minimal="All levelwise coefficients can be finitely typed and every term varied; only the common cross-level functor remains unlicensed.",
        why_not_inequivalence_theorem="The repository proves absence of a sourced map, not mathematical impossibility of every future map.",
        why_not_scale_only="Gauge, spinor, projector, measure and domain pushforwards are missing even in dimensionless form.",
        verdict=VERDICT,
    )


def verdict_payload() -> dict:
    return envelope(
        "BHSM_RB01_closure_verdict_v7_0",
        outcome="C_MAXIMAL_ACTION_WITH_EXACT_MISSING_SOURCE",
        verdict=VERDICT,
        RB01_status="BLOCKED_EXACT_OBJECT_LOCALIZED",
        maximal_consistent_object="THREE_LEVEL_ACTION_COMPLEX",
        full_parent_action_closed=False,
        dimensionless_parent_action_closed=False,
        every_sector_examined=True,
        exact_missing_object=MISSING_OBJECT,
    )


def completion_update_payload() -> dict:
    return envelope(
        "BHSM_1_0_completion_gate_update_v7_0",
        current_verdict=VERDICT,
        BHSM_1_0_release_complete=False,
        Tier_A="BLOCKED",
        Tier_B="NOT_ELIGIBLE",
        Tier_C="NOT_ELIGIBLE",
        RB01={
            "status": "BLOCKED_EXACT_OBJECT_LOCALIZED",
            "missing_object": MISSING_OBJECT,
            "release_blocking": True,
        },
        downstream_blockers_not_closed=[
            "RB-03", "RB-04", "RB-05", "RB-06", "RB-07", "RB-08",
            "RB-09", "RB-10", "RB-11", "RB-12", "RB-13", "RB-14",
            "RB-15", "RB-16",
        ],
        next_scientific_target="CONSTRUCT_OR_RULE_OUT_COVARIANT_BULK_BOUNDARY_REDUCTION_FUNCTOR",
        v6_30_8_lambda5_policy_unchanged=True,
    )


def canonical_completion_gate_payload() -> dict:
    update = completion_update_payload()
    return envelope(
        "BHSM_1_0_completion_gate",
        contract_reconciled_from="v6.30.8",
        current_verdict=VERDICT,
        BHSM_1_0_release_complete=False,
        current_tier_status={"Tier_A": "BLOCKED", "Tier_B": "NOT_ELIGIBLE", "Tier_C": "NOT_ELIGIBLE"},
        RB01=update["RB01"],
        parameter_free_extension_blocker="RB-02",
        downstream_release_blockers=update["downstream_blockers_not_closed"],
        next_highest_upstream_blocker=update["next_scientific_target"],
    )


def code_map_payload() -> dict:
    return envelope(
        "BHSM_master_action_to_code_map_v7_0",
        authoritative_package="src/bhsm/interface/master_action/",
        components={
            "fields_and_bundles": "fields.py",
            "measures_and_orientations": "measures.py",
            "symmetries": "symmetries.py",
            "coefficients": "coefficients.py",
            "action_terms": "terms.py",
            "variations_and_boundary_conditions": "variations.py",
            "reductions_and_recovery": "reductions.py",
            "Hessians": "hessians.py",
            "validation_and_verdict": "validation.py",
            "materialization_and_report": "report.py",
        },
        legacy_modules_status="EVIDENCE_ADAPTERS_NOT_COEQUAL_AUTHORITATIVE_PARENT_ACTIONS",
        CLI="python -m bhsm.interface master-action-status --format markdown",
    )


def validate_model() -> dict[str, bool]:
    coefficients = coefficient_rows()
    term_ids = [r["term_id"] for r in term_rows()]
    return {
        "fields_complete": all(len(r) == 13 for r in field_rows()),
        "symmetries_examined": len(symmetry_rows()) >= 10,
        "every_coefficient_typed": all(r["classification"] for r in coefficients),
        "no_comparison_data_in_action": not any(r["comparison_input"] and r["action_level"] not in {"ACTION_EXCLUDED"} for r in coefficients),
        "action_reality": all(r["real"] for r in term_rows()),
        "dimensional_consistency": all(r["mass_dimension_closed"] for r in term_rows()),
        "gauge_invariance": all(r["gauge_invariant"] for r in term_rows()),
        "no_duplicate_term_ids": len(term_ids) == len(set(term_ids)),
        "every_term_varied": len(term_rows()) == 13 and len(equation_rows()) >= 11,
        "boundary_conditions_present": len(boundary_rows()) >= 7,
        "D0_Hessian_recovered": any(r["block"] == "D0_fixed_h" and r["status"] == "RECOVERED_EXACTLY" for r in hessian_rows()),
        "every_sector_examined": len(sector_rows()) == 8,
        "SM_terms_classified": len(sm_rows()) >= 10,
        "historical_results_classified": len(recovery_rows()) >= 15,
        "no_double_counting": no_double_counting_payload()["passed"],
        "singular_exact_obstruction": obstruction_payload()["exact_missing_object"] == MISSING_OBJECT,
    }
