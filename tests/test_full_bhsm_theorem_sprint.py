import json
from pathlib import Path

from full_bhsm_theorem_final_decision import build_full_bhsm_theorem_final_decision
from full_bhsm_theorem_sprint import (
    export_full_bhsm_sprint_result_json,
    export_full_bhsm_sprint_result_markdown,
    export_full_bhsm_sprint_status_json,
    build_full_bhsm_sprint_status,
)


def test_full_bhsm_sprint_stops_at_single_named_gap():
    status = build_full_bhsm_sprint_status()
    decision = build_full_bhsm_theorem_final_decision()

    assert status.final_result == "STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP"
    assert decision.final_result == "STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP"
    assert status.exact_blocker == "INDEX_THEOREM_FINAL_GAP"
    assert status.final_paper_allowed is False
    assert decision.final_paper_allowed is False
    assert status.frozen_outputs_changed is False


def test_sprint_exports_only_allowed_outputs(tmp_path):
    status_json = tmp_path / "status.json"
    result_json = tmp_path / "result.json"
    result_md = tmp_path / "result.md"

    export_full_bhsm_sprint_status_json(status_json)
    export_full_bhsm_sprint_result_json(result_json)
    export_full_bhsm_sprint_result_markdown(result_md)

    assert json.loads(status_json.read_text())["final_result"] == "STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP"
    assert json.loads(result_json.read_text())["exact_blocker"] == "INDEX_THEOREM_FINAL_GAP"
    assert "INDEX_THEOREM_FINAL_GAP" in result_md.read_text()


def test_requested_sprint_output_files_exist():
    root = Path(__file__).parents[1]
    expected = (
        "theory/full_bhsm_sprint_status.json",
        "theory/full_bhsm_sprint_result.md",
        "theory/full_bhsm_sprint_result.json",
    )
    missing = [path for path in expected if not root.joinpath(path).exists()]
    assert missing == []


def test_sprint_modules_do_not_import_empirical_machinery():
    root = Path(__file__).parents[1]
    source = "\n".join(
        root.joinpath("src", name).read_text()
        for name in (
            "full_bhsm_theorem_sprint.py",
            "ht_lower_bound_transfer.py",
            "index_theorem_hardening.py",
            "mirror_exclusion_hardening.py",
            "full_ht_theorem_final.py",
            "full_bhsm_theorem_final_decision.py",
        )
    )
    forbidden = (
        "from prediction_ledger",
        "import prediction_ledger",
        "from residual_audit",
        "import residual_audit",
        "EMPIRICAL_MASS_RATIOS",
        "compute_ckm",
        "compute_pmns",
        "relative_error",
    )
    assert all(token not in source for token in forbidden)
