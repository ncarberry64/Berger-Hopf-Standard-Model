from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_asymptotic_geometric_product_ball.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_ASYMPTOTIC_GEOMETRIC_PRODUCT_BALL.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_exact_rational_embedding_bounds_select_positive_expansion_radius() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    radius = payload["radius"]
    assert radius["owner"] == "positive_expansion_control"
    assert 0.0976 < float(radius["rho_geom_decimal"]) < 0.0977
    for record in payload["embedding_constants"].values():
        assert int(record["squared_exact_numerator"]) > 0
        assert int(record["rational_upper_numerator"]) > 0


def test_geometric_domain_margins_are_explicit() -> None:
    payload = _payload()
    margins = payload["certified_margins"]
    assert margins["lapse_lower"] == "3/4"
    assert margins["lapse_upper"] == "4/3"
    assert margins["absolute_beta_over_N_upper"] == "1/2"
    assert margins["eta_legendre_lower"] == "63/64"
    assert float(margins["H4_lower_decimal"]) > 0.146


def test_geometric_ball_is_not_overpromoted_to_capture() -> None:
    payload = _payload()
    scale = payload["first_lift_scale_at_geometric_radius"]
    assert scale["complete_nonlinear_remainder_included"] is False
    assert scale["capture_surface_promoted"] is False
    assert float(scale["epsilon_upper_if_only_epsilon_X5_is_budgeted"]) < 2.0e-15
    owner = payload["remaining_capture_side"]
    assert owner["uniform_normalized_constraint_block_inverse"] == "OPEN_CURRENT_OWNER"
    assert owner["uniform_normalized_reduced_kinetic_block_inverse"] == "OPEN_CURRENT_OWNER"
