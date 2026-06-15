from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_boundary_action_to_rep_connection import (  # noqa: E402
    ACTION_TO_PHASE_MAP_STATUS,
    AJ_PERIOD_STATUS,
    AQ_PERIOD_STATUS,
    BOUNDARY_ACTION_TO_AREP_STATUS,
    BOUNDARY_SOURCE_TERMS_STATUS,
    CLAIM_HYGIENE_STATUS,
    COLORED_LOWER_PROJECTOR_STATUS,
    DOWN_CONSEQUENCE_STATUS,
    LEPTON_CONSEQUENCE_STATUS,
    OJ_STATUS,
    OMEGA_AS_DEGREE_STATUS,
    OQ_STATUS,
    SECTOR_CONNECTION_STATUS,
    UP_CONSEQUENCE_STATUS,
    Oq_from_B_L,
    Oj_from_B_T3,
    audit_payload,
    boundary_phase_degree_from_periods,
    colored_lower_projector,
    down_omega_from_kj,
    down_operator_pair,
    export_boundary_action_outputs,
    lepton_omega_from_kj,
    lepton_operator_pair,
    omega_from_Oq_Oj_q_j,
    q_from_kj,
    sector_connection_symbolic,
    sector_operator_pair,
    up_omega_from_kj,
    up_operator_pair,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_boundary_source_operators_have_expected_values() -> None:
    assert Oq_from_B_L(0, 1) == Fraction(-1)
    assert Oq_from_B_L(Fraction(1, 3), 0) == Fraction(1)

    assert colored_lower_projector(0, Fraction(-1, 2)) == Fraction(0)
    assert colored_lower_projector(Fraction(1, 3), Fraction(1, 2)) == Fraction(0)
    assert colored_lower_projector(Fraction(1, 3), Fraction(-1, 2)) == Fraction(1)

    assert Oj_from_B_T3(0, Fraction(-1, 2)) == Fraction(2)
    assert Oj_from_B_T3(Fraction(1, 3), Fraction(1, 2)) == Fraction(-2)
    assert Oj_from_B_T3(Fraction(1, 3), Fraction(-1, 2)) == Fraction(4)


def test_sector_operator_pairs_recover_omega_coefficients() -> None:
    assert lepton_operator_pair() == (Fraction(-1), Fraction(2))
    assert up_operator_pair() == (Fraction(1), Fraction(-2))
    assert down_operator_pair() == (Fraction(1), Fraction(4))

    assert sector_operator_pair(0, 1, Fraction(-1, 2)) == lepton_operator_pair()
    assert sector_operator_pair(Fraction(1, 3), 0, Fraction(1, 2)) == up_operator_pair()
    assert sector_operator_pair(Fraction(1, 3), 0, Fraction(-1, 2)) == down_operator_pair()


def test_q_and_omega_recover_fixed_mode_ledgers() -> None:
    assert q_from_kj(5, 2) == 1
    assert q_from_kj(9, 3) == 3
    assert q_from_kj(6, 0) == 6
    assert q_from_kj(10, 1) == 8
    assert q_from_kj(6, 3) == 0
    assert q_from_kj(8, 2) == 4

    for k, j in ((5, 2), (9, 3)):
        assert lepton_omega_from_kj(k, j) == Fraction(3)

    for k, j in ((6, 0), (10, 1)):
        assert up_omega_from_kj(k, j) == Fraction(6)

    for k, j in ((6, 3), (8, 2)):
        assert down_omega_from_kj(k, j) == Fraction(12)


def test_boundary_phase_degree_checks_match_mode_omega() -> None:
    checks = {
        "lepton_muon": boundary_phase_degree_from_periods(-1, 2, 1, 2),
        "lepton_electron": boundary_phase_degree_from_periods(-1, 2, 3, 3),
        "up_middle": boundary_phase_degree_from_periods(1, -2, 6, 0),
        "up_light": boundary_phase_degree_from_periods(1, -2, 8, 1),
        "down_middle": boundary_phase_degree_from_periods(1, 4, 0, 3),
        "down_light": boundary_phase_degree_from_periods(1, 4, 4, 2),
    }
    assert checks == {
        "lepton_muon": Fraction(3),
        "lepton_electron": Fraction(3),
        "up_middle": Fraction(6),
        "up_light": Fraction(6),
        "down_middle": Fraction(12),
        "down_light": Fraction(12),
    }

    assert omega_from_Oq_Oj_q_j(-1, 2, 1, 2) == Fraction(3)
    assert sector_connection_symbolic(-1, 2) == "A_f = (-1) A_q + (2) A_j"


def test_audit_statuses_are_partial_and_candidate_safe() -> None:
    payload = audit_payload()

    assert payload["boundary_action_to_Arep_status"] == BOUNDARY_ACTION_TO_AREP_STATUS
    assert payload["boundary_source_terms_status"] == BOUNDARY_SOURCE_TERMS_STATUS
    assert payload["Oq_status"] == OQ_STATUS
    assert payload["Oj_status"] == OJ_STATUS
    assert payload["colored_lower_projector_status"] == COLORED_LOWER_PROJECTOR_STATUS
    assert payload["Aq_period_status"] == AQ_PERIOD_STATUS
    assert payload["Aj_period_status"] == AJ_PERIOD_STATUS
    assert payload["sector_connection_status"] == SECTOR_CONNECTION_STATUS
    assert payload["action_to_phase_map_status"] == ACTION_TO_PHASE_MAP_STATUS
    assert payload["omega_as_degree_status"] == OMEGA_AS_DEGREE_STATUS
    assert payload["lepton_consequence_status"] == LEPTON_CONSEQUENCE_STATUS
    assert payload["up_consequence_status"] == UP_CONSEQUENCE_STATUS
    assert payload["down_consequence_status"] == DOWN_CONSEQUENCE_STATUS
    assert payload["claim_hygiene_status"] == CLAIM_HYGIENE_STATUS

    assert payload["does_boundary_action_generate_Arep"] is True
    assert payload["does_degree_equal_Omega"] is True
    assert payload["does_this_promote_full_BHSM"] is False
    assert payload["does_this_claim_full_SM_derivation"] is False
    assert payload["does_this_change_official_predictions"] is False
    assert payload["does_this_change_frozen_predictions"] is False
    assert payload["safe_to_merge_as_candidate_only"] is True
    assert payload["open_blockers"]
    assert payload["missing_assumptions"] == payload["open_blockers"]

    serialized = json.dumps(payload, default=str)
    assert "BOUNDARY_ACTION_TO_A_REP_DERIVED" not in serialized
    assert "FULL_BHSM_THEOREM_PACKAGE_COMPLETE" not in serialized


def test_frozen_sanity_remains_unchanged() -> None:
    sanity = audit_payload()["frozen_sanity"]

    assert sanity["BHSM_BARE_V1_unchanged"] is True
    assert sanity["BHSM_DRESSED_V1_CANDIDATE_unchanged"] is True
    assert sanity["a_unchanged"] is True
    assert sanity["S_unchanged"] is True
    assert sanity["dressed_branch_changes_only_c_over_t"] is True
    assert sanity["u_over_t_unchanged"] is True
    assert sanity["ckm_sin_theta_13_unchanged"] is True


def test_export_writes_valid_reports_without_touching_frozen_predictions() -> None:
    frozen_paths = [
        ROOT / "docs" / "frozen_predictions.md",
        ROOT / "docs" / "frozen_predictions.json",
    ]
    before = {path: _sha(path) for path in frozen_paths}

    payload = export_boundary_action_outputs(ROOT)

    after = {path: _sha(path) for path in frozen_paths}
    assert before == after
    assert payload["official_outputs_modified"] is False
    assert payload["frozen_predictions_modified"] is False

    report_paths = [
        ROOT / "theory" / "boundary_action_to_rep_connection.md",
        ROOT / "theory" / "boundary_action_source_terms_for_Aq_Aj.md",
        ROOT / "theory" / "Oq_boundary_charge_derivation.md",
        ROOT / "theory" / "Oj_weak_isospin_projector_derivation.md",
        ROOT / "theory" / "Aq_Aj_period_normalization_status.md",
        ROOT / "theory" / "action_variation_to_boundary_phase_map.md",
        ROOT / "audits" / "boundary_action_to_rep_connection_audit.md",
        ROOT / "audits" / "boundary_action_to_rep_connection_audit.json",
    ]
    for path in report_paths:
        assert path.exists()

    parsed = json.loads((ROOT / "audits" / "boundary_action_to_rep_connection_audit.json").read_text())
    assert parsed["boundary_action_to_Arep_status"] == BOUNDARY_ACTION_TO_AREP_STATUS
    assert parsed["does_this_change_official_predictions"] is False
    assert parsed["forbidden_claims_absent"] is True


def test_reports_do_not_contain_forbidden_overclaims() -> None:
    export_boundary_action_outputs(ROOT)
    forbidden = [
        "full standard model derivation claim",
        "standard model replacement claim",
        "completed full bhsm proof claim",
        "official lepton prediction update",
        "official quark prediction update",
        "official u/t correction",
        "official ckm correction",
        "official down-sector dressing update",
        "no-parameter-tuning full-theory claim",
        "ordinary faster-than-light neutrino claim",
        "ordinary environmental mass-drift claim",
        "hidden retuning",
    ]
    paths = [
        ROOT / "theory" / "boundary_action_to_rep_connection.md",
        ROOT / "theory" / "boundary_action_source_terms_for_Aq_Aj.md",
        ROOT / "theory" / "Oq_boundary_charge_derivation.md",
        ROOT / "theory" / "Oj_weak_isospin_projector_derivation.md",
        ROOT / "theory" / "Aq_Aj_period_normalization_status.md",
        ROOT / "theory" / "action_variation_to_boundary_phase_map.md",
        ROOT / "audits" / "boundary_action_to_rep_connection_audit.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)
    for phrase in forbidden:
        assert phrase not in text
