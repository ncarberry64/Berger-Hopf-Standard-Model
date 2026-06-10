"""BHSM v2.7 Lichnerowicz bundle-curvature remainder inventory.

This module does not prove a new geometric theorem. It records the exact
bundle-curvature remainder that blocks complete-operator identification until
its formula/action is derived or bounded in the complete operator.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


REMAINDER_TERM_ID = "lichnerowicz_bundle_curvature_remainder"


@dataclass(frozen=True)
class LichnerowiczRemainderTerm:
    term_id: str
    formula_symbol: str
    geometric_origin: str
    connection_source: str
    sector_action: str
    chirality_action: str
    couples_sectors: str
    creates_mirror_leakage: str
    acts_on_formal_kernel: str
    acts_on_h_perp: str
    current_status: str
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class LichnerowiczBundleCurvatureReport:
    title: str
    structure: str
    remainder: LichnerowiczRemainderTerm
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_lichnerowicz_bundle_curvature_report() -> LichnerowiczBundleCurvatureReport:
    """Return the v2.7 inventory of the Lichnerowicz-type remainder."""

    remainder = LichnerowiczRemainderTerm(
        term_id=REMAINDER_TERM_ID,
        formula_symbol="R_bundle = c(F_BH) + possible mixed bundle-curvature contractions",
        geometric_origin="Lichnerowicz/Weitzenbock squaring of the complete Berger-Hopf twisted Dirac/bundle operator",
        connection_source="Hopf, Higgs-selected U1, base, weak/chirality, coframe, and sector-boundary bundle connections",
        sector_action="not explicitly derived; may be sector-diagonal or sector-coupled depending on the complete connection curvature",
        chirality_action="not explicitly derived; may preserve or mix chiral blocks until the full curvature contraction is specified",
        couples_sectors="OPEN",
        creates_mirror_leakage="OPEN",
        acts_on_formal_kernel="OPEN",
        acts_on_h_perp="OPEN",
        current_status="FORMULA_AND_ACTION_NOT_DERIVED",
        limitations=(
            "No explicit complete-connection curvature formula is available in the repository.",
            "Without that formula, the remainder cannot honestly be declared zero, represented, PSD, screened, or relatively bounded.",
        ),
    )
    return LichnerowiczBundleCurvatureReport(
        title="BHSM v2.7 Lichnerowicz Bundle-Curvature Report",
        structure="D_BH^2 = nabla_BH^* nabla_BH + scalar/curvature terms + bundle curvature terms",
        remainder=remainder,
        theorem_complete=False,
        limitations=(
            "The report identifies the missing term but does not close it.",
            "The complete operator theorem remains blocked unless this term is resolved by a separate proof.",
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


def export_lichnerowicz_bundle_curvature_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_lichnerowicz_bundle_curvature_report()), indent=2, sort_keys=True) + "\n")


def export_lichnerowicz_bundle_curvature_markdown(path: str | Path) -> None:
    report = build_lichnerowicz_bundle_curvature_report()
    row = report.remainder
    lines = [
        "# BHSM v2.7 Lichnerowicz Bundle-Curvature Report",
        "",
        f"Structure: `{report.structure}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| term id | `{row.term_id}` |",
        f"| formula symbol | `{row.formula_symbol}` |",
        f"| geometric origin | {row.geometric_origin} |",
        f"| connection source | {row.connection_source} |",
        f"| sector action | {row.sector_action} |",
        f"| chirality action | {row.chirality_action} |",
        f"| couples sectors | `{row.couples_sectors}` |",
        f"| creates mirror leakage | `{row.creates_mirror_leakage}` |",
        f"| acts on formal kernel | `{row.acts_on_formal_kernel}` |",
        f"| acts on H_perp | `{row.acts_on_h_perp}` |",
        f"| current status | `{row.current_status}` |",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.extend(f"- {item}" for item in row.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
