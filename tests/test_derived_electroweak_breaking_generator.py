import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_higgs_scalar as hs  # noqa: E402


def test_neutral_vev_and_breaking_skeleton():
    assert hs.neutral_vev_preserves_Q() is True
    assert hs.symmetry_breaking_skeleton() == "SU(2)_orient x U(1)_Y -> U(1)_Q"


def test_breaking_generator_documentation():
    hs.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_electroweak_breaking_generator.md").read_text()
    assert "<H> = (0, v/sqrt(2))^T" in text
    assert "Q <H> = 0" in text
    assert "SU(2)_orient x U(1)_Y -> U(1)_Q" in text
    assert "ELECTROWEAK_BREAKING_GENERATOR_DERIVED_CONDITIONAL" in text
