"""Diagnostic audit for the common-scale BHSM light-up ratio tension.

The common-scale M_Z quark audit leaves one warning-level dressed-branch row:
u/t.  This module diagnoses that localized tension without changing official
frozen outputs or adopting a new dressing rule.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import isfinite, log10, sqrt
from pathlib import Path
from typing import Any

from bhsm_v1 import build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from common_scale_quark_rg_closure import (
    COMMON_SCALE_RG_VALIDATED_WARNING,
    RATIO_PATHS,
    closure_audit_payload as common_scale_audit_payload,
    load_common_scale_reference,
)
from constants import ALPHA_INV_LOW_ENERGY


U_T_WARNING_CONFIRMED = "U_T_WARNING_CONFIRMED"
U_T_TENSION_EXPLAINED_BY_INPUT_UNCERTAINTY = "U_T_TENSION_EXPLAINED_BY_INPUT_UNCERTAINTY"
LIGHT_UP_DRESSING_CANDIDATE_NOT_OFFICIAL = "LIGHT_UP_DRESSING_CANDIDATE_NOT_OFFICIAL"
U_T_FAILURE_NOT_REPAIRED = "U_T_FAILURE_NOT_REPAIRED"
EXTERNAL_INPUT_REQUIRED = "EXTERNAL_INPUT_REQUIRED"

EXPLORATORY_CANDIDATE = "EXPLORATORY_CANDIDATE"
NO_OFFICIAL_REPAIR = "NO_OFFICIAL_REPAIR"


@dataclass(frozen=True)
class RatioResidual:
    """One common-scale residual row for the dressed branch."""

    ratio: str
    predicted: float
    reference: float
    absolute_error: float
    relative_error: float
    log_error: float
    passes_tolerance: bool


@dataclass(frozen=True)
class CandidateRepair:
    """One exploratory light-up-only candidate factor."""

    name: str
    factor: float
    corrected_u_over_t: float
    relative_error: float
    passes_tolerance: bool
    changes_official_u_over_t: bool
    changes_ckm_sin_theta_13: bool
    status: str
    notes: tuple[str, ...]


@dataclass(frozen=True)
class LightUpTensionResult:
    """Structured diagnostic output for the sprint."""

    classification: str
    u_t_warning_confirmed: bool
    global_rescale_allowed: bool
    candidate_repair_available: bool
    candidate_status: str
    damages_other_ratios: bool
    recommendation: str


def _relative_error(predicted: float, reference: float) -> float:
    return abs(predicted - reference) / abs(reference)


def _dressed_predictions() -> dict[str, float]:
    outputs = build_bhsm_dressed_v1_candidate().outputs
    return {
        ratio: float(outputs[path[0]][path[1]])
        for ratio, path in RATIO_PATHS.items()
    }


def dressed_common_scale_residuals(reference_path: str | Path = "data/reference_common_scale_quark_ratios_mz.json") -> tuple[RatioResidual, ...]:
    """Return dressed-branch common-scale residual rows."""

    reference = load_common_scale_reference(reference_path)
    predictions = _dressed_predictions()
    tolerance = 0.25
    rows: list[RatioResidual] = []
    for ratio, predicted in predictions.items():
        ref_value = float(reference["ratios"][ratio]["value"])
        rel = _relative_error(predicted, ref_value)
        rows.append(
            RatioResidual(
                ratio=ratio,
                predicted=predicted,
                reference=ref_value,
                absolute_error=abs(predicted - ref_value),
                relative_error=rel,
                log_error=log10(predicted / ref_value),
                passes_tolerance=rel <= tolerance,
            )
        )
    return tuple(rows)


def light_up_required_factor(reference_path: str | Path = "data/reference_common_scale_quark_ratios_mz.json") -> float:
    """Return the factor that would map frozen u/t to the M_Z reference."""

    u_row = next(row for row in dressed_common_scale_residuals(reference_path) if row.ratio == "u/t")
    return u_row.reference / u_row.predicted


def global_rescale_diagnostic(reference_path: str | Path = "data/reference_common_scale_quark_ratios_mz.json") -> dict[str, Any]:
    """Test whether a single global quark-ratio rescale can repair u/t safely."""

    factor = light_up_required_factor(reference_path)
    rows = []
    for row in dressed_common_scale_residuals(reference_path):
        corrected = row.predicted * factor
        rel = _relative_error(corrected, row.reference)
        rows.append(
            {
                "ratio": row.ratio,
                "corrected": corrected,
                "reference": row.reference,
                "relative_error": rel,
                "passes_tolerance": rel <= 0.25,
                "was_previously_passing": row.passes_tolerance,
                "damaged": row.passes_tolerance and rel > 0.25,
            }
        )
    damaged = tuple(row["ratio"] for row in rows if row["damaged"])
    return {
        "factor_to_fix_u_over_t": factor,
        "rows": rows,
        "damaged_ratios": damaged,
        "global_rescale_allowed": len(damaged) == 0,
    }


def exploratory_light_up_candidates(reference_path: str | Path = "data/reference_common_scale_quark_ratios_mz.json") -> tuple[CandidateRepair, ...]:
    """Return predeclared exploratory light-up-only candidate factors."""

    alpha = 1.0 / ALPHA_INV_LOW_ENERGY
    required = light_up_required_factor(reference_path)
    candidates = (
        ("no_correction", 1.0, ("Baseline frozen value.",)),
        ("required_factor_diagnostic_only", required, ("Computed after seeing the reference; diagnostic only, not an allowed derivation.",)),
        ("coframe_amplitude_1_over_sqrt3", 1.0 / sqrt(3.0), ("Simple triplet-amplitude factor; structurally suggestive but not derived.",)),
        ("weak_doublet_probability_1_over_2", 0.5, ("Borrowed from existing middle-up dressing family; not derived for light-up mode.",)),
        ("weak_doublet_amplitude_1_over_sqrt2", 1.0 / sqrt(2.0), ("Simple two-component amplitude factor; not derived for light-up mode.",)),
        ("alpha_sqrt", sqrt(alpha), ("Alpha-suppressed candidate; included as exploratory stress test only.",)),
    )
    u_row = next(row for row in dressed_common_scale_residuals(reference_path) if row.ratio == "u/t")
    rows: list[CandidateRepair] = []
    for name, factor, notes in candidates:
        corrected = u_row.predicted * factor
        rel = _relative_error(corrected, u_row.reference)
        rows.append(
            CandidateRepair(
                name=name,
                factor=factor,
                corrected_u_over_t=corrected,
                relative_error=rel,
                passes_tolerance=rel <= 0.25,
                changes_official_u_over_t=factor != 1.0,
                changes_ckm_sin_theta_13=factor != 1.0,
                status=EXPLORATORY_CANDIDATE if factor != 1.0 else "BASELINE",
                notes=notes,
            )
        )
    return tuple(rows)


def tension_result(reference_path: str | Path = "data/reference_common_scale_quark_ratios_mz.json") -> LightUpTensionResult:
    """Return the sprint-level classification."""

    common_scale = common_scale_audit_payload(reference_path)
    residuals = dressed_common_scale_residuals(reference_path)
    u_row = next(row for row in residuals if row.ratio == "u/t")
    reference = load_common_scale_reference(reference_path)
    if common_scale["classification"] != COMMON_SCALE_RG_VALIDATED_WARNING:
        classification = EXTERNAL_INPUT_REQUIRED
    elif reference["ratios"]["u/t"].get("uncertainty") is not None:
        classification = U_T_TENSION_EXPLAINED_BY_INPUT_UNCERTAINTY
    else:
        classification = U_T_WARNING_CONFIRMED
    global_check = global_rescale_diagnostic(reference_path)
    candidates = exploratory_light_up_candidates(reference_path)
    nonofficial_passers = [
        row for row in candidates
        if row.name not in {"no_correction", "required_factor_diagnostic_only"} and row.passes_tolerance
    ]
    return LightUpTensionResult(
        classification=classification,
        u_t_warning_confirmed=not u_row.passes_tolerance,
        global_rescale_allowed=bool(global_check["global_rescale_allowed"]),
        candidate_repair_available=bool(nonofficial_passers),
        candidate_status=EXPLORATORY_CANDIDATE if nonofficial_passers else NO_OFFICIAL_REPAIR,
        damages_other_ratios=bool(global_check["damaged_ratios"]),
        recommendation=(
            "Keep u/t as a common-scale warning. Do not alter official frozen outputs. "
            "A light-up-only factor near 1/sqrt(3) is numerically suggestive but remains "
            "candidate-only and would change official u/t and CKM sin(theta_13)."
        ),
    )


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


def audit_payload(reference_path: str | Path = "data/reference_common_scale_quark_ratios_mz.json") -> dict[str, Any]:
    """Return the full light-up tension audit payload."""

    reference = load_common_scale_reference(reference_path)
    residuals = dressed_common_scale_residuals(reference_path)
    u_row = next(row for row in residuals if row.ratio == "u/t")
    result = tension_result(reference_path)
    return {
        "title": "BHSM common-scale light-up ratio tension audit",
        "classification": result.classification,
        "result": result,
        "reference_source": {
            "scale": reference["scale"],
            "scheme": reference["scheme"],
            "source_citation_text": reference["source_citation_text"],
            "u_over_t_uncertainty": reference["ratios"]["u/t"].get("uncertainty"),
        },
        "u_over_t": u_row,
        "all_residuals": residuals,
        "global_rescale": global_rescale_diagnostic(reference_path),
        "exploratory_candidates": exploratory_light_up_candidates(reference_path),
        "repair_attempted": True,
        "repair_official": False,
        "common_scale_quark_status_changes": False,
        "frozen_sanity": frozen_sanity_payload(),
        "official_u_over_t_changed": False,
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "limitations": (
            "The M_Z reference table lacks uncertainty propagation for u/t.",
            "The up quark is extremely light, so relative errors are visually amplified.",
            "Any light-up-only repair would change official u/t and CKM sin(theta_13).",
            "Global rescaling is rejected because it damages ratios that already survive.",
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
    """Render the tension audit as Markdown."""

    payload = payload or audit_payload()
    result = payload["result"]
    u_row = payload["u_over_t"]
    lines = [
        "# Light-Up Ratio Tension Audit",
        "",
        "## Problem",
        "",
        "The validated common-scale M_Z audit leaves `u/t` as the only dressed-branch quark-ratio warning while dressed `c/t`, `s/b`, and `d/b` pass the declared scheme-aware band.",
        "",
        "## Common-Scale Quark RG Result",
        "",
        f"Classification: `{payload['classification']}`",
        f"BHSM `u/t`: `{u_row.predicted}`",
        f"M_Z reference `u/t`: `{u_row.reference}`",
        f"Relative error: `{u_row.relative_error}`",
        f"Absolute error: `{u_row.absolute_error}`",
        "",
        "## Why u/t Is Special",
        "",
        "The numerator is an extremely light quark. Small absolute changes in a common-scale light-quark reference produce large ordinary relative errors. This does not erase the residual, but it argues for warning-level treatment unless uncertainty propagation is added.",
        "",
        "## Existing Official BHSM Status",
        "",
        "- `BHSM_BARE_V1` is unchanged.",
        "- `BHSM_DRESSED_V1_CANDIDATE` is unchanged.",
        "- Official `u/t` is unchanged.",
        "- The dressed branch still changes only `c/t`.",
        "",
        "## Whether The Tension Is A Failure Or Warning",
        "",
        f"u/t warning confirmed: `{result.u_t_warning_confirmed}`",
        f"Recommendation: {result.recommendation}",
        "",
        "## Possible Structural Explanations",
        "",
        "| Candidate | Factor | Corrected u/t | Relative Error | Status | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["exploratory_candidates"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | {} |".format(
                row.name,
                row.factor,
                row.corrected_u_over_t,
                row.relative_error,
                row.status,
                "<br>".join(row.notes),
            )
        )
    lines.extend(
        [
            "",
            "## Rejected Explanations",
            "",
            f"- Global rescale allowed: `{result.global_rescale_allowed}`",
            f"- Damaged ratios under global rescale: `{payload['global_rescale']['damaged_ratios']}`",
            "- Mixed-scale masses are not used as precision truth.",
            "",
            "## Candidate Repair Criteria",
            "",
            "- Any light-up dressing must be derived before adoption.",
            "- It must be frozen before future external comparison.",
            "- It must not damage official CKM, c/t, s/b, d/b, gauge, or electroweak screens.",
            "",
            "## Recommendation",
            "",
            "Keep `u/t` as a warning-level common-scale tension. The closest simple factor is exploratory only and not official.",
            "",
        ]
    )
    return "\n".join(lines)


def export_light_up_ratio_tension_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export theory and audit files."""

    base = Path(root)
    payload = audit_payload(base / "data/reference_common_scale_quark_ratios_mz.json")
    markdown = render_markdown(payload)
    paths = {
        "theory": base / "theory" / "light_up_ratio_tension_note.md",
        "audit_md": base / "audits" / "light_up_ratio_tension_audit.md",
        "audit_json": base / "audits" / "light_up_ratio_tension_audit.json",
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
    export_light_up_ratio_tension_outputs()
