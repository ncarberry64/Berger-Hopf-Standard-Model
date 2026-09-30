"""Audit the minimum Pauli readout, without supplying a physical BHSM vertex.

This is a reduction of the existing two-form-factor projection, not a new
completion gate. Inputs must use one fixed tensor inner product/convention.
Numerical examples test algebra only and are not muon predictions.
"""
from __future__ import annotations

import numpy as np


def pauli_readout(vertex, dirac, pauli):
    """Return F1/F2 and the unrepresented remainder for supplied tensors.

    At nonzero transfer, P_perp removes the Dirac component of P. Its dual
    isolates F2. The physical q->0 limit must be controlled separately; at
    exactly zero transfer the usual Pauli tensor vanishes and is rejected.
    """
    v, d, p = [np.asarray(x, dtype=complex).reshape(-1) for x in (vertex, dirac, pauli)]
    if not v.size or v.shape != d.shape or v.shape != p.shape:
        raise ValueError("nonempty tensors must have identical shapes")
    if not all(np.all(np.isfinite(x)) for x in (v, d, p)):
        raise ValueError("finite tensors required")
    dd = float(np.vdot(d, d).real)
    if dd <= 0:
        raise ValueError("Dirac tensor must be nonzero")
    perp = p - d * (np.vdot(d, p) / dd)
    denominator = float(np.vdot(perp, perp).real)
    if denominator <= 1e-24 * max(float(np.vdot(p, p).real), np.finfo(float).tiny):
        raise ValueError("independent Pauli tensor required away from q=0")
    dual = perp / denominator
    f2 = np.vdot(dual, v)
    f1 = np.vdot(d, v - f2 * p) / dd
    remainder = v - f1 * d - f2 * p
    return {
        "F1": f1,
        "F2": f2,
        "dual": dual,
        "relative_remainder": float(np.linalg.norm(remainder) / max(np.linalg.norm(v), np.finfo(float).tiny)),
    }
