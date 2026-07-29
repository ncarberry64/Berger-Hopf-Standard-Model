"""BHSM master-action and observable-transport API.

The v7.0 constants and v7.1 master-action report remain exported for
artifact compatibility. Current v7.2 completion constants and status are
exposed separately.
"""

from .common import MISSING_OBJECT, VERDICT, VERSION
from .report import (
    ARTIFACT_FILES,
    artifact_bytes,
    frozen_hashes_match,
    materialize,
    payloads,
    status_payload,
    status_to_markdown,
)
from .validation import validate_model

CURRENT_VERSION = "v7.2"
CURRENT_MISSING_OBJECT = (
    "ABSENCE_OF_DISTINCT_ACTION_DERIVED_FALSIFIABLE_PREDICTION"
)
CURRENT_VERDICT = (
    "BHSM_RELEASE_COMPLETION_BLOCKED_BY_ABSENCE_OF_DISTINCT_"
    "ACTION_DERIVED_FALSIFIABLE_PREDICTION"
)


def observable_status_payload():
    """Return the current v7.2 status without eager module import."""
    from .observable_transport import status_report

    return status_report()


def observable_status_to_markdown(payload=None):
    """Render the current v7.2 status without eager module import."""
    from .observable_transport import status_to_markdown

    return status_to_markdown(payload)

__all__ = [
    "ARTIFACT_FILES",
    "CURRENT_MISSING_OBJECT",
    "CURRENT_VERDICT",
    "CURRENT_VERSION",
    "MISSING_OBJECT",
    "VERDICT",
    "VERSION",
    "artifact_bytes",
    "frozen_hashes_match",
    "materialize",
    "observable_status_payload",
    "observable_status_to_markdown",
    "payloads",
    "status_payload",
    "status_to_markdown",
    "validate_model",
]
