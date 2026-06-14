from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_boundary_holonomy_dimension import (  # noqa: E402
    CYCLIC_HOLONOMY_QUOTIENT_CONDITIONAL,
    DIM_H_EQUALS_ABS_OMEGA_CONDITIONAL,
    GEOMETRIC_QUANTIZATION_DIMENSION_REJECTED,
    LEPTON_CHANNEL_SPACE_CONDITIONAL_PROTECTION_OPEN,
    S2_GEOMETRIC_QUANTIZATION_NOT_USED_FOR_CHANNEL_DIMENSION,
    audit_payload,
    channel_dimension_from_holonomy,
    cyclic_group_order,
    cyclic_residue_classes,
    dim_theorem_status_object,
    export_boundary_holonomy_dimension_outputs,
    group_algebra_dimension,
    is_integer_holonomy,
    monodromy_order,
    omega_from_Arep,
    primitive_holonomy_level,
    q_from_kj,
    sector_channel_dimension,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_exact_holonomy_dimension_arithmetic() -> None:
    assert is_integer_holonomy(Fraction(3, 1)) is True
    assert is_integer_holonomy(Fraction(3, 2)) is False

    assert primitive_holonomy_level(3) == 3
    assert cyclic_group_order(6) == 6
    assert channel_dimension_from_holonomy(3) == 3
    assert channel_dimension_from_holonomy(6) == 6
    assert channel_dimension_from_holonomy(12) == 12
    assert cyclic_residue_classes(3) == [0, 1, 2]
    assert group_algebra_dimension(3) == 3
    assert monodromy_order(3) == 3


def test_mode_pair_omega_and_sector_dimensions() -> None:
    assert q_from_kj(5, 2) == 1
    assert q_from_kj(9, 3) == 3
    assert q_from_kj(6, 0) == 6
    assert q_from_kj(10, 1) == 8
    assert q_from_kj(6, 3) == 0
    assert q_from_kj(8, 2) == 4

    assert omega_from_Arep(q_from_kj(5, 2), 2, 0, 1, Fraction(-1, 2)) == 3
    assert omega_from_Arep(q_from_kj(9, 3), 3, 0, 1, Fraction(-1, 2)) == 3
    assert omega_from_Arep(q_from_kj(6, 0), 0, Fraction(1, 3), 0, Fraction(1, 2)) == 6
    assert omega_from_Arep(q_from_kj(10, 1), 1, Fraction(1, 3), 0, Fraction(1, 2)) == 6
    assert omega_from_Arep(q_from_kj(6, 3), 3, Fraction(1, 3), 0, Fraction(-1, 2)) == 12
    assert omega_from_Arep(q_from_kj(8, 2), 2, Fraction(1, 3), 0, Fraction(-1, 2)) == 12

    assert sector_channel_dimension("charged_lepton").dimension == 3
    assert sector_channel_dimension("up").dimension == 6
    assert sector_channel_dimension("down").dimension == 12


def test_dim_theorem_prefers_cyclic_monodromy_not_s2_quantization() -> None:
    status = dim_theorem_status_object()

    assert status.status == DIM_H_EQUALS_ABS_OMEGA_CONDITIONAL
    assert status.cyclic_holonomy_quotient_status == CYCLIC_HOLONOMY_QUOTIENT_CONDITIONAL
    assert status.preferred_dimension_route == "cyclic_boundary_monodromy"
    assert status.geometric_quantization_plus_one_hazard is True
    assert status.rejected_or_limited_route_note == S2_GEOMETRIC_QUANTIZATION_NOT_USED_FOR_CHANNEL_DIMENSION


def test_payload_records_conditional_closure_and_lepton_protection_open() -> None:
    payload = audit_payload()

    assert payload["boundary_holonomy_dimension_status"] == DIM_H_EQUALS_ABS_OMEGA_CONDITIONAL
    assert payload["cyclic_holonomy_quotient_status"] == CYCLIC_HOLONOMY_QUOTIENT_CONDITIONAL
    assert payload["geometric_quantization_dimension_status"] == GEOMETRIC_QUANTIZATION_DIMENSION_REJECTED
    assert payload["preferred_dimension_route"] == "cyclic_boundary_monodromy"
    assert payload["geometric_quantization_plus_one_hazard"] is True
    assert payload["rejected_or_limited_route_note"] == S2_GEOMETRIC_QUANTIZATION_NOT_USED_FOR_CHANNEL_DIMENSION
    assert payload["does_dim_H_equal_abs_Omega_follow"] is True
    assert payload["is_dim_theorem_conditional"] is True
    assert payload["does_holonomy_define_cyclic_quotient"] is True
    assert payload["does_group_algebra_define_channel_space"] is True
    assert payload["does_geometric_quantization_apply"] is False
    assert payload["does_monodromy_order_match"] is True
    assert payload["lepton_channel_space_consequence_status"] == LEPTON_CHANNEL_SPACE_CONDITIONAL_PROTECTION_OPEN
    assert payload["does_this_promote_full_lepton_8_9"] is False
    assert payload["does_this_change_official_predictions"] is False


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

    export_boundary_holonomy_dimension_outputs(ROOT)

    after = {path: _sha(path) for path in frozen_paths}
    assert before == after

    report_paths = [
        ROOT / "theory" / "boundary_holonomy_quotient_dimension_theorem.md",
        ROOT / "theory" / "cyclic_channel_space_from_holonomy.md",
        ROOT / "theory" / "group_algebra_channel_space_candidate.md",
        ROOT / "theory" / "geometric_quantization_dimension_candidate.md",
        ROOT / "theory" / "boundary_monodromy_dimension_candidate.md",
        ROOT / "theory" / "lepton_channel_space_protection_open_note.md",
        ROOT / "theory" / "sector_channel_dimensions_3_6_12.md",
        ROOT / "audits" / "boundary_holonomy_quotient_dimension_audit.md",
        ROOT / "audits" / "boundary_holonomy_quotient_dimension_audit.json",
    ]
    for path in report_paths:
        assert path.exists()

    parsed = json.loads((ROOT / "audits" / "boundary_holonomy_quotient_dimension_audit.json").read_text())
    assert parsed["official_outputs_modified"] is False
    assert parsed["frozen_predictions_modified"] is False
    assert parsed["preferred_dimension_route"] == "cyclic_boundary_monodromy"


def test_reports_do_not_contain_forbidden_overclaims() -> None:
    export_boundary_holonomy_dimension_outputs(ROOT)
    forbidden = [
        "bhsm is proven",
        "bhsm is confirmed",
        "replaces the standard model",
        "ordinary faster-than-light neutrino",
        "ordinary environmental mass-drift",
        "ordinary environmental mass drift",
        "full standard model derivation",
        "full lepton 8/9 is derived",
    ]
    paths = [
        ROOT / "theory" / "boundary_holonomy_quotient_dimension_theorem.md",
        ROOT / "audits" / "boundary_holonomy_quotient_dimension_audit.md",
        ROOT / "theory" / "geometric_quantization_dimension_candidate.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)
    for phrase in forbidden:
        assert phrase not in text
