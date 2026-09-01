import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP
from state_ontology import (
    StateCategory,
    build_state_ontology_ledger,
    classify_state,
    composite_qcd_state_ledger,
    export_state_ontology_json,
    export_state_ontology_markdown,
    internal_mode_state_ledger,
    is_forbidden_extra_light_state,
    is_observable_particle,
    is_virtual_or_dressing,
    standard_model_state_ledger,
    state_ontology_report,
    virtual_environment_state_ledger,
)


def _states_by_id(states):
    return {state.id: state for state in states}


def _classifications_by_id(ledger):
    return {classification.state_id: classification for classification in ledger.classifications}


def test_standard_model_and_composite_examples_are_observable_states():
    sm_states = _states_by_id(standard_model_state_ledger())
    composite_states = _states_by_id(composite_qcd_state_ledger())

    assert classify_state(sm_states["electron"]).category == StateCategory.ON_SHELL_SM_PARTICLE
    assert classify_state(sm_states["charm_quark_field"]).category == StateCategory.ON_SHELL_SM_PARTICLE
    assert is_observable_particle(sm_states["electron"]) is True
    assert is_observable_particle(sm_states["charm_quark_field"]) is True

    for state_id in ("proton", "neutron", "pion"):
        state = composite_states[state_id]
        assert classify_state(state).category == StateCategory.COMPOSITE_QCD_STATE
        assert is_observable_particle(state) is True


def test_virtual_and_dressing_examples_are_not_new_observable_particles():
    states = _states_by_id(virtual_environment_state_ledger())

    charm_loop = states["temporary_charm_sector_dressing"]
    z_virt = states["z_virt_u2_half"]

    assert classify_state(charm_loop).category == StateCategory.VIRTUAL_EXCITATION
    assert classify_state(z_virt).category == StateCategory.DRESSING_CONTRIBUTION
    assert is_virtual_or_dressing(charm_loop) is True
    assert is_virtual_or_dressing(z_virt) is True
    assert is_observable_particle(charm_loop) is False
    assert is_observable_particle(z_virt) is False
    assert is_forbidden_extra_light_state(z_virt) is False


def test_internal_modes_are_separated_from_forbidden_and_lifted_states():
    states = _states_by_id(internal_mode_state_ledger())

    internal_mode = states["lepton_internal_mode_5_2"]
    forbidden = states["non_sm_light_internal_mode"]
    heavy = states["heavy_complement_mode"]
    screened = states["screened_topographic_scalar"]

    assert classify_state(internal_mode).category == StateCategory.INTERNAL_BERGER_HOPF_MODE
    assert is_observable_particle(internal_mode) is False
    assert classify_state(forbidden).category == StateCategory.FORBIDDEN_EXTRA_LIGHT_STATE
    assert is_forbidden_extra_light_state(forbidden) is True
    assert classify_state(heavy).category == StateCategory.HEAVY_LIFTED_STATE
    assert is_forbidden_extra_light_state(heavy) is False
    assert classify_state(screened).category == StateCategory.SCREENED_TOPOGRAPHIC_STATE
    assert is_forbidden_extra_light_state(screened) is False


def test_ontology_ledger_contains_rules_r1_to_r8_and_explicit_categories():
    ledger = build_state_ontology_ledger()
    classifications = _classifications_by_id(ledger)

    assert {rule.id for rule in ledger.rules} == {f"R{idx}" for idx in range(1, 9)}
    assert all(rule.statement for rule in ledger.rules)
    assert all(rule.limitations for rule in ledger.rules)
    assert all(classification.limitations for classification in ledger.classifications)
    assert ledger.theorem_complete is False
    assert classifications["non_sm_light_internal_mode"].forbidden_extra_light is True
    assert classifications["z_virt_u2_half"].virtual_or_dressing is True


def test_state_ontology_report_preserves_claim_boundary():
    report = state_ontology_report()

    assert report.theorem_complete is False
    assert "not automatically new observable particles" in report.claim_boundary
    assert "Extra observable light states remain forbidden" in report.claim_boundary
    assert report.category_counts[StateCategory.ON_SHELL_SM_PARTICLE.value] >= 1
    assert report.category_counts[StateCategory.DRESSING_CONTRIBUTION.value] >= 1
    assert report.category_counts[StateCategory.FORBIDDEN_EXTRA_LIGHT_STATE.value] >= 1


def test_state_ontology_does_not_import_empirical_or_residual_machinery():
    root = Path(__file__).parents[1]
    source = root.joinpath("src", "state_ontology.py").read_text()
    forbidden = (
        "EMPIRICAL_MASS_RATIOS",
        "from ckm",
        "compute_ckm",
        "from pmns",
        "compute_pmns",
        "mass_ratio(",
        "build_prediction_ledger",
        "build_residual_audit",
    )

    assert all(token not in source for token in forbidden)


def test_state_ontology_does_not_change_frozen_predictions():
    bare_before = build_bhsm_bare_v1()
    dressed_before = build_bhsm_dressed_v1_candidate()

    state_ontology_report()

    bare_after = build_bhsm_bare_v1()
    dressed_after = build_bhsm_dressed_v1_candidate()
    comparison = compare_bhsm_v1_branches()

    assert bare_before.outputs == bare_after.outputs
    assert dressed_before.outputs == dressed_after.outputs
    assert isclose(bare_after.version.geometry_a, 1.157054135733433, rel_tol=0.0, abs_tol=1e-15)
    assert isclose(bare_after.version.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15)
    assert [row for row in comparison["rows"] if row["changed"]] == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]


def test_state_ontology_exports_generate_cleanly(tmp_path):
    md_path = tmp_path / "state_ontology.md"
    json_path = tmp_path / "state_ontology.json"

    export_state_ontology_markdown(md_path)
    export_state_ontology_json(json_path)

    md_text = md_path.read_text()
    data = json.loads(json_path.read_text())
    assert "BHSM v1.3F State Ontology" in md_text
    assert "FORBIDDEN_EXTRA_LIGHT_STATE" in md_text
    assert data["theorem_complete"] is False
    assert data["ledger"]["theorem_complete"] is False


def test_generated_state_ontology_artifacts_are_present_and_conservative():
    root = Path(__file__).parents[1]
    artifact_paths = (
        root / "theory" / "bhsm_state_ontology.md",
        root / "theory" / "bhsm_state_ontology.json",
        root / "manuscript" / "v1_3f_state_ontology_note.md",
        root / "notebooks" / "28_state_ontology.ipynb",
    )

    for path in artifact_paths:
        assert path.exists(), path

    md_text = artifact_paths[0].read_text()
    note_text = artifact_paths[2].read_text()
    data = json.loads(artifact_paths[1].read_text())

    assert "not automatically new observable particles" in md_text
    assert "FORBIDDEN_EXTRA_LIGHT_STATE" in md_text
    assert "does not prove the full `H_T` no-extra-light theorem" in note_text
    assert data["theorem_complete"] is False
    assert "fully proven" not in md_text.lower()
    assert "complete derivation" not in md_text.lower()
