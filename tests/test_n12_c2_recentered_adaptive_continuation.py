import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/certify_n12_c2_recentered_adaptive_continuation.py"
ARTIFACT = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION.json"


def test_recentered_adaptive_continuation_replays_and_preserves_history() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    record = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    cover = record["recentered_cover"]

    assert record["validation_passed"] is True
    assert cover["additional_certified_segments"] > 0
    assert cover["total_certified_segments"] > cover["prior_total_segments"]
    assert cover["initial_center_path_from_recenter"] == 0.0
    assert cover["initial_endpoint_tube_radius_upper"] > 0.0
    assert float(cover["final_signed_lambda_decimal"]) >= float(
        cover["initial_signed_lambda_decimal"]
    )
    assert all(
        row["root_relative_path_plus_tube_upper"]
        < row["translated_ball_total_radius"]
        for row in cover["rows"]
    )
    assert cover["exhaustion_is_event_or_canonical_stop"] is False
    assert record["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
