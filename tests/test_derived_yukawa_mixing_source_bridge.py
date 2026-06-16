import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_overlap_kernel as k  # noqa: E402


def test_mixing_source_bridge_is_symbolic_only():
    bridge = k.mixing_source_bridge()
    assert bridge["cyclic"] == "V_cyclic=U_cyclic_upper_L^dagger U_cyclic_lower_L"
    assert bridge["reference"] == "V_reference=U_reference_charged_L^dagger U_reference_neutral_L"
    assert k.ckm_values_derived() is False
    assert k.pmns_values_derived() is False


def test_mixing_source_bridge_document_preserves_guardrails():
    k.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_mixing_source_bridge.md").read_text()
    assert "V_cyclic=U_cyclic_upper_L^dagger U_cyclic_lower_L" in text
    assert "V_reference=U_reference_charged_L^dagger U_reference_neutral_L" in text
    assert "no CKM values" in text
    assert "no PMNS values" in text
    assert "YUKAWA_MIXING_SOURCE_BRIDGE_DERIVED_CONDITIONAL" in text
