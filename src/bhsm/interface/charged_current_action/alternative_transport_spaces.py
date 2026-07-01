"""Alternative charged-current transport-space blockers."""

from __future__ import annotations

from .common import STATUS_MULTIPLE_SPACES, input_guard
from .transport_space_audit import audit_charged_current_transport_space


def audit_alternative_transport_spaces() -> dict[str, object]:
    space = audit_charged_current_transport_space()
    return {
        "audit": "alternative_transport_spaces",
        "spaces": space["spaces"],
        "status": STATUS_MULTIPLE_SPACES,
        "same_dimension_warning": "Same numerical dimension does not establish the physical source.",
        "claim_boundary": "Alternative assignments remain recorded until the normalized charged-current action selects one.",
        **input_guard(),
    }

