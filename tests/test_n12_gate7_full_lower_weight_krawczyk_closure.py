from __future__ import annotations

from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_FULL_LOWER_WEIGHT_KRAWCZYK_CLOSURE.json"
)
SCRIPT = ROOT / "scripts" / (
    "derive_n12_gate7_full_lower_weight_krawczyk_closure.py"
)


def _load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_full_lower_weight_krawczyk_graph_is_certified() -> None:
    data = _load()
    assert data["validation_passed"] is True
    certificate = data["full_Krawczyk_certificate"]
    assert Decimal(certificate["theta_full_upper"]) < Decimal(1) / 2
    assert Decimal(certificate["initial_map_displacement_upper"]) < Decimal(
        certificate["self_map_radius_budget"]
    )
    assert certificate["contraction"] is True
    assert certificate["self_map"] is True
    assert certificate["unique_full_descriptor_graph"] is True
    assert certificate["complete_lower_weight_inhomogeneous_correction_enclosed"] is True
    assert data["scope"]["quantitative_stable_normal_cone"] == (
        "OPEN_CURRENT_ANALYTIC_OWNER"
    )
    assert data["claim_boundary"]["AE2_reset_image_enters_capture_basin"] == (
        "OPEN_CURRENT_OWNER"
    )
    assert data["FULL_BHSM_COMPLETE"] is False


def test_full_lower_weight_krawczyk_materialization_is_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
    data = _load()
    assert data["exact_local_scale_ledger"]["bulk"][
        "total_expanded_term_count"
    ] == 69
    assert data["exact_local_scale_ledger"]["inertia"][
        "total_expanded_term_count"
    ] == 21
    assert Decimal(data["full_Krawczyk_certificate"]["epsilon_upper"]) < Decimal(
        "2e-1316"
    )
    assert Decimal(data["full_Krawczyk_certificate"]["R4_lower"]) > Decimal(
        "8e657"
    )
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
    assert first == second
