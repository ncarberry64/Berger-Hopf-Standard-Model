"""Scheme ledger for BHSM QCD/RG comparison scaffolds."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from quark_mass_reference_sets import (
    COMMON_SCALE_APPROX,
    MIXED_DEFAULT,
    PRECISION_QCD_PLACEHOLDER,
    THRESHOLD_AWARE_APPROX,
)


@dataclass(frozen=True)
class RGSchemeLedgerEntry:
    """One comparison scheme status row."""

    id: str
    scheme_set: str
    status: str
    scheme_consistent: bool
    final_comparison: bool
    uncertainty_ready: bool
    allowed_use: str
    limitations: tuple[str, ...]


def rg_scheme_ledger() -> tuple[RGSchemeLedgerEntry, ...]:
    """Return the Gate 2 QCD/RG scheme ledger."""

    return (
        RGSchemeLedgerEntry(
            id="RG1",
            scheme_set=MIXED_DEFAULT,
            status="SCHEME_SENSITIVE_BASELINE",
            scheme_consistent=False,
            final_comparison=False,
            uncertainty_ready=False,
            allowed_use="continuity with frozen v1 residuals",
            limitations=("Mixed quark scales/schemes; cannot produce final QCD verdict.",),
        ),
        RGSchemeLedgerEntry(
            id="RG2",
            scheme_set=COMMON_SCALE_APPROX,
            status="APPROXIMATE_RUNNING_SCAFFOLD",
            scheme_consistent=True,
            final_comparison=False,
            uncertainty_ready=False,
            allowed_use="diagnostic common-scale comparison",
            limitations=("Fixed-nf one-loop-inspired running only.",),
        ),
        RGSchemeLedgerEntry(
            id="RG3",
            scheme_set=THRESHOLD_AWARE_APPROX,
            status="THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD",
            scheme_consistent=True,
            final_comparison=False,
            uncertainty_ready=False,
            allowed_use="diagnostic threshold-aware comparison",
            limitations=("Piecewise-nf scaffold; no precision threshold matching.",),
        ),
        RGSchemeLedgerEntry(
            id="RG4",
            scheme_set=PRECISION_QCD_PLACEHOLDER,
            status="PLACEHOLDER_NOT_COMPUTED",
            scheme_consistent=False,
            final_comparison=False,
            uncertainty_ready=False,
            allowed_use="future precision QCD target",
            limitations=("No numerical precision-QCD references are supplied.",),
        ),
    )


def rg_scheme_ledger_asdict() -> list[dict[str, Any]]:
    """Return JSON-ready scheme ledger rows."""

    return [asdict(row) for row in rg_scheme_ledger()]
