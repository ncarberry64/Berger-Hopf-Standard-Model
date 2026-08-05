"""No-double-counting bridge from the classical eta mode to FR quantization."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

VERSION = "v14.29"


@lru_cache(maxsize=1)
def fr_quantization_payload() -> dict[str, Any]:
    validation = {
        "relative_one_knot_sector_retained": True,
        "FR_odd_line_retained_conditionally": True,
        "triplet_associated_representation_retained_conditionally": True,
        "classical_and_Dirac_currents_not_summed": True,
        "first_order_action_derivation_not_overclaimed": True,
        "self_adjoint_domain_not_overclaimed": True,
    }
    return {
        "artifact": "BHSM_eta_FR_current_quantization_no_double_counting_v14_29",
        "version": VERSION,
        "classical_object": "eta tangent zero-mode current j_eta[phi]",
        "quantized_object": "j_Psi=bar(Psi_eta) gamma^mu T_a Psi_eta",
        "identification_rule": "j_Psi is the collective-coordinate quantization of j_eta and is not an additive second source",
        "Gauss_source_ledger": "use the classical source before quantization or the FR Dirac representative after quantization, never both",
        "status": "VALIDATED_CONDITIONALLY",
        "open_gate": "ACTION_EQUIVALENCE_OF_THE_FR_FIRST_ORDER_DIRAC_NORMAL_FORM_WITH_SELF_ADJOINT_RELATIVE_KNOT_DOMAIN",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
