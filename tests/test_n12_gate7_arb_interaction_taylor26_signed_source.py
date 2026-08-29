import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RECORD = BASE / "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_SIGNED_SOURCE.json"
DATA = RECORD.with_suffix(".npz")
TRANSFER = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_TRANSFER_AUDIT.json"


def test_exact_affine_signed_source_certificate() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    assert record["validation_passed"] is True
    assert record["identity"]["fixed_substep_count"] == 5908
    assert record["identity"]["source_unaligned_partial_step_count"] == 2960
    assert record["summary"]["maximum_global_response_Euclidean_radius"] < 6e-22
    assert hashlib.sha256(DATA.read_bytes()).hexdigest().upper() == record["data_SHA256"]
    with np.load(DATA) as source:
        assert source["affine_source_midpoint"].shape == (47, 73)
        assert source["affine_source_arb_strings"].shape == (47, 73)
        assert source["global_signed_response_midpoint"].shape == (48, 73)
        assert source["global_signed_response_arb_strings"].shape == (48, 73)
        assert source["global_signed_response_Euclidean_radius"][0] == 0.0
        assert np.all(np.isfinite(source["global_signed_response_component_radius"]))
        assert np.all(source["global_signed_response_component_radius"] >= 0.0)


def test_exact_affine_center_transfer_routing() -> None:
    record = json.loads(TRANSFER.read_text(encoding="utf-8"))
    assert record["validation_passed"] is True
    summary = record["summary"]
    assert summary["frozen_Decimal_cone_utilization"] < 0.054
    assert summary["maximum_exact_to_Magnus8_combined_outward"] < 3e-20
    assert summary["old_recentered_Gauss12_cone_radius_multiple"] > 1e5
    assert record["routing"]["signed_Taylor_Volterra_Z2_formula_and_majorants"] == "REUSE"
    assert record["routing"]["existing_Gauss12_recentered_cone_numerical_ball"] == "DO_NOT_TRANSFER"
    assert record["FULL_BHSM_COMPLETE"] is False
