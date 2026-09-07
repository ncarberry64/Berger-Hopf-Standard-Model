"""Attach the existing N12 canonical stop to the AE4 endpoint domain."""

from __future__ import annotations

from typing import Any

from bhsm.interface.ae4_stratified_dirac_zeta_induced_owner import ACTION_VERSION


CLASSIFICATION = "AE4_CURRENT_C2_CANONICAL_STOP_DOMAIN_BRIDGE"


def canonical_stop_domain_bridge(
    *,
    exact_stop_certified: bool,
    stop_transverse: bool,
    first_hit_interval_certified: bool,
    open_stop_stratum_derived: bool,
    endpoint_domain_owned: bool,
    canonical_stop_uses_friedrichs: bool,
) -> dict[str, Any]:
    """Return the fail-closed endpoint consequence of the existing stop.

    A canonical stop selects the Friedrichs closure of the retained
    nonnegative minimal form.  It therefore does not require an independent
    finite child Weyl load.  Motion of the stop and variation of the bulk
    coefficients remain part of the operator jet and are not set to zero by
    this domain statement.
    """

    conditions = {
        "exact_forward_canonical_stop_certified": bool(exact_stop_certified),
        "canonical_stop_transverse": bool(stop_transverse),
        "canonical_first_hit_interval_certified": bool(
            first_hit_interval_certified
        ),
        "nonempty_open_stop_reaching_reset_stratum_derived": bool(
            open_stop_stratum_derived
        ),
        "endpoint_domain_class_action_owned": bool(endpoint_domain_owned),
        "canonical_stop_endpoint_is_friedrichs": bool(
            canonical_stop_uses_friedrichs
        ),
    }
    selected = all(conditions.values())
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "conditions": conditions,
        "canonical_stop_branch_available": selected,
        "terminal_domain": (
            "FRIEDRICHS_FORM_CLOSURE_OF_RETAINED_NONNEGATIVE_MINIMAL_FORM"
            if selected
            else "OPEN"
        ),
        "factorized_terminal_graph": (
            "DIRICHLET_FORM_CORE_LIMIT_terminal_load_None"
            if selected
            else "OPEN"
        ),
        "independent_finite_terminal_load_required": False if selected else None,
        "independent_finite_terminal_load_HS_jets_required": (
            False if selected else None
        ),
        "moving_stop_and_bulk_coefficient_jets_required": True,
        "finite_proof_core_edge_promoted_to_stop": False,
        "event_branch_child_Weyl_family_reclassified_as_closed": False,
        "physical_stop_matched_operator_path_evaluated": False,
        "physical_maximal_history_HS_block_derived": False,
    }


def claim_boundary() -> dict[str, bool]:
    return {
        "AE4_CURRENT_C2_CANONICAL_STOP_DOMAIN_BRIDGE_DERIVED": True,
        "AE4_CURRENT_C2_NONEMPTY_OPEN_CANONICAL_STOP_STRATUM_DERIVED": True,
        "AE4_CURRENT_C2_CANONICAL_STOP_FRIEDRICHS_ENDPOINT_SELECTED": True,
        "AE4_CURRENT_C2_STOP_BRANCH_INDEPENDENT_FINITE_TAIL_LOAD_REQUIRED": False,
        "AE4_CURRENT_C2_STOP_MATCHED_OPERATOR_PATH_EVALUATED": False,
        "AE4_CURRENT_C2_STOP_MOVING_ENDPOINT_HS_JETS_DERIVED": False,
        "AE4_CURRENT_C2_EVENT_BRANCH_CHILD_LOAD_AND_HS_JETS_DERIVED": False,
        "AE4_CURRENT_C2_MAXIMAL_HISTORY_RETARDED_HS_CALDERON_BLOCK_DERIVED": False,
        "AE4_E1_FULL_CORE_HS_HESSIAN_DERIVED": False,
        "PHYSICAL_ENCAPSULATION_IDENTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "canonical_stop_domain_bridge",
    "claim_boundary",
]
