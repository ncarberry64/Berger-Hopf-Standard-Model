from __future__ import annotations

from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_QUANTITATIVE_CAPTURE_BRIDGE_RECOMBINATION.json"
)
SCRIPT = ROOT / "scripts" / (
    "derive_n12_gate7_quantitative_capture_bridge_recombination.py"
)


def _load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_quantitative_capture_bridge_recombines_leading_inverse_only() -> None:
    data = _load()
    assert data["validation_passed"] is True
    leading = data["leading_bordered_recombination"]
    assert Decimal(leading["leading_relative_defect_upper"]) <= Decimal(1) / 16
    assert Decimal(leading["leading_Neumann_margin_lower"]) >= Decimal(15) / 16
    assert leading["separate_normalized_constraint_inverse_required"] is False
    assert leading["separate_reduced_kinetic_inverse_required"] is False
    assert leading["combined_Euler_Dirac_inverse_formed"] is False
    assert data["connection_adjudication"]["full_lower_weight_Krawczyk_bound"] == (
        "OPEN"
    )
    assert data["connection_adjudication"][
        "validated_nonempty_reset_family_cover_into_capture_tube"
    ] == "OPEN_CURRENT_OWNER"
    assert data["claim_boundary"]["quantitative_capture_surface"] == "OPEN"
    assert data["FULL_BHSM_COMPLETE"] is False


def test_quantitative_capture_bridge_scale_and_materialization() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
    data = _load()
    assert Decimal(data["first_lift_feasibility"]["epsilon_upper"]) < Decimal(
        "2e-617"
    )
    assert Decimal(data["first_lift_feasibility"]["R4_lower"]) > Decimal("2e308")
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
    assert first == second
