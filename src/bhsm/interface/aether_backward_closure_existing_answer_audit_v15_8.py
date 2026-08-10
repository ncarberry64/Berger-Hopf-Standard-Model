"""BHSM v15.8 backward-closure audit of existing formation ingredients.

The audit composes the strongest compatible results already present in the
repository before permitting another theory object.  It distinguishes
theorem-class machinery from physical attachment, a stability criterion from
an actual unstable configuration, and a nonlinear normal form from an exact
encapsulated solution.  It also preserves the v14.54 conditional cycle-energy
readout without attempting to rederive mass-energy equivalence.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


VERSION = "v15.8"
FULL_BHSM_COMPLETE = False
REPOSITORY_EXISTING_ANSWER_EXHAUSTED = True
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_LOCALIZED_CONSTRAINT_SOLVED_UNSTABLE_PARENT_CONFIGURATION_"
    "WITH_PHYSICAL_ATTACHMENT_OF_THE_EXISTING_GAUGE_REDUCTION_AND_SELF_"
    "ADJOINT_DOMAIN_MACHINERY"
)
PRIMARY_VERDICT = (
    "BHSM_V15_8_BACKWARD_CLOSURE_FINDS_THAT_THE_REPOSITORY_ALREADY_OWNS_"
    "CONDITIONAL_STABILITY_HESSIAN_GAUGE_REDUCTION_SELF_ADJOINT_DOMAIN_"
    "NONLINEAR_NORMAL_FORM_PERSISTENCE_AND_CYCLE_MASS_READOUT_MACHINERY;_"
    "IT_DOES_NOT_OWN_A_LOCALIZED_CONSTRAINT_SOLVED_PHYSICAL_CONFIGURATION_"
    "WITH_A_NEGATIVE_MODE_ON_THE_ATTACHED_DOMAIN_OR_AN_EXACT_CONTINUATION_"
    "TO_ANY_ENCAPSULATED_BRANCH;_CAVITATION_IS_ONE_CANDIDATE_FORMATION_"
    "MECHANISM_NOT_THE_UNIVERSAL_LAW_AND_FULL_BHSM_COMPLETION_REMAINS_FALSE"
)

CLASSIFICATIONS = (
    "CURRENT_DERIVED",
    "CURRENT_DERIVED_CONDITIONAL",
    "CURRENT_CANDIDATE",
    "HISTORICAL_VALID_BUT_SUPERSEDED",
    "HISTORICAL_REUSABLE_COMPONENT",
    "INVALIDATED_BY_LATER_RESULT",
    "PROVENANCE_BLOCKED",
    "NOT_COMPATIBLE_WITH_CURRENT_ACTION",
)


def _row(
    requirement: str,
    sources: list[str],
    classification: str,
    status: str,
    missing_only: str,
) -> dict[str, Any]:
    if classification not in CLASSIFICATIONS:
        raise ValueError(f"unknown classification: {classification}")
    return {
        "requirement": requirement,
        "existing_BHSM_sources": sources,
        "classification": classification,
        "status": status,
        "missing_only": missing_only,
    }


def reverse_dependency_rows() -> list[dict[str, Any]]:
    """Map every atomic v15.7 formation requirement to existing results."""

    return [
        _row(
            "A_unique_parent_surface",
            ["v15.7 author steering ontology"],
            "CURRENT_CANDIDATE",
            "AUTHOR_ONTOLOGY_NOT_ACTION_DERIVED",
            "no parent-surface selection problem is introduced",
        ),
        _row(
            "B_local_physical_configuration",
            ["v14.91 exact homogeneous degree-one M8 branch", "v14.94 Lorentzian controls"],
            "PROVENANCE_BLOCKED",
            "NO_LOCALIZED_CONSTRAINT_SOLVED_CONFIGURATION",
            "localized nonhomogeneous action solution",
        ),
        _row(
            "C_local_physical_tangent_space",
            ["v6.0.3 sigma operator architecture", "v14.61 physical-projector interface"],
            "CURRENT_DERIVED_CONDITIONAL",
            "THEOREM_CLASS_EXISTS_NOT_ATTACHED_LOCALLY",
            "localized tangent-space attachment to an actual solution",
        ),
        _row(
            "D_constraints_solved",
            ["v14.91 M8 identity branch", "v14.94 round and Jensen controls"],
            "CURRENT_DERIVED_CONDITIONAL",
            "SOLVED_ONLY_ON_HOMOGENEOUS_CONTROL_BRANCHES",
            "nonhomogeneous localized constraint solve",
        ),
        _row(
            "E_gauge_quotient",
            ["v14.61 Q-kernel projector", "v14.94 homogeneous lapse-volume reduction"],
            "CURRENT_DERIVED_CONDITIONAL",
            "PROJECTOR_ARCHITECTURE_EXISTS",
            "complete coupled localized physical projector",
        ),
        _row(
            "F_self_adjoint_domain",
            [
                "v14.65 boundary triple",
                "v14.66 Calderon-Wentzell theorem class",
                "v14.91 smooth M8 transmission domain",
                "v15.1 abstract correspondence domain",
            ],
            "CURRENT_DERIVED_CONDITIONAL",
            "DOMAIN_THEOREM_CLASSES_EXIST",
            "physical attachment to the localized coupled operator",
        ),
        _row(
            "G_stability_Hessian_operator",
            [
                "v6.0.3 H_sigma architecture",
                "v14.61 gauge-reduced Hessian interface",
                "v14.70-v14.77 shape/Landau derivatives",
                "v14.94 homogeneous Lorentzian operator",
            ],
            "CURRENT_DERIVED_CONDITIONAL",
            "CRITERION_AND_SECTOR_OPERATORS_EXIST",
            "one complete localized physical operator on the attached domain",
        ),
        _row(
            "H_actual_physical_instability",
            ["v14.94 global homogeneous Jensen tachyon"],
            "PROVENANCE_BLOCKED",
            "GLOBAL_TACHYON_EXISTS_LOCAL_INSTABILITY_DOES_NOT",
            "localized constraint-reduced negative mode",
        ),
        _row(
            "I_nonlinear_continuation",
            [
                "v6.0.3 conditional one-mode Landau branch",
                "v6.30.5 reduced quartic family",
                "v14.74 structural ell2 locking phase",
            ],
            "PROVENANCE_BLOCKED",
            "NORMAL_FORMS_EXIST_NO_EXACT_PHYSICAL_CONTINUATION",
            "same-action exact continuation from a physical unstable state",
        ),
        _row(
            "J_enclosure_or_encapsulation_solution",
            ["v14.60-v14.61 synthetic global fixtures", "v14.93 radial no-branch control"],
            "PROVENANCE_BLOCKED",
            "NO_ACTION_OWNED_NONLINEAR_ENCLOSURE_ENDPOINT",
            "finite exact stationary or relative-periodic enclosure solution",
        ),
        _row(
            "K_persistence",
            ["v14.54 relative-periodic contract", "v15.6 Norman cycle typing"],
            "CURRENT_DERIVED_CONDITIONAL",
            "THEOREM_CLASS_ONLY_NO_ACTION_SELECTED_ORBIT",
            "physical relative-periodic orbit and stability",
        ),
        _row(
            "L_invariant_cycle_energy",
            ["v14.54 complete composite-minus-parent Hamiltonian/Floquet contract"],
            "CURRENT_DERIVED_CONDITIONAL",
            "ALREADY_OWNED_ON_A_STABLE_PHYSICAL_CYCLE",
            "a physical cycle on which to evaluate the charge",
        ),
        _row(
            "M_mass_energy_readout",
            ["v14.54 rest-frame cycle-energy identification"],
            "CURRENT_DERIVED_CONDITIONAL",
            "E_REL_EQUALS_MC2_ALREADY_PRESENT_NO_REDERIVATION",
            "formation and persistence, not mass-energy equivalence",
        ),
    ]


def historical_result_rows() -> list[dict[str, Any]]:
    """Classify the most tempting pre-existing answers at current provenance."""

    return [
        {
            "source": "v6.0.3 conditional nonlinear sigma mode",
            "classification": "HISTORICAL_REUSABLE_COMPONENT",
            "survives": "q^2=-lambda_phys/g_eff when lambda_phys<0 and g_eff>0",
            "failure": "the action did not select the source, coefficients, signature, or stable phase",
        },
        {
            "source": "v6.1.6 scalar-wall bifurcation",
            "classification": "HISTORICAL_REUSABLE_COMPONENT",
            "survives": "critical odd mode and Puiseux-sheet diagnostic",
            "failure": "analytic branch fails the exact junction constraint and no coupled branch was found",
        },
        {
            "source": "v6.30.5 fixed-h Lyapunov-Schmidt potential",
            "classification": "HISTORICAL_REUSABLE_COMPONENT",
            "survives": "complement family and first quartic reduced interaction",
            "failure": "stable-wall exact on-shell branch is blocked at third order; G5 remains unselected",
        },
        {
            "source": "v14.55 pair capture",
            "classification": "CURRENT_CANDIDATE",
            "survives": "typed conservation and identity contract",
            "failure": "no action-derived capture amplitude or transition solution",
        },
        {
            "source": "v14.60-v14.61 global envelopment",
            "classification": "CURRENT_DERIVED_CONDITIONAL",
            "survives": "global-variation architecture and solver/Hessian interfaces",
            "failure": "stationary fixtures and coefficients are synthetic, not a physical BHSM enclosure",
        },
        {
            "source": "v14.65-v14.66 self-adjoint domains",
            "classification": "CURRENT_DERIVED_CONDITIONAL",
            "survives": "exact boundary-triple and Calderon-Wentzell theorem classes",
            "failure": "physical action-normalized blocks and local coupled attachment are absent",
        },
        {
            "source": "v14.74-v14.77 Landau lineage",
            "classification": "CURRENT_DERIVED_CONDITIONAL",
            "survives": "locking cone, exact area coefficients, sign firewalls, and conditional DtN D4",
            "failure": "physical r,u,v on one stationary full-preimage action background are absent",
        },
        {
            "source": "v14.93-v14.94 controls",
            "classification": "CURRENT_DERIVED",
            "survives": "radial zero without nearby branch and global Jensen tachyon without local event",
            "failure": "neither result supplies a localized instability-to-enclosure trajectory",
        },
        {
            "source": "2026-08-03 explicit charged-lepton mass packet / v11.4 module",
            "classification": "PROVENANCE_BLOCKED",
            "survives": "gauge-invariant M4 Yukawa algebra and dimensionless spectral hierarchy candidate",
            "failure": "author-selected action, alpha-anchored anisotropy, and external Planck calibration prevent zero-input action derivation",
        },
    ]


def mass_and_scale_payload() -> dict[str, Any]:
    return {
        "E_EQUALS_MC2_ROLE": "ALREADY_PRESENT",
        "CYCLE_INVARIANT_MASS": "CURRENT_DERIVED_CONDITIONAL_REQUIRES_STABLE_PHYSICAL_CYCLE",
        "HISTORICAL_EXPLICIT_MASS_OPERATOR": (
            "PROVENANCE_BLOCKED_AUTHOR_SELECTED_M4_ACTION_WITH_REUSABLE_GAUGE_"
            "INVARIANT_SPECTRAL_ALGEBRA"
        ),
        "DIMENSIONLESS_MASS_HIERARCHY": "CURRENT_CANDIDATE_FROZEN_NO_RETUNING",
        "ABSOLUTE_SCALE_ACTUAL_STATUS": (
            "CONDITIONAL_ON_EXTERNAL_PLANCK_OR_COSMOLOGICAL_ANCHOR;_ZERO_INPUT_"
            "ACTION_SELECTION_AND_PARENT_CHILD_NESTING_REMAIN_OPEN"
        ),
        "no_mass_energy_equivalence_rederivation": True,
        "no_mass_used_as_formation_trigger": True,
        "no_total_cosmic_scalar_energy_assumed": True,
    }


def composition_payload() -> dict[str, Any]:
    return {
        "LOCAL_STABILITY_OPERATOR": "CONDITIONAL_THEOREM_CLASS_EXISTS_PHYSICAL_LOCAL_ATTACHMENT_OPEN",
        "PHYSICAL_UNSTABLE_CONFIGURATION": "OPEN_NO_LOCALIZED_CONSTRAINT_SOLVED_NEGATIVE_MODE",
        "NONLINEAR_ENCLOSURE_BRANCH": "OPEN_NO_EXACT_ACTION_OWNED_ENDPOINT",
        "INSTABILITY_TO_ENCLOSURE_CONTINUATION": "OPEN_BOTH_PHYSICAL_ENDPOINTS_NOT_JOINTLY_PRESENT",
        "FORMATION_MAP_F": "OPEN_FIRST_AT_LOCALIZED_PHYSICAL_UNSTABLE_CONFIGURATION",
        "PERSISTENCE_MAP_P": "CONDITIONAL_THEOREM_CLASS_NO_ACTION_SELECTED_ORBIT",
        "DE_ENVELOPMENT_MAP_D": "OPEN_FORWARD_RECEIVING_MAP_NOT_INVERSE_OR_DAGGER",
        "COMPLETE_CYCLE": "OPEN",
        "question_A_instability_criterion": "YES_CONDITIONALLY",
        "question_B_unstable_physical_configuration": "NO_LOCALIZED_CONFIGURATION",
        "question_C_nonlinear_destination": "NO_PHYSICAL_ENDPOINT_OR_CONTINUATION",
        "distributed_components_close_formation": False,
        "first_missing_arrow": EXACT_NEXT_OBJECT,
    }


def formation_mechanism_payload() -> dict[str, Any]:
    return {
        "generic_law": "local physical instability may admit multiple nonlinear formation responses",
        "cavitation_role": "ONE_CANDIDATE_FORMATION_OR_ENCAPSULATION_MECHANISM_NOT_UNIVERSAL",
        "candidate_mechanisms": [
            "cavitation_like_local_enclosure",
            "pair_capture_or_collision_assisted_formation",
            "symmetry_breaking_or_bifurcation_locking",
            "nonhomogeneous_localization_or_bound_state_formation",
        ],
        "action_selected_unique_mechanism": None,
        "v14_93_control": {
            "historical_label": "ZERO_MODE_WITHOUT_CAVITATION",
            "generic_classification": "ZERO_MODE_WITHOUT_NEARBY_EQUIVARIANT_RADIAL_ENCAPSULATION",
            "global_no_go": False,
        },
    }


def existing_answer_table() -> list[dict[str, Any]]:
    """Required human/machine ``we already have this`` crosswalk."""

    return [
        _row("Parent surface", ["v15.7 author steering ontology"], "CURRENT_CANDIDATE", "ONE_PARENT_SURFACE_FIXED_AS_AUTHOR_ONTOLOGY", "no selection among parent universes"),
        _row("Local physical tangent", ["v6.0.3 sigma operator", "v14.61 physical projector"], "CURRENT_DERIVED_CONDITIONAL", "ARCHITECTURE_EXISTS", "attachment to a localized action solution"),
        _row("Hessian", ["v6.0.3", "v14.61", "v14.70-v14.77", "v14.94"], "CURRENT_DERIVED_CONDITIONAL", "CRITERION_EXISTS", "complete localized physical coefficients/operator"),
        _row("Negative mode", ["v14.94 Jensen branch"], "PROVENANCE_BLOCKED", "GLOBAL_HOMOGENEOUS_TACHYON_ONLY", "localized constraint-solved negative mode"),
        _row("Nonlinear branch", ["v6.0.3", "v6.30.5", "v14.60-v14.61", "v14.74"], "PROVENANCE_BLOCKED", "NORMAL_FORMS_OR_SYNTHETIC_FIXTURES_ONLY", "exact same-action physical endpoint"),
        _row("Self-adjoint domain", ["v14.65-v14.66", "v14.91", "v15.1"], "CURRENT_DERIVED_CONDITIONAL", "THEOREM_CLASSES_EXIST", "physical intertwining with localized coupled operator"),
        _row("Formation energy ledger", ["v14.81 exchange-current law", "v14.54 relative Hamiltonian contract", "v15.7 conditional Noether ledger"], "CURRENT_DERIVED_CONDITIONAL", "CONSERVATION_ARCHITECTURE_EXISTS", "one formation solution carrying the ledger across the nonlinear event"),
        _row("Relative periodic orbit", ["v14.54", "v15.6"], "CURRENT_DERIVED_CONDITIONAL", "PERSISTENCE_CONTRACT_ONLY", "action-selected stable physical orbit"),
        _row("Cycle energy", ["v14.54"], "CURRENT_DERIVED_CONDITIONAL", "RELATIVE_HAMILTONIAN_OR_FLOQUET_READOUT_OWNED", "physical stable cycle"),
        _row("E=mc^2 readout", ["v14.54"], "CURRENT_DERIVED_CONDITIONAL", "ALREADY_PRESENT", "no re-derivation"),
        _row("Family mass operator", ["2026-08-03 packet", "v11.4 executable"], "PROVENANCE_BLOCKED", "REUSABLE_GAUGE_INVARIANT_SPECTRAL_ALGEBRA", "action selection without alpha-anchored anisotropy"),
        _row("Absolute scale", ["v11.4 Planck-calibrated candidate", "cosmological-parent anchors"], "PROVENANCE_BLOCKED", "CONDITIONAL_EXTERNAL_CALIBRATION", "zero-input action-selected scale and parent-child nesting"),
    ]


def first_action_source_audit() -> dict[str, Any]:
    """Record why no retained term is promoted as the formation trigger."""

    return {
        "U_sigma_and_sigma_geometry": "GENERAL_SECOND_VARIATION_EXISTS_PHYSICAL_LOCAL_COEFFICIENTS_OPEN",
        "eta_sigma_or_attachment_response": "CONDITIONAL_RESPONSE_AND_ZERO_CROSSING_TOOLING_NO_COMMON_PHYSICAL_FORMATION_BRANCH",
        "curvature_and_Jensen": "GLOBAL_HOMOGENEOUS_TACHYON_NOT_LOCAL_EVENT",
        "boundary_flux_or_traction": "CONSERVATION_AND_INTERFACE_ARCHITECTURE_NO_ACTION_DERIVED_FORMATION_SOURCE",
        "Schur_reduced_response": "REUSABLE_THEOREM_MACHINERY_NOT_A_SOURCE_BY_ITSELF",
        "higher_order_texture_terms": "NORMAL_FORMS_EXIST_WITHOUT_SAME_ACTION_PHYSICAL_QUADRATIC_AND_ENDPOINT",
        "action_owned_formation_trigger_identified": False,
    }


def backward_closure_payload() -> dict[str, Any]:
    rows = reverse_dependency_rows()
    return {
        "artifact": "BHSM_backward_closure_existing_answer_audit_v15_8",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "REPOSITORY_EXISTING_ANSWER_EXHAUSTED": REPOSITORY_EXISTING_ANSWER_EXHAUSTED,
        "reverse_dependency_map": rows,
        "historical_result_classification": historical_result_rows(),
        "we_already_have_this_table": existing_answer_table(),
        "first_action_source_audit": first_action_source_audit(),
        "mass_and_scale": mass_and_scale_payload(),
        "composition": composition_payload(),
        "formation_mechanisms": formation_mechanism_payload(),
        "exact_next_object": EXACT_NEXT_OBJECT,
        "no_retuning_certificate": {
            "empirical_inputs_added": False,
            "fitted_parameters_added": False,
            "arbitrary_continuous_parameters_added": False,
            "new_fields_added": False,
            "preferred_frame_added": False,
            "frozen_predictions_changed": False,
            "official_prediction_logic_changed": False,
            "USB_TOUCHED": False,
        },
    }


def formation_composition_eligible(
    *, localized_unstable_configuration: bool, physical_domain_attached: bool,
    same_action_nonlinear_endpoint: bool, continuous_solution_branch: bool,
) -> bool:
    """Fail-closed formation composition gate."""

    return all((
        localized_unstable_configuration,
        physical_domain_attached,
        same_action_nonlinear_endpoint,
        continuous_solution_branch,
    ))


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def materialize(directory: str | Path) -> list[Path]:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_backward_closure_existing_answer_audit_v15_8.json"
    path.write_text(deterministic_json(backward_closure_payload()), encoding="utf-8", newline="\n")
    return [path]
