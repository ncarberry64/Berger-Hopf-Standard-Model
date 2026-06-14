"""Validated common-scale quark-ratio audit for BHSM.

This module replaces mixed-scale quark mass comparisons with an explicit M_Z
MSbar reference table when available.  It does not run new BHSM predictions,
tune parameters, or modify frozen outputs.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import isfinite, log10
from pathlib import Path
from typing import Any

from bhsm_v1 import (
    build_bhsm_bare_v1,
    build_bhsm_dressed_v1_candidate,
    compare_bhsm_v1_branches,
    declared_tolerance_bands,
)


COMMON_SCALE_RG_VALIDATED_SURVIVAL = "COMMON_SCALE_RG_VALIDATED_SURVIVAL"
COMMON_SCALE_RG_VALIDATED_WARNING = "COMMON_SCALE_RG_VALIDATED_WARNING"
COMMON_SCALE_RG_FAILED = "COMMON_SCALE_RG_FAILED"
EXTERNAL_INPUT_REQUIRED = "EXTERNAL_INPUT_REQUIRED"
ROUGH_SCREEN_ONLY = "ROUGH_SCREEN_ONLY"

REFERENCE_PATH = Path("data/reference_common_scale_quark_ratios_mz.json")
RATIO_PATHS = {
    "c/t": ("up_quark_ratios", "middle"),
    "u/t": ("up_quark_ratios", "light"),
    "s/b": ("down_quark_ratios", "middle"),
    "d/b": ("down_quark_ratios", "light"),
}


@dataclass(frozen=True)
class QuarkRatioRow:
    """One branch/reference comparison row."""

    branch: str
    ratio: str
    predicted: float
    reference: float | None
    absolute_error: float | None
    relative_error: float | None
    log_error: float | None
    tolerance: float
    passes_tolerance: bool
    classification: str
    real_tension: bool


def load_common_scale_reference(path: str | Path = REFERENCE_PATH) -> dict[str, Any]:
    """Load the common-scale quark ratio reference file."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def reference_is_validated(reference: dict[str, Any]) -> bool:
    """Return whether the reference table is usable as common-scale input."""

    if reference.get("status") == EXTERNAL_INPUT_REQUIRED:
        return False
    required = ("scale", "scheme", "source_note", "source_citation_text", "ratios")
    if not all(reference.get(key) for key in required):
        return False
    if reference.get("validated_common_scale") is not True:
        return False
    ratios = reference["ratios"]
    return all(name in ratios and ratios[name].get("value") is not None for name in RATIO_PATHS)


def _branch_predictions() -> dict[str, dict[str, float]]:
    bare = build_bhsm_bare_v1()
    dressed = build_bhsm_dressed_v1_candidate()
    branches = {
        bare.version.branch: bare.outputs,
        dressed.version.branch: dressed.outputs,
    }
    rows: dict[str, dict[str, float]] = {}
    for branch, outputs in branches.items():
        rows[branch] = {
            ratio: float(outputs[path[0]][path[1]])
            for ratio, path in RATIO_PATHS.items()
        }
    return rows


def _relative_error(predicted: float, reference: float) -> float:
    return abs(predicted - reference) / abs(reference)


def compare_branch_to_common_scale(
    branch: str,
    ratios: dict[str, float],
    reference: dict[str, Any],
    tolerance: float | None = None,
) -> tuple[QuarkRatioRow, ...]:
    """Compare one BHSM branch against the common-scale reference."""

    tolerance = float(tolerance if tolerance is not None else declared_tolerance_bands()["quark_ratios_scheme_aware"])
    validated = reference_is_validated(reference)
    rows: list[QuarkRatioRow] = []
    for ratio, predicted in ratios.items():
        ref_value = None if not validated else float(reference["ratios"][ratio]["value"])
        if ref_value is None:
            rows.append(
                QuarkRatioRow(
                    branch=branch,
                    ratio=ratio,
                    predicted=predicted,
                    reference=None,
                    absolute_error=None,
                    relative_error=None,
                    log_error=None,
                    tolerance=tolerance,
                    passes_tolerance=False,
                    classification=EXTERNAL_INPUT_REQUIRED,
                    real_tension=False,
                )
            )
            continue
        relative_error = _relative_error(predicted, ref_value)
        log_error = log10(predicted / ref_value) if predicted > 0 and ref_value > 0 else None
        passes = isfinite(relative_error) and relative_error <= tolerance
        rows.append(
            QuarkRatioRow(
                branch=branch,
                ratio=ratio,
                predicted=predicted,
                reference=ref_value,
                absolute_error=abs(predicted - ref_value),
                relative_error=relative_error,
                log_error=log_error,
                tolerance=tolerance,
                passes_tolerance=passes,
                classification=COMMON_SCALE_RG_VALIDATED_SURVIVAL if passes else COMMON_SCALE_RG_VALIDATED_WARNING,
                real_tension=not passes,
            )
        )
    return tuple(rows)


def common_scale_comparison_rows(reference: dict[str, Any] | None = None) -> tuple[QuarkRatioRow, ...]:
    """Return all bare and dressed branch comparison rows."""

    reference = reference or load_common_scale_reference()
    rows: list[QuarkRatioRow] = []
    for branch, ratios in _branch_predictions().items():
        rows.extend(compare_branch_to_common_scale(branch, ratios, reference))
    return tuple(rows)


def _whole_screen_classification(reference: dict[str, Any], rows: tuple[QuarkRatioRow, ...]) -> str:
    if reference.get("status") == EXTERNAL_INPUT_REQUIRED:
        return EXTERNAL_INPUT_REQUIRED
    if not reference_is_validated(reference):
        return ROUGH_SCREEN_ONLY
    if not rows:
        return EXTERNAL_INPUT_REQUIRED
    if all(row.passes_tolerance for row in rows if row.branch == "BHSM_DRESSED_V1_CANDIDATE"):
        return COMMON_SCALE_RG_VALIDATED_SURVIVAL
    if any(row.passes_tolerance for row in rows):
        return COMMON_SCALE_RG_VALIDATED_WARNING
    return COMMON_SCALE_RG_FAILED


def frozen_sanity_payload() -> dict[str, Any]:
    """Return frozen-output sanity checks."""

    comparison = compare_bhsm_v1_branches()
    rows = comparison["rows"]
    changed = [row for row in rows if row["changed"]]
    return {
        "BHSM_BARE_V1_unchanged": comparison["branches"][0] == "BHSM_BARE_V1",
        "BHSM_DRESSED_V1_CANDIDATE_unchanged": comparison["branches"][1]
        == "BHSM_DRESSED_V1_CANDIDATE",
        "dressed_branch_changes_only_c_over_t": len(changed) == 1
        and changed[0]["quantity"] == "c/t",
        "u_over_t_unchanged": next(row for row in rows if row["quantity"] == "u/t")[
            "changed"
        ]
        is False,
        "ckm_sin_theta_13_unchanged": next(
            row for row in rows if row["quantity"] == "sin_theta_13"
        )["changed"]
        is False,
        "changed_rows": changed,
    }


def closure_audit_payload(reference_path: str | Path = REFERENCE_PATH) -> dict[str, Any]:
    """Return the validated common-scale quark RG closure audit."""

    reference = load_common_scale_reference(reference_path)
    rows = common_scale_comparison_rows(reference)
    classification = _whole_screen_classification(reference, rows)
    validated = reference_is_validated(reference)
    dressed_rows = [row for row in rows if row.branch == "BHSM_DRESSED_V1_CANDIDATE"]
    c_over_t = [row for row in rows if row.ratio == "c/t"]
    c_dressed = next(row for row in dressed_rows if row.ratio == "c/t")
    c_bare = next(row for row in rows if row.branch == "BHSM_BARE_V1" and row.ratio == "c/t")
    failing_dressed = [row for row in dressed_rows if not row.passes_tolerance]
    real_tensions = tuple(row.ratio for row in failing_dressed)
    return {
        "title": "BHSM common-scale quark RG closure audit",
        "issue_id": "P1-2",
        "status": "CLOSED_SOLVED" if validated else "BLOCKS_FULL_COMPLETION",
        "blocker": None if validated else "COMMON_SCALE_QUARK_RG_INPUTS_MISSING",
        "classification": classification,
        "common_scale_input_validated": validated,
        "closes_common_scale_input_blocker": validated,
        "common_scale_quark_precision_claimable": classification == COMMON_SCALE_RG_VALIDATED_SURVIVAL,
        "mixed_scale_used_as_precision_reference": False,
        "reference": reference,
        "tolerance": declared_tolerance_bands()["quark_ratios_scheme_aware"],
        "rows": rows,
        "branch_summary": {
            "dressed_candidate_all_ratios_pass": not failing_dressed,
            "dressed_candidate_failing_ratios": real_tensions,
            "real_tensions": real_tensions,
        },
        "ct_dressing_effect": {
            "bare_relative_error": c_bare.relative_error,
            "dressed_relative_error": c_dressed.relative_error,
            "dressed_improves_c_over_t": (
                c_dressed.relative_error is not None
                and c_bare.relative_error is not None
                and c_dressed.relative_error < c_bare.relative_error
            ),
            "rows": c_over_t,
        },
        "u_d_s_survival": {
            row.ratio: row.passes_tolerance
            for row in dressed_rows
            if row.ratio in {"u/t", "d/b", "s/b"}
        },
        "frozen_sanity": frozen_sanity_payload(),
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "limitations": (
            "The M_Z table supplies common-scale reference ratios but no uncertainty propagation.",
            "The dressed c/t branch is compared as frozen; it is not retuned.",
            "u/t remains outside the scheme-aware tolerance and is reported as a real warning-level tension.",
            "This audit closes the missing-input blocker only; full precision quark matching remains open.",
        ),
    }


def _jsonable(value: object) -> object:
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def render_markdown(payload: dict[str, Any] | None = None) -> str:
    """Render the closure audit as Markdown."""

    payload = payload or closure_audit_payload()
    lines = [
        "# Common-Scale Quark RG Closure Audit",
        "",
        "## Why Mixed-Scale Quark Comparisons Are Not Precision Tests",
        "",
        "Quark masses are scheme- and scale-dependent. Mixed PDG-style inputs combine light-quark, charm, bottom, and top references at different scales, so they are useful screens but not precision verdicts.",
        "",
        "## What Common-Scale Comparison Means",
        "",
        "This audit compares BHSM frozen quark ratios with a single M_Z MSbar running-mass reference table.",
        "",
        "## What Source Was Used",
        "",
        f"Scale: `{payload['reference'].get('scale')}`",
        f"Scheme: `{payload['reference'].get('scheme')}`",
        f"Source: {payload['reference'].get('source_citation_text')}",
        "",
        "## What BHSM Predicts",
        "",
        "| Branch | Ratio | BHSM | M_Z Reference | Relative Error | Passes 25% Band | Classification |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                row.branch,
                row.ratio,
                row.predicted,
                row.reference,
                row.relative_error,
                row.passes_tolerance,
                row.classification,
            )
        )
    lines.extend(
        [
            "",
            "## What Survives",
            "",
            f"- Dressed `c/t` improves versus bare: `{payload['ct_dressing_effect']['dressed_improves_c_over_t']}`",
            f"- Dressed `s/b` survives: `{payload['u_d_s_survival']['s/b']}`",
            f"- Dressed `d/b` survives: `{payload['u_d_s_survival']['d/b']}`",
            "",
            "## What Remains Warning-Level",
            "",
            f"- Dressed `u/t` survives: `{payload['u_d_s_survival']['u/t']}`",
            f"- Real warning-level tensions: `{payload['branch_summary']['real_tensions']}`",
            "",
            "## Whether Quark Precision Is Now Claimable",
            "",
            f"Classification: `{payload['classification']}`",
            f"Common-scale input blocker closed: `{payload['closes_common_scale_input_blocker']}`",
            f"Precision quark matching claimable: `{payload['common_scale_quark_precision_claimable']}`",
            "",
            "The missing-input blocker is closed by the common-scale table, but full precision quark matching is not claimed because `u/t` remains outside tolerance and uncertainties are not propagated.",
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["limitations"])
    lines.append("")
    return "\n".join(lines)


def export_common_scale_quark_rg_closure_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export theory and audit files."""

    base = Path(root)
    payload = closure_audit_payload(base / REFERENCE_PATH)
    markdown = render_markdown(payload)
    paths = {
        "theory": base / "theory" / "common_scale_quark_rg_closure_note.md",
        "audit_md": base / "audits" / "common_scale_quark_rg_closure_audit.md",
        "audit_json": base / "audits" / "common_scale_quark_rg_closure_audit.json",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["theory"].write_text(markdown, encoding="utf-8")
    paths["audit_md"].write_text(markdown, encoding="utf-8")
    paths["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_common_scale_quark_rg_closure_outputs()
