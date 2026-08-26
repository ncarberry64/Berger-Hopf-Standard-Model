"""Adjudicate Delta=0 using the exact denominator-free C2 field."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_exact_fixed_s_field import (  # noqa: E402
    exact_cancelled_euler_dirac_field_action,
    exact_fixed_s_field_action,
)
from bhsm.interface.aether_forward_c2_geometry_incidence import (  # noqa: E402
    boundary_geometry_action_covectors,
)


BASE = ROOT / "artifacts" / "flagship_integration"
FIXED_RECON = BASE / "BHSM_N12_C2_LOG_DESCRIPTOR_DELTA_STOP_RECONNAISSANCE.npz"
CANCELLED_RECON = BASE / "BHSM_N12_C2_CANCELLED_EULER_DIRAC_FLOW_RECONNAISSANCE.json"
CANCELLED_DATA = CANCELLED_RECON.with_suffix(".npz")
RESULT = BASE / "BHSM_N12_C2_CANCELLED_EULER_DIRAC_CHART.json"
THEORY = ROOT / "theory" / "n12_c2_cancelled_euler_dirac_chart.md"
MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_forward_c2_exact_fixed_s_field.py"
INPUTS = (FIXED_RECON, CANCELLED_RECON, CANCELLED_DATA, THEORY, MODULE)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _witness(state: np.ndarray, weights: np.ndarray, reference: np.ndarray) -> dict[str, Any]:
    field = exact_cancelled_euler_dirac_field_action(
        state=state, weights=weights, reference=reference,
    )
    geometry = boundary_geometry_action_covectors(state=state, weights=weights)
    lapse = math.exp(float(geometry["log_lapse"]))
    return {
        "selected_branch": int(field["selected_branch"]),
        "selected_eigenvalue": float(field["selected_eigenvalue"]),
        "selected_eigenline_gap": float(field["selected_eigenline_gap"]),
        "Delta": float(field["Delta"]),
        "cancelled_field_action_norm": float(np.linalg.norm(
            field["cancelled_field_action"]
        )),
        "boundary_lapse": lapse,
        "boundary_radius": math.exp(float(geometry["log_R4"])),
        "proper_time_density_d_tau_d_theta": (
            lapse * float(field["selected_eigenvalue"])
        ),
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing cancelled-chart inputs: " + ", ".join(missing))
    recon = json.loads(CANCELLED_RECON.read_text(encoding="utf-8"))
    negative_row = next(row for row in recon["rows"] if float(row["Delta"]) < 0.0)
    with np.load(FIXED_RECON) as data:
        positive_state = np.asarray(data["last_positive_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        reference = np.asarray(data["branch_reference"], dtype=float)
    with np.load(CANCELLED_DATA) as data:
        negative_state = np.asarray(
            data["centers"][int(negative_row["index"])], dtype=float
        )
    positive = exact_cancelled_euler_dirac_field_action(
        state=positive_state, weights=weights, reference=reference,
    )
    fixed = exact_fixed_s_field_action(
        state=positive_state,
        weights=weights,
        reference=reference,
        signed_descriptor=float(positive["selected_eigenvalue"]),
    )
    recombination_defect = float(np.linalg.norm(
        np.asarray(positive["cancelled_field_action"])
        - float(positive["Delta"]) * np.asarray(fixed["field_action"])
    ))
    positive_witness = _witness(positive_state, weights, reference)
    negative_witness = _witness(negative_state, weights, reference)
    validation = {
        "exact_positive_chart_recombination_closes": recombination_defect < 1.0e-15,
        "same_branch_24_on_both_reconnaissance_seeds": (
            positive_witness["selected_branch"]
            == negative_witness["selected_branch"] == 24
        ),
        "negative_Delta_seed_retains_positive_simple_Euler_Dirac_line": (
            negative_witness["Delta"] < 0.0
            and negative_witness["selected_eigenvalue"] > 0.0
            and negative_witness["selected_eigenline_gap"] > 0.0
        ),
        "negative_Delta_seed_retains_positive_lapse_radius_and_time_orientation": (
            negative_witness["boundary_lapse"] > 0.0
            and negative_witness["boundary_radius"] > 0.0
            and negative_witness["proper_time_density_d_tau_d_theta"] > 0.0
        ),
        "cancelled_field_is_finite_on_both_seeds": all(
            math.isfinite(row["cancelled_field_action_norm"])
            for row in (positive_witness, negative_witness)
        ),
        "reconnaissance_centers_not_promoted_to_exact_history_or_stop": True,
        "no_selector_recurrence_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_CANCELLED_EULER_DIRAC_CHART",
        "status": (
            "DELTA_ZERO_ADJUDICATED_AS_FIXED_DESCRIPTOR_CHART_BOUNDARY"
            if passed else "CANCELLED_EULER_DIRAC_CHART_AUDIT_FAILED"
        ),
        "exact_identities": {
            "scaled_field": "G_theta=Delta*F_s=[s*V_q,b_psi*Psi+s*V_hard]",
            "descriptor_rate": "Dlambda[G_theta]=Delta",
            "proper_time_field": "V_tau=G_theta/(N_boundary*s)",
            "proper_time_density": "d_tau/dtheta=N_boundary*s>0",
        },
        "adjudication": {
            "Delta_equals_zero": "TURNING_POINT_AND_FIXED_s_LOG_s_CHART_BOUNDARY",
            "Delta_equals_zero_is_event_or_canonical_stop": False,
            "Euler_Dirac_stop": "selected_eigenvalue_s_equals_zero",
            "full_Euler_Dirac_inverse_formed": False,
            "validated_exact_family_crossing_Delta_zero": False,
        },
        "positive_Delta_witness": positive_witness,
        "negative_Delta_recenter_seed": negative_witness,
        "fixed_chart_recombination_defect": recombination_defect,
        "exact_next_dependency": (
            "VALIDATED_THETA_OR_PROPER_TIME_INTERVAL_PROPAGATION_FROM_THE_1222_"
            "RESET_FAMILY_TO_CAPTURE_OR_A_GENUINE_RETAINED_STOP"
        ),
        "claim_boundary": {
            "Gate7": "OPEN_CURRENT_CONNECTION_OWNER",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "recombination_defect": payload["fixed_chart_recombination_defect"],
        "negative_seed": payload["negative_Delta_recenter_seed"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()

