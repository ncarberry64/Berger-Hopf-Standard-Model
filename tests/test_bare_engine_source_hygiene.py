from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_bare_engine_triangulation import (  # noqa: E402
    FROZEN_SOURCE,
    REFERENCE_SOURCE,
    SPECTRAL_ACTION_SOURCE,
    build_payload,
    existing_prediction_rows,
)


def test_sources_are_read_only_existing_repo_files() -> None:
    payload = build_payload(ROOT)
    assert payload["inputs"]["frozen_predictions_source"] == FROZEN_SOURCE
    assert payload["inputs"]["spectral_action_source"] == SPECTRAL_ACTION_SOURCE
    assert payload["inputs"]["reference_ratio_source"] == REFERENCE_SOURCE
    assert "docs/frozen_predictions.json" in payload["inputs"]["frozen_predictions_source"]
    assert "theory/bhsm_prediction_ledger.json" in payload["inputs"]["reference_ratio_source"]


def test_existing_prediction_extraction_uses_frozen_json_for_quarks_and_ledger_for_leptons() -> None:
    rows = existing_prediction_rows(ROOT)
    by_ratio = {row["ratio_name"]: row for row in rows}
    assert by_ratio["c/t"]["source"] == "docs/frozen_predictions.json"
    assert by_ratio["u/t"]["source"] == "docs/frozen_predictions.json"
    assert by_ratio["s/b"]["source"] == "docs/frozen_predictions.json"
    assert by_ratio["d/b"]["source"] == "docs/frozen_predictions.json"
    assert by_ratio["mu/tau"]["source"] == "theory/bhsm_prediction_ledger.json"
    assert by_ratio["e/tau"]["source"] == "theory/bhsm_prediction_ledger.json"


def test_no_src_files_are_required_for_triangulation_outputs() -> None:
    # The audit utility may import candidate theory helpers, but the generated
    # payload records no official source mutation and no official mass formula.
    payload = build_payload(ROOT)
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
    assert "no new official mass formula" in payload["notes"]

    serialized = json.dumps(payload).lower()
    assert "per-sector fit" not in serialized
    assert "official mass formula\": true" not in serialized
