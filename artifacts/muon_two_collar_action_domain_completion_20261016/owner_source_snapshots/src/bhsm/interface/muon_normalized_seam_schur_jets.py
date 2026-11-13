"""Once-only normalized D5 seam action and full fixed-trace source jets.

This is the exact border identity of the existing action
    A = Kbulk - rho C M B,   Q(A) = [[A,C],[B,0]],
not an additional interface interaction.  B and C are independently supplied
normalized right and Dirac-bar left point traces.  No transpose or adjoint is
substituted for either trace, and no complementary field coordinate is removed.

Every input is a mapping with explicit value/x/y/xy entries.  Sources x,y
are independent analytic coordinates; even on a real base their derivatives
are not formed by conjugating the opposite source.  These finite algebraic
jets do not supply a physical exterior, normal mode, background or magnetic
source.  The original normalized_two_sheet_point_action remains the owner.
"""
from __future__ import annotations

from collections.abc import Mapping
import warnings

import numpy as np
from scipy.linalg import LinAlgWarning, lu_factor, lu_solve


KEYS = ("value", "x", "y", "xy")
PROVENANCE = (
    "muon_full_d5_localized_lepton_trace.normalized_d5_point_trace and "
    "normalized_d5_dirac_bar_trace; "
    "muon_holomorphic_d5_trace_action.normalized_two_sheet_point_action: "
    "SH=-rho*barPsi*C*M18*B*Psi on the two eta sheets, once only"
)


def _jet(value, shape, name):
    if not isinstance(value, Mapping) or set(value) != set(KEYS):
        raise ValueError(name + " requires explicit value/x/y/xy entries")
    out = {}
    for key in KEYS:
        a = np.asarray(value[key], dtype=complex)
        if a.shape != shape or not np.isfinite(a).all():
            raise ValueError(name + ": finite same-shape " + key + " required")
        out[key] = a.copy()
    return out


def _times(a, b):
    return a * b if a.ndim == 0 or b.ndim == 0 else a @ b


def jet_product(a, b):
    """Ordered scalar/matrix product, including both mixed placements."""
    return {
        "value": _times(a["value"], b["value"]),
        "x": _times(a["x"], b["value"]) + _times(a["value"], b["x"]),
        "y": _times(a["y"], b["value"]) + _times(a["value"], b["y"]),
        "xy": (_times(a["xy"], b["value"]) + _times(a["x"], b["y"])
               + _times(a["y"], b["x"]) + _times(a["value"], b["xy"])),
    }


def _negative(a):
    return {key: -a[key] for key in KEYS}


def _balanced_factor(matrix):
    # This is only a fixed numerical preconditioner.  Its coordinates do not
    # replace the supplied coefficient jets, nor are its absolute values
    # differentiated as an analytic field operation.
    tiny = np.finfo(float).tiny
    row = 1 / np.maximum(np.max(abs(matrix), axis=1), tiny)
    col = 1 / np.maximum(np.max(abs(row[:, None] * matrix), axis=0), tiny)
    balanced = row[:, None] * matrix * col[None, :]
    with warnings.catch_warnings():
        warnings.simplefilter("error", LinAlgWarning)
        factor = lu_factor(balanced, check_finite=True)

    def solve(rhs):
        answer = col[:, None] * lu_solve(factor, row[:, None] * rhs)
        if not np.isfinite(answer).all():
            raise ArithmeticError("bare fixed-trace solve is nonfinite")
        return answer

    return solve, row, col


def normalized_seam_schur_jets(Kbulkjet, Bjet, Cjet, rhojet, M18jet):
    """Construct all four jets using one bare-bulk-border factorization.

    Q0 [U;lambda0]=[0;I].  The same U and lambda=lambda0+rho*M
    solve Q(A)[U;lambda]=[0;I], hence Gamma=Gamma_bulk-rho*M.
    The bare-border solve keeps every field/complementary row.  Original
    full-seam border residuals are returned for value/x/y/xy, separately
    from the identically zero algebraic Poisson-invariance rows.
    """
    k0 = np.asarray(Kbulkjet.get("value") if isinstance(Kbulkjet, Mapping)
                    else None, dtype=complex)
    b0 = np.asarray(Bjet.get("value") if isinstance(Bjet, Mapping)
                    else None, dtype=complex)
    if k0.ndim != 2 or k0.shape[0] != k0.shape[1]:
        raise ValueError("complete square full-field bulk action required")
    nf = len(k0)
    if b0.ndim != 2 or b0.shape[1] != nf or not 0 < b0.shape[0] <= nf:
        raise ValueError("right point trace with explicit full-field columns required")
    nt = len(b0)
    K = _jet(Kbulkjet, (nf, nf), "Kbulk")
    B = _jet(Bjet, (nt, nf), "B")
    C = _jet(Cjet, (nf, nt), "C")
    rho = _jet(rhojet, (), "rho")
    M = _jet(M18jet, (nt, nt), "M18")
    zeros = np.zeros((nt, nt), complex)
    rhoM = jet_product(rho, M)
    seam = _negative(jet_product(jet_product(C, rhoM), B))
    action = {key: K[key] + seam[key] for key in KEYS}
    bare = {key: np.block([[K[key], C[key]], [B[key], zeros]]) for key in KEYS}
    full = {key: np.block([[action[key], C[key]], [B[key], zeros]]) for key in KEYS}
    rhs = np.vstack((np.zeros((nf, nt), complex), np.eye(nt)))
    solve, row, col = _balanced_factor(bare["value"])
    z = {"value": solve(rhs)}
    z["x"] = solve(-bare["x"] @ z["value"])
    z["y"] = solve(-bare["y"] @ z["value"])
    z["xy"] = solve(-bare["xy"] @ z["value"]
                    - bare["x"] @ z["y"] - bare["y"] @ z["x"])
    bulk_gamma = {key: -z[key][nf:].copy() for key in KEYS}
    gamma = {key: bulk_gamma[key] - rhoM[key] for key in KEYS}
    full_z = {key: np.vstack((z[key][:nf], z[key][nf:] + rhoM[key])) for key in KEYS}
    bare_rows = jet_product(bare, z)
    full_rows = jet_product(full, full_z)
    bare_rows["value"] -= rhs
    full_rows["value"] -= rhs
    trace_rows = jet_product(B, {key: z[key][:nf] for key in KEYS})
    trace_rows["value"] -= np.eye(nt)
    return {
        "Gamma_bulk": bulk_gamma,
        "Gamma_full": gamma,
        "rho_M": rhoM,
        "full_field_Poisson": {key: full_z[key][:nf] for key in KEYS},
        "bulk_field_Poisson": {key: z[key][:nf] for key in KEYS},
        "bare_border_jet": bare,
        "full_seam_border_jet": full,
        "bare_border_solution_jet": z,
        "full_seam_border_solution_jet": full_z,
        "original_bare_border_rows": bare_rows,
        "original_full_seam_border_rows": full_rows,
        "original_trace_rows": trace_rows,
        "algebraic_Poisson_invariance_rows": {
            key: full_z[key][:nf] - z[key][:nf] for key in KEYS},
        "seam_action_jet": seam,
        "right_wall_bulk_seam_contact": _negative(jet_product(rhoM, B)),
        "left_bulk_wall_seam_contact": _negative(jet_product(C, rhoM)),
        "bare_border_row_scale": row,
        "bare_border_column_scale": col,
        "full_field_count": nf,
        "normalized_trace_count": nt,
        "complementary_field_count": nf - nt,
        "bare_border_factorizations": 1,
        "full_seam_border_factorizations": 0,
        "c45_law_provenance": PROVENANCE,
        "source_left_coefficients_conjugated": False,
        "independent_left_trace_replaced_by_adjoint": False,
        "once_only_original_Higgs_seam": True,
        "physical_exterior_background_or_normalization_claimed": False,
    }
