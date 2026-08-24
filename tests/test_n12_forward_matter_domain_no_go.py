import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_forward_matter_domain_no_go.py"


def _module():
    spec = importlib.util.spec_from_file_location("matter_domain_no_go", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_matter_domain_no_go_payload() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    assert payload["status"] == "CANONICAL_UNCHANGED_RETAINED_ACTION_NO_GO"
    assert payload["adjudication"][
        "retained_action_defines_unique_full_Gate7_operator"
    ] is False
    assert payload["exact_resolvent_separation"]["nonzero"] is True
    assert payload["claim_boundary"]["new_action_term_added"] is False
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
