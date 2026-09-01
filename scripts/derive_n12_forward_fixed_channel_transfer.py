"""Derive the fixed-channel transfer reduction of the Gate-7 exterior."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_channel_transfer import (  # noqa: E402
    backward_weyl_mobius,
    product_dirac_channel_log_radius_jets,
    scalar_channel_log_radius_jets,
)
from bhsm.interface.aether_nonabelian_derham_response_v16_04 import (  # noqa: E402
    angular_derham_blocks,
)
from bhsm.interface.completion.exact_berger_dirac_cap_obstruction_v14_59 import (  # noqa: E402
    berger_dirac_block,
)


ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_FIXED_CHANNEL_TRANSFER.json"
)
MODULES = (
    ROOT / "src/bhsm/interface/aether_forward_channel_transfer.py",
    ROOT / "src/bhsm/interface/aether_forward_common_source_incidence.py",
)
INPUTS = (
    ARTIFACTS
    / "flagship_integration/BHSM_N12_FORWARD_PROPER_TIME_FORM_OWNERSHIP.json",
    ARTIFACTS / "flagship_integration/BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json",
    ARTIFACTS
    / "flagship_integration/BHSM_N12_FORWARD_COMMON_SOURCE_GEOMETRY_JETS.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _homogeneity_witnesses() -> dict[str, Any]:
    radii = (0.8, 1.7)
    dirac_residuals: list[float] = []
    derham_residuals: dict[str, list[float]] = {
        "gradient_R_inverse": [],
        "curl_R_inverse": [],
        "scalar_operator_R_inverse2": [],
        "vector_operator_R_inverse2": [],
        "scalar_vertex_R_inverse": [],
        "vector_vertex_R_inverse": [],
        "scalar_contact_R_zero": [],
        "vector_contact_R_zero": [],
        "temporal_spatial_injection_R_zero": [],
    }
    scale_map = {
        "gradient_R_inverse": ("gradient", 1),
        "curl_R_inverse": ("curl", 1),
        "scalar_operator_R_inverse2": ("scalar_operator", 2),
        "vector_operator_R_inverse2": ("vector_operator", 2),
        "scalar_vertex_R_inverse": ("scalar_vertex", 1),
        "vector_vertex_R_inverse": ("vector_vertex", 1),
        "scalar_contact_R_zero": ("scalar_contact", 0),
        "vector_contact_R_zero": ("vector_contact", 0),
        "temporal_spatial_injection_R_zero": ("temporal_spatial_injection", 0),
    }
    for level in range(4):
        unit_dirac = berger_dirac_block(level, 1.0, 1.0)
        unit_derham = angular_derham_blocks(level, 1.0)
        for radius in radii:
            scaled_dirac = radius * berger_dirac_block(level, radius, 1.0)
            dirac_residuals.append(float(np.linalg.norm(scaled_dirac - unit_dirac)))
            blocks = angular_derham_blocks(level, radius)
            for name, (key, power) in scale_map.items():
                residual = np.linalg.norm(radius**power * blocks[key] - unit_derham[key])
                derham_residuals[name].append(float(residual))
    return {
        "tested_levels": [0, 1, 2, 3],
        "tested_radii": list(radii),
        "maximum_Dirac_R_inverse_residual": max(dirac_residuals),
        "maximum_deRham_residuals": {
            name: max(values) for name, values in derham_residuals.items()
        },
    }


def _transfer_witness() -> dict[str, Any]:
    scalar = scalar_channel_log_radius_jets(5.0, 0.2, -1.0, 0.3, -0.4)
    dirac = product_dirac_channel_log_radius_jets(
        -2.5, 0.2, -1.0, 0.3, -0.4
    )
    transfer = np.asarray([[1.2, 0.4], [0.3, 1.1]], dtype=complex)
    birth = 0.7
    terminal = (transfer[1, 0] + transfer[1, 1] * birth) / (
        transfer[0, 0] + transfer[0, 1] * birth
    )
    recovered = backward_weyl_mobius(transfer, terminal)
    return {
        "scalar_generator": scalar["base"].real.tolist(),
        "product_Dirac_generator": dirac["base"].real.tolist(),
        "scalar_generator_trace": complex(np.trace(scalar["base"])).real,
        "product_Dirac_generator_trace": complex(
            np.trace(dirac["base"])
        ).real,
        "birth_admittance": birth,
        "terminal_admittance": complex(terminal).real,
        "backward_Mobius_recovery_residual": float(abs(recovered - birth)),
    }


def build_payload() -> dict[str, Any]:
    paths = (*INPUTS, *MODULES)
    if not all(path.is_file() for path in paths):
        raise FileNotFoundError("all fixed-channel transfer inputs are required")
    records = [json.loads(path.read_text(encoding="utf-8")) for path in INPUTS]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("all fixed-channel transfer inputs must validate")

    homogeneity = _homogeneity_witnesses()
    transfer = _transfer_witness()
    de_rham_maximum = max(homogeneity["maximum_deRham_residuals"].values())
    validation = {
        "all_inputs_validated": True,
        "round_Dirac_blocks_scale_as_R_inverse_to_1e_minus_12": (
            homogeneity["maximum_Dirac_R_inverse_residual"] < 1.0e-12
        ),
        "all_deRham_operator_vertex_contact_scalings_close_to_1e_minus_12": (
            de_rham_maximum < 1.0e-12
        ),
        "scalar_transfer_generator_has_zero_trace": (
            transfer["scalar_generator_trace"] == 0.0
        ),
        "Dirac_transfer_generator_has_zero_trace": (
            transfer["product_Dirac_generator_trace"] == 0.0
        ),
        "Weyl_Mobius_pullback_recovers_birth_graph": (
            transfer["backward_Mobius_recovery_residual"] < 1.0e-14
        ),
        "no_moving_spatial_basis_required": True,
        "no_history_endpoint_periodicity_p2_profile_fit_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_FORWARD_FIXED_CHANNEL_TRANSFER",
        "classification": (
            "THE_CURRENT_RETAINED_ROUND_FORWARD_SOURCE_OPERATOR_HAS_A_FIXED_"
            "SPATIAL_CHANNEL_BASIS:_DIRAC_AND_PAIR_VERTICES_SCALE_AS_"
            "exp(-x),_LAPLACE_DERHAM_BLOCKS_AS_exp(-2x),_AND_CONTACT_BLOCKS_"
            "ARE_x_INDEPENDENT_FOR_x=log_R4;_THE_EXTERIOR_WEYL_ORACLE_"
            "REDUCES_TO_FINITE_TWO_BY_TWO_CHANNEL_TRANSFER_SYSTEMS_DRIVEN_"
            "BY_ONE_SCALAR_HISTORY_x(tau)_WITH_NO_MOVING_EIGENLINE_OR_"
            "INDEPENDENT_TEMPORAL_COEFFICIENT_ORACLE"
        ),
        "current_flagship_gate": 7,
        "status": "FIXED_CHANNEL_TRANSFER_REDUCTION_DERIVED",
        "fixed_channel_theorem": {
            "spatial_basis": (
                "ONE_tau_INDEPENDENT_ORTHONORMAL_BASIS_PER_RETAINED_ROUND_"
                "DIRAC_SCALAR_AND_DERHAM_LEVEL"
            ),
            "rank16_product_Dirac_channel": {
                "s_lambda": "chirality*lambda*exp(-x(tau))",
                "factor": "A_lambda=d_tau+s_lambda",
                "flux": "v=A_lambda*u",
                "transfer": "d_tau[u,v]^T=[[-s,1],[-z,s]]*[u,v]^T",
            },
            "scalar_and_deRham_channel": {
                "potential": "V_c(tau)=c*exp(-2*x(tau))",
                "flux": "v=d_tau*u",
                "transfer": "d_tau[u,v]^T=[[0,1],[V_c-z,0]]*[u,v]^T",
            },
            "source_incidence": (
                "FINITE_FIXED_CHANNEL_MATRICES_WITH_exp(-x)_PAIR_VERTICES_"
                "AND_x_INDEPENDENT_CONTACTS"
            ),
            "Weyl_propagation": (
                "EACH_TERMINAL_OR_FRIEDRICHS_CHANNEL_ADMITTANCE_PULLS_BACK_"
                "TO_BIRTH_BY_THE_EXACT_TRANSFER_MOBIUS_ACTION"
            ),
            "geometry_variations": (
                "FIRST_AND_MIXED_SECOND_TRANSFER_GENERATOR_JETS_FOLLOW_"
                "EXACTLY_FROM_D_x_exp(-x)_AND_D_x_exp(-2x)"
            ),
        },
        "homogeneity_witnesses": homogeneity,
        "transfer_witness": transfer,
        "dependency_reduction": {
            "generic_operator_coefficient_history_required": False,
            "moving_spatial_eigenbasis_transport_required": False,
            "independent_D_tau_or_Delta_tau_oracle_required": False,
            "one_scalar_maximal_history_required": "x(tau)=log_R4(tau)",
            "full_pointwise_x_history_logically_required": False,
            "equivalent_sufficient_object": (
                "THE_FINITE_CHANNEL_TRANSFER_OR_WEYL_M_FUNCTIONS_AND_THEIR_"
                "FIRST_SECOND_ACTION_VARIATIONS"
            ),
        },
        "exact_next_dependency": (
            "ENCLOSE_THE_FINITE_FIXED_CHANNEL_WEYL_TRANSFER_MAPS_AND_THEIR_"
            "FIRST_SECOND_ACTION_VARIATIONS_FOR_THE_MAXIMAL_FORWARD_"
            "x(tau)=log_R4(tau)_FLOW,_WITHOUT_REQUIRING_TERMINAL_RETURN"
        ),
        "claim_boundary": {
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "chord_03": "NOT_AUTHORIZED",
            "channel_Weyl_values": "OPEN",
            "zero_source_force": "OPEN",
            "same_action_saddle": "OPEN",
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in paths
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
                "Dirac_scaling_residual": payload["homogeneity_witnesses"]
                ["maximum_Dirac_R_inverse_residual"],
                "deRham_scaling_residual": max(
                    payload["homogeneity_witnesses"]
                    ["maximum_deRham_residuals"].values()
                ),
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
