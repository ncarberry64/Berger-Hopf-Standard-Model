"""BHSM v1.3G index-theorem facade for the zero-mode/complement split."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from complement_projector import ComplementProjectorReport, build_complement_projector_report
from zero_mode_index import ZeroModeSplitReport, build_zero_mode_split_report


@dataclass(frozen=True)
class IndexTheoremScaffoldReport:
    """Combined v1.3G zero-mode and complement-split scaffold."""

    title: str
    decomposition: str
    target_kernel_dimension: int
    target_index: int
    zero_mode_report: ZeroModeSplitReport
    complement_projector_report: ComplementProjectorReport
    scaffold_status: str
    theorem_complete: bool
    proven_implications: tuple[str, ...]
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_index_theorem_scaffold_report() -> IndexTheoremScaffoldReport:
    """Return the combined zero-mode/complement-split scaffold report."""

    zero_report = build_zero_mode_split_report()
    projector_report = build_complement_projector_report()
    return IndexTheoremScaffoldReport(
        title="BHSM v1.3G Zero-Mode and Complement-Split Scaffold",
        decomposition="H = ker(D_twist) direct_sum H_perp",
        target_kernel_dimension=zero_report.target_kernel_dimension,
        target_index=zero_report.target_index,
        zero_mode_report=zero_report,
        complement_projector_report=projector_report,
        scaffold_status="INDEX_AND_COMPLEMENT_SCAFFOLD",
        theorem_complete=False,
        proven_implications=(
            "The finite Level 2 protected coordinate projector is idempotent.",
            "The finite Level 2 sector-coupling block vanishes on the protected coordinate block.",
            "The finite heat-lift leaves zero Dirac-squared modes at zero.",
        ),
        open_obligations=(
            "Derive Index(D_twist)=3 from the twisted bundle topology.",
            "Exclude opposite-chirality mirror zero modes from the complete operator.",
            "Identify the formal sector-labeled kernel with the full operator kernel.",
            "Prove the complement projector is well-defined and compatible in the infinite Hilbert space.",
        ),
        limitations=(
            "This scaffold does not prove the full index theorem.",
            "It does not compute the full H_T spectrum.",
            "It does not change frozen BHSM predictions.",
        ),
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def export_index_theorem_scaffold_json(path: str | Path) -> None:
    """Export the combined scaffold as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_index_theorem_scaffold_report()), indent=2, sort_keys=True) + "\n")


def export_index_theorem_scaffold_markdown(path: str | Path) -> None:
    """Export the combined scaffold as Markdown."""

    report = build_index_theorem_scaffold_report()
    lines = [
        "# BHSM v1.3G Zero-Mode and Complement-Split Scaffold",
        "",
        f"Status: `{report.scaffold_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Decomposition target: `{report.decomposition}`",
        f"Target kernel dimension: `{report.target_kernel_dimension}`",
        f"Target index: `{report.target_index}`",
        "",
        "## Proven Finite-Scaffold Implications",
        "",
        *[f"- {item}" for item in report.proven_implications],
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
