"""Callable assembly of the non-production CP O_int symbolic candidate."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class CPOIntCallableEvaluation:
    callable_key: str
    expression: str
    status: str
    callable_available: bool
    production_callable: bool
    inputs_used: tuple[str, ...]
    output_schema: dict[str, Any]
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_symbolic_cp_o_int(
    coupling_symbol: str,
    phase_expression: str,
    field_expression: str,
    boundary_expression: str,
) -> CPOIntCallableEvaluation:
    """Assemble a symbolic expression; do not evaluate a physical amplitude."""

    expression = f"{coupling_symbol} * {phase_expression} * ({field_expression}) * ({boundary_expression}) + h.c."
    return CPOIntCallableEvaluation(
        callable_key="cp_o_int_symbolic_candidate",
        expression=expression,
        status="AVAILABLE_SYMBOLIC_CANDIDATE",
        callable_available=True,
        production_callable=False,
        inputs_used=("coupling_symbol", "phase_expression", "field_expression", "boundary_expression"),
        output_schema={"expression": "symbolic string", "production_eligible": False},
        claim_boundary="This callable assembles a symbolic candidate; it is not a production theorem callable.",
    )
