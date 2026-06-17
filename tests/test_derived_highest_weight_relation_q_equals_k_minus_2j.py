import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_harmonic_highest_weight as hw  # noqa: E402


def test_k_from_qj_and_highest_weight_relation():
    assert hw.k_from_qj(1, 2) == 5
    assert hw.k_from_qj(8, 1) == 10
    assert hw.k_from_qj(0, 3) == 6

    for modes in hw.generation_modes().values():
        for mode in modes:
            label = hw.highest_weight_label(mode)
            assert mode.q == label.k - 2 * label.j
            assert label.n == label.ell - label.j


def test_highest_weight_relation_doc_contains_core_equations():
    hw.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_highest_weight_relation_q_equals_k_minus_2j.md").read_text()
    assert "`q=k-2j`" in text
    assert "`q/2=k/2-j`" in text
    assert "HIGHEST_WEIGHT_NORMALIZATION_DERIVED_CONDITIONAL" in text
