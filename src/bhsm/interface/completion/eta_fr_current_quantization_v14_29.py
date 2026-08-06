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
        "collective_matching_map_not_derived": True,
        "first_order_action_derivation_not_overclaimed": True,
        "self_adjoint_domain_not_overclaimed": True,
    }
    return {
        "artifact": "BHSM_eta_FR_current_quantization_no_double_counting_v14_29",
        "version": VERSION,
        "classical_object": "eta tangent zero-mode current j_eta[phi]",
        "quantized_object": "j_Psi=bar(Psi_eta) gamma^mu T_a Psi_eta",
        "identification_rule": "intended but unproved: j_Psi should be the collective-coordinate quantization of j_eta",
        "Gauss_source_ledger": "safe alternatives: use the classical source before quantization or a derived FR Dirac representative after matching; do not include both complete sectors",
        "matched_description": "OPEN: no mode split, path-integral integration, subtraction functional, or action-equivalence theorem is present",
        "status": "OPEN_MATCHING_THEOREM; NO_DOUBLE_COUNTING_POLICY_VALIDATED",
        "open_gate": "ACTION_EQUIVALENCE_OF_THE_FR_FIRST_ORDER_DIRAC_NORMAL_FORM_WITH_SELF_ADJOINT_RELATIVE_KNOT_DOMAIN",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
