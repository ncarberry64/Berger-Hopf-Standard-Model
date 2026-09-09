"""Exact stored-coordinate HS construction and verified value-only evaluation."""
from contextlib import contextmanager
import numpy as np
from flint import arb, fmpq
from bhsm.interface.arb_eigenpair_inclusion import verify_eigenpair_box
from bhsm.interface.arb_symmetric_inertia import isolate_index


def finite_vector(values, size):
    result = np.asarray(values, dtype=object)
    if result.shape != (size,):
        raise ValueError('complete vector required')
    result = np.array([arb(v) for v in result], dtype=object)
    if not all(v.is_finite() for v in result):
        raise ValueError('finite vector required')
    return result


def weighted_endpoint(state, descriptor, weights):
    w = finite_vector(weights, len(state))
    if not all(v > 0 for v in w):
        raise ValueError('positive weights required')
    x = finite_vector(state, len(w))
    return np.concatenate((x*w, finite_vector([descriptor], 1)))


def physical_midpoint(left, right, left_rate, right_rate, step):
    """Use exact stored step and unrounded weighted endpoints; retain all radii."""
    size = len(left)
    a, b, fa, fb = [finite_vector(v, size) for v in (left, right, left_rate, right_rate)]
    h = arb(step)
    if not h.is_finite() or not h.rad().is_zero() or not h > 0:
        raise ValueError('positive exact stored step required')
    return (a+b)/2+h*(fa-fb)/8


def rational_balls(values):
    values = np.asarray(values, dtype=object)
    if not all(isinstance(v, arb) and v.is_finite() for v in values.flat):
        raise ValueError('finite Arb balls required')
    mid = np.array([str(v.mid().fmpq()) for v in values.flat]).reshape(values.shape)
    rad = np.array([str(v.rad().fmpq()) for v in values.flat]).reshape(values.shape)
    restored = restore_balls(mid, rad)
    if not all(a.contains(b) for a, b in zip(restored.flat, values.flat, strict=True)):
        raise ArithmeticError('rational serialization lost enclosure')
    return mid, rad


def restore_balls(midpoints, radii):
    m, r = np.asarray(midpoints), np.asarray(radii)
    if m.shape != r.shape or not m.size:
        raise ValueError('matching nonempty rational arrays required')
    result = []
    for midpoint, radius in zip(m.flat, r.flat, strict=True):
        mq, rq = fmpq(str(midpoint)), fmpq(str(radius))
        if rq < 0:
            raise ValueError('negative radius')
        # Arb may inflate its radius when reconstructing a ball. That outer
        # enclosure is used for downstream values, never as the original box.
        result.append(arb(arb(mq), arb(rq).upper()))
    output = np.array(result, dtype=object).reshape(m.shape)
    if not all(v.is_finite() for v in output.flat):
        raise ValueError('nonfinite restored ball')
    return output


@contextmanager
def verified_eigenline(cert, checks, *, expected_index=None, normalize_proposal_center=False):
    """Process-local proposal verification; restore parent even on failure."""
    original = cert._eigenline

    def checked(hessian, midpoint, reference):
        result = original(hessian, midpoint, reference)
        if normalize_proposal_center:
            # A small eigen-equation residual does not bound normalization
            # error. Recenter only the proposal, outwardly preserving vector radii
            # and eigenvalue box. The independent inclusion below must prove
            # the resulting NEW box; no old-box certificate is transferred.
            center = [v.mid() for v in result[0]]
            norm = sum((v*v for v in center), arb(0)).sqrt()
            if not norm.is_finite() or not norm > 0:
                raise ArithmeticError('nonzero finite eigenvector proposal center required')
            vector = np.array([(v/norm).mid()+arb(0, old.rad())
                for v, old in zip(center, result[0], strict=True)], dtype=object)
            result = (vector, *result[1:])
        report = verify_eigenpair_box(hessian[cert.QDIM:, cert.QDIM:], result[0], result[1])
        if normalize_proposal_center:
            report['proposal_center_normalized_before_verification'] = True
        if not report['validation_passed']:
            error = ArithmeticError('normalized eigenpair inclusion failed')
            error.eigenpair_inclusion = report
            raise error
        # Establish orientation relative to the unchanged stored reference.
        # This does not prove spectral index or continuation between points.
        overlap = sum((p*arb(float(r)) for p, r in zip(result[0], reference, strict=True)), arb(0))
        if not overlap > 0:
            raise ArithmeticError('eigenpair orientation is unresolved')
        report['positive_stored_reference_overlap'] = True
        if expected_index is not None:
            # Floating eigenvectors provide a fixed change of basis only.
            # Arb verifies its nonsingularity and both threshold inertias.
            reduced = hessian[cert.QDIM:, cert.QDIM:]
            basis = np.linalg.eigh(np.asarray(midpoint[cert.QDIM:, cert.QDIM:], dtype=float))[1]
            try:
                index = isolate_index(reduced, result[1].lower(), result[1].upper(), expected_index, basis=basis)
                report['spectral_index_verification'] = index
                if not index['validation_passed']:
                    raise ArithmeticError('selected eigenvalue index verification failed')
            except ArithmeticError as error:
                report['spectral_index_failure'] = str(error)
                error.eigenpair_inclusion = report
                raise
            report['selected_zero_based_index_verified'] = expected_index
        checks.append(report)
        return result

    cert._eigenline = checked
    try:
        yield
    finally:
        cert._eigenline = original
