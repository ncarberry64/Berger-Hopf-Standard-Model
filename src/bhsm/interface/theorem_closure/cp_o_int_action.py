"""Standalone CP O_int action candidate and disabled author-template loader."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from ..artifact_sources import repository_root

DEFAULT_TEMPLATE_PATH = "data/theorem_inputs/cp_o_int_attachment_candidate_template.json"


@dataclass(frozen=True)
class CPOIntActionCandidate:
    symbol: str
    expression: str
    interaction_defined: bool
    action_derived: bool
    author_supplied: bool
    status: str
    source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_cp_o_int_candidate_template(
    path: str | Path | None = None,
    repository: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repository).resolve() if repository is not None else repository_root()
    selected = Path(path) if path is not None else root / DEFAULT_TEMPLATE_PATH
    if not selected.is_absolute():
        selected = root / selected
    if not selected.is_file():
        return {"enabled": False, "source_status": "ARTIFACT_NOT_FOUND", "path": selected.as_posix()}
    payload = json.loads(selected.read_text(encoding="utf-8"))
    payload["source_status"] = "DISCOVERED"
    payload["path"] = selected.relative_to(root).as_posix() if selected.is_relative_to(root) else selected.as_posix()
    return payload


def candidate_is_enabled(candidate: Mapping[str, Any] | None) -> bool:
    return bool(candidate and candidate.get("enabled") is True and candidate.get("author_supplied") is True)


def candidate_is_complete(candidate: Mapping[str, Any] | None) -> bool:
    required = (
        "formal_statement", "domain", "codomain", "field_representation",
        "lorentz_structure", "gauge_admissibility", "phase_attachment_rule",
        "coupling_normalization", "action_term",
    )
    return candidate_is_enabled(candidate) and all(candidate.get(key) not in (None, "", {}, []) for key in required)


def action_from_candidate(candidate: Mapping[str, Any] | None) -> CPOIntActionCandidate:
    if not candidate_is_enabled(candidate) or not candidate.get("action_term"):
        return CPOIntActionCandidate("O_int", "", False, False, False, "OPEN_MISSING_ACTION_SOURCE", "not present in local action artifacts")
    return CPOIntActionCandidate(
        "O_int",
        str(candidate["action_term"]),
        True,
        False,
        True,
        "AUTHOR_AXIOM_CONDITIONAL",
        str(candidate.get("path", "author-supplied candidate template")),
    )
