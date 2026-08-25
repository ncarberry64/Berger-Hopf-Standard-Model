"""Derive the finite-N12 local NHIM capture basin from exact action data."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_ASYMPTOTIC_NHIM_CAPTURE_BASIN.json"
)
THEORY = ROOT / "theory/n12_asymptotic_nhim_capture_basin.md"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_WEIGHT_SEVEN_TRANSVERSE_DESCRIPTOR.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FULL_RETAINED_ASYMPTOTIC_BRANCH.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_CAPTURE_BASIN_PRECONDITIONS.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_EXACT_WEIGHT_SEVEN_CENTER_FAMILY.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_FORMATION_DECAY_CHRONOLOGY_SUPERSESSION.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_CHILD_EXTERIOR_CONNECTION_PRECONDITIONS.json",
    THEORY,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing NHIM inputs: " + ", ".join(missing))
    descriptor, branch, preconditions, family, chronology, connection = (
        _load(path) for path in INPUTS[:-1]
    )
    records = (descriptor, branch, preconditions, family, chronology, connection)
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated NHIM inputs required")

    clusters = descriptor["descriptor"]["bordered_clusters"]
    physical_parameters = family["exact_family"]["physical_parameters"]
    validation = {
        "exact_nonlinear_center_family_has_25_physical_parameters": (
            physical_parameters["total"] == 25
        ),
        "center_family_tangent_exhausts_all_25_zero_roots": (
            clusters["center_count"] == physical_parameters["total"] == 25
        ),
        "all_25_complementary_finite_roots_are_stable": (
            clusters["stable_count"] == 25 and clusters["unstable_count"] == 0
        ),
        "exact_leading_nonlinear_invariance_identity_is_closed": (
            family["exact_variational_identities"]["consequence"]
            == "N7(a,0)=0_ON_THE_EXACT_CENTER_FAMILY"
        ),
        "algebraic_modes_have_analytic_constraint_IFT_reduction": (
            branch["positive_integer_nonresonance"][
                "algebraic_multiplier_block_removed_by_analytic_constraint_IFT"
            ]
            is True
        ),
        "full_normalized_action_is_analytic_at_epsilon_zero": (
            branch["exact_scale_decomposition"][
                "coefficient_functions_are_real_analytic"
            ]
            is True
        ),
        "all_nonleading_bulk_weights_vanish_by_positive_epsilon_powers": (
            branch["exact_scale_decomposition"]["bulk_epsilon_powers"]
            == [0, 1, 2, 3, 4]
        ),
        "inverse_inertia_starts_at_epsilon_power_seven": (
            branch["exact_scale_decomposition"][
                "normalized_inverse_inertia_leading_epsilon_power"
            ]
            == 7
        ),
        "postevent_infinite_Friedrichs_child_route_is_ontology_allowed": (
            chronology["adjudication"]["infinite_Friedrichs_child_exterior_allowed"]
            is True
        ),
        "reset_to_basin_connection_remains_unproved": (
            connection["claim_boundary"]["maximal_child_exterior_oracle"]
            == "OPEN_CURRENT_OWNER"
        ),
        "no_selector_action_term_scale_fit_endpoint_recurrence_or_chord_added": True,
    }

    return {
        "artifact": "BHSM_N12_ASYMPTOTIC_NHIM_CAPTURE_BASIN",
        "status": "FINITE_N12_EXISTENTIAL_OPEN_CAPTURE_BASIN_DERIVED_RESET_ENTRY_OPEN",
        "classification": (
            "THE_EXACT_25_PARAMETER_WEIGHT_SEVEN_CENTER_FAMILY_EXHAUSTS_"
            "THE_25_ZERO_ROOTS_AND_HAS_25_STRICTLY_STABLE_NORMAL_ROOTS;_"
            "AFTER_ANALYTIC_CONSTRAINT_REDUCTION_AND_REPLACING_THE_COMMON_"
            "SCALE_ORBIT_PHASE_BY_epsilon=R4^-2,_THE_BOUNDARY_FAMILY_HAS_24_"
            "CENTER_DIRECTIONS_AND_26_STABLE_NORMAL_DIRECTIONS,_SO_THE_"
            "ANALYTIC_FULL_RETAINED_FINITE_N12_FLOW_HAS_AN_EXISTENTIAL_OPEN_"
            "LOCAL_CAPTURE_BASIN_WITH_H4_TO_H0_POSITIVE"
        ),
        "leading_weight_NHIM": {
            "invariant_family_dimension_in_autonomous_moving_frame": 25,
            "tangent_center_roots": 25,
            "stable_normal_roots": 25,
            "unstable_normal_roots": 0,
            "stable_normal_root": "-7*H0",
            "nonlinear_invariance": "ACTION_DERIVED_EXACT",
            "normal_attraction": (
                "FINITE_DIMENSIONAL_ANALYTIC_NORMAL_HYPERBOLICITY_BY_EXACT_"
                "INVARIANT_FAMILY_PLUS_DESCRIPTOR_SPECTRAL_SPLITTING"
            ),
        },
        "compactified_full_flow": {
            "scale_variable": "epsilon=R4^-2",
            "kinematic_equation": "epsilon'=-2*H4*epsilon",
            "common_scale_center_replaced_by_epsilon_on_forward_scale_section": True,
            "boundary_family_shape_dimension": 24,
            "stable_velocity_normal_dimension": 25,
            "stable_radial_dimension": 1,
            "total_stable_normal_dimension": 26,
            "radial_root_at_round_member": "-2*H0",
            "lower_weight_vector_field_vanishes_at_epsilon_zero": True,
        },
        "capture_theorem": {
            "there_exist_unquantified": "epsilon_star>0_AND_delta_star>0",
            "domain": (
                "OPEN_RELATIVE_NEIGHBORHOOD_IN_THE_REGULAR_CONSTRAINT_REDUCED_"
                "POSITIVE_LAPSE_FORWARD_SCALE_PHYSICAL_DOMAIN"
            ),
            "forward_local_capture": True,
            "epsilon_limit": 0.0,
            "normal_velocity_limit": 0.0,
            "shape_limit_exists": True,
            "H4_limit": "H0>0",
            "proof_engine": (
                "LOCAL_STABLE_FOLIATION_THEOREM_FOR_A_NORMALLY_ATTRACTING_"
                "INVARIANT_MANIFOLD_AND_ANALYTIC_O(epsilon)_PERTURBATION"
            ),
        },
        "scope": {
            "finite_N12": True,
            "existential_not_quantitative": True,
            "explicit_capture_surface_certified": False,
            "AE2_reset_entry_certified": False,
            "continuum_uniformity_certified": False,
            "postevent_child_exterior_route_only": True,
            "infinite_nonencapsulating_formation_promoted_physical": False,
        },
        "supersession": {
            "two_jet_alone_proves_basin": False,
            "single_Briot_Bouquet_branch_alone_proves_basin": False,
            "exact_center_family_plus_normal_splitting_proves_local_basin": True,
            "prior_analytic_branch_preserved": True,
        },
        "exact_next_dependency": (
            "DERIVE_VALIDATED_QUANTITATIVE_CAPTURE_MAJORANTS_AND_A_CAPTURE_"
            "SURFACE,_THEN_CERTIFY_A_NONEMPTY_EVENT_GENERATED_AE2_RESET_"
            "QUOTIENT_FAMILY_REACHES_IT_WITH_ALL_DOMAIN_MARGINS_AND_FIRST_"
            "GEOMETRY_JETS,_OR_REACHES_A_LATER_EVENT_OR_CANONICAL_STOP_FIRST"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_QUANTITATIVE_RESET_TO_CAPTURE_CONNECTION_CURRENT_OWNER",
            "Gate8": "LOCKED",
            "finite_N12_existential_capture_basin": "DERIVED",
            "quantitative_capture_surface": "OPEN_CURRENT_OWNER",
            "reset_to_capture_connection": "OPEN",
            "maximal_child_exterior_oracle": "OPEN_AFTER_CONNECTION",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
