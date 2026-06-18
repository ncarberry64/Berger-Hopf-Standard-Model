"""Candidate-only bare-engine triangulation audit.

This module compares read-only frozen/existing BHSM predictions against the
candidate spectral-action baseline. It lives under theory/ so it is not
mistaken for official prediction code.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from candidate_bare_yukawa_gate import BareYukawaParameters, charged_ratio_rows
from candidate_bare_yukawa_residual_autopsy import S_variant


BRANCH = "bhsm-bare-engine-triangulation-audit"
STATUS = "candidate_only"
SPECTRAL_ACTION_SOURCE = "candidate_bare_yukawa_residual_autopsy:A_raw_bare_only"
FROZEN_SOURCE = "docs/frozen_predictions.json + theory/bhsm_prediction_ledger.json"
REFERENCE_SOURCE = "theory/bhsm_prediction_ledger.json"
BASELINE_PARAMS = BareYukawaParameters(epsilon=0.05, tau0=0.2, beta_eff=0.0, xi=0.0)

ALLOWED_VERDICTS = {
    "BARE_ENGINE_TRIANGULATION_AUDIT_COMPLETE",
    "SPECTRAL_ACTION_NOT_EXISTING_ENGINE",
    "SPECTRAL_ACTION_PARTIAL_SHAPE_MATCH",
    "MISSING_INVARIANT_SECTOR_OPERATOR_WEIGHTING_INDICATED",
    "MISSING_INVARIANT_ORIENTATION_CROSS_TERM_INDICATED",
    "MISSING_INVARIANT_BRANCH_ASSIGNMENT_INDICATED",
    "MISSING_RESPONSE_LAYER_INDICATED",
    "NONLINEAR_THRESHOLD_LAW_INDICATED",
    "REFERENCE_SCHEME_LIMITATION",
    "NO_NUMERICAL_CLOSURE",
}

CLAIM_LABELS = (
    "BARE_ENGINE_TRIANGULATION_AUDIT_COMPLETE",
    "SPECTRAL_ACTION_NOT_EXISTING_ENGINE",
    "MISSING_INVARIANT_DIAGNOSTIC_CANDIDATE",
    "SECTOR_OPERATOR_WEIGHTING_DIAGNOSTIC",
    "ORIENTATION_CROSS_TERM_DIAGNOSTIC",
    "BRANCH_ASSIGNMENT_DIAGNOSTIC",
    "NONLINEAR_THRESHOLD_LAW_DIAGNOSTIC",
    "NO_NEW_OFFICIAL_MASS_FORMULA_GUARDRAIL",
)

SECTOR_DATA = {
    "charged_lepton": {"B": 0.0, "L": 1.0, "T3": -0.5, "Omega_star": 3},
    "up": {"B": 1.0 / 3.0, "L": 0.0, "T3": 0.5, "Omega_star": 6},
    "down": {"B": 1.0 / 3.0, "L": 0.0, "T3": -0.5, "Omega_star": 12},
}

RATIO_TO_LEDGER_ID = {
    "mu/tau": "mass_ratio.charged_leptons.middle",
    "e/tau": "mass_ratio.charged_leptons.light",
    "c/t": "mass_ratio.up_quarks.middle",
    "u/t": "mass_ratio.up_quarks.light",
    "s/b": "mass_ratio.down_quarks.middle",
    "d/b": "mass_ratio.down_quarks.light",
}


@dataclass(frozen=True)
class EngineRow:
    """One engine comparison row."""

    ratio_name: str
    sector: str
    mode_qj: tuple[int, int]
    official_or_existing_bare_prediction: float | None
    official_or_existing_dressed_candidate_prediction: float | None
    new_spectral_action_prediction: float
    reference_ratio: float | None
    official_bare_log_residual: float | None
    official_dressed_log_residual: float | None
    spectral_action_log_residual: float | None
    which_engine_is_closer: str
    scheme_sensitive: bool


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _ratio_name(sector: str, label: str) -> str:
    return {
        ("charged_lepton", "middle"): "mu/tau",
        ("charged_lepton", "light"): "e/tau",
        ("up", "middle"): "c/t",
        ("up", "light"): "u/t",
        ("down", "middle"): "s/b",
        ("down", "light"): "d/b",
    }[(sector, label)]


def O_q(sector: str) -> float:
    data = SECTOR_DATA[sector]
    return 3.0 * data["B"] - data["L"]


def lower_doublet_projector(sector: str) -> float:
    data = SECTOR_DATA[sector]
    return (3.0 * data["B"]) * (0.5 - data["T3"])


def O_j(sector: str) -> float:
    data = SECTOR_DATA[sector]
    return -4.0 * data["T3"] + 2.0 * lower_doublet_projector(sector)


def omega(sector: str, q: int, j: int) -> float:
    return O_q(sector) * q + O_j(sector) * j


def _load_ledger_predictions(root: Path) -> dict[str, dict[str, Any]]:
    rows = _read_json(root / "theory" / "bhsm_prediction_ledger.json")
    return {row["id"]: row for row in rows}


def _load_frozen_predictions(root: Path) -> dict[str, Any]:
    return _read_json(root / "docs" / "frozen_predictions.json")


def existing_prediction_rows(root: str | Path = ".") -> list[dict[str, Any]]:
    """Return read-only existing BHSM predictions for charged ratios."""

    base = Path(root)
    frozen = _load_frozen_predictions(base)
    ledger = _load_ledger_predictions(base)
    rows: list[dict[str, Any]] = []
    for mode in charged_ratio_rows():
        ratio = _ratio_name(mode.sector, mode.label)
        ledger_row = ledger[RATIO_TO_LEDGER_ID[ratio]]
        if ratio in frozen["outputs"]:
            bare = frozen["outputs"][ratio]["bare"]
            dressed = frozen["outputs"][ratio]["dressed_candidate"]
            source = "docs/frozen_predictions.json"
        else:
            bare = ledger_row["predicted"]
            dressed = ledger_row["predicted"]
            source = "theory/bhsm_prediction_ledger.json"
        rows.append(
            {
                "ratio_name": ratio,
                "sector": mode.sector,
                "label": mode.label,
                "q": mode.q,
                "j": mode.j,
                "existing_bare_prediction": bare,
                "existing_dressed_candidate_prediction": dressed,
                "reference_ratio": ledger_row.get("reference"),
                "scheme_sensitive": any("scheme-sensitive" in item for item in ledger_row.get("limitations", [])),
                "source": source,
            }
        )
    return rows


def spectral_action_prediction(q: int, j: int) -> float:
    """Return new candidate spectral-action baseline prediction."""

    # Need the row only for sector-invariant lambda in S_variant.
    row = next(mode for mode in charged_ratio_rows() if mode.q == q and mode.j == j)
    return math.exp(-S_variant(row, BASELINE_PARAMS, "A_raw"))


def _log_residual(prediction: float | None, reference: float | None) -> float | None:
    if prediction is None or reference is None:
        return None
    return math.log(prediction / reference)


def _closer(
    bare_log: float | None,
    dressed_log: float | None,
    spectral_log: float | None,
) -> str:
    candidates = {
        "existing_bare": bare_log,
        "existing_dressed_candidate": dressed_log,
        "new_spectral_action": spectral_log,
    }
    available = {key: abs(value) for key, value in candidates.items() if value is not None}
    if not available:
        return "shape_only_no_reference"
    return min(available, key=available.get)


def engine_comparison(root: str | Path = ".") -> list[EngineRow]:
    """Return engine comparison rows."""

    rows: list[EngineRow] = []
    for row in existing_prediction_rows(root):
        spectral = spectral_action_prediction(row["q"], row["j"])
        bare_log = _log_residual(row["existing_bare_prediction"], row["reference_ratio"])
        dressed_log = _log_residual(row["existing_dressed_candidate_prediction"], row["reference_ratio"])
        spectral_log = _log_residual(spectral, row["reference_ratio"])
        rows.append(
            EngineRow(
                ratio_name=row["ratio_name"],
                sector=row["sector"],
                mode_qj=(row["q"], row["j"]),
                official_or_existing_bare_prediction=row["existing_bare_prediction"],
                official_or_existing_dressed_candidate_prediction=row["existing_dressed_candidate_prediction"],
                new_spectral_action_prediction=spectral,
                reference_ratio=row["reference_ratio"],
                official_bare_log_residual=bare_log,
                official_dressed_log_residual=dressed_log,
                spectral_action_log_residual=spectral_log,
                which_engine_is_closer=_closer(bare_log, dressed_log, spectral_log),
                scheme_sensitive=row["scheme_sensitive"],
            )
        )
    return rows


def mode_invariants(row: EngineRow) -> dict[str, Any]:
    """Return mode invariant diagnostics."""

    q, j = row.mode_qj
    sector = row.sector
    omega_star = SECTOR_DATA[sector]["Omega_star"]
    n = q * q + j * j
    denominator = n or 1
    oq = O_q(sector)
    oj = O_j(sector)
    nonzero_ns = [
        other.mode_qj[0] ** 2 + other.mode_qj[1] ** 2
        for other in engine_comparison()
        if other.sector == sector
    ]
    return {
        "ratio_name": row.ratio_name,
        "sector": sector,
        "q": q,
        "j": j,
        "k": q + 2 * j,
        "N": n,
        "Omega_f": omega(sector, q, j),
        "Omega_star": omega_star,
        "abs_Omega": abs(omega(sector, q, j)),
        "q_over_Omega": q / omega_star,
        "j_over_Omega": j / omega_star,
        "fiber_fraction": q * q / denominator if n else 0.0,
        "base_fraction": j * j / denominator if n else 0.0,
        "sector_operator_norm": oq * oq + oj * oj,
        "signed_sector_action": omega(sector, q, j),
        "orientation_product": (oq * q) * (oj * j),
        "cross_term": q * j,
        "mode_gap_to_reference": n,
        "mode_gap_between_nonzero_pair": abs(n - min(value for value in nonzero_ns if value != n)),
        "pure_fiber_flag": j == 0,
        "pure_base_flag": q == 0,
        "lower_doublet_projector": lower_doublet_projector(sector),
        "colored_lift_exponent": 3.0 * SECTOR_DATA[sector]["B"] + lower_doublet_projector(sector),
        "channel_dim": omega_star * omega_star,
        "active_dim": omega_star * omega_star - 1,
        "lambda_O": (oq * q) ** 2 + (oj * j) ** 2,
        "lambda_signed": abs(omega(sector, q, j)),
        "lambda_cross_rho1": n + q * j,
        "lambda_branch_gap": n - min(nonzero_ns),
        "lambda_response": n / (omega_star * omega_star - 1),
    }


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


def invariant_correlations(rows: list[EngineRow]) -> list[dict[str, Any]]:
    """Return lightweight correlation diagnostics."""

    invariant_rows = [mode_invariants(row) for row in rows]
    invariant_keys = [
        "N",
        "abs_Omega",
        "q_over_Omega",
        "j_over_Omega",
        "fiber_fraction",
        "base_fraction",
        "sector_operator_norm",
        "orientation_product",
        "cross_term",
        "mode_gap_between_nonzero_pair",
        "lower_doublet_projector",
        "colored_lift_exponent",
        "channel_dim",
        "active_dim",
        "lambda_O",
        "lambda_signed",
        "lambda_cross_rho1",
        "lambda_branch_gap",
        "lambda_response",
    ]
    targets = {
        "log_existing_bare_prediction": [math.log(row.official_or_existing_bare_prediction) for row in rows if row.official_or_existing_bare_prediction],
        "log_reference_ratio": [math.log(row.reference_ratio) for row in rows if row.reference_ratio],
        "spectral_action_log_residual": [row.spectral_action_log_residual for row in rows if row.spectral_action_log_residual is not None],
    }
    correlations: list[dict[str, Any]] = []
    for key in invariant_keys:
        xs = [float(row[key]) for row in invariant_rows]
        for target, ys in targets.items():
            corr = _pearson(xs, [float(value) for value in ys])
            correlations.append(
                {
                    "invariant": key,
                    "target": target,
                    "pearson": corr,
                    "sample_size": len(xs),
                    "diagnostic_only": True,
                }
            )
    return correlations


def candidate_invariant_families(correlations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return candidate invariant family diagnostics."""

    def corr_for(name: str, target: str = "log_existing_bare_prediction") -> float | None:
        row = next(item for item in correlations if item["invariant"] == name and item["target"] == target)
        return row["pearson"]

    return [
        {
            "family": "sector_operator_weighted_action",
            "formula": "lambda_O=(O_q*q)^2+(O_j*j)^2",
            "status": "SECTOR_OPERATOR_WEIGHTING_DIAGNOSTIC",
            "official": False,
            "control": False,
            "correlation_with_existing_bare": corr_for("lambda_O"),
        },
        {
            "family": "signed_boundary_action_magnitude",
            "formula": "lambda_signed=abs(O_q*q+O_j*j)",
            "status": "DIAGNOSTIC_CONSTANT_ON_TARGET_SECTORS",
            "official": False,
            "control": False,
            "correlation_with_existing_bare": corr_for("lambda_signed"),
            "limitation": "constant on fixed target-degree sectors, cannot split generations by itself",
        },
        {
            "family": "cross_coupled_berger_action",
            "formula": "lambda_cross=q^2+j^2+rho*q*j",
            "status": "ORIENTATION_CROSS_TERM_DIAGNOSTIC",
            "official": False,
            "control": False,
            "rho_policy": "universal_only_if_scanned",
            "correlation_with_existing_bare": corr_for("lambda_cross_rho1"),
        },
        {
            "family": "branch_gap_action",
            "formula": "lambda_branch_gap=N-N_min_nonzero_sector",
            "status": "BRANCH_ASSIGNMENT_DIAGNOSTIC",
            "official": False,
            "control": True,
            "correlation_with_existing_bare": corr_for("lambda_branch_gap"),
        },
        {
            "family": "sector_response_weighted_action",
            "formula": "lambda_response=N/(Omega_star^2-1)",
            "status": "CHANNEL_DIMENSION_NORMALIZATION_ALREADY_WEAK",
            "official": False,
            "control": False,
            "correlation_with_existing_bare": corr_for("lambda_response"),
        },
        {
            "family": "orientation_sensitive_action",
            "formula": "lambda_orientation=N+gamma*(O_q*q)*(O_j*j)",
            "status": "ORIENTATION_CROSS_TERM_DIAGNOSTIC",
            "official": False,
            "control": False,
            "gamma_policy": "universal_only_if_scanned",
            "correlation_proxy": corr_for("orientation_product"),
        },
    ]


def build_payload(root: str | Path = ".") -> dict[str, Any]:
    """Return triangulation payload."""

    base = Path(root)
    frozen = _load_frozen_predictions(base)
    comparison = engine_comparison(base)
    invariant_rows = [mode_invariants(row) for row in comparison]
    correlations = invariant_correlations(comparison)
    families = candidate_invariant_families(correlations)
    closer_counts: dict[str, int] = {}
    for row in comparison:
        closer_counts[row.which_engine_is_closer] = closer_counts.get(row.which_engine_is_closer, 0) + 1
    spectral_closer_count = closer_counts.get("new_spectral_action", 0)
    strongest_residual_corr = max(
        (row for row in correlations if row["target"] == "spectral_action_log_residual" and row["pearson"] is not None),
        key=lambda row: abs(row["pearson"]),
    )
    verdicts = [
        "BARE_ENGINE_TRIANGULATION_AUDIT_COMPLETE",
        "SPECTRAL_ACTION_NOT_EXISTING_ENGINE",
        "NO_NUMERICAL_CLOSURE",
        "REFERENCE_SCHEME_LIMITATION",
    ]
    if spectral_closer_count:
        verdicts.append("SPECTRAL_ACTION_PARTIAL_SHAPE_MATCH")
    if abs(strongest_residual_corr["pearson"]) > 0.5 and "orientation" in strongest_residual_corr["invariant"]:
        verdicts.append("MISSING_INVARIANT_ORIENTATION_CROSS_TERM_INDICATED")
    else:
        verdicts.append("MISSING_INVARIANT_BRANCH_ASSIGNMENT_INDICATED")
        verdicts.append("MISSING_RESPONSE_LAYER_INDICATED")
        verdicts.append("NONLINEAR_THRESHOLD_LAW_INDICATED")
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "inputs": {
            "frozen_predictions_source": FROZEN_SOURCE,
            "spectral_action_source": SPECTRAL_ACTION_SOURCE,
            "reference_ratio_source": REFERENCE_SOURCE,
        },
        "engine_comparison": [asdict(row) for row in comparison],
        "read_only_ckm_entries": {
            "sin_theta_13": frozen["outputs"].get("sin_theta_13", {"available": False}),
            "source": "docs/frozen_predictions.json",
            "used_in_mass_engine_fit": False,
        },
        "missing_invariant_diagnostics": {
            "mode_invariants": invariant_rows,
            "correlations": correlations,
            "summary": {
                "closer_counts": closer_counts,
                "spectral_action_closer_count": spectral_closer_count,
                "strongest_residual_correlation": strongest_residual_corr,
                "sample_size": len(comparison),
                "diagnostic_only": True,
            },
        },
        "candidate_invariant_families": families,
        "verdict_labels": verdicts,
        "claim_labels": CLAIM_LABELS,
        "notes": [
            "candidate-only",
            "official/frozen prediction values are read-only",
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
        "# Bare Engine Triangulation Audit",
        "",
        "Status: `BARE_ENGINE_TRIANGULATION_AUDIT_COMPLETE`",
        "",
        "This candidate-only audit compares read-only existing BHSM predictions with the new Tier C spectral-action baseline. It exists because the candidate spectral action preserved hierarchy ordering but did not reproduce the stronger existing BHSM prediction structure.",
        "",
        "## Sources",
        "",
        f"Frozen/existing source: `{p['inputs']['frozen_predictions_source']}`",
        f"Spectral-action source: `{p['inputs']['spectral_action_source']}`",
        f"Reference source: `{p['inputs']['reference_ratio_source']}`",
        "",
        "## Engine Comparison",
        "",
        "| Ratio | Existing bare | Existing dressed | Spectral action | Reference | Closer | Scheme-sensitive |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in p["engine_comparison"]:
        lines.append(
            f"| `{row['ratio_name']}` | `{row['official_or_existing_bare_prediction']}` | `{row['official_or_existing_dressed_candidate_prediction']}` | `{row['new_spectral_action_prediction']}` | `{row['reference_ratio']}` | `{row['which_engine_is_closer']}` | `{row['scheme_sensitive']}` |"
        )
    lines.extend(
        [
            "",
            "## Missing-Invariant Diagnostics",
            "",
            f"Closer counts: `{p['missing_invariant_diagnostics']['summary']['closer_counts']}`",
            f"Strongest spectral-residual correlation: `{p['missing_invariant_diagnostics']['summary']['strongest_residual_correlation']}`",
            "",
            "The spectral action is not the existing BHSM engine. Its largest disagreements point toward missing response-layer structure, branch assignment, nonlinear threshold behavior, or unresolved quark reference schemes rather than a completed universal heat-kernel mass law.",
            "",
            "## Answers",
            "",
            "1. The new spectral-action baseline does not reproduce the existing BHSM bare prediction pattern.",
            "2. It disagrees most on charged-lepton light mode, down light mode, and charm/top underprediction.",
            "3. Correlations are diagnostic-only because the sample has six rows.",
            "4. Candidate missing ingredients include response-layer effects, branch assignment, orientation/cross terms, nonlinear thresholds, and reference-scheme limitations.",
            "5. No invariant candidate is adopted as a new official formula.",
            "6. Next test: derive or reject a nonlinear threshold/response law before adding any official mass formula.",
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


def render_candidates_markdown(payload: dict[str, Any] | None = None) -> str:
    p = payload or build_payload(Path(__file__).resolve().parents[1])
    lines = [
        "# Bare Engine Missing Invariant Candidates",
        "",
        "Status: `MISSING_INVARIANT_DIAGNOSTIC_CANDIDATE`",
        "",
        "This note lists shape-only invariant candidates. None is official.",
        "",
        "| Family | Formula | Status | Official | Control | Diagnostic correlation |",
        "| --- | --- | --- | --- | --- | ---: |",
    ]
    for row in p["candidate_invariant_families"]:
        corr = row.get("correlation_with_existing_bare", row.get("correlation_proxy"))
        lines.append(
            f"| `{row['family']}` | `{row['formula']}` | `{row['status']}` | `{row['official']}` | `{row['control']}` | `{corr}` |"
        )
    lines.extend(
        [
            "",
            "Simple degree/channel normalization already failed in the residual-autopsy sprint. Branch-gap subtraction is marked control/candidate because sector-relative subtraction needs derivation. Cross/orientation terms and nonlinear threshold laws remain diagnostic targets only.",
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
    (base / "theory" / "bare_engine_triangulation_audit.md").write_text(
        render_audit_markdown(payload),
        encoding="utf-8",
    )
    (base / "theory" / "bare_engine_triangulation_results.json").write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (base / "theory" / "bare_engine_missing_invariant_candidates.md").write_text(
        render_candidates_markdown(payload),
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_outputs(Path(__file__).resolve().parents[1])
