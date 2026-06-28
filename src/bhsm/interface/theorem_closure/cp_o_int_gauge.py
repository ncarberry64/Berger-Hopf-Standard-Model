"""Gauge and sector factor for the symbolic CP O_int construction."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .cp_o_int_field_action import load_cp_symbolic_sources


@dataclass(frozen=True)
class CPOIntGaugeFactor:
    expression: str
    gauge_representation: str
    allowed_sectors: tuple[str, ...]
    forbidden_leakage: tuple[str, ...]
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


def build_gauge_factor(repository: str | Path | None = None) -> CPOIntGaugeFactor:
    sources = load_cp_symbolic_sources(repository)
    return CPOIntGaugeFactor(
        expression="P_CP_admissible O_int P_CP_admissible",
        gauge_representation="unspecified; gauge-neutral/admissible projection required",
        allowed_sectors=("CP boundary/interface candidate only",),
        forbidden_leakage=("X_ch closure", "neutrino physical mass closure"),
        status="AVAILABLE_SYMBOLIC_CANDIDATE",
        source="Sprint C symbolic admissibility constraint",
        provenance=sources["sources"],
        is_artifact_backed=False,
        is_author_axiom=False,
        is_placeholder=True,
        missing_object="action-derived gauge representation, sector projectors, and forbidden-channel proof",
        claim_boundary="The symbolic projector does not close X_ch or the neutrino theorem.",
    )
