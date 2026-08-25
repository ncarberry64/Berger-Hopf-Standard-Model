from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_finite_terminal_reset_stratum_candidate.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.json"
)


def test_n12_finite_terminal_reset_stratum_candidate() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["center"]["child"]["hitting_product"] < -1.0e-16
    assert payload["terminal_normal_block"]["rank"] == 58
    assert payload["terminal_normal_block"]["terminal_tangent_dimension"] == 138
    assert payload["proof_boundary"]["finite_terminal_stratum_certified"] is False
    assert payload["claim_boundary"]["Gate7"] == (
        "ACTIVE_TERMINAL_ROOT_BALL_CERTIFICATION"
    )

