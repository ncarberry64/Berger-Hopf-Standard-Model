import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_compact_history_endpoint_role_provenance.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_COMPACT_HISTORY_ENDPOINT_ROLE_PROVENANCE.json"
)


def _module():
    spec = importlib.util.spec_from_file_location("endpoint_roles", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_compact_history_endpoint_roles_validate() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    assert payload["endpoint_roles"]["birth"][
        "adjacent_exterior_response_required_for_reference"
    ] is False
    assert payload["exact_dependency_after_endpoint_partition"][
        "missing_terminal_C2_response"
    ] is True
    assert payload["claim_boundary"]["endpoint_role_ambiguity"] == "CLOSED"


def test_compact_history_endpoint_roles_replay() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = RESULT.read_bytes()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = RESULT.read_bytes()
    assert first == second
    assert json.loads(first)["validation_passed"] is True
