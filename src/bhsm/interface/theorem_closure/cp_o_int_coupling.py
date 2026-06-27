"""Coupling and mass-dimension factor for symbolic CP O_int."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .cp_o_int_field_action import load_cp_symbolic_sources


@dataclass(frozen=True)
class CPOIntCouplingFactor:
    symbol: str
    normalization: str
    operator_mass_dimension: str
    coupling_mass_dimension: str
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


def build_coupling_factor(repository: str | Path | None = None) -> CPOIntCouplingFactor:
    sources = load_cp_symbolic_sources(repository)
    row = sources["ledger_term"]
    symbol = "G_raw" if "G_raw" in str(row.get("symbolic_expression", "")) else "g_CP"
    return CPOIntCouplingFactor(
        symbol=symbol,
        normalization="unspecified symbolic coefficient",
        operator_mass_dimension="not derived",
        coupling_mass_dimension="must make the action density dimension four; value not derived",
        status="AVAILABLE_SYMBOLIC_CANDIDATE",
        source="existing symbolic 4D assembly ledger coefficient symbol",
        provenance=sources["sources"],
        is_artifact_backed=bool(row),
        is_author_axiom=False,
        is_placeholder=True,
        missing_object="normalized coupling and operator/coupling mass dimensions from the action",
        claim_boundary="No W anchor, PDG value, or calibration fixes the symbolic coefficient.",
    )
