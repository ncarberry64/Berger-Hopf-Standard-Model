import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_y0_axis_identification as y0  # noqa: E402


def test_m_equals_q_over_two_is_not_promotable_without_axis_sampling():
    assert y0.m_equals_q_over_2_promotable() is y0.y0_axis_sampling_derived()
    assert y0.m_equals_q_over_2_promotable() is False
    y0.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_y0_to_m_weight_bridge.md").read_text()
    assert "`m=n=q/2` becomes promotable only if `y0` axis sampling is derived" in text
    assert "M_EQUALS_Q_OVER_2_REMAINS_STRUCTURALLY_MOTIVATED" in text
