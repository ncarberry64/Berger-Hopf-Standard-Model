from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_n12_gate7_current_green_mixed_outward_compute_justification.py"
ARTIFACT = ROOT / "artifacts/current_semantics/BHSM_N12_GATE7_CURRENT_GREEN_MIXED_OUTWARD_COMPUTE_JUSTIFICATION.json"


def _module():
    spec = importlib.util.spec_from_file_location("mixed_outward_compute", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_reduced_owner_witness_is_authorized_without_global_campaign() -> None:
    payload = _module().build_payload()
    assert payload == json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["artifact"] == (
        "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_OUTWARD_COMPUTE_JUSTIFICATION"
    )
    assert payload["validation_passed"] is True
    assert payload["authorization"][
        "owner_leading_direction_512_bit_polarization_witness"
    ] is True
    assert payload["authorization"]["worker_count"] == 1
    assert payload["authorization"]["automatic_follow_on_global_campaign"] is False
    assert payload["cost"]["new_directional_evaluations"] == 6
    assert payload["cost"]["scientific_directional_evaluations"] == 2
    assert payload["cost"][
        "packaging_and_provenance_retry_directional_evaluations"
    ] == 4
    assert payload["authorization"][
        "two_identical_packaging_and_provenance_retries"
    ] is True
    assert payload["cost"]["new_owner_witness_wall_minutes_ceiling"] < 30.0


def test_compute_policy_does_not_promote_science() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["claim_boundary"]["FULL_370_ENDPOINT_RECONNAISSANCE_COMPLETE"]
    assert payload["claim_boundary"]["OUTWARD_BILINEAR_EQUIVALENCE_DERIVED"] is False
    assert payload["claim_boundary"]["GATE7_CLOSED"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
