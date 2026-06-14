import json
from pathlib import Path

from bhsm_v1 import compare_bhsm_v1_branches
from common_scale_quark_rg_closure import (
    COMMON_SCALE_RG_VALIDATED_WARNING,
    EXTERNAL_INPUT_REQUIRED,
    closure_audit_payload,
    compare_branch_to_common_scale,
    load_common_scale_reference,
    reference_is_validated,
)


ROOT = Path(__file__).resolve().parents[1]


def test_reference_common_scale_quark_ratios_mz_validates():
    reference = load_common_scale_reference(ROOT / "data/reference_common_scale_quark_ratios_mz.json")

    assert reference["status"] == "VALIDATED_COMMON_SCALE_REFERENCE"
    assert reference["scale"] == "M_Z = 91.1876 GeV"
    assert "MSbar" in reference["scheme"]
    assert reference["source_note"]
    assert reference["source_citation_text"]
    assert reference_is_validated(reference) is True
    for ratio in ("u/t", "c/t", "d/b", "s/b"):
        assert reference["ratios"][ratio]["value"] > 0
        assert "uncertainty" in reference["ratios"][ratio]


def test_common_scale_quark_rg_audit_json_validates():
    payload = json.loads(ROOT.joinpath("audits/common_scale_quark_rg_closure_audit.json").read_text())

    assert payload["status"] == "CLOSED_SOLVED"
    assert payload["blocker"] is None
    assert payload["classification"] == COMMON_SCALE_RG_VALIDATED_WARNING
    assert payload["common_scale_input_validated"] is True
    assert payload["closes_common_scale_input_blocker"] is True
    assert payload["common_scale_quark_precision_claimable"] is False
    assert payload["mixed_scale_used_as_precision_reference"] is False
    assert payload["branch_summary"]["real_tensions"] == ["u/t"]


def test_closure_false_if_source_status_external_input_required():
    reference = {
        "status": EXTERNAL_INPUT_REQUIRED,
        "scale": "M_Z",
        "scheme": "MSbar",
        "source_note": "missing",
        "source_citation_text": "missing",
        "validated_common_scale": False,
        "ratios": {},
    }
    rows = compare_branch_to_common_scale(
        "BHSM_BARE_V1",
        {"c/t": 0.1, "u/t": 0.01, "s/b": 0.02, "d/b": 0.001},
        reference,
    )

    assert all(row.classification == EXTERNAL_INPUT_REQUIRED for row in rows)
    assert all(row.reference is None for row in rows)


def test_dressed_candidate_still_changes_only_c_over_t():
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


def test_frozen_prediction_files_unchanged_by_common_scale_audit():
    frozen_md = ROOT.joinpath("docs/frozen_predictions.md").read_text()
    frozen_json = ROOT.joinpath("docs/frozen_predictions.json").read_text()

    assert "reference_common_scale_quark_ratios_mz" not in frozen_md
    assert "reference_common_scale_quark_ratios_mz" not in frozen_json
    assert "COMMON_SCALE_RG_VALIDATED_WARNING" not in frozen_md
    assert "COMMON_SCALE_RG_VALIDATED_WARNING" not in frozen_json


def test_no_forbidden_claims_in_common_scale_outputs():
    text = "\n".join(
        [
            ROOT.joinpath("theory/common_scale_quark_rg_closure_note.md").read_text(),
            ROOT.joinpath("audits/common_scale_quark_rg_closure_audit.md").read_text(),
            ROOT.joinpath("docs/BHSM_HARD_CLOSURE_STATUS.md").read_text(),
        ]
    ).lower()
    forbidden = (
        "bhsm is proven",
        "bhsm is confirmed",
        "replaces the standard model",
        "precision quark matching is solved",
    )
    for phrase in forbidden:
        assert phrase not in text


def test_payload_reports_dressed_c_over_t_improves_and_u_over_t_warning():
    payload = closure_audit_payload(ROOT / "data/reference_common_scale_quark_ratios_mz.json")

    assert payload["ct_dressing_effect"]["dressed_improves_c_over_t"] is True
    assert payload["u_d_s_survival"]["u/t"] is False
    assert payload["u_d_s_survival"]["d/b"] is True
    assert payload["u_d_s_survival"]["s/b"] is True
    assert payload["official_outputs_modified"] is False
    assert payload["frozen_predictions_modified"] is False
