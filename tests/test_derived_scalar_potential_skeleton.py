import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_higgs_scalar as hs  # noqa: E402


def test_scalar_potential_parameter_predictions_remain_open():
    assert hs.higgs_mass_predicted() is False
    assert hs.vev_predicted() is False
    assert hs.quartic_predicted() is False
    assert hs.yukawa_sector_derived() is False
    assert hs.replacement_claim_ready() is False


def test_scalar_potential_documentation():
    hs.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_scalar_potential_skeleton.md").read_text()
    assert "V(H)=m_H^2 H^dagger H + lambda_H (H^dagger H)^2" in text
    assert "m_H^2 < 0" in text
    assert "remain open/conditional" in text
    assert "SCALAR_POTENTIAL_SKELETON_DERIVED_CONDITIONAL" in text
