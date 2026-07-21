import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from bhsm.interface import correspondence_novelty_firewall as fw


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_correspondence_novelty_firewall_v6_0_6.md"
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key):
    return json.loads((ARTIFACTS / fw.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def public_text():
    paths = [DOC, ROOT / "STATUS.md", ROOT / "CLAIMS.md", ROOT / "ARTIFACT_INDEX.md", ROOT / "CLI_REFERENCE.md"]
    paths.extend(ARTIFACTS / name for name in fw.ARTIFACT_FILES.values())
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def by_concept():
    return {row["concept"]: row for row in load("firewall")["rows"]}


def test_artifact_package_has_required_results_and_claim_guards():
    assert len(fw.ARTIFACT_FILES) == 16
    for key in fw.ARTIFACT_FILES:
        payload = load(key)
        assert payload["primary_result"] == "BHSM_CORRESPONDENCE_NOVELTY_FIREWALL_DERIVED", key
        assert payload["reduction_readiness_result"] == "BHSM_B8_S7_TO_BERGER_S3_REDUCTION_READINESS_IDENTIFIED", key
        assert payload["reduction_status"] == "BHSM_B8_S7_TO_BERGER_S3_REDUCTION_BLOCKED", key
        assert payload["new_parent_field_added"] is False
        assert payload["new_interaction_added"] is False
        assert payload["measured_mass_coupling_or_scale_used"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False


def test_materialization_is_deterministic():
    built = fw.build_artifact_payloads(ROOT)
    for key, filename in fw.ARTIFACT_FILES.items():
        assert (ARTIFACTS / filename).read_text(encoding="utf-8") == fw.deterministic_json(built[key])


def test_physicality_is_frozen_as_ontology_not_dynamical_theorem():
    payload = load("ontology")
    assert payload["status"] == "BHSM_PHYSICALITY_ONTOLOGY_FROZEN"
    assert payload["category"] == "BHSM_GEOMETRIC_REINTERPRETATION"
    assert payload["scope"] == "interpretive ontology, not a new dynamical theorem"
    assert payload["universal_sigma_required"] is False
    assert payload["universal_harmonic_trigger_required"] is False


def test_minimal_dictionary_keeps_differential_persistence_and_objecthood_distinct():
    rows = load("ontology")["dictionary"]
    assert [row["term"] for row in rows] == ["physical differential", "envelopment", "persistence", "objecthood", "particle-like object"]
    assert len({row["definition"] for row in rows}) == 5


def test_registry_covers_every_required_major_concept_with_full_schema():
    required = {
        "stress-energy conservation", "compression", "collisions", "outgoing waves and explosion-like shells",
        "constructive and destructive interference", "curvature sourced by stress-energy", "gauge connections",
        "topological solitons", "compact-space spectra", "particle localization", "stable objecthood",
        "charge quantization", "three generations", "particle masses", "gauge couplings", "fine-structure constant",
        "CKM", "PMNS", "neutrino scale", "black-hole de-envelopment", "shared-core hypothesis",
        "primordial release", "absolute unit", "v5 scalar/topographic vacuum", "exact S7 octave pair",
        "Berger S3 mode ledger",
    }
    rows = by_concept()
    assert required <= set(rows)
    schema = {"category", "precise_statement", "source_artifact", "bhsm_specific", "mathematical_dependencies", "physical_dependencies", "claim_boundary", "changes_observable_calculation", "independently_testable"}
    assert all(schema <= set(row) for row in rows.values())
    assert all(row["category"] in fw.CATEGORIES for row in rows.values())


def test_all_registry_source_artifacts_exist():
    for row in by_concept().values():
        assert (ROOT / row["source_artifact"]).exists(), row["concept"]


def test_established_physics_is_correspondence_not_bhsm_novelty():
    rows = by_concept()
    for concept in ["stress-energy conservation", "compression", "collisions", "outgoing waves and explosion-like shells", "constructive and destructive interference", "curvature sourced by stress-energy", "gauge connections", "topological solitons"]:
        assert rows[concept]["category"] == "ESTABLISHED_PHYSICS_CORRESPONDENCE"
        assert rows[concept]["bhsm_specific"] is False
    assert load("correspondence")["status"] == "BHSM_ESTABLISHED_PHYSICS_CORRESPONDENCE_REGISTRY_DERIVED"


def test_correspondence_does_not_supply_foundational_coefficients_or_fitting():
    payload = load("correspondence")
    assert "supply unexplained foundational coefficients" in payload["forbidden_uses"]
    assert "target fit BHSM outputs" in payload["forbidden_uses"]


def test_prediction_label_requires_preregistration_freeze_and_independent_test():
    gate = load("firewall")["prediction_gate"]
    assert gate["required_category"] == "BHSM_NOVEL_PREDICTION_FROZEN"
    assert "numerical or structural preregistration" in gate["requirements"]
    assert "frozen output before experimental comparison" in gate["requirements"]
    assert "independent testability" in gate["requirements"]
    assert load("firewall")["current_v6_0_6_predictions"] == []


def test_exact_octave_is_retained_but_nonuniversal():
    payload = load("harmonic")
    assert payload["status"] == "BHSM_HARMONIC_ROLE_RECLASSIFIED"
    assert payload["exact_result"]["formula"] == "omega_10=2 omega_4"
    assert payload["exact_result"]["category"] == "BHSM_DERIVED"
    assert payload["ordinary_interference"] == "ESTABLISHED_PHYSICS_CORRESPONDENCE"
    assert payload["future_mode_selection"] == "BHSM_CANDIDATE"
    assert "universal physicality trigger" in payload["not_implied"]
    assert "nonlinear resonance" in payload["not_implied"]


def test_sigma_is_candidate_not_universal_and_reduced_values_stay_conditional():
    payload = load("sigma")
    assert payload["status"] == "BHSM_SIGMA_ROLE_RECLASSIFIED"
    assert payload["category"] == "BHSM_CANDIDATE"
    assert payload["universal_definition_of_physicality"] is False
    assert payload["reduced_model"] == {"potential": "V_red(sigma)=-sigma^2+2 sigma^4", "A_ST": -2, "G_ST": 8, "vacuum_abs_sigma": 0.5, "status": "REDUCED_CONDITIONAL_PARENT_MAP_OPEN"}


def test_v605_kill_test_remains_narrowly_scoped():
    report = load("report")
    assert report["retained_v6_0_5_results"] == [
        "BHSM_MINIMAL_PARENT_THEORY_FAILS_PHYSICALITY_TRIGGER",
        "BHSM_MINIMAL_FREE_SCALAR_COHERENT_TRIGGER_FAILED",
        "BHSM_HARMONIC_ENVELOPMENT_SELECTION_NOT_DERIVED",
        "BHSM_GENERAL_ENERGY_GEOMETRY_ENVELOPMENT_REMAINS_OPEN",
    ]


def test_every_s7_to_s3_candidate_has_explicit_map_requirement_or_rejection():
    rows = load("roles")["rows"]
    assert len(rows) == 9
    assert all(row["map"] is not None or row["status"] in {"REJECTED_AS_CURRENT_CANONICAL_ROLE", "CURRENT_CONSERVATIVE_FALLBACK"} for row in rows)
    assert load("roles")["selected_role"] is None


def test_berger_s3_is_not_automatically_relabelled_as_s7():
    rows = {row["role"]: row for row in load("roles")["rows"]}
    assert rows["S3 fiber of S3->S7->S4"]["status"] == "VIABLE_TOPOLOGY_REDUCTION_BLOCKED"
    assert "generic Berger squashing requires" in rows["S3 fiber of S3->S7->S4"]["metric_relation"]
    assert rows["canonical spatial slice"]["status"] == "REJECTED_AS_CURRENT_CANONICAL_ROLE"
    assert rows["unrelated proxy geometry"]["status"] == "CURRENT_CONSERVATIVE_FALLBACK"


def test_pullback_vertical_restriction_and_pushforward_are_not_conflated():
    payload = load("metric")
    assert payload["relations_not_conflated"] == ["g_Berger=i^*g_S7", "g_Berger=vertical metric", "g_Berger=effective pushforward metric"]
    assert payload["generic_berger_case"]["generic_pullback_proved"] is False
    assert payload["measure_normalization_proved"] is False
    assert payload["hodge_relation_proved"] is False


def test_standard_round_fiber_check_does_not_select_generic_berger_squashing():
    payload = load("metric")
    assert payload["standard_round_case"]["volume_check"] == "Vol(S7)=Vol(S4_radius_half)Vol(S3)=pi^4 L^7/3"
    assert payload["generic_berger_case"]["equals_round_pullback"] == "only at the round specialization with compatible normalization"


def test_required_maps_separate_topology_from_missing_reduction():
    rows = {row["name"]: row for row in load("maps")["maps"]}
    assert rows["Hopf projection"]["status"] == "EXACT_TOPOLOGY"
    assert rows["fiber embedding"]["status"] == "EXACT_AFTER_BASEPOINT"
    assert rows["invariant-mode projection"]["status"] == "MISSING"
    assert rows["action reduction"]["status"] == "MISSING"
    assert load("maps")["reduction_complete"] is False


def test_mode_correspondence_requires_representation_measure_domain_and_operator():
    payload = load("modes")
    assert payload["numeric_eigenvalue_matching_sufficient"] is False
    assert payload["representation_compatibility_required"] is True
    assert payload["measure_normalization_required"] is True
    assert payload["operator_compatibility_required"] is True
    assert payload["branching_map"] is None
    assert payload["target"]["status"] == "lower-dimensional proxy until mapped"


def test_parent_to_v5_map_does_not_reverse_engineer_reduced_coefficients():
    payload = load("action")
    assert payload["reverse_engineering_used"] is False
    assert payload["A_ST_minus_2_used_as_parent_target"] is False
    assert payload["G_ST_8_used_as_parent_target"] is False
    assert {row["sector"] for row in payload["rows"]} == {"boundary geometry", "gauge", "fermion", "scalar/topographic", "charged current", "neutral response", "scale/RG", "recycling"}
    assert all(row["v5_values_used_as_parent_input"] is False for row in payload["rows"])


def test_reduction_blockers_and_exact_next_theorem_are_explicit():
    payload = load("blockers")
    assert payload["status"] == "BHSM_B8_S7_TO_BERGER_S3_REDUCTION_BLOCKED"
    assert len(payload["blockers"]) == 11
    assert payload["round_fiber_topology_available"] is True
    assert payload["generic_berger_metric_derived"] is False
    assert payload["consistent_truncation_derived"] is False
    assert payload["action_reduction_derived"] is False
    assert payload["exact_next_theorem"].endswith("v5 coefficient map")


def test_roadmap_starts_with_bridge_after_firewall_and_full_bhsm_stays_open():
    payload = load("roadmap")
    assert payload["steps"][0]["complete"] is True
    assert payload["steps"][1]["step"] == "derive B8/S7-to-Berger-S3 reduction"
    assert payload["established_physics_must_be_rediscovered"] is False
    assert payload["completion_gate_status"] == "FULL_BHSM_NOT_COMPLETE"


def test_hidden_input_audit_has_no_measured_inputs_or_observable_changes():
    payload = load("audit")
    assert payload["status"] == "NO_NEW_HIDDEN_PHYSICAL_INPUTS"
    assert "measured masses" in payload["not_used"]
    assert "measured gauge couplings" in payload["not_used"]
    assert "absolute length or energy scale" in payload["not_used"]
    assert payload["observable_calculation_changed"] is False
    assert payload["historical_artifacts_rewritten"] is False


def test_cli_json_and_markdown():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    command = [sys.executable, "-m", "bhsm.interface", "correspondence-novelty-firewall-status"]
    result = subprocess.run(command + ["--format", "json"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["primary_result"] == "BHSM_CORRESPONDENCE_NOVELTY_FIREWALL_DERIVED"
    markdown = subprocess.run(command + ["--format", "markdown"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert "BHSM v6.0.6 Correspondence" in markdown.stdout


def test_public_ledgers_preserve_claim_boundary_and_stop_condition():
    text = public_text()
    for required in ["BHSM_CORRESPONDENCE_NOVELTY_FIREWALL_DERIVED", "BHSM_B8_S7_TO_BERGER_S3_REDUCTION_BLOCKED", "FULL_BHSM_NOT_COMPLETE", "correspondence-novelty-firewall-status"]:
        assert required in text
    forbidden = ["BHSM_GENERAL_ENERGY_GEOMETRY_ENVELOPMENT_DERIVED", "particle objecthood is derived", "absolute scale is generated", "full BHSM completion is achieved"]
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_logic_are_unchanged():
    for relative, digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
