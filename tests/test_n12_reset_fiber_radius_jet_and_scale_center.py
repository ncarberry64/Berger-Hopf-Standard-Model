from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_reset_fiber_radius_jet_and_scale_center.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_RESET_FIBER_RADIUS_JET_AND_SCALE_CENTER_AUDIT.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_radius_cauchy_jet_has_two_reset_tangent_directions() -> None:
    payload = _payload()
    witness = payload["radius_Cauchy_jet_witness"]
    assert payload["validation_passed"] is True
    assert witness["raw_reset_tangent_dimension"] == 67
    assert witness["radius_Cauchy_jet_rank"] == 2
    assert witness["radius_Cauchy_jet_singular_values"][1] > 0.18
    assert witness[
        "rank_inequality_after_any_one_dimensional_time_quotient"
    ] == 1


def test_analytic_radius_jet_matches_direct_differences() -> None:
    payload = _payload()
    for row in payload["radius_Cauchy_jet_witness"]["finite_difference_rows"]:
        assert row["absolute_crosscheck_residual"] < 1.0e-8
        assert row["constraint_tangency_residual"] < 1.0e-12


def test_fixed_channel_coefficient_jet_is_invertible() -> None:
    payload = _payload()
    coefficient = payload["radius_Cauchy_jet_witness"][
        "scalar_fixed_channel_coefficient_jet"
    ]
    assert coefficient["determinant"] > 3.9
    assert coefficient["exact_positive_determinant_formula"] == (
        "4*exp(-4*x)>0"
    )


def test_common_scale_is_retained_as_physical_center() -> None:
    payload = _payload()
    center = payload["center_classification"]
    assert center["common_scale_may_be_removed_from_full_replacement_saddle"] is False
    assert payload["claim_boundary"]["common_scale_full_action_gauge"] is False
    assert payload["claim_boundary"]["common_scale_physical_modulation"] == "RETAIN"
    assert payload["fiber_invariance_adjudication"][
        "actual_parametric_exterior_oracle_still_required"
    ] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
