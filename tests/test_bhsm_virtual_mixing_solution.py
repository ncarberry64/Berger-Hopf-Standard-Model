import json
from math import isclose
from pathlib import Path

from bhsm_v1 import build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from bhsm_virtual_mixing_solution import (
    CANDIDATE_MIXING_EXPONENT,
    J_DAMAGE_THRESHOLD,
    NON_23_DAMAGE_THRESHOLD,
    REQUIRED_CANDIDATE_WORDING,
    STATUS,
    Z_MIX_23,
    Z_VIRT_U2,
    build_mixing_candidate_report,
    export_audit_json,
    export_audit_markdown,
    export_mixing_candidate_json,
    export_mixing_candidate_markdown,
)


ROOT = Path(__file__).resolve().parents[1]


def _residuals(state):
    return {residual.quantity: residual for residual in state.residuals}


def test_candidate_constants_are_predeclared():
    assert Z_VIRT_U2 == 0.5
    assert CANDIDATE_MIXING_EXPONENT == 1 / 16
    assert isclose(Z_MIX_23, Z_VIRT_U2 ** (1 / 16))
    assert NON_23_DAMAGE_THRESHOLD == 0.01
    assert J_DAMAGE_THRESHOLD == 0.02


def test_only_s23_changes_in_candidate_state():
    report = build_mixing_candidate_report()

    assert report.status == STATUS
    assert report.candidate.sin_theta_23 == report.baseline.sin_theta_23 * Z_MIX_23
    assert isclose(report.candidate.sin_theta_12, report.baseline.sin_theta_12)
    assert isclose(report.candidate.sin_theta_13, report.baseline.sin_theta_13)
    assert isclose(report.candidate.delta_cp, report.baseline.delta_cp)


def test_official_dressed_ct_output_remains_unchanged():
    dressed = build_bhsm_dressed_v1_candidate()
    comparison = compare_bhsm_v1_branches()
    changed = [row for row in comparison["rows"] if row["changed"]]

    assert dressed.outputs["up_quark_ratios"]["middle"] == 0.004155250277034144
    assert changed == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]


def test_frozen_prediction_docs_do_not_contain_candidate_branch():
    frozen_md = ROOT.joinpath("docs/frozen_predictions.md").read_text(encoding="utf-8")
    frozen_json = ROOT.joinpath("docs/frozen_predictions.json").read_text(encoding="utf-8")

    assert "BHSM_MIXING_DRESSED_V1_CANDIDATE" not in frozen_md
    assert "BHSM_MIXING_DRESSED_V1_CANDIDATE" not in frozen_json
    assert "s23_candidate" not in frozen_md
    assert "s23_candidate" not in frozen_json


def test_candidate_improves_vcb_and_vts_without_damage_flags():
    report = build_mixing_candidate_report()
    baseline = _residuals(report.baseline)
    candidate = _residuals(report.candidate)

    assert report.improves_vcb is True
    assert report.improves_vts is True
    assert candidate["Vcb"].relative_error < baseline["Vcb"].relative_error
    assert candidate["Vts"].relative_error < baseline["Vts"].relative_error
    assert report.non_23_damage_flag is False
    assert report.j_damage_flag is False


def test_candidate_status_and_wording_are_explicit(tmp_path):
    audit_md = tmp_path / "audit.md"
    audit_json = tmp_path / "audit.json"
    candidate_md = tmp_path / "candidate.md"
    candidate_json = tmp_path / "candidate.json"

    export_audit_markdown(audit_md)
    export_audit_json(audit_json)
    export_mixing_candidate_markdown(candidate_md)
    export_mixing_candidate_json(candidate_json)

    audit_text = audit_md.read_text(encoding="utf-8")
    candidate_text = candidate_md.read_text(encoding="utf-8")
    payload = json.loads(candidate_json.read_text(encoding="utf-8"))
    assert "CANDIDATE_NOT_OFFICIAL" in audit_text
    assert "CANDIDATE_EXPONENT" in audit_text
    assert REQUIRED_CANDIDATE_WORDING in candidate_text
    assert payload["status"] == "CANDIDATE_NOT_OFFICIAL"
    assert payload["candidate_mixing_exponent"] == 1 / 16


def test_no_official_release_claim_is_made():
    report = build_mixing_candidate_report()
    text = " ".join(report.limitations)

    assert "not part of the official frozen release" in text
    assert "not a proven BHSM result" in text
