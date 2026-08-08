"""Public completion/status gate for BHSM v14.40."""

from __future__ import annotations

from .matter_sourced_spin4_multipole_v14_40 import (
    EXACT_NEXT_OBJECT,
    PRIMARY_VERDICT,
    SECONDARY_VERDICT,
    completion_payload,
    deterministic_json,
)


def status_text() -> str:
    return f"""# BHSM v14.40 matter-sourced Spin(4) multipole gate

Primary verdict:

`{PRIMARY_VERDICT}`

Secondary verdict:

`{SECONDARY_VERDICT}`

The current radially equivariant FR eta rotor supplies only rigid L=1 frame dragging. Static Wilson insertions and diagonal stationary family occupations do not generate a connected L=2,L=3 source. Off-diagonal family coherence can carry the required magnetic transfers, but using it as the upstream source is circular until the collective Dirac dynamics selects that coherence.

Exact next object:

`{EXACT_NEXT_OBJECT}`

BHSM is not complete. No physical CKM, CP phase, mass, scale, or compact-cap shift eigenvalue is emitted.
"""


__all__ = ["completion_payload", "deterministic_json", "status_text"]
