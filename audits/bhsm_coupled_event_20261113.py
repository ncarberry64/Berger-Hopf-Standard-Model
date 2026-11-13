"""Portable reproduction of reviewed central Maxwell initial-slice integrals.

Requires NumPy and the sibling artifacts/bhsm_coupled_event_20261113/inputs.json.
This evaluates saved coefficients; it neither fits new fields nor imports BHSM
producers. The result is a partial source-action check, not a physical solution.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

DEFAULT_INPUT = Path(__file__).resolve().parents[1] / "artifacts" / "bhsm_coupled_event_20261113" / "inputs.json"


def load_inputs(path=DEFAULT_INPUT):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _rule(points):
    nodes, weights = np.polynomial.legendre.leggauss(points)
    return (nodes + 1.0) / 2.0, weights / 2.0


def evaluate(data, points=192, response_points=192):
    """Evaluate the saved smooth fields, retaining the normal momentum contact.

    The supplied anchor a,a_prime belongs to this one saved x. Changing x alone
    would not recompute the anchored chart and is not a geometry continuation.
    """
    if points < 32 or response_points < 32:
        raise ValueError("At least 32 quadrature points are required.")
    config = data["configuration"]
    x = float(config["x"])
    wall = np.pi / 4.0 + x
    a = np.asarray(data["anchor"]["a"], dtype=float)
    ap = np.asarray(data["anchor"]["a_prime"], dtype=float)
    if config["curl"] != 2 or config["alpha"] != 1:
        raise ValueError("This reproduction owns the constant curl2, alpha1 sector.")
    carriers = data["active_carriers"]
    h = float(config["halfwidth"])
    centers = np.array([row["center"] for row in carriers], dtype=float)
    if (np.min(centers) <= h or np.max(centers) + h >= 1
            or np.min(np.diff(np.sort(centers))) <= 2*h):
        raise ValueError("Carriers must have disjoint compact interior supports.")
    if any(row["kind"] not in ("E", "M") or row["amplitude"] < 0 for row in carriers):
        raise ValueError("Expected nonnegative E/M field amplitudes.")
    rn, rw = _rule(response_points)
    q, qw = _rule(points)

    def primitive(chi):
        chi = np.asarray(chi)
        inner = chi[..., None] * rn
        s2, s6 = np.sin(2*inner), np.sin(6*inner)
        f = inner + a[0]*s2 + a[1]*s6
        fx = ap[0]*s2 + ap[1]*s6  # Fixed physical chi, no wall advection.
        integral = chi * ((np.sin(2*f)**2 / 4) @ rw)
        derivative = chi * ((np.sin(4*f)*fx / 2) @ rw)
        return integral, derivative

    Z, Zx = primitive(np.pi/2)

    def localization(chi):
        integral, derivative = primitive(chi)
        P = integral / Z
        Px = derivative/Z - P*Zx/Z
        f = chi + a[0]*np.sin(2*chi) + a[1]*np.sin(6*chi)
        Pchi = np.sin(2*f)**2 / (4*Z)
        return 4*P*(1-P), 4*(1-2*P)*Px, 4*(1-2*P)*Pchi

    rows = []
    for row in carriers:
        y = float(row["center"]) - h + 2*h*q
        chi = wall*y
        s = (y-float(row["center"]))/h
        phi = y*(1-y)*np.exp(-1/(1-s*s))
        log_y = 1/y-1/(1-y)-2*s/(h*(1-s*s)**2)
        log_yy = -1/y**2-1/(1-y)**2-2*(1+3*s*s)/(h*h*(1-s*s)**3)
        py, pyy = phi*log_y, phi*(log_y**2+log_yy)
        ell, ellx, ellchi = localization(chi)
        ell_material_x = ellx+y*ellchi
        R, Rchi = np.sin(chi)*np.cos(chi), np.cos(2*chi)
        if row["kind"] == "E":
            base = wall*R*phi**2
            energy = ell*base/32
            force = ellx*base/32
            partial_Lx = (ell*R+wall*(ell_material_x*R+ell*Rchi*y))*phi**2/32
            # Direct source-Maxwell d_t L_U; not L_x minus force by definition.
            momentum_rate = -ell*R*y*phi*py/16
        else:
            base = R/wall*py**2+4*wall/R*phi**2
            energy = ell*base/32
            force = -ellx*base/32
            base_x = (Rchi*y/wall-R/wall**2)*py**2+4*(1/R-wall*Rchi*y/R**2)*phi**2
            partial_Lx = -(ell_material_x*base+ell*base_x)/32
            spatial_euler = ((ellchi*R+ell*Rchi)*wall*py+ell*R*pyy)/wall**2-4*ell*phi/R
            momentum_rate = -y*py*spatial_euler/16
        measure = 2*h*qw*float(row["amplitude"])**2
        moments = np.cos(4*np.arange(1,13)[:, None]*chi) @ (measure*energy)
        rows.append(dict(index=int(row["index"]), kind=row["kind"],
                         energy=float(measure @ energy), moments=moments,
                         full_normal=float(measure @ force),
                         partial_Lx=float(measure @ partial_Lx),
                         direct_dt_LU=float(measure @ momentum_rate)))
    T = sum(row["energy"] for row in rows if row["kind"] == "E")
    V = sum(row["energy"] for row in rows if row["kind"] == "M")
    moments = sum((row["moments"] for row in rows), np.zeros(12))
    force = sum(row["full_normal"] for row in rows)
    Lx = sum(row["partial_Lx"] for row in rows)
    dtLU = sum(row["direct_dt_LU"] for row in rows)
    target = np.asarray(data["target"], dtype=float)
    residual = target-np.r_[moments, force]
    contact_error = Lx-dtLU-force
    closed = np.max(np.abs(residual)) < 2e-9 and abs(contact_error) < 2e-7
    return dict(schema_version=1,
                status="PASS_RETAINED_PARTIAL_ROWS" if closed else "RETAINED_ROWS_NOT_CLOSED",
                quadrature=dict(carrier_points=points, response_points=response_points),
                electric_energy=T, magnetic_energy=V, total_energy=T+V,
                positive_energy_moments=moments.tolist(), central_lapse_rows=(-moments).tolist(),
                retained_target=target.tolist(), retained_12_plus_normal_residual=residual.tolist(),
                max_abs_residual=float(np.max(np.abs(residual))),
                full_normal_Euler=force, partial_material_Lx=Lx, direct_dt_LU=dtLU,
                normal_contact_error=contact_error,
                radius_7T_minus_5V_minus_xF=7*T-5*V-x*force,
                initial_central_shift_zero="exact disjoint E/M supports",
                scope=data["scope"], provenance=data["provenance"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate(load_inputs(args.inputs))
    payload = json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+"\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
