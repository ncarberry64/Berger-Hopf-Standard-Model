from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_asymptotic_bordered_graph_norm.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_ASYMPTOTIC_BORDERED_GRAPH_NORM.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_directed_graph_norm_uses_bordered_operator_without_inverse() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    definition = payload["definition"]
    assert definition["bordered_operator"] == "B_minus2=A7+2*H0*E7"
    assert definition["explicit_B_minus2_inverse_formed"] is False
    assert definition["ill_conditioned_kinetic_Dirac_block_inverted"] is False
    value = payload["directed_first_lift_graph_norm"]
    assert 3.94 < float(value["lower"].lstrip("[").split()[0]) < 3.95
    assert value["relative_accuracy_bits"] >= 250


def test_graph_norm_exposes_weak_product_directions() -> None:
    payload = _payload()
    comparison = payload["norm_comparison"]
    assert float(comparison["product_norm_lower"]) > 5.67e13
    assert float(comparison["graph_to_product_ratio_upper"]) < 7.0e-14
    assert "WEAK_DIRECTION" in comparison["interpretation"]


def test_relative_nonlinear_defect_remains_exact_owner() -> None:
    payload = _payload()
    required = payload["required_nonlinear_certificate"]
    assert required["certified_repeated_solves_allowed"] is True
    assert required["explicit_combined_inverse_allowed"] is False
    assert required["relative_defect_theta_certified"] is False
    assert payload["claim_boundary"]["nonlinear_relative_graph_defect"] == "OPEN_CURRENT_OWNER"
