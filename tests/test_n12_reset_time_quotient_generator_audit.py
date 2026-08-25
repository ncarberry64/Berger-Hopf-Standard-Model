from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_reset_time_quotient_generator.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_RESET_TIME_QUOTIENT_GENERATOR_AUDIT.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_raw_and_quotient_dimensions_are_not_conflated() -> None:
    payload = _payload()
    dimension = payload["dimension_statement"]
    assert dimension["raw_fixed_event_child_constraint_tangent"] == 67
    assert dimension[
        "declared_after_existing_whole_system_time_quotient"
    ] == 66
    assert dimension["explicit_generator_certified_in_current_checkpoint"] is False


def test_child_flow_is_not_promoted_to_hybrid_time_generator() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["validation"][
        "child_flow_candidate_is_not_in_fixed_event_reset_kernel"
    ] is True
    assert payload["validation"][
        "child_flow_candidate_failure_is_resolution_stable"
    ] is True
    assert all(
        row["relative_fixed_event_reset_residual"] > 0.011
        for row in payload["witness"]["rows"]
    )
    assert payload["force_and_saddle_consequence"][
        "raw_boundary_log_R4_projection_promoted_to_physical_quotient"
    ] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
