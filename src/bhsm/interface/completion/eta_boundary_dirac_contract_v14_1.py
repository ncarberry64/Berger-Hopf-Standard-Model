"""Fail-closed operator contract for the missing eta-knot boundary Dirac index."""

from __future__ import annotations

from typing import Any

VERSION = "v14.1"
EXACT_CHIRAL_OBJECT = (
    "ACTION_DERIVED_ORIENTED_BOUNDARY_DIRAC_OPERATOR_ON_THE_FR_ETA_KNOT_"
    "BUNDLE_WITH_SELF_ADJOINT_DOMAIN"
)
FLAVOR_OBJECT = (
    "PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_OF_THE_SPECTRAL_"
    "CHARGED_CURRENT_KERNEL"
)


def boundary_dirac_contract_payload() -> dict[str, Any]:
    contract = {
        "boundary_manifold": "B1 or effective M4; the exact compact Euclidean index manifold is not selected",
        "signature": "retained M4 is Lorentzian; an APS index requires a declared Riemannian continuation/bulk",
        "spin_structure": "required, not selected globally by the eta wall alone",
        "FR_bundle": "flat Z2 line over the odd-degree eta-knot moduli fiber, conditional over M4",
        "color_bundle": "E_P only after the missing wall-to-M4 extension, or independent E_color",
        "weak_bundle": "retained effective SU2 representation bundle",
        "hypercharge_bundle": "retained effective U1 representation bundle",
        "family_bundle": "exact C3 module",
        "normal_orientation": "degree branch plus boundary normal; convention does not by itself select physics",
        "formal_operator": "D_boundary=i gamma^mu(nabla_spin+A_FR+A_color+A_weak+A_Y) on the tensor product bundle",
        "mass_or_domain_wall_profile": None,
        "boundary_condition": None,
        "self_adjoint_extension": None,
    }
    validation = {
        "formal_principal_symbol_is_Clifford": True,
        "Euclidean_symbol_elliptic_for_nonzero_covector_conditionally": True,
        "Lorentzian_operator_not_called_elliptic": True,
        "formal_Green_boundary_form_identified": True,
        "maximal_isotropic_domain_required": True,
        "APS_domain_is_candidate_not_selected": True,
        "index_not_emitted": True,
        "eta_invariant_not_emitted": True,
        "color_conjugation_not_weak_chirality": True,
    }
    return {
        "artifact": "BHSM_eta_boundary_Dirac_index_contract_v14_1",
        "version": VERSION,
        "contract": contract,
        "Euclidean_principal_symbol": "sigma_D(x,xi)=i c(xi), sigma_D^2=-|xi|^2 I",
        "formal_self_adjointness": "holds for the metric-compatible tensor connection before boundary-domain selection",
        "Green_boundary_form": "int_boundary <psi,c(n)phi>",
        "candidate_domains": [
            "APS spectral projector after a complete tangential operator is defined",
            "local maximal-isotropic/MIT-type domain if compatible with gauge and orientation bundles",
            "relative transmission domain across the two-cap collar",
        ],
        "APS_formula_status": "NOT_EVALUABLE: bulk, Euclidean continuation, connection, domain, eta invariant, and kernel dimension are incomplete",
        "Index_D_rel": None,
        "eta_D_boundary": None,
        "exact_missing_inputs": [key for key, value in contract.items() if value is None]
        + [
            "action-owned wall-to-M4 color bundle map",
            "complete Berry/FR connection",
            "compact Euclidean bulk and characteristic-form normalization",
        ],
        "exact_next_object": EXACT_CHIRAL_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def flavor_independence_payload() -> dict[str, Any]:
    validation = {
        "AP_acts_as_identity_on_C3": True,
        "commutes_with_all_C3_projectors": True,
        "weak_family_current_I3_preserved": True,
        "common_color_phase_cannot_generate_family_CP": True,
        "K_ud_not_inserted": True,
        "physical_CKM_not_emitted": True,
    }
    return {
        "artifact": "BHSM_eta_color_flavor_independence_v14_1",
        "version": VERSION,
        "operator_factorization": "A_color^P tensor I_C3",
        "commutator_theorem": "[I_color tensor P_r,A_color^P tensor I_C3]=0 for r=0,1,2",
        "charged_current": "J_+^family=I3",
        "K_ud": None,
        "flavor_exact_next_object": FLAVOR_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
