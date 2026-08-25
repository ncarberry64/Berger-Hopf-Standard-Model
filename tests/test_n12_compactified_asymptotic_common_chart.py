from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_compactified_asymptotic_common_chart.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_COMPACTIFIED_ASYMPTOTIC_COMMON_CHART.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_common_chart_uses_the_retained_physical_product_topology() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["chart"]["dimension"] == 74
    assert payload["norm"]["product"] == (
        "H6_coordinates_CROSS_H5_velocities_CROSS_H6_multipliers"
    )
    assert payload["chart"]["common_scale_full_action_status"].endswith(
        "NOT_GAUGE_QUOTIENTED"
    )


def test_directed_first_lift_norm_is_large_and_rigorously_ordered() -> None:
    payload = _payload()
    norm = payload["directed_X5_norm"]
    lower = float(norm["product_lower"])
    upper = float(norm["product_upper"])
    assert 5.67e13 < lower <= upper < 5.69e13
    assert norm["dominant_weighted_component"]["label"].startswith("w_")


def test_capture_radius_remains_symbolic_and_no_wrong_radius_is_imported() -> None:
    payload = _payload()
    conversion = payload["symbolic_capture_conversion"]
    assert conversion["epsilon_upper"] == "rho_star/C_X5_upper"
    assert conversion["R4_lower"] == "sqrt(C_X5_upper/rho_star)"
    assert conversion["rho_star_numerically_selected"] is False
    assert conversion["nonlinear_remainder_included"] is False
    assert payload["claim_boundary"]["quantitative_capture_radius"] == "OPEN_CURRENT_OWNER"
