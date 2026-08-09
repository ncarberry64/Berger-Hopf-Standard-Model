from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.aether_nonlinear_norman_cycle_bvp_v15_7 import EXACT_NEXT_OBJECT, PRIMARY_VERDICT
from bhsm.interface.current_program_status import CURRENT_VERSION, public_repo_status, status_payload


ROOT = Path(__file__).resolve().parents[1]


def test_python_current_status_is_v15_7_and_fail_closed() -> None:
    payload = status_payload()
    assert CURRENT_VERSION == "v15.7"
    assert payload["primary_verdict"] == PRIMARY_VERDICT
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert "no-fit spectral charged-current candidate" in public_repo_status()
    assert payload["completion_marks"]["Mark_III_Physical_derivation"] == "NOT_REACHED"
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_repository_current_surfaces_are_synchronized() -> None:
    for name in ("README.md", "STATUS.md", "CLAIMS.md", "ROADMAP.md", "FALSIFICATION.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "v15.7" in text.lower(), name
        assert EXACT_NEXT_OBJECT in text, name
    assert PRIMARY_VERDICT in (ROOT / "STATUS.md").read_text(encoding="utf-8")
    current = json.loads((ROOT / "docs" / "current_bhsm_status.json").read_text(encoding="utf-8"))
    assert current["current_version"] == CURRENT_VERSION
    assert current["primary_verdict"] == PRIMARY_VERDICT


def test_historical_status_chronology_is_preserved() -> None:
    for name in ("STATUS.md", "CLAIMS.md", "ROADMAP.md", "FALSIFICATION.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "v11.3" in text.lower(), name
        assert "v11.1" in text.lower(), name

