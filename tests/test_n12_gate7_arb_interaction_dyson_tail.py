import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RECORD = BASE / "BHSM_N12_GATE7_ARB_INTERACTION_DYSON_TAIL.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_interaction_dyson_tail_certificate() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    assert record["validation_passed"] is True
    assert record["summary"]["substep_count"] == 5908
    assert record["summary"]["maximum_interaction_beta_upper"] < 1.0
    assert record["summary"]["maximum_local_exact_propagator_tail_upper"] < 1e-20
    assert record["claim_boundary"]["finite_order14_interaction_polynomial"] == (
        "OPEN_FINITE_OUTWARD_EVALUATION"
    )
    assert record["claim_boundary"]["signed_Y"] == "OPEN_INTERVAL_AUTHORITY"
    assert record["FULL_BHSM_COMPLETE"] is False


def test_interaction_dyson_tail_data_and_provenance() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    data = ROOT / record["data"]
    assert _sha256(data) == record["data_SHA256"]
    for relative, digest in record["inputs"].items():
        assert _sha256(ROOT / relative) == digest
    with np.load(data) as arrays:
        assert arrays["interval"].shape == (5908,)
        assert arrays["local_exact_propagator_tail_upper"].shape == (5908,)
        assert np.all(arrays["interaction_beta_upper"] > 0.0)
        assert np.all(arrays["local_exact_propagator_tail_upper"] > 0.0)
        assert np.max(arrays["local_exact_propagator_tail_upper"]) == (
            record["summary"]["maximum_local_exact_propagator_tail_upper"]
        )
