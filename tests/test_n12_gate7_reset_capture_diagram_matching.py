from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_n12_gate7_reset_capture_diagram_matching.py"


def _module():
    spec = importlib.util.spec_from_file_location("reset_capture_matching", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_reset_capture_matching_localizes_only_two_connection_blocks() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["regular_post_collar_proper_time_field"] == (
        "DERIVED_BY_EXACT_REPARAMETRIZATION"
    )
    assert payload["numerical_formula_witness"]["d_tau_ds"] > 0.0
    assert payload["numerical_formula_witness"]["ds_d_tau"] > 0.0
    assert set(payload["genuinely_missing"]) == {
        "terminal_transition",
        "connection_certificate",
    }
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
    assert payload["claim_boundary"]["chord_03_authorized"] is False


def test_matching_audit_has_no_untyped_diagram_slot() -> None:
    payload = _module().build_payload()
    rows = payload["matching_audit"]
    assert len(rows) == 6
    assert all(row["diagram_slot"] and row["required_type"] for row in rows)
    missing = [row for row in rows if row["verdict"].startswith("ACTUALLY_MISSING")]
    assert len(missing) == 2
