"""BHSM v14.44 completion/status surface."""

from __future__ import annotations

from .worldline_clifford_spin_lift_v14_44 import (
    EXACT_NEXT_OBJECT,
    PRIMARY_VERDICT,
    SECONDARY_VERDICT,
    SPINOR_BRANCH_VERDICT,
    VERSION,
    completion_payload,
    deterministic_json,
)


def status_text() -> str:
    return f"""# BHSM {VERSION} worldline/Clifford spin-lift gate

- Primary: `{PRIMARY_VERDICT}`
- Secondary: `{SECONDARY_VERDICT}`
- Spinor branches: `{SPINOR_BRANCH_VERDICT}`
- Exact next object: `{EXACT_NEXT_OBJECT}`
- Mark III: NOT REACHED
- BHSM complete: false
"""


__all__ = [
    "EXACT_NEXT_OBJECT",
    "PRIMARY_VERDICT",
    "SECONDARY_VERDICT",
    "SPINOR_BRANCH_VERDICT",
    "VERSION",
    "completion_payload",
    "deterministic_json",
    "status_text",
]
