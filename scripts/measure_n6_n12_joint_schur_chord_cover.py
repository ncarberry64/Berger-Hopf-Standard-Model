"""Measure the unchanged N6-to-N12 joint weak Schur/chord bridge.

The paired slopes and chord/Broyden updates are proposal machinery only.
Promotion remains controlled by the exact retained joint weak residual, and
the emitted artifact stays fail-closed unless every nonlinear radii and
existing physical-neighborhood certificate is actually present.
"""

import hashlib
import json
import os
from pathlib import Path

import numpy as np

from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _attachment_coordinates_at_order,
    _attachment_jacobian_at_order,
    _authoritative_n6_event_child_anchor,
    _canonical_pair_at_order,
    _eta_legendre_minimum,
    _trace_jacobian_at_order,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    exact_action_jet_at_state,
)
from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    embed_nested_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)
from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
)


PATH = Path("artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json")
CHECKPOINT = Path(".tmp_joint_schur_n12_state.npz")
RESULT = Path(".tmp_joint_schur_result.json")
ARTIFACT = Path(
    "artifacts/BHSM_N6_N12_JOINT_SCHUR_CHORD_COVER.json"
)
ORDER = 12
LOW = 6
POINTS = 96
STEPS = (2.0e-5, 1.0e-5)
PROPOSAL_STEPS = int(os.environ.get("BHSM_CHORD_PROPOSAL_STEPS", "0"))
if not 0 <= PROPOSAL_STEPS <= 24:
    raise ValueError("BHSM_CHORD_PROPOSAL_STEPS must lie in [0,24]")


def decode(exact):
    return tuple(
        np.asarray([float.fromhex(value) for value in exact[name]])
        for name in ("coordinates", "velocities", "multipliers")
    )


def embed_q(value, source, target):
    result = np.zeros(1 + 3 * target)
    result[0] = value[0]
    for family in range(3):
        result[1 + family * target:1 + family * target + source] = value[
            1 + family * source:1 + (family + 1) * source
        ]
    return result


def embed_qm(value, source, target):
    q_source = 1 + 3 * source
    q_target = 1 + 3 * target
    result = np.zeros(q_target + 2 * target)
    result[:q_target] = embed_q(value[:q_source], source, target)
    result[q_target:q_target + source] = value[q_source:q_source + source]
    result[q_target + target:q_target + target + source] = value[
        q_source + source:q_source + 2 * source
    ]
    return result


payload = json.loads(PATH.read_text(encoding="utf-8"))["cross_resolution_reconnaissance"]
anchor = _authoritative_n6_event_child_anchor(payload)
event6 = decode(anchor["event_exact"])
child6 = decode(anchor["child_exact"])
event = embed_nested_state(*event6, 6, ORDER)
child = embed_nested_state(*child6, 6, ORDER)
qdim = dimensions(ORDER)["coordinates"]
mdim = dimensions(ORDER)["multipliers"]
sdim = 2 * qdim + mdim
freq = spectral_frequencies(ORDER)
q_weights = np.sqrt(1.0 + freq["coordinates"] ** 2)
m_weights = np.sqrt(1.0 + freq["multipliers"] ** 2)
state_weights = np.concatenate((q_weights, np.ones(qdim), m_weights))
joint_weights = np.concatenate((state_weights, state_weights))
trace = _trace_jacobian_at_order(ORDER)
attachment = _attachment_jacobian_at_order(ORDER, child[0])
boundary = np.vstack((trace, attachment[1]))


def symmetric_power(matrix, power):
    values, vectors = np.linalg.eigh(matrix)
    return vectors @ np.diag(values**power) @ vectors.T


boundary_inverse_sqrt = symmetric_power(
    boundary @ np.diag(1.0 / q_weights**2) @ boundary.T, -0.5
)
momentum_sqrt = symmetric_power(attachment @ attachment.T, 0.5)

n6_jet = exact_action_jet_at_state(6, *event6, points=POINTS)
n6_values, n6_vectors = np.linalg.eigh(n6_jet.hessian)
n6_branch = int(np.count_nonzero(n6_values < 0.0))
embedded_reference = embed_qm(n6_vectors[:, n6_branch], 6, ORDER)
embedded_reference /= np.linalg.norm(embedded_reference)
center_event_jet = exact_action_jet_at_state(ORDER, *event, points=POINTS)
center_values, center_vectors = np.linalg.eigh(center_event_jet.hessian)
center_branch = int(np.argmax(np.abs(center_vectors.T @ embedded_reference)))
branch_reference = center_vectors[:, center_branch]


def ordered_lambda(state):
    q, v, m = state[:qdim], state[qdim:2 * qdim], state[2 * qdim:]
    values, vectors = np.linalg.eigh(
        exact_action_jet_at_state(ORDER, q, v, m, points=POINTS).hessian
    )
    index = int(np.argmax(np.abs(vectors.T @ branch_reference)))
    return float(values[index])


base_center = np.concatenate((*event, *child))

# Normalize the retained ordered-event scalar by its own action-coordinate dual norm.
ordered_gradient = np.empty(sdim)
ordered_step = STEPS[1]
for column in range(sdim):
    delta = np.zeros(sdim)
    delta[column] = ordered_step / state_weights[column]
    ordered_gradient[column] = (
        ordered_lambda(base_center[:sdim] + delta)
        - ordered_lambda(base_center[:sdim] - delta)
    ) / (2.0 * ordered_step)
ordered_scale = float(np.linalg.norm(ordered_gradient))


def rows(joint):
    event_state = joint[:sdim]
    child_state = joint[sdim:]
    eq, ev, em = event_state[:qdim], event_state[qdim:2 * qdim], event_state[2 * qdim:]
    cq, cv, cm = child_state[:qdim], child_state[qdim:2 * qdim], child_state[2 * qdim:]
    e_constraints = constraint_residual(ORDER, eq, ev, em, points=POINTS)
    e_rows = np.concatenate((
        e_constraints[:mdim] / m_weights,
        e_constraints[mdim:],
        [ordered_lambda(event_state) / ordered_scale],
    ))
    boundary_rows = np.concatenate((
        trace @ (cq - eq),
        [_attachment_coordinates_at_order(ORDER, cq)[1]
         - _attachment_coordinates_at_order(ORDER, eq)[1]],
    ))
    c_constraints = constraint_residual(ORDER, cq, cv, cm, points=POINTS)
    momentum = (
        _canonical_pair_at_order(ORDER, cq, cv, cm, points=POINTS)[0]
        - _canonical_pair_at_order(ORDER, eq, ev, em, points=POINTS)[0]
    )
    c_rows = np.concatenate((
        boundary_inverse_sqrt @ boundary_rows,
        c_constraints[:mdim] / m_weights,
        c_constraints[mdim:],
        momentum_sqrt @ momentum,
    ))
    return np.concatenate((e_rows, c_rows))


if CHECKPOINT.exists():
    checkpoint_payload = np.load(CHECKPOINT)
    center = np.asarray(checkpoint_payload["state"], dtype=float)
    if "branch_reference" in checkpoint_payload.files:
        branch_reference = np.asarray(
            checkpoint_payload["branch_reference"], dtype=float
        )
    center_source = "REFRESHED_FROM_PREVIOUS_EXACT_DESCENT_CHECKPOINT"
else:
    center = base_center.copy()
    center_source = "ZERO_PADDED_REPAIRED_N6_ANCHOR"

# Transport the already-selected ordered event eigenline to the accepted
# chord center before taking its local paired slopes.  Comparing every local
# perturbation directly with the original zero-padded N6 vector can swap two
# nearby eigenlines after a long accepted chord even though the continued
# physical branch itself remains simple.
center_event_state = center[:sdim]
center_eq = center_event_state[:qdim]
center_ev = center_event_state[qdim:2 * qdim]
center_em = center_event_state[2 * qdim:]
transport_values, transport_vectors = np.linalg.eigh(
    exact_action_jet_at_state(
        ORDER, center_eq, center_ev, center_em, points=POINTS
    ).hessian
)
transport_branch = int(np.argmax(np.abs(
    transport_vectors.T @ branch_reference
)))
branch_reference = transport_vectors[:, transport_branch]
transport_neighbor_gap = min(
    float(transport_values[transport_branch] - transport_values[transport_branch - 1])
    if transport_branch > 0 else np.inf,
    float(transport_values[transport_branch + 1] - transport_values[transport_branch])
    if transport_branch + 1 < transport_values.size else np.inf,
)
center_rows = rows(center)


def jacobian(step):
    matrix = np.empty((center_rows.size, center.size))
    for column in range(center.size):
        delta = np.zeros(center.size)
        delta[column] = step / joint_weights[column]
        matrix[:, column] = (rows(center + delta) - rows(center - delta)) / (2.0 * step)
    return matrix


j_full = jacobian(STEPS[0])
j_half = jacobian(STEPS[1])
j = (4.0 * j_half - j_full) / 3.0

e_len = 2 * ORDER + 2
c0 = e_len
low_rows = (
    list(range(LOW))
    + list(range(ORDER, ORDER + LOW))
    + [2 * ORDER, 2 * ORDER + 1]
    + list(range(c0, c0 + 4))
    + list(range(c0 + 4, c0 + 4 + LOW))
    + list(range(c0 + 4 + ORDER, c0 + 4 + ORDER + LOW))
    + [c0 + 4 + 2 * ORDER]
    + list(range(c0 + 4 + 2 * ORDER + 1, c0 + 4 + 2 * ORDER + 3))
)
high_rows = [index for index in range(center_rows.size) if index not in set(low_rows)]


def low_state_indices(order, low):
    q = [0]
    for family in range(3):
        q.extend(range(1 + family * order, 1 + family * order + low))
    v = [qdim + index for index in q]
    m = list(range(2 * qdim, 2 * qdim + low))
    m += list(range(2 * qdim + order, 2 * qdim + order + low))
    return q + v + m


low_one = low_state_indices(ORDER, LOW)
low_columns = low_one + [sdim + index for index in low_one]
high_columns = [index for index in range(center.size) if index not in set(low_columns)]

jll = j[np.ix_(low_rows, low_columns)]
jlh = j[np.ix_(low_rows, high_columns)]
jhl = j[np.ix_(high_rows, low_columns)]
jhh = j[np.ix_(high_rows, high_columns)]
r_low = center_rows[low_rows]
r_high = center_rows[high_rows]

uh, sh, vht = np.linalg.svd(jhh, full_matrices=False)
jhh_right = vht.T @ np.diag(1.0 / sh) @ uh.T
feedback = jlh @ jhh_right @ jhl
source_feedback = jlh @ jhh_right @ r_high

u0, s0, vh0 = np.linalg.svd(jll, full_matrices=False)
v0 = vh0.T
hard_u = u0[:, :-1]
soft_u = u0[:, -1:]
hard_v = v0[:, :-1]
soft_v = v0[:, -1:]


def scalar_data(t):
    schur = jll - t * feedback
    reduced_schur = u0.T @ schur @ v0
    source = r_low - t * source_feedback
    a = hard_u.T @ schur @ hard_v
    b = hard_u.T @ schur @ soft_v
    c = soft_u.T @ schur @ hard_v
    d = float((soft_u.T @ schur @ soft_v).item())
    rh = hard_u.T @ source
    rs = float((soft_u.T @ source).item())
    a_inverse_b = np.linalg.solve(a, b)
    a_inverse_r = np.linalg.solve(a, rh)
    denominator = float(d - (c @ a_inverse_b).item())
    compatibility = float(rs - (c @ a_inverse_r).item())
    return (
        denominator,
        compatibility,
        float(np.linalg.svd(a, compute_uv=False)[-1]),
        float(np.linalg.svd(schur, compute_uv=False)[-1]),
        float(np.linalg.svd(reduced_schur, compute_uv=False)[-1]),
    )


grid = np.linspace(0.0, 1.0, 2001)
data = np.asarray([scalar_data(float(t)) for t in grid])
imin = int(np.argmin(np.abs(data[:, 0])))
ismin = int(np.argmin(data[:, 3]))
irsmin = int(np.argmin(data[:, 4]))


def enclose_affine_schur_interval(left, right):
    """Norm-enclose the fixed-frame affine Schur reduction on [left,right]."""

    midpoint = 0.5 * (left + right)
    radius = 0.5 * (right - left)
    schur = jll - midpoint * feedback
    reduced_schur = u0.T @ schur @ v0
    a = hard_u.T @ schur @ hard_v
    b = hard_u.T @ schur @ soft_v
    c = soft_u.T @ schur @ hard_v
    d = float((soft_u.T @ schur @ soft_v).item())
    a_prime = -(hard_u.T @ feedback @ hard_v)
    b_prime = -(hard_u.T @ feedback @ soft_v)
    c_prime = -(soft_u.T @ feedback @ hard_v)
    d_prime = -float((soft_u.T @ feedback @ soft_v).item())
    a_inverse = np.linalg.inv(a)
    hard_inverse_norm = float(np.linalg.norm(a_inverse, ord=2))
    hard_neumann = radius * float(np.linalg.norm(
        a_prime @ a_inverse, ord=2
    ))
    hard_gap = (1.0 - hard_neumann) / hard_inverse_norm
    reduced_inverse = np.linalg.inv(reduced_schur)
    reduced_inverse_norm = float(np.linalg.norm(reduced_inverse, ord=2))
    reduced_prime = -(u0.T @ feedback @ v0)
    reduced_neumann = radius * float(np.linalg.norm(
        reduced_prime @ reduced_inverse, ord=2
    ))
    full_gap = (1.0 - reduced_neumann) / reduced_inverse_norm
    if hard_gap <= 0.0:
        return {
            "left": left, "right": right, "hard_gap_lower": hard_gap,
            "reduced_full_gap_lower": full_gap,
            "soft_denominator_lower": -np.inf,
        }
    a_inverse_b = np.linalg.solve(a, b)
    denominator = float(d - (c @ a_inverse_b).item())
    b_bound = float(np.linalg.norm(b) + radius * np.linalg.norm(b_prime))
    c_bound = float(np.linalg.norm(c) + radius * np.linalg.norm(c_prime))
    derivative_bound = (
        abs(d_prime)
        + float(np.linalg.norm(c_prime)) * b_bound / hard_gap
        + c_bound * float(np.linalg.norm(a_prime, ord=2)) * b_bound / hard_gap**2
        + c_bound * float(np.linalg.norm(b_prime)) / hard_gap
    )
    derivative_denominator_lower = (
        abs(denominator) - derivative_bound * radius
    )
    # In the orthonormal 33-dimensional normal section, the bottom-right
    # block of reduced_schur^{-1} is denominator^{-1}.  Hence its minimum
    # singular value is also a rigorous (and much sharper) denominator bound.
    denominator_lower = max(
        derivative_denominator_lower, full_gap
    )
    # Round all asserted lower bounds outward by one binary64 ulp.
    return {
        "left": left,
        "right": right,
        "hard_gap_lower": float(np.nextafter(hard_gap, -np.inf)),
        "reduced_full_gap_lower": float(np.nextafter(full_gap, -np.inf)),
        "hard_Neumann_factor_upper": float(np.nextafter(
            hard_neumann, np.inf
        )),
        "reduced_full_Neumann_factor_upper": float(np.nextafter(
            reduced_neumann, np.inf
        )),
        "soft_denominator_midpoint": denominator,
        "soft_derivative_upper": float(np.nextafter(derivative_bound, np.inf)),
        "soft_derivative_route_lower": float(np.nextafter(
            derivative_denominator_lower, -np.inf
        )),
        "soft_denominator_lower": float(np.nextafter(denominator_lower, -np.inf)),
        "soft_lower_bound_uses_full_schur_inverse_identity": bool(
            full_gap >= derivative_denominator_lower
        ),
    }


def affine_schur_interval_cover(max_depth=18):
    pending = [(0.0, 1.0, 0)]
    accepted = []
    rejected = []
    while pending:
        left, right, depth = pending.pop()
        enclosure = enclose_affine_schur_interval(left, right)
        if (
            enclosure["hard_gap_lower"] > 0.0
            and enclosure["reduced_full_gap_lower"] > 0.0
            and enclosure["soft_denominator_lower"] > 0.0
        ):
            accepted.append(enclosure)
        elif depth < max_depth:
            midpoint = 0.5 * (left + right)
            pending.append((midpoint, right, depth + 1))
            pending.append((left, midpoint, depth + 1))
        else:
            rejected.append(enclosure)
    accepted.sort(key=lambda row: row["left"])
    return accepted, rejected


affine_cover, affine_rejected = affine_schur_interval_cover()
affine_cover_digest = hashlib.sha256(
    json.dumps(affine_cover, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()

# One full minimum-norm Schur correction at t=1, evaluated by the unchanged rows.
schur1 = jll - feedback
effective1 = r_low - source_feedback
delta_low = -np.linalg.pinv(schur1, rcond=1.0e-12) @ effective1
delta_high = -jhh_right @ (r_high + jhl @ delta_low)
delta = np.zeros(center.size)
delta[low_columns] = delta_low
delta[high_columns] = delta_high
trial = center + delta / joint_weights
trial_rows = rows(trial)
eq = trial[:qdim]
em = trial[2 * qdim:sdim]
cq = trial[sdim:sdim + qdim]
cm = trial[sdim + 2 * qdim:]
line_trials = []
for factor in (1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625):
    line_state = center + factor * delta / joint_weights
    line_rows = rows(line_state)
    line_trials.append({
        "factor": factor,
        "action_norm": float(factor * np.linalg.norm(delta)),
        "exact_norm": float(np.linalg.norm(line_rows)),
        "exact_low_norm": float(np.linalg.norm(line_rows[low_rows])),
        "exact_high_norm": float(np.linalg.norm(line_rows[high_rows])),
    })
direction = delta / np.linalg.norm(delta)
directional_curvature = []
for radius in (1.0e-3, 5.0e-4):
    plus = rows(center + radius * direction / joint_weights)
    minus = rows(center - radius * direction / joint_weights)
    value = (plus - 2.0 * center_rows + minus) / radius**2
    directional_curvature.append({
        "radius": radius,
        "second_difference_norm": float(np.linalg.norm(value)),
    })

# Continue only the unchanged exact joint residual.  The paired Richardson
# matrix seeds a chord/Broyden proposal; exact total merit and eta decide every
# accepted state.
x = np.zeros(center.size)
current_rows = center_rows.copy()
proposal_jacobian = j.copy()
continuation = []
current_state = center.copy()
for iteration in range(PROPOSAL_STEPS):
    correction = np.linalg.lstsq(
        proposal_jacobian, -current_rows, rcond=1.0e-12
    )[0]
    candidates = []
    for factor in (
        1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125,
        0.015625, 0.0078125, 0.00390625,
    ):
        trial_x = x + factor * correction
        trial_state = center + trial_x / joint_weights
        exact = rows(trial_state)
        candidates.append((float(np.linalg.norm(exact)), factor, trial_x, exact))
    best_norm, factor, next_x, next_rows = min(candidates, key=lambda item: item[0])
    current_norm = float(np.linalg.norm(current_rows))
    if not best_norm < current_norm:
        continuation.append({
            "iteration": iteration,
            "accepted": False,
            "current_norm": current_norm,
            "best_trial_norm": best_norm,
        })
        break
    step = next_x - x
    row_step = next_rows - current_rows
    defect = row_step - proposal_jacobian @ step
    proposal_jacobian += np.outer(defect, step) / float(step @ step)
    x = next_x
    current_rows = next_rows
    current_state = center + x / joint_weights
    event_eta = _eta_legendre_minimum(
        ORDER,
        current_state[:qdim],
        current_state[2 * qdim:sdim],
        points=2000,
    )["minimum"]
    child_eta = _eta_legendre_minimum(
        ORDER,
        current_state[sdim:sdim + qdim],
        current_state[sdim + 2 * qdim:],
        points=2000,
    )["minimum"]
    continuation.append({
        "iteration": iteration,
        "accepted": True,
        "factor": factor,
        "exact_norm_before": current_norm,
        "exact_norm_after": best_norm,
        "cumulative_action_norm": float(np.linalg.norm(x)),
        "event_eta": event_eta,
        "child_eta": child_eta,
        "proposal_smallest_singular": float(
            np.linalg.svd(proposal_jacobian, compute_uv=False)[-1]
        ),
    })
    if best_norm < 1.0e-9:
        break
np.savez_compressed(
    CHECKPOINT, state=current_state, branch_reference=branch_reference
)

out = {
    "order": ORDER,
    "points": POINTS,
    "center_source": center_source,
    "proposal_steps_requested": PROPOSAL_STEPS,
    "center_rows": int(center_rows.size),
    "center_norm": float(np.linalg.norm(center_rows)),
    "center_low_norm": float(np.linalg.norm(r_low)),
    "center_high_norm": float(np.linalg.norm(r_high)),
    "ordered_center_lambda": ordered_lambda(center[:sdim]),
    "ordered_center_neighbor_gap": transport_neighbor_gap,
    "ordered_scale": ordered_scale,
    "jacobian_full_to_half_norm": float(np.linalg.norm(j_half - j_full, ord=2)),
    "jacobian_richardson_to_half_norm": float(np.linalg.norm(j - j_half, ord=2)),
    "jhh_singular_values": sh.tolist(),
    "jhh_right_inverse_defect": float(np.linalg.norm(jhh @ jhh_right - np.eye(len(high_rows)), ord=2)),
    "jll_singular_values": s0.tolist(),
    "minimum_abs_soft_denominator": float(abs(data[imin, 0])),
    "minimum_abs_soft_denominator_t": float(grid[imin]),
    "soft_source_at_minimum": float(data[imin, 1]),
    "minimum_hard_singular": float(np.min(data[:, 2])),
    "minimum_full_schur_singular": float(data[ismin, 3]),
    "minimum_full_schur_singular_t": float(grid[ismin]),
    "minimum_reduced_normal_section_singular": float(data[irsmin, 4]),
    "minimum_reduced_normal_section_singular_t": float(grid[irsmin]),
    "affine_schur_interval_cover": {
        "accepted_interval_count": len(affine_cover),
        "rejected_interval_count": len(affine_rejected),
        "minimum_certified_hard_gap": min(
            row["hard_gap_lower"] for row in affine_cover
        ) if affine_cover else None,
        "minimum_certified_full_gap": min(
            row["reduced_full_gap_lower"] for row in affine_cover
        ) if affine_cover else None,
        "minimum_certified_soft_denominator": min(
            row["soft_denominator_lower"] for row in affine_cover
        ) if affine_cover else None,
        "maximum_interval_width": max(
            row["right"] - row["left"] for row in affine_cover
        ) if affine_cover else None,
        "first_interval": affine_cover[0] if affine_cover else None,
        "last_interval": affine_cover[-1] if affine_cover else None,
        "cover_sha256": affine_cover_digest,
        "scope": "FIXED_PAIRED_RICHARDSON_LINEARIZATION_ONLY",
    },
    "endpoint_data": {"t0": data[0].tolist(), "t1": data[-1].tolist()},
    "correction_action_norm": float(np.linalg.norm(delta)),
    "trial_exact_norm": float(np.linalg.norm(trial_rows)),
    "trial_exact_high_norm": float(np.linalg.norm(trial_rows[high_rows])),
    "trial_event_eta": _eta_legendre_minimum(ORDER, eq, em, points=2000)["minimum"],
    "trial_child_eta": _eta_legendre_minimum(ORDER, cq, cm, points=2000)["minimum"],
    "line_trials": line_trials,
    "directional_curvature": directional_curvature,
    "exact_merit_continuation": continuation,
    "continuation_final_norm": float(np.linalg.norm(current_rows)),
    "continuation_checkpoint": str(CHECKPOINT),
    "certification_status": {
        "exact_joint_weak_root_landed": bool(
            np.linalg.norm(current_rows) < 1.0e-9
        ),
        "fixed_paired_linear_schur_homotopy_enclosed": bool(
            affine_cover and not affine_rejected
        ),
        "nonlinear_segment_radii_polynomials_certified": False,
        "eta_event_Dirac_persistence_ball_transfer_certified": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "first_rigorous_certification_obstruction": (
            "ACTION_ANALYTIC_FOURTH_VARIATION_AND_BORDERED_LIFT_"
            "INVERSE_MAJORANT_ON_EACH_FINITE_CHORD_BALL,_INCLUDING_"
            "THE_ORDERED_EVENT_EIGENPROJECTOR,_STATE_DEPENDENT_"
            "CANONICAL_MOMENTUM_LIFT,_EXISTING_QUADRATURE_"
            "CONSISTENCY_DEFECT,_AND_ETA_DIRAC_EVENT_PERSISTENCE_"
            "NEIGHBORHOOD_LIPSCHITZ_RADII"
        ),
        "paired_slopes_are_proposal_curvature_only": True,
        "new_physics_equation_gate_constraint_or_selector": False,
    },
}
RESULT.write_text(json.dumps(out, indent=2), encoding="utf-8")
checkpoint_payload = np.load(CHECKPOINT)
checkpoint_state = np.asarray(checkpoint_payload["state"], dtype=float)
checkpoint_branch = np.asarray(
    checkpoint_payload["branch_reference"], dtype=float
)
artifact_payload = {
    "artifact": "BHSM_N6_N12_JOINT_SCHUR_CHORD_COVER",
    "classification": (
        "UNCHANGED_JOINT_WEAK_RESIDUAL_CHORD_CONTINUATION_AND_"
        "FIXED_LINEAR_SCHUR_INTERVAL_COVER;_NONLINEAR_ACTION_NORM_"
        "RADII_CERTIFICATE_REMAINS_FAIL_CLOSED"
    ),
    "finite_anchor_history": {
        "zero_padded_repaired_N6_in_N12_exact_joint_norm": (
            0.3322528867427651
        ),
        "first_refreshed_center_exact_joint_norm": 0.04485300994713792,
        "second_refreshed_center_exact_joint_norm": 3.325651595441319e-5,
        "linear_bridge_lower_bounds_at_zero_padded_anchor": {
            "hard_gap": 0.00994932347,
            "full_Schur_gap": 0.00371468430,
            "soft_denominator": 0.00559736955,
        },
        "one_N6_centered_ball_classified_as_retained_action_obstruction": (
            False
        ),
        "one_N6_centered_ball_classification": "LOCAL_BASIN_FAILURE_ONLY",
    },
    "latest_probe": out,
    "latest_checkpoint_binary64_hex": {
        "event": [float(value).hex() for value in checkpoint_state[:sdim]],
        "child": [float(value).hex() for value in checkpoint_state[sdim:]],
        "transported_ordered_event_eigenline": [
            float(value).hex() for value in checkpoint_branch
        ],
    },
    "measurement_center_binary64_hex": {
        "event": [float(value).hex() for value in center[:sdim]],
        "child": [float(value).hex() for value in center[sdim:]],
        "transported_ordered_event_eigenline": [
            float(value).hex() for value in branch_reference
        ],
    },
    "unchanged_joint_weak_residual_used": True,
    "paired_slopes_promoted_as_physics": False,
    "higher_N_complete_child_promoted": False,
    "frozen_predictions_touched": False,
    "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
    "FULL_BHSM_COMPLETE": False,
}
ARTIFACT.write_text(
    json.dumps(artifact_payload, sort_keys=True, separators=(",", ":"))
    + "\n",
    encoding="utf-8",
)
print(json.dumps(out, indent=2))
