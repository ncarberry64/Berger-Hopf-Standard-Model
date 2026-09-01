from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "derive_n12_gate7_outgoing_flow_tail_closure.py"
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_OUTGOING_FLOW_TAIL_CLOSURE.json"
)


def test_outgoing_flow_tail_closure() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["status"] == "OUTGOING_DESCRIPTOR_FLOW_MAXIMAL_TAIL_CLOSED"
    assert payload["launch_witness"]["seed_image_dimension"] == 72
    assert payload["launch_witness"]["launch_dimension_before_closure"] == 73
    assert abs(payload["launch_witness"]["stored_transverse_unit_alignment"] - 1.0) < 1.0e-10
    assert payload["local_flow_derivative_theorem"][
        "noncompact_reset_Jacobi_field_required"
    ] is False
    assert payload["local_flow_derivative_theorem"][
        "superseded_M_at_zero_equals_W_phys_used"
    ] is False
    assert payload["claim_boundary"]["remaining_noncompact_tail_dimension_upper"] == 72
    assert payload["claim_boundary"]["remaining_reset_generated_seed_image_tail"] == (
        "OPEN_CURRENT_OWNER"
    )
    assert payload["claim_boundary"]["actual_projected_KKT_root"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
    for relative, digest in payload["inputs"].items():
        path = ROOT / relative
        content = path.read_bytes()
        if path.suffix.lower() in {".json", ".md", ".py"}:
            content = content.replace(b"\r\n", b"\n")
        assert hashlib.sha256(content).hexdigest().upper() == digest
