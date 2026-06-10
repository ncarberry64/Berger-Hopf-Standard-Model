"""BHSM v2.2 formal-complement closure decision."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from complement_lower_bound_bridge import COMPLEMENT_LOWER_BOUND_CONDITIONAL, build_complement_lower_bound_bridge_report
from finite_projector_convergence import build_finite_projector_convergence_report
from formal_complement_projector import build_formal_complement_projector_report
from formal_kernel_projector import build_formal_kernel_projector_report
from projector_domain_stability import build_projector_domain_stability_report


HT_COMPLEMENT_BRIDGE_PROVEN = "HT_COMPLEMENT_BRIDGE_PROVEN"
HT_THEOREM_CANDIDATE_STRENGTHENED = "HT_THEOREM_CANDIDATE_STRENGTHENED"
HT_THEOREM_CONDITIONAL_ON_INDEX_MIRROR = "HT_THEOREM_CONDITIONAL_ON_INDEX_MIRROR"
HT_THEOREM_BLOCKED_BY_COMPLEMENT = "HT_THEOREM_BLOCKED_BY_COMPLEMENT"
FULL_HT_THEOREM_PROVEN = "FULL_HT_THEOREM_PROVEN"


@dataclass(frozen=True)
class FormalComplementClosureDecision:
    title: str
    formal_kernel_projector_status: str
    formal_complement_projector_status: str
    domain_stability_status: str
    finite_projector_convergence_status: str
    complement_lower_bound_status: str
    ht_dependency_status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def build_formal_complement_closure_decision() -> FormalComplementClosureDecision:
    kernel = build_formal_kernel_projector_report()
    complement = build_formal_complement_projector_report()
    domain = build_projector_domain_stability_report()
    convergence = build_finite_projector_convergence_report()
    lower = build_complement_lower_bound_bridge_report()
    if lower.status == COMPLEMENT_LOWER_BOUND_CONDITIONAL:
        ht_status = HT_THEOREM_CONDITIONAL_ON_INDEX_MIRROR
    else:
        ht_status = HT_THEOREM_BLOCKED_BY_COMPLEMENT
    return FormalComplementClosureDecision(
        title="BHSM v2.2 Formal Complement Closure Decision",
        formal_kernel_projector_status=kernel.status,
        formal_complement_projector_status=complement.status,
        domain_stability_status=domain.status,
        finite_projector_convergence_status=convergence.status,
        complement_lower_bound_status=lower.status,
        ht_dependency_status=ht_status,
        theorem_complete=False,
        open_obligations=(
            "prove topological index theorem for the complete twisted Dirac operator",
            "exclude mirror zero modes in the complete chiral operator",
            "upgrade conditional perturbation-domain stability to complete-operator proof",
        ),
        limitations=(
            "v2.2 closes the formal projector algebra and finite-projector convergence bridge.",
            "The full H_T theorem still requires index and mirror closure.",
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


def export_formal_complement_closure_decision_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_formal_complement_closure_decision()), indent=2, sort_keys=True) + "\n")


def export_formal_complement_closure_decision_markdown(path: str | Path) -> None:
    report = build_formal_complement_closure_decision()
    lines = [
        "# BHSM v2.2 Formal Complement Closure Decision",
        "",
        f"H_T dependency status: `{report.ht_dependency_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Dependency | Status |",
        "| --- | --- |",
        f"| formal kernel projector | `{report.formal_kernel_projector_status}` |",
        f"| formal complement projector | `{report.formal_complement_projector_status}` |",
        f"| domain stability | `{report.domain_stability_status}` |",
        f"| finite-projector convergence | `{report.finite_projector_convergence_status}` |",
        f"| complement lower-bound bridge | `{report.complement_lower_bound_status}` |",
        "",
        "## Open Obligations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
