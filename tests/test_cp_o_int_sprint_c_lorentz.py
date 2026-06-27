from pathlib import Path

from bhsm.interface.theorem_closure.cp_o_int_lorentz import build_lorentz_factor

ROOT = Path(__file__).resolve().parents[1]


def test_lorentz_factor_is_symbolic_not_derived():
    factor = build_lorentz_factor(ROOT)
    assert factor.status == "AVAILABLE_SYMBOLIC_CANDIDATE"
    assert factor.lorentz_scalar_required is True
    assert factor.is_artifact_backed is False
    assert factor.is_placeholder is True
    assert "contraction" in factor.missing_object
