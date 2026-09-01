from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_ae2_negative_axis_seam_family.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_AE2_NEGATIVE_AXIS_SEAM_FAMILY.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_full_negative_axis_is_parametrically_covered() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"][
        "complete_spectral_parameter_coverage"
    ] == "CLOSED_ON_NEGATIVE_REAL_AXIS"
    assert payload["parametric_theorem"]["domain"] == (
        "z=-kappa^2_WITH_kappa>0"
    )
    assert payload["parametric_theorem"]["spectral_role"] == (
        "NEUTRAL_RESOLVENT_PARAMETER_NOT_MOMENTUM"
    )


def test_optimized_product_trial_has_linear_high_probe_growth() -> None:
    payload = _payload()
    high = payload["sampled_crosscheck_rows"][-1]
    assert high["product_dirac"]["base"]["uses_full_certified_core"] is False
    assert high["product_dirac"]["base"]["upper"] / (
        high["kappa_squared"] ** 0.5
    ) < 2.0


def test_broad_family_is_not_promoted_to_force_sign() -> None:
    payload = _payload()
    force = payload["force_adjudication"]
    assert force["negative_axis_family_covered_by_broad_enclosures"] is True
    assert force["broad_intervals_decide_heat_minus_zeta_force_sign"] is False
    assert payload["claim_boundary"]["actual_spectral_trace_value"] == "OPEN"
    assert payload["claim_boundary"]["zero_source_force_value_and_sign"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
