from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_n12_gate7_joint_kkt_information_gate.py"
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_JOINT_KKT_INFORMATION_GATE.json"
)


def test_gate7_joint_kkt_information_gate() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "JOINT_KKT_REQUIRES_COMBINED_SIGNED_COVECTOR_COMPONENT_ZERO_TESTS_RETIRED"
    )
    assert payload["projected_component_ball"]["launch_dimension"] == 73
    assert payload["projected_component_ball"]["contains_zero"] is True
    assert payload["projected_component_ball"]["contains_nonzero_values"] is True
    assert payload["joint_KKT_rule"]["componentwise_zero_required"] is False
    assert payload["adjudication"][
        "separate_C2_zeta_zero_or_zero_exclusion_gate"
    ].startswith("RETIRED")
    assert payload["adjudication"]["Gate7"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
    with np.load(ROOT / payload["data"]) as data:
        assert data["projected_C2_zeta_ball_center"].shape == (73,)
        assert np.linalg.norm(data["projected_C2_zeta_ball_center"]) == 0.0
        assert float(data["projected_C2_zeta_ball_radius_upper"]) > 0.0
    for relative, digest in payload["inputs"].items():
        path = ROOT / relative
        content = path.read_bytes()
        if path.suffix.lower() in {".json", ".md", ".py"}:
            content = content.replace(b"\r\n", b"\n")
        assert hashlib.sha256(content).hexdigest().upper() == digest
