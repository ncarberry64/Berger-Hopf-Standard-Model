from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_bordered_graph_product_norm_equivalence.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_BORDERED_GRAPH_PRODUCT_NORM_EQUIVALENCE.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_directed_scaled_determinant_gives_positive_equivalence() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    certificate = payload["directed_certificate"]
    assert certificate["determinant_contains_zero"] is False
    assert certificate["determinant_relative_accuracy_bits"] >= 200
    diagnostic = payload["magnitude_diagnostic"]
    assert -1144.0 < diagnostic["sigma_min_lower_log10"] < -1142.0
    assert 1142.0 < diagnostic["equivalence_upper_log10"] < 1144.0


def test_no_ill_conditioned_inverse_is_formed() -> None:
    payload = _payload()
    assert payload["definition"]["explicit_inverse_formed"] is False
    validation = payload["validation"]
    assert validation["explicit_bordered_inverse_not_formed"] is True
    assert validation["ill_conditioned_kinetic_Dirac_block_not_inverted"] is True


def test_determinant_bound_is_fallback_not_capture_promotion() -> None:
    payload = _payload()
    diagnostic = payload["magnitude_diagnostic"]
    assert diagnostic["binary_diagnostic_has_proof_authority"] is False
    assert "POSITIVE_FALLBACK" in diagnostic["interpretation"]
    boundary = payload["claim_boundary"]
    assert boundary["useful_repeated_solve_relative_bound"] == "OPEN_CURRENT_OWNER"
    assert boundary["quantitative_capture_surface"] == "OPEN"
