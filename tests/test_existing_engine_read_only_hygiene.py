from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_existing_engine_branch_threshold import (  # noqa: E402
    build_payload,
    read_only_ckm_outputs,
    read_only_existing_outputs,
)


def test_read_only_existing_outputs_include_required_mass_rows() -> None:
    rows = {row["ratio_name"]: row for row in read_only_existing_outputs(ROOT)}
    assert set(rows) == {"mu/tau", "e/tau", "c/t", "u/t", "s/b", "d/b"}
    assert rows["c/t"]["scheme_sensitive"] is True
    assert rows["mu/tau"]["scheme_sensitive"] is False
    assert rows["c/t"]["official_or_existing_dressed_candidate_prediction"] == 0.004155250277034144


def test_read_only_ckm_rows_are_not_used_for_mass_fit() -> None:
    rows = read_only_ckm_outputs(ROOT)
    assert rows
    assert rows[0]["quantity"] == "sin_theta_13"
    assert rows[0]["used_in_mass_engine_fit"] is False
    assert rows[0]["changed"] is False


def test_existing_outputs_match_frozen_json_for_quark_rows() -> None:
    frozen = json.loads((ROOT / "docs" / "frozen_predictions.json").read_text())
    rows = {row["ratio_name"]: row for row in read_only_existing_outputs(ROOT)}
    for ratio in ("c/t", "u/t", "s/b", "d/b"):
        assert rows[ratio]["official_or_existing_bare_prediction"] == frozen["outputs"][ratio]["bare"]
        assert (
            rows[ratio]["official_or_existing_dressed_candidate_prediction"]
            == frozen["outputs"][ratio]["dressed_candidate"]
        )


def test_payload_declares_read_only_and_no_mutation() -> None:
    payload = build_payload(ROOT)
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert "existing/frozen values are read-only" in payload["notes"]
    assert "no official predictions changed" in payload["notes"]
