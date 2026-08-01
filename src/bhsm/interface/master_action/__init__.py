"""BHSM master-action, transport, and vacuum-to-flavor audit API.

The v7.0 constants and v7.1 master-action report remain exported for
artifact compatibility. Current v10.0 completion constants and status are
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

CURRENT_VERSION = "v10.0"
CURRENT_MISSING_OBJECT = (
    "ACTION_SELECTED_GAUGE_DRESSED_CHARGED_SELF_ENVELOPMENT_RELATIVE_"
    "PERIODIC_ORBIT_WITH_LOCAL_CHIRAL_TRANSGRESSION"
)
CURRENT_VERDICT = (
    "BHSM_DYNAMIC_ENVELOPMENT_ACTION_AND_COMPLETION_ARCHITECTURE_"
    "CONSTRUCTED_CONDITIONALLY"
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


def mode_resolved_curvature_status_payload():
    """Return the current v8.1 mode-resolved curvature status."""
    from .mode_resolved_curvature_incidence import status_report

    return status_report()


def mode_resolved_curvature_status_to_markdown(payload=None):
    """Render the current v8.1 mode-resolved curvature status."""
    from .mode_resolved_curvature_incidence import status_to_markdown

    return status_to_markdown(payload)


def generation_projector_action_status_payload():
    """Return the current v8.2 projector-to-action attachment status."""
    from .generation_projector_action_attachment import status_report

    return status_report()


def generation_projector_action_status_to_markdown(payload=None):
    """Render the current v8.2 projector-to-action attachment status."""
    from .generation_projector_action_attachment import status_to_markdown

    return status_to_markdown(payload)


def classical_mode_stress_status_payload():
    """Return the current v8.3 classical mode-stress status."""
    from .classical_mode_stress_incidence import status_report

    return status_report()


def classical_mode_stress_status_to_markdown(payload=None):
    """Render the current v8.3 classical mode-stress status."""
    from .classical_mode_stress_incidence import status_to_markdown

    return status_to_markdown(payload)


def eight_dimensional_vacuum_flavor_status_payload():
    """Return the current v9.0 action-selected vacuum/flavor status."""
    from .eight_dimensional_vacuum_flavor_completion import status_report

    return status_report()


def eight_dimensional_vacuum_flavor_status_to_markdown(payload=None):
    """Render the current v9.0 action-selected vacuum/flavor status."""
    from .eight_dimensional_vacuum_flavor_completion import status_to_markdown

    return status_to_markdown(payload)


def geometry_only_geon_fr_carrier_status_payload():
    """Return the current v9.1 geometry-only completion status."""
    from .geometry_only_geon_fr_carrier_completion import status_report

    return status_report()


def geometry_only_geon_fr_carrier_status_to_markdown(payload=None):
    """Render the current v9.1 geometry-only completion status."""
    from .geometry_only_geon_fr_carrier_completion import status_to_markdown

    return status_to_markdown(payload)


def unified_envelopment_status_payload():
    """Return the current v10.0 unified-envelopment status."""
    from ..envelopment.completion_gate import completion_status

    return completion_status()


def unified_envelopment_status_to_markdown(payload=None):
    """Render the current v10.0 unified-envelopment status."""
    from ..envelopment.completion_gate import status_to_markdown

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
    "classical_mode_stress_status_payload",
    "classical_mode_stress_status_to_markdown",
    "distinct_prediction_status_payload",
    "distinct_prediction_status_to_markdown",
    "eight_dimensional_vacuum_flavor_status_payload",
    "eight_dimensional_vacuum_flavor_status_to_markdown",
    "frozen_file_sha256",
    "frozen_hashes_match",
    "geometry_only_geon_fr_carrier_status_payload",
    "geometry_only_geon_fr_carrier_status_to_markdown",
    "unified_envelopment_status_payload",
    "unified_envelopment_status_to_markdown",
    "materialize",
    "mass_curvature_response_status_payload",
    "mass_curvature_response_status_to_markdown",
    "mode_resolved_curvature_status_payload",
    "mode_resolved_curvature_status_to_markdown",
    "observable_status_payload",
    "observable_status_to_markdown",
    "generation_projector_action_status_payload",
    "generation_projector_action_status_to_markdown",
    "payloads",
    "status_payload",
    "status_to_markdown",
    "validate_model",
]
