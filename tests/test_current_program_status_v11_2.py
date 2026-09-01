from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.aether_cycle_sigma_coefficient_reconstruction_v15_10 import EXACT_NEXT_OBJECT, PRIMARY_VERDICT
from bhsm.interface.current_program_status import CURRENT_VERSION, public_repo_status, status_payload


ROOT = Path(__file__).resolve().parents[1]


def test_historical_python_status_is_v15_10_and_fail_closed() -> None:
    payload = status_payload()
    assert CURRENT_VERSION == "v15.10"
    assert payload["primary_verdict"] == PRIMARY_VERDICT
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert "sigma-response inverse" in public_repo_status()
    assert payload["completion_marks"]["Mark_III_Physical_derivation"] == "NOT_REACHED"
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_repository_current_surfaces_are_synchronized() -> None:
    for name in ("README.md", "STATUS.md", "CLAIMS.md", "docs/current_bhsm_status.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "UNCHANGED_AE2_LOCALIZATION_CARRIER_FOUND = FALSE" in text, name
        assert "PHYSICAL_ENCAPSULATION_IDENTIFIED = FALSE" in text, name
        assert "FULL_BHSM_COMPLETE = FALSE" in text, name


def test_canonical_and_historical_machine_statuses_are_separated() -> None:
    current = json.loads((ROOT / "docs" / "current_bhsm_status.json").read_text(encoding="utf-8"))
    assert current["schema_version"] == "2.0"
    assert current["gate_7"]["status"] == "OPEN"
    historical = json.loads(
        (ROOT / "docs/archive/status/current_bhsm_status_pre_2026_09_01.json")
        .read_text(encoding="utf-8")
    )
    assert historical["current_version"] == CURRENT_VERSION
    assert historical["primary_verdict"] == PRIMARY_VERDICT


def test_historical_status_chronology_is_preserved() -> None:
    for name in ("STATUS.md", "CLAIMS.md", "ROADMAP.md", "FALSIFICATION.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "v11.3" in text.lower(), name
        assert "v11.1" in text.lower(), name

