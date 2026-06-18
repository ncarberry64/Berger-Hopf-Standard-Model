from __future__ import annotations

import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_brownian_generator_topographic import (  # noqa: E402
    BROWNIAN_GENERATOR_TOPOGRAPHIC_PARTIAL,
    LEPTON_8_9_CHANNEL_RULE_PARTIAL_DERIVATION_STRENGTHENED,
    TRACELESS_BROWNIAN_GENERATOR_PARTIAL,
    active_fraction,
    attractor_susceptibility_proxy,
    audit_payload,
    brownian_generator_count,
    end_traceless_fluctuation_dimension,
    endomorphism_dimension,
    eta_from_alpha_active_fraction,
    exponential_dressing,
    export_brownian_generator_outputs,
    lepton_eta_8_9,
    mode_norm_N,
    probability_simplex_fluctuation_dimension,
    q_from_kj,
    sector_brownian_status,
    trace_preserving_noise_condition,
    traceless_generator_count,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_exact_mode_norm_values() -> None:
    assert q_from_kj(0, 0) == 0
    assert q_from_kj(5, 2) == 1
    assert q_from_kj(9, 3) == 3
    assert mode_norm_N(0, 0) == 0
    assert mode_norm_N(5, 2) == 5
    assert mode_norm_N(9, 3) == 18


def test_exact_end_h_and_su_d_counts() -> None:
    assert endomorphism_dimension(3) == 9
    assert traceless_generator_count(3) == 8
    assert brownian_generator_count(3) == 8
    assert active_fraction(3) == Fraction(8, 9)
    assert endomorphism_dimension(6) == 36
    assert active_fraction(6) == Fraction(35, 36)
    assert endomorphism_dimension(12) == 144
    assert active_fraction(12) == Fraction(143, 144)


def test_probability_simplex_dimension_not_confused_with_end_h() -> None:
    assert probability_simplex_fluctuation_dimension(3) == 2
    assert end_traceless_fluctuation_dimension(3) == 8
    assert probability_simplex_fluctuation_dimension(3) != end_traceless_fluctuation_dimension(3)


def test_trace_preserving_and_exponential_dressing() -> None:
    assert trace_preserving_noise_condition(0.0) is True
    assert trace_preserving_noise_condition(0.2) is False
    assert exponential_dressing(0.5, 0, 0) == 1.0
    assert exponential_dressing(0.1, 5, 2) < 1.0


def test_eta_l_equals_8alpha_over_9pi() -> None:
    alpha = 1.0 / 137.035999084
    expected = 8.0 * alpha / (9.0 * math.pi)
    assert math.isclose(eta_from_alpha_active_fraction(alpha, 3), expected)
    assert math.isclose(lepton_eta_8_9(alpha), expected)


def test_susceptibility_decreases_with_mode_norm() -> None:
    tau = attractor_susceptibility_proxy(0, 0)
    muon = attractor_susceptibility_proxy(5, 2)
    electron = attractor_susceptibility_proxy(9, 3)
    assert tau > muon > electron


def test_sector_brownian_statuses() -> None:
    lepton = sector_brownian_status("charged_lepton")
    up = sector_brownian_status("up")
    down = sector_brownian_status("down")

    assert lepton.dimension == 3
    assert lepton.traceless_generators == 8
    assert lepton.active_fraction == Fraction(8, 9)
    assert lepton.candidate_only is False

    assert up.dimension == 6
    assert up.traceless_generators == 35
    assert up.active_fraction == Fraction(35, 36)
    assert up.candidate_only is True

    assert down.dimension == 12
    assert down.traceless_generators == 143
    assert down.active_fraction == Fraction(143, 144)
    assert down.candidate_only is True


def test_payload_statuses_are_partial_not_official() -> None:
    payload = audit_payload()

    assert payload["brownian_generator_topographic_status"] == BROWNIAN_GENERATOR_TOPOGRAPHIC_PARTIAL
    assert payload["su_d_brownian_generator_status"] == TRACELESS_BROWNIAN_GENERATOR_PARTIAL
    assert payload["lepton_8_9_consequence_status"] == LEPTON_8_9_CHANNEL_RULE_PARTIAL_DERIVATION_STRENGTHENED
    assert payload["does_topographic_dynamics_generate_noise"] is True
    assert payload["does_boundary_projection_map_noise_to_H_f"] is True
    assert payload["does_noise_act_on_End_H"] is True
    assert payload["does_trace_preservation_force_su_d"] is True
    assert payload["does_brownian_generator_live_on_su_d"] is True
    assert payload["does_exponential_dressing_follow"] is True
    assert payload["does_N_equal_q2_plus_j2_follow"] is True
    assert payload["does_alpha_over_pi_follow"] is False
    assert payload["does_eta_l_8_9_follow"] is True
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

    export_brownian_generator_outputs(ROOT)

    after = {path: _sha(path) for path in frozen_paths}
    assert before == after

    expected_paths = [
        ROOT / "theory" / "brownian_generator_from_topographic_attractor_dynamics.md",
        ROOT / "theory" / "attractor_hessian_fluctuation_candidate.md",
        ROOT / "theory" / "boundary_projection_of_topographic_noise.md",
        ROOT / "theory" / "traceless_su_d_brownian_generator.md",
        ROOT / "theory" / "exponential_dressing_from_brownian_quadratic_norm.md",
        ROOT / "theory" / "alpha_over_pi_stochastic_strength_candidate.md",
        ROOT / "theory" / "lepton_8_9_partial_derivation_strengthened.md",
        ROOT / "theory" / "quark_brownian_active_fraction_candidate.md",
        ROOT / "theory" / "neutrino_brownian_channel_candidate.md",
        ROOT / "audits" / "brownian_generator_topographic_attractor_audit.md",
        ROOT / "audits" / "brownian_generator_topographic_attractor_audit.json",
    ]
    for path in expected_paths:
        assert path.exists()

    parsed = json.loads((ROOT / "audits" / "brownian_generator_topographic_attractor_audit.json").read_text())
    assert parsed["official_outputs_modified"] is False
    assert parsed["frozen_predictions_modified"] is False
    assert parsed["does_this_promote_full_lepton_8_9"] is False


def test_reports_do_not_contain_forbidden_overclaims() -> None:
    export_brownian_generator_outputs(ROOT)
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
        ROOT / "theory" / "brownian_generator_from_topographic_attractor_dynamics.md",
        ROOT / "theory" / "traceless_su_d_brownian_generator.md",
        ROOT / "audits" / "brownian_generator_topographic_attractor_audit.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)
    for phrase in forbidden:
        assert phrase not in text
