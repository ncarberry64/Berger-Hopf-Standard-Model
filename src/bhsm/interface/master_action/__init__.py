"""BHSM master-action API.

The v7.0 constants remain exported for artifact compatibility.  Current
v7.1 status is exposed by ``CURRENT_*`` and the status-report functions.
"""

from .common import MISSING_OBJECT, VERDICT, VERSION
from .reduction import (
    FINAL_VERDICT as CURRENT_VERDICT,
    NEXT_EXACT_OBJECT as CURRENT_MISSING_OBJECT,
    VERSION as CURRENT_VERSION,
)
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
    "payloads",
    "status_payload",
    "status_to_markdown",
    "validate_model",
]
