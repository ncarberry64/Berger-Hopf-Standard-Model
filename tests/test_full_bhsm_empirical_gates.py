from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_full_bhsm_completion import (  # noqa: E402
    EMPIRICAL_GATE_CATEGORIES,
    empirical_gate_registry,
)


def test_empirical_gate_categories_are_complete() -> None:
    categories = [row["category"] for row in empirical_gate_registry()]
    assert categories == EMPIRICAL_GATE_CATEGORIES
    assert "charged-fermion mass ratios" in categories
    assert "CKM" in categories
    assert "PMNS/neutrinos" in categories
    assert "DESI/Euclid curvature and expansion tests" in categories


def test_each_empirical_gate_has_required_fields() -> None:
    required = {
        "observable",
        "BHSM candidate expectation",
        "standard comparison",
        "data needed",
        "pass/fail criterion placeholder",
        "claim status if passed",
        "claim status if failed",
    }
    for row in empirical_gate_registry():
        assert required <= set(row)
        assert all(row[field] for field in required)


def test_empirical_gate_document_contains_gravity_tests() -> None:
    text = (ROOT / "theory" / "full_bhsm_empirical_gate_plan.md").read_text(
        encoding="utf-8"
    )
    for category in EMPIRICAL_GATE_CATEGORIES:
        assert category in text
    assert "scheme-controlled public data with uncertainties" in text
