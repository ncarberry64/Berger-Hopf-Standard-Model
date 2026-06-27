import json
from pathlib import Path

from bhsm.interface.artifact_report import WARNINGS, build_artifact_prediction_report

ROOT = Path(__file__).resolve().parents[1]


def test_artifact_report_separates_value_classes_and_keeps_blockers_open():
    report = build_artifact_prediction_report(repository=ROOT)
    assert report.artifact_backed_values
    assert report.interface_default_values
    assert report.reference_comparison_values == []
    assert report.calibration_inputs[0]["role"] == "calibration_anchor"
    assert report.empirical_derivation_inputs_used is False
    assert report.reference_values_used_as_derivation_inputs is False
    assert report.frozen_predictions_changed is False
    assert set(("x_ch_production_vertex", "neutrino_physical_basis_scale", "cp_o_int_standalone_attachment")) <= set(report.missing_callables)
    assert tuple(report.warnings) == WARNINGS


def test_report_artifact_and_claim_policy_parse():
    report = json.loads((ROOT / "artifacts/BHSM_artifact_backed_prediction_report_v0_3.json").read_text(encoding="utf-8"))
    policy = json.loads((ROOT / "artifacts/BHSM_artifact_adapter_claim_policy_v0_3.json").read_text(encoding="utf-8"))
    assert report["empirical_derivation_inputs_used"] is False
    assert report["reference_values_used_as_derivation_inputs"] is False
    assert policy["theorem_blocker_policy"]


def test_required_warning_language_and_readme_section():
    combined = "\n".join((ROOT / "docs" / name).read_text(encoding="utf-8") for name in ("artifact_backed_prediction_adapters.md", "artifact_backed_claim_policy.md"))
    for warning in WARNINGS:
        assert warning in combined
    assert "## Artifact-backed prediction adapters" in (ROOT / "README.md").read_text(encoding="utf-8")
