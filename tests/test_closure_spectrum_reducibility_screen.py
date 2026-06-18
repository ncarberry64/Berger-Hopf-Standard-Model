import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_closure_spectrum_selection import classify_dimension, is_reducible_by_lower_primitives  # noqa: E402


def test_reducibility_screen_for_dimensions_4_to_8():
    assert classify_dimension(4).reducibility_status == "composite/reducible under current primitive set"
    assert classify_dimension(5).reducibility_status == (
        "not reducible but unsupported by current low-energy minimality screens"
    )
    assert classify_dimension(6).reducibility_status == "composite/reducible under current primitive set"
    assert classify_dimension(7).reducibility_status == (
        "not reducible but unsupported by current low-energy minimality screens"
    )
    assert classify_dimension(8).reducibility_status == "composite/reducible under current primitive set"


def test_higher_primes_are_unsupported_not_impossible():
    for d in [5, 7]:
        audit = classify_dimension(d)
        assert audit.primitive_status == "higher prime unsupported"
        assert "unsupported, not impossible" in audit.notes


def test_reducibility_helper():
    assert is_reducible_by_lower_primitives(4) is True
    assert is_reducible_by_lower_primitives(6) is True
    assert is_reducible_by_lower_primitives(5) is False
