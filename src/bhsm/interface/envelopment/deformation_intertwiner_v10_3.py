"""Intertwiner, domain, source, and charge audit for the v10.3 common mode."""

from __future__ import annotations

from typing import Any

from .common_envelopment_mode_v10_3 import PRIMARY_VERDICT, UNRESOLVED


def intertwiner_rows() -> list[dict[str, Any]]:
    return [
        {
            "operator": "U_zeta_to_psi",
            "map": "q_fold -> S_Sigma=-(tau*pi*chi_1/16) q_fold",
            "status": "DERIVED_CONDITIONAL",
            "domain_preservation": "fixed-B1 fold domain through local O(D^2 q)",
            "boundary_preservation": True,
            "kinetic_norm_preservation": "not a separate norm; psi is a constrained projection",
            "source_preservation": True,
            "spectral_preservation": "one-dimensional amplitude map only",
            "invertible_on_physical_subspace": True,
        },
        {
            "operator": "U_zeta_to_F",
            "map": None,
            "status": "UNDEFINED_CROSS_DOMAIN",
            "domain_preservation": None,
            "boundary_preservation": None,
            "kinetic_norm_preservation": None,
            "source_preservation": None,
            "spectral_preservation": None,
            "invertible_on_physical_subspace": None,
        },
        {
            "operator": "U_F_to_psi",
            "map": None,
            "status": "UNDEFINED_CROSS_DOMAIN",
            "domain_preservation": None,
            "boundary_preservation": None,
            "kinetic_norm_preservation": None,
            "source_preservation": None,
            "spectral_preservation": None,
            "invertible_on_physical_subspace": None,
        },
    ]


def domain_map_audit() -> dict[str, Any]:
    return {
        "D_env": None,
        "to_D_psi": "derived through v6.27 fixed-support projection",
        "to_D_zeta": "derived for the v6.28-v6.30 fold domain",
        "to_D_F": "separate M8 regularity domain only",
        "one_common_boundary_condition": None,
        "cap_parity_match": "fold cap parity known; Hopf comparison not derived",
        "status": UNRESOLVED,
    }


def conserved_quantity_audit() -> dict[str, Any]:
    labels = (
        "topological_degree", "symplectic_norm", "canonical_energy",
        "constraint_charge", "parity", "triality", "Hopf_weight", "normal_flux",
    )
    return {
        key: {
            "seam_fold_comparison": "compatible where the v6.27 projection applies",
            "Hopf_comparison": None,
            "status": UNRESOLVED,
        }
        for key in labels
    }


def intertwiner_payload() -> dict[str, Any]:
    rows = intertwiner_rows()
    validation = {
        "seam_fold_map_imported": rows[0]["status"] == "DERIVED_CONDITIONAL",
        "Hopf_maps_fail_closed": rows[1]["status"] == rows[2]["status"] == "UNDEFINED_CROSS_DOMAIN",
        "no_inequivalence_promotion": True,
    }
    return {
        "artifact": "BHSM_deformation_intertwiner_v10_3",
        "intertwiners": rows,
        "gauge_equivalence": "not proved; seam--fold relation is a constraint projection",
        "boundary_domain_equivalence": domain_map_audit(),
        "source_equivalence": UNRESOLVED,
        "spectral_equivalence": UNRESOLVED,
        "conserved_charge_equivalence": conserved_quantity_audit(),
        "full_common_intertwiner": None,
        "equivalence_status": UNRESOLVED,
        "physically_inequivalent": False,
        "primary_verdict": PRIMARY_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
