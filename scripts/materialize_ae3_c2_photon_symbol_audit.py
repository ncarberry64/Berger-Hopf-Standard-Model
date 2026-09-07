"""Materialize a scoped audit of the existing finite-mode photon diagnostic."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bhsm.interface.ae3_c2_photon_symbol_audit import (  # noqa: E402
    flat_half_space_control, spectral_dtn, spectral_witness,
)
from bhsm.interface.ae3_c2_lorentzian_gauge_ghost_hessian import (  # noqa: E402
    lowest_transverse_residue_witness, transverse_frequency_dtn,
)

TARGET = ROOT / "artifacts/action_extension/BHSM_AE3_C2_PHOTON_SYMBOL_AUDIT.json"


def build_payload() -> dict:
    rows = [spectral_witness(n) for n in (2, 4, 8, 16)]
    cutoff = spectral_witness(2, epsilon=5.0e-4)
    old = lowest_transverse_residue_witness()
    same_invariant = {"s_minus_q_squared": 4.0,
                      "N_level2_q_squared0": rows[0]["N_static"],
                      "N_level4_q_squared12": spectral_dtn(16.0, 12.0)}
    null_shell = {"level": 2, "spatial_eigenvalue": 4.0, "q_squared": 4.0,
                  "N_on_reference_Maxwell_shell": spectral_dtn(4.0, 4.0),
                  "scope": "Frozen isolated transverse trace; not a global quantum pole calculation"}
    residual_keys = ("static_energy_residual", "spectral_envelope_residual",
                     "frequency_envelope_residual", "spatial_centered_difference_residual",
                     "frequency_centered_difference_residual")
    validation = {
        "independent_Riccati_solver_reproduces_retained_N":
            abs(rows[0]["N_static"] - old["static_dimensionless_DtN"]) < 2.0e-9,
        "retained_complete_mode_ratio_reproduced":
            abs(rows[0]["complete_mode_ratio"] - old["temporal_to_complete_spatial_mode_residue_ratio"]) < 2.0e-9,
        "energy_sensitivity_and_finite_difference_checks":
            all(row[key] < 2.0e-8 for row in rows + [cutoff] for key in residual_keys),
        "derivative_ratio_strictly_between_complete_ratio_and_one":
            all(0 < row["complete_mode_ratio"] < row["derivative_ratio"] < 1 for row in rows),
        "static_quotient_not_spectral_derivative":
            all(row["static_quotient_minus_spatial_derivative"] > 0 for row in rows),
        "cutoff_halving_stable_at_diagnostic_tolerance":
            abs(rows[0]["derivative_ratio"] - cutoff["derivative_ratio"]) < 2.0e-8,
        "two_physical_levels_do_not_depend_only_on_s_minus_q_squared":
            same_invariant["N_level4_q_squared12"] > same_invariant["N_level2_q_squared0"],
        "no_zero_on_reference_Maxwell_shell_in_frozen_trace":
            null_shell["N_on_reference_Maxwell_shell"] > 0,
        "independent_retained_solver_agrees_on_reference_shell":
            abs(null_shell["N_on_reference_Maxwell_shell"] - transverse_frequency_dtn(2, q_squared=4.0)) < 2e-9,
    }
    paths = [Path(__file__), ROOT / "src/bhsm/interface/ae3_c2_photon_symbol_audit.py",
             ROOT / "src/bhsm/interface/ae3_c2_lorentzian_gauge_ghost_hessian.py",
             ROOT / "src/bhsm/interface/aether_event_weighted_unified_pushforward_v15_71.py"]
    return {
        "artifact": "BHSM_AE3_C2_PHOTON_SYMBOL_AUDIT", "action_version": "BHSM-AE-3.0.0",
        "classification": "ANALYTIC_SCOPE_AUDIT_WITH_BINARY64_NUMERICAL_WITNESSES",
        "arithmetic": "SciPy binary64; finite-cutoff ODE and quadrature; not an outward certificate",
        "scope": "Frozen transverse radial problem; spatial spectral continuation is diagnostic only",
        "flat_half_space_analytic_control": flat_half_space_control(),
        "mode_witnesses": rows, "cutoff_halving_witness": cutoff,
        "equal_s_minus_q_squared_comparison": same_invariant,
        "reference_Maxwell_shell_witness": null_shell,
        "validation": validation, "validation_passed": all(validation.values()),
        "inputs": {str(p.relative_to(ROOT)).replace("\\", "/"):
                   hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()
                   for p in paths},
        "claim_boundary": {
            "static_quotient_and_spectral_derivative_distinguished": True,
            "complete_mode_ratio_is_universal_Lorentz_symmetry_test": False,
            "retained_exact_local_Maxwell_identification_repaired": False,
            "frozen_isolated_trace_has_no_zero_on_reference_Maxwell_shell": True,
            "formal_frozen_transverse_boundary_principal_symbol_identified": True,
            "global_causal_or_quantum_propagator_derived": False,
            "physical_photon_pole_derived": False,
            "action_or_domain_changed": False,
            "empirical_input_used": False,
            "numerical_outward_enclosure": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "FULL_BHSM_COMPLETE": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=TARGET)
    args = parser.parse_args(argv)
    payload = build_payload()
    if not payload["validation_passed"]:
        raise RuntimeError(str(payload["validation"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "lowest_mode": payload["mode_witnesses"][0]}))


if __name__ == "__main__":
    main()
