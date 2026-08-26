"""Reproducible non-proof reconnaissance for C2 log-chart transversality.

This script deliberately emits a ``RECONNAISSANCE_ONLY`` artifact.  Its
Heun centers may seed recentered interval boxes but are not validated BHSM
histories and may not be promoted to a physical endpoint.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_exact_fixed_s_field import (  # noqa: E402
    exact_fixed_s_field_action,
)


BASE = ROOT / "artifacts" / "flagship_integration"
CORE = BASE / "BHSM_N12_C2_LOHNER_STEP_1222.json"
CORE_DATA = CORE.with_suffix(".npz")
RESULT = BASE / "BHSM_N12_C2_LOG_DESCRIPTOR_DELTA_STOP_RECONNAISSANCE.json"
DATA = RESULT.with_suffix(".npz")


def main() -> None:
    core = json.loads(CORE.read_text(encoding="utf-8"))
    with np.load(CORE_DATA) as source:
        state = np.asarray(source["endpoint_predictor_center"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
    descriptor = float(core["segment"]["signed_descriptor_end"])
    field = None
    centers = [state.copy()]
    descriptors = [descriptor]
    rows = []
    targets = [1e-18, 1e-16, 1e-14, 1e-12, 1e-11, 1e-10, 2.5e-10]
    target = targets[-1]
    while target < 2e-9:
        target *= 1.25
        targets.append(target)
    failure = None
    for target in targets:
        try:
            if field is None:
                field = exact_fixed_s_field_action(
                    state=state, weights=weights, reference=reference,
                    signed_descriptor=descriptor,
                )
            predictor = state + (target - descriptor) * np.asarray(
                field["field_action"], dtype=float
            ) / weights
            predictor_field = exact_fixed_s_field_action(
                state=predictor, weights=weights, reference=reference,
                signed_descriptor=target,
            )
            next_state = state + 0.5 * (target - descriptor) * (
                np.asarray(field["field_action"], dtype=float)
                + np.asarray(predictor_field["field_action"], dtype=float)
            ) / weights
            next_field = exact_fixed_s_field_action(
                state=next_state, weights=weights, reference=reference,
                signed_descriptor=target,
            )
            state = next_state
            descriptor = target
            field = next_field
            centers.append(state.copy())
            descriptors.append(descriptor)
            if target >= 2.5e-10:
                rows.append({
                    "signed_descriptor": target,
                    "selected_branch": int(field["selected_branch"]),
                    "selected_eigenvalue": float(field["selected_eigenvalue"]),
                    "c_psi": float(field["c_psi"]),
                    "b_psi": float(field["b_psi"]),
                    "R_Dlambda_Vhard": float(field["R_Dlambda_Vhard"]),
                    "Delta": float(field["Delta"]),
                })
        except ArithmeticError as error:
            failure = {
                "attempted_signed_descriptor": target,
                "exception": f"{type(error).__name__}: {error}",
            }
            break
    joint = np.concatenate((state, state))
    np.savez_compressed(
        DATA,
        centers=np.asarray(centers),
        signed_descriptors=np.asarray(descriptors),
        last_positive_state=state,
        state=np.asarray(joint),
        state_weights=weights,
        branch_reference=reference,
    )
    payload = {
        "artifact": "BHSM_N12_C2_LOG_DESCRIPTOR_DELTA_STOP_RECONNAISSANCE",
        "status": "RECONNAISSANCE_ONLY_NOT_A_CERTIFICATE",
        "method": "GEOMETRIC_HEUN_PREDICTOR_CORRECTOR_IN_SIGNED_DESCRIPTOR",
        "rows": rows,
        "first_failed_trial": failure,
        "last_positive_signed_descriptor": descriptor,
        "last_positive_Delta": rows[-1]["Delta"],
        "candidate_boundary_type": "FIXED_DESCRIPTOR_TRANSVERSALITY_LOSS",
        "candidate_boundary_is_canonical_stop": False,
        "reason_not_canonical": (
            "Delta=0 loses the fixed-s chart but does not by itself make the "
            "Euler-Dirac selected eigenvalue vanish"
        ),
        "proof_center_selected_as_physical_history": False,
        "permitted_use": "RECENTERED_INTERVAL_BOX_SEED_ONLY",
        "data": DATA.relative_to(ROOT).as_posix(),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
