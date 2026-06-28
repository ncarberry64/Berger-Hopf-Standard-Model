import hashlib, json
from pathlib import Path
from bhsm.interface.gallery import build_prediction_gallery

ROOT=Path(__file__).resolve().parents[1]

def test_default_gallery_contents_and_boundaries():
    g=build_prediction_gallery(); rows={e.entry_key:e for e in g.entries}
    for key in ("W_boson","electron_neutrino","CKM_matrix_BHSM","PMNS_matrix_BHSM","charged_boundary_response_matrix","neutral_operator_kernel_BH","cp_holonomy_phase_attachment","feynrules_minimal_model","ufo_export","madgraph_smoke_test"):
        assert key in rows
    assert rows["W_boson"].independent_prediction is False
    assert rows["electron_neutrino"].comparison_kind=="upper_limit"
    assert rows["charged_boundary_response_matrix"].category=="conditional_theorem"
    assert rows["cp_holonomy_phase_attachment"].category=="artifact_backed_constraint"
    assert rows["ufo_export"].category=="runtime_disabled_gate"
    assert "template_speculative_mode" not in rows

def test_gallery_artifacts_parse_and_match():
    for name in ("manifest","table","status_counts","plot_manifest"):
        assert json.loads((ROOT/f"artifacts/BHSM_prediction_gallery_{name}_v0_2.json").read_text())
    artifact=json.loads((ROOT/"artifacts/BHSM_prediction_gallery_table_v0_2.json").read_text())
    assert artifact==build_prediction_gallery().to_dict()

def test_frozen_predictions_unchanged():
    expected={"docs/frozen_predictions.md":"9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4","docs/frozen_predictions.json":"f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7"}
    for p,h in expected.items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h

def test_gallery_claim_warnings_and_readme_are_present():
    policy=(ROOT/"docs/prediction_gallery_claim_policy.md").read_text()
    for warning in (
        "Gallery entries are status summaries, not empirical validation claims.",
        "Live PDG values are comparison references only and are never BHSM derivation inputs.",
        "Speculative candidates are disabled by default and are not production predictions.",
        "Theorem-blocker closure attempts do not promote a blocker unless an explicit theorem artifact supports closure.",
        "Plots summarize registry status; they do not validate BHSM empirically.",
    ): assert warning in policy
    assert "prediction gallery" in (ROOT/"README.md").read_text().lower()
