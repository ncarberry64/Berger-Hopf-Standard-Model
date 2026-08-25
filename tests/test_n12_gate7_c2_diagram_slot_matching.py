import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_gate7_c2_diagram_slot_matching.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_C2_DIAGRAM_SLOT_MATCHING_AUDIT.json"
)


def _module():
    spec = importlib.util.spec_from_file_location("c2_matching", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_c2_diagram_slot_matching_validates() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    assert payload["adjudication"]["C2_slot_operator_theory"] == (
        "VALID_MATCH_EXISTING_MAXIMAL_FORWARD_M_C_FAMILY"
    )
    assert payload["adjudication"]["new_C2_physical_theory_required"] is False
    assert payload["adjudication"]["actual_E1_reset_selected_C2_value"] == (
        "ACTUALLY_MISSING_REALIZATION_DATA"
    )
    assert len(payload["matching_audit"]) == 15


def test_c2_diagram_slot_matching_replays() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = RESULT.read_bytes()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = RESULT.read_bytes()
    assert first == second
    assert json.loads(first)["validation_passed"] is True


def test_c2_response_occupies_child_leg_before_ae2_frame_assembly() -> None:
    from bhsm.interface.ae2_covariant_seam_response import (
        covariant_effective_event_load,
        covariant_seam_response,
    )

    child = np.diag([2.0, 5.0]).astype(complex)
    wentzell = np.asarray([[0.7, 0.1j], [-0.1j, 1.1]], dtype=complex)
    lift = np.asarray([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    incoming = np.asarray([[3.0, 0.2], [0.2, 4.0]], dtype=complex)
    expected_load = lift.conj().T @ child @ lift + wentzell

    np.testing.assert_allclose(
        covariant_effective_event_load(child, wentzell, lift),
        expected_load,
    )
    np.testing.assert_allclose(
        covariant_seam_response(incoming, child, wentzell, lift),
        incoming + expected_load,
    )
