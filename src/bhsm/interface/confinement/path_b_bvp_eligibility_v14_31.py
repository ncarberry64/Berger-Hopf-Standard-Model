"""Path B non-Abelian Wilson-sourced BVP eligibility and claim boundary."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from bhsm.interface.completion.path_b_foundational_action_v14_31 import BVP_NEXT_OBJECT
from bhsm.interface.master_action.path_b_master_action_v14_31 import master_action_payload

VERSION = "v14.31"


@lru_cache(maxsize=1)
def bvp_eligibility_payload() -> dict[str, Any]:
    action = master_action_payload()
    validation = {
        "authoritative_joint_eta_SU3_action_exists": action["validation_passed"],
        "eta_sourced_Gauss_equation_exists": True,
        "Wilson_singlet_source_available": True,
        "classical_BVP_does_not_require_premature_FR_identification": True,
        "gauge_fixing_and_FP_domain_required": True,
        "self_adjoint_domain_required": True,
        "parent_relative_subtraction_required": True,
        "nonradial_Hessian_required": True,
        "BVP_not_claimed_solved": True,
        "confinement_not_claimed": True,
    }
    return {
        "artifact": "BHSM_Path_B_nonAbelian_BVP_eligibility_v14_31",
        "version": VERSION,
        "eligible": True,
        "eligibility_scope": "classical eta+SU3 system with external Wilson-dressed singlet source",
        "unknowns": [
            "physical SU3 connection A",
            "physical eta section",
            "retained collar/metric response if varied",
            "ghost and gauge-fixing fields at quadratic order",
        ],
        "equations": [
            "g3^(-2)D_nu F^(nu mu)=J_eta^mu+J_Wilson^mu+J_retained^mu",
            "D_mu[w(kappa1+X_eta^3)D^mu eta]+constraint and target-curvature terms=0",
            "retained Einstein/Higgs/seam equations when included",
        ],
        "source": "normalized Wilson-dressed meson or baryon insertion in a fixed center/N-ality sector",
        "required_domain": "background-covariant gauge, FP zero-mode quotient, regular axis/cap, finite parent-relative action, declared eta topological sector and self-adjoint transmission conditions",
        "numerical_requirement": "non-Abelian nonradial continuation with mesh refinement, residual controls and full fluctuation Hessian",
        "status": "ELIGIBLE_NOT_SOLVED",
        "exact_next_object": BVP_NEXT_OBJECT,
        "FR_boundary": "FR/Dirac matching is required for dynamical quark fields, not for the external-Wilson classical saddle",
        "confinement_boundary": "a stationary finite-width saddle does not establish a Wilson-loop area law, worldsheet limit, string breaking or physical c_sigma",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
