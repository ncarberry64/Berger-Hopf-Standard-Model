from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_maximal_friedrichs_weyl_exhaustion.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_MAXIMAL_FRIEDRICHS_WEYL_EXHAUSTION.json"
)


def test_maximal_friedrichs_weyl_exhaustion() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["closed_here"]["Friedrichs_negative_z_Weyl_value_uniqueness"] is True
    assert payload["theorem"]["global_radius_upper_required"] is False
    assert payload["theorem"]["terminal_return_required"] is False
    assert payload["open_after_theorem"]["noncompact_reset_quotient_first_jet"] is True
    assert payload["open_after_theorem"]["physical_force_root"] is True
    assert payload["claim_boundary"]["chord_03_authorized"] is False
    rows = payload["constant_channel_witness"]["rows"]
    errors = [row["absolute_error"] for row in rows]
    assert all(left > right for left, right in zip(errors, errors[1:]))
