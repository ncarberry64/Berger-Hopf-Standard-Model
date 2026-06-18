import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_m_multiplet_harmonic_features as mm  # noqa: E402


def test_axis_collapse_rule_documents_leading_component_but_does_not_force_it():
    rule = mm.axis_collapse_rule()
    assert "delta_mn" in rule
    assert "m=n=q/2" in rule
    assert mm.single_m_assignment_forced() is False


def test_generic_y0_rule_retains_full_multiplet():
    rule = mm.generic_y0_rule()
    assert "full" in rule.lower()
    assert "D^ell_{m,n}" in rule
