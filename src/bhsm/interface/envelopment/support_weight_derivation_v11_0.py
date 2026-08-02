"""Support-character audit on the frozen stratified BHSM parent action.

Multiplicativity fixes the *form* ``F_a=upsilon**w_a`` but not the weights.
The current parent action declares ``upsilon`` to be an independent scalar; it
does not define a dilation action of support on the metric, measure, bundles,
or boundary embeddings.  Tensor rank and density weight therefore do not
select a character. Two explicit integer-weight assignments prove that the
declared character-level rules do not select a unique representation. A full
action still requires the missing cross-stratum ownership map.
"""

from __future__ import annotations

from typing import Any

from .support_composition_v11_0 import coupling_slope, support_character


PRIMARY_VERDICT = (
    "BHSM_MULTIPLICATIVE_SUPPORT_HAAR_KINEMATICS_DERIVED_BUT_"
    "NORMALIZATION_AND_SUPPORT_WEIGHTS_NOT_ACTION_FIXED"
)
NEXT_EXACT_OBJECT = (
    "ACTION_DERIVED_SUPPORT_REPRESENTATION_FUNCTOR_ON_STRATIFIED_SECTORS_"
    "WITH_FIXED_HAAR_SCALE"
)


def parent_term_inventory() -> list[dict[str, Any]]:
    """Return the term-level action inventory without inventing weights."""

    rows = [
        ("geometry", "kappa1 R8/2", "S8", "kappa1", 8, "Ricci scalar", "Hopf metric", False),
        ("geometry", "-kappa0/2", "S8", "kappa0", 8, "scalar", "bulk measure", False),
        ("core/Hopf", "-Zchi(1+g sigma^2)|dchi|^2/2", "S8", "Zchi,g", 8, "contracted one-form square", "bulk carrier", False),
        ("core/Hopf", "-Zsigma|dsigma|^2/2", "S8", "Zsigma", 8, "contracted one-form square", "bulk envelopment", False),
        ("core/Hopf", "-U(sigma)", "S8", "A0,G0", 8, "scalar", "bulk envelopment", False),
        ("core/Hopf", "-(1+g sigma^2)kappa1 X_eta/2", "S8", "kappa1,g", 8, "contracted spinor-covariant gradient", "Hopf/triality carrier", False),
        ("core/Hopf", "-(1+g sigma^2)X_eta^4/8", "S8", "g", 8, "fourth power of scalar X_eta", "Hopf/triality carrier", False),
        ("core/Hopf", "+Lambda_eta(<eta,eta>-1)/2", "S8", "Lambda_eta", 8, "scalar constraint", "triality carrier", False),
        ("wall", "S5 Einstein term", "S5", "kappa1", 5, "Ricci scalar", "cap reduction", True),
        ("wall", "S5 reduced scalar terms", "S5", "lambda5 and retained coefficients", 5, "contracted gradients/scalars", "cap reduction", True),
        ("boundary", "S_GHY", "boundary of S5", "kappa1", 4, "extrinsic-curvature scalar", "cap boundary", True),
        ("geometry", "B1 intrinsic Einstein term", "S4 intrinsic", "C_partial", 4, "Ricci scalar", "localized boundary", True),
        ("gauge", "intrinsic gauge kinetic terms", "S4 intrinsic", "g1,g2,g3", 4, "contracted curvature two-forms", "retained gauge bundles", False),
        ("fermion", "intrinsic chiral kinetic terms", "S4 intrinsic", "canonical common normalization", 4, "Dirac bilinear", "retained chiral bundles", False),
        ("fermion", "intrinsic Yukawa terms", "S4 intrinsic", "Y_u,Y_d,Y_e", 4, "fermion-scalar bilinear", "family/sector bundles", False),
        ("scalar/topographic", "intrinsic scalar/Higgs terms", "S4 intrinsic", "retained EFT inputs", 4, "gradient and scalar invariants", "localized scalar bundle", False),
        ("compatibility", "metric/bundle compatibility multipliers", "S5|4 compatibility", "normalization 1", 4, "multiplier contractions", "cross-stratum incidence", True),
        ("current", "retained gauge and eta-current terms", "S4/common-current layer", "retained gauge data", 4, "vector-current contraction", "current incidence", False),
        ("core boundary", "S_Sigma_core+S_core", "Sigma_core and M_core", None, None, "not supplied", "core incidence open", True),
    ]
    return [
        {
            "sector": sector,
            "term": term,
            "action_owner": owner,
            "original_coefficient": coefficient,
            "supported_dimensions": dimensions,
            "tensor_rank": tensor_rank,
            "density_weight": 1,
            "fiber_incidence": fiber_incidence,
            "wall_incidence": wall_incidence,
            "support_weight_w_a": None,
            "weighted_term": None,
            "q_D_variation": None,
            "stress_contribution": None,
            "boundary_contribution": "inherits parent completion only after a character is selected",
            "status": "OPEN_PARENT_TERM_AND_SUPPORT_CHARACTER" if coefficient is None else "OPEN_SUPPORT_CHARACTER",
        }
        for sector, term, owner, coefficient, dimensions, tensor_rank, fiber_incidence, wall_incidence in rows
    ]


def admissible_integer_counterexamples() -> list[dict[str, Any]]:
    """Exhibit two inequivalent, positive, no-fit character assignments."""

    assignments = [
        {"name": "A", "w_C": 1, "w_W": 1},
        {"name": "B", "w_C": 1, "w_W": 2},
    ]
    for row in assignments:
        row.update(
            {
                "all_other_parent_weights": 0,
                "F_C": f"upsilon^{row['w_C']}",
                "F_W": f"upsilon^{row['w_W']}",
                "F_C_at_one": support_character(1.0, row["w_C"]),
                "F_W_at_one": support_character(1.0, row["w_W"]),
                "positive_on_regular_domain": True,
                "integer_weights": True,
                "covariant": True,
                "dimension_preserving": True,
                "q_C_source_nontrivial": row["w_C"] != 0,
                "q_W_source_nontrivial": row["w_W"] != 0,
                "canonical_slopes_at_lambda_one": [
                    coupling_slope(row["w_C"]),
                    coupling_slope(row["w_W"]),
                ],
                "particle_data_used": False,
                "adopted": False,
            }
        )
    return assignments


def supported_action_payload() -> dict[str, Any]:
    counterexamples = admissible_integer_counterexamples()
    validation = {
        "haar_kinetic_selected": True,
        "bare_potential_absent": True,
        "parent_limit_at_upsilon_one": all(
            row["F_C_at_one"] == row["F_W_at_one"] == 1.0 for row in counterexamples
        ),
        "two_integer_nontrivial_counterexamples": len(counterexamples) == 2,
        "counterexamples_are_inequivalent": (
            counterexamples[0]["canonical_slopes_at_lambda_one"]
            != counterexamples[1]["canonical_slopes_at_lambda_one"]
        ),
        "both_core_and_wall_source_depth": all(
            row["q_C_source_nontrivial"] and row["q_W_source_nontrivial"]
            for row in counterexamples
        ),
        "no_weight_fabricated": all(
            row["support_weight_w_a"] is None for row in parent_term_inventory()
        ),
        "no_particle_fit": True,
    }
    return {
        "artifact": "BHSM_supported_parent_action_v11_0",
        "parent_action": "S8^env+sum(S5+S_GHY)+S4,intrinsic+S_compatibility+S_current",
        "canonical_support_term": "-1/2 |nabla q_D|^2",
        "bare_support_potential": 0,
        "general_character_form": "F_a(upsilon)=upsilon^w_a=exp[-(w_a/lambda_D)q_D]",
        "support_equation": "Box_G q_D=J_D, with J_D=sum_a (w_a/lambda_D) exp[-w_a q_D/lambda_D] I_a up to the action sign convention",
        "term_inventory": parent_term_inventory(),
        "weight_derivation_result": (
            "tensor rank, density weight, dimensionality, and covariance do not fix w_a because "
            "upsilon is an independent dimensionless scalar and no support dilation action on parent fields is defined"
        ),
        "minimality_audit": {
            "fewest_nonzero_weights_allowed_by_required_sources": 2,
            "smallest_positive_integer_magnitude_candidate": {"w_C": 1, "w_W": 1},
            "unique_physical_theorem": False,
            "reason": (
                "the ordering is an external sparsity convention; the parent variational principle and "
                "geometry do not derive positivity, grouping, or relative character exponents"
            ),
        },
        "admissible_counterexamples": counterexamples,
        "lambda_D_fixed": False,
        "support_weights_fixed": False,
        "complete_supported_parent_action": None,
        "support_action_success_verdict_reached": False,
        "status": PRIMARY_VERDICT,
        "next_exact_object": NEXT_EXACT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
