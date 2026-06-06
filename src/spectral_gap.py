"""Gate 28 proxy spectral-gap audit for the topographic operator H_T.

This module uses the supplied Berger scalar spectrum proxy as a temporary
stand-in for ``D_hat^dagger D_hat``. It does not compute the final twisted
Dirac or full ``H_T`` spectrum.
"""

from __future__ import annotations

from math import pi
from typing import Iterable

import numpy as np

from berger_spectrum import Mode, berger_lambda, ledger_modes
from constants import ALPHA_INV_LOW_ENERGY
from higgs_scale import electroweak_scale_candidate
from screening import ScreenResult

MU_H = 64.0 * pi**5
UNIVERSAL_WIDTH = 1.0 / (4.0 * pi)


def _resolve_lambda2(lambda2: float | None) -> float:
    """Return the explicit cutoff, using the natural width only when omitted."""

    resolved = natural_lambda2() if lambda2 is None else lambda2
    if resolved <= 0:
        raise ValueError("lambda2 must be positive")
    return float(resolved)


def dimensionless_gap_target() -> float:
    """Return the supplied dimensionless target mu_H = 64 pi^5."""

    return dimensionless_hopf_gap()


def hopf_gap_mass(v: float) -> float:
    """Return the supplied Hopf gap mass M_lift = 4 pi^2 v."""

    return 4.0 * pi**2 * v


def dimensionless_hopf_gap() -> float:
    """Return the dimensionless Hopf-gap target mu_H = 64 pi^5."""

    return MU_H


def natural_lambda2() -> float:
    """Return the universal overlap width Lambda^2 = S = 1/(4 pi)."""

    return UNIVERSAL_WIDTH


def alpha_scaled_a() -> float:
    """Return the supplied alpha^{-1}/(12 pi^2) scale used in robustness scans."""

    return ALPHA_INV_LOW_ENERGY / (12.0 * pi**2)


def heat_lift(d: float, lambda2: float | None = None, mu_h: float = MU_H) -> float:
    """Apply the Gate 28 heat-lift proxy to an unlifted eigenvalue.

    The lift is ``d + mu_h * (1 - exp(-d / lambda2))``. It is zero at ``d=0``
    and tends to ``d + mu_h`` when ``d / lambda2`` is large.
    """

    if d < 0:
        raise ValueError("d must be nonnegative")
    if mu_h <= 0:
        raise ValueError("mu_h must be positive")
    resolved_lambda2 = _resolve_lambda2(lambda2)
    return float(d + mu_h * (1.0 - np.exp(-d / resolved_lambda2)))


def required_lambda2(d: float, mu_h: float = MU_H) -> float:
    """Return the largest lambda2 that lets ``heat_lift(d, lambda2) >= mu_h``.

    For ``0 < d < mu_h`` this is ``d / log(mu_h / d)``. For ``d >= mu_h`` the
    unlifted value already clears the dimensionless target, so the result is
    ``inf``. For ``d = 0`` no finite positive lambda2 can lift the zero mode.
    """

    if d < 0:
        raise ValueError("d must be nonnegative")
    if mu_h <= 0:
        raise ValueError("mu_h must be positive")
    if d == 0:
        return 0.0
    if d >= mu_h:
        return float("inf")
    return float(d / np.log(mu_h / d))


def passes_heat_lift_bound(
    d: float,
    lambda2: float | None = None,
    v_min: float = 0.0,
    mu_h: float = MU_H,
) -> bool:
    """Return whether an explicit heat-lift choice clears the Hopf-gap target.

    ``v_min`` is an additive proxy lower bound for curvature/profile
    contributions. Negative values weaken the gap condition. It defaults to
    zero and is never tuned by this function.
    """

    return bool(gap_margin(d, lambda2, v_min=v_min, mu_h=mu_h) >= 0.0)


def gap_margin(
    d: float,
    lambda2: float | None = None,
    v_min: float = 0.0,
    mu_h: float = MU_H,
) -> float:
    """Return ``heat_lift(d, lambda2) + v_min - mu_h``.

    Positive margin passes the proxy Hopf-gap audit; negative margin fails.
    """

    return float(heat_lift(d, lambda2, mu_h=mu_h) + v_min - mu_h)


def scan_proxy_spectrum(
    a: float,
    n_max: int,
    lambda2: float | None = None,
    exclude_zero: bool = True,
) -> list[dict[str, float | int | bool]]:
    """Scan sorted Berger proxy modes and apply the explicit heat lift.

    The scan uses ``0 <= k <= n_max`` and ``0 <= j <= k``. Returned records are
    sorted by unlifted eigenvalue and then by mode labels.
    """

    if a <= 0:
        raise ValueError("a must be positive")
    if n_max < 0:
        raise ValueError("n_max must be nonnegative")
    resolved_lambda2 = _resolve_lambda2(lambda2)

    rows: list[dict[str, float | int | bool]] = []
    for k in range(n_max + 1):
        for j in range(k + 1):
            d = float(berger_lambda(k, j, a=a))
            if exclude_zero and d == 0:
                continue
            lifted = heat_lift(d, resolved_lambda2)
            rows.append(
                {
                    "k": k,
                    "j": j,
                    "q": k - 2 * j,
                    "d": d,
                    "lifted": lifted,
                    "passes": bool(lifted >= MU_H),
                    "lambda2": resolved_lambda2,
                    "required_lambda2": required_lambda2(d),
                }
            )
    return sorted(rows, key=lambda row: (row["d"], row["k"], row["j"]))


def scan_gap_robustness(
    a_values: Iterable[float],
    n_max_values: Iterable[int],
    lambda2: float | None = None,
    v_min_values: Iterable[float] | None = None,
) -> list[dict[str, float | int | bool | tuple[int, int] | None]]:
    """Scan first-mode proxy margins across explicit robustness choices.

    If ``lambda2`` is omitted, the universal width ``1/(4 pi)`` is used. The
    resolved value is recorded in every row so scans cannot silently adjust it.
    """

    resolved_lambda2 = _resolve_lambda2(lambda2)
    v_values = tuple(v_min_values) if v_min_values is not None else (0.0,)
    rows: list[dict[str, float | int | bool | tuple[int, int] | None]] = []
    for a in a_values:
        for n_max in n_max_values:
            scan = scan_proxy_spectrum(
                a=a,
                n_max=n_max,
                lambda2=resolved_lambda2,
                exclude_zero=True,
            )
            first = scan[0] if scan else None
            for v_min in v_values:
                if first is None:
                    rows.append(
                        {
                            "a": float(a),
                            "n_max": int(n_max),
                            "lambda2": resolved_lambda2,
                            "v_min": float(v_min),
                            "first_mode": None,
                            "first_unlifted_d": float("nan"),
                            "first_lifted": float("nan"),
                            "margin": float("nan"),
                            "passes": False,
                        }
                    )
                    continue
                margin = gap_margin(first["d"], resolved_lambda2, v_min=float(v_min))
                rows.append(
                    {
                        "a": float(a),
                        "n_max": int(n_max),
                        "lambda2": resolved_lambda2,
                        "v_min": float(v_min),
                        "first_mode": (int(first["k"]), int(first["j"])),
                        "first_unlifted_d": float(first["d"]),
                        "first_lifted": float(first["lifted"]),
                        "margin": margin,
                        "passes": bool(margin >= 0.0),
                    }
                )
    return rows


def positive_barrier(k: int, j: int, strength: float = 0.0, power: float = 1.0) -> float:
    """Return a nonnegative barrier increasing with the Berger proxy eigenvalue."""

    if strength < 0:
        raise ValueError("strength must be nonnegative")
    if power <= 0:
        raise ValueError("power must be positive")
    d = berger_lambda(k, j)
    return float(strength * d**power)


def profile_well(k: int, j: int, depth: float = 0.0, width: float = 1.0) -> float:
    """Return a bounded negative well localized toward low proxy eigenvalues."""

    if depth < 0:
        raise ValueError("depth must be nonnegative")
    if width <= 0:
        raise ValueError("width must be positive")
    d = berger_lambda(k, j)
    return float(-depth * MU_H * np.exp(-d / width))


def curvature_profile_term(k: int, j: int, model: str = "zero", **params: float) -> float:
    """Return an explicit curvature/profile contribution for a proxy mode.

    Implemented models:
    - ``zero``: no contribution.
    - ``positive_barrier``: nonnegative barrier increasing with proxy eigenvalue.
    - ``bounded_negative``: constant controlled negative contribution
      ``-depth * mu_H``.
    - ``compensated``: negative well plus positive barrier.
    """

    if model == "zero":
        return 0.0
    if model == "positive_barrier":
        return positive_barrier(
            k,
            j,
            strength=float(params.get("strength", 0.0)),
            power=float(params.get("power", 1.0)),
        )
    if model == "bounded_negative":
        depth = float(params.get("depth", 0.0))
        if depth < 0:
            raise ValueError("depth must be nonnegative")
        return float(-depth * MU_H)
    if model == "compensated":
        well = profile_well(
            k,
            j,
            depth=float(params.get("depth", 0.0)),
            width=float(params.get("width", 1.0)),
        )
        barrier = positive_barrier(
            k,
            j,
            strength=float(params.get("strength", 0.0)),
            power=float(params.get("power", 1.0)),
        )
        return float(well + barrier)
    raise ValueError(f"unknown curvature/profile model: {model}")


def net_v_min_over_modes(
    modes: Iterable[Mode],
    model: str,
    **params: float,
) -> float:
    """Return the minimum explicit curvature/profile contribution over modes."""

    values = [curvature_profile_term(mode.k, mode.j, model=model, **params) for mode in modes]
    if not values:
        return float("nan")
    return float(min(values))


def _normalize_profile_models(
    profile_models: Iterable[str | dict[str, object]] | None,
) -> tuple[dict[str, object], ...]:
    if profile_models is None:
        return (
            {"name": "zero", "model": "zero", "params": {}},
            {
                "name": "positive_barrier",
                "model": "positive_barrier",
                "params": {"strength": 1.0, "power": 1.0},
            },
            {"name": "bounded_negative_1pct", "model": "bounded_negative", "params": {"depth": 0.01}},
            {
                "name": "compensated_1pct",
                "model": "compensated",
                "params": {"depth": 0.01, "width": 1.0, "strength": 0.0, "power": 1.0},
            },
        )
    normalized: list[dict[str, object]] = []
    for item in profile_models:
        if isinstance(item, str):
            normalized.append({"name": item, "model": item, "params": {}})
            continue
        model = str(item.get("model", item.get("name", "zero")))
        normalized.append(
            {
                "name": str(item.get("name", model)),
                "model": model,
                "params": dict(item.get("params", {})),
            }
        )
    return tuple(normalized)


def scan_with_profile_terms(
    a_values: Iterable[float],
    n_max_values: Iterable[int],
    lambda2: float | None = None,
    profile_models: Iterable[str | dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    """Scan proxy gap preservation under explicit curvature/profile models."""

    resolved_lambda2 = _resolve_lambda2(lambda2)
    model_specs = _normalize_profile_models(profile_models)
    rows: list[dict[str, object]] = []
    for a in a_values:
        for n_max in n_max_values:
            if n_max < 0:
                raise ValueError("n_max must be nonnegative")
            modes = [
                Mode(k, j)
                for k in range(n_max + 1)
                for j in range(k + 1)
                if berger_lambda(k, j, a=a) != 0
            ]
            for spec in model_specs:
                model = str(spec["model"])
                params = dict(spec["params"])
                mode_rows = []
                for mode in modes:
                    d = float(berger_lambda(mode.k, mode.j, a=a))
                    profile = curvature_profile_term(mode.k, mode.j, model=model, **params)
                    lifted = heat_lift(d, resolved_lambda2)
                    margin = float(lifted + profile - MU_H)
                    mode_rows.append((margin, mode, d, lifted, profile))
                if mode_rows:
                    min_margin, min_mode, min_d, min_lifted, min_profile = min(
                        mode_rows,
                        key=lambda row: (row[0], row[2], row[1].k, row[1].j),
                    )
                    net_v_min = net_v_min_over_modes(modes, model, **params)
                    first_mode = (min_mode.k, min_mode.j)
                else:
                    min_margin = min_d = min_lifted = min_profile = net_v_min = float("nan")
                    first_mode = None
                rows.append(
                    {
                        "a": float(a),
                        "n_max": int(n_max),
                        "lambda2": resolved_lambda2,
                        "model_name": spec["name"],
                        "model": model,
                        "params": params,
                        "critical_mode": first_mode,
                        "critical_unlifted_d": float(min_d),
                        "critical_lifted": float(min_lifted),
                        "critical_profile_term": float(min_profile),
                        "net_v_min": float(net_v_min),
                        "margin": float(min_margin),
                        "passes": bool(min_margin >= 0.0),
                    }
                )
    return rows


def mass_squared_gap_target(v_gev: float | None = None) -> float:
    """Return the no-extra-light mass-squared target (4 pi^2 v)^2."""

    v = electroweak_scale_candidate() if v_gev is None else v_gev
    return hopf_gap_mass(v) ** 2


def default_protected_modes() -> set[Mode]:
    """Return supplied ledger modes protected from the H_perp restriction."""

    return {mode for ranks in ledger_modes().values() for mode in ranks.values()}


def candidate_mode_grid(k_max: int, protected: Iterable[Mode] | None = None) -> list[Mode]:
    """Return finite candidate modes with 0 <= j <= floor(k/2), excluding protected."""

    protected_modes = set(protected or ())
    return [
        Mode(k, j)
        for k in range(k_max + 1)
        for j in range((k // 2) + 1)
        if Mode(k, j) not in protected_modes
    ]


def proxy_ht_eigenvalues(
    modes: Iterable[Mode],
    *,
    beta: float = 0.0,
    gamma: float = 0.0,
    curvature_floor: float = 0.0,
    potential_floor: float | None = None,
) -> np.ndarray:
    """Return finite proxy H_T eigenvalues on supplied modes.

    The default ``potential_floor`` is the supplied dimensionless target. This
    compatibility helper is still a proxy assumption, not a completed spectrum
    computation.
    """

    floor = dimensionless_hopf_gap() if potential_floor is None else potential_floor
    values = []
    for mode in modes:
        lam = berger_lambda(mode.k, mode.j)
        values.append(lam + beta * lam**2 + gamma * curvature_floor + floor)
    return np.array(values, dtype=float)


def spectral_gap_screen(k_max: int = 12, lambda2: float | None = None) -> ScreenResult:
    """Run the Gate 28 finite-grid heat-lift proxy audit."""

    resolved_lambda2 = _resolve_lambda2(lambda2)
    protected = default_protected_modes()
    modes = candidate_mode_grid(k_max, protected=protected)
    unlifted = np.array([berger_lambda(mode.k, mode.j) for mode in modes], dtype=float)
    lifted = np.array([heat_lift(value, resolved_lambda2) for value in unlifted], dtype=float)
    target = dimensionless_hopf_gap()
    scan = scan_proxy_spectrum(a=1.0, n_max=k_max, lambda2=resolved_lambda2, exclude_zero=True)
    first_nonzero = scan[0] if scan else {}
    min_lifted = float(np.min(lifted)) if len(lifted) else float("nan")
    return ScreenResult(
        name="gate_28_ht_proxy_spectral_gap",
        assumptions=(
            f"Finite mode grid uses 0 <= k <= {k_max}.",
            "Supplied charged-sector ledger modes are projected out of H_perp.",
            "Berger scalar spectrum proxy stands in temporarily for D_hat^dagger D_hat.",
            f"Heat-lift lambda2 is fixed at {resolved_lambda2}; no tuning is performed.",
            "This is not a completed H_T spectrum computation.",
        ),
        outputs={
            "mode_count": len(modes),
            "dimensionless_target_mu_H": target,
            "first_nonzero_proxy_eigenvalue": first_nonzero.get("d"),
            "first_nonzero_proxy_mode": (first_nonzero.get("k"), first_nonzero.get("j"))
            if first_nonzero
            else None,
            "min_lifted_proxy_eigenvalue": min_lifted,
            "passes_proxy_bound": bool(min_lifted >= target),
            "mass_squared_target_gev2": mass_squared_gap_target(),
        },
        empirical={},
        relative_error={},
        status="open",
    )
