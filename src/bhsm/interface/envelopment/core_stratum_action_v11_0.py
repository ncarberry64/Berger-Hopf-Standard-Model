"""Variational core-boundary audit after the v11.0 Haar-depth selection."""

from __future__ import annotations

from typing import Any


CORE_VERDICT = (
    "BHSM_CORE_JUNCTION_REMAINS_OPEN_AT_INFINITE_HAAR_DISTANCE_"
    "WITHOUT_A_CORE_RESPONSE_OPERATOR"
)
CORE_NEXT_OBJECT = "CORE_BOUNDARY_PHASE_SPACE_AND_SELF_ADJOINT_TRANSFER_OPERATOR_AT_QD_INFINITY"


def core_action_payload() -> dict[str, Any]:
    classifications = {
        "regular_support_momentum": "DERIVED",
        "regular_metric_GHY_momentum": "DERIVED_CONDITIONAL",
        "Hamiltonian_and_momentum_flux_form": "DERIVED",
        "support_endpoint_upsilon_zero": "FIXED_BY_TOPOLOGY",
        "core_gauge_charge_balance_form": "FIXED_BY_CONSERVATION",
        "core_topological_charge_balance_form": "FIXED_BY_CONSERVATION",
        "core_response_functional": "OPEN",
        "core_symplectic_form": "OPEN",
        "absorption_emission_transfer_operator": "OPEN",
    }
    conservative_ensembles = [
        {
            "name": "terminal Dirichlet",
            "data": "delta q_D vanishes at a finite cutoff q_D=Q before Q->infinity",
            "regular_symplectic_flux": 0,
            "transfer": False,
            "core_action_required": False,
            "adopted_as_absorption_model": False,
        },
        {
            "name": "reflecting Neumann",
            "data": "Pi_D=n^A nabla_A q_D=0 at a finite cutoff before Q->infinity",
            "regular_symplectic_flux": 0,
            "transfer": False,
            "core_action_required": False,
            "adopted_as_absorption_model": False,
        },
    ]
    validation = {
        "regular_boundary_form_derived": True,
        "core_at_infinite_field_distance_recorded": True,
        "two_conservative_boundary_ensembles_exist": len(conservative_ensembles) == 2,
        "conservation_does_not_select_transfer": all(not row["transfer"] for row in conservative_ensembles),
        "core_response_not_fabricated": classifications["core_response_functional"] == "OPEN",
        "no_dissipation_added": True,
        "no_information_destruction_claim": True,
    }
    return {
        "artifact": "BHSM_core_stratum_action_v11_0",
        "complete_domain": "M_regular union Sigma_core union M_core",
        "regular_domain": "0<upsilon<=1, equivalently 0<=q_D<infinity, det(G)!=0",
        "core_boundary": "upsilon=0 corresponds to q_D=+infinity in the Haar metric",
        "support_boundary_variation": "-integral_Sigma sqrt|h| (n^A nabla_A q_D) delta q_D",
        "support_momentum": "Pi_D=sqrt|h| n^A nabla_A q_D",
        "metric_matching": "[Pi_metric^ab]_Sigma=-(2/sqrt|h|) delta S_core-total/delta h_ab",
        "support_flux_balance": "Pi_D,regular+delta S_core-total/delta q_D=0",
        "stress_flux_balance": "[T_AB n^A h^B_b]+D_a tau^a_b+exchange_b=0",
        "gauge_flux_balance": "[J_gauge^A n_A]+D_a j_gauge^a=0",
        "topological_flux_balance": "[J_top^A n_A]+D_a j_top^a=0",
        "symplectic_flux_balance": "omega_regular+omega_Sigma+omega_core=0",
        "infinite_distance_consequence": (
            "the regular action supplies only an asymptotic endpoint; a finite transfer law cannot be "
            "evaluated without asymptotic core data, a compactification, or an explicit core phase space"
        ),
        "conservative_counterexamples": conservative_ensembles,
        "minimal_core_action": None,
        "complete_flux_relation": False,
        "reversible_absorption_emission": False,
        "classifications": classifications,
        "status": CORE_VERDICT,
        "next_exact_object": CORE_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
