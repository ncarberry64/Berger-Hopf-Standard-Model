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
    EXACT_MISSING_DATUM,
    STATUS,
    claim_boundary,
    conditional_geometry_checks,
    downstream_status,
    local_one_jet_nonuniqueness_witness,
    ownership_levels,
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
    lineage = source_lineage_ledger()
    ambiguity = local_one_jet_nonuniqueness_witness()
    conditional = conditional_geometry_checks()
    downstream = downstream_status()
    claims = claim_boundary()
    source_paths = (
        "src/bhsm/interface/aether_hybrid_standard_model_bundle_v15_53.py",
        "src/bhsm/interface/action_extension_global_spin_reset_ae2.py",
        "src/bhsm/interface/ae2_covariant_seam_response.py",
        "src/bhsm/interface/ae31_c2_reset_hadamard_transport.py",
        "src/bhsm/interface/aether_n3_event_complete_child_correspondence_v17_84.py",
        "src/bhsm/interface/aether_n3_event_attachment_state_incidence_v17_89.py",
        "src/bhsm/interface/aether_n3_terminal_child_boundary_map_v17_85.py",
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
            len(lineage) == 11
            and all(row["found"] and row["not_found"] for row in lineage)
        ),
        "AE2_abstract_lift_not_erased": claims[
            "abstract_AE2_equivariant_boundary_lift_exists"
        ],
        "missing_local_one_jet_exposed": (
            not claims["evaluable_principal_bundle_lift_local_one_jet_exists"]
            and claims["exact_missing_datum"] == EXACT_MISSING_DATUM
        ),
        "vertical_one_jet_nonuniqueness_demonstrated": ambiguity[
            "distinct_children_from_missing_vertical_one_jet"
        ],
        "base_tangent_nonuniqueness_demonstrated": ambiguity[
            "distinct_children_from_missing_base_tangent"
        ],
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
    return {
        "artifact": "BHSM_GAUGE_CONNECTION_RESET_BUNDLE_LIFT_ADJUDICATION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "status": STATUS,
        "prior_blocker_refinement": {
            "prior": (
                "ACTION_OWNED_NONZERO_GAUGE_CONNECTION_TRACE_AE4_RESET_MAP_"
                "R_A[B;GAMMA0_A_EVENT]_TO_GAMMA0_A_CHILD"
            ),
            "refined_first_geometric_datum": EXACT_MISSING_DATUM,
            "reason": (
                "THE_AE2_ABSTRACT_BOUNDARY_LIFT_DOES_NOT_EXPOSE_THE_BASE_"
                "JACOBIAN_OR_VERTICAL_TRANSITION_DERIVATIVE_REQUIRED_TO_"
                "EVALUATE_THE_PULLBACK_OF_A_CONNECTION_ONE_FORM"
            ),
        },
        "ownership_levels": levels,
        "focused_source_lineage": lineage,
        "local_one_jet_nonuniqueness": ambiguity,
        "conditional_connection_geometry": conditional,
        "downstream_canonical_chain": downstream,
        "VALIDATED": [
            "V15_53_OWNS_THE_RETURNED_SM_BUNDLE_ISOMORPHISM_CLASS",
            "AE2_OWNS_AN_ABSTRACT_SMOOTH_SPIN_GAUGE_BOUNDARY_LIFT_U_R",
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
            "THE_AE2_POINTWISE_TRACE_UNITARY_SUPPLIES_dg_B_OR_DF_B",
            (
                "NABLA_PHI_U_R_EQUALS_ZERO_IN_A_PARAMETER_SPACE_RESPONSE_"
                "WITNESS_INSTANTIATES_THE_PHYSICAL_SPACETIME_GAUGE_"
                "CONNECTION_RESET"
            ),
            "BOUNDARY_INCIDENCE_OR_ORIENTATION_ALONE_DETERMINES_THE_PULLBACK_OF_A_ONE_FORM",
            "V15_57_CONSTANT_ZERO_BACKGROUND_RECONSTRUCTION_DEFINES_THE_NONZERO_RESET",
            "THE_CONDITIONAL_FINITE_WITNESS_IS_AN_ADMISSIBLE_BHSM_BACKGROUND",
        ],
        "OPEN": [EXACT_MISSING_DATUM],
        "EXACT_NEXT_OBJECT": EXACT_MISSING_DATUM,
        "exact_next_calculation": (
            "MATERIALIZE_IN_OVERLAPPING_EVENT_AND_CHILD_BOUNDARY_CHARTS_THE_"
            "ACTION_OWNED_PRINCIPAL_BUNDLE_LIFT_AS_F_B(x),_DF_B(x),_g_B(x),_"
            "AND_dg_B(x);_THEN_EVALUATE_F_B_STAR_A_CHILD_EQUALS_g_B_A_EVENT_"
            "g_B_DAGGER_MINUS_dg_B_g_B_DAGGER_AND_DIFFERENTIATE_IT"
        ),
        "empirical_inputs": [],
        "claims": claims,
        "source_sha256": hashes,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def main() -> Path:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(deterministic_json(build_payload()), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(main())
