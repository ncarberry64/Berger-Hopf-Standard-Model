"""Finite action/domain screen for the current-C2 gauge-residue mismatch."""

from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any

ACTION_VERSION="BHSM-AE-3.0.0"
CLASSIFICATION="AE3_CURRENT_C2_GAUGE_MISMATCH_FINITE_ACTION_DOMAIN_SCREEN"
SELECTED_ROUTE="TWO_SIDED_CURRENT_C2_PARENT_CALDERON_SCHUR_COMPLEMENT"

@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    existing_parent_action_provenance: bool
    same_current_C2_domain_possible: bool
    compatible_with_zero_AE3_surface_contact: bool
    no_new_continuous_coefficient: bool
    can_change_transverse_temporal_spatial_ratio: bool
    status: str

    @property
    def admissible(self) -> bool:
        return all((self.existing_parent_action_provenance,self.same_current_C2_domain_possible,self.compatible_with_zero_AE3_surface_contact,self.no_new_continuous_coefficient,self.can_change_transverse_temporal_spatial_ratio))

def candidates() -> tuple[Candidate,...]:
    return (
        Candidate(SELECTED_ROUTE,True,True,True,True,True,"SELECTED_UNIQUE_COEFFICIENT_FREE_CALCULATION_ROUTE"),
        Candidate("ONE_SIDED_SMOOTH_PARENT_TRACE",True,True,True,True,False,"INVALIDATED_BY_CURRENT_C2_ZT_OVER_ZS_MISMATCH"),
        Candidate("FREE_INTRINSIC_M4_YANG_MILLS_TERM",False,True,False,False,True,"REJECTED_FREE_TAU_A_AND_NONZERO_CONTACT_ACTION"),
        Candidate("RECOVERED_V14_67_ATTACHMENT_WENTZELL_MATRIX",False,False,True,True,True,"THEOREM_CLASS_ONLY_PHYSICAL_INCIDENCE_AND_CURVATURE_PROVENANCE_OPEN"),
        Candidate("V17_89_TO_92_N3_DYNAMIC_WENTZELL_LAW",True,False,True,True,False,"REUSABLE_DYNAMIC_SEAM_TEMPLATE_NOT_CURRENT_C2_GAUGE_CALDERON_DATA"),
        Candidate("RELATIVE_SPECTRAL_HEAT_BOUNDARY_COEFFICIENT",False,True,True,False,True,"PARTIAL_FORMULAS_ONLY_RELATIVE_SPECTRAL_COEFFICIENT_Z_OPEN"),
        Candidate("DISTRIBUTIONAL_WALL_LOCALIZATION",False,False,False,True,True,"REJECTED_SINGULAR_DOMAIN_OUTSIDE_RESOLVED_AE3_INTERFACE"),
    )

def selection_certificate() -> dict[str,Any]:
    rows=[]
    for c in candidates():
        row=asdict(c); row["admissible"]=c.admissible; rows.append(row)
    allowed=[r for r in rows if r["admissible"]]
    return {"action_version":ACTION_VERSION,"classification":CLASSIFICATION,"candidate_rows":rows,"admissible_count":len(allowed),"selected_route":allowed[0]["candidate_id"] if len(allowed)==1 else None,"certificate_passed":len(allowed)==1 and allowed[0]["candidate_id"]==SELECTED_ROUTE,"selection_is_for_next_calculation_not_residue_promotion":True}

def exterior_calderon_contract() -> dict[str,Any]:
    return {
        "same_parent_operator":"AE3_WEIGHTED_MAXWELL_PLUS_BRST_GAUGE_GHOST_BLOCK",
        "interface":"SIGMA_ZERO_INTERNAL_TWO_SIDED_TRACE_NOT_SPACETIME_EDGE",
        "inside_operator":"CURRENT_DERIVED_N_INSIDE_OMEGA_K",
        "missing_operator":"N_EXTERIOR_OMEGA_K_ON_ACTUAL_CURRENT_C2_MAXIMAL_EXTERIOR",
        "combined_interface_Hessian":"N_TOTAL=N_INSIDE+U_RESET_STAR*N_EXTERIOR*U_RESET",
        "surface_contact_term":None,
        "derivatives_required":["minus_partial_omega_squared_N_TOTAL_at_zero","partial_coexact_k_squared_N_TOTAL_at_zero","longitudinal_ghost_Ward_derivative"],
        "decision":"PROMOTE_RESIDUE_ONLY_IF_ZT_TOTAL_EQUALS_ZS_TOTAL_POSITIVE_WITHOUT_FIELD_OR_CONE_RETUNING",
        "failure_rule":"RECORD_SIGNED_MISMATCH_AND_RESPONSIBLE_EXTERIOR_OR_DOMAIN_TERM",
        "far_Friedrichs_core_is_physical_exterior":False,
        "physical_photon_derived":False,
    }

__all__=["ACTION_VERSION","CLASSIFICATION","SELECTED_ROUTE","Candidate","candidates","exterior_calderon_contract","selection_certificate"]
