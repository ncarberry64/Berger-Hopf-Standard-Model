import json
from dataclasses import FrozenInstanceError
from math import isclose

import pytest

from bhsm_v1 import (
    BHSMVersion,
    build_bhsm_bare_v1,
    build_bhsm_dressed_v1_candidate,
    compare_bhsm_v1_branches,
    declared_tolerance_bands,
    export_falsification_ledger_json,
    export_falsification_ledger_markdown,
    export_frozen_prediction_set_json,
    export_frozen_prediction_set_markdown,
)
from constants import MODE_LEDGER, S_OVERLAP
from falsification import (
    build_bhsm_falsification_ledger,
    evaluate_prediction_against_tolerance,
    score_frozen_prediction_set,
)


def test_frozen_constants_cannot_be_reassigned():
    bare = build_bhsm_bare_v1()

    with pytest.raises(FrozenInstanceError):
        bare.version.geometry_a = 1.0
    with pytest.raises(FrozenInstanceError):
        bare.version.overlap_s = 1.0


def test_frozen_constants_cannot_be_changed_through_constructor():
    with pytest.raises(ValueError):
        BHSMVersion(
            name="BHSM v1.0",
            branch="BHSM_BARE_V1",
            geometry_a=1.0,
            overlap_s=S_OVERLAP,
            mode_ledger=MODE_LEDGER,
            dressing_rules=(),
            status="FROZEN_BARE_CANONICAL",
            notes=("bad constructor attempt",),
        )


def test_bare_and_dressed_branches_build():
    bare = build_bhsm_bare_v1()
    dressed = build_bhsm_dressed_v1_candidate()

    assert bare.version.branch == "BHSM_BARE_V1"
    assert dressed.version.branch == "BHSM_DRESSED_V1_CANDIDATE"
    assert bare.version.geometry_a == dressed.version.geometry_a
    assert bare.version.overlap_s == dressed.version.overlap_s


def test_dressed_changes_only_ct():
    comparison = compare_bhsm_v1_branches()
    changed = [row for row in comparison["rows"] if row["changed"]]

    assert changed == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]


def test_required_outputs_are_frozen_for_bare_branch():
    outputs = build_bhsm_bare_v1().outputs

    assert "charged_lepton_ratios" in outputs
    assert "up_quark_ratios" in outputs
    assert "down_quark_ratios" in outputs
    assert "ckm" in outputs
    assert "pmns_effective" in outputs
    assert "gauge_couplings" in outputs
    assert "higgs_electroweak" in outputs
    assert "ht_gap_status" in outputs
    assert "scalar_decoupling_status" in outputs
    assert isclose(outputs["ckm"]["delta"], 1.1283791670955126)
    assert isclose(outputs["ckm"]["jarlskog"], 3.1011702945437805e-05)


def test_tolerance_bands_exist_before_scoring():
    bands = declared_tolerance_bands()

    for key in (
        "exact_status",
        "gauge_couplings",
        "higgs_electroweak_v",
        "higgs_mass_zeroth_order",
        "charged_lepton_ratios",
        "quark_ratios_scheme_aware",
        "ckm_angles",
        "ckm_cp_jarlskog",
        "pmns_effective",
        "ht_gap",
        "scalar_decoupling",
    ):
        assert key in bands
    assert build_bhsm_bare_v1().score_summary["tolerances_declared_before_scoring"] is True


def test_all_falsification_criteria_exist():
    ledger = build_bhsm_falsification_ledger()

    assert {row.id for row in ledger} == {f"F{i}" for i in range(1, 10)}
    assert all(row.statement for row in ledger)
    assert all(row.implications for row in ledger)


def test_scoring_does_not_change_frozen_predictions():
    prediction_set = build_bhsm_dressed_v1_candidate()
    before = prediction_set.outputs

    score_frozen_prediction_set(prediction_set)

    assert prediction_set.outputs == before
    assert prediction_set.version.dressing_rules[0]["factor"] == 0.5


def test_evaluate_prediction_against_tolerance_handles_binary_and_scheme_sensitive():
    assert evaluate_prediction_against_tolerance(True, True, binary=True)["status"] == "PASS"
    result = evaluate_prediction_against_tolerance(2.0, 1.0, 0.1, scheme_sensitive=True)

    assert result["status"] == "SCHEME_SENSITIVE"


def test_exports_parse_cleanly(tmp_path):
    pred_json = tmp_path / "predictions.json"
    pred_md = tmp_path / "predictions.md"
    fals_json = tmp_path / "falsification.json"
    fals_md = tmp_path / "falsification.md"

    export_frozen_prediction_set_json(pred_json)
    export_frozen_prediction_set_markdown(pred_md)
    export_falsification_ledger_json(fals_json)
    export_falsification_ledger_markdown(fals_md)

    assert json.loads(pred_json.read_text())["comparison"]["no_retuning"] is True
    assert len(json.loads(fals_json.read_text())) == 9
    assert "BHSM v1.0 Frozen Prediction Set" in pred_md.read_text()
    assert "BHSM v1.0 Falsification Ledger" in fals_md.read_text()


def test_generated_files_do_not_claim_final_proof(tmp_path):
    pred_md = tmp_path / "predictions.md"
    fals_md = tmp_path / "falsification.md"

    export_frozen_prediction_set_markdown(pred_md)
    export_falsification_ledger_markdown(fals_md)

    text = (pred_md.read_text() + "\n" + fals_md.read_text()).lower()
    assert "final proof" not in text
    assert "fully proven" not in text
