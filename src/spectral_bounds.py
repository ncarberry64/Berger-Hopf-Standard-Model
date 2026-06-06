"""Gate 32B spectral lower-bound scaffold for the H_T audit.

The functions in this module provide sufficient lower-bound checks for the
finite-basis Level 2 proxy. They do not compute the full analytic twisted
Dirac ``H_T`` spectrum and do not complete the no-extra-light-state theorem.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp
from typing import Callable, Iterable

import numpy as np

from ht_operator import default_level2_config, level2_ht_gap_report
from positivity import complement_projector, is_psd, min_eigenvalue
from spectral_gap import MU_H, natural_lambda2
from twisted_dirac import (
    DIRAC_PROXY_LEVEL_2,
    DiracOperatorConfig,
    build_dirac_basis,
    build_level2_dirac_matrix,
    zero_mode_subspace,
)


@dataclass(frozen=True)
class BoundResult:
    """Auditable lower-bound result for a sufficient gap condition."""

    name: str
    lower_bound: float
    target: float
    margin: float
    passes: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def mu_h_target() -> float:
    """Return the supplied dimensionless Hopf target ``mu_H = 64 pi^5``."""

    return MU_H


def _validate_lambda2(lambda2: float) -> float:
    value = float(lambda2)
    if value <= 0:
        raise ValueError("lambda2 must be positive")
    return value


def _validate_mu_h(mu_h: float) -> float:
    value = float(mu_h)
    if value <= 0:
        raise ValueError("mu_h must be positive")
    return value


def heat_lift_lower_bound(d_lower: float, lambda2: float, mu_h: float) -> float:
    """Return ``d_lower + mu_h * (1 - exp(-d_lower / lambda2))``.

    ``d_lower`` is a lower bound for the complement Dirac-squared spectrum.
    This function is monotone in ``d_lower`` for nonnegative inputs.
    """

    d_value = float(d_lower)
    if d_value < 0:
        raise ValueError("d_lower must be nonnegative")
    resolved_lambda2 = _validate_lambda2(lambda2)
    resolved_mu_h = _validate_mu_h(mu_h)
    return float(d_value + resolved_mu_h * (1.0 - exp(-d_value / resolved_lambda2)))


def required_dirac_lower_bound(
    lambda2: float,
    mu_h: float,
    v_min: float = 0.0,
) -> float:
    """Return the smallest ``d_lower`` sufficient for the H_T target.

    The solved inequality is
    ``d + mu_H * (1 - exp(-d / Lambda^2)) + V_min >= mu_H``.
    """

    resolved_lambda2 = _validate_lambda2(lambda2)
    resolved_mu_h = _validate_mu_h(mu_h)
    target_after_profile = resolved_mu_h - float(v_min)
    if target_after_profile <= 0:
        return 0.0

    def passes(value: float) -> bool:
        return heat_lift_lower_bound(value, resolved_lambda2, resolved_mu_h) + float(v_min) >= resolved_mu_h

    lo = 0.0
    hi = resolved_lambda2
    while not passes(hi):
        hi *= 2.0
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if passes(mid):
            hi = mid
        else:
            lo = mid
    return float(hi)


def complement_gap_bound(
    d_lower: float,
    lambda2: float,
    v_min: float = 0.0,
    mu_h: float | None = None,
) -> BoundResult:
    """Evaluate the sufficient complement gap inequality as a ``BoundResult``."""

    resolved_mu_h = MU_H if mu_h is None else _validate_mu_h(mu_h)
    lifted = heat_lift_lower_bound(d_lower, lambda2, resolved_mu_h) + float(v_min)
    return BoundResult(
        name="complement_gap_bound",
        lower_bound=lifted,
        target=resolved_mu_h,
        margin=float(lifted - resolved_mu_h),
        passes=bool(lifted >= resolved_mu_h),
        assumptions=(
            f"Dirac-squared complement lower bound d_lower = {float(d_lower)}.",
            f"Heat-kernel cutoff Lambda^2 = {float(lambda2)} is explicit.",
            f"Additive curvature/profile lower bound V_min = {float(v_min)}.",
        ),
        limitations=(
            "This is a sufficient lower-bound check, not the full analytic H_T spectrum.",
        ),
    )


def combine_bounds(*bounds: BoundResult) -> BoundResult:
    """Return the conservative minimum of compatible lower-bound results."""

    if not bounds:
        raise ValueError("at least one bound is required")
    target = float(bounds[0].target)
    if any(abs(float(bound.target) - target) > 1e-9 for bound in bounds):
        raise ValueError("cannot combine bounds with different targets")
    lower = min(float(bound.lower_bound) for bound in bounds)
    assumptions = tuple(item for bound in bounds for item in bound.assumptions)
    limitations = tuple(item for bound in bounds for item in bound.limitations)
    names = ", ".join(bound.name for bound in bounds)
    return BoundResult(
        name=f"combined_conservative_min({names})",
        lower_bound=lower,
        target=target,
        margin=float(lower - target),
        passes=bool(lower >= target),
        assumptions=assumptions,
        limitations=limitations + ("Combination keeps the most conservative lower bound.",),
    )


def _as_square_matrix(matrix: np.ndarray) -> np.ndarray:
    arr = np.asarray(matrix, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError("matrix must be square")
    return 0.5 * (arr + arr.T)


def _projector_basis(projector: np.ndarray, tol: float = 1e-10) -> np.ndarray:
    p = _as_square_matrix(projector)
    eigenvalues, eigenvectors = np.linalg.eigh(p)
    keep = eigenvalues > 1.0 - tol
    if not np.any(keep):
        raise ValueError("projector has empty selected subspace")
    return eigenvectors[:, keep]


def minmax_bound(matrix: np.ndarray, projector: np.ndarray) -> float:
    """Return the restricted Rayleigh/min-max lower bound on projector range."""

    arr = _as_square_matrix(matrix)
    basis = _projector_basis(projector)
    restricted = basis.T @ arr @ basis
    return min_eigenvalue(restricted)


def gershgorin_lower_bound(matrix: np.ndarray) -> float:
    """Return the Gershgorin lower bound for a symmetric matrix."""

    arr = _as_square_matrix(matrix)
    radii = np.sum(np.abs(arr), axis=1) - np.abs(np.diag(arr))
    discs = np.diag(arr) - radii
    return float(np.min(discs))


def weyl_lower_bound(base_lower: float, perturbation_lower: float) -> float:
    """Return Weyl's additive lower bound for Hermitian perturbations."""

    return float(base_lower + perturbation_lower)


def psd_profile_bound(profile_operator: np.ndarray, complement_projector_matrix: np.ndarray) -> float:
    """Return a complement lower bound for a PSD profile contribution."""

    profile = _as_square_matrix(profile_operator)
    projector = _as_square_matrix(complement_projector_matrix)
    basis = _projector_basis(projector)
    restricted = basis.T @ profile @ basis
    lower = min_eigenvalue(restricted)
    if not is_psd(restricted):
        return float(lower)
    return float(max(0.0, lower))


def _complement_restricted_matrix(matrix: np.ndarray, projector: np.ndarray) -> np.ndarray:
    basis = _projector_basis(projector)
    return basis.T @ _as_square_matrix(matrix) @ basis


def _level2_baseline_objects(config: DiracOperatorConfig) -> dict[str, object]:
    basis = build_dirac_basis(
        k_max=config.k_max,
        sectors=config.sectors,
        include_chirality=config.include_chirality,
    )
    zero_count = int(config.boundary_params.get("zero_mode_count", 3))
    zero_modes = zero_mode_subspace(basis, index_count=zero_count)
    p_perp = complement_projector(zero_modes)
    dirac_matrix = build_level2_dirac_matrix(config)
    dirac_squared = dirac_matrix.T @ dirac_matrix
    restricted = _complement_restricted_matrix(dirac_squared, p_perp)
    exact_d = min_eigenvalue(restricted)
    return {
        "basis": basis,
        "zero_modes": zero_modes,
        "complement_projector": p_perp,
        "dirac_matrix": dirac_matrix,
        "dirac_squared": dirac_squared,
        "restricted_dirac_squared": restricted,
        "exact_d_lower": exact_d,
    }


def _bound_with_name(
    name: str,
    d_lower: float,
    lambda2: float,
    v_min: float,
    mu_h: float,
    assumptions: Iterable[str],
    limitations: Iterable[str],
) -> BoundResult:
    nonnegative_d = max(0.0, float(d_lower))
    result = complement_gap_bound(nonnegative_d, lambda2, v_min=v_min, mu_h=mu_h)
    return BoundResult(
        name=name,
        lower_bound=result.lower_bound,
        target=result.target,
        margin=result.margin,
        passes=result.passes,
        assumptions=tuple(assumptions) + result.assumptions,
        limitations=tuple(limitations) + result.limitations,
    )


def spectral_bound_report(
    config: DiracOperatorConfig | None = None,
    lambda2: float | None = None,
    profile_operator: np.ndarray | None = None,
    v_min: float = 0.0,
    mu_h: float | None = None,
) -> dict[str, object]:
    """Return Level 2 finite-basis lower-bound diagnostics.

    Bounds are conservative sufficient checks for the Level 2 proxy. The
    returned ``theorem_complete`` flag is always ``False``.
    """

    resolved_config = default_level2_config() if config is None else config
    resolved_lambda2 = natural_lambda2() if lambda2 is None else _validate_lambda2(lambda2)
    resolved_mu_h = MU_H if mu_h is None else _validate_mu_h(mu_h)
    objects = _level2_baseline_objects(resolved_config)
    p_perp = objects["complement_projector"]
    dirac_squared = objects["dirac_squared"]
    restricted = objects["restricted_dirac_squared"]
    exact_d = float(objects["exact_d_lower"])
    exact_gap_report = level2_ht_gap_report(resolved_config, resolved_lambda2)
    exact_ht_gap = float(exact_gap_report["first_ht_complement_gap"]) + float(v_min)

    gersh = gershgorin_lower_bound(np.asarray(restricted))
    minmax = minmax_bound(np.asarray(dirac_squared), np.asarray(p_perp))
    direct = exact_d

    profile_lower = 0.0
    profile_assumption = "No profile operator supplied; profile lower bound is zero."
    profile_limitation = "Profile perturbation bound is absent in this row."
    if profile_operator is not None:
        profile_lower = psd_profile_bound(profile_operator, np.asarray(p_perp))
        profile_assumption = f"Profile complement lower bound = {profile_lower}."
        profile_limitation = "Profile bound uses finite-basis complement restriction."

    weyl_d_lower = weyl_lower_bound(direct, profile_lower)

    bounds = [
        _bound_with_name(
            "direct_finite_spectrum",
            direct,
            resolved_lambda2,
            v_min,
            resolved_mu_h,
            (
                "Direct finite-basis Level 2 complement eigenvalue is used as d_lower.",
                f"Model level is {DIRAC_PROXY_LEVEL_2}.",
            ),
            (
                "Exact only within the finite Level 2 proxy matrix.",
            ),
        ),
        _bound_with_name(
            "minmax_restricted_complement",
            minmax,
            resolved_lambda2,
            v_min,
            resolved_mu_h,
            (
                "Min-max bound is computed on the protected zero-mode complement.",
                f"Model level is {DIRAC_PROXY_LEVEL_2}.",
            ),
            (
                "The projector is finite-basis and proxy-level.",
            ),
        ),
        _bound_with_name(
            "gershgorin_restricted_complement",
            gersh,
            resolved_lambda2,
            v_min,
            resolved_mu_h,
            (
                "Gershgorin estimate is computed on the restricted complement matrix.",
                f"Raw Gershgorin d_lower = {gersh}.",
            ),
            (
                "If the Gershgorin lower bound is negative, the heat-lift check uses zero as the nonnegative D^2 floor.",
                "This bound can be very conservative and may fail while the finite spectrum passes.",
            ),
        ),
        _bound_with_name(
            "weyl_profile_bound",
            weyl_d_lower,
            resolved_lambda2,
            v_min,
            resolved_mu_h,
            (
                "Weyl bound combines direct finite-basis complement lower bound with profile lower bound.",
                profile_assumption,
            ),
            (
                profile_limitation,
                "Weyl bound does not replace a full H_T spectral computation.",
            ),
        ),
    ]

    return {
        "model_level": DIRAC_PROXY_LEVEL_2,
        "theorem_complete": False,
        "lambda2": resolved_lambda2,
        "mu_h": resolved_mu_h,
        "required_dirac_lower_bound": required_dirac_lower_bound(
            resolved_lambda2,
            resolved_mu_h,
            v_min=v_min,
        ),
        "basis_size": len(objects["basis"]),
        "zero_mode_count": int(np.asarray(objects["zero_modes"]).shape[1]),
        "exact_finite_basis_complement_eigenvalue": exact_d,
        "exact_finite_basis_ht_gap": exact_ht_gap,
        "raw_dirac_lower_estimates": {
            "direct_finite_spectrum": direct,
            "minmax_restricted_complement": minmax,
            "gershgorin_restricted_complement": gersh,
            "weyl_profile_bound": weyl_d_lower,
        },
        "bounds": bounds,
        "assumptions": (
            f"Natural cutoff is used when lambda2 is omitted: Lambda^2 = {natural_lambda2()}.",
            "Protected zero modes are projected out before complement bounds are evaluated.",
            "All lower bounds are sufficient finite-basis checks.",
        ),
        "limitations": (
            "The full analytic H_T spectrum on the complete Hilbert space remains open.",
            "Gershgorin and Weyl estimates are finite-basis matrix bounds.",
            "Passing finite-basis bounds do not prove the no-extra-light-state theorem.",
        ),
    }


def robustness_bound_reports(
    configs: Iterable[DiracOperatorConfig],
    lambda2: float | None = None,
    mu_h: float | None = None,
) -> list[dict[str, object]]:
    """Return spectral-bound reports for a sequence of Level 2 configs."""

    return [
        spectral_bound_report(config=config, lambda2=lambda2, mu_h=mu_h)
        for config in configs
    ]


def _bound_margin_by_name(report: dict[str, object], name: str) -> float:
    for bound in report["bounds"]:
        if bound.name == name:
            return float(bound.margin)
    raise KeyError(f"missing bound: {name}")


def basis_convergence_scan(
    k_max_values: Iterable[int],
    a_values: Iterable[float],
    config_factory: Callable[..., DiracOperatorConfig] = default_level2_config,
    lambda2: float | None = None,
) -> list[dict[str, object]]:
    """Audit Level 2 H_T lower-bound stability as the finite basis grows.

    The scan reports truncation behavior only. It keeps ``theorem_complete``
    false in every row because finite-basis convergence evidence is not the
    full analytic spectrum.
    """

    resolved_lambda2 = natural_lambda2() if lambda2 is None else _validate_lambda2(lambda2)
    k_values = tuple(int(value) for value in k_max_values)
    if any(value < 0 for value in k_values):
        raise ValueError("k_max values must be nonnegative")
    rows: list[dict[str, object]] = []
    for a in a_values:
        previous_d: float | None = None
        for k_max in sorted(k_values):
            config = config_factory(k_max=k_max, a=float(a))
            report = spectral_bound_report(config=config, lambda2=resolved_lambda2)
            direct_margin = _bound_margin_by_name(report, "direct_finite_spectrum")
            gershgorin_margin = _bound_margin_by_name(
                report,
                "gershgorin_restricted_complement",
            )
            minmax_margin = _bound_margin_by_name(report, "minmax_restricted_complement")
            first_d = float(report["exact_finite_basis_complement_eigenvalue"])
            if previous_d is None:
                note = "baseline basis for this anisotropy"
            elif first_d < previous_d - 1e-10:
                note = (
                    "nonmonotonic decrease in first complement eigenvalue "
                    f"from {previous_d} to {first_d}"
                )
            elif first_d > previous_d + 1e-10:
                note = (
                    "nonmonotonic increase in first complement eigenvalue "
                    f"from {previous_d} to {first_d}"
                )
            else:
                note = "first complement eigenvalue unchanged within tolerance"
            previous_d = first_d
            worst_margin = min(direct_margin, gershgorin_margin, minmax_margin)
            rows.append(
                {
                    "k_max": int(k_max),
                    "a": float(a),
                    "basis_size": int(report["basis_size"]),
                    "zero_mode_count": int(report["zero_mode_count"]),
                    "first_complement_eigenvalue": first_d,
                    "ht_gap": float(report["exact_finite_basis_ht_gap"]),
                    "direct_margin": direct_margin,
                    "gershgorin_margin": gershgorin_margin,
                    "minmax_margin": minmax_margin,
                    "worst_margin": worst_margin,
                    "passes": bool(worst_margin >= 0.0),
                    "monotonicity_notes": note,
                    "theorem_complete": False,
                }
            )
    return rows
