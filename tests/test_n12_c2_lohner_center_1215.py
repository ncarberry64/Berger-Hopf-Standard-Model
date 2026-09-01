import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BORDERED = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_LOHNER_BORDERED_MATRIX_1215.json"
FIELD = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_LOHNER_FIXED_S_FIELD_1215.json"


def test_lohner_center_1215() -> None:
    bordered = json.loads(BORDERED.read_text(encoding="utf-8"))
    field = json.loads(FIELD.read_text(encoding="utf-8"))
    assert bordered["validation_passed"] is True
    assert field["validation_passed"] is True
    assert bordered["bordered_center"]["selected_branch"] == 24
    assert abs(field["center_field"]["Dlambda_field"] - 1.0) < 1.0e-8
    assert field["fixed_descriptor_matrix"][
        "relative_second_variation_self_consistency"
    ] < 1.0
    assert field["FLAGSHIP_READY"] is False
    assert field["FULL_BHSM_COMPLETE"] is False
