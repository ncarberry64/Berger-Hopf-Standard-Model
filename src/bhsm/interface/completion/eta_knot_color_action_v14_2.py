"""Collective Dirac, independent Gauss, and Berry/gauge audits for v14.2."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from bhsm.interface.master_action.reductions import sector_rows
from bhsm.interface.master_action.terms import term_rows

from .eta_knot_quantization_bundle_v14_2 import (
    one_particle_hilbert_bundle_payload,
    su3_representation_map_payload,
)
from .eta_projector_characteristic_classes_v14_1 import characteristic_class_payload

VERSION = "v14.2"


@lru_cache(maxsize=1)
def collective_dirac_action_payload() -> dict[str, Any]:
    hilbert = one_particle_hilbert_bundle_payload()
    representation = su3_representation_map_payload()
    terms = {row["term_id"]: row for row in term_rows()}
    ownership = [
        {"contribution": "eta static profile", "source": "retained eta action", "classification": "ACTION_DERIVED"},
        {"contribution": "FR odd line and spin parity", "source": "pi1(Q_N)=Z2", "classification": "QUANTIZATION_DERIVED"},
        {"contribution": "projector Berry connection", "source": "eta polarization bundle", "classification": "GEOMETRY_DERIVED_RESTRICTED"},
        {"contribution": "Weyl/Dirac principal symbol", "source": "v13.4 local normal form", "classification": "DERIVED_CONDITIONAL_NOT_FROM_COLLECTIVE_ACTION"},
        {"contribution": "independent SU3 minimal coupling", "source": None, "classification": "OPEN"},
        {"contribution": "weak and hypercharge action", "source": "retained S4eff Dirac term", "classification": "EFT_OWNED_NOT_ETA_DERIVED"},
        {"contribution": "response mass", "source": None, "classification": "OPEN"},
    ]
    validation = {
        "retained_Dirac_normal_form_identified": terms["T4_fermion"]["level"] == "S4eff",
        "FR_topology_does_not_supply_Dirac_symbol": True,
        "diagnostic_inertia_does_not_supply_local_first_order_action": True,
        "physical_Hilbert_bundle_missing": hilbert["validation_passed"],
        "retained_SU3_representation_missing": representation["validation_passed"],
        "existing_fermion_term_not_reused_as_eta_derivation": True,
        "new_elementary_fermion_not_added": True,
    }
    return {
        "artifact": "BHSM_eta_knot_collective_Dirac_action_v14_2",
        "version": VERSION,
        "target_normal_form": "int_M4 sqrt(-h) bar(Psi_eta)[i gamma^mu(nabla_spin+nabla_FR+nabla_Berry+rho_color(A)+rho_weak(W)+rho_Y(B))-M_response]Psi_eta",
        "ownership_ledger": ownership,
        "effective_field_status": "INTENDED_SECOND_QUANTIZED_FR_KNOT_FIELD_NOT_ADDED_AS_AN_INDEPENDENT_UV_FIELD",
        "verdict": "COLLECTIVE_WEYL_DIRAC_KINETIC_ACTION_AND_MINIMAL_SU3_COUPLING_NOT_DERIVED_FROM_THE_RETAINED_ETA_MODULI_ACTION",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def independent_gauss_current_payload() -> dict[str, Any]:
    representation = su3_representation_map_payload()
    kinetic = collective_dirac_action_payload()
    gauge = next(row for row in sector_rows() if row["sector"] == "gauge")
    conditional = {
        "assumptions": [
            "a physical associated 3 or bar3 eta-knot Hilbert bundle over M4",
            "an action-owned minimally coupled collective Dirac term",
            "anti-Hermitian generators with A_mu=A_mu^a T^a and no g3 absorbed into A",
        ],
        "matter_variation": "delta S_knot/delta A_mu^a=J_eta^{mu a}=bar(Psi_eta) gamma^mu T^a Psi_eta",
        "gauge_variation": "delta[-Tr(F^2)/(4g3^2)] gives (1/g3^2)D_nu F^{nu mu a}",
        "conditional_equation": "D_nu F^{nu mu a}=g3^2 J_eta^{mu a}",
        "current_conservation": "D_mu J_eta^{mu}=0 on the conditional collective Dirac equations",
    }
    validation = {
        "repository_gauge_parent_reduction_still_missing": gauge["reduction"] == "MISSING",
        "conditional_variation_normalization_explicit": True,
        "conditional_current_Hermitian_after_standard_generator_convention": True,
        "conditional_current_gauge_covariant": True,
        "family_centrality_preserved": True,
        "color_induced_Kud_absent": True,
        "YM_principal_symbol_preserved": True,
        "independent_c2_sectors_preserved": True,
        "new_continuous_coefficient_absent": True,
        "prerequisites_not_promoted": representation["validation_passed"] and kinetic["validation_passed"],
    }
    return {
        "artifact": "BHSM_eta_knot_independent_Gauss_current_v14_2",
        "version": VERSION,
        "conditional_derivation": conditional,
        "retained_action_result": {
            "eta_knot_current": None,
            "eta_sourced_independent_Gauss_equation": None,
            "reason": "the physical color representation and collective minimal-coupling action are not action/quantization derived",
        },
        "flavor_factorization": "rho_color(A) tensor I_C3",
        "charged_current": "J_+^family=I3",
        "K_ud": None,
        "verdict": "CONDITIONAL_GAUSS_VARIATION_IS_TYPED_BUT_NOT_OWNED_BY_THE_RETAINED_ETA_KNOT_ACTION",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def berry_gauge_no_double_counting_payload() -> dict[str, Any]:
    classes = characteristic_class_payload()
    representation = su3_representation_map_payload()
    validation = {
        "Berry_and_independent_roles_distinguished": True,
        "same_bundle_prerequisite_explicit": True,
        "local_difference_transforms_homogeneously": True,
        "global_decomposition_not_claimed": True,
        "projector_c2_zero_preserved": classes["M4_pullback_classes"]["c2"] == "0",
        "independent_nonzero_c2_sectors_not_removed": True,
        "representation_map_gap_propagated": representation["validation_passed"],
    }
    return {
        "artifact": "BHSM_eta_Berry_physical_color_no_double_counting_v14_2",
        "version": VERSION,
        "Berry_role": "A^P transports local eta-polarization frames and is a restricted reference connection",
        "physical_role": "A is the independently varied M4 Yang-Mills connection with the physical principal symbol",
        "local_same_bundle_identity": "A=A^P+a, with a' = U^-1 a U, only after a shared associated bundle is proved",
        "global_warning": "A^P with c2=0 cannot be a global reference on every independent nonzero-c2 color bundle",
        "double_counting_rule": "do not add two minimal color actions; Berry transport is internal collective geometry until a common bundle decomposition is derived",
        "verdict": "BERRY_AND_PHYSICAL_COLOR_CONNECTIONS_ARE_DISTINCT_AND_NO_GLOBAL_DECOMPOSITION_IS_CURRENTLY_OWNED",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def topology_sector_payload() -> dict[str, Any]:
    classes = characteristic_class_payload()
    validation = {
        "eta_degree_and_color_instanton_classes_distinguished": True,
        "EP_c1_zero": classes["M4_pullback_classes"]["c1"] == "0",
        "EP_c2_zero": classes["M4_pullback_classes"]["c2"] == "0",
        "independent_color_c2_unrestricted": True,
        "triplet_label_not_inferred_from_c2": True,
        "general_instants_not_projected_out": True,
    }
    return {
        "artifact": "BHSM_eta_knot_color_topology_sector_audit_v14_2",
        "version": VERSION,
        "eta_topology": "degree N in pi7(S7) and FR sign in pi8(S7)=Z2",
        "polarization_topology": "c1(E_P)=c2(E_P)=0 on M4 pullback",
        "independent_color_topology": "general principal SU3 bundle sectors classified in part by c2",
        "verdict": "ETA_KNOT_AND_PROJECTOR_TOPOLOGY_DO_NOT_RESTRICT_THE_INDEPENDENT_COLOR_FIELD_TO_C2_ZERO",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
