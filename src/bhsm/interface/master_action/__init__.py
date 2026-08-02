"""BHSM master-action, transport, and vacuum-to-flavor audit API.

The v7.0 constants and v7.1 master-action report remain exported for
artifact compatibility. Current v11.1 completion constants and status are
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

from ..current_program_status import (
    CURRENT_VERSION,
    EXACT_NEXT_OBJECT as CURRENT_MISSING_OBJECT,
    PRIMARY_VERDICT as CURRENT_VERDICT,
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


def relational_envelopment_status_payload():
    """Return the current v10.1 relational-envelopment status."""
    from ..envelopment.relational_completion_gate import completion_payload

    return completion_payload()


def relational_envelopment_status_to_markdown(payload=None):
    """Render the current v10.1 relational-envelopment status."""
    from ..envelopment.relational_completion_gate import command_to_markdown

    wrapped = {
        "version": "v10.1",
        "command": "relational-envelopment-status",
        "primary_verdict": "BHSM_RELATIONAL_ENVELOPMENT_PARENT_ACTION_CONSTRAINTS_CONSTRUCTED_CONDITIONALLY",
        "section": relational_envelopment_status_payload() if payload is None else payload,
        "author_axiom_promoted_to_theorem": False,
        "frozen_predictions_changed": False,
        "physical_matrix_emitted": False,
        "next_exact_object": (
            "COVARIANT_ACTION_DERIVED_NORMAL_RADION_BUOYANCY_FUNCTIONAL_WITH_"
            "GLOBAL_CONSTRAINT_AND_LOCAL_ENVELOPMENT_BACKREACTION"
        ),
    }
    return command_to_markdown("relational-envelopment-status", wrapped)


def buoyancy_status_payload():
    """Return the current v10.2 Topological Buoyancy obstruction status."""
    from ..envelopment.buoyancy_gate_v10_2 import completion_payload

    return completion_payload()


def buoyancy_status_to_markdown(payload=None):
    """Render the current v10.2 Topological Buoyancy status."""
    from ..envelopment.buoyancy_gate_v10_2 import command_to_markdown

    return command_to_markdown("topological-buoyancy-status")


def deformation_domain_status_payload():
    """Return the historical v10.3 physical deformation-domain status."""
    from ..envelopment.deformation_selection_gate_v10_3 import completion_payload

    return completion_payload()


def deformation_domain_status_to_markdown(payload=None):
    """Render the historical v10.3 physical deformation-domain status."""
    from ..envelopment.deformation_selection_gate_v10_3 import command_to_markdown

    return command_to_markdown("deformation-selection-status")


def spacetime_removal_completion_status_payload():
    """Return the current v10.4 constrained depth/completion status."""
    from ..envelopment.final_completion_gate_v10_4 import completion_payload

    return completion_payload()


def spacetime_removal_completion_status_to_markdown(payload=None):
    """Render the current v10.4 constrained depth/completion status."""
    from ..envelopment.final_completion_gate_v10_4 import command_to_markdown

    return command_to_markdown("v10-4-final-completion-status")


def unified_physical_completion_status_payload():
    """Return the current v11.0 unified physical-completion status."""
    from ..envelopment.final_physical_gate_v11_0 import completion_payload

    return completion_payload()


def unified_physical_completion_status_to_markdown(payload=None):
    """Render the current v11.0 unified physical-completion status."""
    from ..envelopment.final_physical_gate_v11_0 import command_to_markdown

    return command_to_markdown("physical-completion-status-v11")


__all__ = [
    "ARTIFACT_FILES",
    "CURRENT_MISSING_OBJECT",
    "CURRENT_VERDICT",
    "CURRENT_VERSION",
    "MISSING_OBJECT",
    "VERDICT",
    "VERSION",
    "artifact_bytes",
    "buoyancy_status_payload",
    "buoyancy_status_to_markdown",
    "deformation_domain_status_payload",
    "deformation_domain_status_to_markdown",
    "spacetime_removal_completion_status_payload",
    "spacetime_removal_completion_status_to_markdown",
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
    "relational_envelopment_status_payload",
    "relational_envelopment_status_to_markdown",
    "unified_envelopment_status_payload",
    "unified_envelopment_status_to_markdown",
    "unified_physical_completion_status_payload",
    "unified_physical_completion_status_to_markdown",
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
