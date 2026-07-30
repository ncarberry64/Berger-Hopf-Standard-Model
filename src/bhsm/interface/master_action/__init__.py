"""BHSM master-action, transport, and curvature-response API.

The v7.0 constants and v7.1 master-action report remain exported for
artifact compatibility. Current v8.0 completion constants and status are
exposed separately.
"""

from .common import MISSING_OBJECT, VERDICT, VERSION
from .report import (
    ARTIFACT_FILES,
    artifact_bytes,
    frozen_file_sha256,
    frozen_hashes_match,
    materialize,
    payloads,
    status_payload,
    status_to_markdown,
)
from .validation import validate_model

CURRENT_VERSION = "v8.0"
CURRENT_MISSING_OBJECT = (
    "FAMILY_RESOLVING_ACTION_INCIDENCE_BEYOND_THE_"
    "UNIVERSAL_CURVATURE_SCALAR"
)
CURRENT_VERDICT = (
    "BHSM_MASS_RESPONSE_BLOCKED_BY_UNIVERSAL_RESPONSE_WITH_NO_"
    "FAMILY_RESOLUTION"
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


def mass_curvature_response_status_payload():
    """Return the current v8.0 mass-curvature response status."""
    from .mass_curvature_response import status_report

    return status_report()


def mass_curvature_response_status_to_markdown(payload=None):
    """Render the current v8.0 mass-curvature response status."""
    from .mass_curvature_response import status_to_markdown

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
    "frozen_file_sha256",
    "frozen_hashes_match",
    "materialize",
    "mass_curvature_response_status_payload",
    "mass_curvature_response_status_to_markdown",
    "observable_status_payload",
    "observable_status_to_markdown",
    "payloads",
    "status_payload",
    "status_to_markdown",
    "validate_model",
]
