from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from bhsm.interface.environmental_child_compatibility_selection import (
    E_CLASS,
    EXACT_NEXT_OBJECT,
    EXCLUDED,
    OWNER_STATUS,
    SUPPORTED,
    UNRESOLVED,
    ChildRequirement,
    EnvironmentalState,
    adversarial_compatibility_tests,
    child_requirement_signature,
    claim_boundary,
    compatibility_relation,
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


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_environmental_child_compatibility_selection.py"


def _materializer():
    spec = importlib.util.spec_from_file_location("environment_materializer", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_owner_postulate_is_recovered_deep_work_not_new_physics() -> None:
    result = owner_environmental_selection_postulate()
    assert result["owner"] == "Norman P. Carberry"
    assert result["status"] == OWNER_STATUS
    assert result["pre_existing_owner_work_not_new_physics"] is True
    assert result["newly_materialized_in_this_sprint"] is True
    assert result["derived_from_thirteen_term_action"] is False
    assert result["existing_channel_semantics"].startswith("(I_event,I_environment,B_SM)")
    assert result["cross_sector_branch_selection_arbitrary"] is False


def test_minimal_environment_descriptor_has_five_necessary_components() -> None:
    result = minimal_environmental_state_descriptor()
    assert result["formula"] == "E_s=(alpha_s,tau_s,I_s,Lambda_s,B_s)"
    assert [row["symbol"] for row in result["components"]] == [
        "alpha_s", "tau_s", "I_s", "Lambda_s", "B_s"
    ]
    assert len(result["minimality"]) == 5
    assert "arbitrary_fitted_thresholds" in result["not_included"]


def test_regime_space_separates_core_firewall_and_regular_geometry() -> None:
    result = spacetime_regime_classification()
    rows = {row["regime"]: row for row in result["rows"]}
    assert "not_upsilon_equals_zero" in rows["C_A_PREGEOMETRIC_CORE"]["condition"]
    assert "metric" in rows["C_A_PREGEOMETRIC_CORE"]["missing"]
    assert "NOT_PROVED_SPACETIME_EDGE" in rows[
        "LEGENDRE_FIREWALL_TRANSITION_FACE"
    ]["status"]
    assert "causal_cones" in rows["G_A_LORENTZIAN_REGULAR"]["objects"]
    assert "Lorentzian_causal_cones" in rows["G_A_EUCLIDEAN_REGULAR"]["missing"]
    assert len(result["forbidden_identifications"]) == 4


def test_event_scenarios_type_structure_creation_and_AE4_support() -> None:
    result = scenario_event_classification()
    assert result["typed_order"] == [
        "formation", "constraint_solved_shear", "surface_separation",
        "Legendre_firewall", "oriented_cut", "child_reconstruction",
    ]
    assert "PRODUCES_IT" in result["creation_semantics"]
    assert result["AE4_child_condition"] == "FUTURE_RETARDED_REGULARITY_OR_OUTGOING_SUPPORT_ONLY"
    assert result["canonical_stop_identifies_spacetime_edge"] is False


def test_scale_and_energy_use_owned_relations_without_optimization() -> None:
    result = scale_and_energy_variables()
    assert result["scale"]["ell_kappa"]["formula"] == "kappa1^(-1/6)"
    assert result["scale"]["canonical_reset_radius"]["owned"] is True
    assert result["scale"]["return_scale"]["owned"] is False
    assert result["scale"]["arbitrary_cutoffs_added"] is False
    assert result["energy"]["core_conventional_energy"] is None
    assert result["energy"]["minimum_energy_selection_used"] is False


def test_child_requirement_signature_is_structural_and_fail_closed() -> None:
    result = child_requirement_signature()
    child = result["knotted_spacetime_child"]
    assert "nondegenerate_metric" in child["required_structures"]
    assert "Hopf_full_preimage" in child["required_structures"]
    assert child["required_invariants"]["degree"] == 1
    assert child["required_invariants"]["FR_parity"] == -1
    assert child["requires_retarded_support"] is True
    assert "environment_conditioned_return_scale" in child["unresolved_requirements"]
    assert "UNKNOWN_IS_OPEN" in result["threshold_policy"]


def test_compatibility_relation_has_supported_excluded_and_unresolved_states() -> None:
    environment = EnvironmentalState(
        regime="R",
        event_class="EVENT",
        available_structures=frozenset({"metric"}),
        produced_structures=frozenset(),
        invariants={"degree": 1},
        scale_data={"scale": "exact"},
        energy_support={"constraint": True},
        retarded=True,
    )
    base = dict(
        child_id="child",
        admitted_regimes=frozenset({"R"}),
        admitted_events=frozenset({"EVENT"}),
        required_structures=frozenset({"metric"}),
        required_invariants={"degree": 1},
        required_scale_relations={"scale": "exact"},
        required_energy_support=frozenset({"constraint"}),
        requires_retarded_support=True,
    )
    supported = ChildRequirement(**base)
    unresolved = ChildRequirement(
        **base, unresolved_requirements=frozenset({"unknown_threshold"})
    )
    excluded = ChildRequirement(**{**base, "required_structures": frozenset({"spin"})})
    missing_energy = EnvironmentalState(
        **{**environment.__dict__, "energy_support": {}, "retarded": None}
    )
    assert compatibility_relation(environment, supported)["status"] == SUPPORTED
    assert compatibility_relation(environment, unresolved)["status"] == UNRESOLVED
    assert compatibility_relation(environment, excluded)["status"] == EXCLUDED
    assert compatibility_relation(missing_energy, supported)["status"] == UNRESOLVED


def test_owner_example_is_direct_incompatibility_with_typed_transition_escape() -> None:
    result = owner_example_adjudication()
    assert "S3_TIMES_S3" in result["spacetime_in_knots_means"]
    assert "NOT_AN_ACTION_DERIVED_SYNONYM_THEOREM" in result[
        "spacetime_in_knots_identification_status"
    ]
    assert result["exact_owner_phrase_to_mathematical_object_equivalence_derived"] is False
    assert "METRIC" in result["no_spacetime_means"]
    assert result["core_directly_to_knotted"]["status"] == EXCLUDED
    assert result["regular_directly_to_pregeometric"]["status"] == EXCLUDED
    assert "DIRECT_PRODUCTION" in result["vice_versa_qualification"]
    assert result["current_general_core_geometry_transition_owned"] is False


def test_adversarial_structure_checks_are_stronger_than_scale_and_energy() -> None:
    result = adversarial_compatibility_tests()
    assert result["known_child_status"]["status"] == UNRESOLVED
    for key in (
        "same_scale_energy_but_spin_incompatible",
        "topology_change_without_owned_transition",
        "advanced_AE4_candidate",
        "incompatible_incidence",
        "nontrivial_holonomy_without_connection",
        "disconnected_attachment_without_boundary_solution",
    ):
        assert result[key]["status"] == EXCLUDED
    assert result["positive_Hopf_rotor"]["positive"] is True
    assert result["positive_Hopf_rotor"]["selects_orientation_or_attachment"] is False
    assert "DOES_NOT_SELECT" in result["Galerkin_restriction"]


def test_environmental_filter_leaves_E5_not_a_unique_reset() -> None:
    result = reset_family_after_environmental_selection()
    assert result["classification"] == E_CLASS == "E5"
    assert result["E1"] is False
    assert result["E2"] is False
    assert result["E3"] is False
    assert result["E4"] is False
    assert result["E5"] is True
    assert "INFINITE_DIMENSIONAL" in result["surviving_freedom"]
    assert result["base_map_witness"]["different_tangent_maps"] is True
    assert result["polarization_witness"]["different_jets"] is True


def test_all_four_base_routes_are_filtered_but_none_is_selected() -> None:
    routes = reset_family_after_environmental_selection()["effect_on_base_routes"]
    assert set(routes) == {
        "common_embedding", "retained_flow", "normal_collar",
        "implicit_spatial_construction",
    }
    assert all(value == "MUST_PASS_COMPATIBILITY_BUT_NOT_SELECTED" for value in routes.values())


def test_owner_postulate_reclassifies_deficit_but_does_not_unlock_generator() -> None:
    result = consequence_and_downstream_status()
    claims = claim_boundary()
    assert result["physical_principle_deficit_reclassified"].startswith("ZERO_NEW_OWNER_PRINCIPLE")
    assert result["functional_dimension_reduced_to_finite"] is False
    assert result["selected_reset"] is None
    assert (result["F_class"], result["L_class"], result["D_class"]) == ("F4", "L4", "D4")
    assert (result["differentiability_class"], result["charge_class"], result["outcome"]) == ("G4", "U", "D")
    assert result["S4"] == "BLOCKED"
    assert claims["interface_functional_implemented"] is False
    assert claims["frozen_predictions_changed"] is False


def test_hindsight_ledger_preserves_provenance_and_exact_next_object() -> None:
    result = hindsight_ledger()
    assert "EXISTING_DEEP_OWNER_SEMANTICS_PRECEDES_THIS_MATERIALIZATION" in result["VALIDATED"]
    assert "OWNER_POSTULATE_IS_NEWLY_INVENTED_PHYSICS" in result["INVALIDATED"]
    assert "NOT_CLASSIFIED_AS_NEW_PHYSICS" in result["NEW_PHYSICS_DEFICIT"]
    assert result["SURVIVING_RESET_FREEDOM"] == "E5"
    assert result["EXACT_NEXT_OBJECT"] == EXACT_NEXT_OBJECT


def test_two_artifact_materializer_is_validated_deterministic_and_byte_stable() -> None:
    module = _materializer()
    owner_first = module.build_postulate_payload()
    owner_second = module.build_postulate_payload()
    class_first = module.build_classification_payload()
    class_second = module.build_classification_payload()
    assert owner_first["validation_passed"] is True
    assert class_first["validation_passed"] is True
    assert class_first["environmental_class"] == "E5"
    assert module.deterministic_json(owner_first) == module.deterministic_json(owner_second)
    assert module.deterministic_json(class_first) == module.deterministic_json(class_second)
    outputs = module.main()
    first_bytes = tuple(path.read_bytes() for path in outputs)
    module.main()
    assert tuple(path.read_bytes() for path in outputs) == first_bytes
    assert json.loads(first_bytes[0])["status"] == OWNER_STATUS
    assert json.loads(first_bytes[1])["EXACT_NEXT_OBJECT"] == EXACT_NEXT_OBJECT
