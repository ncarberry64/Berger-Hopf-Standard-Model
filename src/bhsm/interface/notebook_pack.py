"""Parse-only notebook pack checks with no execution dependency."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

NOTEBOOKS = (
    "notebooks/BHSM_prediction_gallery.ipynb",
    "notebooks/BHSM_cli_review_walkthrough.ipynb",
    "notebooks/BHSM_theorem_blocker_sandbox.ipynb",
)


def notebook_pack_manifest() -> dict[str, Any]:
    return {
        "notebook_pack_name": "BHSM Prediction Review Notebook Pack",
        "version": "0.2",
        "notebooks": list(NOTEBOOKS),
        "offline_safe": True,
        "requires_jupyter": False,
        "requires_internet": False,
        "requires_pdg": False,
        "requires_wolfram": False,
        "requires_feynrules": False,
        "requires_madgraph": False,
        "execution_required_for_tests": False,
        "claim_boundaries": ["Parse-only tests", "No empirical validation", "Theorem blockers remain open"],
    }


def check_notebook_pack(repository_root: Path | None = None) -> dict[str, Any]:
    root = repository_root or Path(__file__).resolve().parents[3]
    rows = []
    for relative in NOTEBOOKS:
        path = root / relative
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            valid = payload.get("nbformat") == 4 and isinstance(payload.get("cells"), list)
        except (OSError, json.JSONDecodeError):
            valid = False
        rows.append({"path": relative, "exists": path.is_file(), "valid_json_notebook": valid})
    return {"passed": all(row["exists"] and row["valid_json_notebook"] for row in rows), "notebooks": rows, "execution_attempted": False}
