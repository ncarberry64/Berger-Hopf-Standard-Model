from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

from scripts.certify_n12_finite_endpoint_force_sign_shortcut_no_go import (
    build_payload,
    force_interval,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/certify_n12_finite_endpoint_force_sign_shortcut_no_go.py"
TARGET = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_ENDPOINT_FORCE_SIGN_SHORTCUT_NO_GO.json"
)


def test_certified_counterpair_has_opposite_strict_signs() -> None:
    assert force_interval("0.5")["strict_sign"] == "NEGATIVE"
    assert force_interval("2.0")["strict_sign"] == "POSITIVE"


def test_claim_scope_does_not_promote_reference_witnesses() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["theorem_scope"]["physical_N12_force_sign"] == "OPEN"
    assert payload["claim_boundary"]["actual_projected_force"] == "OPEN"
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False


def test_artifact_is_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
    assert json.loads(TARGET.read_text(encoding="utf-8"))["validation_passed"] is True
