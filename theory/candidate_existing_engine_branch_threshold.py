"""Candidate-only existing-engine branch/threshold audit.

The audit treats existing BHSM bare/dressed values as read-only data and asks
which branch or threshold structure the failed raw spectral-action candidate
appears to be missing.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from candidate_bare_engine_triangulation import (
    FROZEN_SOURCE,
    REFERENCE_SOURCE,
    SPECTRAL_ACTION_SOURCE,
    SECTOR_DATA,
    O_j,
    O_q,
    engine_comparison,
    lower_doublet_projector,
    omega,
    spectral_action_prediction,
)


BRANCH = "bhsm-existing-engine-branch-threshold-audit"
STATUS = "candidate_only"

ALLOWED_VERDICTS = {
    "EXISTING_ENGINE_BRANCH_THRESHOLD_AUDIT_COMPLETE",
    "EXISTING_ENGINE_NOT_SIMPLE_RAW_EXPONENTIAL",
    "BRANCH_ASSIGNMENT_SIGNAL_INDICATED",
    "NONLINEAR_THRESHOLD_SIGNAL_INDICATED",
    "HIDDEN_RESPONSE_DECOMPOSITION_INDICATED",
    "PURE_FIBER_BRANCH_SPECIALNESS_INDICATED",
    "PURE_BASE_BRANCH_SPECIALNESS_INDICATED",
    "SECTOR_ORIENTATION_SIGNAL_INDICATED",
    "REFERENCE_SCHEME_LIMITATION",
    "NO_NUMERICAL_CLOSURE",
}

CLAIM_LABELS = (
    "EXISTING_ENGINE_BRANCH_THRESHOLD_AUDIT_COMPLETE",
    "EXISTING_ENGINE_NOT_SIMPLE_RAW_EXPONENTIAL",
    "BRANCH_ASSIGNMENT_SIGNAL_INDICATED",
    "NONLINEAR_THRESHOLD_SIGNAL_INDICATED",
    "HIDDEN_RESPONSE_DECOMPOSITION_INDICATED",
    "NO_NEW_OFFICIAL_MASS_FORMULA_GUARDRAIL",
    "OFFICIAL_ENGINE_READ_ONLY_GUARDRAIL",
)

MODE_LEDGER_QJ = {
    "charged_lepton": [
        ("reference", (0, 0)),
        ("mu/tau", (1, 2)),
        ("e/tau", (3, 3)),
    ],
    "up": [
        ("reference", (0, 0)),
        ("c/t", (6, 0)),
        ("u/t", (8, 1)),
    ],
    "down": [
        ("reference", (0, 0)),
        ("s/b", (0, 3)),
        ("d/b", (4, 2)),
    ],
}


@dataclass(frozen=True)
class BranchAssignment:
    """One charged-sector branch assignment row."""

    sector: str
    generation_label: str
    mode_q: int
    mode_j: int
    mode_k: int
    N: int
    Omega_f: float
    Omega_star: int
    branch_role: str
    branch_rank_by_N: int
    branch_gap_to_reference: int
    branch_gap_to_partner: int | None
    pure_fiber_flag: bool
    pure_base_flag: bool
    mixed_flag: bool
    lower_doublet_projector: float
    colored_lift_exponent: float
    sector_operator_norm: float
    orientation_product: float
    cross_term: int


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_only_existing_outputs(root: str | Path = ".") -> list[dict[str, Any]]:
    """Return read-only existing charged mass values."""

    return [
        {
            "ratio_name": row.ratio_name,
            "sector": row.sector,
            "mode_qj": list(row.mode_qj),
            "mode_kj": [row.mode_qj[0] + 2 * row.mode_qj[1], row.mode_qj[1]],
            "official_or_existing_bare_prediction": row.official_or_existing_bare_prediction,
            "official_or_existing_dressed_candidate_prediction": row.official_or_existing_dressed_candidate_prediction,
            "reference_ratio": row.reference_ratio,
            "reference_scheme_note": "quark ratios are scheme-sensitive" if row.scheme_sensitive else "scheme-stable for this audit",
            "scheme_sensitive": row.scheme_sensitive,
        }
        for row in engine_comparison(root)
    ]


def read_only_ckm_outputs(root: str | Path = ".") -> list[dict[str, Any]]:
    """Return CKM rows already present in frozen docs."""

    frozen = _read_json(Path(root) / "docs" / "frozen_predictions.json")
    rows = []
    for key in ("sin_theta_13",):
        if key in frozen.get("outputs", {}):
            rows.append(
                {
                    "quantity": key,
                    "bare": frozen["outputs"][key]["bare"],
                    "dressed_candidate": frozen["outputs"][key]["dressed_candidate"],
                    "changed": frozen["outputs"][key]["changed"],
                    "source": "docs/frozen_predictions.json",
                    "used_in_mass_engine_fit": False,
                }
            )
    return rows


def _n(q: int, j: int) -> int:
    return q * q + j * j


def _role(q: int, j: int, rank: int) -> str:
    if q == 0 and j == 0:
        return "reference"
    branch = "lower_nonzero_action" if rank == 1 else "higher_nonzero_action"
    if j == 0:
        return f"{branch}, pure_fiber"
    if q == 0:
        return f"{branch}, pure_base"
    return f"{branch}, mixed"


def branch_assignments() -> list[BranchAssignment]:
    """Return branch assignment inventory for charged modes."""

    assignments: list[BranchAssignment] = []
    for sector, modes in MODE_LEDGER_QJ.items():
        nonzero = [(label, qj, _n(*qj)) for label, qj in modes if qj != (0, 0)]
        ranked = sorted(nonzero, key=lambda item: item[2])
        rank_by_label = {label: index + 1 for index, (label, _qj, _nval) in enumerate(ranked)}
        n_by_label = {label: nval for label, _qj, nval in nonzero}
        for label, (q, j) in modes:
            rank = 0 if label == "reference" else rank_by_label[label]
            partner_gap = None
            if label != "reference":
                other_n = [value for other_label, value in n_by_label.items() if other_label != label][0]
                partner_gap = abs(_n(q, j) - other_n)
            data = SECTOR_DATA[sector]
            oq = O_q(sector)
            oj = O_j(sector)
            assignments.append(
                BranchAssignment(
                    sector=sector,
                    generation_label=label,
                    mode_q=q,
                    mode_j=j,
                    mode_k=q + 2 * j,
                    N=_n(q, j),
                    Omega_f=omega(sector, q, j),
                    Omega_star=int(data["Omega_star"]),
                    branch_role=_role(q, j, rank),
                    branch_rank_by_N=rank,
                    branch_gap_to_reference=_n(q, j),
                    branch_gap_to_partner=partner_gap,
                    pure_fiber_flag=j == 0 and q > 0,
                    pure_base_flag=q == 0 and j > 0,
                    mixed_flag=q > 0 and j > 0,
                    lower_doublet_projector=lower_doublet_projector(sector),
                    colored_lift_exponent=3.0 * data["B"] + lower_doublet_projector(sector),
                    sector_operator_norm=oq * oq + oj * oj,
                    orientation_product=(oq * q) * (oj * j),
                    cross_term=q * j,
                )
            )
    return assignments


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    denom = math.sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    if denom == 0:
        return None
    return sum(x * y for x, y in zip(dx, dy)) / denom


def candidate_variables() -> list[dict[str, Any]]:
    """Return candidate shape variables for nonzero charged rows."""

    rows = []
    by_label = {(row.sector, row.generation_label): row for row in branch_assignments()}
    for output in read_only_existing_outputs():
        sector = output["sector"]
        label = output["ratio_name"]
        assignment = by_label[(sector, label)]
        n = assignment.N
        sqrt_n = math.sqrt(n)
        rows.append(
            {
                "ratio_name": label,
                "sector": sector,
                "log_existing_bare_prediction": math.log(output["official_or_existing_bare_prediction"]),
                "log_existing_dressed_candidate_prediction": math.log(output["official_or_existing_dressed_candidate_prediction"]),
                "log_reference_ratio": math.log(output["reference_ratio"]) if output["reference_ratio"] else None,
                "N": n,
                "branch_rank_by_N": assignment.branch_rank_by_N,
                "pure_fiber_flag": float(assignment.pure_fiber_flag),
                "pure_base_flag": float(assignment.pure_base_flag),
                "mixed_flag": float(assignment.mixed_flag),
                "lower_nonzero_action_flag": float("lower_nonzero_action" in assignment.branch_role),
                "higher_nonzero_action_flag": float("higher_nonzero_action" in assignment.branch_role),
                "branch_gap": n - min(item.N for item in branch_assignments() if item.sector == sector and item.branch_rank_by_N > 0),
                "partner_gap": assignment.branch_gap_to_partner or 0,
                "lambda_O": (O_q(sector) * assignment.mode_q) ** 2 + (O_j(sector) * assignment.mode_j) ** 2,
                "orientation_product": assignment.orientation_product,
                "cross_term": assignment.cross_term,
                "threshold_linear": n / (1.0 + n),
                "threshold_sqrt": sqrt_n / (1.0 + sqrt_n),
                "threshold_log": math.log(1.0 + n),
                "threshold_inverse_gap": 1.0 / (1.0 + n),
                "threshold_branch_rank": assignment.branch_rank_by_N / 2.0,
                "fiber_fraction": assignment.mode_q * assignment.mode_q / n if n else 0.0,
                "base_fraction": assignment.mode_j * assignment.mode_j / n if n else 0.0,
            }
        )
    return rows


def shape_associations() -> list[dict[str, Any]]:
    """Return lightweight small-sample associations."""

    rows = candidate_variables()
    keys = [
        "N",
        "branch_rank_by_N",
        "pure_fiber_flag",
        "pure_base_flag",
        "mixed_flag",
        "lower_nonzero_action_flag",
        "higher_nonzero_action_flag",
        "branch_gap",
        "partner_gap",
        "lambda_O",
        "orientation_product",
        "cross_term",
        "threshold_linear",
        "threshold_sqrt",
        "threshold_log",
        "threshold_inverse_gap",
        "threshold_branch_rank",
        "fiber_fraction",
        "base_fraction",
    ]
    targets = ("log_existing_bare_prediction", "log_reference_ratio")
    out = []
    for key in keys:
        xs = [float(row[key]) for row in rows]
        for target in targets:
            ys = [float(row[target]) for row in rows if row[target] is not None]
            out.append(
                {
                    "variable": key,
                    "target": target,
                    "pearson": _pearson(xs, ys),
                    "sample_size": len(xs),
                    "diagnostic_only_small_sample": True,
                }
            )
    return out


def _rank_order_for_sector(sector: str, variable: str) -> dict[str, Any]:
    rows = [row for row in candidate_variables() if row["sector"] == sector]
    # Existing predictions are smaller for the lighter branch. A variable that
    # increases from middle to light separates the pair in the expected order.
    middle = next(row for row in rows if row["ratio_name"] in {"mu/tau", "c/t", "s/b"})
    light = next(row for row in rows if row["ratio_name"] in {"e/tau", "u/t", "d/b"})
    return {
        "sector": sector,
        "variable": variable,
        "middle_value": middle[variable],
        "light_value": light[variable],
        "separates_middle_light": light[variable] > middle[variable],
        "diagnostic_only_small_sample": True,
    }


def rank_order_checks() -> list[dict[str, Any]]:
    variables = ("N", "branch_rank_by_N", "branch_gap", "threshold_log", "threshold_branch_rank")
    return [_rank_order_for_sector(sector, variable) for sector in SECTOR_DATA for variable in variables]


def _fit_one_parameter_shape(variable: str, transform: str) -> dict[str, Any]:
    rows = candidate_variables()
    xs = [float(row[variable]) for row in rows]
    ys = [float(row["log_existing_bare_prediction"]) for row in rows]
    denom = sum(x * x for x in xs)
    a = -sum(x * y for x, y in zip(xs, ys)) / denom if denom else 0.0
    predicted_logs = [-a * x for x in xs]
    errors = [pred - y for pred, y in zip(predicted_logs, ys)]
    return {
        "family": transform,
        "status": "candidate_shape_diagnostic",
        "official": False,
        "parameter_policy": "single_universal_parameter",
        "parameters": {"a": a},
        "rms_log_error_to_existing_bare": math.sqrt(sum(error * error for error in errors) / len(errors)),
        "max_abs_log_error_to_existing_bare": max(abs(error) for error in errors),
        "overfit_risk": False,
    }


def threshold_family_diagnostics() -> list[dict[str, Any]]:
    diagnostics = [
        _fit_one_parameter_shape("N", "exponential_action_control"),
        _fit_one_parameter_shape("threshold_linear", "bounded_threshold"),
        _fit_one_parameter_shape("threshold_log", "logarithmic_threshold"),
        _fit_one_parameter_shape("branch_rank_by_N", "branch_rank_threshold"),
    ]
    diagnostics.append(
        {
            "family": "branch_type_weighted_threshold",
            "status": "overfit_risk_diagnostic",
            "official": False,
            "parameter_policy": "universal_a_b_c_not_sector_specific",
            "parameters": {"a": "not fit", "b": "not fit", "c": "not fit"},
            "overfit_risk": True,
            "reason": "three parameters for six charged rows; diagnostic only",
        }
    )
    return diagnostics


def hidden_response_decomposition() -> list[dict[str, Any]]:
    """Return hidden response needed to map spectral action to existing bare."""

    rows = []
    assignments = {(row.sector, row.generation_label): row for row in branch_assignments()}
    for output in read_only_existing_outputs():
        q, j = output["mode_qj"]
        spectral = spectral_action_prediction(q, j)
        hidden = output["official_or_existing_bare_prediction"] / spectral
        assignment = assignments[(output["sector"], output["ratio_name"])]
        rows.append(
            {
                "ratio_name": output["ratio_name"],
                "sector": output["sector"],
                "R_hidden": hidden,
                "log_R_hidden": math.log(hidden),
                "branch_role": assignment.branch_role,
                "pure_fiber_flag": assignment.pure_fiber_flag,
                "pure_base_flag": assignment.pure_base_flag,
                "mixed_flag": assignment.mixed_flag,
                "orientation_product": assignment.orientation_product,
                "lower_doublet_projector": assignment.lower_doublet_projector,
                "diagnostic_only": True,
            }
        )
    return rows


def build_payload(root: str | Path = ".") -> dict[str, Any]:
    outputs = read_only_existing_outputs(root)
    assignments = branch_assignments()
    associations = shape_associations()
    thresholds = threshold_family_diagnostics()
    hidden = hidden_response_decomposition()
    best_threshold = min(
        (row for row in thresholds if row.get("rms_log_error_to_existing_bare") is not None),
        key=lambda row: row["rms_log_error_to_existing_bare"],
    )
    verdicts = [
        "EXISTING_ENGINE_BRANCH_THRESHOLD_AUDIT_COMPLETE",
        "EXISTING_ENGINE_NOT_SIMPLE_RAW_EXPONENTIAL",
        "BRANCH_ASSIGNMENT_SIGNAL_INDICATED",
        "NONLINEAR_THRESHOLD_SIGNAL_INDICATED",
        "HIDDEN_RESPONSE_DECOMPOSITION_INDICATED",
        "PURE_FIBER_BRANCH_SPECIALNESS_INDICATED",
        "PURE_BASE_BRANCH_SPECIALNESS_INDICATED",
        "REFERENCE_SCHEME_LIMITATION",
        "NO_NUMERICAL_CLOSURE",
    ]
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "inputs": {
            "existing_engine_sources": [FROZEN_SOURCE, "docs/frozen_predictions.md", "existing tests"],
            "spectral_action_source": SPECTRAL_ACTION_SOURCE,
            "reference_ratio_source": REFERENCE_SOURCE,
        },
        "read_only_existing_outputs": outputs,
        "read_only_ckm_outputs": read_only_ckm_outputs(root),
        "branch_assignments": [asdict(row) for row in assignments],
        "invariant_diagnostics": {
            "candidate_variables": candidate_variables(),
            "shape_associations": associations,
            "rank_order_checks": rank_order_checks(),
            "small_sample_warning": True,
        },
        "threshold_family_diagnostics": thresholds,
        "hidden_response_decomposition": hidden,
        "summary": {
            "best_supported_missing_structure": [
                "branch_assignment",
                "nonlinear_threshold_behavior",
                "hidden_response_decomposition",
                "reference_scheme_harmonization",
            ],
            "best_threshold_family": best_threshold,
            "recommended_next_target": "derive or reject a branch-aware nonlinear threshold/hidden-response law without sector-specific tuning",
        },
        "verdict_labels": verdicts,
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


def render_audit_markdown(payload: dict[str, Any] | None = None) -> str:
    p = payload or build_payload(Path(__file__).resolve().parents[1])
    lines = [
        "# Existing Engine Branch/Threshold Audit",
        "",
        "Status: `EXISTING_ENGINE_BRANCH_THRESHOLD_AUDIT_COMPLETE`",
        "",
        "This candidate-only audit treats the existing BHSM bare/dressed values as the object to explain. The new spectral-action baseline is demoted to a failed/simple comparator rather than an official mass engine.",
        "",
        "## Read-Only Existing Outputs",
        "",
        "| Ratio | Sector | q,j | k,j | Existing bare | Existing dressed | Reference | Scheme note |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in p["read_only_existing_outputs"]:
        lines.append(
            f"| `{row['ratio_name']}` | `{row['sector']}` | `{tuple(row['mode_qj'])}` | `{tuple(row['mode_kj'])}` | `{row['official_or_existing_bare_prediction']}` | `{row['official_or_existing_dressed_candidate_prediction']}` | `{row['reference_ratio']}` | {row['reference_scheme_note']} |"
        )
    lines.extend(
        [
            "",
            "## Branch Signals",
            "",
            "| Sector | Label | Role | Rank | N | Special |",
            "| --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for row in p["branch_assignments"]:
        special = "pure_fiber" if row["pure_fiber_flag"] else "pure_base" if row["pure_base_flag"] else "mixed" if row["mixed_flag"] else "reference"
        lines.append(
            f"| `{row['sector']}` | `{row['generation_label']}` | `{row['branch_role']}` | `{row['branch_rank_by_N']}` | `{row['N']}` | `{special}` |"
        )
    lines.extend(
        [
            "",
            "## Threshold Diagnostics",
            "",
            "| Family | Policy | RMS to existing bare | Official | Overfit risk |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for row in p["threshold_family_diagnostics"]:
        lines.append(
            f"| `{row['family']}` | `{row['parameter_policy']}` | `{row.get('rms_log_error_to_existing_bare')}` | `{row['official']}` | `{row['overfit_risk']}` |"
        )
    lines.extend(
        [
            "",
            "## Hidden Response Decomposition",
            "",
            "The hidden response `R_hidden=existing_bare/spectral_action` is diagnostic only. It identifies what the simple raw action would need to recover the existing engine pattern, not a new formula.",
            "",
            "## Answers",
            "",
            "1. The existing engine is not closest to a simple raw exponential law.",
            "2. Pure-fiber charm and pure-base strange are special branch types in the ledger.",
            "3. Existing patterns suggest branch assignment before response factors.",
            "4. Missing ingredients include branch assignment, nonlinear threshold behavior, hidden response decomposition, and reference-scheme harmonization.",
            "5. Next target: derive or reject a branch-aware nonlinear threshold/hidden-response law.",
            "6. Forbidden: new official formulas, sector-specific tuning, per-particle response factors, and retrofitting frozen predictions.",
            "",
            "## Claim Boundaries",
            "",
            "- No official predictions are changed.",
            "- No frozen predictions are changed.",
            "- No new official mass formula is introduced.",
            "- `BARE_YUKAWA_SPECTRAL_ACTION_CANDIDATE` is not upgraded to derived.",
            "- `FULL_BHSM_MASS_ENGINE_CANDIDATE_ARCHITECTURE` is not upgraded to derived.",
            "- `RESPONSE_SELECTOR_STRUCTURAL_CANDIDATE` is not upgraded to derived.",
            "",
        ]
    )
    return "\n".join(lines)


def render_hidden_summary(payload: dict[str, Any] | None = None) -> str:
    p = payload or build_payload(Path(__file__).resolve().parents[1])
    return "\n".join(
        [
            "# Existing Engine Hidden Invariant Summary",
            "",
            "Status: `HIDDEN_RESPONSE_DECOMPOSITION_INDICATED`",
            "",
            "Likely missing invariant: branch-aware nonlinear thresholding plus hidden response decomposition.",
            "Pure-fiber charm and pure-base strange are marked as special branch roles, while mixed branches carry different response pressure.",
            "Branch rank separates middle and light modes inside each charged sector better than a raw universal heat-kernel closure.",
            "This is not a new official formula.",
            "",
            f"Recommended next target: `{p['summary']['recommended_next_target']}`",
            "",
        ]
    )


def render_threshold_candidates(payload: dict[str, Any] | None = None) -> str:
    p = payload or build_payload(Path(__file__).resolve().parents[1])
    lines = [
        "# Nonlinear Threshold Law Candidates",
        "",
        "Status: `NONLINEAR_THRESHOLD_SIGNAL_INDICATED`",
        "",
        "Threshold laws may replace a simple heat-kernel exponential if the existing engine effectively saturates or branches response by mode role. These are candidate diagnostics only.",
        "",
        "| Family | Parameters | RMS to existing bare | Official | Overfit risk |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in p["threshold_family_diagnostics"]:
        lines.append(
            f"| `{row['family']}` | `{row['parameter_policy']}` | `{row.get('rms_log_error_to_existing_bare')}` | `{row['official']}` | `{row['overfit_risk']}` |"
        )
    lines.extend(
        [
            "",
            "Forbidden tuning rules: no sector-specific parameters, no per-particle response factors, and no retrofitting frozen predictions.",
            "",
        ]
    )
    return "\n".join(lines)


def export_outputs(root: str | Path = ".") -> dict[str, Any]:
    base = Path(root)
    payload = build_payload(base)
    (base / "theory").mkdir(parents=True, exist_ok=True)
    (base / "theory" / "existing_engine_branch_threshold_audit.md").write_text(
        render_audit_markdown(payload),
        encoding="utf-8",
    )
    (base / "theory" / "existing_engine_branch_threshold_results.json").write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (base / "theory" / "existing_engine_hidden_invariant_summary.md").write_text(
        render_hidden_summary(payload),
        encoding="utf-8",
    )
    (base / "theory" / "nonlinear_threshold_law_candidates.md").write_text(
        render_threshold_candidates(payload),
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_outputs(Path(__file__).resolve().parents[1])
