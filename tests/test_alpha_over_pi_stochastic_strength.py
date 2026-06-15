from __future__ import annotations

import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_alpha_over_pi_stochastic_strength import (  # noqa: E402
    ALPHA_OVER_PI_STOCHASTIC_STRENGTH_PARTIAL,
    BROWNIAN_FACTOR_TWO_HAZARD_RECORDED,
    HOPF_CONTACT_NORMALIZATION_COMPATIBLE,
    LEPTON_8_9_CHANNEL_RULE_PARTIAL_DERIVATION_STRENGTHENED,
    U1_PHASE_NORMALIZATION_PARTIAL,
    audit_payload,
    e_squared_from_alpha,
    export_alpha_over_pi_outputs,
    factor_of_two_hazard_status,
    lepton_active_fraction,
    lepton_dressing_factor,
    lepton_eta_from_alpha,
    mode_norm_N,
    normalized_u1_phase_coupling,
    q_from_kj,
    stochastic_strength_from_alpha,
    stochastic_strength_from_phase_coupling,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_rationalized_u1_algebra_gives_alpha_over_pi() -> None:
    alpha = 1.0 / 137.035999084
    e2 = e_squared_from_alpha(alpha)
    e = math.sqrt(e2)
    coupling = normalized_u1_phase_coupling(e)

    assert math.isclose(e2, 4.0 * math.pi * alpha)
    assert math.isclose(coupling, e / (2.0 * math.pi))
    assert math.isclose(stochastic_strength_from_phase_coupling(e), alpha / math.pi)
    assert math.isclose(stochastic_strength_from_alpha(alpha), alpha / math.pi)


def test_lepton_active_fraction_and_eta_are_exact_consequences() -> None:
    alpha = 1.0 / 137.035999084
    assert lepton_active_fraction() == Fraction(8, 9)
    assert math.isclose(lepton_eta_from_alpha(alpha), 8.0 * alpha / (9.0 * math.pi))


def test_mode_norms_and_reference_dressing_factor() -> None:
    alpha = 1.0 / 137.035999084
    assert q_from_kj(0, 0) == 0
    assert q_from_kj(5, 2) == 1
    assert q_from_kj(9, 3) == 3
    assert mode_norm_N(0, 0) == 0
    assert mode_norm_N(5, 2) == 5
    assert mode_norm_N(9, 3) == 18
    assert lepton_dressing_factor(alpha, 0, 0) == 1.0
    assert lepton_dressing_factor(alpha, 9, 3) < lepton_dressing_factor(alpha, 5, 2) < 1.0


def test_factor_of_two_hazard_is_recorded_not_hidden() -> None:
    hazard = factor_of_two_hazard_status()
    assert hazard.status == BROWNIAN_FACTOR_TWO_HAZARD_RECORDED
    assert hazard.follows is False
    assert any("factor" in item for item in hazard.limitations)


def test_payload_statuses_are_partial_and_non_official() -> None:
    payload = audit_payload()
    assert payload["alpha_over_pi_strength_status"] == ALPHA_OVER_PI_STOCHASTIC_STRENGTH_PARTIAL
    assert payload["u1_phase_normalization_status"] == U1_PHASE_NORMALIZATION_PARTIAL
    assert payload["hopf_contact_normalization_status"] == HOPF_CONTACT_NORMALIZATION_COMPATIBLE
    assert payload["brownian_factor_two_hazard_status"] == BROWNIAN_FACTOR_TWO_HAZARD_RECORDED
    assert payload["lepton_eta_consequence_status"] == LEPTON_8_9_CHANNEL_RULE_PARTIAL_DERIVATION_STRENGTHENED
    assert payload["does_alpha_over_pi_follow"] is True
    assert payload["does_eta_l_8alpha_9pi_follow"] is True
    assert payload["does_this_promote_full_lepton_8_9"] is False
    assert payload["does_this_change_official_predictions"] is False


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

    export_alpha_over_pi_outputs(ROOT)

    after = {path: _sha(path) for path in frozen_paths}
    assert before == after

    report_paths = [
        ROOT / "theory" / "alpha_over_pi_stochastic_strength_derivation.md",
        ROOT / "audits" / "alpha_over_pi_stochastic_strength_audit.md",
        ROOT / "audits" / "alpha_over_pi_stochastic_strength_audit.json",
    ]
    for path in report_paths:
        assert path.exists()

    parsed = json.loads((ROOT / "audits" / "alpha_over_pi_stochastic_strength_audit.json").read_text())
    assert parsed["official_outputs_modified"] is False
    assert parsed["frozen_predictions_modified"] is False
    assert parsed["alpha_over_pi_strength_status"] == ALPHA_OVER_PI_STOCHASTIC_STRENGTH_PARTIAL


def test_reports_do_not_contain_forbidden_overclaims() -> None:
    export_alpha_over_pi_outputs(ROOT)
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
        ROOT / "theory" / "alpha_over_pi_stochastic_strength_derivation.md",
        ROOT / "audits" / "alpha_over_pi_stochastic_strength_audit.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)
    for phrase in forbidden:
        assert phrase not in text
