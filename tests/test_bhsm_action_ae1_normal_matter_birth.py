import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_bhsm_action_ae1_normal_matter_birth.py"


def _module():
    spec = importlib.util.spec_from_file_location("action_ae1_audit", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_action_ae1_stops_before_arbitrary_phase_selection() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    assert payload["action_version"] == "BHSM-AE-1.0.0"
    assert payload["adjudication"]["existing_geometry_forces_birth_law"] is False
    assert payload["adjudication"]["unique_action_extension_derived"] is False
    assert payload["adjudication"]["new_action_term_adopted"] is False
    assert payload["inequivalent_extension_witness"]["resolvents_distinct"] is True
    assert payload["candidate_class_contract"]["arbitrary_phase_selector_absent"] is False
    assert payload["owner_choice_return"]["Codex_selection"] is None
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_action_ae1_materialization_is_byte_deterministic(tmp_path: Path) -> None:
    module = _module()
    first = module.deterministic_bytes()
    second = module.deterministic_bytes()
    assert first == second
    path = tmp_path / "adjudication.json"
    path.write_bytes(first)
    assert path.read_bytes() == second
