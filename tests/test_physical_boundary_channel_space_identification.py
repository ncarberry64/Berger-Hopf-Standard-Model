from __future__ import annotations

import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_physical_boundary_channel_space import (  # noqa: E402
    END_H_STOCHASTIC_ALGEBRA_PARTIAL,
    LEPTON_8_9_CHANNEL_RULE_PARTIAL_DERIVATION,
    PHYSICAL_CHANNEL_SPACE_PARTIAL,
    active_fraction_from_orbit,
    audit_payload,
    common_mode_subspace_dimension,
    cyclic_orbit_states,
    cyclic_random_walk_generator_count,
    density_matrix_dimension,
    endomorphism_dimension_from_channel,
    export_physical_channel_space_outputs,
    group_algebra_basis,
    identity_channel_count,
    lepton_eta_from_physical_channel,
    orbit_basis_labels,
    physical_channel_dimension,
    random_walk_state_count,
    sector_physical_channel_status,
    traceless_channel_count_from_orbit,
    zero_sum_fluctuation_dimension,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_exact_cyclic_orbit_and_channel_dimensions() -> None:
    assert cyclic_orbit_states(3) == [0, 1, 2]
    assert cyclic_orbit_states(6) == [0, 1, 2, 3, 4, 5]
    assert cyclic_orbit_states(12) == list(range(12))

    assert orbit_basis_labels(3) == ["|0>", "|1>", "|2>"]
    assert group_algebra_basis(3) == ["e0", "e1", "e2"]

    assert physical_channel_dimension(3) == 3
    assert physical_channel_dimension(6) == 6
    assert physical_channel_dimension(12) == 12


def test_end_h_counts_and_active_fractions_are_exact() -> None:
    assert density_matrix_dimension(3) == 9
    assert endomorphism_dimension_from_channel(3) == 9
    assert identity_channel_count(3) == 1
    assert traceless_channel_count_from_orbit(3) == 8
    assert active_fraction_from_orbit(3) == Fraction(8, 9)

    assert endomorphism_dimension_from_channel(6) == 36
    assert traceless_channel_count_from_orbit(6) == 35
    assert active_fraction_from_orbit(6) == Fraction(35, 36)

    assert endomorphism_dimension_from_channel(12) == 144
    assert traceless_channel_count_from_orbit(12) == 143
    assert active_fraction_from_orbit(12) == Fraction(143, 144)


def test_probability_simplex_dimension_is_not_end_h_traceless_dimension() -> None:
    assert zero_sum_fluctuation_dimension(3) == 2
    assert common_mode_subspace_dimension(3) == 1
    assert traceless_channel_count_from_orbit(3) == 8
    assert zero_sum_fluctuation_dimension(3) != traceless_channel_count_from_orbit(3)


def test_random_walk_counts_are_finite_state_counts() -> None:
    assert random_walk_state_count(3) == 3
    assert random_walk_state_count(6) == 6
    assert cyclic_random_walk_generator_count(3) == 2


def test_lepton_eta_is_8alpha_over_9pi_as_partial_consequence() -> None:
    alpha = 1.0 / 137.035999084
    assert math.isclose(lepton_eta_from_physical_channel(alpha), 8.0 * alpha / (9.0 * math.pi))


def test_sector_statuses_match_expected_counts() -> None:
    lepton = sector_physical_channel_status("charged_lepton")
    up = sector_physical_channel_status("up")
    down = sector_physical_channel_status("down")

    assert lepton.dimension == 3
    assert lepton.endomorphism_dimension == 9
    assert lepton.traceless_channels == 8
    assert lepton.active_fraction == Fraction(8, 9)

    assert up.dimension == 6
    assert up.endomorphism_dimension == 36
    assert up.traceless_channels == 35
    assert up.active_fraction == Fraction(35, 36)

    assert down.dimension == 12
    assert down.endomorphism_dimension == 144
    assert down.traceless_channels == 143
    assert down.active_fraction == Fraction(143, 144)


def test_payload_statuses_are_partial_and_non_official() -> None:
    payload = audit_payload()

    assert payload["physical_channel_space_status"] == PHYSICAL_CHANNEL_SPACE_PARTIAL
    assert payload["End_H_stochastic_algebra_status"] == END_H_STOCHASTIC_ALGEBRA_PARTIAL
    assert payload["lepton_8_9_consequence_status"] == LEPTON_8_9_CHANNEL_RULE_PARTIAL_DERIVATION
    assert payload["does_orbit_basis_define_physical_channels"] is True
    assert payload["does_stochastic_dressing_sample_orbit_states"] is True
    assert payload["does_density_covariance_live_on_H_f"] is True
    assert payload["does_End_H_become_physical_stochastic_algebra"] is True
    assert payload["does_group_algebra_have_physical_boundary_meaning"] is True
    assert payload["does_random_walk_model_support_channel_space"] is True
    assert payload["does_this_promote_lepton_8_9_to_partial"] is True
    assert payload["does_this_promote_full_lepton_8_9"] is False
    assert payload["does_this_change_official_predictions"] is False


def test_frozen_sanity_and_official_branches_remain_unchanged() -> None:
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

    export_physical_channel_space_outputs(ROOT)

    after = {path: _sha(path) for path in frozen_paths}
    assert before == after

    expected_paths = [
        ROOT / "theory" / "physical_boundary_channel_space_identification.md",
        ROOT / "theory" / "orbit_states_as_boundary_residue_channels.md",
        ROOT / "theory" / "stochastic_dressing_on_channel_space.md",
        ROOT / "theory" / "density_covariance_on_cyclic_channel_space.md",
        ROOT / "theory" / "group_algebra_as_physical_boundary_channel.md",
        ROOT / "theory" / "cyclic_random_walk_boundary_noise_candidate.md",
        ROOT / "theory" / "lepton_8_9_partial_derivation_status.md",
        ROOT / "theory" / "quark_channel_space_consequence_candidate.md",
        ROOT / "theory" / "neutrino_channel_space_consequence_candidate.md",
        ROOT / "audits" / "physical_boundary_channel_space_identification_audit.md",
        ROOT / "audits" / "physical_boundary_channel_space_identification_audit.json",
    ]
    for path in expected_paths:
        assert path.exists()

    parsed = json.loads((ROOT / "audits" / "physical_boundary_channel_space_identification_audit.json").read_text())
    assert parsed["official_outputs_modified"] is False
    assert parsed["frozen_predictions_modified"] is False
    assert parsed["physical_channel_space_status"] == PHYSICAL_CHANNEL_SPACE_PARTIAL
    assert parsed["does_this_promote_full_lepton_8_9"] is False


def test_reports_do_not_contain_forbidden_overclaims() -> None:
    export_physical_channel_space_outputs(ROOT)
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
        ROOT / "theory" / "physical_boundary_channel_space_identification.md",
        ROOT / "theory" / "stochastic_dressing_on_channel_space.md",
        ROOT / "audits" / "physical_boundary_channel_space_identification_audit.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)
    for phrase in forbidden:
        assert phrase not in text
