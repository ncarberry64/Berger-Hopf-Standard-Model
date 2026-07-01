import json, subprocess
from pathlib import Path
from bhsm.interface.ckm_boundary_measure_normalization import build_boundary_measure_normalization_report

ROOT = Path(__file__).resolve().parents[1]
FILES = ("BHSM_ckm_boundary_measure_source_v2_8.json", "BHSM_ckm_coefficient_normalization_v2_8.json", "BHSM_ckm_action_measure_coefficient_pair_v2_8.json", "BHSM_normalized_ckm_action_candidate_v2_8.json", "BHSM_ckm_projector_sandwich_requirement_v2_8.json", "BHSM_ckm_paired_normalization_rule_v2_8.json", "BHSM_ckm_transport_space_blocker_v2_8.json")

def test_artifacts_and_claim_guards():
    for name in FILES:
        p = json.loads((ROOT / "artifacts" / name).read_text())
        assert p["empirical_inputs_used"] is False
        assert p["frozen_predictions_modified"] is False
    report = build_boundary_measure_normalization_report()
    assert len(report["required_boundary_statements"]) == 5

def test_protected_files_unchanged():
    protected = ("docs/frozen_predictions.md", "docs/frozen_predictions.json", "src/bhsm_model.py", "src/bhsm/interface/predictions.py", "artifacts/CKM_no_fit_operator_output_v1.json")
    r = subprocess.run(["git", "diff", "--name-only", "--", *protected], cwd=ROOT, capture_output=True, text=True, check=True)
    assert r.stdout.strip() == ""
