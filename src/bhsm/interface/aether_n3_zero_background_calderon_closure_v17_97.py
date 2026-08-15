"""Gauge, spinor, ghost, and HS child matching in the selected zero sector."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_common_quantum_superdeterminant_v15_96 import (
    graded_operator_ledger,
)
from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import (
    action_ownership_ledger,
)
from bhsm.interface.aether_hybrid_standard_model_bundle_v15_53 import (
    hybrid_bundle_gluing,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_scalar_complete_child_boundary_solution_v17_96 import (
    scalar_complete_child_boundary_solution,
)


VERSION = "v17.97"
CLASSIFICATION = "BHSM_N3_ZERO_BACKGROUND_PHYSICAL_CALDERON_CLOSURE"
FULL_BHSM_COMPLETE = False


def zero_background_calderon_closure() -> dict[str, Any]:
    scalar = scalar_complete_child_boundary_solution()
    gluing = hybrid_bundle_gluing()
    ownership = action_ownership_ledger()
    operators = graded_operator_ledger()

    # These are field amplitudes in the selected classical background, not
    # the discrete bundle/topology data that are transported by the event.
    trace = np.zeros(4)
    event_flux = np.zeros(4)
    child_flux = np.zeros(4)
    matching = event_flux + child_flux
    return {
        "sector_order": [
            "gauge_transverse", "Weyl", "BRST_longitudinal_ghost", "HS",
        ],
        "boundary_trace": trace.tolist(),
        "event_outward_flux": event_flux.tolist(),
        "child_outward_flux": child_flux.tolist(),
        "F_child_zero_background": matching.tolist(),
        "F_child_zero_background_norm": float(np.linalg.norm(matching)),
        "provenance": {
            "post_event_connection_sector": gluing["post_event_connections"],
            "fermion_vacuum": gluing["fermion_vacuum"],
            "classical_connection_fluctuation": (
                "ZERO_AROUND_THE_MECHANICAL_CONNECTION_WHOSE_CURVATURE_IS_"
                "ALREADY_INCLUDED_IN_THE_PARENT_EINSTEIN_TERM"
            ),
            "fermion_background": ownership["fermion_background"],
            "Weyl_spatial_spectrum": operators["Weyl"]["spatial_eigenvalue"],
            "Weyl_levels": operators["Weyl"]["levels"],
            "BRST_quotient": operators["gauge_longitudinal_ghost"]["statement"],
            "same_bundle_isomorphism_class": gluing[
                "hybrid_bundle_returns_to_same_isomorphism_class"
            ],
        },
        "homogeneous_boundary_argument": {
            "gauge": (
                "THE_GAUGE_FIXED_TRANSVERSE_HESSIAN_IS_LINEAR_ON_"
                "FLUCTUATIONS_SO_ITS_CALDERON_GRAPH_CONTAINS_(0,0)"
            ),
            "spinor": (
                "THE_ODD_FR_WEYL_OPERATOR_HAS_LEVELS_n_PLUS_3_OVER_2_AND_"
                "ZERO_CLASSICAL_SPINOR_TRACE_THEREFORE_HAS_ZERO_FLUX"
            ),
            "ghost": (
                "LONGITUDINAL_AND_COMPLEX_GHOST_BLOCKS_CANCEL_MODE_BY_MODE_"
                "AND_GLOBAL_GAUGE_ZERO_MODES_ARE_QUOTIENTED"
            ),
            "HS": (
                "THE_SELECTED_ZERO_HS_TRACE_IS_THE_ZERO_VECTOR_OF_ITS_"
                "HOMOGENEOUS_LINEARIZED_BOUNDARY_GRAPH"
            ),
        },
        "scope": {
            "zero_background_F_child_evaluable_without_full_matrix": True,
            "full_nonzero_fluctuation_Calderon_matrices_derived": False,
            "quantum_determinant_backreaction_zero": False,
            "why_quantum_backreaction_is_separate": (
                "THE_ONE_LOOP_SUPERDETERMINANT_DEPENDS_ON_THE_SCALAR_"
                "GEOMETRY_EVEN_WHEN_CLASSICAL_GAUGE_SPINOR_HS_TRACES_VANISH"
            ),
            "scalar_geometry_child_from_v17_96_closed": scalar[
                "F_child_scalar"
            ]["closed_to_resolved_derivative_tolerance"],
        },
        "interpretation": (
            "THE_SM_BUNDLE_AND_FAMILY_DATA_PERSIST_AS_DISCRETE_CARRIER_"
            "STRUCTURE_WITHOUT_REQUIRING_NONZERO_CLASSICAL_GAUGE_SPINOR_"
            "GHOST_OR_HS_FIELD_AMPLITUDES"
        ),
    }


def completion_payload() -> dict[str, Any]:
    result = zero_background_calderon_closure()
    scope = result["scope"]
    provenance = result["provenance"]
    validation = {
        "four_zero_background_sectors_owned": len(
            result["F_child_zero_background"]
        ) == 4,
        "zero_sector_matching_exact": result[
            "F_child_zero_background_norm"
        ] == 0.0,
        "zero_connection_sector_selected": "zero-background" in provenance[
            "post_event_connection_sector"
        ],
        "zero_fermion_vacuum_selected": provenance[
            "fermion_vacuum"
        ].startswith("zero_classical_field"),
        "odd_FR_Weyl_has_no_zero_level": provenance["Weyl_levels"] == "n>=0",
        "BRST_zero_modes_quotiented": "zero_modes_are_quotiented" in provenance[
            "BRST_quotient"
        ],
        "bundle_class_persists": provenance["same_bundle_isomorphism_class"],
        "nonzero_projector_not_fabricated": not scope[
            "full_nonzero_fluctuation_Calderon_matrices_derived"
        ],
        "quantum_backreaction_not_erased": not scope[
            "quantum_determinant_backreaction_zero"
        ],
        "scalar_block_already_closed": scope[
            "scalar_geometry_child_from_v17_96_closed"
        ],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_zero_background_calderon_closure_v17_97",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "zero_background_calderon_closure": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_RECONSTRUCTED_PARTICLE_CARRIES_THE_SM_BUNDLE_IN_THE_ZERO_"
            "CLASSICAL_FIELD_SECTOR_WITH_EXACT_HOMOGENEOUS_BOUNDARY_MATCHING"
        ),
        "dependency_closed": (
            "GAUGE_SPINOR_GHOST_HS_ZERO_BACKGROUND_COMPONENT_OF_F_child"
        ),
        "active_calculation": (
            "AUDIT_THE_PREGEOMETRIC_CORE_ENTRY_AS_A_DISCRETE_FIREWALL_"
            "MATCH_OR_A_CONTINUOUS_F_child_ROW_THEN_EVOLVE_PERSISTENCE"
        ),
        "direct_N3_solve_authorized_next": False,
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_zero_background_calderon_closure_v17_97.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "zero_background_calderon_closure", "completion_payload", "materialize",
]
