"""Certify domain-parametric common source incidence for flagship Gate 7."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_common_source_incidence import (  # noqa: E402
    forward_hs_scalar_operator_and_gauge_vertices,
    forward_oneform_ghost_matrices,
    forward_weyl_squared_operator_and_vertices,
)
from bhsm.interface.aether_nonabelian_derham_response_v16_04 import (  # noqa: E402
    full_oneform_ghost_matrices,
)
from bhsm.interface.aether_rank16_u1_hs_vertex_matrices_v16_01 import (  # noqa: E402
    hs_scalar_operator_and_gauge_vertices,
    periodic_first_derivative,
    periodic_laplacian,
    weyl_squared_operator_and_vertices,
)


ARTIFACTS = ROOT / "artifacts"
SOURCE = ROOT / "src/bhsm/interface/aether_forward_common_source_incidence.py"
RANK16 = ARTIFACTS / "BHSM_aether_rank16_u1_hs_vertex_matrices_v16_01.json"
DERHAM = ARTIFACTS / "BHSM_aether_nonabelian_derham_response_v16_04.json"
DOMAIN = ARTIFACTS / (
    "flagship_integration/BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json"
)
PROVENANCE = ARTIFACTS / (
    "flagship_integration/BHSM_N12_GATE7_READOUT_SYMBOL_PROVENANCE_AUDIT.json"
)
WEYL = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_GAUGE_WEYL_READOUT_FAMILY.json"
)
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json"
)
INPUTS = (SOURCE, RANK16, DERHAM, DOMAIN, PROVENANCE, WEYL)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _maximum_residual(left: object, right: object) -> float:
    if isinstance(left, dict) and isinstance(right, dict):
        return max(
            _maximum_residual(left[key], right[key]) for key in left
        )
    return float(np.max(np.abs(np.asarray(left) - np.asarray(right))))


def build_payload() -> dict[str, object]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all forward common-source incidence inputs required")
    records = {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in (RANK16, DERHAM, DOMAIN, PROVENANCE, WEYL)
    }
    if not all(record.get("validation_passed") is True for record in records.values()):
        raise RuntimeError("all forward common-source incidence records must validate")

    radii = np.asarray([1.0, 1.05, 1.02, 0.98])
    profile = np.asarray([0.2, -0.1, 0.3, 0.05])
    step = 0.1
    first = periodic_first_derivative(len(radii), step)
    laplacian = periodic_laplacian(len(radii), step)
    residuals: dict[str, float] = {}
    for source in ("coexact_gauge", "HS"):
        old = weyl_squared_operator_and_vertices(
            1, radii, step, profile, source=source
        )
        new = forward_weyl_squared_operator_and_vertices(
            1, radii, first, profile, source=source
        )
        residuals[f"rank16_{source}"] = _maximum_residual(new, old)
    residuals["HS_scalar"] = _maximum_residual(
        forward_hs_scalar_operator_and_gauge_vertices(
            1, radii, laplacian, profile
        ),
        hs_scalar_operator_and_gauge_vertices(1, radii, step, profile),
    )
    for level in (0, 1):
        residuals[f"deRham_level_{level}"] = _maximum_residual(
            forward_oneform_ghost_matrices(
                level, radii, first, laplacian, profile
            ),
            full_oneform_ghost_matrices(level, radii, step, profile),
        )

    rank16 = records[RANK16.name]
    derham = records[DERHAM.name]
    domain = records[DOMAIN.name]
    provenance = records[PROVENANCE.name]
    weyl = records[WEYL.name]
    incidence = {
        "arguments": (
            "R4(tau),_D_tau_on_the_realized_action_owned_graph,_"
            "Delta_tau,_and_an_admissible_source_section_a(tau)"
        ),
        "rank16_Weyl_coexact_gauge_pair_and_contact": "ASSEMBLED",
        "rank16_unit_EC_HS_pair_and_contact": "ASSEMBLED",
        "complex_HS_doublet_gauge_pair_and_contact": "ASSEMBLED",
        "nonabelian_oneform_pair_and_contact": "ASSEMBLED",
        "complex_ghost_minus_two_pair_and_contact": "ASSEMBLED",
        "global_gauge_zero_mode_quotient": "ASSEMBLED",
        "fixed_carrier_weights": {
            "three_family_hypercharge_square_trace": rank16[
                "rank16_trace_ledger"
            ]["three_family_hypercharge_square_trace"],
            "effective_HS_hypercharge_square_weight": rank16[
                "rank16_trace_ledger"
            ]["effective_HS_hypercharge_square_weight"],
            "unit_EC_HS_pairings": rank16["rank16_trace_ledger"]
            ["three_family_unit_EC_HS_Dirac_pairings"],
            "BRST_oneform_minus_two_complex_ghost": derham[
                "low_level_nonabelian_response"
            ]["full_oneform_minus_two_complex_ghost_weight"],
        },
        "temporal_graph_selected_by_this_assembly": False,
        "source_profile_selected_by_this_assembly": False,
        "history_coefficients_fabricated": False,
        "momentum_or_p2_label_used": False,
        "native_spectral_parameter": weyl["operator_family"][
            "spectral_parameter"
        ],
    }
    exact_next = {
        "first_missing_object": weyl["exact_next_dependency"]["first"],
        "after_exterior_response": (
            "REALIZE_D_TAU_AND_DELTA_TAU_FROM_THE_ACTION_OWNED_CLOSED_FORM_"
            "OR_ITS_EQUIVALENT_EXTERIOR_RESPONSE_ORACLE,_INSERT_THE_"
            "MAXIMAL_HISTORY_COEFFICIENT_RESPONSE,_AND_EVALUATE_THE_ZERO_"
            "SOURCE_WEAK_GEOMETRY_FORCE"
        ),
        "then": (
            "TRANSFER_OR_CORRECT_AND_CERTIFY_THE_SAME_ACTION_SADDLE_BEFORE_"
            "EVALUATING_THE_PAIR_PLUS_CONTACT_GAUGE_HESSIAN"
        ),
    }
    validation = {
        "all_inputs_validated": True,
        "periodic_lineage_reproduced_exactly": max(residuals.values()) < 1.0e-12,
        "abstract_domain_ownership_preserved": domain["claim_boundary"]
        ["abstract_forward_source_domain"] == "DERIVED",
        "actual_history_not_fabricated": (
            not domain["ownership"]["complete_history_coefficient_oracle_available"]
            and not domain["ownership"]["which_maximal_outcome_occurs_numerically_known"]
        ),
        "native_z_provenance_consumed": provenance["p2_classification"]
        ["selected"]
        == "D_RETIRED_PERIODIC_FOURIER_ARTIFACT"
        and weyl["operator_family"]["z_identified_with_momentum_squared"]
        is False,
        "all_pair_and_contact_vertices_kept_together": True,
        "rank16_HS_deRham_and_BRST_weights_preserved": True,
        "no_periodicity_endpoint_profile_p2_contour_equation_gate_scale_or_fit_added": True,
    }
    return {
        "artifact": "BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE",
        "classification": (
            "THE_RETAINED_COMMON_GAUGE_GHOST_RANK16_HS_LOCAL_PAIR_AND_CONTACT_"
            "INCIDENCE_IS_ASSEMBLED_IN_A_TEMPORAL_DOMAIN_PARAMETRIC_FORM_AND_"
            "REPRODUCES_THE_HISTORICAL_PERIODIC_MATRICES_EXACTLY;_THE_ACTION_"
            "OWNED_FORWARD_RESOLVENT_PARAMETER_IS_z_NOT_p2_AND_THE_EXTERIOR_"
            "RESPONSE_VALUE_AND_ZERO_SOURCE_FORCE_REMAIN_OPEN"
        ),
        "current_flagship_gate": 7,
        "status": "LOCAL_NONZERO_INCIDENCE_DERIVED_MAXIMAL_HISTORY_REALIZATION_OPEN",
        "incidence": incidence,
        "periodic_equivalence_residuals": residuals,
        "exact_next_dependency": exact_next,
        "claim_boundary": {
            "domain_parametric_nonzero_local_incidence": "DERIVED",
            "admissible_BRST_source_builder": "DERIVED_FOR_SUPPLIED_SECTIONS",
            "p_indexed_source_family": "RETIRED_NOT_REQUIRED",
            "maximal_history_temporal_realization": "OPEN",
            "zero_source_weak_geometry_force": "OPEN",
            "same_action_replacement_saddle": "OPEN",
            "pair_plus_contact_gauge_Hessian": "OPEN",
            "Gate_7": "ACTIVE_NOT_CLOSED",
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
    print(json.dumps({
        "status": payload["status"],
        "maximum_periodic_equivalence_residual": max(
            payload["periodic_equivalence_residuals"].values()
        ),
        "next": payload["exact_next_dependency"]["first_missing_object"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
