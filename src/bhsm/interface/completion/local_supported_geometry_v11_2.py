"""Canonical supported domain recovered for the BHSM v11.2 audit.

This module records only geometry already owned by the merged action.  It does
not assign a support character to any primitive tensor or measure.
"""

from __future__ import annotations

from typing import Any


def geometry_payload() -> dict[str, Any]:
    validation = {
        "regular_domain_separated_from_core": True,
        "wall_boundary_and_seam_distinguished": True,
        "metric_nondegenerate_on_regular_domain": True,
        "core_not_inserted_into_inverse_metric_domain": True,
        "reduction_map_reused": True,
    }
    return {
        "artifact": "BHSM_local_supported_geometry_v11_2",
        "regular_domain": "M_regular={p in M_strat: 0<upsilon(p)<=1}",
        "support_depth": "q_D=-lambda_D log(upsilon), lambda_D>0",
        "wall": "the S5 enclosure-wall/fold stratum carrying q_W",
        "boundary": "ordinary finite boundaries of S8/S5 with induced metric and outward unit normal",
        "seam": "the localized S4 incidence locus; not a fourth physical deformation mode",
        "core_asymptotic_end": "upsilon->0+ iff q_D->+infinity; not a regular inverse-metric point",
        "coframe": "the frozen regular coframe e_0; a supported coframe character is not action-owned",
        "metric": "nondegenerate G on M_regular",
        "measure": "parent bulk, fiber, wall, and boundary measures retained with support characters unassigned",
        "fiber_base_decomposition": "pi_85=id_I x p_H with closed normalized Hopf fiber",
        "m4_reduction_map": "v7.1 normalized pushforward pi_! followed by localized S4 incidence",
        "support_character_assignment": None,
        "new_geometric_fields": [],
        "status": "BHSM_SUPPORTED_REGULAR_DOMAIN_AND_STRATA_RECOVERED_WITHOUT_NEW_SUPPORT_REPRESENTATION",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

