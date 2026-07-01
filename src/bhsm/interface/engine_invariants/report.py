"""Build an offline, deterministic BHSM Engine invariant report."""

from __future__ import annotations

import numpy as np

from .transforms import boundary_chart_forward, boundary_chart_inverse, lorentz_boost_x, minkowski_norm_sq


def _sample_states() -> np.ndarray:
    eps = np.finfo(np.float64).eps
    return np.array(
        [
            [5.0, 3.0, 4.0, 0.0],
            [1.0, 1.0 - 8.0 * eps, 0.0, 0.0],
            [10.0, eps, -eps, np.sqrt(99.0)],
            [1.0e9 + 1.0, 1.0e9, 1.0, -1.0],
            [2.0, 0.0, 0.0, 0.0],
        ],
        dtype=np.float64,
    )


def build_engine_invariant_report() -> dict[str, object]:
    states = _sample_states()
    chart = boundary_chart_forward(states)
    restored = boundary_chart_inverse(chart)
    boosted = lorentz_boost_x(states, 0.3)
    composed = lorentz_boost_x(lorentz_boost_x(states, 0.2), -0.2)
    original_norm = minkowski_norm_sq(states)
    boosted_norm = minkowski_norm_sq(boosted)
    scale = np.maximum(1.0, np.max(np.abs(states), axis=1))
    roundtrip_error = np.max(np.abs(restored - states), axis=1) / scale
    norm_scale = np.maximum(1.0, np.abs(states[:, 0]) ** 2 + np.sum(states[:, 1:4] ** 2, axis=1))
    lorentz_error = np.abs(boosted_norm - original_norm) / norm_scale
    composition_error = np.max(np.abs(composed - states), axis=1) / scale
    tolerance = 256.0 * np.finfo(np.float64).eps
    checks = {
        "minkowski_norm_preserved": bool(np.max(lorentz_error) <= tolerance),
        "roundtrip_preserved": bool(np.max(roundtrip_error) <= tolerance),
        "inverse_transform_consistent": bool(np.allclose(restored, states, rtol=tolerance, atol=tolerance)),
        "boost_inverse_composition_consistent": bool(np.max(composition_error) <= tolerance),
        "near_null_finite": bool(np.all(np.isfinite(chart[1])) and np.isfinite(original_norm[1])),
        "large_magnitude_finite": bool(np.all(np.isfinite(chart[3]))),
        "zero_momentum_chart_defined": bool(np.all(chart[4, 2:5] == 0.0)),
    }
    return {
        "status": "ENGINE_INVARIANTS_DETERMINISTIC_OFFLINE_PASS" if all(checks.values()) else "ENGINE_INVARIANT_FAILURE",
        "scope": "four-vector coordinate transformations; not detector reconstruction",
        "checks": checks,
        "metrics": {
            "max_lorentz_relative_backward_error": float(np.max(lorentz_error)),
            "max_roundtrip_scale_aware_error": float(np.max(roundtrip_error)),
            "max_boost_inverse_composition_error": float(np.max(composition_error)),
            "tolerance": tolerance,
        },
        "sample_count": len(states),
        "claim_boundaries": [
            "engine validation does not validate BHSM particle physics",
            "no detector tracking or reconstruction is tested",
            "ROOT LorentzVector comparison remains an external-runtime check",
        ],
    }
