"""Typed factors for the artifact-traced CP O_int symbolic candidate."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ..artifact_sources import load_artifact_json, repository_root
from .cp_o_int_attachment import load_cp_phase_attachment

EFFECTIVE_LAGRANGIAN_PATH = "artifacts/BHSM_effective_lagrangian_candidate_v0_3.json"
SYMBOLIC_LEDGER_PATH = "artifacts/BHSM_symbolic_4d_lagrangian_assembly_ledger_v0_9.json"


class _Serializable:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CPOIntPhaseFactor(_Serializable):
    expression: str
    value: dict[str, Any]
    status: str
    source: str
    provenance: tuple[str, ...]
    is_artifact_backed: bool
    is_author_axiom: bool
    is_placeholder: bool
    missing_object: str | None
    claim_boundary: str


@dataclass(frozen=True)
class CPOIntFieldFactor(_Serializable):
    field_symbols: tuple[str, ...]
    representation: str
    chirality_defined: bool
    family_indices_defined: bool
    conjugation_defined: bool
    status: str
    source: str
    provenance: tuple[str, ...]
    is_artifact_backed: bool
    is_author_axiom: bool
    is_placeholder: bool
    missing_object: str | None
    claim_boundary: str


@dataclass(frozen=True)
class CPOIntBoundaryFactor(_Serializable):
    symbol: str
    expression: str
    locality: str
    status: str
    source: str
    provenance: tuple[str, ...]
    is_artifact_backed: bool
    is_author_axiom: bool
    is_placeholder: bool
    missing_object: str | None
    claim_boundary: str


@dataclass(frozen=True)
class CPOIntFieldActionCandidate(_Serializable):
    candidate_key: str
    expression: str
    phase_factor: CPOIntPhaseFactor
    field_factor: CPOIntFieldFactor
    boundary_factor: CPOIntBoundaryFactor
    status: str
    source_artifacts: tuple[str, ...]
    claim_boundary: str


@dataclass(frozen=True)
class CPOIntProductionEligibility(_Serializable):
    production_eligible: bool
    runtime_export_eligible: bool
    production_missing: tuple[str, ...]
    runtime_missing: tuple[str, ...]
    status: str


def _term(payload: dict[str, Any], term_id: str) -> dict[str, Any]:
    return next((row for row in payload.get("terms", []) if row.get("term_id") == term_id), {})


def load_cp_symbolic_sources(repository: str | Path | None = None) -> dict[str, Any]:
    root = Path(repository).resolve() if repository is not None else repository_root()
    effective_path = root / EFFECTIVE_LAGRANGIAN_PATH
    ledger_path = root / SYMBOLIC_LEDGER_PATH
    effective = load_artifact_json(effective_path) if effective_path.is_file() else {}
    ledger = load_artifact_json(ledger_path) if ledger_path.is_file() else {}
    return {
        "effective_term": _term(effective, "cp_holonomy_term"),
        "ledger_term": _term(ledger, "L_CP_holonomy_candidate"),
        "sources": tuple(path for path in (EFFECTIVE_LAGRANGIAN_PATH, SYMBOLIC_LEDGER_PATH) if (root / path).is_file()),
    }


def build_phase_factor(repository: str | Path | None = None) -> CPOIntPhaseFactor:
    attachment = load_cp_phase_attachment(repository)
    available = attachment.delta_bh is not None and attachment.boundary_phase is not None
    return CPOIntPhaseFactor(
        expression="exp(i*delta_BH)",
        value={"delta_BH": attachment.delta_bh, "Z6_boundary_phase": attachment.boundary_phase},
        status="AVAILABLE_ARTIFACT_BACKED" if available else "OPEN_MISSING_INTERACTION_ATTACHMENT",
        source="BHSM CP holonomy artifact",
        provenance=attachment.source_artifacts,
        is_artifact_backed=available,
        is_author_axiom=False,
        is_placeholder=False,
        missing_object=None if available else "artifact-backed CP phase",
        claim_boundary="An artifact-backed phase is not a standalone interaction.",
    )


def build_field_factor(repository: str | Path | None = None) -> CPOIntFieldFactor:
    sources = load_cp_symbolic_sources(repository)
    row = sources["effective_term"]
    fields = tuple(str(value) for value in row.get("field_symbols", ()))
    return CPOIntFieldFactor(
        field_symbols=fields or ("Psi_CP_interface",),
        representation="abstract boundary/interface field only; physical representation not derived",
        chirality_defined=False,
        family_indices_defined=False,
        conjugation_defined=False,
        status="AVAILABLE_SYMBOLIC_CANDIDATE",
        source="existing symbolic CP holonomy term",
        provenance=sources["sources"],
        is_artifact_backed=bool(row),
        is_author_axiom=False,
        is_placeholder=True,
        missing_object="action-derived physical field representation with chirality, family indices, and conjugation rules",
        claim_boundary="The generic psi symbol is a symbolic placeholder, not a production field definition.",
    )


def build_boundary_factor(repository: str | Path | None = None) -> CPOIntBoundaryFactor:
    sources = load_cp_symbolic_sources(repository)
    row = sources["effective_term"]
    expression = str(row.get("candidate_density_expression", "candidate: H_CP[boundary holonomy]"))
    return CPOIntBoundaryFactor(
        symbol="H_CP",
        expression=expression,
        locality="boundary/interface-local symbolic candidate",
        status="AVAILABLE_SYMBOLIC_CANDIDATE",
        source="existing effective-Lagrangian candidate artifact",
        provenance=sources["sources"],
        is_artifact_backed=bool(row),
        is_author_axiom=False,
        is_placeholder=True,
        missing_object="boundary-to-action projection theorem and defined integration measure",
        claim_boundary="The boundary symbol is source-traced but not an action-derived operator.",
    )
