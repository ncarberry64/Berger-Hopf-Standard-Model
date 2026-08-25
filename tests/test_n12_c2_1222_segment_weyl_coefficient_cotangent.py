import json
from decimal import Decimal
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"


def test_1222_segment_inverse_free_weyl_cotangent() -> None:
    payload = json.loads((
        BASE / "BHSM_N12_C2_1222_SEGMENT_WEYL_COEFFICIENT_COTANGENT.json"
    ).read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert Decimal(payload["paired_product_Dirac_audit"]["paired_uniform_log_radius_cotangent_decimal"]) != 0
    assert payload["claim_boundary"]["zero_source_force"] == "OPEN"
    with np.load(BASE / "BHSM_N12_C2_1222_SEGMENT_WEYL_COEFFICIENT_COTANGENT.npz") as data:
        for name in (
            "scalar_c3", "product_Dirac_lambda1_5_chirality_plus",
            "product_Dirac_lambda1_5_chirality_minus",
        ):
            assert data[f"{name}__D_log_R4_node_Weyl"].shape == (1223,)
            assert np.all(np.isfinite(data[f"{name}__D_proper_duration_Weyl"]))
