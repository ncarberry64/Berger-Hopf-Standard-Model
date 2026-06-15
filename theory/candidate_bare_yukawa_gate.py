"""Candidate-only bare Yukawa numerical closure gate.

This module is deliberately placed under ``theory/`` so it is not mistaken for
official BHSM prediction logic. It scans one universal parameter set for the
candidate bare spectral action and writes audit artifacts.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


BRANCH = "bhsm-bare-yukawa-numerical-closure-gate"
STATUS = "candidate_only"
PARAMETER_POLICY = "single_universal_parameter_set"

VERDICTS = {
    "BARE_YUKAWA_NUMERICAL_GATE_TIER_A_STRONG",
    "BARE_YUKAWA_NUMERICAL_GATE_TIER_B_PLAUSIBLE",
    "BARE_YUKAWA_NUMERICAL_GATE_TIER_C_ORDERING_ONLY",
    "BARE_YUKAWA_NUMERICAL_GATE_TIER_D_FAIL",
}

CLAIM_LABELS = (
    "BARE_YUKAWA_NUMERICAL_CLOSURE_GATE_CANDIDATE",
    "UNIVERSAL_BARE_YUKAWA_PARAMETER_SCAN_CANDIDATE",
    "BARE_YUKAWA_ORDERING_GATE",
    "BARE_YUKAWA_LOG_SHAPE_GATE",
    "NO_SECTOR_SPECIFIC_TUNING_GUARDRAIL",
    "QUARK_RATIO_SCHEME_SENSITIVITY_GUARDRAIL",
)


@dataclass(frozen=True)
class BareYukawaParameters:
    """Universal candidate bare Yukawa parameters."""

    epsilon: float
    tau0: float
    beta_eff: float
    xi: float


@dataclass(frozen=True)
class ModeRatio:
    """One charged-sector ratio row."""

    sector: str
    label: str
    q: int
    j: int
    reference: float
    reference_label: str
    scheme_sensitive: bool


@dataclass(frozen=True)
class PredictionRow:
    """One predicted/reference comparison row."""

    sector: str
    label: str
    q: int
    j: int
    predicted: float
    reference: float
    log_error: float
    absolute_log_error: float
    response_factor: float
    scheme_sensitive: bool


def lambda_hat(q: int, j: int, epsilon: float) -> float:
    """Return lambda_hat=(1+epsilon)^(-2) q^2+j^2."""

    return (1.0 + epsilon) ** -2 * q * q + j * j


def fiber_fraction(q: int, j: int) -> float:
    """Return q^2/(q^2+j^2), with zero for the heavy reference."""

    denominator = q * q + j * j
    if denominator == 0:
        return 0.0
    return q * q / denominator


def S_bare(q: int, j: int, params: BareYukawaParameters) -> float:
    """Return the candidate bare spectral action."""

    if q == 0 and j == 0:
        return 0.0
    lam = lambda_hat(q, j, params.epsilon)
    return params.tau0 * (lam + params.beta_eff * lam * lam) - params.xi * fiber_fraction(q, j)


def Y_bare(q: int, j: int, params: BareYukawaParameters) -> float:
    """Return exp[-S_bare]."""

    return math.exp(-S_bare(q, j, params))


def alpha_reference() -> float:
    """Return the low-energy alpha used by prior candidate response audits."""

    return 1.0 / 137.035999084


def lepton_eta() -> float:
    """Return candidate eta_l=8 alpha/(9 pi)."""

    return 8.0 * alpha_reference() / (9.0 * math.pi)


def response_factor(sector: str, label: str, q: int, j: int, scenario: str) -> float:
    """Return candidate response factor for a named scenario."""

    if scenario == "bare_only":
        return 1.0
    if scenario != "current_candidate_responses":
        raise ValueError(f"unknown response scenario: {scenario}")
    if sector == "charged_lepton":
        return math.exp(-lepton_eta() * (q * q + j * j))
    if sector == "up" and label == "middle":
        return 0.5
    if sector == "up" and label == "light":
        return 1.0 / math.sqrt(3.0)
    return 1.0


def charged_ratio_rows() -> tuple[ModeRatio, ...]:
    """Return candidate gate comparison rows.

    References are taken from the existing BHSM prediction ledger values used
    in the repository. Quark rows retain scheme-sensitive labels.
    """

    return (
        ModeRatio("charged_lepton", "middle", 1, 2, 0.05946353426831603, "repo_prediction_ledger", False),
        ModeRatio("charged_lepton", "light", 3, 3, 0.0002875853753250115, "repo_prediction_ledger", False),
        ModeRatio("up", "middle", 6, 0, 0.007354218541895883, "repo_prediction_ledger_scheme_sensitive", True),
        ModeRatio("up", "light", 8, 1, 1.2507962244484336e-05, "repo_prediction_ledger_scheme_sensitive", True),
        ModeRatio("down", "middle", 0, 3, 0.022344497607655504, "repo_prediction_ledger_scheme_sensitive", True),
        ModeRatio("down", "light", 4, 2, 0.0011172248803827751, "repo_prediction_ledger_scheme_sensitive", True),
    )


def predict_row(row: ModeRatio, params: BareYukawaParameters, scenario: str) -> PredictionRow:
    """Return one prediction row."""

    z = response_factor(row.sector, row.label, row.q, row.j, scenario)
    predicted = Y_bare(row.q, row.j, params) * z
    log_error = math.log(predicted / row.reference)
    return PredictionRow(
        sector=row.sector,
        label=row.label,
        q=row.q,
        j=row.j,
        predicted=predicted,
        reference=row.reference,
        log_error=log_error,
        absolute_log_error=abs(log_error),
        response_factor=z,
        scheme_sensitive=row.scheme_sensitive,
    )


def score_rows(rows: tuple[PredictionRow, ...]) -> dict[str, float | bool]:
    """Return log residual score and ordering checks."""

    errors = [row.log_error for row in rows]
    by_sector = {(row.sector, row.label): row.predicted for row in rows}
    charged = by_sector[("charged_lepton", "middle")] > by_sector[("charged_lepton", "light")]
    up = by_sector[("up", "middle")] > by_sector[("up", "light")]
    down = by_sector[("down", "middle")] > by_sector[("down", "light")]
    return {
        "rms_log_error": math.sqrt(sum(error * error for error in errors) / len(errors)),
        "max_abs_log_error": max(abs(error) for error in errors),
        "charged_lepton_ordering_pass": charged,
        "up_ordering_pass": up,
        "down_ordering_pass": down,
        "all_charged_ordering_pass": charged and up and down,
        "ordering_pass": charged and up and down,
    }


def parameter_grid() -> tuple[BareYukawaParameters, ...]:
    """Return a broad finite candidate grid."""

    epsilons = [0.0, 0.01, 0.02, 0.03, 0.04, 0.05]
    tau0s = [0.0, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.5, 0.75, 1.0]
    betas = [0.0, 0.001, 0.0025, 0.005, 0.01, 0.02, 0.05]
    xis = [round(0.1 * index, 10) for index in range(0, 21)]
    return tuple(
        BareYukawaParameters(epsilon, tau0, beta, xi)
        for epsilon in epsilons
        for tau0 in tau0s
        for beta in betas
        for xi in xis
    )


def evaluate_parameters(params: BareYukawaParameters, scenario: str) -> dict[str, Any]:
    """Return score for one universal parameter set."""

    rows = tuple(predict_row(row, params, scenario) for row in charged_ratio_rows())
    return {
        "parameters": params,
        "rows": rows,
        **score_rows(rows),
    }


def scan_universal_parameters(scenario: str) -> dict[str, Any]:
    """Return the best universal-parameter scan row for a scenario."""

    best: dict[str, Any] | None = None
    for params in parameter_grid():
        result = evaluate_parameters(params, scenario)
        if best is None or (result["rms_log_error"], result["max_abs_log_error"]) < (
            best["rms_log_error"],
            best["max_abs_log_error"],
        ):
            best = result
    assert best is not None
    return best


def verdict_from_score(result: dict[str, Any]) -> str:
    """Return candidate numerical-gate verdict."""

    if not result["ordering_pass"]:
        return "BARE_YUKAWA_NUMERICAL_GATE_TIER_D_FAIL"
    rms = float(result["rms_log_error"])
    max_abs = float(result["max_abs_log_error"])
    if rms <= 0.25 and max_abs <= 0.6:
        return "BARE_YUKAWA_NUMERICAL_GATE_TIER_A_STRONG"
    if rms <= 1.25 and max_abs <= 2.5:
        return "BARE_YUKAWA_NUMERICAL_GATE_TIER_B_PLAUSIBLE"
    return "BARE_YUKAWA_NUMERICAL_GATE_TIER_C_ORDERING_ONLY"


def _sector_results(rows: tuple[PredictionRow, ...]) -> dict[str, dict[str, Any]]:
    sectors: dict[str, dict[str, Any]] = {}
    for sector in ("charged_lepton", "up", "down"):
        sector_rows = [row for row in rows if row.sector == sector]
        sector_score: dict[str, float | bool] = {}
        if len(sector_rows) == 2:
            errors = [row.log_error for row in sector_rows]
            middle = next(row for row in sector_rows if row.label == "middle")
            light = next(row for row in sector_rows if row.label == "light")
            sector_score = {
                "rms_log_error": math.sqrt(sum(error * error for error in errors) / len(errors)),
                "max_abs_log_error": max(abs(error) for error in errors),
                "ordering_pass": middle.predicted > light.predicted,
            }
        sectors[sector] = {
            "scheme_sensitive": any(row.scheme_sensitive for row in sector_rows),
            "rows": [asdict(row) for row in sector_rows],
            **sector_score,
        }
    return sectors


def _jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def build_gate_payload() -> dict[str, Any]:
    """Return the full candidate numerical-gate payload."""

    scans = {
        "bare_only": scan_universal_parameters("bare_only"),
        "current_candidate_responses": scan_universal_parameters("current_candidate_responses"),
    }
    main_scenario = "current_candidate_responses"
    main = scans[main_scenario]
    verdict = verdict_from_score(main)
    rows = main["rows"]
    return {
        "status": STATUS,
        "verdict": verdict,
        "allowed_verdicts": sorted(VERDICTS),
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "claim_labels": CLAIM_LABELS,
        "main_scan": {
            "response_scenario": main_scenario,
            "parameter_policy": PARAMETER_POLICY,
            "best_parameters": asdict(main["parameters"]),
            "rms_log_error": main["rms_log_error"],
            "max_abs_log_error": main["max_abs_log_error"],
            "ordering_pass": main["ordering_pass"],
            "charged_lepton_ordering_pass": main["charged_lepton_ordering_pass"],
            "up_ordering_pass": main["up_ordering_pass"],
            "down_ordering_pass": main["down_ordering_pass"],
            "all_charged_ordering_pass": main["all_charged_ordering_pass"],
            "grid_size": len(parameter_grid()),
        },
        "sector_results": _sector_results(rows),
        "scenario_comparison": {
            scenario: {
                "best_parameters": asdict(result["parameters"]),
                "rms_log_error": result["rms_log_error"],
                "max_abs_log_error": result["max_abs_log_error"],
                "ordering_pass": result["ordering_pass"],
                "verdict": verdict_from_score(result),
            }
            for scenario, result in scans.items()
        },
        "forbidden_sector_fit_control": {
            "implemented": False,
            "status": "FORBIDDEN_SECTOR_FIT_CONTROL",
            "used_as_evidence": False,
        },
        "parameter_guardrails": {
            "uses_single_universal_parameter_set": True,
            "uses_sector_specific_tau": False,
            "uses_sector_specific_xi": False,
            "uses_sector_specific_beta": False,
            "uses_sector_specific_epsilon": False,
        },
        "references": [
            asdict(row) for row in charged_ratio_rows()
        ],
        "notes": [
            "candidate-only",
            "quark ratios are scheme-sensitive where applicable",
            "no frozen predictions changed",
            "no official prediction values are updated",
            "the official dressed candidate rule remains unchanged",
        ],
    }


def render_markdown(payload: dict[str, Any] | None = None) -> str:
    """Render the numerical closure gate report."""

    p = payload or build_gate_payload()
    best = p["main_scan"]["best_parameters"]
    lines = [
        "# Bare Yukawa Numerical Closure Gate",
        "",
        "Status: `BARE_YUKAWA_NUMERICAL_CLOSURE_GATE_CANDIDATE`",
        "",
        "This candidate-only audit tests whether the bare Yukawa spectral-action mass engine can support the charged-fermion hierarchy with one universal parameter set. It does not create official predictions and does not modify frozen outputs.",
        "",
        "## Formula",
        "",
        "```text",
        "lambda_hat(q,j) = (1 + epsilon)^(-2) * q^2 + j^2",
        "fiber_fraction(q,j) = q^2/(q^2+j^2), with fiber_fraction(0,0)=0",
        "S_bare(q,j) = tau0 * [lambda_hat + beta_eff * lambda_hat^2] - xi * fiber_fraction",
        "S_bare(0,0)=0",
        "Y_bare(q,j)=exp[-S_bare(q,j)]",
        "```",
        "",
        "## Parameter Policy",
        "",
        "`NO_SECTOR_SPECIFIC_TUNING_GUARDRAIL`: the main scan uses one shared set `(epsilon,tau0,beta_eff,xi)` across charged leptons, up quarks, and down quarks.",
        "",
        "## Response Scenarios",
        "",
        "- `bare_only`: `Z_response=1` for all modes.",
        "- `current_candidate_responses`: charged-lepton `eta_l=8 alpha/(9 pi)`, middle-up `1/2`, light-up `1/sqrt(3)`, down-sector `1`.",
        "",
        "## Verdict",
        "",
        f"Verdict: `{p['verdict']}`",
        f"Response scenario: `{p['main_scan']['response_scenario']}`",
        f"Best parameters: `epsilon={best['epsilon']}`, `tau0={best['tau0']}`, `beta_eff={best['beta_eff']}`, `xi={best['xi']}`",
        f"RMS log error: `{p['main_scan']['rms_log_error']}`",
        f"Max absolute log error: `{p['main_scan']['max_abs_log_error']}`",
        f"Ordering pass: `{p['main_scan']['ordering_pass']}`",
        "",
        "## Sector Results",
        "",
        "| Sector | Row | q,j | predicted | reference | log error | response | scheme-sensitive |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for sector, sector_payload in p["sector_results"].items():
        for row in sector_payload["rows"]:
            lines.append(
                f"| `{sector}` | `{row['label']}` | `({row['q']},{row['j']})` | `{row['predicted']}` | `{row['reference']}` | `{row['log_error']}` | `{row['response_factor']}` | `{row['scheme_sensitive']}` |"
            )
    lines.extend(
        [
            "",
            "## Scheme Sensitivity",
            "",
            "`QUARK_RATIO_SCHEME_SENSITIVITY_GUARDRAIL`: quark references are the existing repository comparison values and remain scheme-sensitive. This gate reports log-shape and ordering; it does not provide precision QCD closure.",
            "",
            "## Failure Modes",
            "",
            "- A weak verdict means the universal action orders the hierarchy but does not numerically close it.",
            "- A forbidden sector fit would use separate parameters per sector and is not evidence.",
            "- Candidate response factors remain non-official and are not interchangeable.",
            "",
            "## Claim Boundaries",
            "",
            "- `BARE_YUKAWA_SPECTRAL_ACTION_CANDIDATE` is not upgraded to derived.",
            "- `FULL_BHSM_MASS_ENGINE_CANDIDATE_ARCHITECTURE` is not upgraded to derived.",
            "- Frozen predictions and official dressed-candidate rules are unchanged.",
            "",
        ]
    )
    return "\n".join(lines)


def render_summary(payload: dict[str, Any] | None = None) -> str:
    """Render the full-BHSM numerical gate summary."""

    p = payload or build_gate_payload()
    return "\n".join(
        [
            "# Full BHSM Numerical Gate Summary",
            "",
            "The Full BHSM candidate architecture is now structurally repo-audited.",
            "This sprint tests the first numerical closure gate for the bare Yukawa mass engine.",
            "The gate does not create official predictions.",
            "The gate does not change frozen outputs.",
            "The gate reports whether a universal geometric parameter set can reproduce or at least order the charged-sector hierarchy.",
            "",
            f"Verdict: `{p['verdict']}`",
            f"Ordering pass: `{p['main_scan']['ordering_pass']}`",
            f"RMS log error: `{p['main_scan']['rms_log_error']}`",
            f"Max absolute log error: `{p['main_scan']['max_abs_log_error']}`",
            "",
            "Status labels:",
            "",
            *[f"- `{label}`" for label in p["claim_labels"]],
            "",
        ]
    )


def export_gate_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Write gate Markdown and JSON outputs."""

    base = Path(root)
    payload = build_gate_payload()
    (base / "theory").mkdir(parents=True, exist_ok=True)
    (base / "theory" / "bare_yukawa_numerical_closure_gate.md").write_text(
        render_markdown(payload),
        encoding="utf-8",
    )
    (base / "theory" / "bare_yukawa_numerical_closure_results.json").write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (base / "theory" / "full_bhsm_numerical_gate_summary.md").write_text(
        render_summary(payload),
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_gate_outputs(Path(__file__).resolve().parents[1])
