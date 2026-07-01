"""Audit the artifact-backed boundary of the located CKM interface term."""

from __future__ import annotations

import json

from .common import STATUS_BOUNDED, input_guard, repository_root


def audit_ckm_bounded_interface_term() -> dict[str, object]:
    path = repository_root() / "artifacts/BHSM_minimal_bounded_lagrangian_subset_v1_2.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    term = next(row for row in payload["terms"] if row["term_id"] == "L_CKM_charged_current_bounded")
    return {
        "audit": "ckm_bounded_interface_term",
        "term_name": term["term_id"],
        "term_location": path.relative_to(repository_root()).as_posix(),
        "symbolic_form_if_available": term["symbolic_expression"],
        "boundedness_source": "included in the minimal bounded collider-interface subset",
        "what_is_artifact_backed": [
            "term presence and symbolic target form",
            "inclusion in the bounded collider-interface subset",
            "BHSM collider-interface runtime parameter mode",
            "local CKM source-matrix attachment",
        ],
        "what_is_not_proven": [
            "complete BHSM 4D action term",
            "action-derived coefficient normalization",
            "boundary/action measure",
            "sector projector sandwich",
            "operator domain and codomain",
            "CKM transport-space selection",
        ],
        "status": STATUS_BOUNDED,
        "claim_boundary": "L_CKM_charged_current_bounded is a bounded interface term, not automatically a normalized action-selected transport operator.",
        **input_guard(),
    }
