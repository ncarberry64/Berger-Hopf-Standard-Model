"""Probe one safeguarded matrix-free residual-reduction direction."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    kkt_variable_scales,
    pack_reduced,
    scaled_kkt_residual,
)


def main() -> None:
    artifact = json.loads(Path(
        "artifacts/BHSM_aether_n3_replacement_global_kkt_v16_11.json"
    ).read_text(encoding="utf-8"))
    seed = artifact["strictly_interior_N3_seed"]
    raw_seed = pack_reduced(
        np.asarray(seed["coordinates"]),
        np.asarray(seed["multipliers"]),
        float(seed["period"]),
        0.0,
    )
    y0 = raw_seed * kkt_variable_scales()
    r0 = scaled_kkt_residual(y0)
    p = -r0 / np.linalg.norm(r0)
    rejected_probe_lengths = []
    for probe_length in (3.0e-5, 1.0e-5, 3.0e-6, 1.0e-6):
        try:
            r_plus = scaled_kkt_residual(y0 + probe_length * p)
            r_minus = scaled_kkt_residual(y0 - probe_length * p)
            break
        except (FloatingPointError, ValueError, np.linalg.LinAlgError) as exc:
            rejected_probe_lengths.append({
                "probe_length": probe_length,
                "exception": type(exc).__name__,
            })
    else:
        raise RuntimeError("no admissible central Jacobian probe")
    jp = (r_plus - r_minus) / (2.0 * probe_length)
    first_denominator = float(jp @ jp)
    first_alpha = (
        float(-(r0 @ jp) / first_denominator)
        if first_denominator > 0.0 else 0.0
    )
    # J is the symmetric KKT Jacobian.  Because p=-R/||R||, Jp is
    # proportional to -J^T R, the residual-norm descent direction.
    descent = jp / np.linalg.norm(jp)
    rejected_descent_probes = []
    for descent_probe_length in (3.0e-5, 1.0e-5, 3.0e-6, 1.0e-6):
        try:
            rd_plus = scaled_kkt_residual(
                y0 + descent_probe_length * descent
            )
            rd_minus = scaled_kkt_residual(
                y0 - descent_probe_length * descent
            )
            break
        except (FloatingPointError, ValueError, np.linalg.LinAlgError) as exc:
            rejected_descent_probes.append({
                "probe_length": descent_probe_length,
                "exception": type(exc).__name__,
            })
    else:
        raise RuntimeError("no admissible residual-descent Jacobian probe")
    jd = (rd_plus - rd_minus) / (2.0 * descent_probe_length)
    denominator = float(jd @ jd)
    alpha = float(-(r0 @ jd) / denominator) if denominator > 0.0 else 0.0
    candidates = []
    for factor in (1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125):
        trial_alpha = factor * alpha
        if trial_alpha <= 0.0:
            continue
        try:
            residual = scaled_kkt_residual(y0 + trial_alpha * p)
        except (FloatingPointError, ValueError, np.linalg.LinAlgError) as exc:
            candidates.append({
                "factor": factor,
                "alpha": trial_alpha,
                "accepted_domain": False,
                "exception": type(exc).__name__,
            })
            continue
        candidates.append({
            "factor": factor,
            "alpha": trial_alpha,
            "accepted_domain": True,
            "residual_norm": float(np.linalg.norm(residual)),
            "event_residual": float(residual[-1]),
            "maximum_component": float(np.max(np.abs(residual))),
        })
    print(json.dumps({
        "seed_residual_norm": float(np.linalg.norm(r0)),
        "seed_event_residual": float(r0[-1]),
        "probe_length": probe_length,
        "rejected_probe_lengths": rejected_probe_lengths,
        "directional_derivative_norm": float(np.linalg.norm(jp)),
        "negative_residual_linear_alpha": first_alpha,
        "descent_probe_length": descent_probe_length,
        "rejected_descent_probe_lengths": rejected_descent_probes,
        "descent_directional_derivative_norm": float(np.linalg.norm(jd)),
        "linear_minimum_alpha": alpha,
        "candidates": candidates,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
