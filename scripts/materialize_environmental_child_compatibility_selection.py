"""Materialize the recovered owner postulate and environmental reset audit."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Mapping

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.environmental_child_compatibility_selection import (  # noqa: E402
    ACTION_VERSION,
    CLASSIFICATION,
    E_CLASS,
    EXACT_NEXT_OBJECT,
    IMPLEMENTATION_DEFICIT,
    OWNER_STATUS,
    STATUS,
    adversarial_compatibility_tests,
    child_requirement_signature,
    claim_boundary,
    consequence_and_downstream_status,
    hindsight_ledger,
    minimal_environmental_state_descriptor,
    owner_environmental_selection_postulate,
    owner_example_adjudication,
    reset_family_after_environmental_selection,
    scale_and_energy_variables,
    scenario_event_classification,
    spacetime_regime_classification,
)


POSTULATE_TARGET = (
    ROOT
    / "artifacts/action_extension/BHSM_OWNER_ENVIRONMENTAL_CHILD_SELECTION_POSTULATE.json"
)
CLASSIFICATION_TARGET = (
    ROOT
    / "artifacts/action_extension/BHSM_ENVIRONMENTAL_RESET_COMPATIBILITY_CLASSIFICATION.json"
)
MODULE = ROOT / "src/bhsm/interface/environmental_child_compatibility_selection.py"
SCRIPT = Path(__file__).resolve()
THEORY = ROOT / "theory/bhsm_environmental_child_compatibility_selection.md"
TEST = ROOT / "tests/test_environmental_child_compatibility_selection.py"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".py", ".md", ".json"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _canonical(value: Any) -> Any:
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.ndarray):
        return _canonical(value.tolist())
    if isinstance(value, np.complexfloating):
        value = complex(value)
    if isinstance(value, complex):
        if not (math.isfinite(value.real) and math.isfinite(value.imag)):
            raise ValueError("non-finite complex value")
        return {"real": _canonical(value.real), "imag": _canonical(value.imag)}
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float value")
        rounded = round(value, 12)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True, allow_nan=False) + "\n"


def build_postulate_payload() -> dict[str, Any]:
    postulate = owner_environmental_selection_postulate()
    claims = claim_boundary()
    validation = {
        "owner_named": postulate["owner"] == "Norman P. Carberry",
        "pre_existing_deep_work_preserved": (
            postulate["status"] == OWNER_STATUS
            and postulate["pre_existing_owner_work_not_new_physics"]
        ),
        "not_misclassified_as_old_action_theorem": (
            not postulate["derived_from_thirteen_term_action"]
            and not claims["owner_postulate_derived_from_old_action"]
        ),
        "existing_channel_semantics_recovered": postulate[
            "existing_channel_semantics"
        ].startswith("(I_event,I_environment,B_SM)"),
        "arbitrary_cross_sector_choice_forbidden": not postulate[
            "cross_sector_branch_selection_arbitrary"
        ],
        "no_new_physics_claim": not claims["owner_postulate_newly_invented"],
        "claim_boundary_closed": (
            not claims["FULL_BHSM_COMPLETE"]
            and not claims["frozen_predictions_changed"]
        ),
    }
    return {
        "artifact": "BHSM_OWNER_ENVIRONMENTAL_CHILD_SELECTION_POSTULATE",
        "action_version": ACTION_VERSION,
        "classification": "OWNER_AUTHORIZED_RECOVERED_POSTULATE",
        "status": OWNER_STATUS,
        "postulate": postulate,
        "owner_semantics_separation": {
            "PREVIOUSLY_DERIVED": hindsight_ledger()["PREVIOUSLY_DERIVED"],
            "OWNER_AUTHORIZED_RECOVERED_POSTULATE": hindsight_ledger()[
                "OWNER_AUTHORIZED_RECOVERED_POSTULATE"
            ],
            "NOT_YET_DERIVED": hindsight_ledger()["NOT_YET_DERIVED"],
        },
        "claim_boundary": claims,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def build_classification_payload() -> dict[str, Any]:
    descriptor = minimal_environmental_state_descriptor()
    regimes = spacetime_regime_classification()
    scenarios = scenario_event_classification()
    scale_energy = scale_and_energy_variables()
    requirements = child_requirement_signature()
    owner_example = owner_example_adjudication()
    adversarial = adversarial_compatibility_tests()
    family = reset_family_after_environmental_selection()
    downstream = consequence_and_downstream_status()
    ledger = hindsight_ledger()
    claims = claim_boundary()

    sources = (
        "theory/bhsm_spacetime_edge_ontology_repair.md",
        "theory/norman_owner_ontology_recovered.md",
        "src/bhsm/interface/current_semantic_normalization.py",
        "src/bhsm/interface/envelopment/canonical_crystallization_v11_0.py",
        "src/bhsm/interface/envelopment/spacetime_support_order_parameter_v10_4.py",
        "src/bhsm/interface/completion/aether_parent_stratification_v15_0.py",
        "src/bhsm/interface/completion/local_environment_finite_time_encapsulation_gate_v14_94.py",
        "src/bhsm/interface/aether_reconstruction_firewall_event_v15_45.py",
        "src/bhsm/interface/aether_scale_child_ownership_audit_v16_78.py",
        "src/bhsm/interface/aether_lorentzian_child_galerkin_v15_44.py",
        "src/bhsm/interface/ae4_future_collapse_relative_boundary_domain.py",
        "src/bhsm/interface/gauge_connection_reset_bundle_lift_adjudication.py",
        "src/bhsm/interface/nonfermion_relative_boundary_variation.py",
        "src/bhsm/interface/reset_correspondence_stationarity_adjudication.py",
        MODULE.relative_to(ROOT).as_posix(),
        SCRIPT.relative_to(ROOT).as_posix(),
        THEORY.relative_to(ROOT).as_posix(),
        TEST.relative_to(ROOT).as_posix(),
    )
    source_hashes = {
        source: _sha256(ROOT / source)
        for source in sorted(sources)
        if (ROOT / source).is_file()
    }
    excluded_cases = (
        "same_scale_energy_but_spin_incompatible",
        "topology_change_without_owned_transition",
        "advanced_AE4_candidate",
        "incompatible_incidence",
        "nontrivial_holonomy_without_connection",
        "disconnected_attachment_without_boundary_solution",
    )
    validation = {
        "five_component_environment_is_minimal": (
            descriptor["formula"] == "E_s=(alpha_s,tau_s,I_s,Lambda_s,B_s)"
            and len(descriptor["components"]) == 5
            and len(descriptor["minimality"]) == 5
        ),
        "spacetime_strata_are_not_binary_flag": len(regimes["rows"]) >= 6,
        "core_is_separate_not_upsilon_zero": any(
            row["regime"] == "C_A_PREGEOMETRIC_CORE"
            and "not_upsilon_equals_zero" in row["condition"]
            for row in regimes["rows"]
        ),
        "firewall_not_promoted_to_spacetime_edge": any(
            row["regime"] == "LEGENDRE_FIREWALL_TRANSITION_FACE"
            and "NOT_PROVED_SPACETIME_EDGE" in row["status"]
            for row in regimes["rows"]
        ),
        "scenario_creation_rule_is_typed": "PRODUCES_IT" in scenarios[
            "creation_semantics"
        ],
        "no_arbitrary_scale_cutoff": not scale_energy["scale"][
            "arbitrary_cutoffs_added"
        ],
        "no_minimum_energy_rule": not scale_energy["energy"][
            "minimum_energy_selection_used"
        ],
        "child_requirements_include_structure_scale_energy_causality": (
            len(requirements["knotted_spacetime_child"]["required_structures"]) > 8
            and requirements["knotted_spacetime_child"]["required_scale_relations"]
            and requirements["knotted_spacetime_child"]["required_energy_support"]
            and requirements["knotted_spacetime_child"]["requires_retarded_support"]
        ),
        "owner_example_core_to_knotted_excluded": owner_example[
            "core_directly_to_knotted"
        ]["status"] == "EXCLUDED",
        "owner_example_vice_versa_is_scenario_relative": (
            owner_example["regular_directly_to_pregeometric"]["status"] == "EXCLUDED"
            and "DIRECT_PRODUCTION" in owner_example["vice_versa_qualification"]
        ),
        "unknown_real_child_inputs_fail_open_not_false": adversarial[
            "known_child_status"
        ]["status"] == "UNRESOLVED",
        "all_adversarial_incompatibilities_excluded": all(
            adversarial[key]["status"] == "EXCLUDED" for key in excluded_cases
        ),
        "positive_Hopf_energy_not_used_as_selector": (
            adversarial["positive_Hopf_rotor"]["positive"]
            and not adversarial["positive_Hopf_rotor"][
                "selects_orientation_or_attachment"
            ]
        ),
        "all_base_routes_remain_unselected": all(
            value.endswith("NOT_SELECTED")
            for value in family["effect_on_base_routes"].values()
        ),
        "base_map_nonuniqueness_survives_environment": (
            family["base_map_witness"]["same_degree"]
            and family["base_map_witness"]["same_orientation"]
            and family["base_map_witness"]["same_metric"]
            and family["base_map_witness"]["different_tangent_maps"]
            and family["base_map_witness"][
                "both_have_same_environmental_requirement_signature"
            ]
        ),
        "polarization_nonuniqueness_survives_environment": (
            family["polarization_witness"]["both_maximal_isotropic"]
            and family["polarization_witness"]["different_jets"]
            and family["polarization_witness"][
                "same_environmental_requirement_signature"
            ]
        ),
        "E5_selected_exclusively": (
            not family["E1"] and not family["E2"] and not family["E3"]
            and not family["E4"] and family["E5"]
            and family["classification"] == E_CLASS
        ),
        "deep_owner_work_not_called_new_physics": "NOT_CLASSIFIED_AS_NEW_PHYSICS" in ledger[
            "NEW_PHYSICS_DEFICIT"
        ],
        "implementation_deficit_precise": downstream[
            "mathematical_implementation_deficit"
        ] == IMPLEMENTATION_DEFICIT,
        "no_interface_functional_implemented": not claims[
            "interface_functional_implemented"
        ],
        "G4_U_D_retained": (
            downstream["differentiability_class"] == "G4"
            and downstream["charge_class"] == "U"
            and downstream["outcome"] == "D"
        ),
        "frozen_predictions_unchanged": not claims["frozen_predictions_changed"],
        "full_BHSM_not_claimed": not claims["FULL_BHSM_COMPLETE"],
    }
    return {
        "artifact": "BHSM_ENVIRONMENTAL_RESET_COMPATIBILITY_CLASSIFICATION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "status": STATUS,
        "environmental_class": E_CLASS,
        "owner_postulate": owner_environmental_selection_postulate(),
        "minimal_environmental_state": descriptor,
        "spacetime_regimes": regimes,
        "scenario_event_classes": scenarios,
        "scale_and_energy": scale_energy,
        "child_requirements": requirements,
        "compatibility_relation": owner_example[
            "core_directly_to_knotted"
        ]["formula"],
        "owner_example_adjudication": owner_example,
        "adversarial_tests": adversarial,
        "surviving_reset_family": family,
        "consequence_and_downstream": downstream,
        "PREVIOUSLY_DERIVED": ledger["PREVIOUSLY_DERIVED"],
        "OWNER_AUTHORIZED_RECOVERED_POSTULATE": ledger[
            "OWNER_AUTHORIZED_RECOVERED_POSTULATE"
        ],
        "NOT_YET_DERIVED": ledger["NOT_YET_DERIVED"],
        "VALIDATED": ledger["VALIDATED"],
        "INVALIDATED": ledger["INVALIDATED"],
        "REDUNDANT": ledger["REDUNDANT"],
        "OPEN": ledger["OPEN"],
        "DECISION_POWER": ledger["DECISION_POWER"],
        "NEW_PHYSICS_DEFICIT": ledger["NEW_PHYSICS_DEFICIT"],
        "OWNER_POSTULATE_CONSEQUENCE": ledger["OWNER_POSTULATE_CONSEQUENCE"],
        "ENVIRONMENTAL_CLASSIFICATION": ledger["ENVIRONMENTAL_CLASSIFICATION"],
        "CHILD_REQUIREMENT_CLASSIFICATION": ledger[
            "CHILD_REQUIREMENT_CLASSIFICATION"
        ],
        "SURVIVING_RESET_FREEDOM": ledger["SURVIVING_RESET_FREEDOM"],
        "EXACT_NEXT_OBJECT": EXACT_NEXT_OBJECT,
        "claim_boundary": claims,
        "source_sha256": source_hashes,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def main() -> tuple[Path, Path]:
    POSTULATE_TARGET.parent.mkdir(parents=True, exist_ok=True)
    postulate = deterministic_json(build_postulate_payload())
    classification = deterministic_json(build_classification_payload())
    POSTULATE_TARGET.write_text(postulate, encoding="utf-8", newline="\n")
    CLASSIFICATION_TARGET.write_text(classification, encoding="utf-8", newline="\n")
    return POSTULATE_TARGET, CLASSIFICATION_TARGET


if __name__ == "__main__":
    for output in main():
        print(output)
