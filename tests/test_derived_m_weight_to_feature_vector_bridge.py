from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_m_weight_to_feature_vector_bridge_is_symbolic_until_m_is_derived():
    text = (ROOT / "theory" / "derived_m_weight_to_feature_vector_bridge.md").read_text()

    assert "F_{k,j,m}(y0)=(psi,d_a psi,d_a d_b psi)|_y0" in text
    assert "symbolic until `m` and explicit harmonics are derived" in text
    assert "EXPLICIT_EIGENFUNCTION_VALUES_REMAIN_OPEN" in text
