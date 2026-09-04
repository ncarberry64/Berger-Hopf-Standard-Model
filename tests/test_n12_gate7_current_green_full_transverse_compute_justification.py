import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_n12_gate7_current_green_full_transverse_compute_justification.py"
RESULT = ROOT / "artifacts/current_semantics/BHSM_N12_GATE7_CURRENT_GREEN_FULL_TRANSVERSE_COMPUTE_JUSTIFICATION.json"
BENCHMARK = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_FULL_TRANSVERSE_COMPUTE_BENCHMARK.json"


def _module():
    spec = importlib.util.spec_from_file_location("full_transverse_compute", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_materializer_reproduces_authorized_payload():
    payload = _module().build_payload()
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload == stored
    assert payload["validation_passed"] is True
    assert payload["campaign_authorized"] is True


def test_campaign_is_bounded_and_restart_safe():
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    cost = payload["cost"]
    assert cost["total_rows"] == 740
    assert cost["selected_worker_count"] == 2
    assert cost["projected_total_CPU_hours_including_aborted_pilot"] < cost["fixed_campaign_CPU_ceiling"]
    assert payload["validation"]["existing_valid_shards_are_reused"] is True
    assert payload["validation"]["outward_authority_is_not_claimed_by_the_center_campaign"] is True


def test_benchmark_is_current_and_finite():
    benchmark = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    assert benchmark["validation_passed"] is True
    assert benchmark["benchmark"]["shard_revision"] == 4
    assert benchmark["benchmark"]["quadratic_Frobenius_norm"] > 283135.9524836309
