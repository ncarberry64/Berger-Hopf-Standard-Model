"""Mixed geometry/source jets of the retained product-Dirac form.

These are derivatives of the existing finite-core action, evaluated at a
zero commuting source. They supply operator vertices; no fermion coefficient
background, occupation, or retarded exterior is selected here.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from bhsm.interface.ae3_c2_action_puzzle import (
    assemble_element_forms,
    reduced_product_dirac_hs_source_jet,
)
from bhsm.interface.aether_forward_c2_finite_core_descriptor import (
    assemble_finite_core_descriptor,
)
from bhsm.interface.aether_rank16_u1_hs_vertex_matrices_v16_01 import source_profiles


_S = np.asarray(((1.0, -1.0), (-1.0, 1.0)))
_A6 = np.asarray(((2.0, 1.0), (1.0, 2.0))) / 6.0
_C = np.diag((-1.0, 1.0))


def _assemble_jet(elements: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Assemble element jets, retaining birth and eliminating the far node."""
    diagonal = elements[:, 0, 0, :].copy()
    diagonal[1:] += elements[:-1, 1, 1, :]
    return diagonal, elements[:-1, 0, 1, :].copy()


def normalized_source_mixed_form_jets(
    *,
    log_radii: np.ndarray,
    proper_durations: np.ndarray,
    chirality: int,
    log_radius_first_jet: np.ndarray | None = None,
    proper_durations_first_jet: np.ndarray | None = None,
) -> dict[str, Any]:
    """Return K, M, V, Q and exact radius/duration/source mixed forms.

For each element, ``K=S/h+W**2*M+W*C`` and ``W=chi*1.5*exp(-x_mid)``.
The existing unit commuting source is ``W -> W+epsilon*p`` with canonical
``p=1/sqrt(T)``. At fixed source section, ``d_x V=-2*W*p*M`` and
``d_h V=2*W*p*A/6``. Optional coefficient jets include ``dp=-p*dT/(2*T)``.
Element derivatives remain separate so arbitrary node or element motions
can be contracted without equating their independent coordinates.
"""
    x = np.asarray(log_radii, dtype=float)
    h = np.asarray(proper_durations, dtype=float)
    core = assemble_finite_core_descriptor(
        log_radii=x, proper_durations=h, channel="product_Dirac",
        unit_channel_value=1.5, chirality=chirality,
    )
    duration = float(h.sum())
    tau_mid = np.cumsum(h) - 0.5 * h
    profile = np.asarray(source_profiles({
        "proper_times": tau_mid, "proper_duration": duration,
    })["constant"])
    W = np.asarray(core["element_coefficient"])
    source = reduced_product_dirac_hs_source_jet(
        proper_durations=h, base_W=W, source_profile=profile,
    )
    M = np.asarray(source["mass_elements"])
    K = _S[None] / h[:, None, None] + W[:, None, None] ** 2 * M + W[:, None, None] * _C[None]
    p = profile[:, None, None]
    w = W[:, None, None]
    elements = {
        "K": K, "M": M,
        "V": np.asarray(source["vertex_elements"]),
        "Q": np.asarray(source["contact_elements"]),
        "D_x_mid_K": np.asarray(core["D_x_mid_K_elements"]),
        "D_h_K": np.asarray(core["D_h_K_elements"]),
        "D_h_M": np.asarray(core["D_h_M_elements"]),
        "D_x_mid_V": -2.0 * w * p * M,
        "D_h_V": 2.0 * w * p * _A6[None],
        "D_p_V": 2.0 * w * M + _C[None],
        "D_h_Q": 2.0 * p**2 * _A6[None],
        "D_p_Q": 4.0 * p * M,
    }
    arrays: dict[str, np.ndarray] = {
        "source_profile": profile, "base_W": W,
        **{f"{name}_elements": values for name, values in elements.items()},
    }
    for name in ("K", "M", "V", "Q"):
        assembled = assemble_element_forms(elements[name])
        arrays[f"{name}_diagonal"] = assembled["diagonal"]
        arrays[f"{name}_off_diagonal"] = assembled["off_diagonal"]
    inherited_residual = max(
        float(np.linalg.norm(arrays[f"{name}_{part}"] - core[f"{name}_{part}"]))
        for name in ("K", "M") for part in ("diagonal", "off_diagonal")
    )

    if (log_radius_first_jet is None) != (proper_durations_first_jet is None):
        raise ValueError("both radius and element-duration jets are required")
    direction_count = 0
    normalization_jet_residual = 0.0
    if log_radius_first_jet is not None:
        dx = np.asarray(log_radius_first_jet, dtype=float)
        dh = np.asarray(proper_durations_first_jet, dtype=float)
        if (dx.ndim != 2 or dx.shape[0] != x.size
                or dh.shape != (h.size, dx.shape[1])
                or not np.all(np.isfinite(dx)) or not np.all(np.isfinite(dh))):
            raise ValueError("finite node radius and element-duration jets on this coefficient path required")
        direction_count = dx.shape[1]
        dx_mid = 0.5 * (dx[:-1] + dx[1:])
        dT = dh.sum(axis=0)
        dp = -profile[:, None] * dT[None, :] / (2.0 * duration)
        arrays["source_profile_first_jet"] = dp
        arrays["proper_duration_first_jet"] = dT

        def motion(partial: np.ndarray, direction: np.ndarray) -> np.ndarray:
            return partial[..., None] * direction[:, None, None, :]

        jets = {
            "K": motion(elements["D_x_mid_K"], dx_mid) + motion(elements["D_h_K"], dh),
            "M": motion(elements["D_h_M"], dh),
            "V": (motion(elements["D_x_mid_V"], dx_mid)
                  + motion(elements["D_h_V"], dh) + motion(elements["D_p_V"], dp)),
            "Q": motion(elements["D_h_Q"], dh) + motion(elements["D_p_Q"], dp),
        }
        for name, values in jets.items():
            arrays[f"{name}_first_jet_elements"] = values
            diagonal, off = _assemble_jet(values)
            arrays[f"{name}_diagonal_first_jet"] = diagonal
            arrays[f"{name}_off_diagonal_first_jet"] = off
        normalization_motion = np.sum(dh * profile[:, None] ** 2
                                      + 2.0 * h[:, None] * profile[:, None] * dp, axis=0)
        normalization_jet_residual = float(np.max(np.abs(normalization_motion), initial=0.0))
    return {
        "arrays": arrays,
        "summary": {
            "chirality": int(chirality), "element_count": h.size,
            "retained_form_dimension": h.size, "proper_duration": duration,
            "source_normalization_residual": float(abs(h @ profile**2 - 1.0)),
            "source_normalization_first_jet_residual": normalization_jet_residual,
            "inherited_K_M_assembly_residual": inherited_residual,
            "coefficient_jet_direction_count": direction_count,
            "mixed_log_radius_source_element_frobenius_norm": float(np.linalg.norm(elements["D_x_mid_V"])),
            "mixed_duration_source_element_frobenius_norm": float(np.linalg.norm(elements["D_h_V"])),
        },
    }


def mixed_form_directional_check(log_radii: np.ndarray, proper_durations: np.ndarray) -> dict[str, Any]:
    """Check simultaneous actual-path radius, duration and source motion."""
    x = np.asarray(log_radii, dtype=float)
    h = np.asarray(proper_durations, dtype=float)
    normalized_tau = np.concatenate(([0.0], np.cumsum(h))) / h.sum()
    dx = 0.2 * np.cos(2.0 * np.pi * normalized_tau) + 0.1
    midpoint = 0.5 * (normalized_tau[:-1] + normalized_tau[1:])
    dh = h * (0.3 + 0.2 * np.sin(2.0 * np.pi * midpoint))
    rows = {}
    for chirality, name in ((1, "plus"), (-1, "minus")):
        base = normalized_source_mixed_form_jets(
            log_radii=x, proper_durations=h, chirality=chirality,
            log_radius_first_jet=dx[:, None], proper_durations_first_jet=dh[:, None],
        )["arrays"]
        step_rows = []
        for step in (1.0e-3, 5.0e-4):
            plus = normalized_source_mixed_form_jets(
                log_radii=x + step * dx, proper_durations=h + step * dh, chirality=chirality,
            )["arrays"]
            minus = normalized_source_mixed_form_jets(
                log_radii=x - step * dx, proper_durations=h - step * dh, chirality=chirality,
            )["arrays"]
            errors = {}
            for form in ("K", "M", "V", "Q"):
                difference = (plus[f"{form}_elements"] - minus[f"{form}_elements"]) / (2.0 * step)
                exact = base[f"{form}_first_jet_elements"][..., 0]
                errors[form] = float(np.linalg.norm(difference - exact) / max(np.linalg.norm(exact), np.finfo(float).tiny))
            step_rows.append({"step": step, "relative_errors": errors})
        first, second = [row["relative_errors"] for row in step_rows]
        passed = all(second[key] < 5.0e-6 and
                     (second[key] <= 0.35 * first[key] + 1.0e-9)
                     for key in ("K", "M", "V", "Q"))
        rows[name] = {"steps": step_rows, "passed": passed}
    return {
        "direction": "MATHEMATICAL_CHECK_MOTION_OF_RADIUS_DURATION_AND_CANONICAL_SOURCE;_NOT_A_NEW_PHYSICAL_BACKGROUND",
        "source_normalization_varied_in_difference": True,
        "chirality_checks": rows,
        "passed": all(row["passed"] for row in rows.values()),
    }


__all__ = ["normalized_source_mixed_form_jets", "mixed_form_directional_check"]
