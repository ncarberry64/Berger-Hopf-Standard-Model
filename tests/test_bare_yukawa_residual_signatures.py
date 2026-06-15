from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_bare_yukawa_residual_autopsy import build_autopsy_payload  # noqa: E402


def test_worst_residuals_and_sign_pattern_are_reported() -> None:
    autopsy = build_autopsy_payload()["residual_autopsy"]
    worst = autopsy["worst_residuals"]
    assert [row["ratio_name"] for row in worst[:3]] == ["e/tau", "d/b", "c/t"]
    assert worst[0]["sign"] == "overpredict"
    assert worst[2]["sign"] == "underpredict"

    sign_pattern = autopsy["sign_pattern"]
    assert sign_pattern["mu/tau"] == "overpredict"
    assert sign_pattern["e/tau"] == "overpredict"
    assert sign_pattern["c/t"] == "underpredict"
    assert sign_pattern["u/t"] == "underpredict"
    assert sign_pattern["s/b"] == "overpredict"
    assert sign_pattern["d/b"] == "overpredict"


def test_residual_concentration_identifies_lepton_and_light_mode_pressure() -> None:
    autopsy = build_autopsy_payload()["residual_autopsy"]
    assert autopsy["concentration"]["largest_sector"] == "charged_lepton"
    assert autopsy["concentration"]["largest_mode_class"] == "light"
    assert autopsy["concentration"]["quark_scheme_sensitive"] is True
    assert autopsy["concentration"]["pure_fiber_rows"][0]["ratio_name"] == "c/t"


def test_response_factors_do_not_close_the_universal_gate() -> None:
    payload = build_autopsy_payload()
    raw = next(
        row
        for row in payload["variant_results"]
        if row["variant_id"] == "A_raw" and row["response_scenario"] == "current_candidate_responses"
    )
    assert raw["verdict"] == "BARE_YUKAWA_INVARIANT_VARIANT_TIER_C_ORDERING_ONLY"
    assert raw["response_improvement_delta"] < 0.0
    assert raw["variant_improvement_delta"] < 0.1


def test_residual_autopsy_documentation_mentions_fourth_order_and_focusing_result() -> None:
    text = (ROOT / "theory" / "bare_yukawa_residual_autopsy.md").read_text(
        encoding="utf-8"
    )
    assert "beta_eff=0" in text
    assert "xi=0" in text
    assert "fourth-order and focusing terms are not numerically favored" in text
