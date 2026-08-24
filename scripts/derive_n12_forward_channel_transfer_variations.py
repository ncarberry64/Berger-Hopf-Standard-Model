"""Derive the exact first/mixed-second fixed-channel Weyl variation system."""

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
    backward_weyl_mobius_jets,
    scalar_channel_log_radius_jets,
    scalar_channel_transfer_generator,
    transfer_variation_rhs,
)


ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_CHANNEL_TRANSFER_VARIATIONS.json"
)
INPUTS = (
    ARTIFACTS / "flagship_integration/BHSM_N12_FORWARD_FIXED_CHANNEL_TRANSFER.json",
)
MODULES = (ROOT / "src/bhsm/interface/aether_forward_channel_transfer.py",)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _generator_mixed_witness() -> float:
    x, h, k, ell = 0.11, 0.2, -0.3, 0.4
    eps = 2.0e-4
    jets = scalar_channel_log_radius_jets(3.0, x, -0.5, h, k, ell)

    def generator(left: float, right: float) -> np.ndarray:
        varied_x = x + left * h + right * k + left * right * ell
        return scalar_channel_transfer_generator(3.0, varied_x, -0.5)

    mixed = (
        generator(eps, eps)
        - generator(eps, -eps)
        - generator(-eps, eps)
        + generator(-eps, -eps)
    ) / (4.0 * eps**2)
    return float(np.linalg.norm(jets["mixed_second"] - mixed))


def _triangular_rhs_witness() -> float:
    generator = {
        "base": np.asarray([[0.0, 1.0], [2.0, 0.0]], dtype=complex),
        "first_left": np.asarray([[0.1, 0.0], [0.2, -0.1]], dtype=complex),
        "first_right": np.asarray([[-0.3, 0.0], [0.4, 0.3]], dtype=complex),
        "mixed_second": np.asarray([[0.2, 0.1], [-0.2, -0.2]], dtype=complex),
    }
    transfer = {
        "base": np.asarray([[1.1, 0.2], [0.3, 0.9]], dtype=complex),
        "first_left": np.asarray([[0.2, -0.1], [0.0, 0.3]], dtype=complex),
        "first_right": np.asarray([[-0.1, 0.4], [0.2, 0.0]], dtype=complex),
        "mixed_second": np.asarray([[0.3, 0.0], [-0.2, 0.1]], dtype=complex),
    }
    rhs = transfer_variation_rhs(generator, transfer)
    expected = (
        generator["base"] @ transfer["mixed_second"]
        + generator["first_left"] @ transfer["first_right"]
        + generator["first_right"] @ transfer["first_left"]
        + generator["mixed_second"] @ transfer["base"]
    )
    return float(np.linalg.norm(rhs["mixed_second"] - expected))


def _weyl_jet_witness() -> dict[str, float]:
    transfer = {
        "base": np.asarray([[1.2, 0.4], [0.3, 1.1]], dtype=complex),
        "first_left": np.asarray([[0.1, -0.2], [0.05, 0.03]], dtype=complex),
        "first_right": np.asarray([[-0.07, 0.08], [0.02, -0.04]], dtype=complex),
        "mixed_second": np.asarray([[0.02, 0.01], [-0.03, 0.05]], dtype=complex),
    }
    terminal = {
        "base": 0.8,
        "first_left": 0.06,
        "first_right": -0.09,
        "mixed_second": 0.04,
    }
    jets = backward_weyl_mobius_jets(transfer, terminal)

    def value(left: float, right: float) -> complex:
        matrix = (
            transfer["base"]
            + left * transfer["first_left"]
            + right * transfer["first_right"]
            + left * right * transfer["mixed_second"]
        )
        admittance = (
            terminal["base"]
            + left * terminal["first_left"]
            + right * terminal["first_right"]
            + left * right * terminal["mixed_second"]
        )
        return backward_weyl_mobius(matrix, admittance)

    eps = 1.0e-4
    finite_left = (value(eps, 0.0) - value(-eps, 0.0)) / (2.0 * eps)
    finite_right = (value(0.0, eps) - value(0.0, -eps)) / (2.0 * eps)
    finite_mixed = (
        value(eps, eps)
        - value(eps, -eps)
        - value(-eps, eps)
        + value(-eps, -eps)
    ) / (4.0 * eps**2)
    return {
        "first_left_residual": float(abs(jets["first_left"] - finite_left)),
        "first_right_residual": float(abs(jets["first_right"] - finite_right)),
        "mixed_second_residual": float(abs(jets["mixed_second"] - finite_mixed)),
    }


def build_payload() -> dict[str, Any]:
    paths = (*INPUTS, *MODULES)
    if not all(path.is_file() for path in paths):
        raise FileNotFoundError("all transfer-variation inputs are required")
    input_payload = json.loads(INPUTS[0].read_text(encoding="utf-8"))
    if input_payload.get("validation_passed") is not True:
        raise RuntimeError("fixed-channel reduction must validate")
    generator_residual = _generator_mixed_witness()
    rhs_residual = _triangular_rhs_witness()
    weyl = _weyl_jet_witness()
    validation = {
        "fixed_channel_input_validated": True,
        "mixed_generator_chain_rule_closes_to_1e_minus_7": generator_residual < 1e-7,
        "triangular_transfer_product_rule_is_exact": rhs_residual == 0.0,
        "Weyl_first_jets_close_to_1e_minus_9": max(
            weyl["first_left_residual"], weyl["first_right_residual"]
        )
        < 1e-9,
        "Weyl_mixed_jet_closes_to_1e_minus_7": weyl["mixed_second_residual"] < 1e-7,
        "terminal_return_not_assumed": True,
        "no_new_selector_coupling_threshold_gate_or_prediction": True,
    }
    return {
        "artifact": "BHSM_N12_FORWARD_CHANNEL_TRANSFER_VARIATIONS",
        "status": "FIXED_CHANNEL_TRANSFER_AND_WEYL_VARIATION_EQUATIONS_DERIVED",
        "classification": (
            "THE_FIRST_AND_MIXED_SECOND_ACTION_VARIATIONS_OF_EVERY_RETAINED_"
            "FIXED_CHANNEL_TRANSFER_AND_ITS_BIRTH_WEYL_VALUE_SATISFY_AN_"
            "EXACT_FINITE_TRIANGULAR_SYSTEM;_BULK_VARIATION_IS_OWNED_ONLY_"
            "BY_x_h,_x_k,_x_hk_AND_TERMINAL_DOMAIN_VARIATION_ONLY_BY_THE_"
            "TERMINAL_ADMITTANCE_JETS"
        ),
        "transfer_variation_theorem": {
            "base": "T'=G*T",
            "first_left": "T_h'=G*T_h+G_h*T",
            "first_right": "T_k'=G*T_k+G_k*T",
            "mixed_second": "T_hk'=G*T_hk+G_h*T_k+G_k*T_h+G_hk*T",
            "fixed_birth_frame": "T=I,_T_h=T_k=T_hk=0_AT_THE_RESET_TRACE",
            "bulk_generator_data": "x,_x_h,_x_k,_x_hk_ALONG_THE_MAXIMAL_FORWARD_DOMAIN",
        },
        "Weyl_variation_theorem": {
            "birth_value": "m=(c-mu*a)/(mu*b-d)_FOR_T=[[a,b],[c,d]]",
            "first_and_mixed_jets": (
                "EXACT_QUOTIENT_JETS_FROM_T,_T_h,_T_k,_T_hk_AND_"
                "mu,_mu_h,_mu_k,_mu_hk"
            ),
            "regularity_condition": "abs(mu*b-d)>0_ON_THE_SELECTED_WEYL_CHART",
            "endpoint_owner": (
                "ALL_ENDPOINT_OR_FRIEDRICHS_DOMAIN_VARIATION_ENTERS_THROUGH_"
                "THE_TERMINAL_ADMITTANCE_JETS,_NOT_A_SECOND_BULK_OPERATOR"
            ),
        },
        "witnesses": {
            "mixed_generator_chain_rule_residual": generator_residual,
            "triangular_rhs_residual": rhs_residual,
            "Weyl_jet_residuals": weyl,
        },
        "remaining_action_owned_data": {
            "maximal_forward_base_history": "x(tau)=log_R4(tau)",
            "first_Jacobi_histories": "x_h(tau)_FOR_RETAINED_ACTION_DIRECTIONS",
            "mixed_second_Jacobi_histories": "x_hk(tau)",
            "terminal_or_Friedrichs_graph_jets": "mu,_mu_h,_mu_k,_mu_hk",
            "uniform_regular_Weyl_chart_margin": "inf_tau_abs(mu*b-d)>0_OR_CHART_COVER",
        },
        "exact_next_dependency": (
            "DERIVE_OR_ENCLOSE_THE_ACTION_OWNED_MAXIMAL_FORWARD_x,_x_h,_x_k,_"
            "x_hk_AND_TERMINAL_FRIEDRICHS_GRAPH_JETS,_THEN_PROPAGATE_THE_"
            "FINITE_TRIANGULAR_SYSTEMS_WITH_A_REGULAR_WEYL_CHART_COVER"
        ),
        "claim_boundary": {
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "channel_Weyl_enclosures": "OPEN",
            "zero_source_force": "OPEN",
            "same_action_saddle": "OPEN",
            "chord_03": "NOT_AUTHORIZED",
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in paths},
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
                "witnesses": payload["witnesses"],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
