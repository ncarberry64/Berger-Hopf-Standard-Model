"""Thin status interface for BHSM v14.43."""

from __future__ import annotations

from .moduli_clifford_matcher_zeta_v14_43 import (
    EXACT_NEXT_OBJECT,
    PRIMARY_VERDICT,
    SECONDARY_VERDICT,
    SPINOR_LIFT_VERDICT,
    VERSION,
    ZETA_VERDICT,
    completion_payload,
    deterministic_json,
)


def status_text() -> str:
    payload = completion_payload()
    return "\n".join(
        [
            f"# BHSM {VERSION} moduli/Clifford matcher-zeta gate",
            "",
            f"- Primary: `{PRIMARY_VERDICT}`",
            f"- Secondary: `{SECONDARY_VERDICT}`",
            f"- Spinor lift: `{SPINOR_LIFT_VERDICT}`",
            f"- Zeta: `{ZETA_VERDICT}`",
            f"- Exact next object: `{EXACT_NEXT_OBJECT}`",
            f"- Validation passed: `{payload['validation_passed']}`",
            "- BHSM complete: `False`",
        ]
    ) + "\n"


__all__ = [
    "EXACT_NEXT_OBJECT",
    "PRIMARY_VERDICT",
    "SECONDARY_VERDICT",
    "SPINOR_LIFT_VERDICT",
    "VERSION",
    "ZETA_VERDICT",
    "completion_payload",
    "deterministic_json",
    "status_text",
]
