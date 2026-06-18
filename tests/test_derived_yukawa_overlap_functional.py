import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_overlap as yo  # noqa: E402


def test_overlap_functional_definition_and_symbols_are_deterministic():
    assert yo.overlap_functional_definition() == "Y_f[i,j]=N_f*I_f(A_f[i],H_f,S_f[j])"
    assert yo.overlap_symbol("cyclic_upper", 1, 1) == "I_cyclic_upper_11"
    assert yo.overlap_symbol("reference_neutral", 3, 2) == "I_reference_neutral_32"
    with pytest.raises(ValueError):
        yo.overlap_symbol("cyclic_upper", 0, 1)
    with pytest.raises(ValueError):
        yo.overlap_symbol("missing", 1, 1)


def test_overlap_functional_document_contains_status():
    yo.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_overlap_functional.md").read_text()
    assert "Y_f[i,j]=N_f*I_f(A_f[i],H_f,S_f[j])" in text
    assert "YUKAWA_OVERLAP_FUNCTIONAL_DERIVED_CONDITIONAL" in text
