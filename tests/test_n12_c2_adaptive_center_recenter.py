from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/certify_n12_c2_adaptive_center_recenter.py"
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_ADAPTIVE_CENTER_RECENTER.json"


def test_n12_c2_adaptive_center_recenter() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    recenter = payload["recenter"]
    assert recenter["prior_total_certified_segments"] == 791
    assert recenter["strict_adaptive_allocation_margin"] > 0.0
    assert (
        recenter["recentered_admissible_root_radii"]["admissible_radius"]
        > 2.0 * recenter["incoming_endpoint_tube_upper"]
    )
    assert payload["adjudication"]["physical_history_changed"] is False
    assert payload["claim_boundary"]["actual_later_event_or_canonical_stop"] == "OPEN"
    assert payload["claim_boundary"]["chord_03_authorized"] is False
