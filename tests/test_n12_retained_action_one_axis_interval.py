import numpy as np

from bhsm.interface.aether_retained_action_one_axis_interval import (
    retained_action_one_axis_interval,
)
from bhsm.interface.aether_retained_action_tensor_interval import (
    retained_action_tensor_interval,
)


def test_one_axis_interval_overlaps_general_tensor_rows() -> None:
    base = (
        __import__("pathlib").Path(__file__).resolve().parents[1]
        / "artifacts" / "flagship_integration"
    )
    with np.load(base / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.npz") as data:
        state = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
        psi = np.asarray(data["selected_vector"], dtype=float)
    qdim = 37
    total = 98
    radius = 5.5104723095444935e-11
    state_lo = np.nextafter(state - radius / weights, -np.inf)
    state_hi = np.nextafter(state + radius / weights, np.inf)
    eye = np.eye(total)
    basis = eye[86]
    embed = np.zeros((total, psi.size))
    embed[qdim:] = np.diag(weights[qdim:])
    p = embed @ psi
    spread = np.abs(embed @ np.ones(psi.size)) * 6.0e-9
    p_box = (
        np.nextafter(p - spread, -np.inf),
        np.nextafter(p + spread, np.inf),
    )
    cases = [
        ([basis, eye, p], [None, None, p_box], 1),
        ([basis, eye, p, p], [None, None, p_box, p_box], 1),
        ([basis, eye, p, p, p], [None, None, p_box, p_box, p_box], 1),
    ]
    for directions, bounds, output_index in cases:
        compact = retained_action_one_axis_interval(
            12, state_lo, state_hi, directions, bounds,
            output_index=output_index, points=96,
        )
        tensor_directions = [
            direction if bound is None else bound
            for direction, bound in zip(directions, bounds)
        ]
        reference = retained_action_tensor_interval(
            12, state_lo, state_hi, tensor_directions, points=96
        )
        compact_lo = np.asarray(compact.lo, dtype=float)
        compact_hi = np.asarray(compact.hi, dtype=float)
        reference_lo = np.asarray(reference.lo, dtype=float)
        reference_hi = np.asarray(reference.hi, dtype=float)
        assert compact_lo.shape == (total,)
        assert np.all(np.isfinite(compact_lo))
        assert np.all(np.isfinite(compact_hi))
        assert np.all(compact_lo <= compact_hi)
        assert np.all(compact_lo <= reference_hi)
        assert np.all(reference_lo <= compact_hi)
