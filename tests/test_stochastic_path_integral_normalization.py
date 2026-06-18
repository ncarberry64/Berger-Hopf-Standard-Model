from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_stochastic_path_integral_normalization import (  # noqa: E402
    ALPHA_PI_ROLE_GENERATOR_BY_REPO_CONVENTION_RAW_VARIANCE_ALTERNATIVE,
    BROWNIAN_FACTOR_TWO_CONVENTION_DEPENDENT_STRENGTHENED,
    ITO_SQRT_2D_NORMALIZATION_PARTIAL,
    LEPTON_ETA_NORMALIZATION_CONVENTION_DEPENDENT_STRENGTHENED,
    STOCHASTIC_NORMALIZATION_PARTIAL,
    STOCHASTIC_PATH_INTEGRAL_HEAT_KERNEL_PARTIAL,
    STOCHASTIC_PATH_INTEGRAL_PHASE_CUMULANT_CONDITIONAL,
    D_from_g_squared_ito,
    attenuation_heat_kernel,
    attenuation_phase_cumulant,
    audit_payload,
    eta_from_sqrt_2D_convention,
    eta_half_factor,
    eta_no_extra_half,
    export_stochastic_path_integral_outputs,
    g_squared_from_alpha,
    lepton_active_fraction,
    lepton_eta_half_factor,
    lepton_eta_no_extra_half,
    mode_norm_N,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_exact_normalization_formulas() -> None:
    alpha = 1.0 / 137.035999084
    active = lepton_active_fraction()
    g2 = g_squared_from_alpha(alpha)
    assert math.isclose(g2, alpha / math.pi)
    assert math.isclose(D_from_g_squared_ito(g2), alpha / (2.0 * math.pi))
    assert math.isclose(eta_no_extra_half(alpha, active), 8.0 * alpha / (9.0 * math.pi))
    assert math.isclose(eta_half_factor(alpha, active), 4.0 * alpha / (9.0 * math.pi))
    assert math.isclose(lepton_eta_no_extra_half(alpha), 8.0 * alpha / (9.0 * math.pi))
    assert math.isclose(lepton_eta_half_factor(alpha), 4.0 * alpha / (9.0 * math.pi))


def test_mode_norms_and_attenuation_routes() -> None:
    alpha = 1.0 / 137.035999084
    active = lepton_active_fraction()
    g2 = g_squared_from_alpha(alpha)
    assert mode_norm_N(0, 0) == 0
    assert mode_norm_N(5, 2) == 5
    assert mode_norm_N(9, 3) == 18
    assert attenuation_heat_kernel(g2, 0, active) == 1.0
    assert attenuation_phase_cumulant(g2, 0, active) == 1.0
    assert attenuation_phase_cumulant(g2, 5, active) > attenuation_heat_kernel(g2, 5, active)


def test_ito_sqrt_2d_convention_keeps_roles_explicit() -> None:
    alpha = 1.0 / 137.035999084
    active = lepton_active_fraction()
    assert math.isclose(
        eta_from_sqrt_2D_convention(alpha, active, alpha_pi_role="generator_coefficient"),
        eta_no_extra_half(alpha, active),
    )
    assert math.isclose(
        eta_from_sqrt_2D_convention(alpha, active, alpha_pi_role="raw_variance"),
        eta_half_factor(alpha, active),
    )


def test_payload_statuses_preserve_factor_two_hazard() -> None:
    payload = audit_payload()
    assert payload["stochastic_path_integral_status"] == STOCHASTIC_NORMALIZATION_PARTIAL
    assert payload["heat_kernel_generator_status"] == STOCHASTIC_PATH_INTEGRAL_HEAT_KERNEL_PARTIAL
    assert payload["phase_cumulant_status"] == STOCHASTIC_PATH_INTEGRAL_PHASE_CUMULANT_CONDITIONAL
    assert payload["ito_sqrt_2D_status"] == ITO_SQRT_2D_NORMALIZATION_PARTIAL
    assert payload["alpha_pi_role_status"] == ALPHA_PI_ROLE_GENERATOR_BY_REPO_CONVENTION_RAW_VARIANCE_ALTERNATIVE
    assert payload["brownian_factor_two_status"] == BROWNIAN_FACTOR_TWO_CONVENTION_DEPENDENT_STRENGTHENED
    assert payload["lepton_eta_normalization_status"] == LEPTON_ETA_NORMALIZATION_CONVENTION_DEPENDENT_STRENGTHENED
    assert payload["is_alpha_pi_raw_variance"] is True
    assert payload["is_alpha_pi_generator_coefficient"] is True
    assert payload["is_tau_boundary_cycle_fixed"] is True
    assert payload["does_sqrt_2D_convention_resolve_half_factor"] is True
    assert payload["does_eta_l_8alpha_9pi_remain_supported"] is True
    assert payload["does_factor_two_close"] is False


def test_allowed_eta_forms_are_preserved_without_official_update() -> None:
    payload = audit_payload()
    forms = payload["allowed_eta_forms"]
    assert set(forms) == {"no_extra_half", "half_factor", "double_factor"}
    assert forms["half_factor"] < forms["no_extra_half"] < forms["double_factor"]
    assert payload["preferred_eta_form"] == "no_extra_half_repo_exponent_convention"
    assert payload["does_this_change_official_predictions"] is False
    assert payload["does_this_promote_full_lepton_8_9"] is False
    assert payload["safe_to_merge_as_candidate_only"] is True


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


def test_export_writes_required_reports_without_touching_frozen_predictions() -> None:
    frozen_paths = [
        ROOT / "docs" / "frozen_predictions.md",
        ROOT / "docs" / "frozen_predictions.json",
    ]
    before = {path: _sha(path) for path in frozen_paths}

    export_stochastic_path_integral_outputs(ROOT)

    after = {path: _sha(path) for path in frozen_paths}
    assert before == after

    report_paths = [
        ROOT / "theory" / "stochastic_path_integral_normalization.md",
        ROOT / "theory" / "heat_kernel_generator_vs_phase_variance.md",
        ROOT / "theory" / "ito_sqrt_2D_boundary_noise_normalization.md",
        ROOT / "theory" / "boundary_cycle_time_normalization.md",
        ROOT / "audits" / "stochastic_path_integral_normalization_audit.md",
        ROOT / "audits" / "stochastic_path_integral_normalization_audit.json",
    ]
    for path in report_paths:
        assert path.exists()

    parsed = json.loads((ROOT / "audits" / "stochastic_path_integral_normalization_audit.json").read_text())
    assert parsed["brownian_factor_two_status"] == BROWNIAN_FACTOR_TWO_CONVENTION_DEPENDENT_STRENGTHENED
    assert parsed["official_outputs_modified"] is False


def test_reports_do_not_contain_forbidden_overclaims() -> None:
    export_stochastic_path_integral_outputs(ROOT)
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
        ROOT / "theory" / "stochastic_path_integral_normalization.md",
        ROOT / "theory" / "heat_kernel_generator_vs_phase_variance.md",
        ROOT / "audits" / "stochastic_path_integral_normalization_audit.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)
    for phrase in forbidden:
        assert phrase not in text
