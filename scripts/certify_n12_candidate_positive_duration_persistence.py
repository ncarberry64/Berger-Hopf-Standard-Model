"""Apply the existing BHSM persistence gate to the N12 root candidate.

This is the same projected RK4/coarse-fine witness and local Euler--Dirac
existence test used for the validated N4--N6 children.  The source is the
current N12 child half of the unchanged joint checkpoint.  Persistence may
be measured before the root ball is finally promoted, but cannot promote the
child while the direct radii certificate remains fail-closed.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
)
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _eta_legendre_minimum,
    _exact_full_jet_euler_dirac_acceleration,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    project_nested_constraints_sobolev,
    sobolev_weights,
    spectral_frequencies,
)


ORDER = 12
POINTS = 96
TIME_STEP = float(os.environ.get(
    "BHSM_N12_PERSISTENCE_TIME_STEP", "1e-8"
))
STEPS = int(os.environ.get("BHSM_N12_PERSISTENCE_STEPS", "10"))
CHECKPOINT = Path(os.environ.get(
    "BHSM_N12_CHECKPOINT", ".tmp_direct_n12_corrected_branch_state.npz"
))
RADII = Path(os.environ.get(
    "BHSM_N12_FULL_RADII_RESULT", ".tmp_direct_n12_full_action_radii.json"
))
RESULT = Path(os.environ.get(
    "BHSM_N12_PERSISTENCE_RESULT",
    ".tmp_direct_n12_candidate_positive_duration_persistence.json",
))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    if TIME_STEP <= 0.0 or STEPS < 1:
        raise ValueError("positive persistence controls required")
    size = dimensions(ORDER)
    qdim = size["coordinates"]
    state_dimension = 2 * qdim + size["multipliers"]
    checkpoint = np.load(CHECKPOINT)
    joint = np.asarray(checkpoint["state"], dtype=float)
    source = joint[state_dimension:]
    q0 = source[:qdim].copy()
    v0 = source[qdim:2 * qdim].copy()
    m0 = source[2 * qdim:].copy()
    frequencies = spectral_frequencies(ORDER)
    weights = sobolev_weights(ORDER)
    q_weight = (1.0 + frequencies["coordinates"] ** 2) ** 3.0
    product_weight = np.concatenate((
        q_weight, weights["velocities"], weights["multipliers"]
    ))
    signs_k = (-1.0) ** np.arange(1, ORDER + 1)

    def boundary_lapse(multipliers: np.ndarray) -> float:
        return float(math.exp(float(multipliers[:ORDER] @ signs_k)))

    def rhs(q: np.ndarray, v: np.ndarray, m: np.ndarray):
        dynamics = _exact_full_jet_euler_dirac_acceleration(
            ORDER, q, v, m, points=POINTS
        )
        return (
            np.asarray(dynamics["coordinate_rate"], dtype=float),
            np.asarray(dynamics["acceleration"], dtype=float),
            np.asarray(dynamics["multiplier_rate"], dtype=float),
            float(dynamics["Dirac_condition_number"]),
        )

    def rk4_projected(q, v, m, step):
        k1 = rhs(q, v, m)
        k2 = rhs(
            q + 0.5 * step * k1[0],
            v + 0.5 * step * k1[1],
            m + 0.5 * step * k1[2],
        )
        k3 = rhs(
            q + 0.5 * step * k2[0],
            v + 0.5 * step * k2[1],
            m + 0.5 * step * k2[2],
        )
        k4 = rhs(
            q + step * k3[0],
            v + step * k3[1],
            m + step * k3[2],
        )
        q_trial = q + step * (
            k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0]
        ) / 6.0
        v_trial = v + step * (
            k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1]
        ) / 6.0
        m_trial = m + step * (
            k1[2] + 2.0 * k2[2] + 2.0 * k3[2] + k4[2]
        ) / 6.0
        projection = project_nested_constraints_sobolev(
            ORDER, q_trial, v_trial, m_trial, points=POINTS
        )
        if not projection["success"]:
            raise RuntimeError(str(projection["message"]))
        return (
            q_trial,
            np.asarray(projection["velocities"], dtype=float),
            np.asarray(projection["multipliers"], dtype=float),
            max(k1[3], k2[3], k3[3], k4[3]),
            projection,
        )

    def run(step: float, count: int) -> dict[str, object]:
        q, v, m = q0.copy(), v0.copy(), m0.copy()
        proper_time = 0.0
        rows = []
        maximum_condition = 0.0
        first_exit = None
        for index in range(count + 1):
            constraints = constraint_residual(
                ORDER, q, v, m, points=POINTS
            )
            eta = _eta_legendre_minimum(ORDER, q, m, points=3000)
            state = np.concatenate((q, v, m))
            maximum_constraint = float(np.max(np.abs(constraints)))
            finite = bool(np.all(np.isfinite(state)))
            inside = bool(
                finite and maximum_constraint < 1.0e-8
                and eta["minimum"] > 0.0
            )
            rows.append({
                "step": index,
                "coordinate_time": index * step,
                "child_proper_time": proper_time,
                "maximum_constraint_residual": maximum_constraint,
                "eta_Legendre_minimum": eta["minimum"],
                "boundary_lapse": boundary_lapse(m),
                "finite": finite,
                "inside_persistence_domain": inside,
                "configuration_displacement_norm": float(np.linalg.norm(q-q0)),
                "velocity_displacement_norm": float(np.linalg.norm(v-v0)),
            })
            if not inside:
                first_exit = dict(rows[-1])
                break
            if index < count:
                lapse_before = boundary_lapse(m)
                q, v, m, condition, projection = rk4_projected(q, v, m, step)
                maximum_condition = max(maximum_condition, condition)
                rows[-1]["outgoing_projection_success"] = bool(
                    projection["success"]
                )
                rows[-1]["outgoing_Dirac_condition_number"] = condition
                proper_time += 0.5 * step * (
                    lapse_before + boundary_lapse(m)
                )
        final = np.concatenate((q, v, m))
        return {
            "time_step": step,
            "requested_steps": count,
            "completed": len(rows) == count + 1 and first_exit is None,
            "rows": rows,
            "coordinate_duration": rows[-1]["coordinate_time"],
            "child_proper_duration": rows[-1]["child_proper_time"],
            "maximum_constraint_residual": max(
                row["maximum_constraint_residual"] for row in rows
            ),
            "minimum_eta_Legendre": min(
                row["eta_Legendre_minimum"] for row in rows
            ),
            "maximum_Dirac_condition_number": maximum_condition,
            "final_state": final.tolist(),
            "final_configuration_displacement_norm": rows[-1][
                "configuration_displacement_norm"
            ],
            "final_velocity_displacement_norm": rows[-1][
                "velocity_displacement_norm"
            ],
            "first_exit": first_exit,
        }

    coarse = run(TIME_STEP, STEPS)
    fine = run(0.5 * TIME_STEP, 2 * STEPS)
    coarse_final = np.asarray(coarse["final_state"])
    fine_final = np.asarray(fine["final_state"])
    convergence = float(np.linalg.norm(
        (coarse_final - fine_final) * product_weight
    ) / max(1.0, np.linalg.norm(fine_final * product_weight)))
    numerical_witness = bool(
        coarse["completed"] and fine["completed"]
        and coarse["maximum_constraint_residual"] < 1.0e-8
        and fine["maximum_constraint_residual"] < 1.0e-8
        and min(
            coarse["minimum_eta_Legendre"], fine["minimum_eta_Legendre"]
        ) > 0.0
        and fine["child_proper_duration"] > 0.0
        and fine["final_configuration_displacement_norm"] > 0.0
        and fine["final_velocity_displacement_norm"] > 0.0
        and convergence < 1.0e-2
    )
    initial = _exact_full_jet_euler_dirac_acceleration(
        ORDER, q0, v0, m0, points=POINTS
    )
    dirac_singular = np.linalg.svd(
        np.asarray(initial["Dirac_hessian"]), compute_uv=False
    )
    vector_field = np.concatenate((
        initial["coordinate_rate"], initial["acceleration"],
        initial["multiplier_rate"],
    ))
    initial_constraints = constraint_residual(
        ORDER, q0, v0, m0, points=POINTS
    )
    initial_eta = _eta_legendre_minimum(ORDER, q0, m0, points=5000)
    local_existence = bool(
        np.all(np.isfinite(vector_field))
        and dirac_singular[-1] > 0.0
        and np.max(np.abs(initial_constraints)) < 1.0e-8
        and initial_eta["minimum"] > 0.0
        and boundary_lapse(m0) > 0.0
        and np.linalg.norm(v0) > 0.0
    )
    radii = json.loads(RADII.read_text(encoding="utf-8"))
    root_certified = bool(radii.get("validation_passed") is True)
    payload = {
        "classification": (
            "N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"
            if root_certified and (local_existence or numerical_witness) else
            "N12_ROOT_CANDIDATE_PERSISTENCE_VALIDATED_ROOT_CERTIFICATE_OPEN"
            if local_existence or numerical_witness else
            "N12_ROOT_CANDIDATE_PERSISTENCE_NOT_VALIDATED"
        ),
        "source": "DIRECT_N12_UNCHANGED_57_ROW_ROOT_CANDIDATE",
        "checkpoint": str(CHECKPOINT),
        "checkpoint_SHA256": _sha256(CHECKPOINT),
        "radii_result": str(RADII),
        "radii_result_SHA256": _sha256(RADII),
        "coarse_evolution": coarse,
        "fine_evolution": fine,
        "coarse_fine_relative_difference": convergence,
        "local_existence": {
            "Dirac_smallest_singular_value": float(dirac_singular[-1]),
            "Dirac_condition_number": float(initial["Dirac_condition_number"]),
            "vector_field_finite": bool(np.all(np.isfinite(vector_field))),
            "vector_field_norm": float(np.linalg.norm(vector_field)),
            "initial_constraint_maximum": float(
                np.max(np.abs(initial_constraints))
            ),
            "initial_eta_margin": initial_eta["minimum"],
            "initial_boundary_lapse": boundary_lapse(m0),
            "positive_duration_exists": local_existence,
        },
        "validation": {
            "same_existing_persistence_domain_and_gates": True,
            "nonzero_motion_retained": bool(
                fine["final_configuration_displacement_norm"] > 0.0
                and fine["final_velocity_displacement_norm"] > 0.0
            ),
            "local_positive_duration_existence": local_existence,
            "coarse_fine_numerical_witness": numerical_witness,
            "direct_N12_root_ball_certified": root_certified,
            "new_physics_equation_constraint_or_gate": False,
        },
        "validation_passed": bool(
            root_certified and (local_existence or numerical_witness)
        ),
        "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED": bool(
            root_certified and (local_existence or numerical_witness)
        ),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
