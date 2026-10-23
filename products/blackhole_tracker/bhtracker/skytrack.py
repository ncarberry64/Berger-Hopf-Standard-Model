"""Measured lens-position GLS in a declared tangent plane; no mass inference."""
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform
import sys

import numpy as np
import scipy
from scipy.linalg import solve_triangular
from scipy.stats import chi2

INPUT_SCHEMA = 'bhtracker.measured_lens_skytrack_observations.v1'
RESULT_SCHEMA = 'bhtracker.measured_lens_skytrack_result.v1'
PARAMETER_ORDER = ['east_ref_mas', 'north_ref_mas', 'mu_east_mas_per_Julian_year', 'mu_north_mas_per_Julian_year']
UNAVAILABLE = {'mass_msun': None, 'lens_distance_pc': None, 'transverse_velocity_km_s': None,
               'horizon': None, 'core_state': None, 'physical_interface_shape': None,
               'absolute_lens_motion': None}


def _number(value):
    if type(value) not in (int, float):
        raise ValueError('finite non-boolean numeric values required')
    try: result = float(value)
    except OverflowError as error: raise ValueError('numeric value is not representable') from error
    if not math.isfinite(result) or (type(value) is int and result != value):
        raise ValueError('finite value-preserving binary64 inputs required')
    return result


def _text(value, name):
    if not isinstance(value, str) or not value.strip(): raise ValueError(name + ' must be supplied')
    return value


def _tree(value, depth=0):
    if depth > 64: raise ValueError('JSON nesting exceeds 64 levels')
    if value is None or type(value) in (str, bool): return
    if type(value) in (int, float): _number(value); return
    if type(value) is list:
        for item in value: _tree(item, depth + 1)
        return
    if type(value) is dict and all(type(key) is str for key in value):
        for item in value.values(): _tree(item, depth + 1)
        return
    raise ValueError('only finite JSON values and string keys are admitted')


def _same_values(left, right):
    if type(right) is dict:
        return type(left) is dict and set(left)==set(right) and all(_same_values(left[k],v) for k,v in right.items())
    if type(right) is list:
        return type(left) is list and len(left)==len(right) and all(_same_values(a,b) for a,b in zip(left,right))
    if type(right) is bool: return type(left) is bool and left is right
    if type(right) in (int,float): return type(left) in (int,float) and left==right
    return type(left) is type(right) and left==right


def _document(raw, max_bytes=32_000_000):
    if isinstance(raw, str): text = raw
    else:
        _tree(raw)
        text = json.dumps(raw, sort_keys=True, ensure_ascii=False, allow_nan=False)
    try: encoded = text.encode('utf8')
    except UnicodeError as error: raise ValueError('valid UTF-8 JSON required') from error
    if len(encoded) > max_bytes: raise ValueError('sky-track JSON exceeds its declared byte limit')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result: raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    def constant(value): raise ValueError('nonfinite JSON literal: ' + value)
    try: document = json.loads(text.removeprefix('\ufeff'), object_pairs_hook=pairs, parse_constant=constant)
    except (json.JSONDecodeError, RecursionError) as error: raise ValueError('invalid sky-track JSON') from error
    _tree(document)
    if not isinstance(document, dict): raise ValueError('a versioned observation object is required')
    return document, text, hashlib.sha256(encoded).hexdigest()


def _matrix(value, size):
    if not isinstance(value, list) or len(value) != size or any(not isinstance(row, list) or len(row) != size for row in value):
        raise ValueError(f'covariance must be a supplied {size} by {size} matrix')
    matrix = np.array([[_number(v) for v in row] for row in value])
    if not np.array_equal(matrix, matrix.T): raise ValueError('supplied covariance must be symmetric; no averaging is performed')
    try: lower = np.linalg.cholesky(matrix)
    except np.linalg.LinAlgError as error: raise ValueError('supplied covariance must be strictly positive definite') from error
    if not np.all(np.isfinite(lower)): raise ValueError('covariance factorization is numerically unresolved')
    return lower


def _fraction(value): return Fraction.from_float(_number(value))


def _converted(value):
    try: result = float(value)
    except OverflowError as error: raise ValueError('numerical time-axis transformation overflow') from error
    if not math.isfinite(result) or (value and (result == 0 or abs(result) < sys.float_info.min)):
        raise ValueError('numerical time-axis transformation underflow/overflow')
    return result


def _prepare(raw):
    data, text, digest = _document(raw)
    if data.get('schema') != INPUT_SCHEMA or data.get('position_role') != 'LENS_ANGULAR_POSITION':
        raise ValueError('measured foreground-lens angular positions required; source/event directions are not lens astrometry')
    if data.get('position_origin') not in ('DIRECT_LENS_ASTROMETRY', 'INFERRED_LENS_POSITION_FROM_IDENTIFIED_JOINT_MODEL'):
        raise ValueError('explicit direct/inferred lens-position origin required; raw source photocenters are not admitted')
    lens = _text(data.get('lens_id'), 'lens_id'); _text(data.get('association_evidence'), 'association_evidence')
    frame, time, noise = data.get('frame'), data.get('time'), data.get('noise')
    if not all(isinstance(v, dict) for v in (frame, time, noise)): raise ValueError('frame, time and supplied-noise declarations required')
    if frame.get('kind') != 'INERTIAL_TANGENT_PLANE' or frame.get('axes') != ['east', 'north'] or frame.get('angular_unit') != 'mas':
        raise ValueError('declared inertial east/north tangent-plane mas coordinates required')
    for key in ('name', 'reference_origin', 'calibration_source', 'parallax_source'): _text(frame.get(key), 'frame.' + key)
    if type(frame.get('absolute_frame')) is not bool: raise ValueError('absolute_frame must be an explicit boolean')
    if frame.get('parallax_treatment') not in ('CORRECTED_WITH_SUPPLIED_MODEL', 'NOT_MODELED_CONDITIONAL_RECTILINEAR'):
        raise ValueError('explicit corrected or unmodeled-conditional parallax treatment required')
    if time.get('native_unit') not in ('day', 'Julian_year'): raise ValueError('native time unit must be day or Julian_year')
    for key in ('convention', 'scale', 'source'): _text(time.get(key), 'time.' + key)
    if time['scale'] == 'UNSPECIFIED': _text(time.get('qualification'), 'time.qualification')
    _number(time.get('numeric_origin'))
    if noise.get('distribution') != 'GAUSSIAN_KNOWN_SUPPLIED_COVARIANCE' or noise.get('covariance_unit') != 'mas^2':
        raise ValueError('explicit Gaussian known supplied angular covariance in mas^2 required')
    _text(noise.get('covariance_source'), 'noise.covariance_source')
    kind = noise.get('covariance_kind')
    if kind not in ('FULL_2N', 'PER_EPOCH_2X2'): raise ValueError('full2N or per-epoch2x2 covariance route required')
    rows = data.get('rows')
    if not isinstance(rows, list) or not 2 <= len(rows) <= (512 if kind == 'FULL_2N' else 4096):
        raise ValueError('requires2..512 rows for full covariance or2..4096 for per-epoch covariance; resource limits never discard rows')
    times, positions, identities = [], [], []
    for row in rows:
        if not isinstance(row, dict) or row.get('lens_id') != lens: raise ValueError('every row must identify the same supplied lens')
        if row.get('position_role', 'LENS_ANGULAR_POSITION') != 'LENS_ANGULAR_POSITION': raise ValueError('source/event row is not a lens-position measurement')
        identities.append(_text(row.get('source_row_id'), 'source_row_id'))
        _text(row.get('source_reference'), 'source_reference')
        source_hash = row.get('source_file_sha256')
        if not isinstance(source_hash, str) or len(source_hash) != 64 or any(c not in '0123456789abcdef' for c in source_hash):
            raise ValueError('source_file_sha256 must identify the native source bytes')
        p = row.get('position_mas')
        if not isinstance(p, list) or len(p) != 2: raise ValueError('each row requires the measured east,north lens position')
        positions.append([_number(v) for v in p]); times.append(_fraction(row.get('native_time')))
    if len(set(identities)) != len(rows): raise ValueError('source_row_id values must be unique; no silent deduplication')
    if len(set(times)) < 2: raise ValueError('insufficient numerical time rank: at least two distinct represented epochs required')
    if kind == 'FULL_2N':
        if noise.get('cross_epoch_independence') is not None:
            raise ValueError('FULL_2N requires cross_epoch_independence=null; shared correlations are retained')
        if any('covariance_mas2' in row for row in rows): raise ValueError('supply exactly one covariance route')
        factors = [_matrix(data.get('full_covariance_mas2'), 2 * len(rows))]
    else:
        independence = noise.get('cross_epoch_independence')
        if not isinstance(independence, dict) or independence.get('assumed') is not True:
            raise ValueError('per-epoch covariances require explicit cross-epoch independence assumption')
        _text(independence.get('justification'), 'cross_epoch_independence.justification')
        if data.get('full_covariance_mas2') is not None: raise ValueError('supply exactly one covariance route')
        factors = [_matrix(row.get('covariance_mas2'), 2) for row in rows]
    center = (min(times) + max(times)) / 2; halfspan = (max(times) - min(times)) / 2
    years_per_native = Fraction(4, 1461) if time['native_unit'] == 'day' else Fraction(1)
    scale_years = _converted(halfspan * years_per_native)
    x = np.array([_converted((t - center) / halfspan) for t in times])
    y = np.asarray(positions); pivot = y[0].copy(); relative = y - pivot
    if not np.all(np.isfinite(relative)): raise ValueError('position centering is numerically unresolved')
    design = np.zeros((2 * len(rows), 4)); design[0::2, 0] = 1; design[1::2, 1] = 1
    design[0::2, 2] = x; design[1::2, 3] = x
    def whiten(array):
        if kind == 'FULL_2N': return solve_triangular(factors[0], array, lower=True, check_finite=True)
        return np.concatenate([solve_triangular(L, array[2*i:2*i+2], lower=True, check_finite=True) for i, L in enumerate(factors)])
    B, z = whiten(design), whiten(relative.ravel())
    if not all(np.all(np.isfinite(v)) for v in (B, z)):
        raise ValueError('weighted numerical design is unresolved')
    try: singular = np.linalg.svd(B, compute_uv=False)
    except np.linalg.LinAlgError as error: raise ValueError('weighted numerical rank SVD did not converge') from error
    tolerance = max(B.shape) * np.finfo(float).eps * singular[0]
    rank = int(np.sum(singular > tolerance))
    if rank != 4: raise ValueError('weighted affine design lacks numerical rank4; no pseudoinverse/ridge fit is supplied')
    if not all(np.all(np.isfinite(v)) for v in (B, z, singular)): raise ValueError('weighted numerical design is unresolved')
    return dict(data=data, text=text, digest=digest, rows=rows, times=times, center=center, halfspan=halfspan,
                years_per_native=years_per_native, scale_years=scale_years, x=x, y=y, pivot=pivot,
                B=B, z=z, whiten=whiten, singular=singular, tolerance=tolerance, rank=rank)


def validate_skytrack(raw):
    p = _prepare(raw)
    return {'schema': INPUT_SCHEMA, 'valid': True, 'lens_id': p['data']['lens_id'],
            'rows': len(p['rows']), 'unique_epochs': len(set(p['times'])), 'rank': p['rank'],
            'goodness_of_fit_testable': len(set(p['times'])) >= 3, 'input_utf8_sha256': p['digest'],
            'frame': deepcopy(p['data']['frame']), 'time': deepcopy(p['data']['time']),
            'position_origin': p['data']['position_origin'], 'covariance_kind': p['data']['noise']['covariance_kind'],
            'scope': 'Declaration/numerical admission only; external lens association and gravitational identity are not validated.'}


def _qr(B, z):
    try:
        Q, R = np.linalg.qr(B, mode='reduced')
        beta = solve_triangular(R, Q.T @ z, check_finite=True)
        inverse = solve_triangular(R, np.eye(R.shape[0]), check_finite=True)
        covariance = inverse @ inverse.T
    except (np.linalg.LinAlgError, ValueError) as error:
        raise ValueError('linear QR solve is numerically unresolved') from error
    if not all(np.all(np.isfinite(v)) for v in (beta, covariance)):
        raise ValueError('linear QR coefficients/covariance are numerically unresolved')
    return beta, covariance


def _runtime():
    info = getattr(np.__config__, 'CONFIG', {}).get('Build Dependencies', {}).get('blas', {})
    return {'python':platform.python_version(), 'numpy':np.__version__, 'scipy':scipy.__version__,
            'blas':{key:str(info.get(key, 'unavailable')) for key in ('name','version','openblas configuration')}}


def fit_skytrack(raw, *, reference_native_time=None, significance_alpha=None):
    p = _prepare(raw)
    if significance_alpha is not None:
        significance_alpha = _number(significance_alpha)
        if not 0 < significance_alpha < .5: raise ValueError('explicit significance_alpha must lie in(0,0.5)')
    reference = _number(reference_native_time) if reference_native_time is not None else _converted(p['center'])
    beta, covariance = _qr(p['B'], p['z'])
    prediction_centered = np.column_stack((beta[0]+beta[2]*p['x'], beta[1]+beta[3]*p['x']))
    residual = p['y'] - p['pivot'] - prediction_centered
    white = p['whiten'](residual.ravel()); q = float(white @ white)
    static_beta, _ = _qr(p['B'][:, :2], p['z'])
    static_residual = p['z'] - p['B'][:, :2] @ static_beta; static_q = float(static_residual @ static_residual)
    raw_delta = static_q - q
    if raw_delta < -1e-9 * max(1., q, static_q): raise ValueError('nested stationary comparison is numerically unresolved')
    delta = max(0., raw_delta); motion_p = float(chi2.sf(delta, 2))
    xref = _converted((_fraction(reference) - p['center']) / p['halfspan'])
    invscale = 1 / p['scale_years']
    T = np.array([[1,0,xref,0], [0,1,0,xref], [0,0,invscale,0], [0,0,0,invscale]])
    coefficients = T @ beta; coefficients[:2] += p['pivot']
    reported_covariance = T @ covariance @ T.T
    # Symmetrize computed roundoff only, never the supplied observation matrix.
    reported_covariance = (reported_covariance + reported_covariance.T) * .5
    if not np.all(np.isfinite(reported_covariance)) or np.any(np.diag(reported_covariance) <= 0) or not np.all(np.isfinite(coefficients)):
        raise ValueError('reporting-reference coefficient/covariance transform is numerically unresolved')
    try: np.linalg.cholesky(reported_covariance)
    except np.linalg.LinAlgError as error:
        raise ValueError('reporting-reference covariance lost numerical positive definiteness; choose a representable reference') from error
    testable = len(set(p['times'])) >= 3; dof = 2 * len(p['rows']) - 4
    upper = float(chi2.sf(q, dof)) if testable else None
    lower = float(chi2.cdf(q, dof)) if testable else None
    two = min(1., 2 * min(upper, lower)) if testable else None
    status = 'RECTILINEAR_FIT_STATISTICS_ONLY' if testable else 'TWO_EPOCH_FIT_UNTESTED'
    motion_screen = 'NOT_REQUESTED' if testable else 'NOT_CLASSIFIED_TWO_EPOCH_FIT'
    if significance_alpha is not None and testable:
        status = ('RECTILINEAR_MODEL_OR_NOISE_INADEQUATE' if upper <= lower else 'RECTILINEAR_NOISE_UNDERDISPERSED') if two <= significance_alpha else 'RECTILINEAR_TRACK_NOT_REJECTED'
        motion_screen = 'STATIONARY_NULL_REJECTED_CONDITIONALLY' if motion_p <= significance_alpha else 'STATIONARY_NULL_NOT_REJECTED'
    from .interpretation import surface_geometry_interpretation
    result = {'schema': RESULT_SCHEMA, 'status': status, 'dataset_input': deepcopy(p['data']),
        'dataset_input_json': p['text'], 'input_utf8_sha256': p['digest'],
        'method_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'numerical_runtime': _runtime(),
        'numerical_fit': {'centered_scaled_coefficients':beta.tolist(), 'centered_scaled_covariance':covariance.tolist()},
        'fit_configuration': {'reference_native_time': reference, 'significance_alpha': significance_alpha,
                              'goodness_rule': 'TWO_SIDED_CHI_SQUARE_P_LE_ALPHA; stationary motion uses its separate upper-tail alpha'},
        'reference_epoch': {**deepcopy(p['data']['time']), 'native_time': reference},
        'parameter_order': PARAMETER_ORDER.copy(),
        'parameters': {'position_mas': coefficients[:2].tolist(), 'angular_motion_mas_per_Julian_year': coefficients[2:].tolist()},
        'parameter_covariance': reported_covariance.tolist(),
        'standard_errors': {'position_mas': np.sqrt(np.diag(reported_covariance)[:2]).tolist(),
                            'angular_motion_mas_per_Julian_year': np.sqrt(np.diag(reported_covariance)[2:]).tolist()},
        'predictions_mas': (prediction_centered + p['pivot']).tolist(), 'residuals_mas': residual.tolist(),
        'whitened_residuals': white.tolist(), 'source_row_ids': [r['source_row_id'] for r in p['rows']],
        'diagnostics': {'chi_square': q, 'degrees_of_freedom': dof, 'unique_epochs': len(set(p['times'])),
            'goodness_of_fit_testable': testable, 'chi_square_upper_probability': upper, 'chi_square_lower_probability': lower,
            'chi_square_two_sided_probability': two, 'stationary_null_delta_chi_square': delta,
            'stationary_null_delta_before_roundoff_clip': raw_delta, 'stationary_null_motion_dof': 2,
            'stationary_null_probability': motion_p, 'motion_screen': motion_screen,
            'rank': p['rank'], 'rank_tolerance': float(p['tolerance']), 'singular_values': p['singular'].tolist(),
            'condition_number': float(p['singular'][0] / p['singular'][-1]),
            'stationarity_residual': float(np.linalg.norm(p['B'].T @ white, ord=np.inf)),
            'numerical_basis': {'center_native_exact_ratio': str(p['center']), 'scale_Julian_years': p['scale_years'],
                                'position_pivot_mas': p['pivot'].tolist()}},
        'unavailable': deepcopy(UNAVAILABLE), 'surface_geometry_interpretation': surface_geometry_interpretation(),
        'qualifications': ['Input declarations do not independently validate common-lens association or foreground identity.',
            'Covariance is supplied; Gaussian noise and any cross-epoch independence are declared assumptions. Errors are not rescaled by residuals.',
            'Motion is in the supplied frame; frame, clock and parallax corrections are not invented.',
            'Nonlinearity or noise rejection may reflect parallax, acceleration, association or calibration; it does not exclude a black hole.',
            'This measured-astrometry route is not the only possible future source of track evidence; multi-event association requires a separate likelihood.',
            'No mass, distance, physical transverse speed, horizon, microscopic interface or known-black-hole recovery is inferred.']}
    _tree(result)
    return result


def replay_skytrack(result):
    """Check source/input plus conditioned numerical consistency, not validity.

    The engineering budget and its refusal cap are prospective policy, not a
    rigorous floating-point enclosure or a change to statistical covariance.
    Original cross-runtime failed bitwise witnesses are retained in the review.
    """
    if not isinstance(result, dict) or result.get('schema') != RESULT_SCHEMA: raise ValueError('a versioned sky-track result is required')
    _tree(result)
    source = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if result.get('method_source_sha256') != source: raise ValueError('sky-track method source differs; retain matching source or explicitly refit')
    text = result.get('dataset_input_json')
    if not isinstance(text, str) or hashlib.sha256(text.encode('utf8')).hexdigest() != result.get('input_utf8_sha256'):
        raise ValueError('sky-track input byte hash mismatch')
    parsed, _, _ = _document(text)
    if not _same_values(result.get('dataset_input'),parsed): raise ValueError('parsed observation values differ from the retained original JSON')
    config = result.get('fit_configuration')
    if not isinstance(config, dict) or set(config) != {'reference_native_time','significance_alpha','goodness_rule'}: raise ValueError('sky-track settings are missing or unsupported')
    actual = fit_skytrack(text, reference_native_time=config['reference_native_time'], significance_alpha=config['significance_alpha'])
    if set(result) != set(actual): raise ValueError('sky-track result fields differ from the versioned result schema')
    for key in ('parameters','standard_errors','numerical_fit','diagnostics','numerical_runtime'):
        if type(result.get(key)) is not dict or set(result[key])!=set(actual[key]):
            raise ValueError('sky-track result object fields differ: '+key)
    checks = {}
    for key in ('status','fit_configuration','reference_epoch','parameter_order','source_row_ids','unavailable',
                'qualifications','surface_geometry_interpretation'):
        checks[key] = _same_values(result.get(key),actual[key])
    p = _prepare(text); m = len(p['z']); condition = actual['diagnostics']['condition_number']
    relative_budget = float(64 * max(m,4) * np.finfo(float).eps * (1 + condition**2))
    if not math.isfinite(relative_budget) or relative_budget > 1e-6:
        raise ValueError('conditioned replay budget exceeds declared1e-6 precision cap; comparison unresolved')
    white_budget = relative_budget * max(1., float(np.linalg.norm(p['z'])), float(np.linalg.norm(actual['whitened_residuals'])))
    if not math.isfinite(white_budget):
        raise ValueError('whitened replay budget overflow; comparison unresolved')
    def array(value, shape):
        out = np.asarray(value, dtype=object)
        if out.shape != shape: raise ValueError('sky-track replay array shape differs')
        return np.array([_number(v) for v in out.ravel()]).reshape(shape)
    def covariance_error(saved, expected):
        A = array(expected, (4,4)); S = array(saved, (4,4))
        if not np.array_equal(S,S.T): return math.inf
        try:
            L = np.linalg.cholesky(A); np.linalg.cholesky(S)
            W = solve_triangular(L,S,lower=True)
            W = solve_triangular(L,W.T,lower=True).T
            return float(np.max(np.abs(np.linalg.eigvalsh((W+W.T)*.5-np.eye(4)))))
        except np.linalg.LinAlgError: return math.inf
    expected_cov = array(actual['parameter_covariance'], (4,4))
    theta = np.concatenate([array(result['parameters'][key], (2,)) for key in ('position_mas','angular_motion_mas_per_Julian_year')])
    expected_theta = np.concatenate([array(actual['parameters'][key], (2,)) for key in ('position_mas','angular_motion_mas_per_Julian_year')])
    state_difference = float(np.linalg.norm(solve_triangular(np.linalg.cholesky(expected_cov),theta-expected_theta,lower=True)))
    gamma = array(result['numerical_fit']['centered_scaled_coefficients'], (4,))
    expected_gamma = np.asarray(actual['numerical_fit']['centered_scaled_coefficients'])
    gamma_difference = float(np.linalg.norm(p['B']@(gamma-expected_gamma)))
    prediction_difference = float(np.linalg.norm(p['whiten']((array(result['predictions_mas'],p['y'].shape)-np.asarray(actual['predictions_mas'])).ravel())))
    residual_difference = float(np.linalg.norm(p['whiten']((array(result['residuals_mas'],p['y'].shape)-np.asarray(actual['residuals_mas'])).ravel())))
    white_difference = float(np.linalg.norm(array(result['whitened_residuals'],(m,))-np.asarray(actual['whitened_residuals'])))
    cov_error = covariance_error(result['parameter_covariance'], actual['parameter_covariance'])
    basis_cov_error = covariance_error(result['numerical_fit']['centered_scaled_covariance'], actual['numerical_fit']['centered_scaled_covariance'])
    checks.update(parameters=state_difference<=white_budget, numerical_fit=gamma_difference<=white_budget and basis_cov_error<=relative_budget,
                  predictions_mas=prediction_difference<=white_budget, residuals_mas=residual_difference<=white_budget,
                  whitened_residuals=white_difference<=white_budget, parameter_covariance=cov_error<=relative_budget)
    errors = np.concatenate([array(result['standard_errors'][key], (2,)) for key in ('position_mas','angular_motion_mas_per_Julian_year')])
    checks['standard_errors'] = bool(np.all(errors>0) and np.max(np.abs(errors**2/np.diag(expected_cov)-1))<=relative_budget)
    diagnostic = result.get('diagnostics', {}); expected = actual['diagnostics']
    for key in ('chi_square_upper_probability','chi_square_lower_probability','chi_square_two_sided_probability','stationary_null_probability'):
        if diagnostic[key] is not None and not 0 <= _number(diagnostic[key]) <= 1:
            raise ValueError('sky-track diagnostic probability outside its natural range: '+key)
    for key in ('chi_square','stationary_null_delta_chi_square','stationarity_residual'):
        if _number(diagnostic[key]) < 0:
            raise ValueError('sky-track diagnostic outside its nonnegative natural range: '+key)
    if _number(diagnostic['rank_tolerance']) <= 0 or _number(diagnostic['condition_number']) < 1:
        raise ValueError('sky-track diagnostic rank/condition outside its natural range')
    values=array(diagnostic['singular_values'],(4,))
    if np.any(values<=0) or np.any(values[1:]>values[:-1]):
        raise ValueError('sky-track diagnostic singular values outside their positive descending range')
    exact_keys = ('degrees_of_freedom','unique_epochs','goodness_of_fit_testable','stationary_null_motion_dof','motion_screen','rank','numerical_basis')
    checks['diagnostic_exact_fields'] = set(diagnostic)==set(expected) and all(_same_values(diagnostic.get(k),expected[k]) for k in exact_keys)
    # Saved probabilities must describe their OWN statistics, independently of
    # the potentially coarse cross-runtime Q allowance for very large signals.
    if not checks['diagnostic_exact_fields']:
        raise ValueError('sky-track exact diagnostic fields differ')
    def same_tail(saved, recomputed):
        if recomputed is None: return saved is None
        saved=_number(saved)
        if recomputed==0: return saved==0  # Never borrow an absolute tolerance at underflow.
        if saved<=0: return False
        return abs(_fraction(saved)-_fraction(recomputed))<=_fraction(relative_budget)*_fraction(recomputed)
    saved_q=_number(diagnostic['chi_square']);saved_delta=_number(diagnostic['stationary_null_delta_chi_square'])
    testable=diagnostic['goodness_of_fit_testable'];df=diagnostic['degrees_of_freedom']
    own_upper=float(chi2.sf(saved_q,df)) if testable else None
    own_lower=float(chi2.cdf(saved_q,df)) if testable else None
    own_two=min(1.,2*min(own_upper,own_lower)) if testable else None
    own_motion=float(chi2.sf(saved_delta,2))
    checks['diagnostic_saved_tail_coherence']=all(same_tail(diagnostic[key],value) for key,value in (
        ('chi_square_upper_probability',own_upper),('chi_square_lower_probability',own_lower),
        ('chi_square_two_sided_probability',own_two),('stationary_null_probability',own_motion)))
    own_status='RECTILINEAR_FIT_STATISTICS_ONLY' if testable else 'TWO_EPOCH_FIT_UNTESTED'
    own_screen='NOT_REQUESTED' if testable else 'NOT_CLASSIFIED_TWO_EPOCH_FIT'
    alpha=config['significance_alpha']
    if alpha is not None and testable:
        own_status=(('RECTILINEAR_MODEL_OR_NOISE_INADEQUATE' if diagnostic['chi_square_upper_probability']<=diagnostic['chi_square_lower_probability'] else 'RECTILINEAR_NOISE_UNDERDISPERSED')
            if diagnostic['chi_square_two_sided_probability']<=alpha else 'RECTILINEAR_TRACK_NOT_REJECTED')
        own_screen='STATIONARY_NULL_REJECTED_CONDITIONALLY' if diagnostic['stationary_null_probability']<=alpha else 'STATIONARY_NULL_NOT_REJECTED'
    checks['diagnostic_saved_status_coherence']=result['status']==own_status and diagnostic['motion_screen']==own_screen
    checks['diagnostic_saved_delta_clip_coherence']=saved_delta==max(0.,_number(diagnostic['stationary_null_delta_before_roundoff_clip']))
    q_budget = (2*float(np.linalg.norm(actual['whitened_residuals']))*white_budget+white_budget*white_budget
                +2*relative_budget*max(1.,expected['chi_square']+expected['stationary_null_delta_chi_square']))
    stationarity_budget = (float(p['singular'][0])*white_budget
        +relative_budget*float(p['singular'][0])*max(1.,float(np.linalg.norm(actual['whitened_residuals']))))
    if not math.isfinite(q_budget) or not math.isfinite(stationarity_budget):
        raise ValueError('diagnostic replay budget overflow; comparison unresolved')
    for key in expected:
        if key in exact_keys: continue
        a,b = diagnostic.get(key),expected[key]
        if b is None: checks['diagnostic_'+key]=a is None
        elif 'probability' in key: checks['diagnostic_'+key]=abs(_number(a)-b)<=min(1.,q_budget+relative_budget)
        elif key in ('chi_square','stationary_null_delta_chi_square','stationary_null_delta_before_roundoff_clip'):
            checks['diagnostic_'+key]=abs(_number(a)-b)<=q_budget
        elif key=='stationarity_residual':
            checks['diagnostic_'+key]=abs(_number(a)-b)<=stationarity_budget
        else:
            B=np.asarray(b,dtype=float);A=array(a,B.shape)
            checks['diagnostic_'+key]=A.shape==B.shape and bool(np.all(np.abs(A-B)<=relative_budget*np.maximum(1.,np.abs(B))))
    if not all(checks.values()): raise ValueError('sky-track saved result differs from conditioned replay: ' + ', '.join(k for k,v in checks.items() if not v))
    numeric_keys=('parameters','parameter_covariance','standard_errors','predictions_mas','residuals_mas','whitened_residuals','diagnostics','numerical_fit')
    return {'schema':'bhtracker.measured_lens_skytrack_replay.v1', 'passed':True, 'checks':checks,
            'input_utf8_sha256':actual['input_utf8_sha256'], 'method_source_sha256':source,
            'exact_numeric_match':all(actual[k]==result[k] for k in numeric_keys),
            'recorded_numerical_runtime':result['numerical_runtime'],'current_numerical_runtime':actual['numerical_runtime'],
            'numerical_comparison':{'relative_budget':relative_budget,'precision_refusal_cap':1e-6,'whitened_budget':white_budget,
                'state_difference_in_covariance_metric':state_difference,'centered_prediction_difference':gamma_difference,
                'prediction_difference':prediction_difference,'residual_difference':residual_difference,
                'whitened_residual_difference':white_difference,'maximum_fractional_variance_error':cov_error,
                'centered_fractional_variance_error':basis_cov_error,'chi_square_comparison_budget':q_budget,
                'stationarity_comparison_budget':stationarity_budget,
                'qualification':'Declared dimension/epsilon/conditioning engineering comparison, not a rigorous enclosure or covariance rescaling.'},
            'scope':'Content and numerical linear-solve consistency only; no new scientific validation, lens association or black-hole identification.'}


def export_skytrack(result, directory):
    check = replay_skytrack(result)
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=False)
    (directory/'dataset.json').write_bytes(result['dataset_input_json'].encode('utf8'))
    for name, value in (('result.json',result),('replay_check.json',check)):
        with (directory/name).open('x',encoding='utf8',newline='\n') as stream: json.dump(value,stream,indent=2,allow_nan=False)
    (directory/'README.txt').write_bytes(b'Measured lens angular track only. Run: python -m bhtracker skytrack replay result.json\nSource identity and byte replay do not validate gravitational origin or black-hole identity.\n')
    return {'export_directory':str(directory.resolve()), **check}


def synthetic_example():
    """Constructed angular positions, never a known/observed black-hole result."""
    times = [-4., -2.25, -.5, .75, 2.5, 4.75]
    offsets = [[.15,-.08],[-.12,.23],[.07,-.2],[-.19,.13],[.1,-.17],[-.04,.09]]
    return {'schema':INPUT_SCHEMA,'lens_id':'SYNTHETIC-LENS','position_role':'LENS_ANGULAR_POSITION',
        'position_origin':'DIRECT_LENS_ASTROMETRY','association_evidence':'Invented same-object control; not observational evidence.',
        'frame':{'name':'SYNTHETIC-INERTIAL-TANGENT','kind':'INERTIAL_TANGENT_PLANE','axes':['east','north'],'angular_unit':'mas',
            'reference_origin':'Constructed tangent origin; no sky position assigned.','absolute_frame':False,
            'calibration_source':'Invented control, no measured calibration.', 'parallax_treatment':'NOT_MODELED_CONDITIONAL_RECTILINEAR',
            'parallax_source':'No annual parallax in the constructed signal.'},
        'time':{'native_unit':'day','numeric_origin':2450000.,'convention':'native_time + numeric_origin, JD_TDB for constructed control',
                'scale':'TDB','source':'Invented epochs; one Julian year is365.25 days.'},
        'noise':{'distribution':'GAUSSIAN_KNOWN_SUPPLIED_COVARIANCE','covariance_kind':'PER_EPOCH_2X2','covariance_unit':'mas^2',
                 'covariance_source':'Invented positive-definite test matrices; no empirical covariance claim.',
                 'cross_epoch_independence':{'assumed':True,'justification':'Explicit constructed control assumption.'}},
        'rows':[{'source_row_id':f'synthetic:{i+1}','source_file_sha256':hashlib.sha256(b'INVENTED-SKYTRACK-CONTROL').hexdigest(),
                 'source_reference':'Synthetic example generated by bhtracker.skytrack.synthetic_example; no observation file.',
                 'lens_id':'SYNTHETIC-LENS','native_time':6000.+365.25*t,
                 'position_mas':[12.+80.*t+offsets[i][0],-8.-30.*t+offsets[i][1]],
                 'covariance_mas2':[[.04,.01],[.01,.09]]} for i,t in enumerate(times)],
        'full_covariance_mas2':None,'metadata':{'kind':'synthetic','synthetic':True,'true_reference_native_time':6000.,
        'true_position_mas':[12.,-8.],'true_angular_motion_mas_per_Julian_year':[80.,-30.],'known_black_hole':False}}
