"""Representation-normalization diagnostics for BHSM flavor ratios.

This module evaluates possible representation factors without adopting them.
No canonical geometry, overlap width, mode ledger, or model ratio is changed.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import log10, sqrt
from pathlib import Path
from typing import Any, Iterable, Mapping

from constants import ALPHA_INV_LOW_ENERGY, MODE_LEDGER
from quark_running import MZ, compare_bhsm_to_threshold_common_scale


DIAGNOSTIC_ONLY = "DIAGNOSTIC_ONLY"
ACTION_LINKED = "ACTION_LINKED"
ADOPTED_CANONICAL = "ADOPTED_CANONICAL"
REJECTED = "REJECTED"


@dataclass(frozen=True)
class RepresentationNormalization:
    """One possible representation-normalization factor."""

    sector: str
    mode: tuple[int, int] | str
    factor: float
    source_rule: str
    status: str
    applies_to: str
    notes: tuple[str, ...]


def candidate_normalization_factors() -> tuple[RepresentationNormalization, ...]:
    """Return diagnostic-only candidate factors from simple representation rules."""

    alpha = 1.0 / ALPHA_INV_LOW_ENERGY
    return (
        RepresentationNormalization(
            "all",
            "all",
            1.0,
            "NONE",
            DIAGNOSTIC_ONLY,
            "all_modes",
            ("Null factor; included as control.",),
        ),
        RepresentationNormalization(
            "up_quarks",
            (6, 0),
            0.5,
            "WEAK_DOUBLE_PROJECTION",
            DIAGNOSTIC_ONLY,
            "pure_fiber_up_nonzero_j0",
            ("Possible probability-level projection from two weak components onto one upper component.",),
        ),
        RepresentationNormalization(
            "up_quarks",
            (6, 0),
            1.0 / sqrt(2.0),
            "AMPLITUDE_PROJECTION",
            DIAGNOSTIC_ONLY,
            "pure_fiber_up_nonzero_j0",
            ("Possible amplitude-level projection from a weak doublet.",),
        ),
        RepresentationNormalization(
            "quarks",
            "all",
            1.0 / 3.0,
            "COFRAME_AVERAGE",
            DIAGNOSTIC_ONLY,
            "all_quark_modes",
            ("Triplet coframe average candidate.",),
        ),
        RepresentationNormalization(
            "quarks",
            "all",
            1.0 / sqrt(3.0),
            "COFRAME_AMPLITUDE",
            DIAGNOSTIC_ONLY,
            "all_quark_modes",
            ("Triplet coframe amplitude candidate.",),
        ),
        RepresentationNormalization(
            "all",
            "all_nonzero",
            sqrt(alpha),
            "ALPHA_SUPPRESSED",
            DIAGNOSTIC_ONLY,
            "all_nonzero_modes",
            ("Fine-structure amplitude suppression candidate.",),
        ),
        RepresentationNormalization(
            "all",
            "all_nonzero",
            2.0 * sqrt(alpha),
            "ALPHA_SUPPRESSED",
            DIAGNOSTIC_ONLY,
            "all_nonzero_modes",
            ("Twice fine-structure amplitude suppression candidate.",),
        ),
    )


def normalization_from_representation(
    sector: str,
    mode: tuple[int, int],
    boundary_data: Mapping[str, Any],
    phase_data: Mapping[str, Any],
) -> RepresentationNormalization:
    """Return a diagnostic normalization from supplied representation labels."""

    source_rule = str(boundary_data.get("source_rule", phase_data.get("source_rule", "NONE")))
    applies_to = str(boundary_data.get("applies_to", phase_data.get("applies_to", "no_modes")))
    factors = {row.source_rule: row.factor for row in candidate_normalization_factors()}
    factor = float(factors.get(source_rule, 1.0))
    status = DIAGNOSTIC_ONLY if source_rule in factors else REJECTED
    return RepresentationNormalization(
        sector=sector,
        mode=mode,
        factor=factor,
        source_rule=source_rule,
        status=status,
        applies_to=applies_to,
        notes=(
            "Constructed from supplied representation labels only.",
            "Not adopted unless independently derived from action-level rules.",
        ),
    )


def _rank_for_mode(sector: str, mode: tuple[int, int]) -> str | None:
    for rank, candidate in MODE_LEDGER[sector].items():
        if tuple(candidate) == tuple(mode):
            return rank
    return None


def _mode_for_rank(sector: str, rank: str) -> tuple[int, int]:
    return tuple(MODE_LEDGER[sector][rank])


def _rule_applies(rule: RepresentationNormalization, sector: str, rank: str) -> bool:
    mode = _mode_for_rank(sector, rank)
    k, j = mode
    if rank == "heavy":
        return False
    if rule.applies_to == "all_modes":
        return True
    if rule.applies_to == "all_nonzero_modes":
        return True
    if rule.applies_to == "all_up_sector_modes":
        return sector == "up_quarks"
    if rule.applies_to == "pure_fiber_up_nonzero_j0":
        return sector == "up_quarks" and j == 0 and mode != (0, 0)
    if rule.applies_to == "middle_up_mode_only":
        return sector == "up_quarks" and mode == (6, 0)
    if rule.applies_to == "all_quark_modes":
        return sector in {"up_quarks", "down_quarks"}
    if rule.applies_to == "no_modes":
        return False
    return False


def apply_normalization_to_ratios(
    ratios: Mapping[str, Mapping[str, float]],
    normalization_rules: Iterable[RepresentationNormalization],
) -> dict[str, dict[str, float]]:
    """Apply diagnostic normalization rules to a copy of ratio outputs."""

    normalized = {
        sector: dict(rows)
        for sector, rows in ratios.items()
    }
    for rule in normalization_rules:
        if rule.status == ADOPTED_CANONICAL:
            raise ValueError("canonical adoption is not allowed in the diagnostic audit")
        for sector, rows in normalized.items():
            for rank in rows:
                if _rule_applies(rule, sector, rank):
                    rows[rank] = float(rows[rank]) * float(rule.factor)
    return normalized


def _relative_error(predicted: float, reference: float) -> float:
    return abs(float(predicted) - float(reference)) / abs(float(reference))


def _log_error(predicted: float, reference: float) -> float | None:
    if predicted <= 0 or reference <= 0:
        return None
    return log10(float(predicted) / float(reference))


def _threshold_reference_by_id(model: Any, target_scale: float = MZ) -> dict[str, float]:
    return {
        row["id"]: float(row["reference"])
        for row in compare_bhsm_to_threshold_common_scale(model, target_scale)
    }


def compare_normalized_ratios(
    model: Any,
    normalization_rules: Iterable[RepresentationNormalization],
    target_scale: float = MZ,
) -> dict[str, object]:
    """Compare diagnostic normalized ratios to threshold-aware references."""

    base = {
        sector: dict(yukawa.ratios)
        for sector, yukawa in model.yukawa_sectors.items()
    }
    normalized = apply_normalization_to_ratios(base, normalization_rules)
    refs = _threshold_reference_by_id(model, target_scale)
    rows = []
    for row_id, sector, rank in (
        ("mass_ratio.up_quarks.middle", "up_quarks", "middle"),
        ("mass_ratio.up_quarks.light", "up_quarks", "light"),
        ("mass_ratio.down_quarks.middle", "down_quarks", "middle"),
        ("mass_ratio.down_quarks.light", "down_quarks", "light"),
    ):
        predicted = float(normalized[sector][rank])
        reference = refs[row_id]
        rows.append(
            {
                "id": row_id,
                "predicted": predicted,
                "reference": reference,
                "relative_error": _relative_error(predicted, reference),
                "log_error": _log_error(predicted, reference),
            }
        )
    sin13 = sqrt(float(normalized["up_quarks"]["light"]))
    return {
        "rules": [asdict(rule) for rule in normalization_rules],
        "ratios": normalized,
        "comparisons": rows,
        "ckm": {
            "sin_theta_13": sin13,
            "status": "DIAGNOSTIC_ONLY",
            "note": "Computed from normalized u/t only for diagnostic scope testing.",
        },
        "target_scale": target_scale,
        "adopted": False,
    }


def _scope_rule(factor: float, applies_to: str) -> RepresentationNormalization:
    return RepresentationNormalization(
        sector="diagnostic",
        mode="scope_test",
        factor=factor,
        source_rule="WEAK_DOUBLE_PROJECTION_SCOPE_TEST",
        status=DIAGNOSTIC_ONLY,
        applies_to=applies_to,
        notes=("Scope diagnostic only; not action-linked or adopted.",),
    )


def up_sector_normalization_diagnostic(model: Any, target_scale: float = MZ) -> dict[str, object]:
    """Return the up-sector representation-normalization diagnostic."""

    ratios = {
        sector: dict(yukawa.ratios)
        for sector, yukawa in model.yukawa_sectors.items()
    }
    refs = _threshold_reference_by_id(model, target_scale)
    c_pred = float(ratios["up_quarks"]["middle"])
    c_ref = refs["mass_ratio.up_quarks.middle"]
    required = c_ref / c_pred
    candidates = []
    for rule in candidate_normalization_factors():
        comparison = compare_normalized_ratios(model, (rule,), target_scale)
        ct = next(row for row in comparison["comparisons"] if row["id"] == "mass_ratio.up_quarks.middle")
        ut = next(row for row in comparison["comparisons"] if row["id"] == "mass_ratio.up_quarks.light")
        candidates.append(
            {
                "source_rule": rule.source_rule,
                "factor": rule.factor,
                "status": rule.status,
                "applies_to": rule.applies_to,
                "c_over_t": ct["predicted"],
                "c_over_t_relative_error": ct["relative_error"],
                "u_over_t": ut["predicted"],
                "sin_theta_13": comparison["ckm"]["sin_theta_13"],
                "distance_to_required_factor": abs(rule.factor - required),
                "adopted": False,
            }
        )
    scope_rows = []
    for scope in ("middle_up_mode_only", "pure_fiber_up_nonzero_j0", "all_up_sector_modes", "all_quark_modes", "no_modes"):
        comparison = compare_normalized_ratios(model, (_scope_rule(0.5, scope),), target_scale)
        ct = next(row for row in comparison["comparisons"] if row["id"] == "mass_ratio.up_quarks.middle")
        ut = next(row for row in comparison["comparisons"] if row["id"] == "mass_ratio.up_quarks.light")
        sb = next(row for row in comparison["comparisons"] if row["id"] == "mass_ratio.down_quarks.middle")
        scope_rows.append(
            {
                "scope": scope,
                "factor": 0.5,
                "c_over_t": ct["predicted"],
                "c_over_t_relative_error": ct["relative_error"],
                "u_over_t": ut["predicted"],
                "u_over_t_relative_error": ut["relative_error"],
                "s_over_b": sb["predicted"],
                "sin_theta_13": comparison["ckm"]["sin_theta_13"],
                "status": DIAGNOSTIC_ONLY,
                "adopted": False,
            }
        )
    return {
        "canonical_geometry": {
            "name": model.geometry_config.name,
            "a": model.geometry_config.a,
        },
        "base_ratios": ratios,
        "threshold_references": refs,
        "required_factor": required,
        "candidate_factors": candidates,
        "scope_diagnostics": scope_rows,
        "status_counts": {
            DIAGNOSTIC_ONLY: len(candidate_normalization_factors()) + len(scope_rows),
            ACTION_LINKED: 0,
            ADOPTED_CANONICAL: 0,
            REJECTED: 0,
        },
        "conclusion": (
            "The 1/2 factor is numerically suggestive for c/t but remains "
            "DIAGNOSTIC_ONLY. No implemented representation rule independently "
            "forces adoption."
        ),
        "limitations": (
            "No empirical residual is used to select or adopt a factor.",
            "No canonical ratio, geometry, S, or mode ledger is changed.",
            "Action-level derivation of any representation normalization remains open.",
        ),
    }


def _jsonable(value: object) -> object:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def export_representation_normalization_json(model: Any, path: str | Path) -> None:
    """Export the representation-normalization audit as JSON."""

    Path(path).write_text(json.dumps(_jsonable(up_sector_normalization_diagnostic(model)), indent=2, sort_keys=True) + "\n")


def export_representation_normalization_markdown(model: Any, path: str | Path) -> None:
    """Export the representation-normalization audit as Markdown."""

    report = up_sector_normalization_diagnostic(model)
    lines = [
        "# BHSM Representation-Normalization Audit",
        "",
        "This audit evaluates candidate factors without tuning or adoption.",
        "",
        f"Required factor for threshold-aware c/t: `{report['required_factor']}`",
        "",
        "## Candidate Factors",
        "",
        "| Source Rule | Factor | Applies To | c/t | c/t Relative Error | u/t | sin(theta_13) | Status | Adopted |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report["candidate_factors"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                row["source_rule"],
                row["factor"],
                row["applies_to"],
                row["c_over_t"],
                row["c_over_t_relative_error"],
                row["u_over_t"],
                row["sin_theta_13"],
                row["status"],
                row["adopted"],
            )
        )
    lines.extend([
        "",
        "## Scope Diagnostics for Factor 1/2",
        "",
        "| Scope | c/t | c/t Relative Error | u/t | u/t Relative Error | sin(theta_13) | Adopted |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ])
    for row in report["scope_diagnostics"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                row["scope"],
                row["c_over_t"],
                row["c_over_t_relative_error"],
                row["u_over_t"],
                row["u_over_t_relative_error"],
                row["sin_theta_13"],
                row["adopted"],
            )
        )
    lines.extend(["", "## Conclusion", "", report["conclusion"], "", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.append("")
    Path(path).write_text("\n".join(lines))
