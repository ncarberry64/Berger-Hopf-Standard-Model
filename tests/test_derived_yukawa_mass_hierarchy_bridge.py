import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_overlap_kernel as k  # noqa: E402


def test_mass_hierarchy_bridge_is_symbolic_only():
    assert k.mass_hierarchy_bridge() == "m_f,i ~ v/sqrt(2)*N_f*I_f(i,i)"
    assert k.numerical_overlap_values_derived() is False
    assert k.fermion_mass_ratios_derived() is False


def test_mass_hierarchy_bridge_document_preserves_guardrails():
    k.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_mass_hierarchy_bridge.md").read_text()
    assert "m_f,i ~ v/sqrt(2)*N_f*I_f(i,i)" in text
    assert "no numerical masses" in text
    assert "no mass ratios" in text
    assert "YUKAWA_MASS_HIERARCHY_BRIDGE_DERIVED_CONDITIONAL" in text
