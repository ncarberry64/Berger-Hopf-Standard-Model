"""Formula-integrity audit for the charged-lepton dressing candidate.

This module checks whether the charged-lepton precision sprint documented the
same exponent that the code implemented.  It also compares a fixed list of
candidate mode norms by fitting one eta parameter from mu/tau and holding out
e/tau.

No candidate produced here is official.  Frozen BHSM outputs are not modified.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import exp, isclose, isfinite, log, sqrt
from pathlib import Path
from typing import Any, Callable

from bhsm_v1 import compare_bhsm_v1_branches
from charged_lepton_precision_closure import (
    CANDIDATE_NOT_OFFICIAL,
    LEPTON_MODES,
    baseline_residuals,
    candidate_dressing_rows,
    frozen_sanity_payload,
    mode_norm,
)
from mode_selection import hopf_charge


FORMULA_CONSISTENT = "FORMULA_CONSISTENT"
FORMULA_MISMATCH_FIXED = "FORMULA_MISMATCH_FIXED"
FORMULA_MISMATCH_REMAINS = "FORMULA_MISMATCH_REMAINS"
LEPTON_DRESSING_CANDIDATE_REJECTED = "LEPTON_DRESSING_CANDIDATE_REJECTED"
LEPTON_DRESSING_CANDIDATE_RESCOPED = "LEPTON_DRESSING_CANDIDATE_RESCOPED"

ALLOWED_CLASSIFICATIONS = (
    FORMULA_CONSISTENT,
    FORMULA_MISMATCH_FIXED,
    FORMULA_MISMATCH_REMAINS,
    LEPTON_DRESSING_CANDIDATE_REJECTED,
    LEPTON_DRESSING_CANDIDATE_RESCOPED,
)

ORIGINALLY_REPORTED_FORMULA = "Z_l(k,j)=exp[-eta_l*(q^2+j^2)]"
IMPLEMENTED_FORMULA = "Z_l(k,j)=exp[-eta_l*((k-2j)^2+j^2)]"
IMPLEMENTED_Q_DEFINITION = "q = k - 2j"


@dataclass(frozen=True)
class ModeExponentRow:
    """Exponent data for one charged-lepton mode."""

    rank: str
    particle_ratio: str
    mode: tuple[int, int]
    k: int
    j: int
    q_hopf: int
    implemented_exponent: float
    implemented_expression: str
    tau_effective_exponent: float


@dataclass(frozen=True)
class CandidateNormResult:
    """One candidate norm comparison row."""

    norm_name: str
    formula: str
    mu_exponent: float
    electron_exponent: float
    eta_from_mu_tau: float
    mu_dressed_prediction: float
    mu_relative_error: float
    electron_held_out_prediction: float
    electron_relative_error: float
    improves_electron: bool
    included: bool
    structural_note: str
    official: bool = False


@dataclass(frozen=True)
class FormulaIntegrityReport:
    """Structured formula-integrity report."""

    classification: str
    candidate_status: str
    documentation_and_code_match: bool
    prior_candidate_result_remains_valid: bool
    official_outputs_changed: bool
    official_lepton_ratios_changed: bool
    lepton_precision_blocker_closed: bool
    originally_reported_formula: str
    actual_implemented_formula: str
    q_definition: str
    mode_exponents: tuple[ModeExponentRow, ...]
    candidate_norms: tuple[CandidateNormResult, ...]
    best_numerical_candidate: str
    best_structurally_motivated_candidate: str
    limitations: tuple[str, ...]


def _baseline_by_rank() -> dict[str, Any]:
    return {row.rank: row for row in baseline_residuals()}


def implemented_mode_exponents() -> tuple[ModeExponentRow, ...]:
    """Return the exact exponent currently used by the precision candidate."""

    rows = []
    for rank, ratio in (("middle", "mu/tau"), ("light", "e/tau")):
        k, j = LEPTON_MODES[rank]
        q = hopf_charge(k, j)
        rows.append(
            ModeExponentRow(
                rank=rank,
                particle_ratio=ratio,
                mode=(k, j),
                k=k,
                j=j,
                q_hopf=q,
                implemented_exponent=float(mode_norm((k, j))),
                implemented_expression="q^2+j^2 with q=k-2j",
                tau_effective_exponent=0.0,
            )
        )
    return tuple(rows)


def _norm_value(mode: tuple[int, int], name: str) -> float:
    k, j = mode
    q = hopf_charge(k, j)
    values: dict[str, float] = {
        "q": float(q),
        "j": float(j),
        "q+j": float(q + j),
        "q^2+j^2": float(q * q + j * j),
        "sqrt(q^2+j^2)": sqrt(float(q * q + j * j)),
        "2q": float(2 * q),
        "q+3j": float(q + 3 * j),
    }
    return values[name]


def _norm_formula(name: str) -> str:
    formulas = {
        "q": "Z_l=exp[-eta_l*q]",
        "j": "Z_l=exp[-eta_l*j]",
        "q+j": "Z_l=exp[-eta_l*(q+j)]",
        "q^2+j^2": "Z_l=exp[-eta_l*(q^2+j^2)]",
        "sqrt(q^2+j^2)": "Z_l=exp[-eta_l*sqrt(q^2+j^2)]",
        "2q": "Z_l=exp[-eta_l*(2q)]",
        "q+3j": "Z_l=exp[-eta_l*(q+3j)]",
    }
    return formulas[name]


def _structural_note(name: str) -> str:
    notes = {
        "q": "Hopf-fiber-only diagnostic; numerically strong but ignores base index.",
        "j": "Base-index-only diagnostic; ignores Hopf charge.",
        "q+j": "Simple additive Hopf/base diagnostic.",
        "q^2+j^2": "Current predeclared Hopf/base norm candidate using q=k-2j.",
        "sqrt(q^2+j^2)": "Euclidean Hopf/base amplitude diagnostic.",
        "2q": "Fiber-weight diagnostic; numerically degenerate with q for held-out ratio ordering.",
        "q+3j": "Diagnostic only; a three-base-weight variant motivated by generation/coframe bookkeeping, not adopted.",
    }
    return notes[name]


def fit_eta_for_norm(norm_name: str) -> float:
    """Fit eta_l from mu/tau for a named norm."""

    baseline = _baseline_by_rank()
    mu = baseline["middle"]
    mu_exponent = _norm_value(mu.mode, norm_name)
    if mu_exponent <= 0:
        raise ValueError(f"invalid mu/tau exponent for {norm_name}")
    factor = mu.reference / mu.predicted
    if factor <= 0:
        raise ValueError("invalid mu/tau fit factor")
    eta = -log(factor) / mu_exponent
    if not isfinite(eta):
        raise ValueError(f"nonfinite eta_l for {norm_name}")
    return eta


def candidate_norm_results() -> tuple[CandidateNormResult, ...]:
    """Return all predeclared norm checks with mu/tau fit and e/tau holdout."""

    baseline = _baseline_by_rank()
    mu = baseline["middle"]
    electron = baseline["light"]
    results = []
    for name in ("q", "j", "q+j", "q^2+j^2", "sqrt(q^2+j^2)", "2q", "q+3j"):
        eta = fit_eta_for_norm(name)
        mu_exp = _norm_value(mu.mode, name)
        e_exp = _norm_value(electron.mode, name)
        mu_prediction = mu.predicted * exp(-eta * mu_exp)
        e_prediction = electron.predicted * exp(-eta * e_exp)
        mu_rel = abs(mu_prediction - mu.reference) / abs(mu.reference)
        e_rel = abs(e_prediction - electron.reference) / abs(electron.reference)
        results.append(
            CandidateNormResult(
                norm_name=name,
                formula=_norm_formula(name),
                mu_exponent=mu_exp,
                electron_exponent=e_exp,
                eta_from_mu_tau=eta,
                mu_dressed_prediction=mu_prediction,
                mu_relative_error=mu_rel,
                electron_held_out_prediction=e_prediction,
                electron_relative_error=e_rel,
                improves_electron=e_rel < electron.relative_error,
                included=True,
                structural_note=_structural_note(name),
            )
        )
    return tuple(results)


def documentation_matches_implementation() -> bool:
    """Return whether the prior precision candidate matches the implemented norm."""

    current = candidate_dressing_rows()
    by_rank = {row.rank: row for row in current}
    structural = next(row for row in candidate_norm_results() if row.norm_name == "q^2+j^2")
    return isclose(
        by_rank["middle"].dressed_prediction,
        structural.mu_dressed_prediction,
        rel_tol=0.0,
        abs_tol=1e-15,
    ) and isclose(
        by_rank["light"].dressed_prediction,
        structural.electron_held_out_prediction,
        rel_tol=0.0,
        abs_tol=1e-15,
    )


def formula_integrity_report() -> FormulaIntegrityReport:
    """Build the charged-lepton formula-integrity report."""

    norm_results = candidate_norm_results()
    best_numerical = min(norm_results, key=lambda row: row.electron_relative_error)
    structural = next(row for row in norm_results if row.norm_name == "q^2+j^2")
    matches = documentation_matches_implementation()
    sanity = frozen_sanity_payload()
    changed = sanity["changed_rows"]
    return FormulaIntegrityReport(
        classification=FORMULA_CONSISTENT if matches else FORMULA_MISMATCH_REMAINS,
        candidate_status=CANDIDATE_NOT_OFFICIAL,
        documentation_and_code_match=matches,
        prior_candidate_result_remains_valid=matches,
        official_outputs_changed=False,
        official_lepton_ratios_changed=False,
        lepton_precision_blocker_closed=False,
        originally_reported_formula=ORIGINALLY_REPORTED_FORMULA,
        actual_implemented_formula=IMPLEMENTED_FORMULA,
        q_definition=IMPLEMENTED_Q_DEFINITION,
        mode_exponents=implemented_mode_exponents(),
        candidate_norms=norm_results,
        best_numerical_candidate=best_numerical.norm_name,
        best_structurally_motivated_candidate=structural.norm_name,
        limitations=(
            "All candidate norms fit eta_l from mu/tau, so none is independently derived.",
            "The q^2+j^2 candidate uses Hopf charge q=k-2j, not the coordinate k.",
            "The best numerical held-out candidate is still exploratory and non-official.",
            "Frozen BHSM_BARE_V1 and BHSM_DRESSED_V1_CANDIDATE outputs are unchanged.",
            "The lepton precision blocker remains open.",
            f"Official branch comparison changes only {[row['quantity'] for row in changed]}.",
        ),
    )


def audit_payload() -> dict[str, Any]:
    """Return JSON-ready audit payload before dataclass conversion."""

    report = formula_integrity_report()
    return {
        "title": "BHSM charged-lepton dressing formula integrity audit",
        "classification": report.classification,
        "candidate_status": report.candidate_status,
        "documentation_and_code_match": report.documentation_and_code_match,
        "prior_candidate_result_remains_valid": report.prior_candidate_result_remains_valid,
        "official_outputs_changed": report.official_outputs_changed,
        "official_lepton_ratios_changed": report.official_lepton_ratios_changed,
        "lepton_precision_blocker_closed": report.lepton_precision_blocker_closed,
        "originally_reported_formula": report.originally_reported_formula,
        "actual_implemented_formula": report.actual_implemented_formula,
        "q_definition": report.q_definition,
        "mode_exponents": report.mode_exponents,
        "candidate_norms": report.candidate_norms,
        "best_numerical_candidate": report.best_numerical_candidate,
        "best_structurally_motivated_candidate": report.best_structurally_motivated_candidate,
        "frozen_sanity": frozen_sanity_payload(),
        "official_branch_comparison": compare_bhsm_v1_branches(),
        "limitations": report.limitations,
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
    """Render the formula-integrity audit as Markdown."""

    payload = payload or audit_payload()
    lines = [
        "# Charged-Lepton Dressing Formula Integrity Audit",
        "",
        "## Summary",
        "",
        f"Classification: `{payload['classification']}`",
        f"Candidate status: `{payload['candidate_status']}`",
        f"Documentation/code match: `{payload['documentation_and_code_match']}`",
        f"Prior candidate remains valid: `{payload['prior_candidate_result_remains_valid']}`",
        f"Lepton precision blocker closed: `{payload['lepton_precision_blocker_closed']}`",
        "",
        "## Formula Check",
        "",
        f"Originally reported formula: `{payload['originally_reported_formula']}`",
        f"Actual implemented formula: `{payload['actual_implemented_formula']}`",
        f"Definition: `{payload['q_definition']}`",
        "",
        "The earlier ambiguity is that `q` is the Hopf charge `k-2j`, not the coordinate `k`.",
        "",
        "## Implemented Exponents",
        "",
        "| Rank | Ratio | Mode | k | j | q=k-2j | Implemented exponent | Tau exponent |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["mode_exponents"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                row.rank,
                row.particle_ratio,
                row.mode,
                row.k,
                row.j,
                row.q_hopf,
                row.implemented_exponent,
                row.tau_effective_exponent,
            )
        )
    lines.extend(
        [
            "",
            "## Candidate Norm Scan",
            "",
            "| Norm | Mu exponent | Electron exponent | eta_l | Held-out e/tau | e/tau relative error | Improves e/tau | Note |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in payload["candidate_norms"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | {} |".format(
                row.norm_name,
                row.mu_exponent,
                row.electron_exponent,
                row.eta_from_mu_tau,
                row.electron_held_out_prediction,
                row.electron_relative_error,
                row.improves_electron,
                row.structural_note,
            )
        )
    lines.extend(
        [
            "",
            "## Best Candidates",
            "",
            f"Best numerical held-out candidate: `{payload['best_numerical_candidate']}`",
            f"Best structurally motivated current candidate: `{payload['best_structurally_motivated_candidate']}`",
            "",
            "The best numerical row is not official. The current `q^2+j^2` row remains the scoped candidate from the precision sprint because it uses both Hopf charge and base index.",
            "",
            "## Frozen Output Check",
            "",
            f"Official outputs changed: `{payload['official_outputs_changed']}`",
            f"Official lepton ratios changed: `{payload['official_lepton_ratios_changed']}`",
            f"Dressed branch changes only c/t: `{payload['frozen_sanity']['dressed_branch_changes_only_c_over_t']}`",
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["limitations"])
    lines.append("")
    return "\n".join(lines)


def export_formula_integrity_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export formula-integrity audit files."""

    base = Path(root)
    payload = audit_payload()
    markdown = render_markdown(payload)
    paths = {
        "audit_md": base / "audits" / "charged_lepton_dressing_formula_integrity_audit.md",
        "audit_json": base / "audits" / "charged_lepton_dressing_formula_integrity_audit.json",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["audit_md"].write_text(markdown, encoding="utf-8")
    paths["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_formula_integrity_outputs()
