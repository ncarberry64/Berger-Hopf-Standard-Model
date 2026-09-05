"""Provenance-only recovery audit for the missing full-field reset selector.

This module does not implement a selector, add an action term, or choose a
reset.  It records historical candidates, translates their actual authority
into the current reset language, and fails closed when no current K4/K5 rule
survives.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


ACTION_VERSION = "BHSM-AE-3.2.9-RESET-SELECTOR-RECOVERY"
RECOVERY_VERDICT = "RECOVERY_EXHAUSTED_OWNER_INPUT_REQUIRED"
STATUS = "CREDIBLE_PARTIAL_AND_SUPERSEDED_RULES_RECOVERED_NO_CURRENT_FULL_FIELD_K4_OR_K5"
EFFECT_ON_E5 = "UNCHANGED_INFINITE_DIMENSIONAL_WITHIN_SECTOR_FREEDOM"
EXACT_NEXT_OBJECT = (
    "OWNER_SUPPLY_THE_GAUGE_COVARIANT_EVENT_ENVIRONMENT_TO_CHILD_BOUNDARY_"
    "CAUCHY_NOETHER_DATA_RULE_OR_EQUIVALENT_FULL_FIELD_BOUNDARY_GENERATING_"
    "RELATION_THAT_SELECTS_ONE_PHYSICAL_RESET_EQUIVALENCE_CLASS"
)
ONE_OWNER_QUESTION = (
    "Given the gauge-quotiented last-regular event trace and environment "
    "(z_event,E_s,B_SM), what boundary Cauchy/Noether datum E_boundary—or "
    "equivalently what full-field boundary generating relation—must the "
    "reconstructed child satisfy?"
)


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    historical_stage: str
    original_terms: tuple[str, ...]
    provenance: tuple[str, ...]
    authority: str
    historical_power: str
    current_e5_power: str
    disposition: str
    current_acceptance: str
    modern_translation: str
    residual: str


def candidate_ledger() -> tuple[Candidate, ...]:
    """Return every serious recovered selection candidate."""

    return (
        Candidate(
            "C01_CORE_TRAJECTORY_TARGET",
            "v11.0; commit 146ef0b41329979f0ce8510c6617b1799e7cf2c7",
            ("pure energy core", "trajectory target selection", "T_core"),
            (
                "src/bhsm/interface/envelopment/canonical_crystallization_v11_0.py",
                "src/bhsm/interface/completion/aether_parent_stratification_v15_0.py",
            ),
            "P0/P1",
            "K0",
            "K0",
            "OWNER_SEMANTICS_ONLY",
            "ACCEPTED_AS_ONTOLOGY_ONLY",
            "T_core would map incoming state, phase, topology and gauge data to an outgoing state, but every transfer block and exit condition is unset.",
            "No equation for energy matching, phase/topology/gauge transport, exit, or target selection.",
        ),
        Candidate(
            "C02_GLOBAL_ENVELOPMENT_STATIONARITY",
            "v14.59-v14.68; integrated at commit 5e6820948d336ff3e7b31ca18b9c98f6c50a9b4d",
            ("global envelopment", "seam becomes an output", "strict convexity"),
            (
                "src/bhsm/interface/completion/exact_berger_dirac_cap_obstruction_v14_59.py",
                "src/bhsm/interface/completion/global_envelopment_cap_selection_v14_60.py",
                "src/bhsm/interface/completion/action_attachment_wentzell_v14_67.py",
                "src/bhsm/interface/completion/global_attachment_incidence_curvature_v14_68.py",
            ),
            "P2",
            "K4_ON_SYNTHETIC_REDUCED_WITNESS_ONLY",
            "K0",
            "PARTIAL_RULE",
            "ARCHITECTURE_ACCEPTED_PHYSICAL_SELECTOR_NOT_ACCEPTED",
            "For fixed complete action data, solve parent, child, seam, traction and nesting simultaneously and quotient symmetries; an isolated stationary solution would determine a reset class.",
            "The strict-convexity coefficients are synthetic; the full gauge-fixed BHSM Hessian, branch exhaustion and physical coefficients were never supplied.",
        ),
        Candidate(
            "C03_BOUNDARY_TRIPLE_CALDERON_WENTZELL",
            "v14.65-v14.68; integrated at commit 5e6820948d336ff3e7b31ca18b9c98f6c50a9b4d",
            ("boundary triple", "Calderon/Weyl", "Wentzell response"),
            (
                "src/bhsm/interface/completion/boundary_triple_heat_semigroup_v14_65.py",
                "src/bhsm/interface/completion/operator_valued_calderon_wentzell_v14_66.py",
                "src/bhsm/interface/completion/action_attachment_wentzell_v14_67.py",
            ),
            "P2/P3_THEOREM_CLASS",
            "K1",
            "K1",
            "LOST_TRANSLATION/PARTIAL_RULE",
            "ACCEPTED_AS_DOMAIN_AND_SOLVABILITY_RESTRICTION",
            "A self-adjoint Calderon/Wentzell boundary relation constrains L_s and the child DtN response after its physical blocks and incidence placement are given.",
            "The theorem class does not select its physical W_phys, ensemble, full-field projector, or base map F_B.",
        ),
        Candidate(
            "C04_UNIQUE_ACTUALIZATION_MASTER_FIXED_POINT",
            "v15.5-v15.8; commits fc6cdffb8d371aef4ea21455a7832524c813d38b through db8626609d1d573b2cbaefcc8abf3d397ea3ee07",
            ("Unique Actualization Principle", "master map", "fixed point"),
            (
                "src/bhsm/interface/aether_master_closure_v15_5.py",
                "src/bhsm/interface/aether_nonlinear_norman_cycle_bvp_v15_7.py",
                "src/bhsm/interface/aether_backward_closure_existing_answer_audit_v15_8.py",
            ),
            "P0",
            "K0",
            "K0",
            "OWNER_SEMANTICS_ONLY",
            "ACCEPTED_AS_COMPLETION_CRITERION",
            "A physical master return map would select a gauge class by a unique fixed point.",
            "The master map, formation arrow, reconstruction arrow, physical orbit and action-selected generator are explicitly absent; reset-semigroup fixed pairs form continuous families.",
        ),
        Candidate(
            "C05_SKIN_CLOCK_AND_RESPONSE_SELECTOR",
            "v15.14-v15.16; commit bdf2ab21ae61d910a73f5cb5e84d755b4717e5a7",
            ("child clock", "skin phase", "coupled skin selector"),
            (
                "src/bhsm/interface/aether_internal_clock_skin_phase_v15_14.py",
                "src/bhsm/interface/aether_material_skin_variation_v15_15.py",
                "src/bhsm/interface/aether_coupled_skin_selector_v15_16.py",
            ),
            "P2_NEGATIVE_RESULT",
            "K0",
            "K0",
            "ABSENT",
            "ACCEPTED_NO_GO",
            "Clock transport evolves data on a selected domain; the coupled normal field equations are a forward problem conditional on coefficients and asymptotics.",
            "The available selector Jacobian has rank zero and nullity three; a clock does not choose its boundary condition.",
        ),
        Candidate(
            "C06_CONSTANT_METRIC_ERASING_ACTUALIZATION",
            "v15.52-v15.57; commit bdf2ab21ae61d910a73f5cb5e84d755b4717e5a7",
            ("Reconstruct(I_star)=z_star", "constant return", "unique hybrid fixed point"),
            (
                "src/bhsm/interface/aether_hybrid_actualization_persistence_v15_52.py",
                "src/bhsm/interface/aether_full_sobolev_hybrid_actualization_v15_57.py",
                "src/bhsm/interface/aether_persistent_nonequilibrium_child_v17_87.py",
            ),
            "P2",
            "K5_HISTORICAL",
            "K0",
            "SUPERSEDED_RULE",
            "REJECTED_AS_EVENT_SPECIFIC_PHYSICAL_SELECTOR",
            "The old map sent every state in one event basin to a fixed z_star, making reset data derived and the derivative zero.",
            "v17.82 and v17.84 reject it as rank-zero on event data; v17.87 replaces exact identical return by finite persistence in B_child.",
        ),
        Candidate(
            "C07_ENVIRONMENT_SUPERSELECTION_CHANNEL",
            "v16.78; commit c10d67e442118ed8a64feaa042886eaa30fffd19",
            ("admissible child sector", "R_rec", "z_return"),
            (
                "src/bhsm/interface/aether_scale_child_ownership_audit_v16_78.py",
                "src/bhsm/interface/environmental_child_compatibility_selection.py",
            ),
            "P1",
            "K1_FROM_A0_TO_E5",
            "K0_WITHIN_E5",
            "PARTIAL_RULE",
            "ACCEPTED",
            "(I_event,I_environment,B_SM) restricts the child sector and types R_rec and z_return as reconstruction outputs.",
            "It forbids incompatible sectors but supplies no event-layer-to-boundary-data map and no within-sector selection.",
        ),
        Candidate(
            "C08_N3_EVENT_CONDITIONED_CAUCHY_NOETHER_BVP",
            "v17.82-v17.99; commit 02ddaa947aaa1f4a3e486ce4b723047203e37eb0",
            ("E_boundary", "Solve_child_BVP", "F_child", "complete retained boundary solvability map"),
            (
                "src/bhsm/interface/aether_n3_whole_child_encapsulation_audit_v17_82.py",
                "src/bhsm/interface/aether_n3_event_complete_child_correspondence_v17_84.py",
                "src/bhsm/interface/aether_n3_terminal_child_boundary_map_v17_85.py",
                "src/bhsm/interface/aether_n3_lorentzian_child_cauchy_correspondence_v17_88.py",
                "src/bhsm/interface/aether_n3_firewall_core_child_ownership_v17_98.py",
            ),
            "P2/P3_CONDITIONAL_LOCAL_N3",
            "K5_FOR_ONE_SUPPLIED_N3_EVENT_TRACE_AND_LOCALLY_WELL_POSED_CHILD_BVP",
            "K1",
            "LOST_TRANSLATION/PARTIAL_RULE",
            "ACCEPTED_AT_N3_FIELD_STATE_LEVEL_ONLY",
            "E_boundary(z_event,E_s,B_SM) supplies child boundary data; the action-owned child BVP and Calderon flux balance determine Phi_child and z_return. For a selected N3 event, inherited q and Pi plus seven independent constraint directions give a locally determinate field-state map.",
            "E_boundary itself is not defined, W_phys is not generally selected, and the field-state relation supplies neither a spatial point map F_B nor a full nonfermion L_s class.",
        ),
        Candidate(
            "C09_N12_SET_VALUED_RESET_AND_FIRST_RETURN",
            "N12 continuum, 2026-08-22 onward; first-return audit commit 80d42df633ff0d7076c0ac575101f710b24d2f22",
            ("set-valued reset relation", "first-positive return", "normal section"),
            (
                "artifacts/intrinsic_state_selection/BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json",
                "scripts/audit_n12_intrinsic_state_return_section.py",
                "theory/n12_finite_encapsulation_local_branch.md",
            ),
            "P3_LOCAL_EXISTENCE_RELATION",
            "K1",
            "K1",
            "PARTIAL_RULE",
            "ACCEPTED_AS_NONEMPTY_RELATION_NOT_SELECTOR",
            "The unchanged action gives a regular local event-to-child relation and a typed first-positive-return relation when a later event exists.",
            "The fixed-event child fiber is 67-dimensional (66 after time quotient); the numerical normal chart is not physical selection, and the return map is not executable or single-valued.",
        ),
    )


def r_rec_lineage() -> dict[str, Any]:
    return {
        "first_exact_symbol_commit": "c10d67e442118ed8a64feaa042886eaa30fffd19",
        "first_exact_symbol_date": "2026-08-13",
        "first_path": "src/bhsm/interface/aether_scale_child_ownership_audit_v16_78.py",
        "original_equation": "C_rec=q_log_scale(return)-log(R_rec[I_event,I_environment]/R_star)=0",
        "original_interpretation": "post-event constraint-solved broken-reconstruction BVP return-scale output",
        "depends_on_event_environment": True,
        "determines_scale": True,
        "determines_geometry": False,
        "determines_boundary_data": False,
        "determines_topology": False,
        "determines_child_state": False,
        "input_or_output": "OUTPUT_AFTER_RECONSTRUCTION",
        "current_status": "UNEVALUATED_UNTIL_E_boundary_AND_THE_FULL_CHILD_BVP_ARE_OWNED",
    }


def z_return_lineage() -> dict[str, Any]:
    return {
        "first_exact_symbol_commit": "02ddaa947aaa1f4a3e486ce4b723047203e37eb0",
        "first_exact_symbol_date": "2026-08-14",
        "first_path": "src/bhsm/interface/aether_n3_whole_child_encapsulation_audit_v17_82.py",
        "original_equation": "z_return=Trace_return[Phi_child]",
        "earlier_typed_channel": "(I_event,I_environment,B_SM)->(admissible_child_sector,R_rec,z_return)",
        "original_interpretation": "trace of the solved broken child reconstruction, not a free reset input",
        "depends_on_event_environment": True,
        "determines_scale": "BY_PROJECTION_AFTER_THE_CHILD_SOLUTION",
        "determines_geometry": "CONTAINS_THE_RECONSTRUCTED_RETURN_STATE_IF_THE_BVP_CLOSES",
        "determines_boundary_data": False,
        "determines_topology": "INHERITS_ALREADY_RESTRICTED_DISCRETE_DATA",
        "determines_child_state": "IS_THE_RETURN_TRACE_OF_THE_CHILD_SOLUTION",
        "input_or_output": "OUTPUT_AFTER_RECONSTRUCTION",
        "current_status": "TYPED_BUT_NO_GENERAL_ENVIRONMENT_CONDITIONED_VALUE",
    }


def spacetime_edge_lineage() -> dict[str, Any]:
    return {
        "conceptual_antecedent": {
            "stage": "v11.0",
            "commit": "146ef0b41329979f0ce8510c6617b1799e7cf2c7",
            "term": "pure energy without ordinary spacetime support is the core",
        },
        "normalized_symbol": {
            "commit": "a506e89b5a423f5f0e17c6a63ae8be2efcec618d",
            "date": "2026-08-27",
            "path": "theory/bhsm_spacetime_edge_ontology_repair.md",
        },
        "meaning": "owner-authorized ontological limit where geometry ceases and pure energy/Aether is operative",
        "preserved": ["abstract invariant signature", "degree", "orientation", "FR parity", "incidence", "bundle isomorphism class"],
        "not_transported_as_pregeometric_primitives": ["metric", "proper time", "curvature", "local energy density", "canonical metric momentum"],
        "open": ["action location", "core adjacency", "energy/phase/topology/gauge transfer", "exit condition", "emergent boundary Cauchy data", "return geometry"],
        "forbidden_identifications": ["firewall=SPACETIME_EDGE", "canonical_stop=SPACETIME_EDGE", "form_core_cutoff=SPACETIME_EDGE"],
        "older_transition_law_found": False,
    }


def n3_n12_comparison() -> dict[str, Any]:
    return {
        "N3": {
            "inputs_that_make_local_field_state_determinate": [
                "one selected terminal N3 event trace Gamma0",
                "GHY/eta canonical and Noether flux Gamma1",
                "same action Legendre map for q and Pi",
                "degree one, negative child orientation, FR=-1, incidence and bundle class",
                "gauge f=chi and anchored reset phase",
                "seven independent local constraint directions",
                "gravity-eta-sigma child BVP and zero-background gauge/spinor/ghost/HS block",
            ],
            "selection_statement": "K5 only conditionally for that supplied N3 event trace and field-state BVP",
            "not_selected": ["general E_boundary", "spatial F_B", "general L_s", "global event member"],
        },
        "N12": {
            "joint_map": "F12:R^196->R^57",
            "fixed_event_child_block": "31x98 rank 31",
            "fixed_event_fiber_dimension": 67,
            "after_time_quotient": 66,
            "normal_chart_role": "reproducible representative, not physical selector",
            "status": "THE_N3_BOUNDARY_SOLVABILITY_ARCHITECTURE_GENERALIZES_AS_A_RELATION_NOT_AS_UNIQUENESS",
            "diagnosis": "LOST_TRANSLATION_PLUS_MATHEMATICAL_NONUNIQUENESS;_NO_N12_K4_OR_K5",
        },
    }


def recovery_payload() -> dict[str, Any]:
    candidates = [asdict(row) for row in candidate_ledger()]
    current_strong = [
        row["candidate_id"]
        for row in candidates
        if row["current_e5_power"] in {"K4", "K5"}
    ]
    return {
        "artifact": "BHSM_ENVIRONMENT_CONDITIONED_RESET_SELECTOR_RECOVERY",
        "action_version": ACTION_VERSION,
        "status": STATUS,
        "target": "E_s_TO_EQUIVALENCE_CLASS_OF_(F_B,L_s)",
        "search_scope": {
            "current": ["src", "theory", "docs", "artifacts", "scripts", "tests", "ledgers/status files"],
            "history": ["all reachable local and remote refs", "file creation commits", "content history for R_rec, z_return, E_boundary and SPACETIME_EDGE"],
            "historical_worktrees": ["BHSM-oriented-event-return", "BHSM-singular-event-reset", "BHSM-cross-resolution", "BHSM-museum-facade", "Berger-Hopf-Standard-Model"],
            "museum": "agent/bhsm-museum-facade plus BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35",
        },
        "historical_terminology": [
            "global envelopment", "seam output", "trajectory target selection",
            "Unique Actualization", "master self-reconstruction map", "hybrid return",
            "constant metric-erasing reset", "skin response jet", "event basin",
            "broken reconstruction BVP", "Calderon range", "DtN flux balance",
            "first-positive return", "normal section", "set-valued reset relation",
        ],
        "spacetime_edge_lineage": spacetime_edge_lineage(),
        "R_rec_lineage": r_rec_lineage(),
        "z_return_lineage": z_return_lineage(),
        "formation_reconstruction_return_lineage": [
            "v14.59 local seam data fail to determine a child interior",
            "v14.60 global variation demonstrates a conditional architecture that co-selects interior, seam and scale",
            "v15.5-v15.8 Unique Actualization is retained as an owner completion criterion while the master/formation maps remain absent",
            "v15.52-v15.57 installs a constant reset to z_star and a unique fixed point",
            "v16.78 types environment-conditioned sector, R_rec and z_return outputs",
            "v17.82-v17.87 supersedes the constant reset and requires event-conditioned Cauchy/Noether boundary reconstruction",
            "v17.98 closes the retained N3 field-state boundary solvability map for one supplied event",
            "N12 proves a nonempty local set-valued event-child relation with a 67-dimensional fixed-event fiber",
        ],
        "candidates": candidates,
        "N3_to_N12": n3_n12_comparison(),
        "current_full_field_K4_or_K5": current_strong,
        "effect_on_E5": EFFECT_ON_E5,
        "selected_equivalence_class": None,
        "selected_reset": None,
        "generator_charge": {
            "unlocked": False,
            "classes": "G4/U",
            "reason": "no unique physical reset tangent domain was selected",
        },
        "ABCD": "D_UNCHANGED",
        "downstream": {"beta": "BLOCKED", "graph_jets": "BLOCKED", "S1_S4": "BLOCKED", "full_field_action_attachment": "BLOCKED"},
        "classification_summary": {
            "LOST_IMPLEMENTATION": [],
            "LOST_TRANSLATION": ["C03_BOUNDARY_TRIPLE_CALDERON_WENTZELL", "C08_N3_EVENT_CONDITIONED_CAUCHY_NOETHER_BVP"],
            "PARTIAL_RULE": ["C02_GLOBAL_ENVELOPMENT_STATIONARITY", "C03_BOUNDARY_TRIPLE_CALDERON_WENTZELL", "C07_ENVIRONMENT_SUPERSELECTION_CHANNEL", "C08_N3_EVENT_CONDITIONED_CAUCHY_NOETHER_BVP", "C09_N12_SET_VALUED_RESET_AND_FIRST_RETURN"],
            "SUPERSEDED_RULE": ["C06_CONSTANT_METRIC_ERASING_ACTUALIZATION"],
            "OWNER_SEMANTICS_ONLY": ["C01_CORE_TRAJECTORY_TARGET", "C04_UNIQUE_ACTUALIZATION_MASTER_FIXED_POINT"],
            "ABSENT": ["C05_SKIN_CLOCK_AND_RESPONSE_SELECTOR", "current full-field environment-conditioned K4/K5 selector"],
        },
        "VALIDATED": [
            "environment/topology compatibility restricts sectors",
            "R_rec and z_return are reconstruction outputs",
            "N3 event traces and Noether flux can condition a locally solved child field state",
            "N12 event-child existence is a set-valued relation",
        ],
        "INVALIDATED": [
            "constant metric-erasing reset as event-specific selector",
            "clock transport as boundary-condition selector",
            "normal numerical chart as physical child selector",
            "N3 local determinacy implies N12 uniqueness",
        ],
        "REDUNDANT": [
            "topology/Hopf/incidence filtering already accounted for by E5",
            "fixed-point language without an independently owned map",
        ],
        "OPEN": [
            "environment-to-boundary Cauchy/Noether data rule",
            "physical Wentzell/attachment block and ensemble",
            "spatial F_B and nonfermion L_s reconstruction",
            "N12 elimination of the 67-dimensional fixed-event fiber",
        ],
        "DECISION_POWER": "NO_RECOVERED_CURRENT_RULE_REDUCES_E5_BELOW_INFINITE_DIMENSIONAL_WITHIN_SECTOR_FREEDOM",
        "RECOVERY_VERDICT": RECOVERY_VERDICT,
        "ONE_SMALLEST_OWNER_QUESTION": ONE_OWNER_QUESTION,
        "EXACT_NEXT_OBJECT": EXACT_NEXT_OBJECT,
        "claim_boundary": {
            "new_action_term_added": False,
            "new_interface_functional_added": False,
            "new_physical_law_added": False,
            "new_coefficient_added": False,
            "reset_selected": False,
            "FULL_BHSM_COMPLETE": False,
            "frozen_predictions_changed": False,
        },
    }


__all__ = [
    "ACTION_VERSION", "EFFECT_ON_E5", "EXACT_NEXT_OBJECT",
    "ONE_OWNER_QUESTION", "RECOVERY_VERDICT", "STATUS", "Candidate",
    "candidate_ledger", "n3_n12_comparison", "r_rec_lineage",
    "recovery_payload", "spacetime_edge_lineage", "z_return_lineage",
]
