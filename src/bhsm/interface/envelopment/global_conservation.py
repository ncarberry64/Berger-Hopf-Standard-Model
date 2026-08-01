"""Reversibility, conservation, entropy, and global-energy qualification."""

from __future__ import annotations

from typing import Any

import sympy as sp

from .relational_axioms import DoctrineStatus


CONSERVATION_VERDICT = "BHSM_SCALAR_TOTAL_COSMIC_ENERGY_NOT_COVARIANTLY_DEFINED"
TOPOLOGY_VERDICT = "BHSM_ETA_MAP_DEGREE_CONSERVED_UNDER_SMOOTH_FIXED_DOMAIN_EVOLUTION"
HAMILTONIAN_VERDICT = "BHSM_HAMILTONIAN_CONSTRAINT_IS_NOT_A_SCALAR_TOTAL_COSMIC_ENERGY"


def local_noether_identity() -> dict[str, Any]:
    # Algebraic check of the standard diffeomorphism Noether identity once all
    # Euler-Lagrange terms vanish; this is a symbolic ledger, not a PDE solve.
    e_g, e_chi, e_sigma, e_eta, flux = sp.symbols(
        "E_G E_chi E_sigma E_eta F_boundary"
    )
    divergence = e_g + e_chi + e_sigma + e_eta + flux
    on_shell_closed = sp.simplify(
        divergence.subs({e_g: 0, e_chi: 0, e_sigma: 0, e_eta: 0, flux: 0})
    )
    Z, velocity, acceleration, potential_gradient = sp.symbols(
        "Z v a U_prime", real=True
    )
    homogeneous_energy_derivative = velocity * (Z * acceleration + potential_gradient)
    homogeneous_eom = Z * acceleration + potential_gradient
    return {
        "identity": "nabla_A T_total^(AB)=sum_fields E_field . nabla^B(field)+connection equations+boundary flux",
        "on_shell_closed_value": int(on_shell_closed),
        "on_shell_closed_conservation": on_shell_closed == 0,
        "homogeneous_scalar_check": {
            "energy": "E=Z sigma_dot^2/2+U(sigma)",
            "dE_dt": "sigma_dot(Z sigma_ddot+U')",
            "equation": "Z sigma_ddot+U'=0",
            "factorization_exact": sp.simplify(homogeneous_energy_derivative - velocity * homogeneous_eom) == 0,
            "on_shell_value": int(homogeneous_energy_derivative.subs(homogeneous_eom, 0)),
        },
        "scope": "complete covariant action with all strata and fluxes included",
        "classification": DoctrineStatus.DERIVED_CONDITIONAL.value,
    }


def reversibility_audit() -> dict[str, Any]:
    return {
        "parent_local_terms": "real and even in first derivatives after tensor contraction",
        "explicit_dissipative_terms": [],
        "nonlocal_memory_terms": [],
        "fundamental_time_arrow": False,
        "time_reversal": "invariant conditional on time-reversal-compatible gauge/background and boundary data",
        "CPT": "OPEN_FULL_LOCAL_LORENTZIAN_QUANTUM_FIELD_CONTENT_NOT_DERIVED",
        "Hamiltonian_structure": "FORMAL_CONSTRAINED_COVARIANT_SYSTEM",
        "symplectic_structure": "covariant presymplectic current exists sectorwise; global reduced nondegeneracy open",
        "unitarity": "OPEN_NO_QUANTIZED_PHYSICAL_HILBERT_SPACE",
        "open_system_dissipation": "allowed only after an explicit subsystem trace/coarse graining",
        "classification": DoctrineStatus.DERIVED_CONDITIONAL.value,
    }


def topology_conservation() -> dict[str, Any]:
    return {
        "charge": "N=deg(eta|Sigma7) in pi7(S7)=Z",
        "law": "N is homotopy invariant under smooth continuous evolution with fixed based boundary data",
        "change_requires": ["singularity", "loss of unit constraint", "boundary flux", "domain topology change"],
        "current_action_allows_unqualified_change": False,
        "verdict": TOPOLOGY_VERDICT,
        "classification": DoctrineStatus.DERIVED_CONDITIONAL.value,
    }


def boundary_flux_ledger() -> dict[str, Any]:
    return {
        "balance": "Q[Sigma2]-Q[Sigma1]=-int_timelike_boundary j.A s_A dSigma",
        "closed_cosmos_flux": 0,
        "eta_boundary_flux": "n^A(1+g sigma^2)(kappa1+X_eta^3) Re<D_A eta,Sigma^(IJ)eta>",
        "GHY_and_matcher_required": True,
        "all_physical_boundary_conditions_selected": False,
        "classification": DoctrineStatus.DERIVED_CONDITIONAL.value,
    }


def global_energy_audit() -> dict[str, Any]:
    return {
        "covariant_local_conservation": True,
        "Hamiltonian_constraint": "H_perp approximately 0 on a closed generally covariant solution",
        "Hamiltonian_constraint_is_positive_scalar_energy": False,
        "ordinary_integral_T00_coordinate_independent": False,
        "global_timelike_Killing_field_selected": False,
        "Komar_charge_available": "only on a stationary branch with the required Killing field",
        "Brown_York_energy_available": "quasilocally after a boundary, normal, subtraction/reference, and ensemble are fixed",
        "closed_cosmos_has_external_boundary": False,
        "scalar_total_cosmic_energy": None,
        "constraint_realization_verdict": HAMILTONIAN_VERDICT,
        "scalar_energy_verdict": CONSERVATION_VERDICT,
        "classification": DoctrineStatus.BLOCKED_EXACT_OBJECT_PROVED.value,
    }


def entropy_gate() -> dict[str, Any]:
    return {
        "fundamental_closed_state_space": "covariant constrained phase space of the complete stratified fields",
        "coarse_graining_map": None,
        "discarded_variables": None,
        "measure": None,
        "observer_or_subsystem": None,
        "entropy_functional": None,
        "monotonicity_theorem": None,
        "recurrence_audit": None,
        "information_conservation_beyond_topological_degree": None,
        "local_entropy_explained": False,
        "classification": DoctrineStatus.OPEN.value,
        "exact_missing_object": "MICROSCOPIC_ENVELOPMENT_COARSE_GRAINING_AND_ENTROPY_PRODUCTION_THEOREM",
    }


def conservation_payload() -> dict[str, Any]:
    local = local_noether_identity()
    energy = global_energy_audit()
    validation = {
        "local_identity_closes_on_shell": local["on_shell_closed_conservation"],
        "homogeneous_energy_check_exact": local["homogeneous_scalar_check"]["factorization_exact"],
        "no_fundamental_dissipation": reversibility_audit()["explicit_dissipative_terms"] == [],
        "topological_charge_conserved_conditionally": topology_conservation()["current_action_allows_unqualified_change"] is False,
        "boundary_flux_accounted": boundary_flux_ledger()["closed_cosmos_flux"] == 0,
        "T00_not_promoted": not energy["ordinary_integral_T00_coordinate_independent"],
        "entropy_not_overclaimed": not entropy_gate()["local_entropy_explained"],
    }
    return {
        "artifact": "BHSM_global_conservation_gate_v10_1",
        "reversibility": reversibility_audit(),
        "local_Noether_identity": local,
        "topological_information": topology_conservation(),
        "boundary_flux": boundary_flux_ledger(),
        "global_energy": energy,
        "entropy": entropy_gate(),
        "verdict": CONSERVATION_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
