"""Independent lens-geometry audit, with no BHSM temporal-provider imports.

This checks the calculus of the conditional SIS delay and the exact
effective-potential correspondence. The finite matrix family is a numerical
completion for a derivative check, not a second-order physical metric.
"""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import root

HERE = Path(__file__).resolve().parent
DOL, DOS, DLS = 0.21, 0.38, 0.24
ZL = 0.3
B = 2.0e-6
THETA_E = B * DLS / DOS
BETA_MAG = 0.25 * THETA_E
T0 = (1 + ZL) * DOL * DOS / DLS
H = np.diag([1.0, -1.0])
COEFFICIENTS = (0.31, -0.27, 0.19)  # E_ol, E_os, E_ls


def maps(eps):
    al, ass, als = COEFFICIENTS
    eye = np.eye(2)
    dl = DOL * (eye + eps * al * H)
    ds = DOS * (eye + eps * ass * H)
    dls = DLS * (eye + eps * als * H)
    tt = (1 + ZL) * dl.T @ np.linalg.solve(dls, ds)
    return dl, ds, dls, tt


def image_and_delay(eps, angle):
    e = np.array([np.cos(angle), np.sin(angle)])
    physical_source = DOS * BETA_MAG * e
    dl, ds, dls, tt = maps(eps)
    beta = np.linalg.solve(ds, physical_source)

    def lens_eq(z):
        theta = THETA_E * z
        position = dl @ theta
        alpha = B * position / np.linalg.norm(position)
        return (theta - np.linalg.solve(ds, dls @ alpha) - beta) / THETA_E

    def arrival(theta):
        v = theta - beta
        return 0.5 * v @ tt @ v - (1 + ZL) * B * np.linalg.norm(dl @ theta)

    images = []
    residuals = []
    for sign in (1, -1):
        guess = (BETA_MAG / THETA_E + sign) * e
        sol = root(lens_eq, guess, method="hybr", options={"xtol": 1e-11})
        residual = float(np.linalg.norm(lens_eq(sol.x)))
        if residual > 1e-10:
            raise RuntimeError(f"Image solve failed: {residual}")
        images.append(sol.x * THETA_E)
        residuals.append(residual)
    delay = arrival(images[1]) - arrival(images[0])
    if delay <= 0:
        raise RuntimeError("Unexpected image-delay ordering")
    return delay, max(residuals), images, beta


def delay_derivative_audit():
    entries = []
    maximum_error = 0.0
    maximum_residual = 0.0
    for angle in (0.0, np.pi/8, np.pi/4, np.pi/3, np.pi/2):
        baseline, _, _, _ = image_and_delay(0.0, angle)
        h = 2e-4
        f = {}
        for factor in (-2, -1, 1, 2):
            delay, residual, _, _ = image_and_delay(factor * h, angle)
            f[factor] = delay
            maximum_residual = max(maximum_residual, residual)
        numerical = (f[-2] - 8*f[-1] + 8*f[1] - f[2]) / (12*h*baseline)
        analytic = (COEFFICIENTS[0] - COEFFICIENTS[1]) * np.cos(2*angle)
        error = float(abs(numerical-analytic))
        maximum_error = max(maximum_error, error)
        entries.append({"source_angle_radians": angle,
                        "analytic_fractional_delay_derivative": float(analytic),
                        "independent_four_point_derivative": float(numerical),
                        "absolute_error": error})
    assert maximum_error < 2e-8
    return {"max_absolute_error": maximum_error,
            "max_dimensionless_lens_equation_residual": maximum_residual,
            "entries": entries}


def exact_correspondence_audit():
    max_fermat_error = 0.0
    max_gradient_error = 0.0
    max_time_symmetry = 0.0
    for eps in (-0.12, 0.08):
        dl, ds, dls, tt = maps(eps)
        mm = tt / T0
        max_time_symmetry = max(max_time_symmetry, float(np.linalg.norm(tt-tt.T)))
        for angle in (0.2, 0.7):
            physical_source = DOS * BETA_MAG * np.array([np.cos(angle), np.sin(angle)])
            beta = np.linalg.solve(ds, physical_source)
            beta_eff = mm @ beta
            source_constant = 0.5 * beta @ (mm-mm@mm) @ beta
            for direction in ([1.3, -0.4], [-0.8, 0.6], [0.35, 1.1]):
                theta = THETA_E * np.asarray(direction)
                x = dl @ theta
                psi = B * np.linalg.norm(x)
                alpha = B * x / np.linalg.norm(x)
                vv = theta-beta
                original = (0.5*vv@tt@vv - (1+ZL)*psi)/T0
                psi_eff = (1+ZL)*psi/T0 + 0.5*theta@(np.eye(2)-mm)@theta
                conventional = 0.5*np.dot(theta-beta_eff,theta-beta_eff)-psi_eff+source_constant
                # Normalize the tiny angular-squared Fermat values by theta_E^2.
                max_fermat_error = max(max_fermat_error, float(abs(original-conventional)/THETA_E**2))
                original_gradient = (tt@vv-(1+ZL)*dl.T@alpha)/T0
                conventional_gradient = theta-beta_eff-((1+ZL)*dl.T@alpha/T0+(np.eye(2)-mm)@theta)
                max_gradient_error = max(max_gradient_error, float(np.linalg.norm(original_gradient-conventional_gradient)/THETA_E))
    assert max_fermat_error < 1e-12
    assert max_gradient_error < 1e-12
    return {"max_scaled_fermat_difference": max_fermat_error,
            "max_scaled_gradient_difference": max_gradient_error,
            "max_time_matrix_antisymmetry": max_time_symmetry}


if __name__ == "__main__":
    result = {
        "scope": "Independent algebra/derivative audit of ideal SIS matrix optics; no observational or microscopic validation",
        "finite_completion": "D_ab=d_ab(I+epsilon a_ab diag(1,-1)); commuting maps, not an action-derived second-order metric",
        "delay_derivative": delay_derivative_audit(),
        "effective_potential_correspondence": exact_correspondence_audit(),
    }
    output = HERE / "geometry_identity_audit.json"
    output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
