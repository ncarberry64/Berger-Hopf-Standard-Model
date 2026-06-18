from __future__ import annotations

import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_identity_traceless_stochastic import (  # noqa: E402
    IDENTITY_TRACELESS_STOCHASTIC_CONDITIONAL,
    LEPTON_8_9_CHANNEL_RULE_CONDITIONAL,
    QUARK_ACTIVE_FRACTION_CONSEQUENCE_CANDIDATE_ONLY,
    active_traceless_fraction,
    algebra_split_label,
    audit_payload,
    common_mode_cancels_in_ratio,
    endomorphism_dimension,
    eta_from_active_fraction,
    export_identity_traceless_stochastic_outputs,
    identity_channel_dimension,
    lepton_8_9_status_object,
    lepton_eta_8_9,
    sector_active_fraction,
    sector_dimension,
    trace_preserving_condition,
    traceless_channel_dimension,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_exact_endomorphism_and_traceless_counts() -> None:
    assert endomorphism_dimension(3) == 9
    assert identity_channel_dimension(3) == 1
    assert traceless_channel_dimension(3) == 8
    assert active_traceless_fraction(3) == Fraction(8, 9)
    assert algebra_split_label(3) == "C I_3 + su(3)"


def test_eta_formula_is_exact_8alpha_over_9pi() -> None:
    alpha = 1.0 / 137.035999084
    assert math.isclose(eta_from_active_fraction(alpha, 3), 8.0 * alpha / (9.0 * math.pi))
    assert math.isclose(lepton_eta_8_9(alpha), 8.0 * alpha / (9.0 * math.pi))


def test_sector_active_fractions_are_candidate_consequences() -> None:
    assert sector_dimension("charged_lepton") == 3
    assert sector_dimension("up") == 6
    assert sector_dimension("down") == 12
    assert sector_active_fraction("charged_lepton") == Fraction(8, 9)
    assert sector_active_fraction("up") == Fraction(35, 36)
    assert sector_active_fraction("down") == Fraction(143, 144)


def test_common_mode_and_trace_preserving_conditions() -> None:
    assert common_mode_cancels_in_ratio(7.0, 2.5, 11.0) is True
    assert trace_preserving_condition(0.0) is True
    assert trace_preserving_condition(0.1) is False


def test_lepton_status_is_conditional_not_official() -> None:
    status = lepton_8_9_status_object(1.0 / 137.035999084)
    assert status.lepton_8_9_status == LEPTON_8_9_CHANNEL_RULE_CONDITIONAL
    assert status.d_l == 3
    assert status.endomorphism_channels == 9
    assert status.identity_channels == 1
    assert status.traceless_channels == 8
    assert status.active_fraction == Fraction(8, 9)
    assert status.conditional is True
    assert status.official is False


def test_payload_statuses_are_conditional_and_non_official() -> None:
    payload = audit_payload()
    assert payload["identity_traceless_stochastic_status"] == IDENTITY_TRACELESS_STOCHASTIC_CONDITIONAL
    assert payload["lepton_8_9_status"] == LEPTON_8_9_CHANNEL_RULE_CONDITIONAL
    assert payload["quark_active_fraction_consequence_status"] == QUARK_ACTIVE_FRACTION_CONSEQUENCE_CANDIDATE_ONLY
    assert payload["does_stochastic_dressing_act_on_End_H"] is True
    assert payload["does_identity_channel_get_protected"] is True
    assert payload["does_trace_preservation_justify_protection"] is True
    assert payload["does_common_mode_cancel_in_ratios"] is True
    assert payload["does_traceless_activity_follow"] is True
    assert payload["does_active_fraction_follow"] is True
    assert payload["does_eta_l_8_9_follow"] is True
    assert payload["is_lepton_8_9_conditional"] is True
    assert payload["does_this_change_official_predictions"] is False
    assert payload["forbidden_claims_absent"] is True
    assert payload["safe_to_merge_as_candidate_only"] is True


def test_frozen_sanity_remains_unchanged() -> None:
    sanity = audit_payload()["frozen_sanity"]
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

    export_identity_traceless_stochastic_outputs(ROOT)

    after = {path: _sha(path) for path in frozen_paths}
    assert before == after

    report_paths = [
        ROOT / "theory" / "identity_channel_protection_theorem.md",
        ROOT / "theory" / "traceless_brownian_activity_theorem.md",
        ROOT / "theory" / "lepton_8_9_conditional_derivation.md",
        ROOT / "theory" / "common_mode_cancellation_in_mass_ratios.md",
        ROOT / "theory" / "trace_preserving_channel_splitting.md",
        ROOT / "theory" / "attractor_normalization_identity_protection.md",
        ROOT / "theory" / "quark_active_fraction_consequence_candidate.md",
        ROOT / "theory" / "lindblad_like_traceless_generator_candidate.md",
        ROOT / "audits" / "identity_traceless_stochastic_protection_audit.md",
        ROOT / "audits" / "identity_traceless_stochastic_protection_audit.json",
    ]
    for path in report_paths:
        assert path.exists()

    parsed = json.loads((ROOT / "audits" / "identity_traceless_stochastic_protection_audit.json").read_text())
    assert parsed["official_outputs_modified"] is False
    assert parsed["frozen_predictions_modified"] is False
    assert parsed["lepton_8_9_status"] == LEPTON_8_9_CHANNEL_RULE_CONDITIONAL


def test_reports_do_not_contain_forbidden_overclaims() -> None:
    export_identity_traceless_stochastic_outputs(ROOT)
    forbidden = [
        "bhsm is proven",
        "bhsm is confirmed",
        "replaces the standard model",
        "ordinary faster-than-light neutrino",
        "ordinary environmental mass-drift",
        "ordinary environmental mass drift",
        "full standard model derivation",
    ]
    paths = [
        ROOT / "theory" / "identity_channel_protection_theorem.md",
        ROOT / "audits" / "identity_traceless_stochastic_protection_audit.md",
        ROOT / "theory" / "lepton_8_9_conditional_derivation.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)
    for phrase in forbidden:
        assert phrase not in text
