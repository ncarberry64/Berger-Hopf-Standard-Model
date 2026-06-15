from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_charged_lepton_consolidation import (  # noqa: E402
    CHANNEL_DIMENSION_STATUS,
    CONSOLIDATION_STATUS,
    FACTOR_TWO_STATUS,
    LEPTON_CHAIN_OVERALL_STATUS,
    LEPTON_OMEGA_STATUS,
    active_fraction,
    alpha_over_pi,
    allowed_eta_forms,
    audit_payload,
    end_dimension,
    eta_double_factor,
    eta_half_factor,
    eta_no_extra_half,
    export_charged_lepton_consolidation_outputs,
    identity_channel_count,
    lepton_channel_dimension,
    lepton_dressing_factor,
    lepton_omega,
    mode_norm_N,
    preferred_eta_form,
    q_from_kj,
    traceless_channel_count,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_exact_charged_lepton_mode_arithmetic() -> None:
    assert q_from_kj(0, 0) == 0
    assert q_from_kj(5, 2) == 1
    assert q_from_kj(9, 3) == 3
    assert lepton_omega(0, 0) == 0
    assert lepton_omega(1, 2) == 3
    assert lepton_omega(3, 3) == 3
    assert mode_norm_N(0, 0) == 0
    assert mode_norm_N(5, 2) == 5
    assert mode_norm_N(9, 3) == 18


def test_channel_space_and_active_fraction_arithmetic() -> None:
    d = lepton_channel_dimension()
    assert d == 3
    assert end_dimension(d) == 9
    assert identity_channel_count(d) == 1
    assert traceless_channel_count(d) == 8
    assert active_fraction(d).numerator == 8
    assert active_fraction(d).denominator == 9


def test_eta_forms_are_exact_and_preserved() -> None:
    alpha = 1.0 / 137.035999084
    assert math.isclose(alpha_over_pi(alpha), alpha / math.pi)
    assert math.isclose(eta_no_extra_half(alpha), 8.0 * alpha / (9.0 * math.pi))
    assert math.isclose(eta_half_factor(alpha), 4.0 * alpha / (9.0 * math.pi))
    assert math.isclose(eta_double_factor(alpha), 16.0 * alpha / (9.0 * math.pi))
    forms = allowed_eta_forms(alpha)
    assert set(forms) == {"no_extra_half", "half_factor", "double_factor"}
    assert forms["half_factor"] < forms["no_extra_half"] < forms["double_factor"]
    assert preferred_eta_form() == "no_extra_half_repo_exponent_convention"


def test_candidate_dressing_factors_are_numeric_not_official() -> None:
    alpha = 1.0 / 137.035999084
    assert lepton_dressing_factor(alpha, 0, 0) == 1.0
    assert lepton_dressing_factor(alpha, 5, 2) < 1.0
    assert lepton_dressing_factor(alpha, 9, 3) < lepton_dressing_factor(alpha, 5, 2)
    assert lepton_dressing_factor(alpha, 5, 2, eta_form="half_factor") > lepton_dressing_factor(alpha, 5, 2)


def test_payload_statuses_are_claim_safe() -> None:
    payload = audit_payload()
    assert payload["consolidation_status"] == CONSOLIDATION_STATUS
    assert payload["lepton_chain_overall_status"] == LEPTON_CHAIN_OVERALL_STATUS
    assert payload["lepton_omega_status"] == LEPTON_OMEGA_STATUS
    assert payload["channel_dimension_status"] == CHANNEL_DIMENSION_STATUS
    assert payload["factor_two_status"] == FACTOR_TWO_STATUS
    assert payload["does_eta_l_8alpha_9pi_remain_supported"] is True
    assert payload["does_factor_two_close"] is False
    assert payload["does_this_promote_full_lepton_8_9"] is False
    assert payload["does_this_change_official_predictions"] is False
    assert payload["dressing_status"] == "LEPTON_DRESSING_CANDIDATE_NOT_OFFICIAL"
    assert "LEPTON_8_9_CHANNEL_RULE_DERIVED" not in json.dumps(payload, default=str)


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
    assert sanity["official_branch_comparison"]["no_retuning"] is True


def test_export_writes_reports_without_touching_frozen_predictions() -> None:
    frozen_paths = [
        ROOT / "docs" / "frozen_predictions.md",
        ROOT / "docs" / "frozen_predictions.json",
    ]
    before = {path: _sha(path) for path in frozen_paths}

    export_charged_lepton_consolidation_outputs(ROOT)

    after = {path: _sha(path) for path in frozen_paths}
    assert before == after

    report_paths = [
        ROOT / "theory" / "charged_lepton_partial_derivation_consolidated.md",
        ROOT / "theory" / "charged_lepton_claim_status_table.md",
        ROOT / "theory" / "charged_lepton_factor_two_normalization_status.md",
        ROOT / "theory" / "charged_lepton_open_blockers.md",
        ROOT / "audits" / "charged_lepton_partial_derivation_consolidation_audit.md",
        ROOT / "audits" / "charged_lepton_partial_derivation_consolidation_audit.json",
    ]
    for path in report_paths:
        assert path.exists()

    parsed = json.loads(
        (ROOT / "audits" / "charged_lepton_partial_derivation_consolidation_audit.json").read_text()
    )
    assert parsed["consolidation_status"] == CONSOLIDATION_STATUS
    assert parsed["official_outputs_modified"] is False
    assert parsed["safe_to_merge_as_candidate_only"] is True


def test_reports_do_not_contain_forbidden_overclaims() -> None:
    export_charged_lepton_consolidation_outputs(ROOT)
    forbidden = [
        "full standard model derivation claim",
        "standard model replacement claim",
        "official lepton prediction update",
        "official quark prediction update",
        "no-parameter-tuning full-theory claim",
        "ordinary faster-than-light neutrino claim",
        "ordinary environmental mass-drift claim",
        "time-dependent constants as official lab prediction",
        "hidden retuning",
    ]
    paths = [
        ROOT / "theory" / "charged_lepton_partial_derivation_consolidated.md",
        ROOT / "theory" / "charged_lepton_claim_status_table.md",
        ROOT / "audits" / "charged_lepton_partial_derivation_consolidation_audit.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)
    for phrase in forbidden:
        assert phrase not in text
