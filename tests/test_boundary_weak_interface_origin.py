import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_automorphism_closure import weak_algebra_blocks, weak_interface_spaces  # noqa: E402


def test_weak_interface_spaces_and_blocks():
    spaces = weak_interface_spaces()
    assert spaces["weak_active"].dimension == 2
    assert spaces["inactive_upper"].dimension == 1
    assert spaces["inactive_lower"].dimension == 1

    blocks = weak_algebra_blocks()
    assert blocks["M2_active"].algebra == "M2(C)"
    assert blocks["M2_active"].dimension == 4
    assert blocks["C_sigma_plus"].algebra == "C"
    assert blocks["C_sigma_plus"].dimension == 1
    assert blocks["C_sigma_minus"].algebra == "C"
    assert blocks["C_sigma_minus"].dimension == 1


def test_weak_interface_origin_document_guardrail():
    text = (ROOT / "theory" / "boundary_weak_interface_origin.md").read_text()
    assert "A_weak = M2(C)_{w=1} direct_sum C_{sigma=+} direct_sum C_{sigma=-}" in text
    assert "S_sigma^2 = I" in text
    assert "This is not yet a derivation of SU(2)_L." in text
