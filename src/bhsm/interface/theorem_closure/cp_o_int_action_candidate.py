"""Artifact-traced symbolic CP O_int action-density candidate."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from ..artifact_sources import repository_root
from .cp_o_int_field_action import load_cp_symbolic_sources

TEMPLATE_PATH = "data/theorem_inputs/cp_o_int_field_action_candidate_template.json"


@dataclass(frozen=True)
class CPOIntActionDensityCandidate:
    symbol: str
    expression: str
    integration_measure: str
    locality: str
    variation_eom_defined: bool
    status: str
    source: str
    provenance: tuple[str, ...]
    is_artifact_backed: bool
    is_author_axiom: bool
    is_placeholder: bool
    missing_object: str | None
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_field_action_template(
    path: str | Path | None = None,
    repository: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repository).resolve() if repository is not None else repository_root()
    selected = Path(path) if path is not None else root / TEMPLATE_PATH
    if not selected.is_absolute():
        selected = root / selected
    if not selected.is_file():
        return {"enabled": False, "source_status": "ARTIFACT_NOT_FOUND", "path": selected.as_posix()}
    payload = json.loads(selected.read_text(encoding="utf-8"))
    payload["source_status"] = "DISCOVERED"
    payload["path"] = selected.relative_to(root).as_posix() if selected.is_relative_to(root) else selected.as_posix()
    return payload


def field_action_template_enabled(template: Mapping[str, Any] | None) -> bool:
    return bool(template and template.get("enabled") is True and template.get("author_supplied") is True)


def build_action_density_candidate(
    repository: str | Path | None = None,
    template: Mapping[str, Any] | None = None,
) -> CPOIntActionDensityCandidate:
    if field_action_template_enabled(template) and template.get("action_density"):
        return CPOIntActionDensityCandidate(
            "L_CP_O_int",
            str(template["action_density"]),
            str(template.get("integration_measure", "author supplied")),
            str(template.get("locality", "author supplied")),
            bool(template.get("variation_eom_defined", False)),
            "AVAILABLE_AUTHOR_AXIOM_CONDITIONAL",
            str(template.get("path", "author-supplied template")),
            (str(template.get("path", "author-supplied template")),),
            False, True, False,
            "action-derived source remains absent",
            "A conditional author action is not production-ready or action-derived.",
        )
    sources = load_cp_symbolic_sources(repository)
    row = sources["ledger_term"]
    expression = str(row.get("symbolic_expression", "G_raw exp(i delta_BH) O_int + h.c."))
    return CPOIntActionDensityCandidate(
        "L_CP_holonomy_candidate",
        expression,
        "undefined boundary/interface measure",
        "boundary/interface-local symbolic candidate",
        False,
        "AVAILABLE_SYMBOLIC_CANDIDATE",
        "existing symbolic 4D Lagrangian assembly ledger",
        sources["sources"],
        bool(row), False, True,
        "action-derived measure, locality theorem, variation, and EOM effect",
        "The source-traced symbolic density is not an action-derived theorem.",
    )
