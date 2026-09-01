"""BHSM v1.8 uniform relative-bound theorem attempt."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


UNIFORM_RELATIVE_BOUND_PROVEN = "UNIFORM_RELATIVE_BOUND_PROVEN"
UNIFORM_RELATIVE_BOUND_CANDIDATE = "UNIFORM_RELATIVE_BOUND_CANDIDATE"
UNIFORM_RELATIVE_BOUND_CONDITIONAL = "UNIFORM_RELATIVE_BOUND_CONDITIONAL"
FINITE_SCAN_ONLY = "FINITE_SCAN_ONLY"
FAILS_UNIFORM_BOUND = "FAILS_UNIFORM_BOUND"


@dataclass(frozen=True)
class UniformRelativeBoundTerm:
    """One perturbation term in the infinite-basis relative-bound audit."""

    term_id: str
    finite_scaffold_bound: str
    candidate_infinite_bound: str
    depends_on: tuple[str, ...]
    uniform_in_kmax: bool
    proof_method: str
    assumptions_proven: bool
    relative_a: float
    relative_b: float
    status: str
    open_obligations: tuple[str, ...]


@dataclass(frozen=True)
class UniformRelativeBoundReport:
    """Uniform relative-bound theorem attempt report."""

    title: str
    terms: tuple[UniformRelativeBoundTerm, ...]
    total_relative_a_upper: float
    total_relative_b_upper: float
    all_a_below_one: bool
    all_assumptions_proven: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def uniform_relative_bound_terms() -> tuple[UniformRelativeBoundTerm, ...]:
    """Return perturbation rows for V_Hopf + V_boundary + V_chi + K_sector."""

    return (
        UniformRelativeBoundTerm(
            term_id="V_Hopf",
            finite_scaffold_bound="bounded on finite q-ranges in truncation audits",
            candidate_infinite_bound="|V_Hopf psi| <= b_H ||psi|| if Hopf twist coefficient is uniformly bounded or relatively D0-bounded by q^2 <= C lambda_diag",
            depends_on=("q", "k", "j"),
            uniform_in_kmax=True,
            proof_method="candidate q^2/lambda_diag comparison",
            assumptions_proven=False,
            relative_a=0.0,
            relative_b=0.0,
            status=UNIFORM_RELATIVE_BOUND_CONDITIONAL,
            open_obligations=("prove the q^2/lambda_diag comparison for the complete Berger twisted spectrum",),
        ),
        UniformRelativeBoundTerm(
            term_id="V_boundary",
            finite_scaffold_bound="bounded by sector boundary residuals in finite ledgers",
            candidate_infinite_bound="|V_boundary psi| <= a_B |D0 psi| + b_B ||psi|| using Omega_f growth controlled by k,j and diagonal action",
            depends_on=("k", "j", "q", "sector"),
            uniform_in_kmax=True,
            proof_method="relative growth bound against diagonal action",
            assumptions_proven=False,
            relative_a=0.0,
            relative_b=0.0,
            status=UNIFORM_RELATIVE_BOUND_CONDITIONAL,
            open_obligations=("prove Omega_f growth is relatively bounded by the complete diagonal operator",),
        ),
        UniformRelativeBoundTerm(
            term_id="V_chi",
            finite_scaffold_bound="chirality projector is bounded in finite matrices",
            candidate_infinite_bound="||V_chi psi|| <= b_chi ||psi|| because chirality is a two-valued bounded projector",
            depends_on=("chirality",),
            uniform_in_kmax=True,
            proof_method="bounded projector",
            assumptions_proven=True,
            relative_a=0.0,
            relative_b=1.0,
            status=UNIFORM_RELATIVE_BOUND_CANDIDATE,
            open_obligations=(),
        ),
        UniformRelativeBoundTerm(
            term_id="K_sector",
            finite_scaffold_bound="v1.7 inherits a_K = 0.015621013485509948, b_K = 0 from structured uniform scans",
            candidate_infinite_bound="|<psi,K_sector psi>| <= a_K <psi,D0^2 psi> with a_K < 1 if the sparse/banded coupling rule is uniform in the infinite basis",
            depends_on=("sector", "k", "j", "q", "chirality"),
            uniform_in_kmax=True,
            proof_method="structured relative-bound candidate from sparse sector-preserving coupling",
            assumptions_proven=False,
            relative_a=0.015621013485509948,
            relative_b=0.0,
            status=UNIFORM_RELATIVE_BOUND_CONDITIONAL,
            open_obligations=("prove sparse/banded sector-coupling rule and a_K bound in the complete infinite basis",),
        ),
    )


def build_uniform_relative_bound_report() -> UniformRelativeBoundReport:
    """Build the uniform relative-bound theorem attempt report."""

    terms = uniform_relative_bound_terms()
    total_a = sum(row.relative_a for row in terms)
    total_b = sum(row.relative_b for row in terms)
    all_below = total_a < 1.0 and all(row.relative_a < 1.0 for row in terms)
    all_proven = all(row.assumptions_proven for row in terms)
    if not all_below:
        status = FAILS_UNIFORM_BOUND
    elif all_proven:
        status = UNIFORM_RELATIVE_BOUND_PROVEN
    else:
        status = UNIFORM_RELATIVE_BOUND_CONDITIONAL
    return UniformRelativeBoundReport(
        title="BHSM v1.8 Uniform Relative-Bound Theorem Attempt",
        terms=terms,
        total_relative_a_upper=total_a,
        total_relative_b_upper=total_b,
        all_a_below_one=all_below,
        all_assumptions_proven=all_proven,
        status=status,
        theorem_complete=status == UNIFORM_RELATIVE_BOUND_PROVEN,
        limitations=(
            "The total relative-a upper estimate is below one, but not all infinite-basis assumptions are proven.",
            "This report upgrades finite scans to explicit conditional theorem obligations, not to a completed proof.",
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


def export_uniform_relative_bound_json(path: str | Path) -> None:
    """Export the uniform relative-bound report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_uniform_relative_bound_report()), indent=2, sort_keys=True) + "\n")


def export_uniform_relative_bound_markdown(path: str | Path) -> None:
    """Export the uniform relative-bound report as Markdown."""

    report = build_uniform_relative_bound_report()
    lines = [
        "# BHSM v1.8 Uniform Relative-Bound Theorem Attempt",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Total relative-a upper estimate: `{report.total_relative_a_upper}`",
        f"All a below one: `{report.all_a_below_one}`",
        "",
        "| Term | a | b | Uniform in k_max | Status | Open obligations |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.terms:
        lines.append(f"| `{row.term_id}` | `{row.relative_a}` | `{row.relative_b}` | `{row.uniform_in_kmax}` | `{row.status}` | {'<br>'.join(row.open_obligations) or 'none'} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

