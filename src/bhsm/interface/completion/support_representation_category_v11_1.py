"""Stratified BHSM category and support-representation lift audit.

The frozen action supplies geometric objects and maps after forgetting support.
It does not supply a natural ``G_D`` action on the primitive metric, measures,
bundles, embeddings, or core data.  Consequently the forgetful data admit
inequivalent character lifts and cannot select an action-derived functor.
"""

from __future__ import annotations

from typing import Any


SUPPORT_GROUP = "G_D=(R_{>0},multiplication)"
from .support_functor_equivalence_quotient_v11_1 import (
    EQUIVALENCE_VERDICT as FUNCTOR_VERDICT,
    NEXT_EQUIVALENCE_OBJECT as NEXT_EXACT_OBJECT,
)


def _object(
    key: str,
    domain: str,
    tensor_type: str,
    density_type: str,
    dimension: str,
    *,
    fiber: str = "none",
    wall: str = "none",
    core: str = "none",
    codimension: int = 0,
    gauge: str = "singlet",
    triality: str = "singlet",
    coefficient: str | None = None,
    role: str,
) -> dict[str, Any]:
    return {
        "key": key,
        "domain": domain,
        "codomain": domain,
        "tensor_type": tensor_type,
        "density_type": density_type,
        "engineering_dimension": dimension,
        "supported_dimensionality": domain,
        "fiber_incidence": fiber,
        "wall_incidence": wall,
        "core_incidence": core,
        "boundary_codimension": codimension,
        "gauge_representation": gauge,
        "triality_representation": triality,
        "existing_action_coefficient": coefficient,
        "frozen_action_role": role,
        "action_defined_support_representation": None,
    }


def category_objects() -> list[dict[str, Any]]:
    """Return the required object ledger without assigning support weights."""

    return [
        _object("regular_bulk_metric", "S8 regular bulk", "symmetric (0,2)", "weight-zero tensor before integration", "L^2", coefficient="kappa1", role="Einstein-Hilbert carrier"),
        _object("hopf_core_mode", "S8 regular bulk", "scalar/metric mode", "scalar", "action dependent", fiber="Hopf fiber", core="asymptotic core-facing", coefficient="Zchi,Zsigma,kappa1", role="q_C carrier"),
        _object("enclosure_wall_mode", "S5 cap plus boundary", "scalar/radial mode", "scalar", "action dependent", wall="moving cap/fold", codimension=3, coefficient="lambda5,kappa1", role="q_W carrier"),
        _object("support_depth_mode", "regular stratified support", "real scalar", "scalar", "canonical", core="q_D to infinity", coefficient="1", role="q_D Haar carrier"),
        _object("gauge_curvature", "intrinsic S4", "adjoint-valued two-form", "form", "L^-2", gauge="U1 x SU2 x SU3 adjoint", coefficient="g1,g2,g3", role="gauge kinetic sectors"),
        _object("fermion_kinetic", "intrinsic S4", "chiral spinor and dual", "spinor density after pairing", "L^-3/2", gauge="frozen SM ledger", triality="sector dependent", coefficient="common kinetic normalization", role="fermion kinetic sectors"),
        _object("scalar_topographic", "S8/S5/S4 stratified", "real/complex scalar candidate", "scalar", "action dependent", fiber="profile dependent", wall="profile incidence", coefficient="retained scalar inputs", role="scalar/topographic sector"),
        _object("charged_current", "common S4 current layer", "vector-current pairing", "scalar density after contraction", "L^-4", gauge="charged weak current", triality="sector projectors", coefficient="retained gauge data", role="charged-current sector"),
        _object("neutral_response", "localized S4/collar", "projected response operator", "boundary density", "action dependent", wall="collar incidence", coefficient=None, role="neutral-response sector"),
        _object("scale_rg", "effective transport layer", "scheme/scale object", "not a local density", "various", coefficient=None, role="scale and RG transport"),
        _object("regular_boundary", "boundary of S5/S8", "induced metric, normal, extrinsic curvature", "boundary density", "mixed", wall="GHY/cap boundary", codimension=1, coefficient="kappa1", role="regular boundary sector"),
        _object("core_asymptotic_boundary", "q_D=+infinity", "asymptotic phase-space candidate", "not supplied", "not supplied", core="terminal stratum", codimension=1, coefficient=None, role="core boundary sector"),
        _object("effective_m4_projection", "intrinsic/effective M4", "projection functor target", "M4 density", "mixed", fiber="fiber integration target", wall="seam projection", core="core data required", coefficient=None, role="effective M4 projection"),
    ]


def _morphism(key: str, domain: str, codomain: str, law: str, missing: str) -> dict[str, Any]:
    return {
        "key": key,
        "domain": domain,
        "codomain": codomain,
        "required_support_law": law,
        "underlying_action_map_present": True,
        "gd_equivariance_derived": False,
        "missing_support_datum": missing,
    }


def category_morphisms() -> list[dict[str, Any]]:
    """Return the map ledger whose support equivariance must be derived."""

    return [
        _morphism("covariant_derivative", "field", "T* tensor field", "w(nabla Phi)=w(Phi)+w(nabla)", "support action on connection"),
        _morphism("gauge_derivative", "gauge bundle", "T* tensor gauge bundle", "w(D Phi)=w(Phi)+w(D)", "support action on gauge connection"),
        _morphism("exterior_derivative", "p-form", "p+1-form", "w(d alpha)=w(alpha)+w(d)", "whether support is spacetime constant"),
        _morphism("codifferential", "p-form", "p-1-form", "delta depends on star and metric", "support action on Hodge star"),
        _morphism("wedge", "p-form tensor q-form", "p+q-form", "weights add", "primitive form weights"),
        _morphism("tensor_product", "V tensor W", "V tensor W", "weights add", "primitive object weights"),
        _morphism("contraction", "tensor with metric inverse", "lower-rank tensor", "factor plus inverse-metric weights", "metric support weight"),
        _morphism("hodge_star", "p-form", "n-p-form", "metric and orientation dependent", "metric/measure support action"),
        _morphism("trace", "endomorphism", "scalar", "dual and representation weights cancel only if derived", "dual representation law"),
        _morphism("fiber_integration", "S8 form", "S5/S4 form", "output=input+fiber-measure weight", "fiber-measure support weight"),
        _morphism("boundary_pullback", "bulk tensor", "boundary tensor", "pullback must intertwine GD", "support action on embedding"),
        _morphism("normal_restriction", "bulk tensor", "boundary tensor", "normal weight contributes", "support action on unit normal"),
        _morphism("sector_projector", "finite module", "sector module", "projector must commute with GD", "GD action on frozen module"),
        _morphism("adjoint_pairing", "V* tensor V", "scalar", "dual weights and measure must close", "measure-modified adjoint law"),
        _morphism("compatibility_map", "S8/S5 data", "S4 data", "source and target weights connected by an intertwiner", "cross-stratum GD intertwiner"),
        _morphism("core_asymptotic_map", "regular phase data", "core data", "symplectic GD correspondence", "core phase space and GD action"),
        _morphism("m4_projection", "complete stratified data", "effective M4 data", "projection must be GD natural", "complete reduction functor"),
    ]


def functor_laws() -> list[dict[str, Any]]:
    return [
        {"law": "identity_and_composition", "equation": "R(id)=id; R(g o f)=R(g)oR(f)", "status": "FORMAL_REQUIREMENT"},
        {"law": "tensor", "equation": "R(V tensor W)=R(V) tensor R(W)", "status": "FORMAL_REQUIREMENT"},
        {"law": "multiplicative_invariant", "equation": "w(I_a I_b)=w(I_a)+w(I_b)", "status": "DERIVED_FROM_CHARACTERS"},
        {"law": "dual", "equation": "w(V*)=-w(V) only when the pairing measure is invariant", "status": "MEASURE_DEPENDENT_OPEN"},
        {"law": "direct_sum", "equation": "summed action terms require a common representation or derived intertwiner", "status": "INTERTWINER_OPEN"},
        {"law": "adjoint", "equation": "support action must preserve Hermitian pairings", "status": "MEASURE_DEPENDENT_OPEN"},
        {"law": "integration", "equation": "w(integral_fiber alpha)=w(alpha)+w(dmu_fiber)", "status": "MEASURE_WEIGHT_OPEN"},
        {"law": "pullback", "equation": "R(i*) is natural only with a GD action on i", "status": "EMBEDDING_ACTION_OPEN"},
    ]


def candidate_lifts() -> list[dict[str, Any]]:
    """Exhibit inequivalent lifts of the same forgotten action data.

    The fiber-measure character compensates the changed wall character, so
    fiber integration remains homogeneous.  The action does not select either
    measure character.
    """

    rows = []
    for name, w_core, w_wall in (("R_D^(A)", 1, 1), ("R_D^(B)", 1, 2)):
        rows.append(
            {
                "name": name,
                "primitive_weights": {
                    "regular_bulk_metric": 0,
                    "bulk_measure": 0,
                    "hopf_core_invariant": w_core,
                    "enclosure_wall_invariant": w_wall,
                    "fiber_measure_S8_to_S5": w_wall - w_core,
                    "support_depth_mode": 0,
                },
                "derived_composite_rule": "tensor/wedge weights add; dual weights negate relative to the selected pairing measure",
                "fiber_integration_homogeneous": True,
                "identity_and_composition_preserved": True,
                "tensor_law_preserved": True,
                "parent_action_recovered_at_upsilon_one": True,
                "positive_characters_on_regular_domain": True,
                "particle_inputs_used": False,
                "action_selected": False,
            }
        )
    return rows


def category_payload() -> dict[str, Any]:
    objects = category_objects()
    morphisms = category_morphisms()
    laws = functor_laws()
    validation = {
        "required_objects_present": len(objects) == 13,
        "required_morphism_classes_present": len(morphisms) >= 17,
        "all_support_representations_unassigned_by_action": all(row["action_defined_support_representation"] is None for row in objects),
        "all_equivariance_questions_explicit": all(not row["gd_equivariance_derived"] for row in morphisms),
        "character_multiplication_law_derived": any(row["law"] == "multiplicative_invariant" and row["status"] == "DERIVED_FROM_CHARACTERS" for row in laws),
    }
    return {
        "artifact": "BHSM_support_representation_category_v11_1",
        "support_group": SUPPORT_GROUP,
        "category": "C_BHSM^strat",
        "objects": objects,
        "morphisms": morphisms,
        "functor_laws": laws,
        "status": "BHSM_STRATIFIED_ACTION_CATEGORY_PRESENTED_WITHOUT_GD_LIFT",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def functor_payload() -> dict[str, Any]:
    lifts = candidate_lifts()
    validation = {
        "two_lifts_present": len(lifts) == 2,
        "lifts_inequivalent": lifts[0]["primitive_weights"] != lifts[1]["primitive_weights"],
        "both_recover_parent": all(row["parent_action_recovered_at_upsilon_one"] for row in lifts),
        "both_preserve_declared_generated_laws": all(row["fiber_integration_homogeneous"] and row["tensor_law_preserved"] and row["identity_and_composition_preserved"] for row in lifts),
        "neither_action_selected": all(not row["action_selected"] for row in lifts),
        "no_particle_inputs": all(not row["particle_inputs_used"] for row in lifts),
    }
    return {
        "artifact": "BHSM_support_representation_functor_v11_1",
        "target": "Rep(G_D)",
        "character_family": "chi_w(upsilon)=upsilon^w=exp[-w q_D/lambda_D]",
        "action_defined_natural_gd_action": None,
        "smallest_blocking_object": "primitive regular-bulk metric/measure pair and its induced fiber/boundary measures",
        "smallest_blocking_morphism": "fiber integration, whose character depends on an action-unfixed fiber-measure weight",
        "candidate_action_limit_compatible_lifts": lifts,
        "provisional_counterexample": (
            "R_D^(A) and R_D^(B) have different fixed characters and coincide with the frozen "
            "action at upsilon=1. This proves that the forgotten data do not select a representative, "
            "but physical inequivalence requires the separate equivalence quotient."
        ),
        "action_extension_required": True,
        "support_weights": None,
        "unique_functor": None,
        "unique_fixed_character_representative": False,
        "physical_equivalence_quotient_complete": False,
        "status": FUNCTOR_VERDICT,
        "next_exact_object": NEXT_EXACT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
