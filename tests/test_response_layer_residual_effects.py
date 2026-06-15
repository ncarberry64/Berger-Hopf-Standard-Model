from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_response_layer_decomposition import build_response_payload  # noqa: E402


def test_lepton_8_9_response_is_directionally_helpful_but_small() -> None:
    summary = build_response_payload()["response_effect_summary"]["lepton_8_9"]
    assert summary["mu_tau"]["improves"] is True
    assert summary["e_tau"]["improves"] is True
    assert summary["mu_tau"]["delta_abs_log_residual"] < 0
    assert summary["e_tau"]["delta_abs_log_residual"] < 0
    assert summary["directionally_suppresses_overpredictions"] is True


def test_up_half_response_worsens_c_t_underprediction() -> None:
    up_half = build_response_payload()["response_effect_summary"]["up_half"]
    assert up_half["c_t"]["bare_log_residual"] < 0
    assert up_half["c_t"]["scenario_log_residual"] < up_half["c_t"]["bare_log_residual"]
    assert up_half["c_t"]["improves"] is False
    assert up_half["worsens_existing_underprediction"] is True


def test_up_light_amplitude_worsens_u_t_underprediction() -> None:
    up_light = build_response_payload()["response_effect_summary"]["up_light_amplitude"]
    assert up_light["u_t"]["bare_log_residual"] < 0
    assert up_light["u_t"]["scenario_log_residual"] < up_light["u_t"]["bare_log_residual"]
    assert up_light["u_t"]["improves"] is False
    assert up_light["worsens_existing_underprediction"] is True


def test_current_bundled_responses_hurt_global_rms_and_are_mixed() -> None:
    payload = build_response_payload()
    current = payload["response_effect_summary"]["current_candidate_responses"]
    assert current["net_rms_delta_vs_bare"] > 0
    assert current["num_residuals_improved"] == 2
    assert current["num_residuals_worsened"] == 2
    assert "RESPONSE_LAYER_EXISTING_RESPONSES_MIXED" in payload["verdict_labels"]
    assert "RESPONSE_LAYER_EXISTING_RESPONSES_HURT_GLOBAL" in payload["verdict_labels"]


def test_down_missing_response_sign_is_suppression_required() -> None:
    payload = build_response_payload()
    assert payload["response_effect_summary"]["down_missing_response_sign"] == "suppression_required"
