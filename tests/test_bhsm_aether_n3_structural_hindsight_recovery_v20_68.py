import json
from pathlib import Path


def test_structural_hindsight_uses_exact_merit_and_unchanged_physics() -> None:
    payload = json.loads(Path("artifacts/BHSM_N3_STRUCTURAL_HINDSIGHT_RECOVERY_V20_68.json").read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    result = payload["structural_hindsight_recovery"]
    assert result["source_frontier"]["version"] == "v20.66"
    assert result["classification"].startswith(tuple(f"H{i}:" for i in range(1, 7)))
    assert not result["physical_equations_changed"]
    assert not result["complete_child_gate_changed"]
