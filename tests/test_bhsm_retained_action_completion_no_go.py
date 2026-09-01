import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_bhsm_retained_action_completion_no_go.py"


def _module():
    spec = importlib.util.spec_from_file_location("completion_no_go", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_retained_action_completion_no_go_payload() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    assert payload["campaign_terminal_condition"] == 2
    assert payload["terminal_adjudication"]["canonical_no_go_earned"] is True
    assert payload["terminal_adjudication"]["FULL_BHSM_COMPLETE"] is False
    assert payload["validation"][
        "far_endpoint_Friedrichs_does_not_select_matter_birth_graph"
    ] is True
    assert payload["future_scope"][
        "no_go_for_all_possible_BHSM_action_extensions"
    ] is False
    assert payload["claim_boundary"]["new_action_term_added"] is False
