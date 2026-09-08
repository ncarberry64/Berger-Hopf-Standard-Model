"""Materialize algebraic controls for the state/observable distinction."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bhsm.interface.ae31_c2_state_observable_audit import (  # noqa: E402
    CHARGE, CONJUGATION, REFERENCE, affine_response_screen, algebraic_controls,
    claim_boundary, direct_affine_difference, phase_covariance,
)
from bhsm.interface.ae31_c2_fixed_history_state_nonuniqueness import pure_self_dual_covariance  # noqa: E402

TARGET = ROOT / "artifacts/action_extension/BHSM_AE31_C2_STATE_OBSERVABLE_AUDIT.json"


def build_payload() -> dict:
    controls = algebraic_controls()
    rows = {name: affine_response_screen(matrix) for name, matrix in controls.items()}
    errors = {key: 0. for key in ("purity", "CAR_reality", "charge", "affine_formula")}
    for theta in (0., .17, .63, np.pi/2):
        for phase in (0., .41, np.pi/2, np.pi):
            c = phase_covariance(theta, phase)
            errors["purity"] = max(errors["purity"], float(np.linalg.norm(c@c-c)))
            errors["CAR_reality"] = max(errors["CAR_reality"], float(np.linalg.norm(
                c+CONJUGATION@c.conj()@CONJUGATION-np.eye(4))))
            errors["charge"] = max(errors["charge"], float(np.linalg.norm(c@CHARGE-CHARGE@c)))
            for name, matrix in controls.items():
                row = rows[name]
                b = complex(row["b_real"], row["b_imag"])
                formula = row["a"]*np.sin(theta)**2+np.sin(2*theta)*(np.exp(1j*phase)*b).real
                errors["affine_formula"] = max(errors["affine_formula"],
                    abs(direct_affine_difference(matrix, theta, phase)-float(formula)))
    c = phase_covariance(.37, .61)
    nonlinear = {
        "functional": "F(C)=Tr(C^2)",
        "reference_value": float(np.trace(REFERENCE@REFERENCE).real),
        "rotated_value": float(np.trace(c@c).real),
        "reference_gradient": "2*P0",
        "incorrect_affine_extension_of_reference_gradient_changes_by": direct_affine_difference(2*REFERENCE, .37, .61),
        "purpose": "Counterexample to applying an affine finite-change test to a nonlinear functional",
    }
    # Free CAR control only: chosen dimensionless energies are not BHSM masses.
    energies = np.asarray([1., 2., -1., -2.])
    ut = np.diag(np.exp(-.4j*energies))
    us = np.diag(np.exp(.2j*energies))
    greater = ut@c@us.conj().T
    lesser = ut@(np.eye(4)-c)@us.conj().T
    causal_control = {
        "classification": "FIXED_QUADRATIC_CAR_ALGEBRA_CONTROL",
        "dimensionless_control_energies": energies.tolist(),
        "control_energies_are_BHSM_masses": False,
        "retarded_state_difference_norm": float(np.linalg.norm(greater+lesser-ut@us.conj().T)),
        "time_ordered_state_difference_norm": float(np.linalg.norm(ut@(c-REFERENCE)@us.conj().T)),
        "retarded_identity": "G_retarded=-i*theta(t-s)*U(t,s), independent of C for this fixed quadratic operator",
        "interacting_or_composite_response_independence_inferred": False,
    }
    validation = {
        "numerical_algebra_residuals_small": max(errors.values()) < 2e-14,
        "real_phase_reproduces_retained_covariance": bool(np.allclose(
            phase_covariance(.37, 0), pure_self_dual_covariance(.37)["covariance_theta"], rtol=0, atol=2e-15)),
        "identity_control_is_invariant": rows["identity"]["floating_coefficients_exactly_zero"],
        "charge_control_is_invariant": rows["charge"]["floating_coefficients_exactly_zero"],
        "occupation_control_is_not_invariant": rows["reference_occupation"]["affine_range_diameter"] == 2.,
        "complex_phase_reveals_real_angle_blind_spot":
            abs(direct_affine_difference(controls["imaginary_mixed_response"], np.pi/4, 0)) < 2e-15
            and abs(direct_affine_difference(controls["imaginary_mixed_response"], np.pi/4, np.pi/2)+1) < 2e-15,
        "nonlinear_counterexample_verified": abs(nonlinear["rotated_value"]-2) < 2e-15
            and abs(nonlinear["incorrect_affine_extension_of_reference_gradient_changes_by"]) > .1,
        "quadratic_retarded_control_does_not_select_time_ordered_state":
            causal_control["retarded_state_difference_norm"] < 2e-15
            and causal_control["time_ordered_state_difference_norm"] > .1,
    }
    sources = [Path(__file__), ROOT / "src/bhsm/interface/ae31_c2_state_observable_audit.py",
               ROOT / "src/bhsm/interface/ae31_c2_fixed_history_state_nonuniqueness.py"]
    return {
        "artifact": "BHSM_AE31_C2_STATE_OBSERVABLE_AUDIT",
        "action_version": "BHSM-AE-3.1.0",
        "classification": "EXACT_ALGEBRAIC_CRITERION_WITH_BINARY64_CONTROLS",
        "controls_are_physical_operators": False,
        "controls": rows, "nonlinear_counterexample": nonlinear,
        "quadratic_causal_control": causal_control,
        "maximum_sampled_residuals": errors,
        "sample_grid_is_a_proof": False,
        "lepton_target": {
            "functional": "log(M_e)-9*log(M_mu)+8*log(M_tau)-54/pi",
            "first_variation": "delta_M_e/M_e-9*delta_M_mu/M_mu+8*delta_M_tau/M_tau",
            "physical_mass_functionals_defined_here": False,
            "covariance_response_operator_available": False,
            "numerical_target_used": False,
        },
        "inputs": {str(p.relative_to(ROOT)).replace("\\", "/"):
            hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper() for p in sources},
        "validation": validation, "validation_passed": all(validation.values()),
        "claim_boundary": claim_boundary(), "FULL_BHSM_COMPLETE": False,
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
    print(json.dumps({"output": str(args.output), "validation": payload["validation"]}))


if __name__ == "__main__":
    main()
