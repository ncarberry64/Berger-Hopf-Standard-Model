from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_colored_lower_doublet_projector import (  # noqa: E402
    COLORED_LOWER_PROJECTOR_PARTIAL_DERIVATION,
    DOWN_COFAME_BONUS_PARTIAL_DERIVATION,
    NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE,
    a_from_B_L,
    audit_payload,
    b_from_T3_B,
    chi_colored_lower,
    color_normalized_baryon,
    export_colored_lower_outputs,
    lower_doublet_projector,
    omega_charged_lepton,
    omega_down,
    omega_from_sm_projector,
    omega_neutrino_candidate,
    omega_up,
    q_from_kj,
    sector_coefficients,
    sector_data,
    validate_mode_pair_constant_level,
)


def _sha(path: str) -> str:
    return hashlib.sha256(ROOT.joinpath(path).read_bytes()).hexdigest()


def test_exact_colored_lower_projector_arithmetic() -> None:
    assert color_normalized_baryon(Fraction(1, 3)) == Fraction(1)
    assert lower_doublet_projector(Fraction(-1, 2)) == Fraction(1)
    assert lower_doublet_projector(Fraction(1, 2)) == Fraction(0)
    assert chi_colored_lower(Fraction(0), Fraction(-1, 2)) == Fraction(0)
    assert chi_colored_lower(Fraction(1, 3), Fraction(1, 2)) == Fraction(0)
    assert chi_colored_lower(Fraction(1, 3), Fraction(-1, 2)) == Fraction(1)
    assert b_from_T3_B(Fraction(-1, 2), Fraction(0)) == Fraction(2)
    assert b_from_T3_B(Fraction(1, 2), Fraction(1, 3)) == Fraction(-2)
    assert b_from_T3_B(Fraction(-1, 2), Fraction(1, 3)) == Fraction(4)
    assert a_from_B_L(Fraction(0), Fraction(1)) == Fraction(-1)
    assert a_from_B_L(Fraction(1, 3), Fraction(0)) == Fraction(1)


def test_sector_coefficients_and_neutrino_candidate() -> None:
    assert sector_coefficients("charged_lepton").a == Fraction(-1)
    assert sector_coefficients("charged_lepton").b == Fraction(2)
    assert sector_coefficients("charged_lepton").chi_colored_lower == Fraction(0)
    assert sector_coefficients("up").a == Fraction(1)
    assert sector_coefficients("up").b == Fraction(-2)
    assert sector_coefficients("up").chi_colored_lower == Fraction(0)
    assert sector_coefficients("down").a == Fraction(1)
    assert sector_coefficients("down").b == Fraction(4)
    assert sector_coefficients("down").chi_colored_lower == Fraction(1)
    assert sector_coefficients("neutrino").a == Fraction(-1)
    assert sector_coefficients("neutrino").b == Fraction(-2)
    assert sector_coefficients("neutrino").status == NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE
    assert sector_data("neutrino").candidate_only is True
    try:
        sector_data("bad")
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("unknown sector should raise")


def test_omega_formula_recovers_charged_mode_pairs() -> None:
    assert q_from_kj(5, 2) == 1
    assert omega_from_sm_projector(1, 2, Fraction(0), Fraction(1), Fraction(-1, 2)) == Fraction(3)
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


def test_payload_status_and_closure_discipline() -> None:
    payload = audit_payload()
    assert payload["official_outputs_modified"] is False
    assert payload["frozen_predictions_modified"] is False
    assert payload["prs_opened"] is False
    assert payload["colored_lower_projector_status"] == COLORED_LOWER_PROJECTOR_PARTIAL_DERIVATION
    assert payload["down_coframe_bonus_status"] == DOWN_COFAME_BONUS_PARTIAL_DERIVATION
    assert payload["does_chi_d_follow_from_B_T3"] is True
    assert payload["does_formula_reproduce_omega_l_u_d"] is True
    assert payload["does_this_close_down_bonus"] is False
    assert payload["derived_components"] == ()
    assert "independent_chi_d_indicator_replaced_by_B_T3_projector" in payload["blockers_closed"]
    assert payload["neutrino_candidate"]["ordinary_FTL_claim"] is False
    assert payload["safe_to_merge_as_candidate_only"] is True


def test_official_outputs_and_frozen_files_unchanged_by_export() -> None:
    frozen_md = _sha("docs/frozen_predictions.md")
    frozen_json = _sha("docs/frozen_predictions.json")
    payload = export_colored_lower_outputs(ROOT)
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
    export_colored_lower_outputs(ROOT)
    path = ROOT / "audits" / "colored_lower_doublet_coframe_bonus_audit.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "official_outputs_modified",
        "frozen_predictions_modified",
        "prs_opened",
        "colored_lower_projector_status",
        "down_coframe_bonus_status",
        "q_coefficient_status",
        "j_coefficient_status",
        "does_chi_d_follow_from_B_T3",
        "does_formula_reproduce_omega_l_u_d",
        "does_this_close_down_bonus",
        "boundary_connection_consequence_status",
        "lepton_8_9_consequence_status",
        "neutrino_projector_consequence_status",
        "blockers_closed",
        "blockers_remaining",
        "derived_components",
        "candidate_components",
        "missing_assumptions",
        "forbidden_claims_absent",
        "safe_to_merge_as_candidate_only",
    }
    assert required.issubset(data)
    assert data["forbidden_claims_absent"] is True


def test_no_forbidden_claims_in_new_reports() -> None:
    export_colored_lower_outputs(ROOT)
    paths = [
        "theory/colored_lower_doublet_coframe_bonus.md",
        "audits/colored_lower_doublet_coframe_bonus_audit.md",
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
