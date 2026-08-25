from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from certify_n12_c2_pole_free_regularized_jacobi import build_payload  # noqa: E402


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_C2_POLE_FREE_REGULARIZED_JACOBI.json"
)


def test_pole_free_payload_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_bound_is_finite_pole_free_and_improved() -> None:
    payload = build_payload()
    bounds = payload["bounds"]
    assert 0.0 < bounds["pole_free_regularized_Jacobi_upper"]
    assert bounds["pole_free_regularized_Jacobi_upper"] < bounds[
        "superseded_crude_regularized_Jacobi_upper"
    ]
    assert payload["structural_identities"]["inverse_soft_eigenvalue_powers"] == 0
