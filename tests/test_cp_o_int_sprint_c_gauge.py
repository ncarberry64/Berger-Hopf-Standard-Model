from pathlib import Path

from bhsm.interface.theorem_closure.cp_o_int_gauge import build_gauge_factor

ROOT = Path(__file__).resolve().parents[1]


def test_gauge_factor_forbids_cross_theorem_leakage():
    factor = build_gauge_factor(ROOT)
    assert factor.status == "AVAILABLE_SYMBOLIC_CANDIDATE"
    assert factor.is_placeholder is True
    assert set(factor.forbidden_leakage) == {"X_ch closure", "neutrino physical mass closure"}
    assert "gauge representation" in factor.missing_object
