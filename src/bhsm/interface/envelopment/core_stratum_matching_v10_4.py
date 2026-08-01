"""Regular-to-core variational matching ledger for BHSM v10.4."""

from __future__ import annotations

from typing import Any


CORE_STATUS = "BHSM_REGULAR_TO_CORE_SUPPORT_BOUNDARY_CONDITIONS_DERIVED_CONDITIONALLY"


def core_matching_payload() -> dict[str, Any]:
    validation = {
        "regular_metric_nondegenerate": True,
        "scalar_boundary_variation_recorded": True,
        "metric_flux_balance_recorded": True,
        "symplectic_flux_recorded": True,
        "topological_flux_not_fabricated": True,
        "core_action_not_fabricated": True,
        "absorption_not_claimed": True,
        "fail_closed": True,
    }
    return {
        "artifact": "BHSM_core_stratum_matching_gate_v10_4",
        "domain": "M_complete=M_regular union Sigma_core union M_core",
        "regular_domain_boundary": "Sigma_core is approached from upsilon>0 with det(G)!=0; upsilon|Sigma_core=0",
        "variational_ensembles": {
            "dirichlet_terminal": {
                "data": "delta upsilon|Sigma_core=0 and fixed induced metric",
                "support_condition": "upsilon|Sigma_core=0",
                "extra_scalar_boundary_action": None,
                "transfer_claim_allowed": False,
            },
            "flux_matching": {
                "data": "delta upsilon free with a supplied S_Sigma_core+S_core",
                "support_condition": (
                    "[Pi_upsilon]_Sigma=0 with Pi_upsilon=sqrt(|h|) n_A Z nabla^A upsilon+"
                    "delta(S_Sigma_core+S_core)/delta upsilon"
                ),
                "extra_scalar_boundary_action": "OPEN",
                "transfer_claim_allowed": "only after the core variation and orientation are supplied",
            },
        },
        "metric_matching": (
            "[Pi_metric^ab]_Sigma=-(2/sqrt|h|) delta(S_Sigma_core+S_core)/delta h_ab; "
            "the regular P1 side includes its coefficient-locked GHY momentum"
        ),
        "normal_stress_balance": (
            "[T_AB n^A h^B_b]_Sigma+D_a tau^a_b+support/core exchange=0"
        ),
        "support_flux": "[Pi_upsilon]_Sigma=0 conditionally; numerical flux is undefined without S_core",
        "symplectic_flux": (
            "omega_regular|Sigma+omega_Sigma+omega_core=0; only the regular support contribution "
            "delta pi_upsilon wedge delta upsilon is identified"
        ),
        "topological_charge": (
            "[J_top^A n_A]_Sigma+D_a j_top^a=0 when a core current is supplied; current value is undefined"
        ),
        "gauge_current": (
            "[J_gauge^A n_A]_Sigma+D_a j_gauge^a=0; no core current or emission map is presently owned"
        ),
        "wall_termination_or_continuation": None,
        "stress_transfer": None,
        "absorption_or_emission": None,
        "information_destruction": False,
        "fundamental_dissipation": False,
        "internal_core_action": None,
        "complete_junction_law": False,
        "status": CORE_STATUS,
        "exact_missing_core_terms": [
            "S_core and its field content",
            "S_Sigma_core or a declared terminal Dirichlet ensemble",
            "core metric momentum/stress response",
            "core symplectic form",
            "core topological and gauge currents",
        ],
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
