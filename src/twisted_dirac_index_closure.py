"""BHSM v2.3 twisted Dirac index closure scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from index_sector_count import SECTOR_COUNT_PROVEN, build_sector_count_report
from topological_index_operator import INDEX_THEOREM_CONDITIONAL, build_topological_index_operator_report


INDEX_THEOREM_PROVEN = "INDEX_THEOREM_PROVEN"
INDEX_THEOREM_CANDIDATE = "INDEX_THEOREM_CANDIDATE"
INDEX_THEOREM_CONDITIONAL = "INDEX_THEOREM_CONDITIONAL"
INDEX_THEOREM_OPEN = "INDEX_THEOREM_OPEN"
FAILS_INDEX_THEOREM = "FAILS_INDEX_THEOREM"


@dataclass(frozen=True)
class TwistedDiracIndexClosureReport:
    title: str
    topological_index_status: str
    sector_count_status: str
    target_index: int
    visible_kernel_count: int
    exactly_one_each_sector: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_twisted_dirac_index_closure_report() -> TwistedDiracIndexClosureReport:
    topo = build_topological_index_operator_report()
    sector = build_sector_count_report()
    ok = topo.status == INDEX_THEOREM_CONDITIONAL and sector.status == SECTOR_COUNT_PROVEN
    return TwistedDiracIndexClosureReport(
        title="BHSM v2.3 Twisted Dirac Index Closure Report",
        topological_index_status=topo.status,
        sector_count_status=sector.status,
        target_index=topo.target_index,
        visible_kernel_count=topo.visible_kernel_dimension,
        exactly_one_each_sector=sector.one_each_lepton_up_down,
        status=INDEX_THEOREM_CONDITIONAL if ok else INDEX_THEOREM_OPEN,
        theorem_complete=False,
        open_obligations=topo.open_obligations,
        limitations=(
            "The index closure is conditional because the complete topological index density/operator calculation remains open.",
            "The visible formal sector count is verified and excludes coordinate-first artifacts.",
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


def export_twisted_dirac_index_closure_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_twisted_dirac_index_closure_report()), indent=2, sort_keys=True) + "\n")


def export_twisted_dirac_index_closure_markdown(path: str | Path) -> None:
    report = build_twisted_dirac_index_closure_report()
    lines = [
        "# BHSM v2.3 Twisted Dirac Index Closure Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Dependency | Status/Value |",
        "| --- | --- |",
        f"| topological index | `{report.topological_index_status}` |",
        f"| sector count | `{report.sector_count_status}` |",
        f"| target index | `{report.target_index}` |",
        f"| visible kernel count | `{report.visible_kernel_count}` |",
        f"| exactly one each sector | `{report.exactly_one_each_sector}` |",
        "",
        "## Open Obligations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
