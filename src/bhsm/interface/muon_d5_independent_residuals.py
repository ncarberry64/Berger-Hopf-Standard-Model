"""Independent strong D5 checks, separated from collocation solve checks.

The field callback returns the differentiated declared solution polynomial;
the coefficient callback rebuilds the original unsquared differential operator.
Neither callback may replace a derivative by the equation being checked.
"""
from __future__ import annotations

import numpy as np
from scipy.interpolate import BarycentricInterpolator
from numpy.polynomial import Polynomial
from numpy.polynomial.legendre import leggauss
from pathlib import Path
from hashlib import sha256
import json


FIELD_KEYS = ('value', 'time', 'radial', 'source', 'time_source', 'radial_source')
COEFFICIENT_KEYS = ('time', 'radial', 'body', 'time_source', 'radial_source', 'body_source')


def _apply(coefficient, field):
    """Full carrier or explicitly repeated equal-size carrier blocks."""
    a = np.asarray(coefficient, complex)
    v = np.asarray(field, complex)
    if v.ndim != 2:
        raise ValueError('field must be carrier by input-column')
    if a.ndim == 2 and a.shape == (v.shape[0], v.shape[0]):
        return a @ v
    if a.ndim == 3 and a.shape[1] == a.shape[2] and a.shape[0]*a.shape[1] == v.shape[0]:
        return np.einsum('bij,bjk->bik', a, v.reshape(a.shape[0], a.shape[1], -1)).reshape(v.shape)
    raise ValueError('coefficient and full carrier identities do not match')


def original_strong_rows(field, coefficients):
    """D5 V and its complete first source at one independent point.

    R_x V_r + T_x V_t + K_x V + R V_rx + T V_tx + K V_x.
    The two source placements are retained separately for localization.
    """
    if any(k not in field for k in FIELD_KEYS) or any(k not in coefficients for k in COEFFICIENT_KEYS):
        raise ValueError('complete field and coefficient source derivatives required')
    f = {k: np.asarray(field[k], complex) for k in FIELD_KEYS}
    if any(a.shape != f['value'].shape or not np.isfinite(a).all() for a in f.values()):
        raise ValueError('same finite carrier/input columns required for every derivative')
    parts = dict(radial=_apply(coefficients['radial'], f['radial']),
        time=_apply(coefficients['time'], f['time']),
        body=_apply(coefficients['body'], f['value']),
        source_vertex_radial=_apply(coefficients['radial_source'], f['radial']),
        source_vertex_time=_apply(coefficients['time_source'], f['time']),
        source_vertex_body=_apply(coefficients['body_source'], f['value']),
        source_field_radial=_apply(coefficients['radial'], f['radial_source']),
        source_field_time=_apply(coefficients['time'], f['time_source']),
        source_field_body=_apply(coefficients['body'], f['source']))
    parts['strong'] = parts['radial'] + parts['time'] + parts['body']
    parts['source_vertex'] = sum(parts['source_vertex_'+k] for k in ('radial', 'time', 'body'))
    parts['source_field'] = sum(parts['source_field_'+k] for k in ('radial', 'time', 'body'))
    parts['strong_source'] = parts['source_vertex'] + parts['source_field']
    return parts


def _norms(array):
    a = np.asarray(array)
    return dict(max_abs=float(np.max(np.abs(a))), frobenius=float(np.linalg.norm(a)))


def independent_residual_application(field_evaluate, coefficient_evaluate, points, *,
        comparison_coefficient_evaluate=None, carrier_block_size=64):
    """Evaluate ORIGINAL equations at explicit independent (time, radial) points.

    A comparison coefficient callback may be a nodal interpolant.  Its
    difference is reported separately; it never replaces the original rows.
    Term-scaled diagnostics are conditioning checks, not admission norms.
    """
    p = np.asarray(points, float)
    if p.ndim != 2 or p.shape[1] != 2 or not len(p) or not np.isfinite(p).all():
        raise ValueError('finite nonempty independent (time,radial) point list required')
    rows = []
    comparisons = []
    field_values = []
    for t, r in p:
        f = field_evaluate(float(t), float(r))
        rows.append(original_strong_rows(f, coefficient_evaluate(float(t), float(r))))
        field_values.append(np.asarray(f['value'], complex))
        if comparison_coefficient_evaluate is not None:
            comparisons.append(original_strong_rows(f, comparison_coefficient_evaluate(float(t), float(r))))
    arrays = {k: np.array([a[k] for a in rows]) for k in rows[0]}
    arrays.update(points=p, field_value=np.array(field_values))
    report = dict(norm='max absolute original strong coordinate-component residual across stated points/input columns',
        point_count=len(p), field_input_columns=int(arrays['strong'].shape[-1]),
        field_value=_norms(arrays['field_value']), original_bulk=_norms(arrays['strong']),
        original_source=_norms(arrays['strong_source']),
        source_vertex=_norms(arrays['source_vertex']), source_field=_norms(arrays['source_field']),
        original_equation='R V_r + T V_t + K V; complete source derivative',
        finite_arithmetic_not_continuum_or_physical_admission=True)
    for key, terms in (('bulk', ('radial', 'time', 'body')),
            ('source', tuple('source_'+place+'_'+k for place in ('vertex', 'field') for k in ('radial', 'time', 'body')))):
        scale = sum(float(np.max(abs(arrays[k]))) for k in terms)
        residual = report['original_'+key]['max_abs']
        report[key+'_term_scale'] = scale
        report[key+'_term_scaled_relative'] = residual/scale if scale else (0. if residual == 0. else None)
    d = arrays['strong'].shape[-2]
    if type(carrier_block_size) is not int or carrier_block_size < 1 or d % carrier_block_size:
        raise ValueError('explicit carrier blocks must cover full carrier')
    report['carrier_blocks'] = []
    for start in range(0, d, carrier_block_size):
        sl = slice(start, start+carrier_block_size)
        report['carrier_blocks'].append(dict(start=start, stop=start+carrier_block_size,
            bulk=_norms(arrays['strong'][:, sl]), source=_norms(arrays['strong_source'][:, sl])))
    if comparisons:
        for key in ('strong', 'strong_source'):
            arrays['comparison_'+key] = np.array([a[key] for a in comparisons])
            arrays['coefficient_difference_'+key] = arrays[key]-arrays['comparison_'+key]
        report['comparison_bulk'] = _norms(arrays['comparison_strong'])
        report['comparison_source'] = _norms(arrays['comparison_strong_source'])
        report['coefficient_application_difference_bulk'] = _norms(arrays['coefficient_difference_strong'])
        report['coefficient_application_difference_source'] = _norms(arrays['coefficient_difference_strong_source'])
    return arrays, report


class SavedOneStepPolynomialField:
    """Reuse a saved degree-5-time/degree-3-radial consumed field.

    Its initial value and three saved Gauss slopes identify the original
    cubic dense output.  Derivatives are evaluated from that polynomial,
    independently of G V.  Stored physical-rho rounding is exposed by
    ``saved_derivative_checks``.  No field solve
    or discarded homogeneous datum is introduced here.
    """
    def __init__(self, shared, saved, prefix):
        self.times = np.asarray(shared['times'], float)
        self.radial_nodes = np.asarray(shared['radial_nodes'], float)
        if len(self.times) != 6 or len(self.radial_nodes) != 5 or np.any(np.asarray(shared['radial_node_step']) != 0):
            raise ValueError('saved original six-time/one-step cubic radial chart required')
        self.t0 = self.times[0]
        self.dt = self.times[-1]-self.t0
        self.r0 = self.radial_nodes[0]
        self.dr = self.radial_nodes[-1]-self.r0
        if not self.dt > 0 or not self.dr < 0:
            raise ValueError('ordered original time and inward radial chart required')
        self.time_basis = BarycentricInterpolator((self.times-self.t0)/self.dt, np.eye(6), axis=0)
        self.gauss = (leggauss(3)[0]+1)/2
        self.radial_polynomials = []
        self.radial_integrals = []
        for j in range(3):
            p = Polynomial([1.])
            for k in range(3):
                if k != j:
                    p *= Polynomial([-self.gauss[k], 1.])/(self.gauss[j]-self.gauss[k])
            self.radial_polynomials.append(p)
            self.radial_integrals.append(p.integ())
        self.saved = {k: np.asarray(saved[prefix+'_'+k], complex) for k in FIELD_KEYS}
        if any(v.shape[:2] != (5, 6) for v in self.saved.values()):
            raise ValueError('same saved radial/time axes required')

    def __call__(self, time, radial):
        z = (time-self.t0)/self.dt
        x = (radial-self.r0)/self.dr
        if not -1e-12 <= z <= 1+1e-12 or not -1e-8 <= x <= 1+1e-8:
            raise ValueError('independent point outside declared incoming strip')
        tw = self.time_basis(z)
        td = self.time_basis.derivative(z)/self.dt
        integral = np.array([p(x)-p(0.) for p in self.radial_integrals])
        radial_weights = np.array([p(x) for p in self.radial_polynomials])
        value = lambda initial, slopes, time: np.einsum('t,tdk->dk', time, initial) + self.dr*np.einsum(
            'r,t,rtdk->dk', integral, time, slopes)
        derivative = lambda slopes: np.einsum('r,t,rtdk->dk', radial_weights, tw, slopes)
        v, vx = self.saved['value'][0], self.saved['source'][0]
        vr, vrx = self.saved['radial'][1:4], self.saved['radial_source'][1:4]
        return dict(value=value(v, vr, tw), time=value(v, vr, td), radial=derivative(vr),
            source=value(vx, vrx, tw), time_source=value(vx, vrx, td), radial_source=derivative(vrx))

    def saved_derivative_checks(self):
        errors = {k: 0. for k in FIELD_KEYS}
        for i, r in enumerate(self.radial_nodes):
            for j, t in enumerate(self.times):
                got = self(float(t), float(r))
                for k in errors:
                    errors[k] = max(errors[k], float(np.max(abs(got[k]-self.saved[k][i, j]))))
        return errors


class RecoveredOriginalPhase:
    """The original exported one-cell affine history, without an ancestor solve.

    The constructor consumes the saved phase reconstruction operands, signed
    receipt span, and explicit sample times.  Its first source is the exact
    within-cell time-translation direction, not a free background variation.
    """
    def __init__(self, operands, *, span, side, times):
        if side not in ('incoming', 'outgoing') or not np.isfinite(span) or span == 0:
            raise ValueError('original signed incoming/outgoing cell required')
        key = 'stage_midpoint_raw' if side == 'incoming' else 'stage_independent_raw'
        p = np.asarray(operands['resolved_phase_coordinate_lift'])
        stages = np.asarray(operands[key])
        if p.shape != (268, 252) or stages.shape != (1, 268):
            raise ValueError('one original raw268 midpoint and full252 canonical lift required')
        self.stage = stages[0].copy()
        eta = p.T @ self.stage
        if np.max(abs(p @ eta-self.stage)) > 1e-12:
            raise ValueError('original stage lies outside saved phase lift')
        self.rate = p[:, :106] @ eta[106:212]
        self.midpoint = float(span)/2
        self.span = float(span)
        self.side = side
        self.times = np.asarray(times, float)
        if self.times.shape != (6,) or not np.all(np.diff(self.times) > 0) or (
                self.times[0] != min(0., span) or self.times[-1] != max(0., span)):
            raise ValueError('actual six exported times on the same original cell required')

    def _domain(self, time):
        if not np.isfinite(time) or not self.times[0]-1e-14 <= np.real(time) <= self.times[-1]+1e-14:
            raise ValueError('original finite history may not be extrapolated')

    def value(self, time):
        self._domain(time)
        return self.stage+(time-self.midpoint)*self.rate, self.rate.copy()

    def source(self, time):
        self._domain(time)
        return self.rate.copy(), np.zeros_like(self.rate)


def recovered_export_history(root, side, times, raw, rates):
    """Verify the recovered original callback against all current samples.

    The narrow copied archive operands retain their original bytes and hashes.
    No source loader, phase solve, or frozen-basis initializer is run.
    """
    root = Path(root)
    folder = root/'artifacts/muon_d5_valid_domain_application_20261019/inputs'
    provenance_path = folder/'PROVENANCE.json'
    provenance = json.loads(provenance_path.read_bytes())
    pins = {provenance_path.relative_to(root).as_posix(): sha256(provenance_path.read_bytes()).hexdigest()}
    for relative, record in provenance['files'].items():
        path = folder/relative
        actual = sha256(path.read_bytes()).hexdigest()
        if actual != record['sha256']:
            raise ValueError('original recovered operand changed: '+relative)
        pins[path.relative_to(root).as_posix()] = actual
    if side not in ('incoming', 'outgoing'):
        raise ValueError('explicit original history required')
    receipt = json.loads((folder/side/'original_phase_receipt.json').read_bytes())
    if receipt['steps'] != 1 or receipt['completed_steps'] != 1:
        raise ValueError('this recovered callback owns exactly one original cell')
    with np.load(folder/side/'phase_reconstruction_operands.npz', allow_pickle=False) as z:
        operands = {k: z[k] for k in z.files}
    history = RecoveredOriginalPhase(operands, span=receipt['span'], side=side, times=times)
    history.original_phase_operands = operands
    original_raw = np.array([history.value(t)[0] for t in times])
    original_rates = np.array([history.value(t)[1] for t in times])
    if not np.array_equal(original_raw, raw) or not np.array_equal(original_rates, rates):
        raise ValueError('original callback does not reproduce every current raw/rate sample exactly')
    with np.load(folder/side/'original_radial_frame.npz', allow_pickle=False) as z:
        rep = {k: z[k] for k in z.files}
    rep.update(json.loads((folder/side/'original_radial_frame.json').read_bytes()))
    from .muon_birth_trace_enriched_action import trace_enriched_radial_basis

    def gauge_basis(rho):
        b = trace_enriched_radial_basis(rep, np.asarray(rho, float))[0]
        out = np.zeros((len(b), 20, 80))
        for k in range(4):
            out[:, :, 20*k:20*(k+1)] = b[:, k, None, None]*np.eye(20)
        return out
    history.gauge_basis = gauge_basis
    history.original_radial_representation = rep
    return history, dict(schema='bhsm.original-export-callback-recovery.v1', side=side,
        input_sha256=pins, span=receipt['span'], steps=1,
        all_six_raw268_bitwise_match=True, all_six_rate268_bitwise_match=True,
        raw_max_difference=0., rate_max_difference=0.,
        original_callback='stage+(t−span/2)*(P[:,:106]@(P.T@stage)[106:212])',
        gauge_radial_basis='two regular interior polynomials, exact stored affine source complement, wall lift',
        physical_history=False, original_provisional_phase_limitations_preserved=True)


def original_d5_coefficient_callback(history_evaluate, *, sheet_orientation, gauge_basis_evaluate=None):
    """Parent-history original callback; all three families and both carriers.

    ``history_evaluate(t)`` explicitly supplies (raw268, rate268).  A legacy
    value/rate interpolant and a consistent Hermite history are different
    callbacks and must be named separately by the checkpoint consumer.
    """
    if sheet_orientation not in (-1, 1):
        raise ValueError('opposite eta collar sign required')
    from .muon_adopted_incoming_reference import static_field_maps
    from .muon_combined_f_eta_contact import combined_f_eta_contact
    from .muon_full_d5_source_first import full_d5_differential_source_first
    from .muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
    from .muon_holomorphic_d5_trace_action import d5_trial_stage_coefficients
    full = full_d5_localized_lepton_trace()

    def evaluate(time, radial):
        raw, rate = (np.asarray(a, complex) for a in history_evaluate(time))
        if raw.shape != (268,) or rate.shape != (268,):
            raise ValueError('same complete original parent raw/rate history required')
        rho = np.array([radial], float)
        basis = (static_field_maps(rho, enrich_temporal=False)[0]
            if gauge_basis_evaluate is None else np.asarray(gauge_basis_evaluate(rho)))
        if basis.shape != (1, 20, 80):
            raise ValueError('original gauge coordinate map must have shape(radial,20,80)')
        rep = dict(rho=rho, gauge_basis=basis.transpose(0, 2, 1).reshape(1, 80, 1, 5, 4))
        c = d5_trial_stage_coefficients(raw, rate[:, None], raw, rate[:, None], np.array([raw, raw]),
            np.array([rate[:, None], rate[:, None]]), rep, rho, side='parent')
        eta, etax = {}, {}
        for branch in ('particle', 'conjugate'):
            e = combined_f_eta_contact(c, gamma=full['gamma5D_'+branch], carrier_count=16,
                angular_count=1, sheet_orientation=sheet_orientation)
            eta[branch] = e['combined_f_eta_contact']
            etax[branch] = e['combined_f_eta_contact_first'][0]
        a = full_d5_differential_source_first(c, np.zeros((3, 1, 1)), source_slot=0,
            sheet_orientation=sheet_orientation, full_representation=full,
            eta_contacts=eta, eta_contacts_first=etax)
        out = {}
        for k in ('time', 'radial', 'body'):
            out[k] = np.array([a['value']['blocks'][branch][k][0]
                for family in range(3) for branch in ('particle', 'conjugate')])
            out[k+'_source'] = np.array([a['first']['blocks'][branch][k][0]
                for family in range(3) for branch in ('particle', 'conjugate')])
        return out
    return evaluate
