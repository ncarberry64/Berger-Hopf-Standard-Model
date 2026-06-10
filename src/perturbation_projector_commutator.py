"""BHSM v2.4 projector/perturbation commutator audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from formal_complement_projector import FORMAL_COMPLEMENT_PROJECTOR_PROVEN, build_formal_complement_projector_report
from perturbation_closure_decision import KATO_RELLICH_CLOSURE_CONDITIONAL, build_perturbation_closure_decision


PROJECTOR_COMMUTATORS_CONTROLLED = "PROJECTOR_COMMUTATORS_CONTROLLED"
PROJECTOR_COMMUTATORS_CONDITIONAL = "PROJECTOR_COMMUTATORS_CONDITIONAL"
PROJECTOR_COMMUTATORS_OPEN = "PROJECTOR_COMMUTATORS_OPEN"
FAILS_PROJECTOR_COMMUTATOR_CONTROL = "FAILS_PROJECTOR_COMMUTATOR_CONTROL"


@dataclass(frozen=True)
class ProjectorCommutatorRow:
    term_id: str
    commutator: str
    vanishes: bool
    bounded: bool
    relatively_bounded: bool
    relative_a: float
    status: str
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class PerturbationProjectorCommutatorReport:
    title: str
    projector_status: str
    perturbation_bridge_status: str
    rows: tuple[ProjectorCommutatorRow, ...]
    all_commutators_controlled: bool
    all_complete_operator_proven: bool
    status: str
    theorem_complete: bool
    open_obligations: tuple[str, ...]
    limitations: tuple[str, ...]


def commutator_rows() -> tuple[ProjectorCommutatorRow, ...]:
    return (
        ProjectorCommutatorRow("[P_perp,A0]", "0 on the diagonal formal-kernel decomposition", True, True, True, 0.0, "COMMUTATOR_CONTROLLED", ("A0 is diagonal in the sector-labeled basis",), ()),
        ProjectorCommutatorRow("[P_perp,V_Hopf]", "conditional zero/bounded on named formal kernel", False, True, True, 0.0, "COMMUTATOR_CONDITIONAL", ("Hopf term preserves the formal kernel/complement split in the scaffold",), ("complete-operator Hopf domain invariance remains to prove",)),
        ProjectorCommutatorRow("[P_perp,V_boundary]", "conditional zero/bounded on named formal kernel", False, True, True, 0.0, "COMMUTATOR_CONDITIONAL", ("v1.2 boundary functional preserves protected sector labels",), ("full boundary problem remains action-scaffold conditional",)),
        ProjectorCommutatorRow("[P_perp,V_chi]", "zero for the protected chirality projector channel", True, True, True, 0.0, "COMMUTATOR_CONTROLLED", ("chiral projector acts diagonally on chirality labels",), ()),
        ProjectorCommutatorRow("[P_perp,K_sector]", "zero on protected block, relatively bounded on complement", False, True, True, 0.015621013485509948, "COMMUTATOR_CONDITIONAL", ("sector coupling vanishes on the formal kernel and has the v2.1 relative-bound estimate",), ("upgrade structured bound to complete-operator theorem",)),
        ProjectorCommutatorRow("[P_perp,P_lift+PSD]", "bounded PSD lift/profile channel", False, True, True, 0.0, "COMMUTATOR_CONDITIONAL", ("lift/profile terms are bounded or PSD on the scaffold complement",), ("profile positivity/domain invariance remains action-level conditional",)),
    )


def build_perturbation_projector_commutator_report() -> PerturbationProjectorCommutatorReport:
    projector = build_formal_complement_projector_report()
    perturbation = build_perturbation_closure_decision()
    rows = commutator_rows()
    controlled = projector.status == FORMAL_COMPLEMENT_PROJECTOR_PROVEN and perturbation.kato_rellich_status == KATO_RELLICH_CLOSURE_CONDITIONAL and all(row.bounded and row.relatively_bounded for row in rows)
    proven = controlled and all(row.vanishes for row in rows)
    status = PROJECTOR_COMMUTATORS_CONTROLLED if proven else PROJECTOR_COMMUTATORS_CONDITIONAL if controlled else PROJECTOR_COMMUTATORS_OPEN
    return PerturbationProjectorCommutatorReport(
        title="BHSM v2.4 Perturbation Projector Commutator Report",
        projector_status=projector.status,
        perturbation_bridge_status=perturbation.kato_rellich_status,
        rows=rows,
        all_commutators_controlled=controlled,
        all_complete_operator_proven=proven,
        status=status,
        theorem_complete=status == PROJECTOR_COMMUTATORS_CONTROLLED,
        open_obligations=(
            "prove nonzero commutators are bounded or relatively bounded in the complete twisted Dirac/bundle operator",
            "prove sector-coupling commutator control independent of scaffold identification assumptions",
        ),
        limitations=(
            "Commutators are controlled in the explicit scaffold chain.",
            "They are not all zero or complete-operator proven, so the status remains conditional.",
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


def export_perturbation_projector_commutator_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_perturbation_projector_commutator_report()), indent=2, sort_keys=True) + "\n")


def export_perturbation_projector_commutator_markdown(path: str | Path) -> None:
    report = build_perturbation_projector_commutator_report()
    lines = [
        "# BHSM v2.4 Perturbation Projector Commutator Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Term | Vanishes | Bounded | Relatively bounded | a | Status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.rows:
        lines.append(f"| `{row.term_id}` | `{row.vanishes}` | `{row.bounded}` | `{row.relatively_bounded}` | `{row.relative_a}` | `{row.status}` |")
    lines.extend(["", "## Open Obligations", ""])
    lines.extend(f"- {item}" for item in report.open_obligations)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
