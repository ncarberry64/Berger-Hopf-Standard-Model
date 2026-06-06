from math import isclose, pi

from bhsm_config import (
    alpha_anchored_geometry_config,
    available_geometry_configs,
    canonical_geometry_config,
    compare_geometry_configs,
    legacy_low_a_config,
    round_geometry_config,
)
from bhsm_model import build_bhsm_model, export_model_card_json, export_model_card_markdown
from constants import ALPHA_INV_LOW_ENERGY


def test_alpha_anchored_value_matches_alpha_inverse_rule():
    config = alpha_anchored_geometry_config()

    assert isclose(config.a, ALPHA_INV_LOW_ENERGY / (12.0 * pi**2))
    assert config.status == "CANONICAL_CANDIDATE"


def test_round_config_remains_baseline_control():
    config = round_geometry_config()

    assert config.name == "ROUND"
    assert config.a == 1.0
    assert config.status == "BASELINE_CONTROL"


def test_legacy_low_a_remains_sensitivity_only():
    config = legacy_low_a_config()

    assert config.name == "LEGACY_LOW_A"
    assert config.a == 0.573
    assert config.status == "LEGACY_SENSITIVITY"


def test_canonical_config_is_selected_by_theory_rule_not_residuals():
    config = canonical_geometry_config()
    notes = " ".join(config.notes)

    assert config.name == "ALPHA_ANCHORED"
    assert config.status == "CANONICAL"
    assert "epsilon_alpha" in notes
    assert "Not chosen by fitting residuals" in notes


def test_full_ledger_comparison_runs_for_all_geometry_configs():
    rows = compare_geometry_configs(build_bhsm_model, available_geometry_configs())

    assert {row["geometry"]["name"] for row in rows} == {"ROUND", "LEGACY_LOW_A", "ALPHA_ANCHORED"}
    assert all(row["charged_fermion_mass_ratios"] for row in rows)
    assert all(row["ckm_angles"]["sin_theta_13"] > 0 for row in rows)
    assert all(row["residual_summary"] for row in rows)


def test_canonical_choice_does_not_reference_empirical_masses():
    config = canonical_geometry_config()
    text = " ".join((config.source, *config.notes)).lower()

    assert "best fit" not in text
    assert "does not inspect empirical mass" in text
    assert "not chosen by fitting residuals" in text


def test_default_model_uses_alpha_anchored_geometry_and_card_records_rule(tmp_path):
    model = build_bhsm_model()
    md_path = tmp_path / "model_card.md"
    json_path = tmp_path / "model_card.json"

    export_model_card_markdown(model, md_path)
    export_model_card_json(model, json_path)

    markdown = md_path.read_text()
    json_text = json_path.read_text()
    assert model.geometry_config.name == "ALPHA_ANCHORED"
    assert "ALPHA_ANCHORED" in markdown
    assert "alpha^{-1}/(12*pi^2)" in markdown
    assert '"name": "ALPHA_ANCHORED"' in json_text
