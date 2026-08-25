from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_n12_c2_enclosure_class_invariant_extension import build_payload  # noqa: E402


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_ENCLOSURE_CLASS_INVARIANT_EXTENSION.json"
)


def test_class_invariant_extension_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_all_1064_segments_are_one_class() -> None:
    payload = build_payload()
    theorem = payload["class_invariance_extension"]
    assert theorem["extended_certified_segment_count"] == 1064
    assert theorem["number_of_distinct_certified_C2_enclosure_classes"] == 1
    assert theorem["analytic_recenter_is_physical_transition"] is False
    assert theorem["proof_frontier_is_physical_transition"] is False


def test_count_chain_and_transition_classification_are_exact() -> None:
    payload = build_payload()
    chain = payload["continuation_provenance_chain"]
    assert [row["total"] for row in chain] == [436, 451, 791, 1064]
    assert all(row["regular_rows"] for row in chain)
    assert not any(row["event_or_canonical_stop_reached"] for row in chain)


def test_box_refinement_is_not_gate7_owner() -> None:
    consequence = build_payload()["Gate7_consequence"]
    assert consequence["more_local_boxes_required_to_define_C2_physical_class"] is False
    assert consequence["box_refinement_is_not_the_owner"] is True
