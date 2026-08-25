from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_n12_c2_enclosure_class_invariant import build_payload  # noqa: E402


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_ENCLOSURE_CLASS_INVARIANT_AUDIT.json"
)


def test_c2_enclosure_class_invariant_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_98_segments_are_one_class_and_not_98_classes() -> None:
    payload = build_payload()
    theorem = payload["class_invariance_theorem"]
    assert theorem["certified_segment_count"] == 98
    assert theorem["number_of_distinct_certified_C2_enclosure_classes"] == 1
    assert theorem["proof_frontier_is_physical_transition"] is False
    assert payload["hindsight"]["event_or_class_transition"] == "NONE_CROSSED"
    assert payload["hindsight"]["canonical_stop"] == "NONE_REACHED"


def test_global_finiteness_is_not_overclaimed() -> None:
    payload = build_payload()
    adjudication = payload["finite_quotient_adjudication"]
    assert adjudication["finite_C2_certified_prefix_quotient"] == "PROVED_ONE_CLASS"
    assert adjudication[
        "global_number_of_physical_enclosure_classes_is_finite"
    ] == "OPEN"
    assert adjudication["forbidden_product_count"] is True


def test_invalid_physical_markers_are_excluded() -> None:
    payload = build_payload()
    proof_marker = next(
        row for row in payload["class_transition_surface_ledger"]
        if row["marker"] == "proof tube or safety counter"
    )
    assert proof_marker["status"] == (
        "INVALID_PHYSICAL_MARKER_PROOF_TECHNOLOGY_ONLY"
    )
