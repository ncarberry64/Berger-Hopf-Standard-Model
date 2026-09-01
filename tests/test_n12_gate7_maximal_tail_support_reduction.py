from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "derive_n12_gate7_maximal_tail_support_reduction.py"
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_MAXIMAL_TAIL_SUPPORT_REDUCTION.json"
)


def test_maximal_tail_support_reduction() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["status"] == "FIXED_C2_UPSTREAM_INTERFACE_MAXIMAL_TAIL_CLOSED"
    spaces = payload["exact_subspace_decomposition"]
    assert spaces["reset_tangent_dimension"] == 139
    assert spaces["outgoing_C2_seed_projection_rank"] == 72
    assert spaces["fixed_C2_kernel_dimension"] == 67
    assert spaces["remaining_noncompact_tail_support_dimension_upper"] == 73
    assert spaces["fixed_C2_component_operator_norm"] < 1.0e-12
    assert payload["claim_boundary"][
        "fixed_C2_upstream_interface_full_graded_maximal_tail"
    ] == "CERTIFIED_CAUCHY"
    assert payload["formation_amplitude_routing"]["is_reset_fiber_tangent"] is False
    assert payload["claim_boundary"]["remaining_outgoing_C2_launch_tail"] == (
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
