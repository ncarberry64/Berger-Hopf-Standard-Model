import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_forward_graded_phase_independence.py"


def _module():
    spec = importlib.util.spec_from_file_location("graded_phase_no_go", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_graded_phase_independence_payload() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    assert payload["adjudication"][
        "universal_Ward_BRST_phase_independence_identity"
    ] is False
    assert payload["graded_heat_integrand_phase_difference"][
        "zero_excluded"
    ] is True
    assert payload["claim_boundary"][
        "actual_N12_history_specific_cancellation_excluded"
    ] is False
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
