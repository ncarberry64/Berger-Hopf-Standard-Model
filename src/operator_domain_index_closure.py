"""BHSM v1.7 operator-domain, index, and mirror closure audit.

The v1.7 target is upstream of the full H_T theorem. It does not redo earlier
finite/scaffold audits; it classifies whether those audits are enough to close
the complete operator-domain/index/mirror chain.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from full_operator_domain import FORMAL_KERNEL_STATES, build_full_operator_domain_report
from mirror_exclusion_theorem import build_mirror_exclusion_theorem_report
from self_adjoint_domain import SELF_ADJOINT_DOMAIN_OPEN, build_self_adjoint_domain_report
from twisted_dirac_index_theorem import build_twisted_dirac_index_theorem_report


RELATIVE_BOUND_CONDITIONAL = "RELATIVE_BOUND_CONDITIONAL"
RELATIVE_BOUND_OPEN = "RELATIVE_BOUND_OPEN"
RELATIVE_BOUND_FAILS = "RELATIVE_BOUND_FAILS"

INDEX_THEOREM_PROVEN = "INDEX_THEOREM_PROVEN"
INDEX_THEOREM_CANDIDATE = "INDEX_THEOREM_CANDIDATE"
INDEX_THEOREM_CONDITIONAL = "INDEX_THEOREM_CONDITIONAL"
INDEX_THEOREM_OPEN = "INDEX_THEOREM_OPEN"
FAILS_INDEX_CHECK = "FAILS_INDEX_CHECK"

MIRROR_EXCLUSION_PROVEN = "MIRROR_EXCLUSION_PROVEN"
MIRROR_EXCLUSION_CANDIDATE = "MIRROR_EXCLUSION_CANDIDATE"
MIRROR_EXCLUSION_CONDITIONAL = "MIRROR_EXCLUSION_CONDITIONAL"
MIRROR_EXCLUSION_OPEN = "MIRROR_EXCLUSION_OPEN"
FAILS_MIRROR_EXCLUSION = "FAILS_MIRROR_EXCLUSION"

HT_THEOREM_CANDIDATE_STRENGTHENED = "HT_THEOREM_CANDIDATE_STRENGTHENED"
HT_THEOREM_BLOCKED_BY_DOMAIN = "HT_THEOREM_BLOCKED_BY_DOMAIN"
HT_THEOREM_BLOCKED_BY_INDEX = "HT_THEOREM_BLOCKED_BY_INDEX"
HT_THEOREM_BLOCKED_BY_MIRROR = "HT_THEOREM_BLOCKED_BY_MIRROR"
FULL_HT_THEOREM_PROVEN = "FULL_HT_THEOREM_PROVEN"


@dataclass(frozen=True)
class RelativeBoundTerm:
    """One Kato-Rellich/relative-bound audit row."""

    term_id: str
    operator_role: str
    relative_a: float
    relative_b: float
    below_one: bool
    evidence_scope: str
    infinite_basis_compatible: bool
    open_obligations: tuple[str, ...]


@dataclass(frozen=True)
class RelativeBoundAuditReport:
    """Relative-bound audit summary for the v1.7 domain chain."""

    terms: tuple[RelativeBoundTerm, ...]
    max_relative_a: float
    all_bounds_below_one: bool
    all_infinite_basis_compatible: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class IndexMirrorClosureReport:
    """Combined v1.7 index/mirror status."""

    formal_kernel: tuple[str, ...]
    sector_labels: tuple[str, ...]
    index_status: str
    mirror_status: str
    scaffold_index: int
    target_index: int
    chiral_channel_excludes_generated_mirrors: bool
    higgs_u1_channel_closed: bool
    boundary_functional_channel_closed: bool
    theorem_complete: bool
    open_obligations: tuple[str, ...]


@dataclass(frozen=True)
class OperatorDomainIndexClosureReport:
    """Complete v1.7 operator-domain/index/mirror closure report."""

    title: str
    formal_kernel: tuple[str, ...]
    old_coordinate_first_kernel_rejected: tuple[int, int, int]
    domain_status: str
    relative_bound_status: str
    index_status: str
    mirror_status: str
    ht_dependency_status: str
    self_adjoint_report_status: str
    relative_bound_report: RelativeBoundAuditReport
    index_mirror_report: IndexMirrorClosureReport
    theorem_complete: bool
    frozen_outputs_changed: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def relative_bound_terms() -> tuple[RelativeBoundTerm, ...]:
    """Return the v1.7 relative-bound audit rows.

    Numerical values are inherited from existing v1.3 sector-coupling audits
    and conservative boundedness classifications. Infinite-basis compatibility
    is only marked true when the current repo has a genuine structural proof,
    not merely a finite scan.
    """

    return (
        RelativeBoundTerm("D_diag_squared", "unperturbed diagonal operator", 0.0, 0.0, True, "definition of base operator", True, ()),
        RelativeBoundTerm("V_Hopf", "Hopf twist term", 0.0, 0.0, True, "finite/scaffold boundedness", False, ("prove infinite-basis Hopf twist relative boundedness",)),
        RelativeBoundTerm("V_boundary", "sector boundary term", 0.0, 0.0, True, "finite/scaffold boundedness", False, ("prove complete boundary functional relative boundedness",)),
        RelativeBoundTerm("V_chi", "chirality projector term", 0.0, 0.0, True, "projector scaffold", False, ("prove chirality projector preserves the full operator domain",)),
        RelativeBoundTerm("K_sector", "sector-coupling block", 0.015621013485509948, 0.0, True, "uniform scan and structured relative-bound candidate through k_max=32", False, ("upgrade uniform scan to an infinite-basis sector-coupling theorem",)),
        RelativeBoundTerm("P_perp_lift", "heat lift on the formal complement", 0.0, 0.0, True, "PSD monotone lift", False, ("prove full formal-kernel complement projector and domain stability",)),
        RelativeBoundTerm("PSD_profile", "positive semidefinite profile contribution", 0.0, 0.0, True, "PSD construction", True, ()),
    )


def build_relative_bound_audit_report() -> RelativeBoundAuditReport:
    """Build the v1.7 Kato-Rellich/relative-bound audit report."""

    terms = relative_bound_terms()
    max_a = max(term.relative_a for term in terms)
    all_below = all(term.below_one for term in terms)
    all_infinite = all(term.infinite_basis_compatible for term in terms)
    if not all_below:
        status = RELATIVE_BOUND_FAILS
    elif all_infinite:
        status = HT_THEOREM_CANDIDATE_STRENGTHENED
    else:
        status = RELATIVE_BOUND_CONDITIONAL
    return RelativeBoundAuditReport(
        terms=terms,
        max_relative_a=max_a,
        all_bounds_below_one=all_below,
        all_infinite_basis_compatible=all_infinite,
        status=status,
        theorem_complete=False,
        limitations=(
            "All listed relative-a estimates are below 1 in the current scaffold.",
            "Several terms remain finite/scaffold or uniform-scan evidence, not complete infinite-basis proofs.",
        ),
    )


def build_index_mirror_closure_report() -> IndexMirrorClosureReport:
    """Build the v1.7 index/mirror closure report."""

    index = build_twisted_dirac_index_theorem_report()
    mirror = build_mirror_exclusion_theorem_report()
    sector_labels = tuple(state.split(",", maxsplit=1)[0].replace("|", "") for state in FORMAL_KERNEL_STATES)
    index_status = INDEX_THEOREM_CONDITIONAL if index.visible_kernel_states == 3 else FAILS_INDEX_CHECK
    if index.status.endswith("OPEN"):
        index_status = INDEX_THEOREM_OPEN
    mirror_status = MIRROR_EXCLUSION_CONDITIONAL if mirror.chiral_channel_excludes_all_generated else MIRROR_EXCLUSION_OPEN
    if mirror.status == MIRROR_EXCLUSION_CONDITIONAL:
        mirror_status = MIRROR_EXCLUSION_CONDITIONAL
    elif not mirror.higgs_u1_channel_closed or not mirror.boundary_functional_channel_closed:
        mirror_status = MIRROR_EXCLUSION_OPEN
    open_obligations = tuple(
        dict.fromkeys(
            (
                *index.open_obligations,
                *mirror.open_obligations,
            )
        )
    )
    return IndexMirrorClosureReport(
        formal_kernel=FORMAL_KERNEL_STATES,
        sector_labels=sector_labels,
        index_status=index_status,
        mirror_status=mirror_status,
        scaffold_index=index.audit.finite_scaffold_index,
        target_index=3,
        chiral_channel_excludes_generated_mirrors=mirror.chiral_channel_excludes_all_generated,
        higgs_u1_channel_closed=mirror.higgs_u1_channel_closed,
        boundary_functional_channel_closed=mirror.boundary_functional_channel_closed,
        theorem_complete=index_status == INDEX_THEOREM_PROVEN and mirror_status == MIRROR_EXCLUSION_PROVEN,
        open_obligations=open_obligations,
    )


def _ht_dependency_status(domain_status: str, index_status: str, mirror_status: str) -> str:
    if domain_status != SELF_ADJOINT_DOMAIN_OPEN and index_status == INDEX_THEOREM_PROVEN and mirror_status == MIRROR_EXCLUSION_PROVEN:
        return HT_THEOREM_CANDIDATE_STRENGTHENED
    if domain_status == SELF_ADJOINT_DOMAIN_OPEN:
        return HT_THEOREM_BLOCKED_BY_DOMAIN
    if index_status != INDEX_THEOREM_PROVEN:
        return HT_THEOREM_BLOCKED_BY_INDEX
    if mirror_status != MIRROR_EXCLUSION_PROVEN:
        return HT_THEOREM_BLOCKED_BY_MIRROR
    return FULL_HT_THEOREM_PROVEN


def build_operator_domain_index_closure_report() -> OperatorDomainIndexClosureReport:
    """Build the v1.7 operator-domain/index/mirror closure report."""

    domain = build_full_operator_domain_report()
    self_adjoint = build_self_adjoint_domain_report()
    relative = build_relative_bound_audit_report()
    index_mirror = build_index_mirror_closure_report()
    ht_status = _ht_dependency_status(domain.status, index_mirror.index_status, index_mirror.mirror_status)
    open_obligations = tuple(
        dict.fromkeys(
            (
                *domain.open_obligations,
                *(item for term in relative.terms for item in term.open_obligations),
                *index_mirror.open_obligations,
            )
        )
    )
    return OperatorDomainIndexClosureReport(
        title="BHSM v1.7 Operator-Domain and Index Closure Report",
        formal_kernel=FORMAL_KERNEL_STATES,
        old_coordinate_first_kernel_rejected=(0, 1, 2),
        domain_status=domain.status,
        relative_bound_status=relative.status,
        index_status=index_mirror.index_status,
        mirror_status=index_mirror.mirror_status,
        ht_dependency_status=ht_status,
        self_adjoint_report_status=self_adjoint.status,
        relative_bound_report=relative,
        index_mirror_report=index_mirror,
        theorem_complete=ht_status == FULL_HT_THEOREM_PROVEN,
        frozen_outputs_changed=False,
        open_obligations=open_obligations,
        limitations=(
            "v1.7 strengthens the dependency audit but does not close the full domain/index/mirror theorem chain.",
            "The old coordinate-first kernel (0,1,2) is rejected for corrected formal-kernel reports.",
            "No frozen predictions, constants, mode ledgers, tolerances, or prior scaffold outputs are changed.",
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


def export_operator_domain_index_closure_json(path: str | Path) -> None:
    """Export the v1.7 closure report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_operator_domain_index_closure_report()), indent=2, sort_keys=True) + "\n")


def export_operator_domain_index_closure_markdown(path: str | Path) -> None:
    """Export the v1.7 closure report as Markdown."""

    report = build_operator_domain_index_closure_report()
    lines = [
        "# BHSM v1.7 Operator-Domain and Index Closure Report",
        "",
        f"Domain status: `{report.domain_status}`",
        f"Relative-bound status: `{report.relative_bound_status}`",
        f"Index status: `{report.index_status}`",
        f"Mirror status: `{report.mirror_status}`",
        f"H_T dependency status: `{report.ht_dependency_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Frozen outputs changed: `{report.frozen_outputs_changed}`",
        "",
        "## Corrected Formal Kernel",
        "",
    ]
    lines.extend(f"- `{state}`" for state in report.formal_kernel)
    lines.extend(
        [
            "",
            f"Rejected coordinate-first kernel: `{report.old_coordinate_first_kernel_rejected}`",
            "",
            "## Relative-Bound Audit",
            "",
            "| Term | a | b | Below 1 | Scope | Infinite-basis compatible | Open obligations |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for term in report.relative_bound_report.terms:
        lines.append(
            f"| `{term.term_id}` | `{term.relative_a}` | `{term.relative_b}` | `{term.below_one}` | {term.evidence_scope} | `{term.infinite_basis_compatible}` | {'<br>'.join(term.open_obligations) or 'none'} |"
        )
    lines.extend(
        [
            "",
            "## Index and Mirror Summary",
            "",
            f"- Scaffold index: `{report.index_mirror_report.scaffold_index}`",
            f"- Target index: `{report.index_mirror_report.target_index}`",
            f"- Chiral channel excludes generated mirrors: `{report.index_mirror_report.chiral_channel_excludes_generated_mirrors}`",
            f"- Higgs-U1 channel closed: `{report.index_mirror_report.higgs_u1_channel_closed}`",
            f"- Boundary-functional channel closed: `{report.index_mirror_report.boundary_functional_channel_closed}`",
            "",
            "## Open Obligations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))


def export_self_adjoint_domain_markdown(path: str | Path) -> None:
    """Export a v1.7 self-adjoint domain report."""

    report = build_operator_domain_index_closure_report()
    lines = [
        "# BHSM v1.7 Self-Adjoint Domain Report",
        "",
        f"Status: `{report.domain_status}`",
        f"Self-adjoint report status: `{report.self_adjoint_report_status}`",
        f"Relative-bound status: `{report.relative_bound_status}`",
        "",
        "The finite matrix scaffold is Hermitian, but the complete operator still requires domain, core, projector, and infinite-basis relative-bound proofs.",
        "",
    ]
    Path(path).write_text("\n".join(lines))


def export_self_adjoint_domain_json(path: str | Path) -> None:
    """Export a compact self-adjoint domain report."""

    report = build_operator_domain_index_closure_report()
    payload = {
        "status": report.domain_status,
        "self_adjoint_report_status": report.self_adjoint_report_status,
        "relative_bound_status": report.relative_bound_status,
        "theorem_complete": report.theorem_complete,
        "open_obligations": report.open_obligations,
    }
    Path(path).write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n")


def export_index_mirror_closure_markdown(path: str | Path) -> None:
    """Export a compact v1.7 index/mirror report."""

    report = build_operator_domain_index_closure_report()
    im = report.index_mirror_report
    lines = [
        "# BHSM v1.7 Index and Mirror Closure Report",
        "",
        f"Index status: `{im.index_status}`",
        f"Mirror status: `{im.mirror_status}`",
        f"Theorem complete: `{im.theorem_complete}`",
        "",
        f"Formal kernel: `{im.formal_kernel}`",
        f"Sector labels: `{im.sector_labels}`",
        f"Scaffold index: `{im.scaffold_index}`",
        f"Target index: `{im.target_index}`",
        "",
        "## Open Obligations",
        "",
    ]
    lines.extend(f"- {item}" for item in im.open_obligations)
    lines.append("")
    Path(path).write_text("\n".join(lines))


def export_index_mirror_closure_json(path: str | Path) -> None:
    """Export a compact v1.7 index/mirror report."""

    report = build_operator_domain_index_closure_report()
    Path(path).write_text(json.dumps(_jsonable(report.index_mirror_report), indent=2, sort_keys=True) + "\n")
