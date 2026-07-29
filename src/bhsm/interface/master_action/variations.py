"""Levelwise variations and boundary conditions."""

from __future__ import annotations

from .common import envelope


def equation_rows() -> list[dict]:
    return [
        {"variation": "delta G_AB", "level": "S8", "equation": "kappa1 Einstein8_AB+(kappa0/2)G_AB-T_chi_AB-T_sigma_AB=0", "status": "LEVELWISE_DERIVED"},
        {"variation": "delta chi", "level": "S8", "equation": "nabla_A[Zchi(1+g sigma^2)nabla^A chi]=0", "status": "LEVELWISE_DERIVED"},
        {"variation": "delta sigma", "level": "S8", "equation": "Zsigma Box8 sigma-A0 sigma-G0 sigma^3-Zchi g sigma |dchi|^2=0", "status": "LEVELWISE_DERIVED"},
        {"variation": "delta g_eps", "level": "S5|4", "equation": "cap Einstein-scalar equations plus Pi_eps^{ab}+matcher reaction=0", "status": "RECOVERED_V6_CHAIN"},
        {"variation": "delta Lambda_eps", "level": "S5|4", "equation": "h_ab-gamma_eps,ab=0", "status": "EXACT_MATCHER"},
        {"variation": "delta h_ab", "level": "S5|4", "equation": "intrinsic B1 Einstein-matter equation+sum_eps Lambda_eps=0", "status": "LEVELWISE_CONDITIONAL"},
        {"variation": "delta N,delta N^a", "level": "S5|4", "equation": "Hamiltonian and momentum constraints", "status": "RECOVERED_D0_BLOCK"},
        {"variation": "delta A_i", "level": "S4eff", "equation": "D_mu(F_i^{mu nu}/g_i^2)=J_i^nu", "status": "EFT_DERIVED"},
        {"variation": "delta barPsi", "level": "S4eff", "equation": "i gamma^mu D_mu Psi-Y(H)Psi=0", "status": "EFT_DERIVED_DOMAIN_INPUT"},
        {"variation": "delta H", "level": "S4eff", "equation": "D_mu D^mu H+dV/dHdagger+Yukawa sources=0", "status": "EFT_DERIVED"},
        {"variation": "delta N_neu", "level": "DeltaS4", "equation": "-Z_neu D^2 N_neu-A_neu N_neu+g_neu R=0", "status": "EFFECTIVE_CONDITIONAL"},
    ]


def equations_payload() -> dict:
    return envelope(
        "BHSM_master_variational_equations_v7_0",
        equations=equation_rows(),
        every_term_has_variation=True,
        every_equation_has_action_term=True,
        Noether_identities=[
            "nabla_A(E_G^{AB}) equals scalar/carrier equations times gradients",
            "D_nu[D_mu(F^{mu nu}/g^2)-J^nu]=0 on fermion equations",
            "cap Hamiltonian/tangential identities close with matcher reaction",
        ],
        cross_level_variation_commutes_with_reduction=False,
        reason="R_* is undefined.",
    )


def boundary_rows() -> list[dict]:
    return [
        {"field": "G_AB", "condition": "fixed temporal endpoint metric or compact temporal support", "Green_form": "cancelled by coefficient-locked GHY if endpoints present", "status": "WELL_POSED_LEVELWISE"},
        {"field": "g_eps", "condition": "regular cap pole; matched induced metric on B1", "Green_form": "EH normal derivative cancelled by oriented GHY", "status": "WELL_POSED_RELATIVE_DOMAIN"},
        {"field": "sigma", "condition": "regular pole and fixed Dirichlet trace in D0", "Green_form": "Z5 n.sigma delta sigma", "status": "D0_CLOSED_LARGER_DOMAIN_OPEN"},
        {"field": "h_ab", "condition": "fixed in D0; active with exact matcher in parent relative domain", "Green_form": "intrinsic B1 variation plus reactions", "status": "EXPLICIT"},
        {"field": "A_i", "condition": "gauge quotient with absolute or relative elliptic boundary condition", "Green_form": "Tr(delta A wedge *F)", "status": "EFT_DOMAIN_INPUT"},
        {"field": "Psi", "condition": "maximal-isotropic subspace of Dirac boundary pairing", "Green_form": "int_boundary barPsi gamma.n deltaPsi", "status": "FAMILY_NOT_UNIQUELY_SELECTED"},
        {"field": "N_neu", "condition": "declared nonnegative response cone and compatible collar trace", "Green_form": "Z_neu deltaN n.DN", "status": "CONDITIONAL_NOT_PARENT_DERIVED"},
    ]


def boundary_payload() -> dict:
    return envelope(
        "BHSM_master_boundary_conditions_v7_0",
        boundary_conditions=boundary_rows(),
        cap_orientation_consistent=True,
        GHY_cancellation=True,
        matcher_variation_exact=True,
        unified_domain_exists=False,
    )
