"""Phase 9A H_T construction from finite Dirac proxy spectra."""

from __future__ import annotations

from typing import Iterable, Mapping

import numpy as np

from constants import ALPHA_INV_LOW_ENERGY
from positivity import compensated_barrier, is_psd, psd_barrier_from_q
from spectral_gap import MU_H, heat_lift, natural_lambda2
from twisted_dirac import (
    DIRAC_PROXY_LEVEL,
    DIRAC_PROXY_LEVEL_2,
    DiracOperatorConfig,
    build_dirac_basis,
    complement_spectrum,
    dirac_squared_spectrum,
    level2_dirac_squared_spectrum,
    zero_mode_subspace,
)


def _protected_indices(zero_modes: np.ndarray) -> set[int]:
    arr = np.asarray(zero_modes)
    if arr.ndim != 2:
        raise ValueError("zero_modes must be a 2D coordinate basis")
    return set(np.where(arr.any(axis=1))[0])


def _profile_values(
    profile_term: np.ndarray | Iterable[float] | None,
    size: int,
    *,
    allow_negative_profile: bool,
) -> np.ndarray:
    if profile_term is None:
        return np.zeros(size)
    arr = np.asarray(profile_term, dtype=float)
    if arr.ndim == 1:
        if arr.shape[0] != size:
            raise ValueError("profile vector size does not match spectrum")
        if np.any(arr < 0) and not allow_negative_profile:
            raise ValueError("negative profile terms require allow_negative_profile=True")
        return arr
    if arr.ndim == 2:
        if arr.shape != (size, size):
            raise ValueError("profile matrix size does not match spectrum")
        if not is_psd(arr) and not allow_negative_profile:
            raise ValueError("non-PSD profile matrix requires allow_negative_profile=True")
        return np.diag(arr)
    raise ValueError("profile_term must be a vector or square matrix")


def build_ht_spectrum(
    dirac_spectrum: Iterable[Mapping[str, object]],
    lambda2: float | None,
    mu_h: float,
    profile_term: np.ndarray | Iterable[float] | None = None,
    *,
    allow_negative_profile: bool = False,
) -> np.ndarray:
    """Build H_T spectrum records by heat-lifting Dirac-squared values."""

    resolved_lambda2 = natural_lambda2() if lambda2 is None else lambda2
    if resolved_lambda2 <= 0:
        raise ValueError("lambda2 must be positive")
    if mu_h <= 0:
        raise ValueError("mu_h must be positive")
    rows = [dict(row) for row in dirac_spectrum]
    profile = _profile_values(
        profile_term,
        len(rows),
        allow_negative_profile=allow_negative_profile,
    )
    ht_rows = []
    for position, row in enumerate(rows):
        d2 = float(row["eigenvalue"])
        lifted = heat_lift(d2, resolved_lambda2, mu_h=mu_h)
        ht_rows.append(
            {
                **row,
                "dirac_squared": d2,
                "profile_term": float(profile[position]),
                "ht_eigenvalue": float(lifted + profile[position]),
                "lambda2": resolved_lambda2,
                "mu_h": mu_h,
                "model_level": DIRAC_PROXY_LEVEL,
                "theorem_complete": False,
            }
        )
    return np.array(
        sorted(ht_rows, key=lambda row: (row["ht_eigenvalue"], row["index"])),
        dtype=object,
    )


def first_complement_gap(
    ht_spectrum: Iterable[Mapping[str, object]],
    zero_modes: np.ndarray,
) -> dict[str, object]:
    """Return the first H_T spectrum row outside protected zero modes."""

    protected = _protected_indices(zero_modes)
    complement = [row for row in ht_spectrum if int(row["index"]) not in protected]
    if not complement:
        raise ValueError("empty complement spectrum")
    return min(complement, key=lambda row: (row["ht_eigenvalue"], row["index"]))


def passes_no_extra_light_gap(
    ht_spectrum: Iterable[Mapping[str, object]],
    zero_modes: np.ndarray,
    mu_h: float,
) -> bool:
    """Return whether the first complement H_T eigenvalue clears mu_h."""

    return bool(float(first_complement_gap(ht_spectrum, zero_modes)["ht_eigenvalue"]) >= mu_h)


def gap_report(
    dirac_spectrum: Iterable[Mapping[str, object]],
    zero_modes: np.ndarray,
    lambda2: float | None = None,
    mu_h: float = MU_H,
    profile_term: np.ndarray | Iterable[float] | None = None,
    *,
    allow_negative_profile: bool = False,
) -> dict[str, object]:
    """Return an auditable H_T gap report for the finite Dirac proxy."""

    ht_spectrum = build_ht_spectrum(
        dirac_spectrum,
        lambda2=lambda2,
        mu_h=mu_h,
        profile_term=profile_term,
        allow_negative_profile=allow_negative_profile,
    )
    first = first_complement_gap(ht_spectrum, zero_modes)
    return {
        "model_level": DIRAC_PROXY_LEVEL,
        "basis_size": len(list(dirac_spectrum)) if not isinstance(dirac_spectrum, np.ndarray) else len(dirac_spectrum),
        "protected_zero_modes": int(np.asarray(zero_modes).shape[1]),
        "first_complement_index": int(first["index"]),
        "first_complement_dirac_squared": float(first["dirac_squared"]),
        "first_ht_complement_gap": float(first["ht_eigenvalue"]),
        "mu_h": mu_h,
        "passes_mu_h": bool(float(first["ht_eigenvalue"]) >= mu_h),
        "theorem_complete": False,
        "limitations": (
            "DIRAC_PROXY_LEVEL_1 finite-basis scaffold only; full analytic H_T spectrum remains open."
        ),
    }


def _default_twist_params() -> dict[str, object]:
    return {
        "dirac_scale": 2.0,
        "boundary_strength": 0.05,
        "chirality_shift": 0.01,
        "hopf_shift": 0.0,
        "sector_shifts": {},
    }


def _resolve_profile_model(
    profile_model: str | Mapping[str, object] | None,
    size: int,
    zero_modes: np.ndarray,
) -> tuple[np.ndarray | None, bool, str]:
    if profile_model is None or profile_model == "zero":
        return None, False, "zero"
    if profile_model == "psd_identity":
        return psd_barrier_from_q(np.eye(size)), False, "psd_identity"
    if profile_model == "compensated_zero_shift":
        return compensated_barrier(np.eye(size), zero_modes, zero_mode_shift=1.0), False, "compensated_zero_shift"
    if profile_model == "negative_failure":
        return np.full(size, -0.01 * MU_H), True, "negative_failure"
    if isinstance(profile_model, Mapping):
        model = str(profile_model.get("model", "zero"))
        if model == "negative_failure":
            depth = float(profile_model.get("depth", 0.01))
            return np.full(size, -depth * MU_H), True, model
        if model == "psd_identity":
            strength = float(profile_model.get("strength", 1.0))
            if strength < 0:
                raise ValueError("PSD profile strength must be nonnegative")
            return psd_barrier_from_q(np.sqrt(strength) * np.eye(size)), False, model
    raise ValueError(f"unknown profile_model: {profile_model}")


def scan_twisted_dirac_robustness(
    k_max_values: Iterable[int],
    a_values: Iterable[float],
    twist_param_grid: Iterable[Mapping[str, object]] | None = None,
    sectors: Iterable[str] | Iterable[Iterable[str]] | None = None,
    include_chirality: bool = True,
    lambda2: float | None = None,
    profile_model: str | Mapping[str, object] | None = None,
) -> list[dict[str, object]]:
    """Scan DIRAC_PROXY_LEVEL_1 robustness across basis and twist choices."""

    resolved_lambda2 = natural_lambda2() if lambda2 is None else lambda2
    if resolved_lambda2 <= 0:
        raise ValueError("lambda2 must be positive")
    twist_grid = tuple(twist_param_grid or (_default_twist_params(),))
    if sectors is None:
        sector_cases: tuple[tuple[str, ...], ...] = (("lepton", "up", "down"),)
    else:
        sector_items = tuple(sectors)
        if sector_items and isinstance(sector_items[0], str):
            sector_cases = (tuple(sector_items),)  # type: ignore[arg-type]
        else:
            sector_cases = tuple(tuple(item) for item in sector_items)  # type: ignore[assignment]

    rows: list[dict[str, object]] = []
    for sector_case in sector_cases:
        for k_max in k_max_values:
            for a in a_values:
                for twist_params in twist_grid:
                    basis = build_dirac_basis(
                        k_max=k_max,
                        sectors=sector_case,
                        include_chirality=include_chirality,
                    )
                    index_count = min(3, len(basis))
                    zero_modes = zero_mode_subspace(basis, index_count=index_count)
                    spectrum = dirac_squared_spectrum(basis, a=a, twist_params=twist_params)
                    complement = complement_spectrum(spectrum, zero_modes)
                    profile, allow_negative, profile_name = _resolve_profile_model(
                        profile_model,
                        len(spectrum),
                        zero_modes,
                    )
                    report = gap_report(
                        spectrum,
                        zero_modes,
                        lambda2=resolved_lambda2,
                        mu_h=MU_H,
                        profile_term=profile,
                        allow_negative_profile=allow_negative,
                    )
                    first_mode = complement[0]["mode"] if len(complement) else None
                    rows.append(
                        {
                            "k_max": int(k_max),
                            "a": float(a),
                            "twist_params": dict(twist_params),
                            "sectors": sector_case,
                            "include_chirality": bool(include_chirality),
                            "lambda2": resolved_lambda2,
                            "profile_model": profile_name,
                            "basis_size": report["basis_size"],
                            "zero_mode_count": report["protected_zero_modes"],
                            "first_complement_d": report["first_complement_dirac_squared"],
                            "first_complement_mode": first_mode,
                            "first_ht_gap": report["first_ht_complement_gap"],
                            "margin": float(report["first_ht_complement_gap"]) - MU_H,
                            "passes": bool(report["passes_mu_h"]),
                            "theorem_complete": False,
                            "model_level": DIRAC_PROXY_LEVEL,
                        }
                    )
    return rows


def default_twist_parameter_grid() -> tuple[dict[str, object], ...]:
    """Return baseline and nearby perturbations for Phase 9B scans."""

    baseline = _default_twist_params()
    low_scale = dict(baseline, dirac_scale=1.8)
    stronger_boundary = dict(baseline, boundary_strength=0.08)
    chirality_perturbed = dict(baseline, chirality_shift=0.02)
    return (baseline, low_scale, stronger_boundary, chirality_perturbed)


def alpha_scaled_a() -> float:
    """Return alpha^{-1}/(12 pi^2) for robustness scans."""

    from math import pi

    return ALPHA_INV_LOW_ENERGY / (12.0 * pi**2)


def build_ht_from_level2_dirac(
    config: DiracOperatorConfig,
    lambda2: float | None,
    profile_operator: np.ndarray | Iterable[float] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Build H_T from the Level 2 finite-basis Dirac matrix spectrum."""

    basis = build_dirac_basis(
        k_max=config.k_max,
        sectors=config.sectors,
        include_chirality=config.include_chirality,
    )
    zero_count = int(config.boundary_params.get("zero_mode_count", 3))
    zero_modes = zero_mode_subspace(basis, index_count=zero_count)
    spectrum = level2_dirac_squared_spectrum(config)
    ht_spectrum = build_ht_spectrum(
        spectrum,
        lambda2=lambda2,
        mu_h=MU_H,
        profile_term=profile_operator,
        allow_negative_profile=False,
    )
    for row in ht_spectrum:
        row["model_level"] = DIRAC_PROXY_LEVEL_2
    return ht_spectrum, zero_modes


def level2_ht_gap_report(
    config: DiracOperatorConfig,
    lambda2: float | None,
    profile_operator: np.ndarray | Iterable[float] | None = None,
) -> dict[str, object]:
    """Return an auditable Level 2 H_T gap report."""

    ht_spectrum, zero_modes = build_ht_from_level2_dirac(config, lambda2, profile_operator)
    first = first_complement_gap(ht_spectrum, zero_modes)
    basis = build_dirac_basis(
        k_max=config.k_max,
        sectors=config.sectors,
        include_chirality=config.include_chirality,
    )
    return {
        "model_level": DIRAC_PROXY_LEVEL_2,
        "basis_size": len(basis),
        "zero_mode_count": int(zero_modes.shape[1]),
        "first_complement_eigenvalue": float(first["dirac_squared"]),
        "first_ht_complement_gap": float(first["ht_eigenvalue"]),
        "margin": float(first["ht_eigenvalue"]) - MU_H,
        "passes": bool(float(first["ht_eigenvalue"]) >= MU_H),
        "theorem_complete": False,
        "limitations": "Level 2 finite-basis matrix scaffold only; full analytic H_T spectrum remains open.",
    }


def default_level2_config(
    k_max: int = 4,
    a: float = 1.0,
    sectors: tuple[str, ...] = ("lepton", "up", "down"),
) -> DiracOperatorConfig:
    """Return a baseline Level 2 operator config."""

    return DiracOperatorConfig(
        a=a,
        k_max=k_max,
        sectors=sectors,
        twist_params={
            "dirac_scale": 2.0,
            "spin_connection_strength": 0.05,
            "hopf_twist_strength": 0.03,
            "chirality_strength": 0.02,
        },
        boundary_params={
            "boundary_strength": 0.04,
            "sector_coupling": 0.01,
            "offdiag_boundary_coupling": 0.005,
            "complement_floor": 1.1,
            "zero_mode_count": 3,
        },
        include_chirality=True,
        operator_level=DIRAC_PROXY_LEVEL_2,
    )


def default_level2_perturbations() -> tuple[dict[str, dict[str, float]], ...]:
    """Return baseline and nearby Level 2 coupling perturbations."""

    return (
        {"twist_params": {}, "boundary_params": {}},
        {"twist_params": {"spin_connection_strength": 0.07}, "boundary_params": {}},
        {"twist_params": {}, "boundary_params": {"sector_coupling": 0.02}},
    )


def scan_level2_ht_robustness(
    k_max_values: Iterable[int],
    a_values: Iterable[float],
    perturbations: Iterable[Mapping[str, Mapping[str, float]]] | None = None,
    lambda2: float | None = None,
) -> list[dict[str, object]]:
    """Scan Level 2 H_T gap robustness across basis and coupling choices."""

    rows: list[dict[str, object]] = []
    for k_max in k_max_values:
        for a in a_values:
            for perturbation in tuple(perturbations or default_level2_perturbations()):
                base = default_level2_config(k_max=k_max, a=a)
                twist = dict(base.twist_params)
                twist.update(dict(perturbation.get("twist_params", {})))
                boundary = dict(base.boundary_params)
                boundary.update(dict(perturbation.get("boundary_params", {})))
                config = DiracOperatorConfig(
                    a=base.a,
                    k_max=base.k_max,
                    sectors=base.sectors,
                    twist_params=twist,
                    boundary_params=boundary,
                    include_chirality=base.include_chirality,
                    operator_level=base.operator_level,
                )
                report = level2_ht_gap_report(config, lambda2)
                rows.append(
                    {
                        "k_max": int(k_max),
                        "a": float(a),
                        "twist_params": twist,
                        "boundary_params": boundary,
                        **report,
                    }
                )
    return rows
