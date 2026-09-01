import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT / "artifacts" / "flagship_integration"
    / "BHSM_N12_C2_SIGNED_FIRST_COEFFICIENT_VECTORS.json"
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_signed_first_coefficient_vector_certificate() -> None:
    record = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    data_path = ROOT / record["data"]
    assert record["validation_passed"] is True
    assert record["status"] == "C2_SIGNED_CENTER_Db_Dc_Dlambda_VECTORS_CERTIFIED"
    assert record["data_SHA256"] == _sha256(data_path)
    assert all(
        digest == _sha256(ROOT / relative)
        for relative, digest in record["inputs"].items()
    )
    with np.load(data_path) as data:
        for prefix in ("b", "c", "lambda"):
            lo = np.asarray(data[f"{prefix}_first_action_lower"], dtype=float)
            hi = np.asarray(data[f"{prefix}_first_action_upper"], dtype=float)
            assert lo.shape == (98,)
            assert np.all(np.isfinite(lo))
            assert np.all(np.isfinite(hi))
            assert np.all(lo <= hi)
        assert (
            data["b_first_action_lower"][86]
            <= -0.7673819343475514
            <= data["b_first_action_upper"][86]
        )
    assert record["adjudication"]["complete_D2Delta_operator"] == "OPEN"
    assert record["adjudication"]["Gate7"] == "OPEN"
    assert record["adjudication"]["Gate8"] == "LOCKED"
    assert record["adjudication"]["chord_03_authorized"] is False
    assert record["FULL_BHSM_COMPLETE"] is False
