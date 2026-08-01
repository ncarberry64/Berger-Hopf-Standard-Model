"""BHSM v10.0 Machian geometric-envelopment interface."""

from .completion_gate import (
    PRIMARY_VERDICT,
    VERSION,
    completion_status,
    materialize,
    status_to_markdown,
)

__all__ = [
    "PRIMARY_VERDICT",
    "VERSION",
    "completion_status",
    "materialize",
    "status_to_markdown",
]
