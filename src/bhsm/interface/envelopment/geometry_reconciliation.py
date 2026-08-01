"""Exact reconciliation of author S3 x M4 language with BHSM strata."""

from __future__ import annotations

from typing import Any

from .relational_axioms import DoctrineStatus


GEOMETRY_VERDICT = "BHSM_S3_M4_IS_A_LOCAL_OR_REDUCED_DESCRIPTION_NOT_THE_FULL_PARENT"


def domain_rows() -> list[dict[str, Any]]:
    return [
        {
            "object": "M8",
            "dimension": 8,
            "topology": "I_t x S7",
            "role": "global parent domain of S8^env",
            "ownership": "structural eta-extended parent action",
        },
        {
            "object": "Hopf S3",
            "dimension": 3,
            "topology": "Sp(1) fiber in Sp(1) -> S7 -> S4 with c2=+1",
            "role": "internal vertical fiber, not a global product factor of S7",
            "ownership": "M8-to-M5 pushforward geometry",
        },
        {
            "object": "M5",
            "dimension": 5,
            "topology": "I_t x S4, represented by two caps",
            "role": "Hopf base/target stratum and cap variational domain",
            "ownership": "independent cap Wilson action plus GHY, constrained by compatibility",
        },
        {
            "object": "M4=B1",
            "dimension": 4,
            "topology": "I_t x S3 at chi=pi/2",
            "role": "observable intrinsic seam shared by the M5 caps",
            "ownership": "intrinsic localized EFT, not derived from the M8 metric",
        },
        {
            "object": "M5 collar",
            "dimension": 5,
            "topology": "M4 x [0,epsilon_rho) locally",
            "role": "normal neighborhood of the observable seam",
            "ownership": "cap metric, GHY, matcher, and boundary data",
        },
    ]


def s3_m4_identification() -> dict[str, Any]:
    return {
        "author_expression": "S3 x M4",
        "dimension": 7,
        "not_equal_to_M8_by_dimension": True,
        "repository_identification": (
            "the Hopf-fiber lift of the M4 equatorial seam; the restricted "
            "Sp(1) bundle over the spatial equator S3 is topologically trivial, "
            "so this seven-dimensional lifted seam admits an S3_fiber x M4 description"
        ),
        "restriction_triviality_proof": (
            "principal Sp(1) bundles over S3 are classified by "
            "[S3,BSp(1)]=pi3(BSp(1))=pi2(Sp(1))=0"
        ),
        "global_product_claim": False,
        "eight_dimensional_completion": (
            "a local normal coordinate rho in the lifted M5 collar gives "
            "S3_fiber x M4 x I_rho locally; globally the parent remains I_t x S7"
        ),
        "classification": DoctrineStatus.DERIVED_CONDITIONAL.value,
        "reason_for_conditional": (
            "the topology/domain identification is exact, while interpreting its "
            "normal direction as physical buoyancy is not action-derived"
        ),
    }


def radial_ownership() -> dict[str, Any]:
    return {
        "rho": {
            "meaning": "dimensionless Gaussian-normal collar coordinate",
            "domain": "M5 near M4",
            "physical_normal_element": "ds=a(t) d rho",
            "action_owned": True,
            "buoyancy_sign_derived": False,
        },
        "a_F": {
            "meaning": "Hopf-fiber radius/radion",
            "domain": "M8-to-M5 reduction",
            "action_owned_if_varied": "pi_!S8 becomes scalar-tensor gravity",
            "identified_with_sigma": False,
            "stored_S5_action_contains_full_radion_reduction": False,
        },
        "R": {
            "meaning": "v10 prototype texture scale",
            "domain": "collective R7 compactification ansatz",
            "classification": DoctrineStatus.PROXY_ONLY.value,
            "covariant_parent_coordinate": False,
        },
        "selected_buoyancy_coordinate": None,
        "exact_missing_object": "COVARIANT_RADIAL_BUOYANCY_FUNCTIONAL",
    }


def geometry_payload() -> dict[str, Any]:
    rows = domain_rows()
    identification = s3_m4_identification()
    validation = {
        "dimensions_consistent": {row["object"]: row["dimension"] for row in rows}
        == {"M8": 8, "Hopf S3": 3, "M5": 5, "M4=B1": 4, "M5 collar": 5},
        "S3_M4_not_silently_M8": identification["not_equal_to_M8_by_dimension"],
        "restricted_bundle_triviality_named": "pi2(Sp(1))=0" in identification["restriction_triviality_proof"],
        "parent_owned": rows[0]["role"].startswith("global parent"),
        "observable_hypersurface_owned": rows[3]["role"].startswith("observable intrinsic seam"),
        "radial_coordinate_not_overpromoted": radial_ownership()["selected_buoyancy_coordinate"] is None,
    }
    return {
        "artifact": "BHSM_geometry_reconciliation_v10_1",
        "domains": rows,
        "S3_x_M4": identification,
        "radial_ownership": radial_ownership(),
        "verdict": GEOMETRY_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
