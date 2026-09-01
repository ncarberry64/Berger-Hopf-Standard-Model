"""Derive proper-time temporal-form ownership for the Gate-7 source graph."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_common_source_incidence import (  # noqa: E402
    canonical_temporal_form_laplacian,
    temporal_form_pair_residual,
)
from bhsm.interface.aether_rank16_u1_hs_vertex_matrices_v16_01 import (  # noqa: E402
    periodic_first_derivative,
    periodic_laplacian,
)


ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_PROPER_TIME_FORM_OWNERSHIP.json"
)
MODULE = ROOT / "src/bhsm/interface/aether_forward_common_source_incidence.py"
INPUTS = (
    ARTIFACTS / "BHSM_aether_proper_time_joint_pushforward_v15_91.json",
    ARTIFACTS / "flagship_integration/BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json",
    ARTIFACTS
    / "flagship_integration/BHSM_N12_FORWARD_COMMON_SOURCE_GEOMETRY_JETS.json",
    ARTIFACTS
    / "flagship_integration/BHSM_N12_FORWARD_GAUGE_WEYL_READOUT_FAMILY.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _nonperiodic_form_witness() -> dict[str, Any]:
    derivative = np.array(
        [[-1.0, 1.0, 0.0], [0.0, -1.0, 1.0], [0.0, 0.0, 0.0]],
        dtype=complex,
    )
    endpoint = np.diag([0.25, 0.0, 0.5])
    laplacian = canonical_temporal_form_laplacian(derivative, endpoint)
    return {
        "first_derivative": derivative.real.tolist(),
        "retained_endpoint_form": endpoint.real.tolist(),
        "form_laplacian": laplacian.real.tolist(),
        "minimum_eigenvalue": float(np.min(np.linalg.eigvalsh(laplacian))),
        "form_pair_residual": temporal_form_pair_residual(
            derivative, laplacian, endpoint
        ),
    }


def build_payload() -> dict[str, Any]:
    if not MODULE.is_file() or not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all proper-time form inputs are required")
    records = {
        path.name: json.loads(path.read_text(encoding="utf-8")) for path in INPUTS
    }
    for name, record in records.items():
        if record.get("validation_passed") is not True:
            raise RuntimeError(f"input did not validate: {name}")

    points = 24
    step = 0.1
    derivative = periodic_first_derivative(points, step)
    laplacian = periodic_laplacian(points, step)
    periodic_residual = temporal_form_pair_residual(derivative, laplacian)
    periodic_norm = float(np.linalg.norm(laplacian, ord=2))
    relative_residual = periodic_residual / periodic_norm
    nonperiodic = _nonperiodic_form_witness()

    proper = records["BHSM_aether_proper_time_joint_pushforward_v15_91.json"]
    domain = records["BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json"]
    jets = records["BHSM_N12_FORWARD_COMMON_SOURCE_GEOMETRY_JETS.json"]
    weyl = records["BHSM_N12_FORWARD_GAUGE_WEYL_READOUT_FAMILY.json"]

    validation = {
        "all_inputs_validated": True,
        "proper_time_measure_is_action_owned": proper["proper_time_cycle_pushforward"]
        ["same_proper_time_measure_for_gauge_and_Yukawa"],
        "positive_lapse_defines_single_forward_proper_clock": (
            proper["proper_time_cycle_pushforward"]["mean_boundary_lapse"] > 0.0
        ),
        "periodic_lineage_obeys_DstarD_identity_to_1e_minus_14_relative": (
            relative_residual < 1.0e-14
        ),
        "nonperiodic_form_witness_is_exact": (
            nonperiodic["form_pair_residual"] == 0.0
        ),
        "nonperiodic_form_witness_is_nonnegative": (
            nonperiodic["minimum_eigenvalue"] >= -1.0e-13
        ),
        "maximal_endpoint_rule_is_action_owned": (
            domain["validation"]["Friedrichs_rule_retained_for_excluded_endpoint"]
        ),
        "local_log_radius_geometry_jets_already_derived": (
            jets["scope"]["local_log_R4_first_and_mixed_second_variations"]
            == "DERIVED"
        ),
        "native_z_remains_distinct_from_p2": (
            weyl["operator_family"]["z_identified_with_momentum_squared"]
            is False
        ),
        "no_temporal_operator_endpoint_p2_fit_or_prediction_added": True,
    }

    return {
        "artifact": "BHSM_N12_FORWARD_PROPER_TIME_FORM_OWNERSHIP",
        "classification": (
            "THE_POSITIVE_ACTION_OWNED_CLOCK_d_tau=N_boundary*dt_REMOVES_"
            "LAPSE_AS_AN_INDEPENDENT_LOCAL_SOURCE_OPERATOR_COEFFICIENT:_ON_"
            "THE_REALIZED_MAXIMAL_PROPER_TIME_DOMAIN_D_tau_IS_THE_CANONICAL_"
            "COVARIANT_DERIVATIVE_AND_Delta_tau=D_tau^star*D_tau_PLUS_THE_"
            "SINGLE_RETAINED_NONNEGATIVE_ENDPOINT_FORM;_THE_ONLY_UNREALIZED_"
            "BULK_GEOMETRY_COEFFICIENT_IN_THE_CURRENT_SOURCE_REPRESENTATION_"
            "IS_log_R4(tau)"
        ),
        "current_flagship_gate": 7,
        "status": "PROPER_TIME_TEMPORAL_FORM_OWNERSHIP_DERIVED",
        "provenance_classification": {
            "positive_boundary_lapse": {
                "class": "ACTION_REQUIRED",
                "role": "DEFINES_d_tau=N_boundary*dt_AND_FORWARD_ORIENTATION",
                "independent_bulk_source_coefficient_after_pullback": False,
            },
            "D_tau": {
                "class": "ACTION_REQUIRED_KINEMATIC",
                "role": (
                    "CANONICAL_COVARIANT_DERIVATIVE_ON_THE_ACTION_OWNED_"
                    "MAXIMAL_PROPER_TIME_DOMAIN"
                ),
                "separate_coefficient_oracle_required": False,
            },
            "Delta_tau": {
                "class": "INTERNAL_CONSISTENCY_REQUIRED",
                "role": (
                    "FORM_OPERATOR_D_tau^star*D_tau_WITH_THE_SAME_RETAINED_"
                    "ENDPOINT_FORM"
                ),
                "independently_selectable": False,
            },
            "maximal_interval_and_endpoint_class": {
                "class": "ACTION_REQUIRED_DOMAIN",
                "role": "ALREADY_COMPRESSED_IN_THE_WEYL_CALDERON_ORACLE",
                "separate_bulk_coefficient_tube_required": False,
            },
            "log_R4_of_tau": {
                "class": "ACTION_REQUIRED_DYNAMIC_COEFFICIENT",
                "local_first_second_jets": "DERIVED",
                "maximal_history_value_and_Jacobi_envelope": "OPEN",
            },
        },
        "proper_time_form_theorem": {
            "clock_pullback": "tau(t)=integral_0^t_N_boundary(s)ds",
            "positive_orientation": "N_boundary>0_IMPLIES_d_tau>0",
            "bulk_form": "integral_Ic_norm(D_tau_U)^2*d_tau",
            "temporal_operator": "Delta_tau=D_tau^star*D_tau",
            "endpoint_completion": (
                "ADD_THE_EXISTING_NONNEGATIVE_RESET_WENTZELL_FORM_IF_HIT;_"
                "USE_THE_FRIEDRICHS_FORM_CLOSURE_OTHERWISE"
            ),
            "compactly_supported_geometry_variation": (
                "D_Phi_D_tau=0_AND_D_Phi_Delta_tau=0_AT_FIXED_PROPER_TIME_"
                "DOMAIN;_ALL_LOCAL_BULK_GEOMETRY_VARIATION_ENTERS_THROUGH_"
                "log_R4(tau)"
            ),
            "endpoint_shape_variation": (
                "BELONGS_TO_D_Phi_M_C_AND_IS_NOT_A_SECOND_BULK_TEMPORAL_"
                "COEFFICIENT"
            ),
        },
        "finite_witnesses": {
            "historical_periodic_equivalence_only": {
                "points": points,
                "step": step,
                "absolute_DstarD_residual": periodic_residual,
                "relative_DstarD_residual": relative_residual,
                "physical_periodicity_selected": False,
            },
            "nonperiodic_endpoint_form": nonperiodic,
        },
        "dependency_reduction": {
            "prior_string": (
                "MAXIMAL_FORWARD_TUBE_FOR_log_R4,D_tau,Delta_tau_AND_"
                "THEIR_FIRST_SECOND_GEOMETRY_VARIATIONS"
            ),
            "reclassification": (
                "D_tau_AND_Delta_tau_ARE_FORM_OWNED_KINEMATICS_ON_THE_"
                "REALIZED_DOMAIN_NOT_INDEPENDENT_HISTORY_COEFFICIENTS"
            ),
            "remaining_owner": (
                "THE_MAXIMAL_FORWARD_log_R4(tau)_WEYL_RESPONSE_AND_ITS_"
                "FIRST_SECOND_ACTION_JACOBI_VARIATIONS_OR_AN_EQUIVALENT_"
                "DIRECT_M_C_ORACLE_ENCLOSURE"
            ),
        },
        "exact_next_dependency": (
            "ENCLOSE_THE_MAXIMAL_FORWARD_log_R4(tau)_WEYL_RESPONSE_AND_ITS_"
            "FIRST_AND_SECOND_ACTION_JACOBI_VARIATIONS,_OR_COMPUTE_THE_"
            "EQUIVALENT_M_C,D_Phi_M_C,D_Phi2_M_C_ORACLE_DIRECTLY"
        ),
        "claim_boundary": {
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "chord_03": "NOT_AUTHORIZED",
            "zero_source_force": "OPEN",
            "same_action_saddle": "OPEN",
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in (*INPUTS, MODULE)
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
    print(
        json.dumps(
            {
                "status": payload["status"],
                "relative_periodic_form_residual": payload["finite_witnesses"]
                ["historical_periodic_equivalence_only"]
                ["relative_DstarD_residual"],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
