"""Materialize the current AE4 nonlinear carrier-authority adjudication."""

from __future__ import annotations

import hashlib
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae4_current_c2_nonlinear_carrier_authority_adjudication import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    nonlinear_carrier_authority_contract,
)


A = ROOT / "artifacts/action_extension"
F = ROOT / "artifacts/flagship_integration"
TRANSFER = F / "BHSM_N12_GATE7_AFFINE_72D_NONLINEAR_TRANSFER_AUDIT.json"
OUTWARD = F / "BHSM_N12_GATE7_ACCEPTED_REPLAY_CENTER_OUTWARD_74D_CONTRACTION.json"
BLOCK_SCREEN = F / "BHSM_N12_GATE7_ACCEPTED_REPLAY_ACTION_BLOCK_SCREEN.json"
GREEN_PARTITION = A / "BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.json"
GREEN_SEED = F / "BHSM_N12_GATE7_CURRENT_GREEN_DIRECTIONAL_CURVATURE_SEED.json"
GREEN_ENDPOINTS = F / "BHSM_N12_GATE7_CURRENT_GREEN_DIRECTIONAL_ENDPOINT_CURVATURE.json"
GREEN_MIDPOINT = F / "BHSM_N12_GATE7_CURRENT_GREEN_HERMITE_SIMPSON_MIDPOINT_CURVATURE.json"
GREEN_MIDPOINT_512 = F / "BHSM_N12_GATE7_CURRENT_GREEN_HERMITE_SIMPSON_MIDPOINT_CURVATURE_512BIT.json"
GREEN_CORRELATED_355 = F / "BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_INTERVAL355.json"
GREEN_CORRELATED_ALL = F / "BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_ALL_INTERVALS.json"
GREEN_CORRELATED_CAUSAL = F / "BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_CAUSAL_COMPOSITION.json"
GAUGE = A / "BHSM_AE4_CURRENT_C2_AFFINE72_GAUGE_CALDERON_FIRST_JET.json"
PARTICLE = A / "BHSM_AE4_CURRENT_C2_AFFINE72_PARTICLE_FIBER_CALDERON.json"
TARGET = A / "BHSM_AE4_CURRENT_C2_NONLINEAR_CARRIER_AUTHORITY_ADJUDICATION.json"
INPUTS = (
    TRANSFER,
    OUTWARD,
    BLOCK_SCREEN,
    GREEN_PARTITION,
    GREEN_SEED,
    GREEN_ENDPOINTS,
    GREEN_MIDPOINT,
    GREEN_MIDPOINT_512,
    GREEN_CORRELATED_355,
    GREEN_CORRELATED_ALL,
    GREEN_CORRELATED_CAUSAL,
    GAUGE,
    PARTICLE,
    ROOT / "src/bhsm/interface/ae4_current_c2_nonlinear_carrier_authority_adjudication.py",
    ROOT / "scripts/materialize_ae4_current_c2_nonlinear_carrier_authority_adjudication.py",
    ROOT / "theory/ae4_current_c2_nonlinear_carrier_authority_adjudication.md",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


@lru_cache(maxsize=1)
def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    transfer, outward, block_screen, green_partition, green_seed, green_endpoints, green_midpoint, green_midpoint_512, green_correlated_355, green_correlated_all, green_correlated_causal, gauge, particle = (
        _load(path) for path in INPUTS[:13]
    )
    if not all(
        row.get("validation_passed") is True
        for row in (
            transfer, outward, block_screen, green_partition, green_seed, green_endpoints, green_midpoint, green_midpoint_512, green_correlated_355, green_correlated_all, green_correlated_causal,
            gauge, particle
        )
    ):
        raise RuntimeError("validated transfer, outward, and AE4 carrier inputs required")

    transfer_allowed = transfer["adjudication"][
        "affine_jet_may_be_used_as_complete_operator_authority"
    ]
    decision = outward["decision"]
    result = nonlinear_carrier_authority_contract(
        affine_transfer_allowed=transfer_allowed,
        same_center_contraction_obstructed=decision[
            "current_same_center_contraction_theorem_obstructed"
        ],
        field_descriptor_block_obstructed=block_screen["decision"][
            "coarse_73_plus_1_field_descriptor_block_route_obstructed"
        ],
        green_image_partition_recovered=green_partition["claim_boundary"][
            "G7_BHSM_NATIVE_GREEN_IMAGE_PARTITION_RECOVERED"
        ],
        green_directional_seed_derived=green_seed["claim_boundary"][
            "CURRENT_CENTER_NODE1_GREEN_DIRECTIONAL_RATE_CURVATURE_DERIVED"
        ],
        green_directional_endpoints_derived=green_endpoints["claim_boundary"][
            "CURRENT_CENTER_ALL_POST_RESET_ENDPOINT_GREEN_DIRECTIONAL_CURVATURE_DERIVED"
        ],
        green_midpoint_componentwise_route_obstructed=green_midpoint[
            "claim_boundary"
        ]["CURRENT_CENTER_COMPONENTWISE_GREEN_DIRECTION_BALL_MIDPOINT_ROUTE_OBSTRUCTED"],
        green_correlated_scalar_interval355_finite=green_correlated_355[
            "claim_boundary"
        ]["CURRENT_GREEN_CORRELATED_SCALAR_INTERVAL355_FINITE"],
        green_correlated_scalar_all_intervals_derived=green_correlated_all[
            "claim_boundary"
        ]["CURRENT_GREEN_CORRELATED_SCALAR_ALL_INTERVALS_DERIVED"],
        green_correlated_scalar_causal_composition_derived=green_correlated_causal[
            "claim_boundary"
        ]["CURRENT_GREEN_CORRELATED_CENTRAL_SCALAR_CAUSAL_COMPOSITION_DERIVED"],
        root_nonexistence_claim=decision["root_nonexistence_claim"],
        physical_instability_claim=decision[
            "physical_spacetime_instability_claim"
        ],
        another_center_or_trajectory_authorized=decision[
            "another_center_or_trajectory_authorized"
        ],
    )
    operands = outward["outward_operands"]
    boundary = claim_boundary()
    validation = {
        "same_center_outward_calculation_already_complete": (
            outward["owner"]
            == "SAME_CENTER_GATE7_Z2_PHYSICAL_LOCALIZATION_AND_ADJUDICATION"
            and outward["validation_passed"]
        ),
        "necessary_scalar_discriminant_strictly_negative": (
            operands[
                "necessary_discriminant_upper_1_minus_4_Ylower_Z2lower"
            ]
            < 0.0
            and outward["validation"][
                "necessary_quadratic_discriminant_strictly_negative"
            ]
        ),
        "affine_transfer_independently_rejected": transfer_allowed is False,
        "gauge_candidate_remains_non_authoritative": (
            gauge["validation_passed"]
            and not gauge["carrier"]["nonlinear_exact_family_authority"]
        ),
        "particle_candidate_remains_non_authoritative": (
            particle["validation_passed"]
            and not particle["carrier"]["nonlinear_exact_family_authority"]
            and particle["scientific_result"]["attached_existing_fiber_count"]
            == 9
        ),
        "no_physical_instability_or_root_nonexistence_overclaim": (
            not result["physical_spacetime_instability_inferred"]
            and not result["root_nonexistence_inferred"]
            and not boundary["G7_ROOT_NONEXISTENCE_DERIVED"]
            and not boundary["G7_PHYSICAL_SPACETIME_INSTABILITY_DERIVED"]
        ),
        "no_new_numerical_campaign_authorized": (
            not result[
                "accepted_replay_center_or_trajectory_may_be_reselected"
            ]
            and not boundary["NEW_CENTER_OR_TRAJECTORY_AUTHORIZED"]
        ),
        "scalar_route_not_left_as_open_next_calculation": boundary[
            "G7_SINGLE_RADIUS_74D_CONTRACTION_ROUTE_OBSTRUCTED"
        ],
        "coarse_field_descriptor_route_not_left_open": (
            boundary["G7_FIELD_DESCRIPTOR_BLOCK_CONTRACTION_ROUTE_OBSTRUCTED"]
            and block_screen["necessary_field_block_test"]["discriminant_upper"]
            < 0.0
        ),
        "BHSM_native_green_longitudinal_correlation_is_reused": (
            green_partition["validation_passed"]
            and boundary["G7_BHSM_NATIVE_GREEN_IMAGE_PARTITION_RECOVERED"]
            and boundary["G7_CURRENT_CENTER_CORRELATED_GREEN_NORMALIZATION_TRANSPORT_DERIVED"]
        ),
        "current_green_directional_seed_is_reused": (
            green_seed["validation_passed"]
            and green_seed["green_directional_rate_curvature"]["total"][
                "upper"
            ]
            < 0.03
        ),
        "all_post_reset_green_directional_endpoints_are_reused": (
            green_endpoints["validation_passed"]
            and green_endpoints["post_reset_nodes_certified"] == 370
            and green_endpoints["terminal_endpoint_stiffening"][
                "terminal_node"
            ] == 370
        ),
        "componentwise_green_midpoint_obstruction_is_reused": (
            green_midpoint["validation_passed"]
            and green_midpoint["componentwise_direction_ball_obstruction"][
                "first_nonfinite_intrinsic_interval"
            ] == 355
            and not green_midpoint["claim_boundary"][
                "CURRENT_CENTER_GREEN_MIDPOINT_INTRINSIC_CURVATURE_GLOBAL_FINITE_ENCLOSURE_DERIVED"
            ]
        ),
        "componentwise_green_midpoint_obstruction_persists_at_512_bit": (
            green_midpoint_512["validation_passed"]
            and green_midpoint_512["componentwise_direction_ball_obstruction"][
                "first_nonfinite_intrinsic_interval"
            ] == 355
            and green_midpoint_512["componentwise_direction_ball_obstruction"][
                "nonfinite_intrinsic_intervals"
            ] == list(range(355, 370))
            and green_midpoint_512["claim_boundary"][
                "CURRENT_CENTER_COMPONENTWISE_GREEN_DIRECTION_BALL_MIDPOINT_ROUTE_OBSTRUCTED"
            ]
            and not green_midpoint_512["claim_boundary"][
                "CURRENT_GREEN_AXIS_NEIGHBORHOOD_MIXED_TRANSVERSE_BOUND_DERIVED"
            ]
        ),
        "correlated_green_scalar_interval355_reconciliation_is_reused": (
            green_correlated_355["validation_passed"]
            and green_correlated_355["interval"] == 355
            and green_correlated_355["operand_norm_bounds"][
                "midpoint_intrinsic_curvature"
            ]["upper"] < 0.012207
        ),
        "all_370_correlated_green_scalar_intervals_are_reused": (
            green_correlated_all["validation_passed"]
            and green_correlated_all["intervals_certified"] == 370
            and green_correlated_all["claim_boundary"][
                "CURRENT_GREEN_CORRELATED_SCALAR_ALL_INTERVALS_DERIVED"
            ]
            and not green_correlated_all["claim_boundary"][
                "CURRENT_GREEN_AXIS_NEIGHBORHOOD_MIXED_TRANSVERSE_BOUND_DERIVED"
            ]
        ),
        "correlated_green_central_scalar_causal_composition_is_reused": (
            green_correlated_causal["validation_passed"]
            and green_correlated_causal["nodes_composed"] == 371
            and green_correlated_causal["first_recursive_wrapping_node"] is None
            and green_correlated_causal["maximum_causal_curvature_norm_upper"] < 8.406
            and not green_correlated_causal["claim_boundary"][
                "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED"
            ]
        ),
    }
    return {
        "artifact": "BHSM_AE4_CURRENT_C2_NONLINEAR_CARRIER_AUTHORITY_ADJUDICATION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "recovered_same_center_operands": {
            "Y_lower": operands["Y_lower"],
            "Z1_upper": operands["Z1_upper"],
            "Z2_required_lower_from_center_direction": operands[
                "Z2_required_lower_from_center_direction"
            ],
            "necessary_discriminant_upper": operands[
                "necessary_discriminant_upper_1_minus_4_Ylower_Z2lower"
            ],
        },
        "recovered_coarse_block_obstruction": {
            "field_Y_lower": block_screen["outward_center_defect"][
                "field_Y_lower"
            ],
            "field_from_field_curvature_lower": block_screen[
                "existing_curvature_witness"
            ]["terminal_field_block_curvature_lower"],
            "necessary_field_discriminant_upper": block_screen[
                "necessary_field_block_test"
            ]["discriminant_upper"],
        },
        "recovered_green_image_partition": {
            "absolute_obstruction_longitudinal_projection_upper": (
                green_partition["coarse_obstruction_localization"][
                    "absolute_longitudinal_projection_upper"
                ]
            ),
            "obstruction_transverse_projection_lower": green_partition[
                "coarse_obstruction_localization"
            ]["transverse_projection_lower"],
            "historical_numerical_values_reused": False,
        },
        "recovered_green_directional_seed": {
            "node": green_seed["node"],
            "curvature_lower": green_seed[
                "green_directional_rate_curvature"
            ]["total"]["lower"],
            "curvature_upper": green_seed[
                "green_directional_rate_curvature"
            ]["total"]["upper"],
            "transverse_to_green_lower_factor": green_seed[
                "comparison_to_existing_transverse_obstruction"
            ]["transverse_to_green_lower_factor"],
        },
        "recovered_green_directional_endpoints": {
            "post_reset_nodes_certified": green_endpoints[
                "post_reset_nodes_certified"
            ],
            "minimum_curvature_lower": green_endpoints[
                "endpoint_green_directional_curvature_norm"
            ]["minimum_lower"],
            "maximum_curvature_upper": green_endpoints[
                "endpoint_green_directional_curvature_norm"
            ]["maximum_upper"],
            "maximum_upper_owner_node": green_endpoints[
                "endpoint_green_directional_curvature_norm"
            ]["maximum_upper_owner_node"],
            "terminal_to_node1_upper_growth_factor": green_endpoints[
                "terminal_endpoint_stiffening"
            ]["terminal_to_node1_upper_growth_factor"],
            "raw_terminal_growth_is_not_causal_obstruction": True,
        },
        "recovered_green_midpoint_obstruction": {
            "finite_intrinsic_prefix_intervals": green_midpoint[
                "componentwise_direction_ball_obstruction"
            ]["finite_intrinsic_prefix_intervals"],
            "first_nonfinite_intrinsic_interval": green_midpoint[
                "componentwise_direction_ball_obstruction"
            ]["first_nonfinite_intrinsic_interval"],
            "midpoint_direction_and_second_incidence_remain_finite": green_midpoint[
                "componentwise_direction_ball_obstruction"
            ]["midpoint_direction_and_second_incidence_remain_finite"],
            "physical_instability_or_path_nonexistence_inferred": False,
            "same_first_nonfinite_interval_at_512_bit": green_midpoint_512[
                "componentwise_direction_ball_obstruction"
            ]["first_nonfinite_intrinsic_interval"],
            "higher_precision_removes_obstruction": False,
        },
        "recovered_green_correlated_scalar_interval355": {
            "midpoint_intrinsic_curvature_upper": green_correlated_355[
                "operand_norm_bounds"
            ]["midpoint_intrinsic_curvature"]["upper"],
            "local_HS_second_residual_upper": green_correlated_355[
                "operand_norm_bounds"
            ]["local_HS_second_residual"]["upper"],
            "left_axis_neighborhood_error_upper": green_correlated_355[
                "central_axis_neighborhood_error_upper"
            ]["left_node_355"],
            "right_axis_neighborhood_error_upper": green_correlated_355[
                "central_axis_neighborhood_error_upper"
            ]["right_node_356"],
            "global_or_causal_promotion": False,
        },
        "recovered_green_correlated_scalar_all_intervals": {
            "intervals_certified": green_correlated_all["intervals_certified"],
            "maximum_norm_upper": green_correlated_all["maximum_norm_upper"],
            "maximum_norm_owner_interval": green_correlated_all[
                "maximum_norm_owner_interval"
            ],
            "maximum_axis_neighborhood_error_upper": green_correlated_all[
                "axis_neighborhood"
            ]["maximum_error_upper"],
            "maximum_axis_neighborhood_error_owner_node": green_correlated_all[
                "axis_neighborhood"
            ]["maximum_error_owner_node"],
            "axis_neighborhood_mixed_transverse_bound_derived": False,
        },
        "recovered_green_correlated_central_scalar_causal_composition": {
            "nodes_composed": green_correlated_causal["nodes_composed"],
            "maximum_causal_curvature_norm_upper": green_correlated_causal[
                "maximum_causal_curvature_norm_upper"
            ],
            "maximum_causal_curvature_owner_node": green_correlated_causal[
                "maximum_causal_curvature_owner_node"
            ],
            "exact_axis_neighborhood_causal_composition_derived": False,
            "two_radius_certificate_derived": False,
        },
        "authority_adjudication": result,
        "claim_boundary": boundary,
        "exact_next_calculation": result["next_proof_object"],
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("nonlinear carrier-authority adjudication failed")
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
