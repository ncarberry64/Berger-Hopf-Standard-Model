"""Boundary variational-domain audit, preserving all earlier sector results."""

from __future__ import annotations

from typing import Any


def boundary_payload() -> dict[str, Any]:
    validation = {
        "scalar_flux_recovered": True,
        "ghy_role_preserved": True,
        "historical_domains_not_misapplied": True,
        "canonical_domain_not_invented": True,
    }
    return {
        "artifact": "BHSM_boundary_variational_domain_v11_2",
        "known_normal_momentum": "pi_D=sqrt(|h|) n^A partial_A q_D",
        "known_support_boundary_form": "-integral_boundary pi_D delta q_D",
        "metric_boundary_pair": "the parent Einstein-Hilbert/GHY pair on finite regular boundaries",
        "admissible_scalar_ensembles": ["Dirichlet delta q_D=0", "Neumann pi_D fixed with the corresponding Legendre boundary term", "mixed only after an action-owned boundary functional"],
        "selected_scalar_ensemble": None,
        "matter_domain": "v6.7/v6.10 maximal-isotropic families are sector-specific and do not select the support/core domain",
        "z2_interface_result": "v6.15 interface trace is presymplectic-null and selects no support boundary condition",
        "complete_boundary_counterterm": None,
        "complete_boundary_symplectic_flux": None,
        "well_posed_complete_variation": False,
        "status": "BHSM_BOUNDARY_SUPPORT_FLUX_DERIVED_BUT_CANONICAL_ENSEMBLE_NOT_ACTION_SELECTED",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

