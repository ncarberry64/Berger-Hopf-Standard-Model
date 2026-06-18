import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_higgs_scalar as hs  # noqa: E402


def test_covariant_derivative_and_mass_skeleton():
    derivative = hs.scalar_covariant_derivative_skeleton()
    assert "g2" in derivative
    assert "gY" in derivative
    assert "Y=1" in derivative
    masses = hs.gauge_boson_mass_skeleton()
    assert masses["m_W_squared"] == "g2^2 v^2/4"
    assert masses["m_Z_squared"] == "(g2^2+gY^2)v^2/4"
    assert masses["m_A_squared"] == "0"


def test_covariant_derivative_documentation():
    hs.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_scalar_covariant_derivative.md").read_text()
    assert "su(2)_orient" in text
    assert "u(1)_Y" in text
    assert "m_A^2 = 0" in text
    assert "not a measured mass prediction" in text
    assert "SCALAR_COVARIANT_DERIVATIVE_DERIVED_CONDITIONAL" in text
