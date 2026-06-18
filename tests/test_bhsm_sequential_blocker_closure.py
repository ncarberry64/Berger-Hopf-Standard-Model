import json
from pathlib import Path

from bhsm_sequential_blocker_closure import (
    BLOCKER_ORDER,
    BOUNDARY_MODE_PAIR_INVARIANT_DERIVED_ACTION_OPEN,
    audit_payload,
    ordered_blocker_attempts,
)
from bhsm_v1 import compare_bhsm_v1_branches


ROOT = Path(__file__).resolve().parents[1]


def test_sequential_closure_json_validates():
    payload = json.loads(ROOT.joinpath("audits/bhsm_sequential_blocker_closure_audit.json").read_text())

    assert tuple(payload["blocker_order"]) == BLOCKER_ORDER
    assert payload["official_outputs_modified"] is False
    assert payload["frozen_predictions_modified"] is False
    assert payload["prs_opened"] is False
    assert payload["forbidden_claims_absent"] is True
    assert payload["safe_to_merge_as_candidate_only"] is True


def test_blockers_attempted_in_order_and_not_forced_closed():
    payload = audit_payload()
    attempts = ordered_blocker_attempts()

    assert tuple(attempt.blocker_id for attempt in attempts) == BLOCKER_ORDER
    assert payload["blockers_closed"] == ()
    assert payload["blockers_remaining"] == BLOCKER_ORDER
    assert set(payload["candidate_components"]) == set(BLOCKER_ORDER)
    assert payload["derived_components"] == ()


def test_expected_candidate_statuses_are_preserved():
    attempts = {attempt.blocker_id: attempt for attempt in ordered_blocker_attempts()}

    assert attempts["lepton_8alpha_9pi"].status == "SCREENED_ALPHA_PI_LEPTON_CANDIDATE_NOT_DERIVED"
    assert attempts["pure_fiber_one_half"].status == "PURE_FIBER_DOUBLET_CANDIDATE_NOT_DERIVED"
    assert attempts["boundary_action"].status == BOUNDARY_MODE_PAIR_INVARIANT_DERIVED_ACTION_OPEN
    assert attempts["ckm_one_sixteenth"].status == "CKM_FOUR_PROJECTION_CANDIDATE_NOT_DERIVED"
    assert attempts["neutrino_pmns"].status == "NEUTRINO_LEAKAGE_LEDGER_CANDIDATE_ONLY"
    assert all(attempt.closed is False for attempt in attempts.values())
    assert all(attempt.official_outputs_changed is False for attempt in attempts.values())


def test_frozen_files_and_official_branches_unchanged():
    frozen_md = ROOT.joinpath("docs/frozen_predictions.md").read_text()
    frozen_json = ROOT.joinpath("docs/frozen_predictions.json").read_text()
    comparison = compare_bhsm_v1_branches()
    changed = [row for row in comparison["rows"] if row["changed"]]

    assert "BHSM_SEQUENTIAL_BLOCKER_CLOSURE" not in frozen_md
    assert "BHSM_SEQUENTIAL_BLOCKER_CLOSURE" not in frozen_json
    assert changed == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]
    assert audit_payload()["frozen_sanity"]["u_over_t_unchanged"] is True
    assert audit_payload()["frozen_sanity"]["ckm_sin_theta_13_unchanged"] is True


def test_no_forbidden_claims_or_mass_drift_language():
    text = "\n".join(
        [
            ROOT.joinpath("docs/BHSM_SEQUENTIAL_BLOCKER_CLOSURE.md").read_text(),
            ROOT.joinpath("audits/bhsm_sequential_blocker_closure_audit.md").read_text(),
            ROOT.joinpath("theory/neutrino_leakage_pmns_candidate_ledger.md").read_text(),
        ]
    ).lower()

    assert "ordinary faster-than-light neutrino claim is made" in text
    assert "environmental mass-drift mechanism is introduced" in text
    forbidden = (
        "bhsm is proven",
        "bhsm is confirmed",
        "replaces the standard model",
        "standard model replacement",
        "official outputs modified: `true`",
        "closed: `true`",
    )
    for phrase in forbidden:
        assert phrase not in text


def test_optional_theory_notes_exist():
    for path in (
        "theory/lepton_screened_alpha_pi_derivation_attempt.md",
        "theory/pure_fiber_doublet_derivation_attempt.md",
        "theory/boundary_action_derivation_attempt.md",
        "theory/ckm_four_projection_derivation_attempt.md",
        "theory/neutrino_leakage_pmns_candidate_ledger.md",
    ):
        assert ROOT.joinpath(path).is_file()
