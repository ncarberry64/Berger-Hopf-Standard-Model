"""Reproduce conditional BHSM response bridges without a physical campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae4_c2_stratified_event_flux_assembly import (
    SECTOR_ORDER, assemble_stratified_direct_sum,
)
from bhsm.interface.ae4_mixed_event_response import (
    canonical_noether_flux_balance_mixed_jet, solve_retarded_event_kkt_mixed_jet,
)
from bhsm.interface.ae4_mixed_terminal_hs import substitute_mixed_terminal_hs_jets

TERMINAL = ROOT / "artifacts/action_extension/BHSM_AE4_CURRENT_C2_TERMINAL_HS_JET_TRANSPORT.json"
DEFAULT_OUTPUT = ROOT / "artifacts/action_extension/BHSM_WHOLE_SYSTEM_RESPONSE_BRIDGES_20261013.json"
INPUTS = (
    TERMINAL,
    ROOT / "src/bhsm/interface/ae4_c2_stratified_event_flux_assembly.py",
    ROOT / "src/bhsm/interface/ae4_mixed_event_response.py",
    ROOT / "src/bhsm/interface/ae4_mixed_terminal_hs.py",
    ROOT / "src/bhsm/interface/charged_lepton_pole_observable.py",
    ROOT / "src/bhsm/interface/universal_dressed_pole.py",
    ROOT / "src/bhsm/interface/ae31_charged_lepton_pole_dressing_invariant.py",
    ROOT / "scripts/materialize_bhsm_whole_system_response_bridges.py",
)


def _array(value: np.ndarray) -> dict[str, object]:
    """Preserve complete numerical witness operands, including complex parts."""
    return {"real": value.real.tolist(), "imaginary": value.imag.tolist()}


def build_payload() -> dict[str, object]:
    saved = json.loads(TERMINAL.read_text(encoding="utf-8"))
    if not saved["validation_passed"]:
        raise ValueError("validated existing terminal transport coefficients required")
    reused = {}
    for channel, loads in saved["negative_axis_terminal_HS_jet_transport_rows"].items():
        reused[channel] = {}
        for name, coefficients in loads.items():
            # The zero-load reference stays fixed: no admissible nonnegative
            # open-neighborhood terminal branch is inferred from a reference.
            terminal_jet = (0, 0, 0) if coefficients["terminal_nonnegative_load"] == 0 else ("0.375", "-0.25", "0.2")
            reused[channel][name] = {
                "segment_count": coefficients["segment_count"],
                "spectral_parameter": coefficients["spectral_parameter"],
                "base_terminal_reference_load": coefficients["terminal_nonnegative_load"],
                "same_scalar_H_fixed_profile_mixed_substitution": substitute_mixed_terminal_hs_jets(
                    coefficients, hs_coordinate_jet=("0.7", "-0.4", "0.15"),
                    terminal_load_jet=terminal_jet,
                ),
                "classification": "REFERENCE_COEFFICIENT_REUSE_NOT_PHYSICAL_BOUNDARY_DATA",
            }

    # Synthetic six-sector finite matrices exercise the existing graded order.
    # They have no physical projection from the saved scalar HS references.
    sectors = {
        name: (np.eye(1)*(2+i/10), np.eye(1)*(.1+i/100), np.eye(1)*(1.5+i/10+.2j))
        for i, name in enumerate(SECTOR_ORDER)
    }
    blocks = assemble_stratified_direct_sum(sectors)
    n = len(SECTOR_ORDER)
    cross = np.diag(np.ones(n-1), 1) + np.diag(np.ones(n-1), -1)
    args = {
        "parent_jet": (blocks["parent_block"], np.diag(np.arange(n)/100), cross*.03, np.eye(n)*.02),
        "coupling_jet": (blocks["parent_child_coupling"], np.eye(n)*.03j, cross*.02, np.eye(n)*.01),
        "child_retarded_jet": (blocks["child_retarded_block"], cross*.04j, np.diag(np.arange(n)/100), np.eye(n)*.02),
        "response_jet": (np.ones((1,n)), np.arange(n)[None,:]/100, np.ones((1,n))*.02j, np.ones((1,n))*.01),
        "source_jet": (np.arange(n)/10, np.ones(n)*.1j, np.arange(n)*.02, np.ones(n)*.02),
        "response_target_jet": (np.array([.1]), np.array([.03]), np.array([.02j]), np.array([.01])),
    }
    response = solve_retarded_event_kkt_mixed_jet(**args)
    generator = 1j * np.diag(np.arange(1, n+1))
    noether = canonical_noether_flux_balance_mixed_jet(
        trace_jet=response["parent_trace_jet"],
        event_traction_jets=response["event_traction_jets"], generator=generator,
    )
    checks = {
        "saved_1222_segment_coefficients_reused": all(
            row["segment_count"] == 1222 for loads in reused.values() for row in loads.values()),
        "six_existing_sectors_assembled": blocks["all_required_sectors_explicit"],
        "all_four_event_orders_balance": max(response["event_balance_residual_norms"]) < 1e-12,
        "all_four_child_orders_balance": max(response["child_equation_residual_norms"]) < 1e-12,
        "all_four_constraint_orders_balance": max(response["response_constraint_residual_norms"]) < 1e-12,
        "all_four_Noether_orders_balance": max(abs(v) for v in noether["canonical_noether_flux_residual_jet"]) < 1e-12,
        "no_inverse_or_regularizer_used": not (response["explicit_inverse_formed"] or response["regularizer_or_pseudoinverse_used"]),
        "physical_promotion_remains_false": not response["physical_sector_values_certified"],
    }
    return {
        "artifact": "BHSM_WHOLE_SYSTEM_RESPONSE_BRIDGES_20261013",
        "classification": "CONDITIONAL_INTEGRATION_WITH_EXISTING_OPERATOR_OWNERS",
        "saved_terminal_transport_reuse": reused,
        "finite_event_witness": {
            "classification": "SYNTHETIC_SOFTWARE_WITNESS_NOT_PHYSICAL_SECTOR_DATA",
            "sector_order": SECTOR_ORDER,
            "jet_labels": response["jet_labels"],
            "input_jets": {name: [_array(v) for v in values] for name, values in args.items()},
            "fixed_generator": _array(generator),
            "parent_trace_jet": [_array(v) for v in response["parent_trace_jet"]],
            "child_state_jet": [_array(v) for v in response["future_child_state_jet"]],
            "response_multiplier_jet": [_array(v) for v in response["response_multiplier_jet"]],
            "event_balance_residual_norms": response["event_balance_residual_norms"],
            "child_equation_residual_norms": response["child_equation_residual_norms"],
            "response_constraint_residual_norms": response["response_constraint_residual_norms"],
            "residual_normalization": response["residual_normalization"],
            "noether": noether,
        },
        "pole_to_lepton_invariant_bridge": {
            "source": "src/bhsm/interface/charged_lepton_pole_observable.py",
            "common_log_mass_jacobian": [8, -9, 1],
            "common_scale_log_direction": [1, 1, 1],
            "shared_scale_contraction": 0,
            "full_correlated_covariance_required": True,
            "physical_family_poles_supplied": False,
        },
        "input_hash_protocol": "SHA256_OF_LF_NORMALIZED_SOURCE_BYTES",
        "inputs": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest() for p in INPUTS},
        "scalar_HS_reference_to_physical_sector_projection_derived": False,
        "physical_terminal_load_or_jets_selected": False,
        "physical_event_response_evaluated": False,
        "Gate7_background_or_proof_contract_changed": False,
        "muon_calculation_or_subtotal_changed": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": checks,
        "validation_passed": all(checks.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("conditional integration witness failed validation")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False)+"\n", encoding="utf-8", newline="\n")
    print(args.output)


if __name__ == "__main__":
    main()
