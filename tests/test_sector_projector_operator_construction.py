from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_sector_projector_operator import (  # noqa: E402
    COLOR_COFRAME_OPERATOR_SUPPORTED,
    COLORED_LOWER_PROJECTOR_PARTIAL,
    NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE,
    SECTOR_PROJECTOR_OPERATOR_PARTIAL,
    WEAK_LOWER_PROJECTOR_SUPPORTED,
    audit_payload,
    color_coframe_operator,
    colored_lower_projector,
    export_sector_projector_operator_outputs,
    j_orientation_operator,
    lower_weak_projector,
    omega_charged_lepton,
    omega_down,
    omega_from_operator,
    omega_neutrino_candidate,
    omega_up,
    q_from_kj,
    q_orientation_operator,
    representation_for_sector,
    sector_projector_coefficients,
    validate_mode_pair_constant_level,
)


def _sha(path: str) -> str:
    return hashlib.sha256(ROOT.joinpath(path).read_bytes()).hexdigest()


def test_exact_operator_values() -> None:
    assert color_coframe_operator(Fraction(0)) == Fraction(0)
    assert color_coframe_operator(Fraction(1, 3)) == Fraction(1)
    assert lower_weak_projector(Fraction(1, 2)) == Fraction(0)
    assert lower_weak_projector(Fraction(-1, 2)) == Fraction(1)
    assert colored_lower_projector(Fraction(0), Fraction(-1, 2)) == Fraction(0)
    assert colored_lower_projector(Fraction(1, 3), Fraction(1, 2)) == Fraction(0)
    assert colored_lower_projector(Fraction(1, 3), Fraction(-1, 2)) == Fraction(1)
    assert q_orientation_operator(Fraction(0), Fraction(1)) == Fraction(-1)
    assert q_orientation_operator(Fraction(1, 3), Fraction(0)) == Fraction(1)
    assert j_orientation_operator(Fraction(0), Fraction(-1, 2)) == Fraction(2)
    assert j_orientation_operator(Fraction(1, 3), Fraction(1, 2)) == Fraction(-2)
    assert j_orientation_operator(Fraction(1, 3), Fraction(-1, 2)) == Fraction(4)


def test_sector_coefficients_and_neutrino_candidate() -> None:
    assert sector_projector_coefficients("charged_lepton").a == Fraction(-1)
    assert sector_projector_coefficients("charged_lepton").b == Fraction(2)
    assert sector_projector_coefficients("up").a == Fraction(1)
    assert sector_projector_coefficients("up").b == Fraction(-2)
    assert sector_projector_coefficients("down").a == Fraction(1)
    assert sector_projector_coefficients("down").b == Fraction(4)
    assert sector_projector_coefficients("neutrino").a == Fraction(-1)
    assert sector_projector_coefficients("neutrino").b == Fraction(-2)
    assert sector_projector_coefficients("neutrino").status == NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE
    assert representation_for_sector("neutrino").candidate_only is True
    try:
        representation_for_sector("bad")
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("unknown sector should raise")


def test_operator_omega_functions_recover_mode_pairs() -> None:
    assert q_from_kj(5, 2) == 1
    assert omega_from_operator(1, 2, Fraction(0), Fraction(1), Fraction(-1, 2)) == Fraction(3)
    assert omega_charged_lepton(q_from_kj(5, 2), 2) == Fraction(3)
    assert omega_charged_lepton(q_from_kj(9, 3), 3) == Fraction(3)
    assert omega_up(q_from_kj(6, 0), 0) == Fraction(6)
    assert omega_up(q_from_kj(10, 1), 1) == Fraction(6)
    assert omega_down(q_from_kj(6, 3), 3) == Fraction(12)
    assert omega_down(q_from_kj(8, 2), 2) == Fraction(12)
    assert omega_neutrino_candidate(1, 2) == Fraction(-5)


def test_mode_pair_validation() -> None:
    assert validate_mode_pair_constant_level("charged_lepton")["level"] == Fraction(3)
    assert validate_mode_pair_constant_level("up")["level"] == Fraction(6)
    assert validate_mode_pair_constant_level("down")["level"] == Fraction(12)
    try:
        validate_mode_pair_constant_level("neutrino")
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("neutrino has no official charged mode pair")


def test_payload_statuses() -> None:
    payload = audit_payload()
    assert payload["official_outputs_modified"] is False
    assert payload["frozen_predictions_modified"] is False
    assert payload["prs_opened"] is False
    assert payload["sector_projector_operator_status"] == SECTOR_PROJECTOR_OPERATOR_PARTIAL
    assert payload["color_coframe_operator_status"] == COLOR_COFRAME_OPERATOR_SUPPORTED
    assert payload["weak_lower_projector_status"] == WEAK_LOWER_PROJECTOR_SUPPORTED
    assert payload["colored_lower_projector_status"] == COLORED_LOWER_PROJECTOR_PARTIAL
    assert payload["does_operator_reproduce_omega_l_u_d"] is True
    assert payload["does_3B_act_as_color_coframe_operator"] is True
    assert payload["does_lower_projector_follow_from_T3"] is True
    assert payload["does_colored_lower_projector_follow"] is True
    assert payload["derived_components"] == ()
    assert payload["neutrino_candidate"]["ordinary_FTL_claim"] is False
    assert payload["safe_to_merge_as_candidate_only"] is True


def test_official_outputs_and_frozen_files_unchanged_by_export() -> None:
    frozen_md = _sha("docs/frozen_predictions.md")
    frozen_json = _sha("docs/frozen_predictions.json")
    payload = export_sector_projector_operator_outputs(ROOT)
    assert _sha("docs/frozen_predictions.md") == frozen_md
    assert _sha("docs/frozen_predictions.json") == frozen_json
    sanity = payload["frozen_sanity"]
    assert sanity["BHSM_BARE_V1_unchanged"] is True
    assert sanity["BHSM_DRESSED_V1_CANDIDATE_unchanged"] is True
    assert sanity["dressed_branch_changes_only_c_over_t"] is True
    assert sanity["u_over_t_unchanged"] is True
    assert sanity["ckm_sin_theta_13_unchanged"] is True
    changed = [row for row in payload["official_branch_comparison"]["rows"] if row["changed"]]
    assert [row["quantity"] for row in changed] == ["c/t"]


def test_audit_json_validates() -> None:
    export_sector_projector_operator_outputs(ROOT)
    path = ROOT / "audits" / "sector_projector_operator_construction_audit.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "official_outputs_modified",
        "frozen_predictions_modified",
        "prs_opened",
        "sector_projector_operator_status",
        "color_coframe_operator_status",
        "weak_lower_projector_status",
        "colored_lower_projector_status",
        "q_orientation_operator_status",
        "j_orientation_operator_status",
        "boundary_connection_consequence_status",
        "lepton_8_9_consequence_status",
        "pure_fiber_consequence_status",
        "ckm_consequence_status",
        "neutrino_consequence_status",
        "does_operator_reproduce_omega_l_u_d",
        "does_3B_act_as_color_coframe_operator",
        "does_lower_projector_follow_from_T3",
        "does_colored_lower_projector_follow",
        "blockers_closed",
        "blockers_remaining",
        "missing_assumptions",
        "forbidden_claims_absent",
        "safe_to_merge_as_candidate_only",
    }
    assert required.issubset(data)
    assert data["forbidden_claims_absent"] is True


def test_no_forbidden_claims_in_new_reports() -> None:
    export_sector_projector_operator_outputs(ROOT)
    paths = [
        "theory/sector_projector_operator_construction.md",
        "audits/sector_projector_operator_construction_audit.md",
        "theory/sector_projected_boundary_connection_operator_candidate.md",
    ]
    text = "\n".join(ROOT.joinpath(path).read_text(encoding="utf-8").lower() for path in paths)
    forbidden = [
        "ordinary faster-than-light neutrino claim is made",
        "ordinary environmental mass-drift claim",
        "standard model replacement",
        "bhsm is proven",
        "bhsm is confirmed",
        "full standard model derivation claim is made",
    ]
    for phrase in forbidden:
        assert phrase not in text
    assert "no ordinary superluminal neutrino claim is made" in text
    assert "no ordinary environmental mass drift claim is made" in text
