from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "derive_n12_gate7_incoming_amplitude_zeta_cotangent.py"
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_INCOMING_AMPLITUDE_ZETA_COTANGENT.json"
)


def test_incoming_amplitude_zeta_cotangent() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "INCOMING_AMPLITUDE_ZETA_COTANGENT_STRICT_SIGN_CERTIFIED"
    )
    enclosure = payload["certified_enclosure"]
    assert enclosure["amplitude_interval"][1] > 0.0
    assert enclosure["absolute_covector_per_lambda_interval"][0] > 0.0
    assert enclosure["outer_amplitude_signed_covector_interval"][1] < 0.0
    assert enclosure["outer_amplitude_replacement_covector_interval"][0] > 0.0
    assert enclosure["uniform_strict_sign_for_every_positive_amplitude"] is True
    assert enclosure["uniform_positive_magnitude_lower_on_open_interval"] is False
    assert payload["joint_direction_matching"][
        "incoming_graded_heat_amplitude_component"
    ].startswith("OPEN")
    assert payload["adjudication"]["Gate7"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
    for relative, digest in payload["inputs"].items():
        path = ROOT / relative
        content = path.read_bytes()
        if path.suffix.lower() in {".json", ".md", ".py"}:
            content = content.replace(b"\r\n", b"\n")
        assert hashlib.sha256(content).hexdigest().upper() == digest
