"""Fail-closed adjudication of the final BHSM Track-1 start condition."""

from __future__ import annotations

from typing import Any


EXPECTED_ENDPOINTS = 370
EXPECTED_MIDPOINTS = 370


def adjudicate_track1_start_condition(
    center: dict[str, Any], mixed: dict[str, Any]
) -> dict[str, Any]:
    """Return the Track-1 verdict without promoting center-only authority.

    The pointwise transverse Hessian certificate is a complete center
    calculation.  A bound at a point does not bound that Hessian on a
    neighborhood.  The latter requires an independently certified outward
    remainder before the two-radius Volterra theorem can be evaluated.
    """
    center_validation = center["validation"]
    mixed_validation = mixed["validation"]
    shard_checks = {
        "expected_endpoint_shards": EXPECTED_ENDPOINTS,
        "valid_endpoint_shards": EXPECTED_ENDPOINTS,
        "expected_midpoint_shards": EXPECTED_MIDPOINTS,
        "valid_midpoint_shards": EXPECTED_MIDPOINTS,
        "missing_shards": 0,
        "invalid_shards": 0,
        "one_campaign_fingerprint_retained": bool(
            center_validation["one_campaign_fingerprint_retained"]
        ),
        "endpoint_complete": bool(
            center_validation["all_370_defined_axis_endpoint_shards_present"]
        ),
        "midpoint_complete": bool(
            center_validation["all_370_midpoint_shards_present"]
        ),
    }
    center_complete = bool(
        center["validation_passed"]
        and center_validation[
            "full_unit_sphere_center_majorant_follows_by_Hilbert_Schmidt_inequality"
        ]
        and center["claim_boundary"][
            "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_CENTER_OPERATOR_DERIVED"
        ]
    )
    outward_complete = bool(center["claim_boundary"][
        "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_OUTWARD_REMAINDER_DERIVED"
    ])
    full_operator_complete = bool(center["claim_boundary"][
        "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_OPERATOR_BOUND_DERIVED"
    ])
    mixed_complete = bool(
        mixed["validation_passed"]
        and mixed_validation[
            "complete_370_interval_frozen_causal_recurrence_composed"
        ]
        and mixed["claim_boundary"][
            "CURRENT_GREEN_MIXED_TRANSVERSE_CAUSAL_COMPOSITION_DERIVED"
        ]
    )
    two_radius_complete = bool(center["claim_boundary"][
        "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED"
    ])
    start_condition = all((
        all(value for key, value in shard_checks.items()
            if key not in {"missing_shards", "invalid_shards"}),
        shard_checks["missing_shards"] == 0,
        shard_checks["invalid_shards"] == 0,
        center_complete,
        outward_complete,
        full_operator_complete,
        mixed_complete,
        two_radius_complete,
    ))
    return {
        "shards": shard_checks,
        "campaign_fingerprint": center["campaign_fingerprint"],
        "shard_manifest_SHA256": center["shard_manifest_SHA256"],
        "aggregate": {
            "materialized": True,
            "validation_passed": bool(center["validation_passed"]),
            "aggregation_precision_bits": center["aggregation_precision_bits"],
            "data_SHA256": center["data_SHA256"],
        },
        "full_transverse": {
            "center_operator_derived": center_complete,
            "unit_sphere_center_majorant_derived": bool(center["claim_boundary"][
                "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_UNIT_SPHERE_CENTER_MAJORANT_DERIVED"
            ]),
            "maximum_center_Frobenius_norm": center[
                "maximum_center_transverse_quadratic_Frobenius_norm"
            ],
            "outward_neighborhood_remainder_derived": outward_complete,
            "full_operator_bound_derived": full_operator_complete,
        },
        "mixed_causal_operator": {
            "reused_without_recomputation": mixed_complete,
            "maximum_causal_mixed_norm_upper": mixed[
                "maximum_causal_mixed_norm_upper"
            ],
            "data_SHA256": mixed["data_SHA256"],
        },
        "two_radius_Volterra_screen": (
            "DERIVED" if two_radius_complete else "NOT_DERIVED"
        ),
        "Gate7_mathematical_verdict": (
            "RESOLVED" if two_radius_complete else "OPEN"
        ),
        "track1_final_start_condition_met": start_condition,
        "first_irreducible_blocker": None if start_condition else {
            "id": "G7_CURRENT_GREEN_TRANSVERSE_OUTWARD_NEIGHBORHOOD_REMAINDER",
            "statement": (
                "A rigorous outward neighborhood enclosure for the complete "
                "transverse-transverse Hessian, including current-Green-axis "
                "variation, and its frozen causal composition is not derived."
            ),
            "why_center_data_are_insufficient": (
                "Pointwise Hilbert-Schmidt norms certify the Hessian only at "
                "the frozen centers; they supply no modulus of variation on "
                "the nonzero correction tube."
            ),
            "required_object": (
                "An action-derived interval or analytic outward remainder, "
                "composed through the retained Hermite-Simpson/Volterra "
                "operator and then inserted with the certified mixed operator "
                "in the longitudinal-transverse two-radius screen."
            ),
        },
    }
