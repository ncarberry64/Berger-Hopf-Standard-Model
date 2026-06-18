from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_internal_mode_amplitude_hierarchy_bridge_keeps_values_open():
    text = (ROOT / "theory" / "derived_internal_mode_amplitude_hierarchy_bridge.md").read_text()

    assert "Node suppression" in text
    assert "Anisotropic focusing" in text
    assert "Off-diagonal entries reflect" in text
    assert "No numerical values are derived" in text
    assert "INTERNAL_MODE_AMPLITUDE_HIERARCHY_BRIDGE_DERIVED_CONDITIONAL" in text
