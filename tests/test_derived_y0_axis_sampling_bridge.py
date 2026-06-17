import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_y0_axis_identification as y0  # noqa: E402


def test_axis_sampling_follows_only_axis_derivation():
    assert y0.y0_axis_sampling_derived() is False
    assert "D^ell_{m,n}(y0)=delta_mn only if" in y0.wigner_axis_sampling_rule()
    y0.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_y0_axis_sampling_bridge.md").read_text()
    assert "WIGNER_HOPF_AXIS_SAMPLING_REMAINS_OPEN" in text
