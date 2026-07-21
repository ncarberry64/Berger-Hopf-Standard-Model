import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface import minimal_parent_theory_kill_test as mp

ROOT=Path(__file__).resolve().parents[1]
ARTIFACTS=ROOT/"artifacts"
DOC=ROOT/"docs"/"bhsm_minimal_parent_theory_kill_test_v6_0_5.md"
EXPECTED_HASHES={
    "docs/frozen_predictions.md":"9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json":"f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py":"8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}

def load(key): return json.loads((ARTIFACTS/mp.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))

def focused_text():
    paths=[DOC,ROOT/"STATUS.md",ROOT/"CLAIMS.md",ROOT/"ARTIFACT_INDEX.md",ROOT/"CLI_REFERENCE.md"]+[ARTIFACTS/name for name in mp.ARTIFACT_FILES.values()]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)

def test_package_has_one_immutable_freeze_and_claim_guards():
    assert len(mp.ARTIFACT_FILES)==10
    assert len(mp.FREEZE_ID)==64
    for key in mp.ARTIFACT_FILES:
        payload=load(key)
        assert payload["version"]=="v6.0.5",key
        assert payload["primary_result"]=="BHSM_MINIMAL_PARENT_THEORY_FAILS_PHYSICALITY_TRIGGER"
        assert payload["coherent_trigger_result"]=="BHSM_MINIMAL_FREE_SCALAR_COHERENT_TRIGGER_FAILED"
        assert payload["harmonic_envelopment_result"]=="BHSM_HARMONIC_ENVELOPMENT_SELECTION_NOT_DERIVED"
        assert payload["general_envelopment_result"]=="BHSM_GENERAL_ENERGY_GEOMETRY_ENVELOPMENT_REMAINS_OPEN"
        assert payload["freeze_id"]==mp.FREEZE_ID
        assert payload["post_freeze_terms_added"] is False
        assert payload["alternative_parent_fields_searched"] is False
        assert payload["empirical_inputs_used"] is False
        assert payload["absolute_unit_generated"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False

def test_freeze_id_is_deterministic_and_covers_exact_specification():
    expected=hashlib.sha256(mp.deterministic_json(mp.FREEZE_SPEC).encode("utf-8")).hexdigest()
    assert mp.FREEZE_ID==expected
    payload=load("freeze")
    assert payload["freeze"]==mp.FREEZE_SPEC
    assert payload["status"]=="IMMUTABLE_PROVISIONAL_THEORY_FROZEN"

def test_freeze_explicitly_selects_every_required_choice():
    required={"parent_domain","signature","parent_family","energy_carrier","sigma_domain","action","sigma_coupling","boundary_conditions","raw_primitives","terms_may_be_added_after_freeze","alternative_fields_may_be_searched"}
    assert set(mp.FREEZE_SPEC)==required
    assert mp.FREEZE_SPEC["parent_family"].startswith("P1")
    assert mp.FREEZE_SPEC["energy_carrier"]=="one real massless scalar chi"
    assert mp.FREEZE_SPEC["terms_may_be_added_after_freeze"] is False

def test_materialization_is_deterministic():
    built=mp.build_artifact_payloads(ROOT)
    for key,name in mp.ARTIFACT_FILES.items():
        assert (ARTIFACTS/name).read_text(encoding="utf-8")==mp.deterministic_json(built[key])

@pytest.mark.parametrize("level,value",[(0,0),(1,7),(4,40),(10,160)])
def test_frozen_round_s7_spectrum(level,value):
    assert mp.s7_eigenvalue(level,1.0)==value

def test_invalid_spectrum_inputs_are_rejected():
    with pytest.raises(ValueError): mp.s7_eigenvalue(-1,1)
    with pytest.raises(ValueError): mp.s7_eigenvalue(1,0)

def test_kill_1_parent_field_exists_at_sigma_zero():
    action=load("action")
    spectrum=load("spectrum")
    assert action["kill_tests"]["field_exists_at_sigma_zero"]=="PASS"
    assert spectrum["field_at_sigma_zero"] is True

def test_kill_2_parent_action_is_stipulated_not_geometrically_derived():
    freeze=load("freeze")
    action=load("action")
    assert freeze["derived_by_geometry"] is False
    assert action["kill_tests"]["action_follows_from_geometric_reduction"]=="FAIL"
    assert action["geometric_reduction_source"].startswith("none")

def test_kill_3_stress_is_defined_and_on_shell_conserved_within_frozen_action():
    action=load("action")
    assert "T_AB^chi" in action["chi_stress_at_sigma_zero"]
    assert "conserved" in action["stress_conservation"]
    assert action["kill_tests"]["conserved_stress_well_defined"]=="PASS_WITHIN_STIPULATED_ACTION"
    assert action["boundary_completion_new_primitive"] is False

def test_kill_4_free_carrier_has_no_nonlinear_self_interaction():
    payload=load("interaction")
    assert payload["chi_action_at_sigma_zero"]=="purely quadratic"
    assert payload["third_chi_derivative"]==0
    assert payload["fourth_chi_derivative"]==0
    assert payload["kill_tests"]["action_derived_nonlinear_parent_interaction"]=="FAIL"

def test_mixed_tensor_does_not_phase_lock_free_parent_modes():
    payload=load("interaction")
    assert "sigma delta sigma delta chi delta chi" in payload["mixed_tensor"]
    assert "does not phase-lock" in payload["mixed_tensor_role"]

def test_kill_5_octave_commensurability_has_no_nonzero_parent_channel():
    payload=load("interaction")
    assert "l=10" in payload["representation_allowed_commensurability"]
    assert payload["nonzero_resonant_parent_channel"] is False
    assert payload["kill_tests"]["nonzero_representation_allowed_resonant_channel"]=="FAIL"

def test_sigma_quadratic_shift_is_exact_but_lorentzian_sign_indefinite():
    assert mp.effective_sigma_quadratic(2,3,-1,4)==-10
    payload=load("shift")
    assert payload["sigma_shift"]=="Delta H_sigma=Zchi g (nabla chi)^2"
    assert "indefinite" in payload["lorentzian_sign"]
    assert payload["coupling_sign"]=="g is an unsourced primitive"

def test_kill_6_no_equal_energy_negative_coherent_shift_is_derived():
    payload=load("shift")
    assert payload["delta_lambda_coherent_minus_incoherent"] is None
    assert "initial data" in payload["local_interference"]
    assert payload["kill_test"]=="FAIL"

def test_kill_7_nonzero_sigma_branch_is_only_conditional():
    branch=mp.sigma_branches(-2,8)
    assert branch["nonzero"]==pytest.approx([-0.5,0.5])
    assert branch["formed_hessian"]==4
    assert mp.sigma_branches(2,8)["nonzero"]==[]
    with pytest.raises(ValueError): mp.sigma_branches(-1,0)
    payload=load("branch")
    assert payload["stable_nonlinear_branch_derived"] is False
    assert payload["kill_test"]=="CONDITIONAL_FORMULA_TRIGGER_FAILS"

def test_kill_8_coupled_hessian_spectrum_is_not_acceptable_or_complete():
    payload=load("hessian")
    assert payload["gauge_quotient"]=="missing"
    assert payload["negative_modes"] is None
    assert payload["acceptable_physical_spectrum"] is False
    assert payload["kill_test"]=="FAIL"

def test_time_dependent_interference_requires_floquet_problem():
    assert load("hessian")["Floquet_problem"].startswith("required")

def test_kill_9_v5_reduction_is_not_recovered_or_reverse_engineered():
    payload=load("v5_map")
    assert payload["A_ST_minus_2"] is None
    assert payload["G_ST_8"] is None
    assert payload["sigma_half"] is None
    assert payload["reverse_engineering_used"] is False
    assert payload["kill_test"]=="FAIL"

def test_kill_10_primitive_count_is_exact_and_all_sources_remain_open():
    payload=load("primitives")
    assert payload["raw"]=={"dimensional":6,"dimensionless":1,"total":7}
    assert payload["field_normalized_count"]==5
    assert tuple(payload["field_normalized_combinations"])==mp.normalized_primitive_combinations()
    assert payload["internally_sourced_count"]==0
    assert payload["absolute_scale"] is None

def test_all_ten_kill_tests_are_present_once():
    rows=load("report")["kill_tests"]
    assert [row["id"] for row in rows]==list(range(1,11))
    assert sum("FAIL" in row["result"] for row in rows)>=6

def test_first_decisive_failure_is_free_carrier_nonlinearity_not_a_fitted_number():
    report=load("report")
    assert "free at sigma=0" in report["first_decisive_trigger_failure"]
    assert "no action-derived nonlinear" in report["first_decisive_trigger_failure"]

def test_failure_does_not_propose_replacement_candidate():
    report=load("report")
    assert report["alternative_candidate_proposed"] is False
    assert report["recommended_next_branch"] is None

def test_foundational_axiom_change_is_reported_explicitly():
    text=load("report")["foundational_axiom_that_must_change"]
    assert "free canonical energy carrier" in text
    assert "must be abandoned" in text
    assert "outside this frozen sprint" in text

def test_trigger_failure_is_scoped_and_general_envelopment_remains_open():
    report=load("report")
    assert report["failure_scope"]=="frozen free-scalar coherent sigma-transition trigger only"
    assert "transient free-scalar localized energy differentials" in report["not_falsified"]
    assert "General energy-geometry envelopment remains open" in report["central_answer"]

def test_project_ledgers_reject_overrestricted_physicality_doctrine():
    text=focused_text().lower()
    required=[
        "bhsm_minimal_free_scalar_coherent_trigger_failed",
        "bhsm_harmonic_envelopment_selection_not_derived",
        "bhsm_general_energy_geometry_envelopment_remains_open",
        "physicality is an action-supported localized or propagating",
        "transient localized energy differential",
    ]
    assert all(phrase in text for phrase in required)
    forbidden=[
        "general physicality failed",
        "envelopment requires harmonic coherence",
        "sigma != 0 is necessary for all physicality",
        "a free scalar cannot produce transient localized energy differentials",
    ]
    assert not any(phrase in text for phrase in forbidden)

def test_prior_v604_artifacts_are_not_rewritten():
    paths=list(ARTIFACTS.glob("*v6_0_4.json")); before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    mp.build_artifact_payloads(ROOT); after={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    assert paths and before==after

def test_cli_json_and_markdown():
    env={**os.environ,"PYTHONPATH":str(ROOT/"src")}; command=[sys.executable,"-m","bhsm.interface","minimal-parent-kill-status"]
    result=subprocess.run(command+["--format","json"],cwd=ROOT,env=env,check=True,capture_output=True,text=True)
    assert json.loads(result.stdout)["primary_result"]=="BHSM_MINIMAL_PARENT_THEORY_FAILS_PHYSICALITY_TRIGGER"
    markdown=subprocess.run(command+["--format","markdown"],cwd=ROOT,env=env,check=True,capture_output=True,text=True)
    assert "BHSM v6.0.5 Minimal Parent" in markdown.stdout

def test_public_ledgers_preserve_claim_boundary():
    text=focused_text()
    assert "BHSM_MINIMAL_PARENT_THEORY_FAILS_PHYSICALITY_TRIGGER" in text
    assert "minimal-parent-kill-status" in text
    assert "FULL_BHSM_NOT_COMPLETE" in text
    forbidden=["all parent theories are impossible","v6.0.5 derives physicality","absolute unit is generated","full BHSM completion is achieved"]
    assert not any(phrase in text for phrase in forbidden)

def test_frozen_predictions_and_official_logic_are_unchanged():
    for relative,digest in EXPECTED_HASHES.items(): assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest
