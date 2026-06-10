"""Topological index theorem completion wrapper.

This module reuses the existing zero-mode/index audits and records whether the
full topological theorem is actually closed. It does not invent a topological
proof beyond the checked scaffold.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from twisted_dirac_index_audit import TwistedDiracIndexAudit, build_twisted_dirac_index_audit


INDEX_THEOREM_PROVEN = "INDEX_THEOREM_PROVEN"
INDEX_THEOREM_CANDIDATE = "INDEX_THEOREM_CANDIDATE"
INDEX_THEOREM_OPEN = "INDEX_THEOREM_OPEN"
FAILS_INDEX_OR_MIRROR = "FAILS_INDEX_OR_MIRROR"


@dataclass(frozen=True)
class TwistedDiracIndexTheoremReport:
    """Topological index theorem status."""

    title: str
    audit: TwistedDiracIndexAudit
    target_index: int
    target_kernel_dimension: int
    visible_kernel_states: int
    connects_to_sectors: tuple[str, ...]
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_twisted_dirac_index_theorem_report() -> TwistedDiracIndexTheoremReport:
    """Build the conservative index theorem report."""

    audit = build_twisted_dirac_index_audit()
    sectors = tuple(candidate.sector for candidate in audit.zero_mode_report.candidates)
    hard_failure = audit.target_index != audit.finite_scaffold_index
    theorem_complete = False
    status = FAILS_INDEX_OR_MIRROR if hard_failure else INDEX_THEOREM_OPEN
    return TwistedDiracIndexTheoremReport(
        title="BHSM Twisted Dirac Topological Index Theorem Attempt",
        audit=audit,
        target_index=3,
        target_kernel_dimension=3,
        visible_kernel_states=audit.target_kernel_dimension,
        connects_to_sectors=sectors,
        status=status,
        theorem_complete=theorem_complete,
        open_obligations=(
            "derive the topological index of the complete twisted Dirac operator",
            "prove absence of additional protected kernel states in the complete operator",
            "prove the formal-kernel/complement split independently of finite truncation",
        ),
        limitations=(
            "The current index equals 3 in the scaffold but is not a full topological theorem.",
            "No empirical masses, CKM values, or residuals enter this report.",
        ),
    )


def _jsonable(value: object) -> object:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def export_twisted_dirac_index_theorem_json(path: str | Path) -> None:
    """Export the index theorem report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_twisted_dirac_index_theorem_report()), indent=2, sort_keys=True) + "\n")


def export_twisted_dirac_index_theorem_markdown(path: str | Path) -> None:
    """Export the index theorem report as Markdown."""

    report = build_twisted_dirac_index_theorem_report()
    lines = [
        "# BHSM Twisted Dirac Topological Index Theorem Attempt",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "## Index Summary",
        "",
        f"- Target index: `{report.target_index}`",
        f"- Target kernel dimension: `{report.target_kernel_dimension}`",
        f"- Scaffold visible kernel states: `{report.visible_kernel_states}`",
        f"- Sector labels: `{report.connects_to_sectors}`",
        "",
        "## Open Obligations",
        "",
        *[f"- {item}" for item in report.open_obligations],
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in report.limitations],
        "",
    ]
    Path(path).write_text("\n".join(lines))

