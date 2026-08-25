from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_global_finite_enclosure_quotient_kill_screen import build_payload  # noqa: E402


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_GLOBAL_FINITE_ENCLOSURE_QUOTIENT_KILL_SCREEN.json"
)


def test_global_finite_quotient_kill_screen_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_conditional_finite_ledger_does_not_become_global_count() -> None:
    payload = build_payload()
    ledger = payload["distributed_candidate_ledger"]
    kill = payload["kill_screen"]
    assert ledger["primitive_closure_spectrum"] == [1, 2, 3]
    assert ledger["charged_family_slot_count"] == 3
    assert kill["global_number_of_physical_enclosure_classes_is_finite"] == "OPEN"
    assert kill["exact_number_of_classes"] is None
    assert kill["candidate_product_count_authorized"] is False


def test_support_character_obstruction_is_exactly_localized() -> None:
    payload = build_payload()
    assert payload["validation"]["support_constraint_rank_is_seven"] is True
    assert payload["validation"]["support_constraint_nullity_is_twelve"] is True
    assert payload["validation"]["support_equivalence_quotient_not_closed"] is True
    assert payload["validation"]["emergent_enclosure_not_derived"] is True


def test_C2_local_class_is_not_blocked_by_global_finiteness() -> None:
    payload = build_payload()
    routing = payload["Gate7_routing"]
    assert routing["C2_local_class_theorem_blocked_by_global_finiteness"] is False
    assert routing["C2_class_count_on_certified_prefix"] == 1
