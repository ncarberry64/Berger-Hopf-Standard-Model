"""Outward even-Y tails of the reached, stored finite-element heat form.

The value certificate uses the actual stored FE matrices and their Gram
matrix, not an approximate eigenvalue diagonal as the original operator.
The derivative certificate consumes upper bounds on stored quadrature
primitive norms and includes the Gram derivative.  This module certifies
neither continuum convergence nor production of the stored entries.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import math

from flint import arb, acb, acb_mat, ctx
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
INPUT = 'artifacts/muon_native_mean_causal_heat_20261010/target_coefficients_run_5'
PINNED = {
    'paired_target_coefficients.json': '45b249f5b6f3aa5710478f8fbd9ba5ce67bbbc3cdf03a2880cbfd306f8cef7c8',
    'paired_target_coefficients.npz': '6db9b664f6f18ac8763186ed15cdd749ce13ea844db2060af434869aec75d800',
}


def _finite_matrix(value, name):
    a = np.asarray(value, complex)
    if a.ndim != 2 or a.shape[0] != a.shape[1] or not a.size or not np.all(np.isfinite(a)):
        raise ValueError(name + ' must be a nonempty finite square matrix')
    return a


def _acb_matrix(value):
    return acb_mat([[acb(float(z.real), float(z.imag)) for z in row] for row in value])


def _adjoint(value):
    return value.conjugate().transpose()


def _frobenius_upper(value):
    # abs_upper first avoids squaring a zero-centred Arb ball as an interval.
    total = arb(0)
    for i in range(value.nrows()):
        for j in range(value.ncols()):
            total += abs(value[i, j]).abs_upper() ** 2
    return total.sqrt().upper()


def _upper_float(value):
    if not value.is_finite():
        raise ValueError('a finite outward bound was required')
    if value.is_zero():
        return 0.0
    return float(np.nextafter(float(value.upper()), math.inf))


def _record(value):
    return dict(arb=str(value), upper_binary64=_upper_float(value))


def _operator_norm_upper(matrix, reference):
    """Certified norm by a reference unitary congruence, including its defect."""
    h = (reference + reference.conj().T) / 2
    values, vectors = np.linalg.eigh(h)
    V = _acb_matrix(vectors)
    gram = _adjoint(V) * V - acb_mat(np.eye(len(values)).tolist())
    epsilon = _frobenius_upper(gram)
    if not epsilon < 1:
        raise ValueError('reference eigenbasis is not certified invertible')
    diagonal = acb_mat(np.diag(values).tolist())
    defect = _frobenius_upper(_adjoint(V) * matrix * V - diagonal)
    bound = (arb(float(np.max(abs(values)))) + defect) / (1 - epsilon)
    return bound.upper(), dict(reference_Gram_defect=_record(epsilon),
        transformed_operator_defect=_record(defect), operator_norm_upper=_record(bound))


def certify_generalized_even_pencil(K0, K1, K2, gram, reference_vectors,
        reference_eigenvalues, grading, *, precision_bits=192):
    """Certify a positive exact-stored generalized polynomial and its parity.

    No tolerance erases forbidden grading entries or Hermiticity defects.
    Reference vectors need not be orthonormal: their exact stored Gram
    defect is explicitly enclosed.  The accepted scope is a finite pencil.
    """
    if type(precision_bits) is not int or precision_bits < 96:
        raise ValueError('explicit Arb precision of at least96 bits required')
    matrices = [_finite_matrix(a, n) for a, n in zip((K0, K1, K2, gram),
        ('K0', 'K1', 'K2', 'Gram'))]
    n = len(matrices[0])
    if any(a.shape != (n, n) for a in matrices):
        raise ValueError('all FE matrices must share one dimension')
    if any(not np.array_equal(a, a.conj().T) for a in matrices):
        raise ValueError('exact stored FE matrices must be Hermitian')
    signs = np.asarray(grading)
    if signs.shape != (n,) or not np.all(np.isin(signs, (-1, 1))):
        raise ValueError('one exact L/R sign per FE coordinate required')
    parity = signs[:, None] * signs[None, :]
    for a, sign in zip(matrices, (1, -1, 1, 1)):
        if np.any(a[parity != sign] != 0):
            raise ValueError('the exact stored polynomial must preserve its L/R grading')
    V = _finite_matrix(reference_vectors, 'reference vectors')
    lam = np.asarray(reference_eigenvalues, float)
    if V.shape != (n, n) or lam.shape != (n,) or not np.all(np.isfinite(lam)) or np.min(lam) <= 0:
        raise ValueError('complete positive reference eigenvalues and vectors required')
    old = ctx.prec
    try:
        ctx.prec = precision_bits
        AV = _acb_matrix(V)
        transformed = [_adjoint(AV) * _acb_matrix(a) * AV for a in matrices]
        epsilon = _frobenius_upper(transformed[3] - acb_mat(np.eye(n).tolist()))
        if not epsilon < 1:
            raise ValueError('stored reference does not certify positive Gram')
        delta = _frobenius_upper(transformed[0] - acb_mat(np.diag(lam).tolist()))
        lower = (arb(float(np.min(lam))) - delta) / (1 + epsilon)
        if not lower > 0:
            raise ValueError('the stored FE P0 positivity could not be certified')
        maximum = (arb(float(np.max(lam))) + delta) / (1 - epsilon)
        norms = []
        certificates = []
        for T, raw in zip(transformed[1:3], matrices[1:3]):
            norm, certificate = _operator_norm_upper(T, V.conj().T @ raw @ V)
            norms.append((norm / (1 - epsilon)).upper())
            certificates.append(certificate)
        # Point bounds are Arb endpoints; they remain outward at this precision.
        constants = dict(dimension=n, gap_lower=lower.lower(), maximum_upper=maximum.upper(),
            C_norm_upper=norms[0], B_norm_upper=norms[1],
            primitive_squared_norm_factor=(1 / (1 - epsilon)).upper())
        metadata = dict(dimension=n, precision_bits=precision_bits,
            exact_stored_Hermitian_and_LR_parity=True,
            reference_Gram_defect=_record(epsilon), reference_K0_diagonal_defect=_record(delta),
            gap_lower_arb=str(lower.lower()), maximum_upper=_record(maximum),
            C_norm_upper=_record(norms[0]), B_norm_upper=_record(norms[1]),
            primitive_squared_norm_factor=_record(constants['primitive_squared_norm_factor']),
            operator_norm_certificates=certificates,
            approximate_diagonal_is_not_substituted_for_original_P0=True)
        return constants, metadata
    finally:
        ctx.prec = old


def even_y_tail_bounds(constants, cutoff, middle_y, light_y, primitive_norms=None,
        *, precision_bits=192, grading_preserving_variations=False):
    """Cauchy/semigroup tail after Y², including a generalized-Gram derivative.

    The paired coefficient bound uses the difference of the two geometric
    even tails, avoiding a looser sum.  Directional primitives define a
    finite quadrature derivative family, not a chosen physical state.
    Its variations must preserve the SAME L/R grading for the derivative
    to be even in Y. Norm data alone do not establish that condition.
    """
    if not all(np.isfinite(v) for v in (cutoff, middle_y, light_y)) or cutoff <= 0:
        raise ValueError('finite couplings and positive explicit cutoff required')
    if not abs(middle_y) > abs(light_y):
        raise ValueError('middle absolute Y must exceed light absolute Y')
    if type(precision_bits) is not int or precision_bits < 96:
        raise ValueError('explicit Arb precision of at least96 bits required')
    if primitive_norms is not None and grading_preserving_variations is not True:
        raise ValueError('directional even-Y bound requires explicit grading-preserving variations')
    old = ctx.prec
    try:
        ctx.prec = precision_bits
        a = constants['gap_lower']; C = constants['C_norm_upper']; B = constants['B_norm_upper']
        maximum = constants['maximum_upper']; d = constants['dimension']
        if not a > 0 or not C >= 0 or not B >= 0:
            raise ValueError('positive gap and nonnegative operator norm bounds required')
        candidate = min(float((a / (4 * C)).lower()) if not C.is_zero() else math.inf,
            float((a / (4 * B)).sqrt().lower()) if not B.is_zero() else math.inf)
        if math.isinf(candidate): candidate = max(1., 4 * abs(middle_y))
        radius = 2. ** math.floor(math.log2(candidate))
        r = arb(radius)
        if not r * C + r * r * B <= a / 2:
            raise ValueError('the chosen dyadic circle did not certify half-gap accretivity')
        if not arb(abs(middle_y)) < r:
            raise ValueError('fixed Y lies outside the certified Taylor circle')
        x, y = arb(abs(middle_y)) / r, arb(abs(light_y)) / r
        pair = x ** 4 / (1 - x ** 2) - y ** 4 / (1 - y ** 2)
        half = a / 2
        value = d * (arb(cutoff) * half).expint(1) * pair
        slope = d * (-arb(cutoff) * half).exp() / half * pair
        result = dict(circle_radius_exact_binary64=radius,
            circle_perturbation_norm_upper=_record(r * C + r * r * B),
            circle_accretivity_lower_arb=str(half.lower()),
            paired_even_tail_factor=_record(pair), value_tail_upper=_record(value),
            derivative_semigroup_factor_upper=_record(slope),
            difference_of_even_tails_used=True,
            finite_operator_only=True, complete_native_or_Pauli_evaluated=False)
        if primitive_norms is not None:
            names = ('u', 'Au', 'Mu', 'deltaA', 'deltaMu', 'measure', 'weight')
            arrays = {k: np.asarray(primitive_norms[k], float) for k in names}
            samples = arrays['u'].shape
            if len(samples) != 1 or arrays['Au'].shape != samples or arrays['Mu'].shape != samples or arrays['weight'].shape != samples:
                raise ValueError('one nonnegative primitive norm set per sample required')
            shape = arrays['deltaA'].shape
            if len(shape) != 2 or shape[0] != samples[0] or arrays['deltaMu'].shape != shape or arrays['measure'].shape != shape:
                raise ValueError('aligned directional norm arrays required')
            if any(not np.all(np.isfinite(v)) or np.any(v < 0) for v in arrays.values()):
                raise ValueError('primitive norm bounds must be finite and nonnegative')
            factor = constants['primitive_squared_norm_factor']
            bound = np.zeros(shape)
            for i in range(shape[0]):
                u, an, mn, weight = (arb(float(arrays[k][i])) for k in ('u', 'Au', 'Mu', 'weight'))
                for j in range(shape[1]):
                    da, dm, measure = (arb(float(arrays[k][i, j])) for k in ('deltaA', 'deltaMu', 'measure'))
                    z0 = weight * factor * (2 * an * da + measure * (an * an + maximum * u * u))
                    z1 = weight * factor * (2 * mn * da + 2 * an * dm + measure * (2 * an * mn + C * u * u))
                    z2 = weight * factor * (2 * mn * dm + measure * (mn * mn + B * u * u))
                    bound[i, j] = _upper_float(slope * (z0 + r * z1 + r * r * z2))
            result['weighted_directional_tail_upper'] = bound
            sums = []
            for j in range(shape[1]):
                sums.append(_upper_float(sum((arb(float(v)) for v in bound[:, j]), arb(0))))
            result['constant_directional_tail_upper'] = np.asarray(sums)
            result['Gram_measure_derivative_included_once'] = True
            result['primitive_FE_Gram_normalization_factor_included'] = True
            result['directional_grading_preservation_is_required'] = True
        return result
    finally:
        ctx.prec = old


def retained_certificate(*, repository=ROOT, precision_bits=192):
    """Consume the pinned actual17-node finite-core export, without a replay."""
    root = Path(repository); base = root / INPUT
    records = []
    for name, digest in PINNED.items():
        raw = (base / name).read_bytes()
        if sha256(raw).hexdigest() != digest:
            raise ValueError('pinned finite-core input changed: ' + name)
        records.append(dict(path=INPUT + '/' + name, bytes=len(raw), sha256=digest))
    receipt = json.loads((base / 'paired_target_coefficients.json').read_text())
    for item in receipt['source_records'] + receipt['consumed_input_records']:
        raw = (root / item['path']).read_bytes()
        if len(raw) != item['bytes'] or sha256(raw).hexdigest() != item['sha256']:
            raise ValueError('coefficient provenance changed: ' + item['path'])
    with np.load(base / 'paired_target_coefficients.npz', allow_pickle=False) as source:
        a = {k: source[k] for k in source.files}
    for name, item in receipt['array_records'].items():
        value = np.ascontiguousarray(a[name])
        if list(value.shape) != item['shape'] or str(value.dtype) != item['dtype'] or sha256(value.tobytes()).hexdigest() != item['raw_sha256']:
            raise ValueError('coefficient array identity failed: ' + name)
    constants, pencil = certify_generalized_even_pencil(a['actual_FE_K0'], a['actual_FE_K1'], a['actual_FE_K2'],
        a['actual_FE_Gram'], a['computed_generalized_eigenvectors'], a['normalized_P0_eigenvalues'],
        a['actual_FE_LR_sign_grading'], precision_bits=precision_bits)
    norms = dict(u=a['u_Frobenius_upper'], Au=a['Au_Frobenius_upper'], Mu=a['Mu_Frobenius_upper'],
        deltaA=a['deltaA_Frobenius_upper'], deltaMu=a['deltaMu_Frobenius_upper'],
        measure=a['abs_deltaN_over_N'], weight=a['sample_weight'])
    tails = even_y_tail_bounds(constants, receipt['parameter'], receipt['fixed_Y_middle'], receipt['fixed_Y_light'],
        norms, precision_bits=precision_bits, grading_preserving_variations=True)
    arrays = {k: tails.pop(k) for k in ('weighted_directional_tail_upper', 'constant_directional_tail_upper')}
    arrays['coefficient_time_samples'] = a['coefficient_time_samples']
    packet = dict(classification='OUTWARD_EXACT_STORED_FINITE_FE_EVEN_Y_TAYLOR_REMAINDER',
        input_records=records, consumed_source_records=receipt['source_records'],
        coefficient_scope=receipt['coefficient_scope'], pencil_certificate=pencil, tail_certificate=tails,
        cutoff=receipt['parameter'], fixed_Y_middle=receipt['fixed_Y_middle'], fixed_Y_light=receipt['fixed_Y_light'],
        raw228_order='geometry100,gauge_value60,gauge_rate60,Hreal4,Hrate4',
        primitive_norm_scope=receipt['norm_rounding_policy'],
        value_scope='exact stored FE generalized polynomial; Gram/eigenbasis mismatch enclosed',
        derivative_scope='quadrature derivative defined by stored primitive norm bounds, with true FEGram normalization factor',
        derivative_grading_owner='pinned corrected_even_y_paired_heat_cotangent: geometry/connection variations keep A blockdiagonal L/R; H variations keep unit mass offdiagonal; Gram variations remain blockdiagonal',
        norm_data_alone_do_not_prove_derivative_grading=True,
        omitted_error_sources=['production of FE/field/geometry derivative entries', 'quadrature and temporal FE convergence',
            'numerical evaluation of the retained Y2 coefficient/cotangent', 'complete stratified domain/heat and Pauli completion'],
        physical_background_or_cutoff_selected=False, complete_native_or_Pauli_evaluated=False)
    return packet, arrays
