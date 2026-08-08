"""BHSM v14.45 completion/status surface."""

from __future__ import annotations

from .foundational_dirac_spin_glue_v14_45 import (
    EXACT_NEXT_OBJECT,
    PRIMARY_VERDICT,
    RENORMALIZATION_VERDICT,
    SECONDARY_VERDICT,
    VERSION,
    completion_payload,
    deterministic_json,
)


def status_text() -> str:
    return f"""# BHSM {VERSION} foundational Dirac and spin-glue gate

- Primary: `{PRIMARY_VERDICT}`
- Secondary: `{SECONDARY_VERDICT}`
- Renormalization: `{RENORMALIZATION_VERDICT}`
- Exact next object: `{EXACT_NEXT_OBJECT}`
- Mark III: NOT REACHED
- BHSM complete: false
"""


__all__ = [
    "EXACT_NEXT_OBJECT",
    "PRIMARY_VERDICT",
    "RENORMALIZATION_VERDICT",
    "SECONDARY_VERDICT",
    "VERSION",
    "completion_payload",
    "deterministic_json",
    "status_text",
]
