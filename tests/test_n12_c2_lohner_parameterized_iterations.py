import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/flagship_integration"


def _load(name: str) -> dict:
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def test_parameterized_lohner_iterations_through_1219() -> None:
    for segment in (1216, 1217, 1218):
        recenter = _load(f"BHSM_N12_C2_LOHNER_RECENTER_{segment}.json")
        growth = _load(f"BHSM_N12_C2_LOHNER_GROWTH_{segment}.json")
        bordered = _load(f"BHSM_N12_C2_LOHNER_BORDERED_MATRIX_{segment}.json")
        field = _load(f"BHSM_N12_C2_LOHNER_FIXED_S_FIELD_{segment}.json")
        response = _load(f"BHSM_N12_C2_LOHNER_RESPONSE_BALL_{segment}.json")
        assert all(record["validation_passed"] is True for record in (
            recenter, growth, bordered, field, response,
        ))
        assert recenter["center"]["selected_branch"] == 24
        assert abs(field["center_field"]["Dlambda_field"] - 1.0) < 1.0e-8
        assert field["fixed_descriptor_matrix"][
            "relative_second_variation_self_consistency"
        ] < 1.0

    for segment in (1217, 1218, 1219):
        step = _load(f"BHSM_N12_C2_LOHNER_STEP_{segment}.json")
        assert step["validation_passed"] is True
        assert step["segment"]["total_certified_segments"] == segment
        assert step["segment"]["stored_step_action_norm"] > 0.0
        assert step["segment"]["joint_domain_use_upper"] < step["domain"][
            "selected_domain_radius"
        ]
        assert step["adjudication"]["actual_later_event_or_canonical_stop"] == "NOT_REACHED"
        assert step["FULL_BHSM_COMPLETE"] is False
