from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_boundary_covering_map_channel import (  # noqa: E402
    CHANNEL_DIMENSION_STATUS,
    COVERING_MAP_THEOREM_STATUS,
    LEPTON_8_9_STATUS,
    QUARK_COVERING_CONSEQUENCE_STATUS,
    WILSON_LOOP_TRAP_STATUS,
    active_fraction_from_covering_degree,
    active_fraction_from_dimension,
    audit_payload,
    classical_simplex_relative_dimension,
    coherent_end_dimension,
    coherent_traceless_dimension,
    covering_channel_dimension,
    deck_group_order,
    degree_from_omega,
    export_boundary_covering_map_outputs,
    is_primitive_covering,
    is_wilson_loop_globally_trivial_for_integer_degree,
    lepton_omega,
    q_from_kj,
    sheet_count_from_degree,
    wilson_loop_phase_from_degree,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_lepton_boundary_arithmetic_and_covering_degree() -> None:
    assert q_from_kj(5, 2) == 1
    assert q_from_kj(9, 3) == 3
    assert lepton_omega(1, 2) == 3
    assert lepton_omega(3, 3) == 3
    assert degree_from_omega(3) == 3
    assert sheet_count_from_degree(3) == 3
    assert deck_group_order(3) == 3
    assert covering_channel_dimension(3) == 3
    assert is_primitive_covering(3) is True


def test_wilson_loop_triviality_does_not_erase_sheet_count() -> None:
    phase = wilson_loop_phase_from_degree(3)
    assert abs(phase.real - 1.0) < 1e-12
    assert abs(phase.imag) < 1e-12
    assert is_wilson_loop_globally_trivial_for_integer_degree(3) is True
    assert sheet_count_from_degree(3) == 3
    assert deck_group_order(3) == 3


def test_simplex_and_end_h_dimensions_are_distinct() -> None:
    assert classical_simplex_relative_dimension(3) == 2
    assert coherent_end_dimension(3) == 9
    assert coherent_traceless_dimension(3) == 8
    assert active_fraction_from_dimension(3) == Fraction(8, 9)
    assert active_fraction_from_covering_degree(3) == Fraction(8, 9)
    assert active_fraction_from_covering_degree(6) == Fraction(35, 36)
    assert active_fraction_from_covering_degree(12) == Fraction(143, 144)


def test_payload_statuses_are_partial_and_candidate_safe() -> None:
    payload = audit_payload()
    assert payload["covering_map_theorem_status"] == COVERING_MAP_THEOREM_STATUS
    assert payload["channel_dimension_status"] == CHANNEL_DIMENSION_STATUS
    assert payload["wilson_loop_triviality_trap_status"] == WILSON_LOOP_TRAP_STATUS
    assert payload["lepton_8_9_consequence_status"] == LEPTON_8_9_STATUS
    assert payload["quark_covering_consequence_status"] == QUARK_COVERING_CONSEQUENCE_STATUS
    assert payload["does_wilson_loop_phase_become_trivial"] is True
    assert payload["does_covering_degree_resolve_wilson_trap"] is True
    assert payload["does_H_equal_C_Z_N_follow"] is True
    assert payload["does_EndH_not_simplex_give_8_9"] is True
    assert payload["does_this_promote_full_lepton_8_9"] is False
    assert payload["does_this_change_official_predictions"] is False
    assert payload["geometric_quantization_plus_one_hazard"] is True
    assert payload["rejected_or_limited_route_note"] == "S2_GEOMETRIC_QUANTIZATION_NOT_USED_FOR_CHANNEL_DIMENSION"


def test_quark_consequences_are_candidate_only() -> None:
    payload = audit_payload()
    rows = {row.sector: row for row in payload["sector_covering_table"]}
    assert rows["charged_lepton"].active_fraction == Fraction(8, 9)
    assert rows["up_candidate_only"].active_fraction == Fraction(35, 36)
    assert rows["down_candidate_only"].active_fraction == Fraction(143, 144)
    assert rows["up_candidate_only"].official_prediction_update is False
    assert rows["down_candidate_only"].official_prediction_update is False
    assert rows["up_candidate_only"].status == QUARK_COVERING_CONSEQUENCE_STATUS
    assert rows["down_candidate_only"].status == QUARK_COVERING_CONSEQUENCE_STATUS


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

    export_boundary_covering_map_outputs(ROOT)

    after = {path: _sha(path) for path in frozen_paths}
    assert before == after

    report_paths = [
        ROOT / "theory" / "boundary_covering_map_channel_theorem.md",
        ROOT / "theory" / "wilson_loop_triviality_vs_covering_degree.md",
        ROOT / "theory" / "coherent_residue_sheet_channel_space.md",
        ROOT / "theory" / "classical_simplex_vs_endH_stochastic_space.md",
        ROOT / "audits" / "boundary_covering_map_channel_theorem_audit.md",
        ROOT / "audits" / "boundary_covering_map_channel_theorem_audit.json",
    ]
    for path in report_paths:
        assert path.exists()

    parsed = json.loads((ROOT / "audits" / "boundary_covering_map_channel_theorem_audit.json").read_text())
    assert parsed["wilson_loop_triviality_trap_status"] == WILSON_LOOP_TRAP_STATUS
    assert parsed["official_outputs_modified"] is False
    assert parsed["safe_to_merge_as_candidate_only"] is True


def test_reports_do_not_contain_forbidden_overclaims() -> None:
    export_boundary_covering_map_outputs(ROOT)
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
        "DIM_H_EQUALS_ABS_OMEGA_COVERING_MAP_DERIVED",
        "LEPTON_8_9_CHANNEL_RULE_DERIVED",
    ]
    paths = [
        ROOT / "theory" / "boundary_covering_map_channel_theorem.md",
        ROOT / "theory" / "wilson_loop_triviality_vs_covering_degree.md",
        ROOT / "audits" / "boundary_covering_map_channel_theorem_audit.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    for phrase in forbidden:
        assert phrase not in text
