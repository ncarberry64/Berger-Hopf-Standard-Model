from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "derive_n12_gate7_one_seam_full_graded_finite_core_heat_bound.py"
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_ONE_SEAM_FULL_GRADED_FINITE_CORE_HEAT_BOUND.json"
)


def _run() -> bytes:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return RESULT.read_bytes()


def test_full_graded_one_seam_heat_seed_bound() -> None:
    payload = json.loads(_run())
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "FULL_GRADED_ONE_SEAM_FINITE_CORE_HEAT_SEED_SUPPRESSED_IN_LOG_SPACE"
    )
    domain = payload["finite_core_domain"]
    coercive = payload["coercive_bound"]
    bounds = payload["full_graded_bounds"]
    assert domain["total_duration_upper"] > domain["child_duration_upper"] > 0.0
    assert domain["joint_D_tau_log_R4_absolute_upper"] > 0.0
    assert coercive["Dirac_linear_coefficient"] > 0.0
    assert coercive["lowest_Weyl_spatial_lower"] > 0.0
    assert coercive["common_gap_lower"] > 1.0e50
    assert math.isfinite(bounds["heat_trace_absolute_log_upper"])
    assert bounds["heat_trace_absolute_log10_upper"] < -1.0e50
    assert bounds["heat_cotangent_seed_trace_norm_log10_upper"] < -1.0e50
    assert bounds["binary64_underflow_is_exact_zero"] is False
    assert payload["matching_audit"]["full_finite_core_angular_sum"] == (
        "CLOSED_ABSOLUTELY"
    )
    assert payload["matching_audit"]["signed_non_scale_geometry_contraction"] == "OPEN"
    assert payload["matching_audit"]["maximal_C2_tail"] == "OPEN"
    assert payload["claim_boundary"]["Gate7"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_full_graded_one_seam_heat_bound_is_deterministic() -> None:
    first = hashlib.sha256(_run()).hexdigest()
    second = hashlib.sha256(_run()).hexdigest()
    assert first == second
