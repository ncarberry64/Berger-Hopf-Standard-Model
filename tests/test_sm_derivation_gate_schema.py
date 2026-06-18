from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_sm_derivation_gate import (  # noqa: E402
    BRANCH,
    DERIVATION_STATUSES,
    TARGET_CLASSIFICATIONS,
    VERDICT_LABELS,
    build_results_payload,
    classify_target,
    export_outputs,
    is_full_replacement_claim_allowed,
)


def test_sm_derivation_gate_json_schema() -> None:
    payload = export_outputs(ROOT)
    parsed = json.loads(
        (ROOT / "theory" / "sm_low_energy_limit_derivation_results.json").read_text(
            encoding="utf-8"
        )
    )
    assert parsed == payload
    assert parsed["status"] == "candidate_only"
    assert parsed["branch"] == BRANCH
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["bhsm_replacement_claim_allowed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["local_sm_layer_status"] == "preserved_as_input"
    assert parsed["replacement_by_derivation_goal"] is True
    assert parsed["core_particle_sector_only"] is True
    assert parsed["collective_curvature_extension_separate"] is True
    assert parsed["verdict_labels"] == VERDICT_LABELS


def test_required_classifications_are_exact() -> None:
    assert set(TARGET_CLASSIFICATIONS.values()) <= set(DERIVATION_STATUSES)
    assert classify_target("Three-generation discrete skeleton") == "partially_derived"
    assert classify_target("Fermion mode ledger") == "partially_derived"
    assert classify_target("Local SM gauge group") == "preserved_as_input"
    assert classify_target("B, L, T3 labels") == "preserved_as_input"
    assert classify_target("Hypercharge assignments") == "preserved_as_input"
    assert classify_target("Full chiral field content") == "preserved_as_input"
    assert classify_target("Gauge coupling ratio 1:2:7") == "partially_derived"
    assert classify_target("Gauge group derivation") == "open_derivation_obligation"
    assert classify_target("Higgs/scalar decoupling") == "open_derivation_obligation"
    assert classify_target("Mass numerical closure") == "failed_or_limited_candidate"
    assert classify_target("Collective-curvature/dark matter") == "connected_extension_only"


def test_replacement_claim_requires_all_core_derivations() -> None:
    incomplete = {
        "local_gauge_group_derived": True,
        "field_content_derived": True,
    }
    complete = {
        "local_gauge_group_derived": True,
        "field_content_derived": True,
        "charge_assignments_derived": True,
        "masses_mixings_derived": True,
        "higgs_scalar_derived": True,
        "anomaly_cancellation_derived": True,
        "low_energy_lagrangian_recovered": True,
    }
    assert is_full_replacement_claim_allowed(incomplete) is False
    assert is_full_replacement_claim_allowed(complete) is True
