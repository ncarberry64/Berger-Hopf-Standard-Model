import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_legacy_geometric_overlap as lg  # noqa: E402


def test_universal_higgs_topographic_profile_is_not_flavor_fit():
    lg.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_universal_higgs_topographic_profile.md").read_text()

    assert lg.universal_profile() == "Phi(y)=Phi0 exp[-sigma d_I(y,y0)^2]"
    assert lg.universal_profile() in text
    assert "universal across flavor" in text
    assert "universal across generation" in text
    assert "no fitted sector widths" in text
    assert "UNIVERSAL_HIGGS_TOPOGRAPHIC_PROFILE_DERIVED_CONDITIONAL" in text
