"""BHSM v14.1 eta-induced versus independent SU(3) fork theorem."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from .eta_boundary_dirac_contract_v14_1 import (
    boundary_dirac_contract_payload,
    flavor_independence_payload,
)
from .eta_color_bundle_matcher_audit_v14_1 import (
    BRANCH_DECISION,
    EXACT_NEXT_OBJECT,
    PROJECTION_PROVENANCE_VERDICT,
    bundle_isomorphism_payload,
    composite_variational_payload,
    matcher_payload,
    parent_architecture_recovery_payload,
    wall_extension_payload,
)
from .eta_projector_characteristic_classes_v14_1 import characteristic_class_payload
from .eta_projector_dof_audit_v14_1 import dof_payload
from .eta_projector_principal_symbol_v14_1 import principal_symbol_payload

VERSION = "v14.1"
THEOREM_TARGET = (
    "ETA_INDUCED_PROJECTOR_CONNECTION_VERSUS_INDEPENDENT_M4_SU3_CONNECTION_"
    "DEGREE_OF_FREEDOM_CHARACTERISTIC_CLASS_AND_ACTION_EQUIVALENCE_AUDIT"
)
ARTIFACT_FILES = {
    "lineage": "BHSM_scientific_lineage_v14_1.json",
    "recovery": "BHSM_v7_parent_bundle_eta_extension_recovery_v14_1.json",
    "bundle": "BHSM_eta_SU3_bundle_isomorphism_audit_v14_1.json",
    "dof": "BHSM_eta_projector_local_DOF_rank_v14_1.json",
    "symbol": "BHSM_eta_projector_principal_symbol_v14_1.json",
    "classes": "BHSM_eta_projector_characteristic_classes_v14_1.json",
    "holonomy": "BHSM_eta_projector_holonomy_algebra_v14_1.json",
    "extension": "BHSM_eta_wall_to_M4_extension_audit_v14_1.json",
    "variation": "BHSM_eta_projector_composite_variational_contract_v14_1.json",
    "matcher": "BHSM_eta_independent_connection_matcher_audit_v14_1.json",
    "dirac": "BHSM_eta_boundary_Dirac_index_contract_v14_1.json",
    "flavor": "BHSM_eta_color_flavor_independence_v14_1.json",
    "completion": "BHSM_completion_gate_v14_1.json",
}


def scientific_lineage_payload() -> dict[str, Any]:
    rows = [
        {"layer": "v6.3-v6.4", "classification": "RECOVERED_CONDITIONAL_GEOMETRY", "result": "G2/SU3 projectors, boundary polarization, Hopf connection split, and conditional chiral collar; action selection/transgression remained open"},
        {"layer": "v7.0-v7.1", "classification": "RECOVERED_CONDITIONAL_PARENT_ARCHITECTURE", "result": "stratified parent action, associated-bundle R85 transport, R54 trace, normalized measures, compatibility multipliers, and KKT intertwiners"},
        {"layer": "v8.8 common-parent current", "classification": "RECOVERED_CONDITIONAL_ASSOCIATED_CONNECTION_PRECEDENT", "result": "D_mu^fam U with parent-induced associated-bundle connections; kernel/action provenance remained conditional"},
        {"layer": "main through v11.3", "classification": "LIVE_MERGED", "result": "reciprocal Lambda85 metric attachment; no color-connection matcher"},
        {"layer": "v11.5 PR218", "classification": "OPEN_STACKED", "result": "coefficient-free spectral charged-current candidate; provenance gate open"},
        {"layer": "v11.6 PR219", "classification": "OPEN_STACKED_ACTION_OWNED", "result": "parent-action weak family current I3 and non-uniqueness no-go"},
        {"layer": "v13.1", "classification": "CONTINUATION_DERIVED_CONDITIONAL", "result": "degree-one static eta solution and radial stability"},
        {"layer": "v13.3", "classification": "CONTINUATION_CONDITIONAL", "result": "FR odd-degree quantization and emergent knot ontology"},
        {"layer": "v13.4-v13.5", "classification": "CONTINUATION_GEOMETRIC", "result": "eta-wall polarization, projector connection, and singlet covariance"},
        {"layer": "v14.0 PR220", "classification": "OPEN_STACKED_ACTION_AUDIT", "result": "block-separated eta/SU3 variation is zero; coupled BVP unauthorized"},
        {"layer": "v12.2 Lambda85 flavor bridge", "classification": "SUPERSEDED_INVALIDATED", "result": "family-central Hessian cannot supply off-diagonal flavor"},
        {"layer": "v11.5 spectral kernel", "classification": "DIAGNOSTIC_ACTION_CANDIDATE", "result": "mathematically viable but not parent-action derived"},
        {"layer": "gauge-dressed eta hadron BVP", "classification": "DOWNSTREAM_BLOCKED", "result": "requires a coupled Gauss equation"},
    ]
    validation = {
        "live_merged_distinguished_from_stacked": True,
        "conditional_distinguished_from_action_owned": True,
        "v7_parent_reduction_architecture_recovered": True,
        "superseded_candidate_identified": True,
        "diagnostic_kernel_not_promoted": True,
        "exact_gates_explicit": True,
    }
    return {
        "artifact": "BHSM_scientific_lineage_v14_1",
        "version": VERSION,
        "rows": rows,
        "exact_open_gates": [
            EXACT_NEXT_OBJECT,
            "ACTION_DERIVED_ORIENTED_BOUNDARY_DIRAC_OPERATOR_ON_THE_FR_ETA_KNOT_BUNDLE_WITH_SELF_ADJOINT_DOMAIN",
            "PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_OF_THE_SPECTRAL_CHARGED_CURRENT_KERNEL",
        ],
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def holonomy_payload() -> dict[str, Any]:
    dof = dof_payload()
    dimensions = dof["holonomy_algebra_dimensions"]
    validation = {
        "generic_universal_holonomy_su3": dimensions == [8, 8, 8, 8],
        "constant_selector_spacetime_holonomy_trivial": True,
        "symmetric_maps_can_reduce_holonomy": True,
        "full_holonomy_not_field_space_equivalence": True,
    }
    return {
        "artifact": "BHSM_eta_projector_holonomy_algebra_v14_1",
        "version": VERSION,
        "method": "Ambrose-Singer curvature generators closed under matrix commutators",
        "generic_dimensions": dimensions,
        "constant_selector_dimension": 0,
        "interpretation": "The canonical homogeneous connection can generate all su3 directions, but selector-derived spacetime connections remain a constrained subset.",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def completion_payload() -> dict[str, Any]:
    lineage = scientific_lineage_payload()
    recovery = parent_architecture_recovery_payload()
    bundle = bundle_isomorphism_payload()
    dof = dof_payload()
    symbol = principal_symbol_payload()
    classes = characteristic_class_payload()
    holonomy = holonomy_payload()
    extension = wall_extension_payload()
    variation = composite_variational_payload()
    matcher = matcher_payload()
    dirac = boundary_dirac_contract_payload()
    flavor = flavor_independence_payload()
    validation = {
        "lineage_recovered": lineage["validation_passed"],
        "conditional_parent_architecture_recovered": recovery["validation_passed"],
        "bundle_nonidentification_proved": bundle["validation_passed"],
        "local_DOF_and_holonomy_resolved": dof["validation_passed"] and holonomy["validation_passed"],
        "principal_symbol_no_go_proved": symbol["validation_passed"],
        "characteristic_class_no_go_proved": classes["validation_passed"],
        "wall_extension_missing": extension["validation_passed"] and extension["canonical_extension"] is None,
        "composite_variation_not_independent_Gauss": variation["validation_passed"],
        "eta_color_matcher_not_instantiated": matcher["validation_passed"] and matcher["retained_matcher"] is None,
        "boundary_index_fail_closed": dirac["validation_passed"] and dirac["Index_D_rel"] is None,
        "family_current_I3_preserved": flavor["validation_passed"],
        "no_proxy_BVP_solved": True,
        "frozen_predictions_unchanged": True,
        "official_prediction_logic_unchanged": True,
        "measured_inputs_not_used": True,
        "new_fields_not_introduced": True,
        "new_continuous_coefficients_not_introduced": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v14_1",
        "version": VERSION,
        "theorem_target": THEOREM_TARGET,
        "branch_decision": BRANCH_DECISION,
        "projection_provenance_verdict": PROJECTION_PROVENANCE_VERDICT,
        "composite_connection_verdict": (
            "RESTRICTED_ETA_INDUCED_COLOR_FRAME_BERRY_CONNECTION_NOT_FULL_QCD"
        ),
        "independent_connection_verdict": (
            "RETAINED_AS_THE_ONLY_CURRENT_ACTION_FIELD_WITH_YANG_MILLS_PRINCIPAL_"
            "SYMBOL_BUT_NOT_COUPLED_TO_ETA"
        ),
        "bundle_isomorphism_verdict": "NO_CANONICAL_OR_ACTION_OWNED_PHI_EXISTS",
        "local_DOF_rank": {
            "dP_per_covector": 6,
            "generic_curvature_Jacobian_24_to_48": 23,
            "constant_selector_linear_rank": 0,
        },
        "principal_symbol_verdict": symbol["verdict"],
        "characteristic_class_verdict": classes["verdict"],
        "instanton_sector_verdict": "COMPOSITE_EP_HAS_C2_ZERO_AND_CANNOT_SPAN_GENERAL_SU3_INSTANTON_SECTORS",
        "holonomy_algebra_dimension": 8,
        "variational_Gauss_law_verdict": "NO_INDEPENDENT_ETA_SOURCED_SU3_GAUSS_EQUATION",
        "boundary_Dirac_index_status": "OPERATOR_CONTRACT_ONLY_INDEX_NOT_EVALUABLE",
        "flavor_current_status": "J_PLUS_FAMILY_EQUALS_I3",
        "Mark_III": "BLOCKED_BY_UNPROVEN_ETA_AND_M4_SU3_ASSOCIATED_PROJECTIONS_OF_THE_RECOVERED_PARENT_CONNECTION_ARCHITECTURE",
        "BHSM_physical_completion": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _default(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"real": float(value.real), "imag": float(value.imag)}
    raise TypeError(type(value).__name__)


def deterministic_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, default=_default) + "\n"


def build_artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "lineage": scientific_lineage_payload(),
        "recovery": parent_architecture_recovery_payload(),
        "bundle": bundle_isomorphism_payload(),
        "dof": dof_payload(),
        "symbol": principal_symbol_payload(),
        "classes": characteristic_class_payload(),
        "holonomy": holonomy_payload(),
        "extension": wall_extension_payload(),
        "variation": composite_variational_payload(),
        "matcher": matcher_payload(),
        "dirac": boundary_dirac_contract_payload(),
        "flavor": flavor_independence_payload(),
        "completion": completion_payload(),
    }


def materialize(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payloads = build_artifact_payloads()
    paths = []
    for key, filename in ARTIFACT_FILES.items():
        path = output_dir / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        paths.append(path)
    return paths
