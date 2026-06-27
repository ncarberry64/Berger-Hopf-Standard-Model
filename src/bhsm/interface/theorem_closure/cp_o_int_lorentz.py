"""Lorentz/index factor for the symbolic CP O_int construction."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .cp_o_int_field_action import load_cp_symbolic_sources


@dataclass(frozen=True)
class CPOIntLorentzFactor:
    expression: str
    index_structure: str
    lorentz_scalar_required: bool
    hermiticity_rule: str
    cp_sensitive_structure: str
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


def build_lorentz_factor(repository: str | Path | None = None) -> CPOIntLorentzFactor:
    sources = load_cp_symbolic_sources(repository)
    return CPOIntLorentzFactor(
        expression="LorentzScalar[O_int] + h.c.",
        index_structure="unspecified symbolic contraction",
        lorentz_scalar_required=True,
        hermiticity_rule="add Hermitian conjugate",
        cp_sensitive_structure="complex phase multiplies O_int and its conjugate",
        status="AVAILABLE_SYMBOLIC_CANDIDATE",
        source="Sprint C symbolic constraint informed by artifact missing-item ledger",
        provenance=sources["sources"],
        is_artifact_backed=False,
        is_author_axiom=False,
        is_placeholder=True,
        missing_object="action-derived spinor/vector/tensor contraction and CP transformation law",
        claim_boundary="A scalar wrapper requirement is not a derived Lorentz operator.",
    )
