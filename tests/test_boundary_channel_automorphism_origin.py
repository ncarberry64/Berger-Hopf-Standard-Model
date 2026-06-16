import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_automorphism_closure import (  # noqa: E402
    BoundaryVectorSpace,
    channel_algebra_blocks,
    channel_spaces,
    endomorphism_block,
)


def test_endomorphism_block_represents_c_and_matrix_algebras():
    assert endomorphism_block(BoundaryVectorSpace("C", 1, "unit")).algebra == "C"
    assert endomorphism_block(BoundaryVectorSpace("C2", 2, "two-state")).algebra == "M2(C)"
    assert endomorphism_block(BoundaryVectorSpace("C3", 3, "three-state")).algebra == "M3(C)"


def test_endomorphism_block_rejects_nonpositive_dimension():
    with pytest.raises(ValueError):
        endomorphism_block(BoundaryVectorSpace("zero", 0, "invalid"))


def test_channel_spaces_and_blocks():
    spaces = channel_spaces()
    assert spaces["leptonic_single_channel"].dimension == 1
    assert spaces["three_channel_active"].dimension == 3

    blocks = channel_algebra_blocks()
    assert blocks["C_ell"].algebra == "C"
    assert blocks["C_ell"].dimension == 1
    assert blocks["M3_C"].algebra == "M3(C)"
    assert blocks["M3_C"].dimension == 9


def test_channel_origin_document_guardrail():
    text = (ROOT / "theory" / "boundary_channel_automorphism_origin.md").read_text()
    assert "A_channel = End(V_ell) direct_sum End(V_C)" in text
    assert "P_C + P_ell = I_channel" in text
    assert "This is not yet a derivation of SU(3)." in text
