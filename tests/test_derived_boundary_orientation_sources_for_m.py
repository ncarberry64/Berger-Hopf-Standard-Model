import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_m_weight_assignment as mw  # noqa: E402


def test_boundary_orientation_sources_for_m_include_required_sources():
    mw.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_boundary_orientation_sources_for_m.md").read_text()

    for source in [
        "weak orientation sigma=2T3",
        "active interface w",
        "active/singlet side",
        "left/right chirality",
        "scalar insertion H or H_tilde",
        "cyclic/reference channel",
        "boundary orientation algebra",
        "charge closure Q,T3,Y",
    ]:
        assert source in mw.candidate_m_sources()
        assert source in text
