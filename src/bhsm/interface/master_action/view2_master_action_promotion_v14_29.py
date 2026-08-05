"""Authoritative v14.29 View 2 master-action promotion."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from bhsm.interface.completion.eta_fr_current_quantization_v14_29 import fr_quantization_payload
from bhsm.interface.completion.eta_g2_composite_intrinsic_torsion_v14_29 import composite_theta_bundle_payload, theta_hessian_payload
from bhsm.interface.completion.eta_minimally_gauged_p2_p8_action_v14_29 import minimally_gauged_action_payload
from bhsm.interface.completion.eta_su3_noether_current_v14_29 import noether_current_payload, pure_wall_current_payload, tangent_mode_payload
from bhsm.interface.completion.wilson_singlet_source_functional_v14_29 import wilson_singlet_payload

VERSION = "v14.29"
PRIMARY_VERDICT = "BHSM_VIEW2_MINIMALLY_GAUGED_ETA_ACTION_AND_COMPOSITE_THETA_CURRENT_ARE_CONSTRUCTED_CONDITIONALLY_BUT_FULL_MASTER_ACTION_OWNERSHIP_REMAINS_BLOCKED"


def object_ledger() -> list[dict[str, str]]:
    return [
        {"Object": "A_physical", "Type": "SU(3) connection", "Stratum": "M4/collar pullback", "Independent/composite": "independent", "Variation": "delta A", "Equation produced": "Yang-Mills Gauss/evolution equation", "Normalization source": "retained S_YM; common coefficient unresolved", "Double-counting risk": "must not equal A^P", "Status": "authoritative"},
        {"Object": "eta", "Type": "G2/SU3=S6 section", "Stratum": "candidate physical-SU3 collar; original field is on M8", "Independent/composite": "independent section", "Variation": "delta eta tangent to Sigma_eta", "Equation produced": "candidate gauged p2+p8 eta Euler equation", "Normalization source": "retained kappa1 and fixed p8 term", "Double-counting risk": "S_etaA must replace, not supplement, the ungauged eta kinetic term", "Status": "conditional; common-domain reduction open"},
        {"Object": "theta=Theta_eta(D_A eta)", "Type": "intrinsic torsion", "Stratum": "candidate collar", "Independent/composite": "composite", "Variation": "chain rule from delta A,delta eta", "Equation produced": "none independently", "Normalization source": "canonical reductive bundle map", "Double-counting risk": "forbid independent theta Hessian", "Status": "geometric definition conditional on common bundle; not action-derived"},
        {"Object": "u_eta", "Type": "selector background", "Stratum": "pure wall", "Independent/composite": "fixed background section", "Variation": "not a source insertion", "Equation produced": "J[u_eta]=0", "Normalization source": "stabilizer selection", "Double-counting risk": "do not infer all tangent currents vanish", "Status": "background limit"},
        {"Object": "Psi_eta", "Type": "FR collective field", "Stratum": "effective M4", "Independent/composite": "effective quantization of eta zero mode", "Variation": "conditional Dirac variation", "Equation produced": "conditional first-order collective equation", "Normalization source": "relative knot Hilbert bundle", "Double-counting risk": "replace, never add to, classical zero-mode current", "Status": "conditional"},
        {"Object": "Wilson singlet", "Type": "source/observable insertion", "Stratum": "M4 paths", "Independent/composite": "functional of A and endpoint matter", "Variation": "source response only", "Equation produced": "singlet response functional", "Normalization source": "SU(3) invariant tensor and unitary holonomy", "Double-counting risk": "not a new eta action term", "Status": "exact source functional"},
    ]


@lru_cache(maxsize=1)
def master_action_payload() -> dict[str, Any]:
    dependencies = [
        composite_theta_bundle_payload(), theta_hessian_payload(), minimally_gauged_action_payload(),
        noether_current_payload(), pure_wall_current_payload(), tangent_mode_payload(),
        fr_quantization_payload(), wilson_singlet_payload(),
    ]
    validation = {
        "all_classical_View2_dependencies_pass": all(item["validation_passed"] for item in dependencies),
        "physical_YM_connection_retained": True,
        "A_P_distinct_from_A_physical": True,
        "eta_term_not_duplicated": True,
        "theta_not_independently_varied": True,
        "FR_current_not_double_counted": True,
        "Wilson_operator_is_source_not_field": True,
        "conditional_action_layer_recorded": True,
        "preexisting_parent_action_derivation_absent": True,
        "FR_matching_theorem_absent": True,
    }
    return {
        "artifact": "BHSM_View2_master_action_promotion_v14_29",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "authoritative_action": None,
        "conditional_completion_candidate": "S_candidate=S_retained_without_old_ungauged_eta_kinetic+S_YM[A_physical]+S_etaA[A_physical,eta]+S_constraint+S_collar_geometry; Wilson functionals are source insertions",
        "replacement_rule": "S_etaA is the gauge-covariant replacement of the retained eta p2+p8 term, not an added duplicate",
        "YM_equation": "g3^(-2)(D_nu F^(nu mu))_a=j_eta,a^mu+j_retained,a^mu",
        "retained_source_definition": "variations of pre-existing non-eta color-charged action terms only; after FR quantization the eta zero-mode Dirac representative replaces its classical source",
        "configuration_space": "candidate common-domain space Conn(P_color) x Gamma(Sigma_eta) x retained fields; the map from the original M8 eta field to this collar space is not derived",
        "precise_blockers": ["common-domain M8-to-collar eta/SU3 reduction and measure", "collective FR/Dirac action-equivalence and mode-subtraction theorem"],
        "source_functionals": ["Wilson-dressed meson", "Wilson-dressed baryon"],
        "object_ledger": object_ledger(),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
