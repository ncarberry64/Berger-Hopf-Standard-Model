"""BHSM v10.0 Machian geometric-envelopment interface."""

from .completion_gate import (
    PRIMARY_VERDICT,
    VERSION,
    completion_status,
    materialize,
    status_to_markdown,
)
from .relational_completion_gate import completion_payload as relational_completion_payload
from .buoyancy_gate_v10_2 import completion_payload as buoyancy_completion_payload
from .deformation_selection_gate_v10_3 import completion_payload as deformation_completion_payload
from .common_envelopment_mode_v10_3 import common_mode_payload
from .three_mode_architecture_v10_3 import architecture_payload
from .final_completion_gate_v10_4 import completion_payload as v10_4_completion_payload

__all__ = [
    "PRIMARY_VERDICT",
    "VERSION",
    "completion_status",
    "materialize",
    "status_to_markdown",
    "relational_completion_payload",
    "buoyancy_completion_payload",
    "deformation_completion_payload",
    "common_mode_payload",
    "architecture_payload",
    "v10_4_completion_payload",
]
