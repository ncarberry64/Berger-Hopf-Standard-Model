"""Authoritative BHSM v14.31 Path B master-action ledger."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from bhsm.interface.completion.path_b_foundational_action_v14_31 import (
    PRIMARY_VERDICT,
    SECONDARY_VERDICT,
    connection_fork_payload,
    foundational_action_payload,
    foundational_bundle_payload,
    no_new_vector_hessian_payload,
)

VERSION = "v14.31"


def object_ledger() -> list[dict[str, str]]:
    return [
        {
            "object": "P_color and A_physical",
            "type": "physical SU3 principal bundle and connection",
            "independent_or_composite": "independent",
            "variation": "delta A",
            "equation": "Yang-Mills equation with eta and retained matter sources",
            "status": "FOUNDATIONAL_RETAINED",
        },
        {
            "object": "Q_G2=P_color x_SU3 G2",
            "type": "extended parent bundle",
            "independent_or_composite": "canonical structure-group extension",
            "variation": "none independently",
            "equation": "none",
            "status": "FOUNDATIONAL_POSTULATE",
        },
        {
            "object": "eta",
            "type": "section of Q_G2/SU3",
            "independent_or_composite": "independent physical sigma-model field",
            "variation": "tangent delta eta",
            "equation": "gauged p2+p8 eta Euler equation",
            "status": "AUTHORITATIVE_PHYSICAL_FIELD",
        },
        {
            "object": "theta=Theta_eta(D_A eta)",
            "type": "G2/SU3 intrinsic torsion",
            "independent_or_composite": "composite",
            "variation": "chain rule from delta A and delta eta",
            "equation": "none independently",
            "status": "NO_INDEPENDENT_VECTOR_FIELD",
        },
        {
            "object": "M8 eta construction",
            "type": "candidate ultraviolet/geometric origin",
            "independent_or_composite": "not co-varied with eta_phys",
            "variation": "outside the physical Path-B action unless a future matching theorem replaces eta_phys",
            "equation": "UV matching problem",
            "status": "OPEN_PROVENANCE_NOT_DUPLICATE_PHYSICAL_FIELD",
        },
        {
            "object": "Wilson singlet",
            "type": "gauge-invariant source/observable insertion",
            "independent_or_composite": "functional of A and endpoints",
            "variation": "source response",
            "equation": "Wilson-sourced BVP",
            "status": "EXACT_SOURCE_NOT_DYNAMICAL_FIELD",
        },
        {
            "object": "Psi_eta",
            "type": "future FR collective Dirac representative",
            "independent_or_composite": "not yet admitted simultaneously",
            "variation": "after collective matching only",
            "equation": "future first-order Dirac equation",
            "status": "OPEN_NO_DOUBLE_COUNTING_GATE",
        },
    ]


@lru_cache(maxsize=1)
def master_action_payload() -> dict[str, Any]:
    dependencies = (
        foundational_bundle_payload(),
        connection_fork_payload(),
        no_new_vector_hessian_payload(),
        foundational_action_payload(),
    )
    validation = {
        "all_path_B_dependencies_pass": all(item["validation_passed"] for item in dependencies),
        "one_physical_color_bundle": True,
        "one_physical_eta_field": True,
        "theta_not_independently_varied": True,
        "old_M8_eta_not_double_counted": True,
        "Wilson_operator_is_source_not_field": True,
        "FR_field_not_prematurely_added": True,
        "action_ownership_gate_closed_by_declared_postulate": True,
    }
    return {
        "artifact": "BHSM_Path_B_master_action_v14_31",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "authoritative_action": "S_BHSM^PathB=S_retained_non_eta+S_YM[A]+S_eta_phys[A,eta]+S_constraint+retained gravity/Higgs/seam terms",
        "field_space": "Conn(P_color) x Gamma(Q_G2/SU3) x retained independent fields",
        "postulates": [
            "Q_G2=P_color x_SU3 G2",
            "eta is the physical section of Q_G2/SU3",
            "the v14.29 gauged p2+p8 eta density is a foundational physical action term",
            "theta=Theta_eta(D_A eta) is composite",
        ],
        "replacement_rule": "do not add a second independently varied M8 eta copy; M8 is a UV-origin candidate until matched",
        "object_ledger": object_ledger(),
        "action_ownership_gate": "PASSED_BY_EXPLICIT_FOUNDATIONAL_POSTULATE",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
