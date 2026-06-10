"""BHSM v2.2 formal-complement projector scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from formal_kernel_projector import FORMAL_KERNEL_PROJECTOR_PROVEN, build_formal_kernel_projector_report


FORMAL_COMPLEMENT_PROJECTOR_PROVEN = "FORMAL_COMPLEMENT_PROJECTOR_PROVEN"
FORMAL_COMPLEMENT_PROJECTOR_CONDITIONAL = "FORMAL_COMPLEMENT_PROJECTOR_CONDITIONAL"
FORMAL_COMPLEMENT_PROJECTOR_OPEN = "FORMAL_COMPLEMENT_PROJECTOR_OPEN"
FAILS_FORMAL_COMPLEMENT_PROJECTOR = "FAILS_FORMAL_COMPLEMENT_PROJECTOR"


@dataclass(frozen=True)
class FormalComplementProjectorReport:
    title: str
    kernel_projector_status: str
    complement_definition: str
    idempotent: bool
    self_adjoint: bool
    orthogonal_to_kernel: bool
    range_kernel_decomposition: str
    compatible_with_hilbert_completion: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_formal_complement_projector_report() -> FormalComplementProjectorReport:
    kernel = build_formal_kernel_projector_report()
    algebra_passes = kernel.status == FORMAL_KERNEL_PROJECTOR_PROVEN
    return FormalComplementProjectorReport(
        title="BHSM v2.2 Formal Complement Projector Report",
        kernel_projector_status=kernel.status,
        complement_definition="P_perp = I - P_K on H = l2({sector,k,j,q,chi})",
        idempotent=algebra_passes,
        self_adjoint=algebra_passes,
        orthogonal_to_kernel=algebra_passes,
        range_kernel_decomposition="H = K_formal direct-sum K_formal^perp",
        compatible_with_hilbert_completion=algebra_passes,
        status=FORMAL_COMPLEMENT_PROJECTOR_PROVEN if algebra_passes else FAILS_FORMAL_COMPLEMENT_PROJECTOR,
        theorem_complete=False,
        limitations=(
            "The orthogonal-complement projector algebra is proven for the finite-rank sector-labeled kernel in l2.",
            "Operator-domain invariance is handled separately and is not implied by projector algebra alone.",
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


def export_formal_complement_projector_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_formal_complement_projector_report()), indent=2, sort_keys=True) + "\n")


def export_formal_complement_projector_markdown(path: str | Path) -> None:
    report = build_formal_complement_projector_report()
    lines = [
        "# BHSM v2.2 Formal Complement Projector Report",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Definition: `{report.complement_definition}`",
        "",
        "| Property | Value |",
        "| --- | --- |",
        f"| kernel projector status | `{report.kernel_projector_status}` |",
        f"| idempotent | `{report.idempotent}` |",
        f"| self-adjoint | `{report.self_adjoint}` |",
        f"| orthogonal to kernel | `{report.orthogonal_to_kernel}` |",
        f"| compatible with Hilbert completion | `{report.compatible_with_hilbert_completion}` |",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
