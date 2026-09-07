"""Reuse saved full-core HS coefficients and exercise the event jet handoff."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae4_c2_stratified_event_flux_assembly import SECTOR_ORDER, assemble_stratified_direct_sum
from bhsm.interface.ae4_event_response_jet_integration import (
    canonical_noether_flux_balance_jet, solve_retarded_event_kkt_jet, substitute_terminal_hs_jets,
)
from bhsm.interface.ae4_existing_asset_system_integration import existing_variable_completion_handoffs

TARGET = ROOT / "artifacts/action_extension/BHSM_AE4_EVENT_RESPONSE_JET_INTEGRATION.json"
TERMINAL = ROOT / "artifacts/action_extension/BHSM_AE4_CURRENT_C2_TERMINAL_HS_JET_TRANSPORT.json"
INPUTS = (
    TERMINAL,
    ROOT / "src/bhsm/interface/ae4_event_response_jet_integration.py",
    ROOT / "src/bhsm/interface/ae4_c2_stratified_event_flux_assembly.py",
    ROOT / "src/bhsm/interface/ae4_existing_asset_system_integration.py",
    ROOT / "scripts/materialize_ae4_event_response_jet_integration.py",
)


def build_payload():
    saved = json.loads(TERMINAL.read_text(encoding="utf-8"))
    if not saved["validation_passed"]:
        raise ValueError("validated saved terminal transport required")
    reused = {}
    for channel, loads in saved["negative_axis_terminal_HS_jet_transport_rows"].items():
        reused[channel] = {}
        for name, coefficients in loads.items():
            reused[channel][name] = {
                "segment_count": coefficients["segment_count"],
                "spectral_parameter": coefficients["spectral_parameter"],
                "reference_terminal_load": coefficients["terminal_nonnegative_load"],
                "zero_terminal_jet_reference": substitute_terminal_hs_jets(
                    coefficients, terminal_load_first=0, terminal_load_second=0),
                "nonzero_terminal_jet_witness": substitute_terminal_hs_jets(
                    coefficients, terminal_load_first="0.375", terminal_load_second="-0.25"),
                "either_reference_is_action_selected": False,
            }

    # Synthetic finite matrix witness of the existing assembly. No physical
    # projection of the scalar HS references into this domain is assumed.
    sectors = {name: (np.eye(1)*(2+i/10), np.eye(1)*(.1+i/100),
                      np.eye(1)*(1.5+i/10+.2j)) for i, name in enumerate(SECTOR_ORDER)}
    blocks = assemble_stratified_direct_sum(sectors)
    n = len(SECTOR_ORDER)
    args = {
        "parent_jet": (blocks["parent_block"], np.diag(np.arange(n)/100), np.eye(n)*.02),
        "coupling_jet": (blocks["parent_child_coupling"], np.eye(n)*.03j, np.eye(n)*.01),
        "child_retarded_jet": (blocks["child_retarded_block"], np.eye(n)*.04j, np.eye(n)*.02),
        "response_jet": (np.ones((1,n)), np.arange(n)[None,:]/100, np.ones((1,n))*.01),
        "source_jet": (np.arange(n)/10, np.ones(n)*.1j, np.ones(n)*.02),
        "response_target_jet": (np.array([.1]), np.array([.03]), np.array([.01])),
    }
    response = solve_retarded_event_kkt_jet(**args)
    noether = canonical_noether_flux_balance_jet(
        trace_jet=response["parent_trace_jet"], event_traction_jets=response["event_traction_jets"],
        generator=1j*np.eye(n))
    checks = {
        "saved_full_core_coefficients_reused": all(
            row["segment_count"] == 1222 for loads in reused.values() for row in loads.values()),
        "six_existing_sectors_assembled": blocks["all_required_sectors_explicit"],
        "all_response_orders_balance": max(response["event_balance_residual_norms"]) < 1e-12,
        "all_child_equation_orders_balance": max(response["child_equation_residual_norms"]) < 1e-12,
        "all_constraint_orders_balance": max(response["response_constraint_residual_norms"]) < 1e-12,
        "all_Noether_orders_balance": max(abs(v) for v in noether["canonical_noether_flux_residual_jet"]) < 1e-12,
        "no_physical_values_promoted": not response["physical_sector_values_certified"],
    }
    return {
        "artifact": "BHSM_AE4_EVENT_RESPONSE_JET_INTEGRATION",
        "classification": "IMPLEMENTED_CONDITIONAL_RESPONSE_HANDOFF_WITH_EXISTING_OPERATOR_OWNERS",
        "saved_current_C2_transport_reuse": reused,
        "finite_matrix_witness": {
            "classification": "SYNTHETIC_SOFTWARE_VERIFICATION_NOT_PHYSICAL_SECTOR_DATA",
            "event_balance_residual_norms": response["event_balance_residual_norms"],
            "child_equation_residual_norms": response["child_equation_residual_norms"],
            "response_constraint_residual_norms": response["response_constraint_residual_norms"],
            "noether": noether,
        },
        "completion_handoffs": existing_variable_completion_handoffs(),
        "physical_terminal_HS_load_and_jets_derived": False,
        "current_C2_physical_HS_sector_projection_derived_here": False,
        "current_C2_physical_event_response_evaluated": False,
        "Gate7_action_center_caches_or_proof_contract_changed": False,
        "inputs": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper() for p in INPUTS},
        "validation": checks, "validation_passed": all(checks.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main():
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("response integration failed validation")
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True)+"\n", encoding="utf-8", newline="\n")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
