from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_minimal_branch_threshold import build_payload, read_only_targets  # noqa: E402


def test_read_only_targets_match_existing_sources() -> None:
    targets = {row["ratio_name"]: row for row in read_only_targets(ROOT)}
    assert set(targets) == {"mu/tau", "e/tau", "c/t", "u/t", "s/b", "d/b"}
    assert targets["c/t"]["official_or_existing_bare_prediction"] == 0.008310500554068288
    assert targets["c/t"]["official_or_existing_dressed_candidate_prediction"] == 0.004155250277034144
    assert targets["mu/tau"]["reference_scheme_note"] == "scheme-stable for this audit"
    assert targets["u/t"]["reference_scheme_note"] == "quark ratios are scheme-sensitive"


def test_branch_feature_table_contains_required_mode_features() -> None:
    row = build_payload(ROOT)["branch_feature_table"][0]
    required = {
        "ratio_name",
        "sector",
        "q",
        "j",
        "k",
        "N",
        "Omega_f",
        "Omega_star",
        "branch_rank_by_N",
        "branch_role",
        "mode_type",
        "fiber_fraction",
        "base_fraction",
        "cross_term",
        "orientation_product",
        "lower_doublet_projector",
        "colored_lift_exponent",
    }
    assert required <= set(row)


def test_quark_scheme_warnings_are_preserved() -> None:
    payload = build_payload(ROOT)
    quark_rows = [row for row in payload["read_only_existing_outputs"] if row["sector"] in {"up", "down"}]
    assert quark_rows
    assert all(row["scheme_sensitive"] is True for row in quark_rows)
    assert "quark ratios are scheme-sensitive where applicable" in payload["notes"]


def test_official_frozen_values_remain_read_only() -> None:
    frozen = json.loads((ROOT / "docs" / "frozen_predictions.json").read_text())
    assert frozen["branches"]["bare"] == "BHSM_BARE_V1"
    assert frozen["branches"]["dressed_candidate"] == "BHSM_DRESSED_V1_CANDIDATE"
    assert frozen["dressing_rule"]["affects_only"] == "c/t"
    assert build_payload(ROOT)["official_predictions_changed"] is False
