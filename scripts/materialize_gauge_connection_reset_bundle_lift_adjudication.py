"""Materialize the AE4 gauge-reset bundle-lift adjudication."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Mapping

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.gauge_connection_reset_bundle_lift_adjudication import (  # noqa: E402
    ACTION_VERSION,
    CLASSIFICATION,
    EXACT_CLOSED_VERTICAL_DATUM,
    EXACT_MISSING_BASE_DATUM,
    EXACT_MISSING_DATUM,
    STATUS,
    claim_boundary,
    common_reset_gauge_vertical_one_jet,
    conditional_geometry_checks,
    downstream_status,
    local_one_jet_nonuniqueness_witness,
    ownership_levels,
    one_jet_component_status,
    requested_object_classification,
    spatial_base_attachment_authority,
    spatial_base_route_audit,
    spatial_correspondence_nonuniqueness_witness,
    source_lineage_ledger,
)


TARGET = ROOT / (
    "artifacts/action_extension/"
    "BHSM_GAUGE_CONNECTION_RESET_BUNDLE_LIFT_ADJUDICATION.json"
)
SCRIPT = Path(__file__).resolve()
MODULE = ROOT / (
    "src/bhsm/interface/gauge_connection_reset_bundle_lift_adjudication.py"
)
THEORY = ROOT / "theory/bhsm_gauge_connection_reset_bundle_lift_adjudication.md"
TEST = ROOT / "tests/test_gauge_connection_reset_bundle_lift_adjudication.py"
FIREWALL_AUTHORITY = (
    ROOT / "artifacts/BHSM_aether_n3_firewall_core_child_ownership_v17_98.json"
)


def _sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in {".py", ".md", ".json"}:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest().upper()


def _canonical(value: Any) -> Any:
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.ndarray):
        return _canonical(value.tolist())
    if isinstance(value, np.complexfloating):
        value = complex(value)
    if isinstance(value, complex):
        if not (math.isfinite(value.real) and math.isfinite(value.imag)):
            raise ValueError("non-finite complex value")
        return {"real": _canonical(value.real), "imag": _canonical(value.imag)}
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float value")
        rounded = round(value, 12)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True, allow_nan=False) + "\n"


def build_payload() -> dict[str, Any]:
    levels = ownership_levels()
    split = one_jet_component_status()
    vertical_witness = common_reset_gauge_vertical_one_jet(3, 16)
    vertical = {
        "status": vertical_witness["status"],
        "object": vertical_witness["object"],
        "G_R": "I_16",
        "dG_R": "ZERO_3_BY_16_BY_16",
        "full_spin_lift_derivative_claimed_zero": vertical_witness[
            "full_spin_lift_derivative_claimed_zero"
        ],
        "independent_relative_gauge_parameter": vertical_witness[
            "independent_relative_gauge_parameter"
        ],
        "frame_covariance": vertical_witness["frame_covariance"],
    }
    lineage = source_lineage_ledger()
    ambiguity = local_one_jet_nonuniqueness_witness()
    conditional = conditional_geometry_checks()
    downstream = downstream_status()
    object_classification = requested_object_classification()
    authority = spatial_base_attachment_authority()
    route_audit = spatial_base_route_audit()
    spatial_ambiguity = spatial_correspondence_nonuniqueness_witness()
    firewall_authority = json.loads(FIREWALL_AUTHORITY.read_text(encoding="utf-8"))
    claims = claim_boundary()
    source_paths = (
        "src/bhsm/interface/aether_hybrid_standard_model_bundle_v15_53.py",
        "src/bhsm/interface/action_extension_global_spin_reset_ae2.py",
        "src/bhsm/interface/ae2_covariant_seam_response.py",
        "src/bhsm/interface/ae31_c2_reset_hadamard_transport.py",
        "src/bhsm/interface/aether_n3_event_complete_child_correspondence_v17_84.py",
        "src/bhsm/interface/aether_n3_event_attachment_state_incidence_v17_89.py",
        "src/bhsm/interface/aether_n3_terminal_child_boundary_map_v17_85.py",
        "src/bhsm/interface/aether_material_skin_variation_v15_15.py",
        "src/bhsm/interface/aether_boundary_identity_ejection_v15_13.py",
        "src/bhsm/interface/aether_hybrid_actualization_persistence_v15_52.py",
        "src/bhsm/interface/aether_n3_firewall_core_child_ownership_v17_98.py",
        "src/bhsm/interface/aether_reconstruction_firewall_event_v15_45.py",
        "artifacts/BHSM_aether_n3_firewall_core_child_ownership_v17_98.json",
        "scripts/audit_n12_intrinsic_state_return_section.py",
        "scripts/derive_n12_reset_stratum_moving_endpoint_jets.py",
        "src/bhsm/interface/reset_boundary_generating_functional_adjudication.py",
        str(MODULE.relative_to(ROOT)).replace("\\", "/"),
        str(SCRIPT.relative_to(ROOT)).replace("\\", "/"),
        str(THEORY.relative_to(ROOT)).replace("\\", "/"),
        str(TEST.relative_to(ROOT)).replace("\\", "/"),
    )
    hashes = {
        source: _sha256(ROOT / source)
        for source in sorted(source_paths)
        if (ROOT / source).is_file()
    }
    validation = {
        "three_ownership_levels_distinguished": (
            levels["bundle_isomorphism_class"]["status"] == "EXISTS"
            and levels["actual_equivariant_bundle_morphism"]["status"]
            == "EXISTS_ABSTRACTLY_ON_THE_AE2_BOUNDARY_BUNDLE"
            and levels["induced_connection_transport"]["configuration_map"] is None
        ),
        "focused_source_lineage_classified": (
            len(lineage) == 17
            and all(row["found"] and row["not_found"] for row in lineage)
        ),
        "AE2_abstract_lift_not_erased": claims[
            "abstract_AE2_equivariant_boundary_lift_exists"
        ],
        "missing_spatial_base_half_exposed": (
            not claims["evaluable_principal_bundle_lift_local_one_jet_exists"]
            and claims["exact_missing_datum"] == EXACT_MISSING_BASE_DATUM
        ),
        "vertical_gauge_one_jet_closed_in_common_frame": (
            split["B_vertical_gauge_lift"]["status"] == "CLOSED"
            and np.allclose(vertical_witness["G_R"], np.eye(16))
            and np.allclose(vertical_witness["dG_R"], 0.0)
            and claims["common_reset_frame_gauge_vertical_one_jet_derived"]
        ),
        "full_spin_lift_derivative_not_overclaimed": (
            not vertical_witness["full_spin_lift_derivative_claimed_zero"]
        ),
        "N12_state_jet_rejected_as_spatial_base_jet": (
            split["A_base_attachment"]["local_spatial_map_F_B"] is None
            and "R^196_TO_R^57" in split["A_base_attachment"]["N12_first_hit_map"]
            and split["A_base_attachment"]["implicit_differentiation_for_DF_B"].startswith(
                "INAPPLICABLE"
            )
        ),
        "base_tangent_nonuniqueness_demonstrated": ambiguity[
            "distinct_children_from_missing_base_tangent"
        ],
        "child_spatial_ontology_is_case_4": authority["child_ontology"].startswith(
            "CASE_4"
        ),
        "all_four_base_map_routes_exhausted": (
            [row["route"][0] for row in route_audit] == ["A", "B", "C", "D"]
            and all(row["status"] == "DOES_NOT_CLOSE" for row in route_audit)
        ),
        "no_embedding_flow_collar_or_implicit_map_promoted": (
            authority["event_embedding"] is None
            and authority["child_embedding"] is None
            and authority["flow_if_any"]["spatial_event_child_flow"] is None
            and authority["collar_if_any"]["event_wide_attachment_map"] is None
            and authority["F_B"] is None
            and authority["D_F_B"] is None
        ),
        "S3_times_S3_cross_copy_nonuniqueness_demonstrated": (
            spatial_ambiguity["same_degree"] == 1
            and spatial_ambiguity["same_orientation"]
            and spatial_ambiguity["same_volume_jacobian"]
            and spatial_ambiguity["both_preserve_product_tangent_metric"]
            and spatial_ambiguity["tangent_maps_distinct"]
            and spatial_ambiguity["connection_components_can_differ"]
        ),
        "field_state_boundary_map_not_confused_with_spatial_map": (
            firewall_authority["firewall_core_child_ownership"][
                "complete_retained_F_child"
            ]["boundary_map_closed"]
            and firewall_authority["validation_passed"]
            and authority["F_B"] is None
        ),
        "conditional_connection_law_verified": (
            conditional["connection_pullback_residual"] < 1.0e-12
            and conditional["nonzero_trace_transported"]
            and conditional["affine_term_nonzero"]
        ),
        "reference_zero_field_recovered": (
            conditional["reference_identity_zero_field_recovery_residual"] < 1.0e-12
        ),
        "conditional_witness_not_promoted_to_BHSM_background": conditional[
            "not_an_admissible_BHSM_background_evaluation"
        ],
        "canonical_chain_fails_closed": (
            downstream["R_A"] is None
            and downstream["Maxwell_conormal_cotangent_lift"] is None
            and downstream["S_RESET_GFHS"] is None
        ),
        "requested_objects_separately_classified": (
            object_classification["F_B"].startswith("OPEN")
            and object_classification["D_F_B"].startswith("OPEN")
            and "GAUGE_FACTOR_IS_I" in object_classification["U_R"]
            and "dG_R_EQUALS_ZERO" in object_classification["d_U_R"]
            and object_classification["R_A"].startswith("OPEN")
            and set(object_classification["global_S1_S4"]) == {"S1", "S2", "S3", "S4"}
        ),
        "HS_rank_zero_retained": (
            downstream["HS_normal_Legendre_rank"] == 0
            and downstream["pi_H"] == 0.0
        ),
        "no_invalidated_route_reused": (
            not claims["constant_v15_57_reused"]
            and not claims["family_spectrum_rebuilt"]
        ),
        "no_empirical_coefficient_or_physical_promotion": (
            not claims["empirical_coefficients_used"]
            and not claims["FULL_FIELD_ACTION_ATTACHMENT_READY_FOR_GATE7_BACKGROUND"]
            and not claims["physical_background_bound"]
            and not claims["physical_HS_direction_derived"]
            and not claims["physical_yukawas_derived"]
            and not claims["physical_spectrum_derived"]
            and not claims["FULL_BHSM_COMPLETE"]
        ),
    }
    payload = {
        "artifact": "BHSM_GAUGE_CONNECTION_RESET_BUNDLE_LIFT_ADJUDICATION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "status": STATUS,
        **authority,
        "spatial_base_route_audit": route_audit,
        "spatial_correspondence_nonuniqueness": spatial_ambiguity,
        "prior_blocker_refinement": {
            "prior": (
                "ACTION_OWNED_NONZERO_GAUGE_CONNECTION_TRACE_AE4_RESET_MAP_"
                "R_A[B;GAMMA0_A_EVENT]_TO_GAMMA0_A_CHILD"
            ),
            "refined_first_geometric_datum": EXACT_MISSING_BASE_DATUM,
            "reason": (
                "THE_CHILD_IS_A_SEPARATE_POST_CUT_BOUNDARY_COPY_AND_THE_"
                "RETAINED_ACTION_CLOSES_STATE_INHERITANCE_BUT_SUPPLIES_NO_"
                "CROSS_COPY_SPATIAL_POINT_CORRESPONDENCE"
            ),
        },
        "ownership_levels": levels,
        "one_jet_component_split": split,
        "common_reset_gauge_vertical_one_jet": vertical,
        "focused_source_lineage": lineage,
        "local_one_jet_nonuniqueness": ambiguity,
        "conditional_connection_geometry": conditional,
        "downstream_canonical_chain": downstream,
        "requested_object_classification": object_classification,
        "VALIDATED": [
            "V15_53_OWNS_THE_RETURNED_SM_BUNDLE_ISOMORPHISM_CLASS",
            "AE2_OWNS_AN_ABSTRACT_SMOOTH_SPIN_GAUGE_BOUNDARY_LIFT_U_R",
            EXACT_CLOSED_VERTICAL_DATUM,
            "CHILD_ONTOLOGY_IS_CASE_4_ABSTRACT_POST_CUT_BOUNDARY_COPY",
            (
                "V17_98_CLOSES_THE_FIELD_STATE_BOUNDARY_SOLVABILITY_RELATION_"
                "NOT_A_SPATIAL_POINT_MAP"
            ),
            (
                "THE_N12_FIRST_HIT_JACOBIAN_AND_MOVING_ENDPOINT_JETS_ACT_ON_"
                "CAUCHY_STATE_SPACE,_NOT_THE_SPATIAL_BOUNDARY_BASE"
            ),
            (
                "THE_REPOSITORY_CONNECTION_COMPATIBILITY_EQUATION_IS_dU_PLUS_"
                "FSTAR_A_CHILD_U_MINUS_U_A_EVENT_EQUALS_ZERO"
            ),
            (
                "A_SUPPLIED_LOCAL_ONE_JET_DEFINES_AN_AFFINE_NONZERO_"
                "CONNECTION_TRANSPORT_AND_ITS_LINEARIZATION"
            ),
            (
                "THE_RANK16_U1_SU2_SU3_THREE_FAMILY_STRUCTURE_IS_"
                "CONDITIONALLY_PRESERVED_BY_A_G_SM_VALUED_LIFT"
            ),
            "HS_NORMAL_LEGENDRE_RANK_ZERO_AND_PI_H_ZERO_REMAIN_UNCHANGED",
        ],
        "INVALIDATED": [
            "BUNDLE_ISOMORPHISM_CLASS_IS_AN_EVALUABLE_CONNECTION_TRANSPORT",
            "THE_AE2_COMMON_RESET_FRAME_SUPPLIES_THE_SPATIAL_BASE_MAP_F_B_OR_DF_B",
            "THE_N12_R196_TO_R57_STATE_JACOBIAN_IS_DF_B",
            "THE_TOPOLOGICAL_CUT_NOTATION_ALONE_SUPPLIES_EXECUTABLE_CROSS_COPY_EMBEDDINGS",
            "THE_V15_13_SCALAR_CLOSEST_POINT_DISTANCE_IS_AN_EVENT_WIDE_NORMAL_EXPONENTIAL_MAP",
            "THE_RETAINED_CAUCHY_STATE_FLOW_IS_A_SPATIAL_EVENT_CHILD_FLOW",
            (
                "NABLA_PHI_U_R_EQUALS_ZERO_IN_A_PARAMETER_SPACE_RESPONSE_"
                "WITNESS_INSTANTIATES_THE_PHYSICAL_SPACETIME_GAUGE_"
                "CONNECTION_RESET"
            ),
            "BOUNDARY_INCIDENCE_OR_ORIENTATION_ALONE_DETERMINES_THE_PULLBACK_OF_A_ONE_FORM",
            "V15_57_CONSTANT_ZERO_BACKGROUND_RECONSTRUCTION_DEFINES_THE_NONZERO_RESET",
            "THE_CONDITIONAL_FINITE_WITNESS_IS_AN_ADMISSIBLE_BHSM_BACKGROUND",
        ],
        "OPEN": [EXACT_MISSING_BASE_DATUM],
        "EXACT_NEXT_OBJECT": EXACT_MISSING_BASE_DATUM,
        "exact_next_calculation": (
            "DERIVE_FROM_THE_ACTION_OR_DOMAIN_AN_EXPLICIT_CROSS_COPY_SPATIAL_"
            "ATTACHMENT_MORPHISM_BETWEEN_THE_SEPARATE_EVENT_AND_CHILD_S3_"
            "TIMES_S3_BOUNDARY_COPIES;_ONLY_THEN_DIFFERENTIATE_IT_AND_"
            "INSTANTIATE_CONNECTION_AND_MAXWELL_TRANSPORT"
        ),
        "empirical_inputs": [],
        "claims": claims,
        "source_sha256": hashes,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    payload["validated"] = payload["VALIDATED"]
    payload["invalidated"] = payload["INVALIDATED"]
    payload["open"] = payload["OPEN"]
    return payload


def main() -> Path:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(deterministic_json(build_payload()), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(main())
