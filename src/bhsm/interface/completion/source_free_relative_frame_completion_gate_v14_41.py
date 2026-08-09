"""Public completion/status gate for BHSM v14.41."""

from __future__ import annotations

from .source_free_relative_frame_v14_41 import (
    EXACT_NEXT_OBJECT,
    PRIMARY_VERDICT,
    SECONDARY_VERDICT,
    completion_payload,
    deterministic_json,
)


def status_text() -> str:
    return f"""# BHSM v14.41 source-free relative-frame gate

Primary verdict:

`{PRIMARY_VERDICT}`

Secondary verdict:

`{SECONDARY_VERDICT}`

The source-free stationary coexact ADM shift is a weighted square of the
Killing operator.  Its only zero modes are Killing fields.  On a round S3 cap,
the L=2 and L=3 eigenvalues are 5/R^2 and 12/R^2, so the classical universal
relative-frame branch is off.  The remaining universal route is a derived and
renormalized collective-fermion vacuum polarization on the physical compact
cap.

Exact next object:

`{EXACT_NEXT_OBJECT}`

BHSM is not complete.  No physical CKM, CP phase, mass, scale, or quantum
polarization is emitted.
"""


__all__ = ["completion_payload", "deterministic_json", "status_text"]
