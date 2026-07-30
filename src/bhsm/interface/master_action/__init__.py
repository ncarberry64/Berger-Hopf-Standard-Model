"""BHSM master-action, observable-transport, and prediction-campaign API.

The v7.0 constants and v7.1 master-action report remain exported for
artifact compatibility. Current v7.3 completion constants and status are
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

CURRENT_VERSION = "v7.3"
CURRENT_MISSING_OBJECT = (
    "NONUNIVERSAL_BHSM_TO_LOCALIZED_PHYSICAL_SECTOR_ACTION_COUPLING"
)
CURRENT_VERDICT = (
    "BHSM_DISTINCT_PREDICTION_REQUIRES_NEW_BULK_BOUNDARY_"
    "COUPLING_NOT_PRESENT_IN_ACTION"
)


def observable_status_payload():
    """Return the current v7.2 status without eager module import."""
    from .observable_transport import status_report

    return status_report()


def observable_status_to_markdown(payload=None):
    """Render the current v7.2 status without eager module import."""
    from .observable_transport import status_to_markdown

    return status_to_markdown(payload)


def distinct_prediction_status_payload():
    """Return the current v7.3 prediction-campaign status."""
    from .distinct_prediction import status_report

    return status_report()


def distinct_prediction_status_to_markdown(payload=None):
    """Render the current v7.3 prediction-campaign status."""
    from .distinct_prediction import status_to_markdown

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
    "distinct_prediction_status_payload",
    "distinct_prediction_status_to_markdown",
    "frozen_hashes_match",
    "materialize",
    "observable_status_payload",
    "observable_status_to_markdown",
    "payloads",
    "status_payload",
    "status_to_markdown",
    "validate_model",
]
