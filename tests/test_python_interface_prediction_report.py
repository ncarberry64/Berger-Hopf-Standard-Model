from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.report import (
    CALIBRATION_WARNING,
    NEUTRINO_WARNING,
    OPEN_THEOREM_WARNING,
    RUNTIME_WARNING,
    build_prediction_report,
)

ROOT = Path(__file__).resolve().parents[1]


def test_report_preserves_calibration_and_upper_limit_semantics() -> None:
    report = build_prediction_report(
        anchor_particle="W_boson",
        particles=("W_boson", "electron_neutrino"),
        include_open_theorem_entries=True,
    ).to_dict()
    statuses = {row["particle_key"]: row["status"] for row in report["registry_statuses"]}
    assert statuses["W_boson"] == "CALIBRATION_ANCHOR_NOT_INDEPENDENT_PREDICTION"
    assert statuses["electron_neutrino"] == "MODEL_PREDICTION_GIVEN_CALIBRATION"
    assert report["comparisons"][1]["reference"]["reference_kind"] == "upper_limit"
    assert {CALIBRATION_WARNING, NEUTRINO_WARNING, OPEN_THEOREM_WARNING, RUNTIME_WARNING} <= set(report["warnings"])
    assert report["empirical_derivation_inputs_used"] is False
    assert report["internet_required"] is False
    assert report["pdg_dependency_required"] is False
    assert report["claims_of_empirical_validation"] is False


def test_report_marks_blockers_and_runtime_gates() -> None:
    report = build_prediction_report(include_open_theorem_entries=True).to_dict()
    statuses = {row["particle_key"]: row["status"] for row in report["registry_statuses"]}
    assert statuses["charged_boundary_response_matrix"] == "OPEN_THEOREM_REQUIRED"
    assert statuses["neutral_operator_kernel_BH"] == "OPEN_THEOREM_REQUIRED"
    assert statuses["cp_holonomy_phase_attachment"] == "OPEN_THEOREM_REQUIRED"
    assert statuses["feynrules_minimal_model"] == "DISABLED_UNTIL_RUNTIME_VALIDATED"
    assert statuses["ufo_export"] == "DISABLED_UNTIL_RUNTIME_VALIDATED"
    assert statuses["madgraph_smoke_test"] == "DISABLED_UNTIL_RUNTIME_VALIDATED"

    direct = build_prediction_report(
        particles=("charged_boundary_response_matrix", "ufo_export"),
        include_open_theorem_entries=False,
    ).to_dict()
    assert OPEN_THEOREM_WARNING in direct["warnings"]
    assert RUNTIME_WARNING in direct["warnings"]


def test_report_artifact_matches_runtime_output() -> None:
    artifact = json.loads((ROOT / "artifacts/BHSM_prediction_report_example_v0_1.json").read_text())
    runtime = build_prediction_report(include_open_theorem_entries=True).to_dict()
    assert artifact == runtime


def test_required_warnings_are_documented() -> None:
    text = (ROOT / "docs/python_prediction_claim_policy.md").read_text()
    for warning in (CALIBRATION_WARNING, NEUTRINO_WARNING, OPEN_THEOREM_WARNING, RUNTIME_WARNING):
        assert warning in text
    assert "## Computational Quickstart" in (ROOT / "README.md").read_text()
