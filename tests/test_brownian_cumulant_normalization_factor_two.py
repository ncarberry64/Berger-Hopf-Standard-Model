from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_brownian_cumulant_normalization import (  # noqa: E402
    BROWNIAN_FACTOR_TWO_CONVENTION_DEPENDENT,
    ETA_EXPONENT_CONVENTION_REPO_SUPPORTED,
    HEAT_KERNEL_NORMALIZATION_PARTIAL,
    LEPTON_ETA_NORMALIZATION_CONVENTION_DEPENDENT,
    PHASE_CUMULANT_HALF_FACTOR_CONDITIONAL,
    attenuation_heat_kernel,
    attenuation_phase_cumulant,
    audit_payload,
    doubled_eta,
    e_squared_from_alpha,
    export_brownian_cumulant_outputs,
    heat_kernel_eta,
    lepton_active_fraction,
    lepton_eta_double_factor,
    lepton_eta_half_factor,
    lepton_eta_no_extra_half,
    mode_norm_N,
    phase_coupling_squared,
    phase_cumulant_eta,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_exact_eta_forms() -> None:
    alpha = 1.0 / 137.035999084
    active = lepton_active_fraction()
    assert math.isclose(phase_coupling_squared(alpha), alpha / math.pi)
    assert math.isclose(e_squared_from_alpha(alpha), 4.0 * math.pi * alpha)
    assert math.isclose(heat_kernel_eta(alpha, active), 8.0 * alpha / (9.0 * math.pi))
    assert math.isclose(phase_cumulant_eta(alpha, active), 4.0 * alpha / (9.0 * math.pi))
    assert math.isclose(doubled_eta(alpha, active), 16.0 * alpha / (9.0 * math.pi))
    assert math.isclose(lepton_eta_no_extra_half(alpha), 8.0 * alpha / (9.0 * math.pi))
    assert math.isclose(lepton_eta_half_factor(alpha), 4.0 * alpha / (9.0 * math.pi))
    assert math.isclose(lepton_eta_double_factor(alpha), 16.0 * alpha / (9.0 * math.pi))


def test_mode_norms_and_attenuation_reference() -> None:
    alpha = 1.0 / 137.035999084
    active = lepton_active_fraction()
    assert mode_norm_N(0, 0) == 0
    assert mode_norm_N(5, 2) == 5
    assert mode_norm_N(9, 3) == 18
    assert attenuation_heat_kernel(alpha, 0, active) == 1.0
    assert attenuation_phase_cumulant(alpha, 0, active) == 1.0
    assert attenuation_phase_cumulant(alpha, 5, active) > attenuation_heat_kernel(alpha, 5, active)


def test_payload_convention_statuses() -> None:
    payload = audit_payload()
    assert payload["brownian_factor_two_status"] == BROWNIAN_FACTOR_TWO_CONVENTION_DEPENDENT
    assert payload["heat_kernel_normalization_status"] == HEAT_KERNEL_NORMALIZATION_PARTIAL
    assert payload["phase_cumulant_status"] == PHASE_CUMULANT_HALF_FACTOR_CONDITIONAL
    assert payload["eta_exponent_convention_status"] == ETA_EXPONENT_CONVENTION_REPO_SUPPORTED
    assert payload["lepton_eta_normalization_status"] == LEPTON_ETA_NORMALIZATION_CONVENTION_DEPENDENT
    assert payload["does_repo_define_eta_as_exponent_coefficient"] is True
    assert payload["does_heat_kernel_convention_support_no_extra_half"] is True
    assert payload["does_phase_cumulant_convention_require_half"] is True
    assert payload["is_alpha_over_pi_raw_variance"] is True
    assert payload["is_alpha_over_pi_generator_coefficient"] is True
    assert payload["is_factor_two_resolved"] is False
    assert payload["does_eta_l_8alpha_9pi_remain_supported"] is True
    assert payload["preferred_eta_form"] == "no_extra_half_repo_exponent_convention"


def test_all_eta_forms_are_reported_without_official_change() -> None:
    payload = audit_payload()
    forms = payload["allowed_eta_forms"]
    assert set(forms) == {"no_extra_half", "half_factor", "double_factor"}
    assert forms["half_factor"] < forms["no_extra_half"] < forms["double_factor"]
    assert payload["does_this_change_official_predictions"] is False
    assert payload["does_this_promote_full_lepton_8_9"] is False


def test_frozen_sanity_and_official_outputs_are_unchanged() -> None:
    payload = audit_payload()
    sanity = payload["frozen_sanity"]
    assert payload["official_outputs_modified"] is False
    assert payload["frozen_predictions_modified"] is False
    assert sanity["BHSM_BARE_V1_unchanged"] is True
    assert sanity["BHSM_DRESSED_V1_CANDIDATE_unchanged"] is True
    assert sanity["dressed_branch_changes_only_c_over_t"] is True
    assert sanity["u_over_t_unchanged"] is True
    assert sanity["ckm_sin_theta_13_unchanged"] is True
    assert sanity["a_unchanged"] is True
    assert sanity["S_unchanged"] is True


def test_export_writes_reports_without_touching_frozen_predictions() -> None:
    frozen_paths = [
        ROOT / "docs" / "frozen_predictions.md",
        ROOT / "docs" / "frozen_predictions.json",
    ]
    before = {path: _sha(path) for path in frozen_paths}

    export_brownian_cumulant_outputs(ROOT)

    after = {path: _sha(path) for path in frozen_paths}
    assert before == after

    report_paths = [
        ROOT / "theory" / "brownian_cumulant_normalization_factor_two.md",
        ROOT / "theory" / "heat_kernel_vs_phase_cumulant_conventions.md",
        ROOT / "theory" / "eta_as_exponent_coefficient_repo_convention.md",
        ROOT / "theory" / "lepton_eta_factor_two_consequence.md",
        ROOT / "theory" / "ito_generator_normalization_note.md",
        ROOT / "theory" / "no_official_prediction_update_factor_two_note.md",
        ROOT / "audits" / "brownian_cumulant_normalization_factor_two_audit.md",
        ROOT / "audits" / "brownian_cumulant_normalization_factor_two_audit.json",
    ]
    for path in report_paths:
        assert path.exists()

    parsed = json.loads((ROOT / "audits" / "brownian_cumulant_normalization_factor_two_audit.json").read_text())
    assert parsed["brownian_factor_two_status"] == BROWNIAN_FACTOR_TWO_CONVENTION_DEPENDENT
    assert parsed["official_outputs_modified"] is False


def test_reports_do_not_contain_forbidden_overclaims() -> None:
    export_brownian_cumulant_outputs(ROOT)
    forbidden = [
        "bhsm is proven",
        "bhsm is confirmed",
        "replaces the standard model",
        "ordinary faster-than-light neutrino",
        "ordinary environmental mass-drift",
        "ordinary environmental mass drift",
        "full standard model derivation",
        "official lepton dressing update",
        "official quark dressing update",
    ]
    paths = [
        ROOT / "theory" / "brownian_cumulant_normalization_factor_two.md",
        ROOT / "theory" / "eta_as_exponent_coefficient_repo_convention.md",
        ROOT / "audits" / "brownian_cumulant_normalization_factor_two_audit.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)
    for phrase in forbidden:
        assert phrase not in text
