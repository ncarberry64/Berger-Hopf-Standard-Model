from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_full_bhsm_completion import (  # noqa: E402
    BRANCH,
    VERDICT_LABELS,
    build_results_payload,
    export_outputs,
)


def test_full_bhsm_completion_json_schema() -> None:
    payload = export_outputs(ROOT)
    parsed = json.loads(
        (ROOT / "theory" / "full_bhsm_completion_results.json").read_text(
            encoding="utf-8"
        )
    )
    assert parsed == payload
    assert parsed["status"] == "candidate_only"
    assert parsed["branch"] == BRANCH
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["full_bhsm_candidate_complete"] is True
    assert parsed["full_bhsm_proven"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["dark_matter_solved"] is False
    assert parsed["official_mass_formula_changed"] is False
    assert parsed["verdict_labels"] == VERDICT_LABELS


def test_required_full_completion_files_exist() -> None:
    export_outputs(ROOT)
    required = [
        "full_bhsm_completion_v1_candidate.md",
        "full_bhsm_master_equation_map.md",
        "full_bhsm_claim_status_matrix.md",
        "full_bhsm_open_proof_obligations.md",
        "full_bhsm_empirical_gate_plan.md",
        "full_bhsm_completion_results.json",
        "full_bhsm_candidate_release_notes.md",
    ]
    for name in required:
        assert (ROOT / "theory" / name).exists(), name


def test_candidate_utility_does_not_compute_official_predictions() -> None:
    source = (ROOT / "theory" / "candidate_full_bhsm_completion.py").read_text(
        encoding="utf-8"
    )
    assert "BHSM_BARE_V1" not in source
    assert "BHSM_DRESSED_V1_CANDIDATE" not in source
    assert "prediction_ledger" not in source
    assert "frozen_predictions.json" not in source
