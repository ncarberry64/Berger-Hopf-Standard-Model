import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/adjudicate_n12_gate7_ae2_maximal_exterior.py"


def _adjudicator():
    spec = importlib.util.spec_from_file_location("ae2_maximal_exterior", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ae2_maximal_exterior_adjudication_localizes_the_new_no_go() -> None:
    payload = _adjudicator().build_payload()
    assert payload["validation_passed"] is True
    assert payload["action_extension_adjudication"]["selected_option"] == "A"
    assert payload["action_extension_adjudication"][
        "self_adjoint_physical_matter_domain"
    ] == "CLOSED"
    assert payload["Gate7_native_requirement"]["choice"] == "C"
    assert payload["Gate7_native_requirement"][
        "universal_terminal_event_reachability_required"
    ] is False
    assert payload["adjudication"]["new_canonical_no_go_reached"] is True
    assert payload["adjudication"]["additional_action_extension_required"] is False
    assert payload["adjudication"]["Gate7"] == "ACTIVE_NOT_CLOSED"
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_ae2_maximal_exterior_adjudication_is_byte_deterministic() -> None:
    module = _adjudicator()
    assert module.deterministic_bytes(module.build_payload()) == (
        module.deterministic_bytes(module.build_payload())
    )
