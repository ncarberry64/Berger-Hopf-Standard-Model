"""Validated author ontology used by the minimal-action closure evaluator."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .common import repository_path


AUTHOR_ONTOLOGY_PATH = "artifacts/BHSM_author_ontology_v0_8.json"


@dataclass(frozen=True)
class AuthorOntologyAxiom:
    axiom_key: str
    statement: str
    maximum_status: str
    artifact_support: tuple[str, ...]
    evidence_class: str
    definitions: Mapping[str, str]
    standalone_target_status: str | None = None


def load_author_ontology(repository: str | Path | None = None) -> dict[str, Any]:
    """Load the controlling author ontology without consulting external data."""

    path = repository_path(repository) / AUTHOR_ONTOLOGY_PATH
    if not path.is_file():
        return {"axioms": [], "source_status": "MISSING", "source_path": AUTHOR_ONTOLOGY_PATH}
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["source_status"] = "DISCOVERED"
    payload["source_path"] = AUTHOR_ONTOLOGY_PATH
    validate_author_ontology(payload)
    return payload


def validate_author_ontology(payload: Mapping[str, Any]) -> None:
    """Fail closed if the ontology weakens provenance or runtime guardrails."""

    if payload.get("author_supplied") is not True:
        raise ValueError("author ontology must be explicitly author supplied")
    guardrails = payload.get("guardrails", {})
    required_false = {
        "empirical_derivation_inputs_used",
        "pdg_values_used_as_theorem_inputs",
        "w_calibration_used_as_theorem_input",
        "frozen_predictions_changed",
        "official_predictions_changed",
        "feynrules_ready_claimed",
        "ufo_ready_claimed",
        "madgraph_ready_claimed",
        "empirical_validation_claimed",
    }
    if any(guardrails.get(key) is not False for key in required_false):
        raise ValueError("author ontology violates a required false guardrail")
    keys = [row.get("axiom_key") for row in payload.get("axioms", [])]
    if len(keys) != len(set(keys)):
        raise ValueError("author ontology axiom keys must be unique")


def require_author_axiom(payload: Mapping[str, Any], axiom_key: str) -> AuthorOntologyAxiom:
    """Return one enabled, structurally complete author axiom."""

    for row in payload.get("axioms", []):
        if row.get("axiom_key") == axiom_key and row.get("enabled") is True:
            return AuthorOntologyAxiom(
                axiom_key=axiom_key,
                statement=str(row["statement"]),
                maximum_status=str(row["maximum_status"]),
                artifact_support=tuple(str(path) for path in row.get("artifact_support", [])),
                evidence_class=str(row["evidence_class"]),
                definitions={str(key): str(value) for key, value in row.get("definitions", {}).items()},
                standalone_target_status=row.get("standalone_target_status"),
            )
    raise ValueError(f"required author ontology axiom is missing or disabled: {axiom_key}")
