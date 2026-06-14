import json
from pathlib import Path

from bhsm_v1 import compare_bhsm_v1_branches
from light_up_ratio_tension import (
    EXPLORATORY_CANDIDATE,
    LIGHT_UP_DRESSING_CANDIDATE_NOT_OFFICIAL,
    U_T_FAILURE_NOT_REPAIRED,
    U_T_TENSION_EXPLAINED_BY_INPUT_UNCERTAINTY,
    U_T_WARNING_CONFIRMED,
    audit_payload,
    exploratory_light_up_candidates,
    global_rescale_diagnostic,
    tension_result,
)


ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    U_T_WARNING_CONFIRMED,
    U_T_TENSION_EXPLAINED_BY_INPUT_UNCERTAINTY,
    LIGHT_UP_DRESSING_CANDIDATE_NOT_OFFICIAL,
    U_T_FAILURE_NOT_REPAIRED,
    "EXTERNAL_INPUT_REQUIRED",
}


def test_light_up_audit_outputs_exist_and_json_validates():
    paths = [
        ROOT / "theory/light_up_ratio_tension_note.md",
        ROOT / "audits/light_up_ratio_tension_audit.py",
        ROOT / "audits/light_up_ratio_tension_audit.md",
        ROOT / "audits/light_up_ratio_tension_audit.json",
    ]
    for path in paths:
        assert path.exists()

    payload = json.loads((ROOT / "audits/light_up_ratio_tension_audit.json").read_text())
    assert payload["classification"] in ALLOWED
    assert payload["u_over_t"]["ratio"] == "u/t"


def test_u_t_warning_is_confirmed_without_official_repair():
    result = tension_result(ROOT / "data/reference_common_scale_quark_ratios_mz.json")

    assert result.classification == U_T_WARNING_CONFIRMED
    assert result.u_t_warning_confirmed is True
    assert result.global_rescale_allowed is False
    assert result.candidate_status in {EXPLORATORY_CANDIDATE, "NO_OFFICIAL_REPAIR"}


def test_global_rescale_is_rejected_if_it_damages_other_ratios():
    diagnostic = global_rescale_diagnostic(ROOT / "data/reference_common_scale_quark_ratios_mz.json")

    assert diagnostic["global_rescale_allowed"] is False
    assert set(diagnostic["damaged_ratios"])
    assert {"c/t", "s/b", "d/b"}.intersection(set(diagnostic["damaged_ratios"]))


def test_candidate_repair_cannot_be_official():
    candidates = exploratory_light_up_candidates(ROOT / "data/reference_common_scale_quark_ratios_mz.json")

    assert any(row.status == EXPLORATORY_CANDIDATE for row in candidates)
    for row in candidates:
        if row.name != "no_correction":
            assert row.changes_official_u_over_t is True
            assert row.changes_ckm_sin_theta_13 is True
            assert row.status == EXPLORATORY_CANDIDATE


def test_official_branches_and_u_over_t_unchanged():
    comparison = compare_bhsm_v1_branches()
    changed = [row for row in comparison["rows"] if row["changed"]]

    assert comparison["branches"] == ("BHSM_BARE_V1", "BHSM_DRESSED_V1_CANDIDATE")
    assert changed == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]
    assert next(row for row in comparison["rows"] if row["quantity"] == "u/t")["changed"] is False
    assert next(row for row in comparison["rows"] if row["quantity"] == "sin_theta_13")[
        "changed"
    ] is False


def test_frozen_prediction_files_unchanged_by_light_up_audit():
    frozen_md = (ROOT / "docs/frozen_predictions.md").read_text()
    frozen_json = (ROOT / "docs/frozen_predictions.json").read_text()

    assert "light_up_ratio_tension" not in frozen_md
    assert "light_up_ratio_tension" not in frozen_json
    assert "U_T_WARNING_CONFIRMED" not in frozen_md
    assert "U_T_WARNING_CONFIRMED" not in frozen_json


def test_no_forbidden_claims_in_light_up_outputs():
    text = "\n".join(
        [
            (ROOT / "theory/light_up_ratio_tension_note.md").read_text(),
            (ROOT / "audits/light_up_ratio_tension_audit.md").read_text(),
            (ROOT / "audits/light_up_ratio_tension_audit.json").read_text(),
        ]
    ).lower()
    forbidden = (
        "bhsm is proven",
        "bhsm is confirmed",
        "replaces the standard model",
        "official light-up dressing",
    )
    for phrase in forbidden:
        assert phrase not in text


def test_common_scale_status_does_not_change():
    payload = audit_payload(ROOT / "data/reference_common_scale_quark_ratios_mz.json")

    assert payload["common_scale_quark_status_changes"] is False
    assert payload["repair_official"] is False
    assert payload["official_u_over_t_changed"] is False
    assert payload["official_outputs_modified"] is False
    assert payload["frozen_predictions_modified"] is False
