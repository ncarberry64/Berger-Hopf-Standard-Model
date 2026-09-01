from __future__ import annotations

from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_QUANTITATIVE_STABLE_CAPTURE_TUBE.json"
)
SCRIPT = ROOT / "scripts" / (
    "derive_n12_gate7_quantitative_stable_capture_tube.py"
)


def _load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_quantitative_stable_capture_tube_is_certified() -> None:
    data = _load()
    assert data["validation_passed"] is True
    assert data["claim_boundary"]["quantitative_capture_tube"] == "CERTIFIED"
    tube = data["capture_tube"]
    assert Decimal(tube["total_Jacobian_defect_upper"]) < (
        Decimal(tube["h0_lower"]) / 32
    )
    assert Decimal(tube["integrated_total_center_drift_upper"]) < Decimal(
        tube["center_margin"]
    )
    assert tube["stable_boundary_strictly_inward"] is True
    assert data["consequence"]["every_regular_history_entering_tube_is_captured"] is True
    assert data["claim_boundary"]["AE2_reset_image_enters_capture_tube"] == (
        "OPEN_CURRENT_OWNER"
    )
    assert data["FULL_BHSM_COMPLETE"] is False


def test_stable_capture_materialization_is_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
    data = _load()
    directed = data["directed_flow_Dirac_certificate"]
    assert directed["dimension"] == 49
    assert directed["determinant_contains_zero"] is False
    assert directed["explicit_inverse_formed"] is False
    assert Decimal(data["capture_tube"]["epsilon_upper"]) > 0
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
    assert first == second
