"""Candidate-only minimal branch-threshold reconstruction audit.

This module fits small universal log-space candidate laws to the read-only
existing BHSM bare values. It is diagnostic only and does not modify or replace
official prediction machinery.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

from candidate_existing_engine_branch_threshold import (
    BRANCH as PRIOR_BRANCH,
    REFERENCE_SOURCE,
    branch_assignments,
    read_only_existing_outputs,
)


BRANCH = "bhsm-minimal-branch-threshold-reconstruction"
STATUS = "candidate_only"
EXISTING_ENGINE_SOURCES = [
    "docs/frozen_predictions.json",
    "docs/frozen_predictions.md",
    "theory/bhsm_prediction_ledger.json",
    "existing tests/fixtures",
]

ALLOWED_VERDICTS = {
    "MINIMAL_BRANCH_THRESHOLD_RECONSTRUCTION_COMPLETE",
    "BRANCH_RANK_THRESHOLD_APPROXIMATES_EXISTING_ENGINE",
    "BRANCH_TYPE_SPECIALNESS_IMPROVES_SHAPE",
    "BOUNDED_THRESHOLD_SIGNAL_INDICATED",
    "LOG_THRESHOLD_SIGNAL_INDICATED",
    "MIXED_BRANCH_PENALTY_INDICATED",
    "ORIENTATION_CROSS_TERM_SIGNAL_INDICATED",
    "HIDDEN_RESPONSE_REMAINS_INDICATED",
    "OVERFIT_RISK_WARNING",
    "REFERENCE_SCHEME_LIMITATION",
    "NO_NUMERICAL_CLOSURE",
}

CLAIM_LABELS = (
    "MINIMAL_BRANCH_THRESHOLD_RECONSTRUCTION_COMPLETE",
    "BRANCH_RANK_THRESHOLD_DIAGNOSTIC",
    "BRANCH_TYPE_SPECIALNESS_DIAGNOSTIC",
    "NONLINEAR_THRESHOLD_CANDIDATE_DIAGNOSTIC",
    "HIDDEN_RESPONSE_REMAINS_DIAGNOSTIC",
    "NO_NEW_OFFICIAL_MASS_FORMULA_GUARDRAIL",
)


LAW_DEFINITIONS = {
    "A_branch_rank_only": {
        "formula": "log_pred=A0-a*branch_rank_by_N",
        "coefficient_names": ["A0", "a"],
        "status": "BRANCH_RANK_THRESHOLD_DIAGNOSTIC",
    },
    "B_branch_rank_plus_type": {
        "formula": "log_pred=A0-a*branch_rank_by_N+b_fiber*pure_fiber+b_base*pure_base",
        "coefficient_names": ["A0", "a", "b_fiber", "b_base"],
        "status": "BRANCH_TYPE_SPECIALNESS_DIAGNOSTIC",
    },
    "C_bounded_norm_plus_type": {
        "formula": "log_pred=A0-a*N/(1+N)+b_fiber*pure_fiber+b_base*pure_base",
        "coefficient_names": ["A0", "a", "b_fiber", "b_base"],
        "status": "NONLINEAR_THRESHOLD_CANDIDATE_DIAGNOSTIC",
    },
    "D_log_threshold_plus_type": {
        "formula": "log_pred=A0-a*log(1+N)+b_fiber*pure_fiber+b_base*pure_base",
        "coefficient_names": ["A0", "a", "b_fiber", "b_base"],
        "status": "NONLINEAR_THRESHOLD_CANDIDATE_DIAGNOSTIC",
    },
    "E_branch_rank_mixed_penalty": {
        "formula": "log_pred=A0-a*branch_rank_by_N+b_fiber*pure_fiber+b_base*pure_base-c_mixed*mixed",
        "coefficient_names": ["A0", "a", "b_fiber", "b_base", "c_mixed"],
        "status": "MIXED_BRANCH_PENALTY_DIAGNOSTIC",
    },
    "F_orientation_cross": {
        "formula": "log_pred=A0-a*branch_rank_by_N+b_fiber*pure_fiber+b_base*pure_base+gamma*orientation_product",
        "coefficient_names": ["A0", "a", "b_fiber", "b_base", "gamma"],
        "status": "ORIENTATION_CROSS_TERM_SIGNAL_INDICATED",
    },
}


def _assignment_by_ratio() -> dict[str, dict[str, Any]]:
    return {row.generation_label: asdict(row) for row in branch_assignments() if row.generation_label != "reference"}


def read_only_targets(root: str | Path = ".") -> list[dict[str, Any]]:
    """Return read-only existing bare targets enriched with branch features."""

    assignments = _assignment_by_ratio()
    rows = []
    for output in read_only_existing_outputs(root):
        assignment = assignments[output["ratio_name"]]
        rows.append(
            {
                **output,
                **{
                    "q": assignment["mode_q"],
                    "j": assignment["mode_j"],
                    "k": assignment["mode_k"],
                    "N": assignment["N"],
                    "Omega_f": assignment["Omega_f"],
                    "Omega_star": assignment["Omega_star"],
                    "branch_rank_by_N": assignment["branch_rank_by_N"],
                    "branch_role": assignment["branch_role"],
                    "mode_type": "pure_fiber"
                    if assignment["pure_fiber_flag"]
                    else "pure_base"
                    if assignment["pure_base_flag"]
                    else "mixed",
                    "fiber_fraction": assignment["mode_q"] ** 2 / assignment["N"] if assignment["N"] else 0.0,
                    "base_fraction": assignment["mode_j"] ** 2 / assignment["N"] if assignment["N"] else 0.0,
                    "cross_term": assignment["cross_term"],
                    "orientation_product": assignment["orientation_product"],
                    "lower_doublet_projector": assignment["lower_doublet_projector"],
                    "colored_lift_exponent": assignment["colored_lift_exponent"],
                    "log_existing_bare": math.log(output["official_or_existing_bare_prediction"]),
                },
            }
        )
    return rows


def _features(row: dict[str, Any], law_id: str) -> list[float]:
    n = float(row["N"])
    rank = float(row["branch_rank_by_N"])
    pure_fiber = 1.0 if row["mode_type"] == "pure_fiber" else 0.0
    pure_base = 1.0 if row["mode_type"] == "pure_base" else 0.0
    mixed = 1.0 if row["mode_type"] == "mixed" else 0.0
    if law_id == "A_branch_rank_only":
        return [1.0, -rank]
    if law_id == "B_branch_rank_plus_type":
        return [1.0, -rank, pure_fiber, pure_base]
    if law_id == "C_bounded_norm_plus_type":
        return [1.0, -(n / (1.0 + n)), pure_fiber, pure_base]
    if law_id == "D_log_threshold_plus_type":
        return [1.0, -math.log(1.0 + n), pure_fiber, pure_base]
    if law_id == "E_branch_rank_mixed_penalty":
        return [1.0, -rank, pure_fiber, pure_base, -mixed]
    if law_id == "F_orientation_cross":
        return [1.0, -rank, pure_fiber, pure_base, float(row["orientation_product"])]
    raise ValueError(law_id)


def _ordering_pass(predictions: dict[str, float]) -> bool:
    return (
        predictions["mu/tau"] > predictions["e/tau"]
        and predictions["c/t"] > predictions["u/t"]
        and predictions["s/b"] > predictions["d/b"]
    )


def fit_law(law_id: str, root: str | Path = ".") -> dict[str, Any]:
    """Fit one candidate law to existing read-only bare values."""

    rows = read_only_targets(root)
    x = np.array([_features(row, law_id) for row in rows], dtype=float)
    y = np.array([row["log_existing_bare"] for row in rows], dtype=float)
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    predicted_logs = x @ beta
    residuals = predicted_logs - y
    coefficient_names = LAW_DEFINITIONS[law_id]["coefficient_names"]
    coefficients = {name: float(value) for name, value in zip(coefficient_names, beta)}
    row_predictions = []
    predictions_by_ratio: dict[str, float] = {}
    for row, pred_log, residual in zip(rows, predicted_logs, residuals):
        predicted = float(math.exp(pred_log))
        predictions_by_ratio[row["ratio_name"]] = predicted
        row_predictions.append(
            {
                "ratio_name": row["ratio_name"],
                "sector": row["sector"],
                "mode_type": row["mode_type"],
                "branch_rank_by_N": row["branch_rank_by_N"],
                "existing_bare_prediction": row["official_or_existing_bare_prediction"],
                "candidate_prediction": predicted,
                "log_residual": float(residual),
                "abs_log_residual": float(abs(residual)),
            }
        )
    parameter_count = len(coefficient_names)
    sample_count = len(rows)
    overfit_risk = parameter_count >= 4
    return {
        "law_id": law_id,
        "formula": LAW_DEFINITIONS[law_id]["formula"],
        "status": LAW_DEFINITIONS[law_id]["status"],
        "official": False,
        "parameter_policy": "single_universal_parameter_set",
        "parameter_count": parameter_count,
        "sample_count": sample_count,
        "overfit_risk": overfit_risk,
        "rms_log_error_to_existing_bare": float(math.sqrt(float(np.mean(residuals * residuals)))),
        "max_abs_log_error_to_existing_bare": float(np.max(np.abs(residuals))),
        "ordering_pass": _ordering_pass(predictions_by_ratio),
        "middle_vs_light_separation_pass": _ordering_pass(predictions_by_ratio),
        "coefficients": coefficients,
        "row_predictions": row_predictions,
        "row_log_residuals": {row["ratio_name"]: float(residual) for row, residual in zip(rows, residuals)},
    }


def candidate_law_results(root: str | Path = ".") -> list[dict[str, Any]]:
    """Return all candidate law fit results."""

    return [fit_law(law_id, root) for law_id in LAW_DEFINITIONS]


def best_law(root: str | Path = ".") -> dict[str, Any]:
    """Return best candidate law by RMS, with no official promotion."""

    return min(
        candidate_law_results(root),
        key=lambda row: (row["rms_log_error_to_existing_bare"], row["max_abs_log_error_to_existing_bare"]),
    )


def hidden_response_decomposition(best: dict[str, Any], root: str | Path = ".") -> list[dict[str, Any]]:
    """Return residual hidden response after best candidate law."""

    rows = read_only_targets(root)
    predicted = {row["ratio_name"]: row for row in best["row_predictions"]}
    out = []
    for row in rows:
        pred = predicted[row["ratio_name"]]["candidate_prediction"]
        hidden = row["official_or_existing_bare_prediction"] / pred
        out.append(
            {
                "ratio_name": row["ratio_name"],
                "sector": row["sector"],
                "mode_type": row["mode_type"],
                "R_hidden": hidden,
                "log_R_hidden": math.log(hidden),
                "pure_fiber": row["mode_type"] == "pure_fiber",
                "pure_base": row["mode_type"] == "pure_base",
                "mixed": row["mode_type"] == "mixed",
                "lower_doublet_projector": row["lower_doublet_projector"],
                "orientation_product": row["orientation_product"],
                "diagnostic_only": True,
            }
        )
    return out


def verdict_labels(best: dict[str, Any]) -> list[str]:
    labels = [
        "MINIMAL_BRANCH_THRESHOLD_RECONSTRUCTION_COMPLETE",
        "HIDDEN_RESPONSE_REMAINS_INDICATED",
        "REFERENCE_SCHEME_LIMITATION",
        "NO_NUMERICAL_CLOSURE",
    ]
    law_id = best["law_id"]
    if law_id.startswith("A"):
        labels.append("BRANCH_RANK_THRESHOLD_APPROXIMATES_EXISTING_ENGINE")
    if law_id.startswith(("B", "E", "F")):
        labels.append("BRANCH_TYPE_SPECIALNESS_IMPROVES_SHAPE")
    if law_id.startswith("C"):
        labels.append("BOUNDED_THRESHOLD_SIGNAL_INDICATED")
    if law_id.startswith("D"):
        labels.append("LOG_THRESHOLD_SIGNAL_INDICATED")
    if law_id.startswith("E"):
        labels.append("MIXED_BRANCH_PENALTY_INDICATED")
    if law_id.startswith("F"):
        labels.append("ORIENTATION_CROSS_TERM_SIGNAL_INDICATED")
    if any(row["overfit_risk"] for row in candidate_law_results()):
        labels.append("OVERFIT_RISK_WARNING")
    return labels


def build_payload(root: str | Path = ".") -> dict[str, Any]:
    """Return reconstruction payload."""

    best = best_law(root)
    laws = candidate_law_results(root)
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "inputs": {
            "existing_engine_sources": EXISTING_ENGINE_SOURCES,
            "reference_ratio_source": REFERENCE_SOURCE,
            "base_branch": PRIOR_BRANCH,
        },
        "read_only_existing_outputs": read_only_targets(root),
        "branch_feature_table": [
            {
                key: row[key]
                for key in (
                    "ratio_name",
                    "sector",
                    "q",
                    "j",
                    "k",
                    "N",
                    "Omega_f",
                    "Omega_star",
                    "branch_rank_by_N",
                    "branch_role",
                    "mode_type",
                    "fiber_fraction",
                    "base_fraction",
                    "cross_term",
                    "orientation_product",
                    "lower_doublet_projector",
                    "colored_lift_exponent",
                )
            }
            for row in read_only_targets(root)
        ],
        "candidate_law_results": laws,
        "best_candidate_law": {
            key: best[key]
            for key in (
                "law_id",
                "official",
                "parameter_count",
                "sample_count",
                "overfit_risk",
                "rms_log_error_to_existing_bare",
                "max_abs_log_error_to_existing_bare",
                "ordering_pass",
                "middle_vs_light_separation_pass",
                "coefficients",
            )
        },
        "hidden_response_decomposition": hidden_response_decomposition(best, root),
        "summary": {
            "best_supported_structure": [
                "branch_threshold",
                "branch_type_specialness",
                "hidden_response_remaining",
                "reference_scheme_harmonization",
            ],
            "recommended_next_target": "derive or reject the best branch-threshold law and its residual hidden-response terms from BHSM boundary dynamics",
        },
        "verdict_labels": verdict_labels(best),
        "claim_labels": CLAIM_LABELS,
        "notes": [
            "candidate-only",
            "existing/frozen values are read-only",
            "no frozen predictions changed",
            "no official predictions changed",
            "quark ratios are scheme-sensitive where applicable",
            "no new official mass formula",
        ],
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def render_reconstruction_markdown(payload: dict[str, Any] | None = None) -> str:
    p = payload or build_payload(Path(__file__).resolve().parents[1])
    best = p["best_candidate_law"]
    lines = [
        "# Minimal Branch-Threshold Reconstruction",
        "",
        "Status: `MINIMAL_BRANCH_THRESHOLD_RECONSTRUCTION_COMPLETE`",
        "",
        "This candidate-only audit tests whether simple universal branch-threshold laws can approximate the read-only existing BHSM bare mass pattern. It introduces no official mass formula.",
        "",
        "## Best Diagnostic Law",
        "",
        f"Law: `{best['law_id']}`",
        f"RMS log error to existing bare: `{best['rms_log_error_to_existing_bare']}`",
        f"Max abs log error: `{best['max_abs_log_error_to_existing_bare']}`",
        f"Ordering pass: `{best['ordering_pass']}`",
        f"Middle-vs-light separation pass: `{best['middle_vs_light_separation_pass']}`",
        f"Parameter count: `{best['parameter_count']}` of sample count `{best['sample_count']}`",
        f"Overfit risk: `{best['overfit_risk']}`",
        f"Coefficients: `{best['coefficients']}`",
        "",
        "## Candidate Laws",
        "",
        "| Law | RMS | Max abs | Parameters | Overfit risk | Official |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in p["candidate_law_results"]:
        lines.append(
            f"| `{row['law_id']}` | `{row['rms_log_error_to_existing_bare']}` | `{row['max_abs_log_error_to_existing_bare']}` | `{row['parameter_count']}` | `{row['overfit_risk']}` | `{row['official']}` |"
        )
    lines.extend(
        [
            "",
            "## Conclusions",
            "",
            "1. Branch-rank threshold alone approximates the existing engine only coarsely.",
            "2. Adding pure-fiber and pure-base branch specialness improves shape in diagnostic laws but increases overfit risk.",
            "3. Bounded/log thresholds are diagnostic alternatives, not official formulas.",
            "4. Remaining error is structured by sector and mode type through hidden response terms.",
            "5. The next derivation target is a branch-aware threshold law plus residual hidden-response terms from boundary dynamics.",
            "",
            "## Claim Boundaries",
            "",
            "- No official predictions are changed.",
            "- No frozen predictions are changed.",
            "- No new official mass formula is introduced.",
            "- No sector-specific or per-particle coefficients are used.",
            "- `BARE_YUKAWA_SPECTRAL_ACTION_CANDIDATE` is not upgraded to derived.",
            "- `FULL_BHSM_MASS_ENGINE_CANDIDATE_ARCHITECTURE` is not upgraded to derived.",
            "- `RESPONSE_SELECTOR_STRUCTURAL_CANDIDATE` is not upgraded to derived.",
            "",
        ]
    )
    return "\n".join(lines)


def render_laws_markdown(payload: dict[str, Any] | None = None) -> str:
    p = payload or build_payload(Path(__file__).resolve().parents[1])
    lines = [
        "# Branch Threshold Candidate Laws",
        "",
        "Status: `BRANCH_RANK_THRESHOLD_DIAGNOSTIC`",
        "",
        "This note describes candidate branch-threshold laws. They are diagnostics only and remain unofficial.",
        "",
        "| Law | Formula | Parameter count | Overfit risk |",
        "| --- | --- | ---: | --- |",
    ]
    for row in p["candidate_law_results"]:
        lines.append(
            f"| `{row['law_id']}` | `{row['formula']}` | `{row['parameter_count']}` | `{row['overfit_risk']}` |"
        )
    lines.extend(
        [
            "",
            "Pure-fiber and pure-base specialness are tested as universal coefficients, not sector-specific tuning. Mixed-branch penalties and orientation/cross terms are diagnostic only. Forbidden tuning rules: no sector-specific parameters, no per-particle response factors, no retrofitting frozen predictions.",
            "",
            "Guardrail: `NO_NEW_OFFICIAL_MASS_FORMULA_GUARDRAIL`.",
            "",
        ]
    )
    return "\n".join(lines)


def export_outputs(root: str | Path = ".") -> dict[str, Any]:
    base = Path(root)
    payload = build_payload(base)
    (base / "theory").mkdir(parents=True, exist_ok=True)
    (base / "theory" / "minimal_branch_threshold_reconstruction.md").write_text(
        render_reconstruction_markdown(payload),
        encoding="utf-8",
    )
    (base / "theory" / "minimal_branch_threshold_reconstruction_results.json").write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (base / "theory" / "branch_threshold_candidate_laws.md").write_text(
        render_laws_markdown(payload),
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_outputs(Path(__file__).resolve().parents[1])
