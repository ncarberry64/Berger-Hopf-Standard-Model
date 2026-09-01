import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_finite_terminal_forward_component_compatibility.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_TERMINAL_FORWARD_COMPONENT_COMPATIBILITY.json"
)


def _module():
    spec = importlib.util.spec_from_file_location("terminal_component_audit", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_terminal_incidence_is_not_promoted_to_positive_duration_history():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["finite_terminal_incidence"] == "CERTIFIED"
    assert payload["claim_boundary"]["finite_terminal_incoming_germ"] == "CERTIFIED"
    assert payload["claim_boundary"][
        "positive_duration_reset_to_later_endpoint_history"
    ] == "OPEN_CURRENT_OWNER"
    assert "T=0" in payload["exact_logical_factorization"][
        "why_the_terminal_root_is_not_that_connection"
    ]
    assert payload["claim_boundary"]["actual_projected_force"] == "OPEN_AFTER_OPERATOR"
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_generated_terminal_component_audit_is_reproducible():
    assert _module().build_payload() == json.loads(
        ARTIFACT.read_text(encoding="utf-8")
    )
