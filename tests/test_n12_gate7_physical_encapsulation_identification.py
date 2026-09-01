from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface.physical_encapsulation_identification import (
    assert_no_forbidden_equivalence,
    evaluate_identification,
)
from scripts.materialize_n12_gate7_physical_encapsulation_identification import (
    build_payload,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / (
    "scripts/materialize_n12_gate7_physical_encapsulation_identification.py"
)
TARGET = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_PHYSICAL_ENCAPSULATION_IDENTIFICATION_BRIDGE.json"
)


def test_current_evidence_fails_closed_after_the_mathematical_carrier() -> None:
    payload = build_payload()
    bridge = payload["bridge_evaluation"]
    satisfied = {
        row["id"]: row["satisfied"] for row in bridge["requirements"]
    }
    assert satisfied["PEI_01"] is True
    assert satisfied["PEI_02"] is True
    assert satisfied["PEI_10"] is True
    assert satisfied["PEI_03"] is False
    assert satisfied["PEI_04"] is False
    assert satisfied["PEI_05"] is False
    assert satisfied["PEI_06"] is False
    assert satisfied["PEI_07"] is False
    assert satisfied["PEI_08"] is False
    assert satisfied["PEI_09"] is False
    assert bridge["physical_encapsulation_identified"] is False


def test_route_is_not_silently_identified_with_spacetime_edge() -> None:
    payload = build_payload()
    routes = payload["admissible_enclosure_routes"]
    assert routes["current_selection"] is None
    assert routes["spacetime_edge_required"] is False
    assert "SPACETIME_EDGE_TRANSITION" in routes["routes"]
    assert payload["forbidden_substitutions"][
        "canonical_stop_equals_spacetime_edge"
    ] is False


def test_particle_manifestation_requires_transport_not_spectrum_rebuild() -> None:
    evidence = {f"PEI_{index:02d}": True for index in range(1, 11)}
    generic = evaluate_identification(
        evidence, particle_state_transport_claimed=False
    )
    particle = evaluate_identification(
        evidence, particle_state_transport_claimed=True
    )
    assert generic["physical_encapsulation_identified"] is True
    assert particle["physical_encapsulation_identified"] is False
    assert particle["missing_required_obligations"] == ["PEI_11"]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"lambda24_equals_two_pi": True},
        {"canonical_stop_equals_spacetime_edge": True},
        {"positive_duration_equals_stability": True},
    ],
)
def test_forbidden_equivalences_raise(kwargs: dict[str, bool]) -> None:
    values = {
        "lambda24_equals_two_pi": False,
        "canonical_stop_equals_spacetime_edge": False,
        "positive_duration_equals_stability": False,
    }
    values.update(kwargs)
    with pytest.raises(ValueError, match="unsupported physical equivalence"):
        assert_no_forbidden_equivalence(**values)


def test_materialized_artifact_is_deterministic_and_guarded() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    payload = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["first_stop_strengthened"] is False
    assert payload["claim_boundary"]["historical_particle_spectrum_rebuilt"] is False
    assert payload["claim_boundary"]["upstream_particle_assets_modified"] is False
    assert payload["claim_boundary"]["new_action_term_added"] is False
    assert payload["claim_boundary"]["new_numerical_run_used"] is False
    assert payload["claim_boundary"]["Gate7_closed"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_historical_particle_assets_are_imported_with_provenance() -> None:
    payload = build_payload()
    policy = payload["upstream_particle_asset_policy"]
    paths = {asset["path"] for asset in policy["assets"]}
    assert "artifacts/BHSM_aether_hybrid_standard_model_bundle_v15_53.json" in paths
    assert "artifacts/BHSM_generation_projector_action_attachment_v8_2.json" in paths
    assert "artifacts/BHSM_parent_action_charged_current_v11_6.json" in paths
    assert "theory/derived_hopf_phase_closure.md" in paths
    assert all(asset["sha256"] for asset in policy["assets"])
    assert payload["current_evidence"]["particle_state_registry"][
        "spectrum_rederived"
    ] is False
