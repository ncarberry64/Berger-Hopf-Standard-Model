"""Report the physical normalization gate without introducing a unit anchor."""

from __future__ import annotations

from .common import no_empirical_inputs


def audit_physical_normalization() -> dict[str, object]:
    return {
        "audit": "physical_normalization_gate",
        "status": "OPEN_MISSING_PHYSICAL_NORMALIZATION",
        "required_objects": [
            "normalized boundary measure",
            "charged and neutral stiffness unit maps",
            "cross-scale transport normalization",
            "gauge/scalar action normalization",
        ],
        "physical_unit_map_available": False,
        "dimensionful_prediction_produced": False,
        "claim_boundary": "Exact dimensionless incidence identities do not supply a physical unit map.",
        **no_empirical_inputs(),
    }
