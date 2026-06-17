import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_harmonic_highest_weight as hw  # noqa: E402


def test_j_equals_ell_minus_n_for_every_frozen_mode():
    for labels in hw.highest_weight_ledgers().values():
        for label in labels:
            assert hw.lowering_index_identity_holds(label)
            assert label.ell - label.n == label.j


def test_j_as_lowering_index_doc():
    hw.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_j_as_lowering_index.md").read_text()
    assert "`ell-n=j`" in text
    assert "J_AS_LOWERING_INDEX_DERIVED_CONDITIONAL" in text
