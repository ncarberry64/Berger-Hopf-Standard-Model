"""Exact local delta-seam transfer and independent analytic source jets.

For the declared weak jump J(psi_out-psi_in)=C T q, the isotropic
trace condition B J^-1 C=0 gives q=B psi_out=B psi_in and
psi_out=(I+N)psi_in, N=J^-1 C T B, N^2=0.  These in/out labels do not
rename the physical eta-sheet orientations.  The function below builds
these candidate maps and reports their original equations; it does not
silently admit an arbitrary input as isotropic or as a physical domain.

C is supplied independently.  No source derivative is conjugated and no
adjoint, transpose, trace average, new seam coefficient or boundary load is
introduced.  A Hermitian/Riesz interpretation requires its real physical
pairing and the separately owned source/frame identifications.  Physical
adoption, closed global operator, outgoing domain and normalization remain
outside this finite exact algebra.
"""
from __future__ import annotations

from collections.abc import Mapping
import warnings

import numpy as np
from scipy.linalg import LinAlgWarning, lu_factor, lu_solve


KEYS = ("value", "x", "y", "xy")


def _jet(value, shape, name):
    if not isinstance(value, Mapping) or set(value) != set(KEYS):
        raise ValueError(name + " requires explicit value/x/y/xy entries")
    result = {}
    for key in KEYS:
        a = np.asarray(value[key], complex)
        if a.shape != shape or not np.isfinite(a).all():
            raise ValueError(name + ": finite same-shape " + key + " required")
        result[key] = a.copy()
    return result


def _product(a, b):
    return {
        "value": a["value"] @ b["value"],
        "x": a["x"] @ b["value"] + a["value"] @ b["x"],
        "y": a["y"] @ b["value"] + a["value"] @ b["y"],
        "xy": (a["xy"] @ b["value"] + a["x"] @ b["y"]
               + a["y"] @ b["x"] + a["value"] @ b["xy"]),
    }


def _difference(a, b):
    return {key: a[key] - b[key] for key in KEYS}


def _identity(n):
    return {key: np.eye(n, dtype=complex) if key == "value"
            else np.zeros((n,n), complex) for key in KEYS}


def _inverse_jet(J):
    # Fixed numerical preconditioning does not alter or differentiate the
    # supplied analytic coefficients.  One factorization serves all four
    # exact differentiated inverse equations; no spectral mode is dropped.
    tiny = np.finfo(float).tiny
    row = 1 / np.maximum(np.max(abs(J["value"]), axis=1), tiny)
    col = 1 / np.maximum(np.max(abs(row[:,None]*J["value"]), axis=0), tiny)
    balanced = row[:,None]*J["value"]*col[None,:]
    with warnings.catch_warnings():
        warnings.simplefilter("error", LinAlgWarning)
        factor = lu_factor(balanced, check_finite=True)
    def solve(rhs):
        answer = col[:,None]*lu_solve(factor, row[:,None]*rhs)
        if not np.isfinite(answer).all():
            raise ArithmeticError("nonfinite full-fibre J inverse solve")
        return answer
    inv = {"value": solve(np.eye(len(J["value"]), dtype=complex))}
    inv["x"] = solve(-J["x"]@inv["value"])
    inv["y"] = solve(-J["y"]@inv["value"])
    inv["xy"] = solve(-J["xy"]@inv["value"]
                      - J["x"]@inv["y"] - J["y"]@inv["x"])
    return inv, row, col


def isotropic_seam_transfer_jets(Jjet, Cjet, Tjet, Bjet):
    """Return value/x/y/xy maps and admission residuals, without admission.

    J is dxd and invertible; C is dxn, T is nxn, B is nxd.  All d fibre
    rows remain.  Shape/finite/inverse failures raise; nonzero isotropy,
    nilpotence, trace or inverse residuals are returned to the application
    with no hidden numerical tolerance or physical interpretation.
    """
    j0 = np.asarray(Jjet.get("value") if isinstance(Jjet, Mapping) else None,
                    complex)
    b0 = np.asarray(Bjet.get("value") if isinstance(Bjet, Mapping) else None,
                    complex)
    if j0.ndim != 2 or j0.shape[0] != j0.shape[1] or not len(j0):
        raise ValueError("nonempty square full-fibre J required")
    d = len(j0)
    if b0.ndim != 2 or b0.shape[1] != d or not 0 < b0.shape[0] <= d:
        raise ValueError("B must contain explicit full-fibre columns")
    n = len(b0)
    J = _jet(Jjet, (d,d), "J")
    C = _jet(Cjet, (d,n), "C")
    T = _jet(Tjet, (n,n), "T")
    B = _jet(Bjet, (n,d), "B")
    I = _identity(d)
    inv, row, col = _inverse_jet(J)
    V = _product(_product(C,T),B)
    N = _product(inv,V)
    transfer = {key: I[key] + N[key] for key in KEYS}
    inverse = {key: I[key] - N[key] for key in KEYS}
    # This independent analytic row map is the J-contragredient of I-N.
    # It is not inferred as transfer^dagger and supplies no physical Riesz
    # identification. Its Green identity is conditional on inverse rows.
    dual = _product(_product(J,inverse),inv)
    return {
        "N": N,
        "transfer": transfer,
        "inverse_transfer": inverse,
        "J_inverse": inv,
        "V": V,
        "isotropy": _product(_product(B,inv),C),
        "original_jump_rows": _difference(_product(J,N),V),
        "original_reverse_jump_rows": _difference(
            _product(J,_difference(I,inverse)),V),
        "trace_continuity_rows": _difference(_product(B,transfer),B),
        "reverse_trace_continuity_rows": _difference(_product(B,inverse),B),
        "nilpotence_rows": _product(N,N),
        "inverse_graph_rows": _difference(_product(inverse,transfer),I),
        "reverse_inverse_graph_rows": _difference(_product(transfer,inverse),I),
        "original_J_inverse_rows": _difference(_product(J,inv),I),
        "reverse_J_inverse_rows": _difference(_product(inv,J),I),
        "seam_source_continuity_rows": _difference(_product(V,transfer),V),
        "independent_dual_transfer": dual,
        "independent_bilinear_green_rows": _difference(
            _product(_product(dual,J),transfer),J),
        "J_inverse_row_scale": row,
        "J_inverse_column_scale": col,
        "full_fibre_count": d,
        "normalized_trace_count": n,
        "full_fibre_rows_deleted": 0,
        "source_left_coefficients_conjugated": False,
        "C_replaced_by_adjoint_or_transpose": False,
        "trace_average_selected": False,
        "new_surface_coefficient_selected": False,
        "physical_domain_adoption": None,
        "closed_global_operator_claimed": False,
        "physical_outgoing_or_spin_normalization_claimed": False,
        "scope": "conditional exact local weak delta-seam graph; all residual jets returned",
    }
