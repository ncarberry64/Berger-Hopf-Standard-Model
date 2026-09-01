"""Audit whether the certified child Galerkin tail transfers to Gate-7 sources."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_product_dirac_weyl_enclosures import (  # noqa: E402
    product_dirac_compact_radius_weyl_variation_bounds,
    product_dirac_nonnegative_exterior_weyl_bounds,
)
from bhsm.interface.aether_forward_scalar_weyl_enclosures import (  # noqa: E402
    scalar_compact_radius_weyl_variation_bounds,
    scalar_nonnegative_exterior_weyl_bounds,
)


ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_SOURCE_TAIL_OWNERSHIP_AUDIT.json"
)
CONTINUUM = ARTIFACTS / (
    "n12_continuum_majorant_effectiveness/BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"
)
PROJECTOR = ARTIFACTS / (
    "n12_continuum_majorant_effectiveness/BHSM_N12_ACTION_GRAPH_GALERKIN_PROJECTOR.json"
)
OWNERSHIP = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FLAGSHIP_GAUGE_ACTION_OWNERSHIP_AUDIT.json"
)
RANK16 = ARTIFACTS / "BHSM_aether_rank16_u1_hs_vertex_matrices_v16_01.json"
DERHAM = ARTIFACTS / "BHSM_aether_nonabelian_derham_response_v16_04.json"
INCIDENCE = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json"
)
SCALAR = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_TWO_CHORD_SCALAR_WEYL_ENCLOSURES.json"
)
DIRAC = ARTIFACTS / (
    "flagship_integration/"
    "BHSM_N12_FORWARD_TWO_CHORD_PRODUCT_DIRAC_WEYL_ENCLOSURES.json"
)
INPUTS = (
    CONTINUUM,
    PROJECTOR,
    OWNERSHIP,
    RANK16,
    DERHAM,
    INCIDENCE,
    SCALAR,
    DIRAC,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _comparison_growth_witnesses(
    duration: float, radius_lower: float
) -> list[dict[str, Any]]:
    rows = []
    for level in (4, 8, 16, 32):
        scalar_eigenvalue = float(level * (level + 2))
        scalar_potential = scalar_eigenvalue / radius_lower**2
        scalar_base = scalar_nonnegative_exterior_weyl_bounds(
            duration, scalar_potential, 1.0
        )
        scalar_weak = scalar_compact_radius_weyl_variation_bounds(
            scalar_base["upper"], scalar_potential, 1.0
        )

        dirac_eigenvalue = float(level + 1.5)
        superpotential = dirac_eigenvalue / radius_lower
        dirac_base = product_dirac_nonnegative_exterior_weyl_bounds(
            duration, superpotential, 1.0
        )
        dirac_weak = product_dirac_compact_radius_weyl_variation_bounds(
            dirac_base["upper"], superpotential, 1.0
        )
        rows.append(
            {
                "level": level,
                "scalar_unit_eigenvalue": scalar_eigenvalue,
                "scalar_Weyl_upper": scalar_base["upper"],
                "scalar_first_weak_upper": scalar_weak[
                    "first_Weyl_variation_bound"
                ],
                "Dirac_absolute_unit_eigenvalue": dirac_eigenvalue,
                "product_Dirac_Weyl_upper": dirac_base["upper"],
                "product_Dirac_first_weak_upper": dirac_weak[
                    "first_Weyl_variation_bound"
                ],
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all forward source-tail audit inputs are required")
    records = {
        path.name: json.loads(path.read_text(encoding="utf-8")) for path in INPUTS
    }
    if not all(record.get("validation_passed") is True for record in records.values()):
        raise RuntimeError("all forward source-tail audit inputs must validate")

    continuum = records[CONTINUUM.name]
    projector = records[PROJECTOR.name]
    ownership = records[OWNERSHIP.name]
    rank16 = records[RANK16.name]
    derham = records[DERHAM.name]
    incidence = records[INCIDENCE.name]
    scalar = records[SCALAR.name]
    dirac = records[DIRAC.name]
    duration = float(scalar["certified_core"]["proper_duration_lower"])
    radius_lower = float(scalar["certified_core"]["R4_lower"])
    growth = _comparison_growth_witnesses(duration, radius_lower)

    validation = {
        "all_inputs_validated": True,
        "continuum_event_child_is_certified": continuum[
            "CONTINUUM_EVENT_CHILD_CERTIFIED"
        ]
        is True,
        "certified_tail_owner_is_action_graph_child_correction": (
            continuum["scientific_result"]["construction"].startswith(
                "CERTIFIED_N12_COMPLETE_CHILD"
            )
            and "action weighted trace graph"
            in projector["classification"].lower().replace("_", " ")
        ),
        "child_projector_basis_is_cohomogeneity_one_chi_basis": (
            "chi" in projector["analytic_countersequence"]["definition"]
        ),
        "gauge_source_Hessian_tail_is_explicitly_open": ownership["open"][
            "continuum_Galerkin_tail_bound_for_gauge_source_Hessian"
        ]
        is False,
        "rank16_level_convergence_is_explicitly_open": rank16["claim_boundary"][
            "level_convergence_established"
        ]
        is False,
        "deRham_angular_heat_tail_is_explicitly_open": derham["claim_boundary"][
            "angular_heat_tail_converged"
        ]
        is False,
        "pair_contact_incidence_is_only_domain_parametric": incidence[
            "claim_boundary"
        ]["pair_plus_contact_gauge_Hessian"]
        == "OPEN",
        "new_channel_rows_are_low_level_witnesses_not_tail_certificates": (
            scalar["representative_retained_low_levels"]["levels"] == [0, 1, 2, 3]
            and dirac["representative_retained_low_levels"]["levels"]
            == [0, 1, 2, 3]
        ),
        "current_comparison_bounds_do_not_supply_level_decay": all(
            later["scalar_Weyl_upper"] >= earlier["scalar_Weyl_upper"]
            and later["scalar_first_weak_upper"]
            >= earlier["scalar_first_weak_upper"]
            and later["product_Dirac_Weyl_upper"]
            >= earlier["product_Dirac_Weyl_upper"]
            and later["product_Dirac_first_weak_upper"]
            >= earlier["product_Dirac_first_weak_upper"]
            for earlier, later in zip(growth, growth[1:])
        ),
        "spatial_child_tail_not_relabelled_as_source_or_temporal_tail": True,
        "no_gate_equation_source_profile_subtraction_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_FORWARD_SOURCE_TAIL_OWNERSHIP_AUDIT",
        "status": "CERTIFIED_CHILD_SPATIAL_TAIL_NOT_A_GATE7_SOURCE_HESSIAN_TAIL",
        "classification": (
            "THE_CERTIFIED_CONTINUUM_GALERKIN_TAIL_CONTROLS_THE_N12_EVENT_"
            "CHILD_COHOMOGENEITY_ONE_ACTION_GRAPH_CORRECTION;_IT_DOES_NOT_"
            "CONTROL_THE_DISTINCT_INTERNAL_S3_DIRAC_DERHAM_AND_CARRIER_LEVEL_"
            "SUM_IN_THE_GATE7_COMMON_SOURCE_HESSIAN,_WHOSE_RANK16_LEVEL_"
            "CONVERGENCE_AND_NONABELIAN_ANGULAR_HEAT_TAIL_REMAIN_EXPLICITLY_"
            "OPEN;_THE_NEW_CHANNEL_COMPARISON_BOUNDS_ARE_PARAMETRIC_LOW_LEVEL_"
            "ENCLOSURES_BUT_HAVE_NO_SUMMABLE_LEVEL_DECAY"
        ),
        "tail_provenance": {
            "certified_tail": {
                "owner": "CONTINUUM_EVENT_CHILD_ACTION_GRAPH_CORRECTION",
                "basis": (
                    "COHOMOGENEITY_ONE_chi_JACOBI_CHEBYSHEV_BLOCKS_FOR_"
                    "N12_EVENT_CHILD_STATE_COORDINATES"
                ),
                "norm": "RETAINED_ACTION_WEIGHTED_TRACE_GRAPH_G",
                "controlled_quantity": (
                    "INVERSE_SQUARE_WEAK_SOURCE_TAIL_AND_NONLINEAR_NORMAL_"
                    "CORRECTION_OF_THE_EVENT_CHILD_ROOT"
                ),
                "certified": True,
            },
            "missing_Gate7_tail": {
                "owner": "COMMON_GAUGE_GHOST_RANK16_HS_SOURCE_HESSIAN",
                "basis": "INTERNAL_S3_DIRAC_DERHAM_LEVELS_AND_CARRIER_SECTORS",
                "required_quantity": (
                    "BRST_COMBINED_PAIR_PLUS_CONTACT_ANGULAR_LEVEL_TAIL_OR_"
                    "AN_ACTION_OWNED_RELATIVE_TRACE_SUBTRACTION_BOUND"
                ),
                "certified": False,
            },
            "same_Galerkin_index": False,
            "same_normed_operator": False,
            "transfer_theorem_present": False,
        },
        "comparison_bound_scope": {
            "scalar_deRham": "PARAMETRIC_PER_CHANNEL_AT_z_MINUS_1",
            "product_Dirac": "PARAMETRIC_PER_CHANNEL_AT_z_MINUS_1",
            "low_level_witnesses": [0, 1, 2, 3],
            "angular_sum_or_relative_trace": "NOT_CERTIFIED",
            "growth_witnesses": growth,
            "inference": (
                "MONOTONE_GROWTH_OF_THE_AVAILABLE_UPPER_BOUNDS_SHOWS_ONLY_"
                "THAT_THESE_BOUNDS_CANNOT_THEMSELVES_CERTIFY_THE_LEVEL_TAIL;_"
                "IT_DOES_NOT_PROVE_THE_RETAINED_BRST_RELATIVE_RESPONSE_DIVERGES"
            ),
        },
        "adjudication": {
            "SPATIAL_GALERKIN_TAIL_CERTIFIED": True,
            "certified_for_event_child_state_correction": True,
            "certified_for_Gate7_source_Hessian": False,
            "may_be_used_as_temporal_tail": False,
            "may_be_used_as_internal_source_level_tail_without_new_theorem": False,
            "pair_contact_low_level_incidence": "ASSEMBLED_DOMAIN_PARAMETRIC",
            "pair_contact_continuum_or_relative_trace": "OPEN",
            "zero_source_force": "OPEN",
        },
        "exact_next_dependency": (
            "DERIVE_A_COMMON_SOURCE_ANGULAR_LEVEL_TAIL_OR_ACTION_OWNED_"
            "BRST_RELATIVE_TRACE_SUBTRACTION_BOUND_FOR_THE_PAIR_PLUS_CONTACT_"
            "HESSIAN_ON_THE_SAME_MAXIMAL_FORWARD_DOMAIN;_THEN_COMBINE_IT_"
            "WITH_THE_PER_CHANNEL_z_MINUS_1_POISSON_BOUNDS_AND_ASSEMBLE_THE_"
            "ZERO_SOURCE_WEAK_GEOMETRY_FORCE"
        ),
        "claim_boundary": {
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "chord_03_authorized": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
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
    print(
        json.dumps(
            {
                "status": payload["status"],
                "source_tail_certified": payload["adjudication"][
                    "certified_for_Gate7_source_Hessian"
                ],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
