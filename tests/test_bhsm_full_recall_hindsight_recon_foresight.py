from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_bhsm_full_recall_hindsight_recon_foresight.py"
ARTIFACT = ROOT / "artifacts/flagship_integration/BHSM_FULL_RECALL_HINDSIGHT_RECON_FORESIGHT.json"


def test_full_recall_rebuilds_byte_deterministically() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = ARTIFACT.read_bytes()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    assert ARTIFACT.read_bytes() == first


def test_full_recall_preserves_current_claim_boundary() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE_G7_08_FORCE"
    assert payload["claim_boundary"]["Gate8"] == "LOCKED"
    assert payload["claim_boundary"]["a_equals_1_over_118"] == (
        "ROUNDED_SOURCE_TRACE_FOUND_AS_1_OVER_12PI2_BUT_NOT_ACTION_DERIVED_OR_AE2_ATTACHED"
    )
    assert payload["inventory"]["norman_pdf_page_total"] == 194
    assert len(payload["inventory"]["norman_pdf_sources"]) == 27
    assert payload["inventory"]["norman_document_page_total"] == 4
    assert len(payload["inventory"]["norman_document_sources"]) == 1
    assert payload["inventory"]["reviewed_source_page_total"] == 198
    assert payload["inventory"]["nightcrawler_snapshot"]["file_count"] == 1036
    assert payload["validation"]["fine_structure_mapping_conflict_quarantined"] is True
    assert payload["downstream_completion_program"][0]["work_package"] == (
        "G7_PARAMETRIC_PHYSICAL_HISTORY"
    )
    assert payload["downstream_completion_program"][-1]["work_package"] == (
        "FROZEN_COMPARISON_AND_EXTERNAL_TESTS"
    )
