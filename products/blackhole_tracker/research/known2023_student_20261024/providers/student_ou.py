"""Synthetic research only: independent unit-variance Student-t innovations.

No physical model, fitting, authentic input loader, calibration or adoption is
provided. This is a NEW generative noise hypothesis, not a Gaussian OU method
shortcut and not an elliptic multivariate Student-t distribution. Exact ties
use supplied stable row order; this order is part of the generative hypothesis.
"""
import math

import numpy as np
from scipy.special import betaln


def _vector(value, name):
    raw = np.asarray(value)
    if raw.dtype.kind not in "iuf" or raw.ndim != 1 or not len(raw):
        raise ValueError("Finite real nonempty vectors required: " + name)
    if not isinstance(value, np.ndarray) and any(isinstance(v, (bool, np.bool_)) for v in value):
        raise ValueError("Boolean vector entries are not measurements: " + name)
    result = np.asarray(raw, dtype=float)
    if not np.isfinite(result).all():
        raise ValueError("Finite real vectors required: " + name)
    return result


def _scalar(value, name):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, float, np.integer, np.floating)) or not math.isfinite(value):
        raise ValueError("Finite numeric scalar required: " + name)
    return float(value)


def _student_terms(z, nu):
    """Stable unnormalized deviance and its innovation derivative."""
    root = math.sqrt(nu - 2.)
    absolute = np.abs(z)
    penalty = np.empty(len(z))
    score = np.empty(len(z))
    small = absolute <= root
    ratio = z[small] / root
    penalty[small] = (nu + 1.) * np.log1p(ratio * ratio)
    score[small] = (2. * ((nu + 1.) / (nu - 2.))) * z[small] / (1. + ratio * ratio)
    if np.any(~small):
        inverse = root / z[~small]
        penalty[~small] = (nu + 1.) * (2. * (np.log(absolute[~small]) - math.log(root)) + np.log1p(inverse * inverse))
        score[~small] = (2. * (nu + 1.) / z[~small]) / (1. + inverse * inverse)
    return penalty, score


def student_ou_deviance_score(times, residual, scale, fraction, tau_days, nu, *, row_ids=None):
    """Normalized -2log density and O(N) r/logS/f/logtau adjoints; fixed nu.

    In supplied chronological stable order, R=(1-f)I+f exp(-|dt|/tau),
    B has unit diagonal and subdiagonal -rho, T=B R B'=L L', and
    z=L^-1 B (r/S) are INDEPENDENT unit-variance Student-t draws. Thus C=SRS
    is the covariance, but does not by itself specify this non-Gaussian density.
    nu>2, 0<=f<1, tau>0. No nu optimizer/score or physical fit is implemented.

    Duplicate times are allowed; their stable supplied order is scientifically
    material for this non-Gaussian innovation law. The function NEVER sorts rows.
    If supplied, unique row_ids record that ordering. No native clock equivalence,
    source identities, errors or calibration are established by this helper.
    """
    t, r, s = [_vector(value, name) for value, name in ((times, "times"), (residual, "residual"), (scale, "scale"))]
    f, tau, nu = [_scalar(value, name) for value, name in ((fraction, "fraction"), (tau_days, "tau_days"), (nu, "nu"))]
    n = len(t)
    if r.shape != t.shape or s.shape != t.shape or np.any(s <= 0) or np.any(np.diff(t) < 0):
        raise ValueError("Matched chronological vectors and positive scales required")
    if not 0 <= f < 1 or tau <= 0 or nu <= 2:
        raise ValueError("Require 0<=fraction<1, tau_days>0 and fixed nu>2")
    if row_ids is not None:
        row_ids = list(row_ids)
        if len(row_ids) != n or any(not isinstance(v, str) or not v for v in row_ids) or len(set(row_ids)) != n:
            raise ValueError("Matched unique nonempty stable source-row identities required")
    delta = np.diff(t)
    if not np.isfinite(delta).all():
        raise ValueError("Finite adjacent time differences required")
    rho = np.exp(-delta / tau)
    u = r / s
    if not np.isfinite(u).all():
        raise FloatingPointError("Residual/scale ratio not representable")
    constant = float(n * (math.log(nu - 2.) + 2. * betaln(nu / 2., .5)))
    if f == 0:
        z = u.copy()
        penalty, psi = _student_terms(z, nu)
        history, gf = 0., 0.
        for i in range(1, n):
            history = rho[i - 1] * (history + u[i - 1])
            gf -= psi[i] * history
        gu = psi
        logdet = float(2. * np.log(s).sum())
        log_tau_score = 0.
        method = "EXACT_FRACTION_ZERO_ONE_SIDED_WHITENING_LIMIT"
        diagonal = np.ones(n)
    else:
        a = np.ones(n)
        a[1:] += (1. - 2. * f) * rho * rho
        c = -(1. - f) * rho
        diagonal = np.empty(n)
        subdiagonal = np.empty(max(0, n - 1))
        diagonal[0] = 1.
        z = np.empty(n)
        z[0] = u[0]
        for i in range(1, n):
            subdiagonal[i - 1] = c[i - 1] / diagonal[i - 1]
            pivot = a[i] - subdiagonal[i - 1] ** 2
            if not math.isfinite(pivot) or pivot <= 0:
                raise FloatingPointError("Nonpositive/unresolved Cholesky pivot; no covariance floor substituted")
            diagonal[i] = math.sqrt(pivot)
            w = u[i] - rho[i - 1] * u[i - 1]
            z[i] = (w - subdiagonal[i - 1] * z[i - 1]) / diagonal[i]
        if not np.isfinite(z).all():
            raise FloatingPointError("Whitened innovation not representable")
        penalty, psi = _student_terms(z, nu)
        # Reverse lower-bidiagonal triangular whitening.
        gz = psi.copy()
        gl = 2. / diagonal
        gq = np.zeros(max(0, n - 1))
        gw = np.empty(n)
        for i in range(n - 1, -1, -1):
            gw[i] = gz[i] / diagonal[i]
            gl[i] -= gw[i] * z[i]
            if i:
                gq[i - 1] -= gw[i] * z[i - 1]
                gz[i - 1] -= gw[i] * subdiagonal[i - 1]
        # Reverse the tridiagonal Cholesky recurrence.
        ga = np.empty(n)
        gc = np.empty(max(0, n - 1))
        for i in range(n - 1, 0, -1):
            ga[i] = gl[i] / (2. * diagonal[i])
            gq[i - 1] -= 2. * subdiagonal[i - 1] * ga[i]
            gc[i - 1] = gq[i - 1] / diagonal[i - 1]
            gl[i - 1] -= gc[i - 1] * subdiagonal[i - 1]
        ga[0] = gl[0] / (2. * diagonal[0])
        # Reverse w=B u and the tridiagonal entries a(f,rho),c(f,rho).
        gu = gw.copy()
        gu[:-1] -= rho * gw[1:]
        grho = -u[:-1] * gw[1:] + 2. * (1. - 2. * f) * rho * ga[1:] - (1. - f) * gc
        gf = float(np.sum(-2. * rho * rho * ga[1:] + rho * gc))
        log_tau_score = float(np.sum(grho * rho * delta / tau))
        logdet = float(2. * np.log(diagonal).sum() + 2. * np.log(s).sum())
        method = "BIDIAGONAL_WHITENING_AND_CHOLESKY_REVERSE_ADJOINT"
    residual_score = gu / s
    log_scale_score = 2. - gu * u
    innovation_deviance = float(np.sum(penalty))
    deviance = innovation_deviance + logdet + constant
    if not all(math.isfinite(v) for v in (deviance, gf, log_tau_score, constant)) or not np.isfinite(residual_score).all() or not np.isfinite(log_scale_score).all():
        raise FloatingPointError("Deviance/score not representable; no clipped score substituted")
    return {"schema": "bhsm.synthetic_student_ou_whitening_score.v1", "negative_two_log_density": deviance,
            "innovation_deviance": innovation_deviance, "log_determinant": logdet,
            "normalizing_deviance_constant": constant, "whitened_innovations": z,
            "innovation_score": psi, "residual_score": residual_score, "log_scale_score": log_scale_score,
            "fraction_score": float(gf), "log_tau_score": log_tau_score, "fixed_nu": nu,
            "nu_score": None, "method": method, "row_ids_in_generative_order": row_ids,
            "ordering_contract": "Chronological nondecreasing times; exact ties retain supplied stable row order, which is part of this non-Gaussian generative law. No sorting performed.",
            "scope": "Synthetic generic noise research only; not adopted, calibrated, or authorized for physical fits.",
            "flux_positive_support_contract": "No Gaussian positive-flux tail bound or normalization inherited; separate analysis required before any flux application."}
