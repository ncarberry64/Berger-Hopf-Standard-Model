"""BHSM v2.3 sector-count audit for the formal kernel."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from formal_kernel_projector import DEFAULT_FORMAL_COORDINATES, OLD_COORDINATE_FIRST_KERNEL, build_formal_kernel_projector_report


SECTOR_COUNT_PROVEN = "SECTOR_COUNT_PROVEN"
SECTOR_COUNT_CONDITIONAL = "SECTOR_COUNT_CONDITIONAL"
SECTOR_COUNT_OPEN = "SECTOR_COUNT_OPEN"
FAILS_SECTOR_COUNT = "FAILS_SECTOR_COUNT"


@dataclass(frozen=True)
class SectorCountRow:
    sector: str
    protected_count: int
    coordinate_hint_kmax4: int
    status: str
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class SectorCountReport:
    title: str
    rows: tuple[SectorCountRow, ...]
    total_visible_protected_states: int
    one_each_lepton_up_down: bool
    duplicate_lepton_coordinate_artifact: bool
    missing_up_down_state: bool
    extra_visible_protected_state: bool
    old_coordinate_first_kernel_used: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_sector_count_report() -> SectorCountReport:
    kernel = build_formal_kernel_projector_report()
    counts: dict[str, int] = {}
    coords: dict[str, int] = {}
    for row in kernel.kernel_basis:
        counts[row.sector] = counts.get(row.sector, 0) + 1
        coords[row.sector] = row.coordinate_hint_kmax4
    rows = tuple(
        SectorCountRow(
            sector=sector,
            protected_count=counts.get(sector, 0),
            coordinate_hint_kmax4=coords.get(sector, -1),
            status="SECTOR_PRESENT_ONCE" if counts.get(sector, 0) == 1 else "SECTOR_COUNT_FAIL",
            limitations=("Sector count is for the formal visible kernel; topological uniqueness remains separate.",),
        )
        for sector in ("lepton", "up", "down")
    )
    one_each = all(row.protected_count == 1 for row in rows)
    total = sum(row.protected_count for row in rows)
    duplicate_lepton = tuple(row.coordinate_hint_kmax4 for row in rows) == OLD_COORDINATE_FIRST_KERNEL
    missing = any(row.protected_count == 0 for row in rows)
    extra = total != 3
    status = SECTOR_COUNT_PROVEN if one_each and not duplicate_lepton and not missing and not extra else FAILS_SECTOR_COUNT
    return SectorCountReport(
        title="BHSM v2.3 Sector Count Report",
        rows=rows,
        total_visible_protected_states=total,
        one_each_lepton_up_down=one_each,
        duplicate_lepton_coordinate_artifact=duplicate_lepton,
        missing_up_down_state=missing,
        extra_visible_protected_state=extra,
        old_coordinate_first_kernel_used=False,
        status=status,
        theorem_complete=False,
        limitations=(
            f"The corrected k_max=4 coordinate hints are {DEFAULT_FORMAL_COORDINATES}, not {OLD_COORDINATE_FIRST_KERNEL}.",
            "This proves the visible formal sector count, not the full topological index theorem.",
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


def export_sector_count_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_sector_count_report()), indent=2, sort_keys=True) + "\n")


def export_sector_count_markdown(path: str | Path) -> None:
    report = build_sector_count_report()
    lines = [
        "# BHSM v2.3 Sector Count Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Old coordinate-first kernel used: `{report.old_coordinate_first_kernel_used}`",
        "",
        "| Sector | Count | k_max=4 coordinate hint | Status |",
        "| --- | --- | --- | --- |",
    ]
    for row in report.rows:
        lines.append(f"| `{row.sector}` | `{row.protected_count}` | `{row.coordinate_hint_kmax4}` | `{row.status}` |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
