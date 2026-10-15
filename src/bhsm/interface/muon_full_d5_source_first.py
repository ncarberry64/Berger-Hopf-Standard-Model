"""Full D5 directional coefficient/application derivatives on supplied germs.

All source slots, trial/dual contacts and coordinate-weight derivatives are
explicit. The independent analytic left is never conjugated. The separately
named positive form is for a REAL source axis and explicit positive Riesz
data only; no physical outgoing/domain derivative is inferred from it.
"""
from __future__ import annotations

import numpy as np

from bhsm.interface.muon_full_d5_differential_form import (
    full_d5_differential_coefficients, apply_full_d5_expression,
)
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_holomorphic_d5_trace_action import d5_sigma_foliation_eta


def _finite(value, shape, name):
    a = np.asarray(value, complex)
    if a.shape != shape or not np.isfinite(a).all():
        raise ValueError(name + ': explicit finite shape ' + str(shape) + ' required')
    return a


def full_d5_differential_source_first(c, angular_derivatives, *, source_slot,
        sheet_orientation, full_representation=None, eta_contacts=None,
        eta_contacts_first=None):
    """Differentiate one supplied c[*_first] slot, retaining full384h rows.

    The angular coefficient basis and Eulerian Clifford frame are fixed.
    Moving physical frames/test maps require their explicit trial/dual
    derivatives at application. This is not a derivative of a solved tail.
    """
    if type(source_slot) is not int or source_slot < 0:
        raise ValueError('explicit nonnegative source slot required')
    if (eta_contacts is None) != (eta_contacts_first is None):
        raise ValueError('both actual eta contact and its first are required together')
    f = full_d5_localized_lepton_trace() if full_representation is None else full_representation
    base = full_d5_differential_coefficients(c, angular_derivatives,
        sheet_orientation=sheet_orientation, full_representation=f,
        sigma_eta_contacts=eta_contacts)
    q, h, d = base['radial_count'], base['angular_count'], base['block_width']
    if q < 1:
        raise ValueError('nonempty supplied coefficient germ required')
    eps = base['sheet_orientation']
    names = ('lapse', 'radial_coframe', 'radius', 'coordinate_shift',
             'geometric_time_contact', 'geometric_radial_contact',
             'surface_proper_clock_rate', 'volume_density', 'gauge_connection_material')
    first = {}
    for name in names:
        if name + '_first' not in c:
            raise ValueError('explicit source first required: ' + name)
        a = np.asarray(c[name + '_first'], complex)
        shape = (q, 5, 4) if name == 'gauge_connection_material' else (q,)
        if a.ndim != len(shape) + 1 or a.shape[1:] != shape or source_slot >= len(a) or not np.isfinite(a).all():
            raise ValueError('same source slot and point axes required: ' + name)
        first[name] = a[source_slot]
    blocks = {}
    for branch in ('particle', 'conjugate'):
        gamma = np.asarray(f['gamma5D_' + branch], complex)
        g = np.array([np.kron(a, np.eye(16 * h)) for a in gamma])
        gen = np.asarray(f['unitTr16_gauge_particle'], complex)
        if branch == 'conjugate':
            gen = gen.conj()  # Fixed representation only; never source conjugation.
        internal = np.array([np.kron(np.eye(4), np.kron(a, np.eye(h))) for a in gen])
        if eta_contacts is None:
            normal = d5_sigma_foliation_eta(c, gamma=gamma, carrier_count=16,
                angular_count=h, sheet_orientation=eps)
            supplied_first = normal['sigma_normal_eta_contact_first'][source_slot]
        else:
            supplied_first = eta_contacts_first[branch]
        eta_x = _finite(supplied_first, (q, d, d), 'actual eta contact first')
        b = base['blocks'][branch]
        records = {name: [] for name in ('time', 'radial', 'body', 'energy',
            'Dtau_time', 'Dtau_radial', 'Dtau_body', 'W_radial', 'W_body',
            'A_time', 'A_radial', 'A_body', 'A_energy')}
        I = np.eye(d, dtype=complex)
        for r in range(q):
            N, C, R, z, ell = (c[name][r] for name in (
                'lapse', 'radial_coframe', 'radius', 'coordinate_shift', 'surface_proper_clock_rate'))
            Nx, Cx, Rx, zx, h0x, h4x, ex = (first[name][r] for name in (
                'lapse', 'radial_coframe', 'radius', 'coordinate_shift',
                'geometric_time_contact', 'geometric_radial_contact', 'surface_proper_clock_rate'))
            gauge = np.einsum('fc,cij->fij', c['gauge_connection_material'][r], internal)
            gx = np.einsum('fc,cij->fij', first['gauge_connection_material'][r], internal)
            dt = -Nx * I / N**2
            dr = -(zx / N - z * Nx / N**2) * I
            db = h0x * I + (gx[0] - zx * gauge[1] - z * gx[1]) / N
            db -= (gauge[0] - z * gauge[1]) * Nx / N**2
            wr = -b['W_radial'][r] * Cx / C
            wb_inside = 1j * eps * g[4] * h4x + eta_x[r]
            wb_inside -= (b['round_spin_Dirac_matrix'] + b['angular_Dirac_matrix']) * Rx / R**2
            wb_inside += 1j * eps * g[4] @ (gx[1] / C - gauge[1] * Cx / C**2)
            wb_inside += sum(1j * g[a + 1] @ (gx[a + 2] / R - gauge[a + 2] * Rx / R**2)
                             for a in range(3))
            wb = -g[0] @ wb_inside
            phase = ex / N - ell * Nx / N**2
            values = dict(time=1j * g[0] @ dt, radial=g[0] @ (1j * dr - wr),
                body=g[0] @ (1j * db - wb), energy=g[0] * phase,
                Dtau_time=dt, Dtau_radial=dr, Dtau_body=db, W_radial=wr, W_body=wb,
                A_time=dt, A_radial=dr + wr, A_body=db + wb, A_energy=-1j * phase * I)
            for name, v in values.items():
                records[name].append(v)
        blocks[branch] = {name: np.array(v) for name, v in records.items()}
        blocks[branch]['sigma_eta_contact'] = eta_x
    derivative = {name: base[name] for name in (
        'radial_count', 'angular_count', 'block_width', 'full_width', 'sheet_orientation')}
    derivative.update(blocks=blocks, volume_density=first['volume_density'])
    return dict(value=base, first=derivative, source_slot=source_slot,
        eta_contact_owner='original sigma level-set owner' if eta_contacts is None else 'explicit caller-supplied contact and its first',
        fixed_Eulerian_Clifford_and_Haar_coefficient_frame=True,
        independent_source_coefficients_conjugated=False,
        full_physical_E_B_or_outgoing_domain_derivative=False)


def _phase_action(c, V, placement):
    out = np.empty_like(V)
    d = c['block_width']
    key = 'energy' if placement == 'lorentz' else 'A_energy'
    for family in range(3):
        for j, branch in enumerate(('particle', 'conjugate')):
            sl = slice((2 * family + j) * d, (2 * family + j + 1) * d)
            out[:, sl] = c['blocks'][branch][key] @ V[:, sl]
    return out


def apply_full_d5_source_first(germ, value, radial_derivative, time_derivative, *,
        value_first, radial_derivative_first, time_derivative_first,
        energy, energy_first, placement):
    """Apply exact coefficient, moving-trial and phase contacts separately."""
    c, cx = germ['value'], germ['first']
    V = np.asarray(value, complex)
    Vx = _finite(value_first, V.shape, 'value first')
    Vrx = _finite(radial_derivative_first, V.shape, 'radial trial first')
    Vtx = _finite(time_derivative_first, V.shape, 'time trial first')
    E, Ex = complex(energy), complex(energy_first)
    if not np.isfinite(E) or not np.isfinite(Ex):
        raise ValueError('explicit finite phase and its first required')
    acted = apply_full_d5_expression(c, V, radial_derivative, time_derivative,
                                     energy=E, placement=placement)
    coefficient = apply_full_d5_expression(cx, V, radial_derivative, time_derivative,
                                           energy=E, placement=placement)
    trial = apply_full_d5_expression(c, Vx, Vrx, Vtx, energy=E, placement=placement)
    phase = _phase_action(c, V, placement)
    return dict(value=acted, first=coefficient + trial + Ex * phase,
        coefficient_contact=coefficient, moving_trial_contact=trial,
        phase_frequency_contact=Ex * phase, phase_frequency_partial=phase,
        phase_frequency_partial_first=_phase_action(cx, V, placement) + _phase_action(c, Vx, placement),
        physical_total_energy_or_field_domain_derivative=False)


def full_d5_weak_source_first(germ, value, radial_derivative, time_derivative, *,
        value_first, radial_derivative_first, time_derivative_first,
        independent_left, independent_left_first, coordinate_weights,
        coordinate_weights_first, energy, energy_first, placement):
    """Differentiate the ordered weak form, keeping density and left contacts."""
    a = apply_full_d5_source_first(germ, value, radial_derivative, time_derivative,
        value_first=value_first, radial_derivative_first=radial_derivative_first,
        time_derivative_first=time_derivative_first, energy=energy, energy_first=energy_first,
        placement=placement)
    q, D = a['value'].shape[:2]
    L = np.asarray(independent_left, complex)
    if L.ndim != 3 or L.shape[0] != q or L.shape[2] != D:
        raise ValueError('explicit independent full-fibre left map required')
    L = _finite(L, L.shape, 'left')
    Lx = _finite(independent_left_first, L.shape, 'left first')
    w = _finite(coordinate_weights, (q,), 'coordinate weights')
    wx = _finite(coordinate_weights_first, (q,), 'coordinate weights first')
    mu, mux = germ['value']['volume_density'], germ['first']['volume_density']
    density, densityx = w * mu, wx * mu + w * mux
    contract = lambda m, l, r: np.einsum('q,qij,qjk->ik', m, l, r)
    dx = contract(densityx, L, a['value'])
    leftx = contract(density, Lx, a['value'])
    operatorx = contract(density, L, a['first'])
    return dict(value=contract(density, L, a['value']), first=dx + leftx + operatorx,
        density_contact=dx, independent_left_contact=leftx, operator_and_trial_contact=operatorx,
        point_application=a, independent_analytic_left_conjugated=False,
        full_physical_outgoing_derivative_pass=False)


def full_d5_positive_source_first(germ, value, radial_derivative, time_derivative, *,
        value_first, radial_derivative_first, time_derivative_first,
        positive_coordinate_weights, coordinate_weights_first,
        output_block_grams, output_block_grams_first, energy, energy_first,
        real_source_axis):
    """Local positive A form and its REAL-source derivative on supplied maps.

    Coordinate weights include the actual scalar density and its derivative.
    Moving domain/boundary contacts still require their actual trace maps.
    """
    if real_source_axis is not True:
        raise ValueError('positive Riesz differentiation requires a declared REAL source axis')
    c = germ['value']
    q, d = c['radial_count'], c['block_width']
    w = _finite(positive_coordinate_weights, (q,), 'positive coordinate weights')
    wx = _finite(coordinate_weights_first, (q,), 'coordinate weights first')
    if np.any(w.imag != 0) or np.any(w.real <= 0) or np.any(wx.imag != 0):
        raise ValueError('real positive coordinate weights and real first required')
    G = _finite(output_block_grams, (q, 2, d, d), 'output Gram')
    Gx = _finite(output_block_grams_first, G.shape, 'output Gram first')
    if max(np.max(abs(G - G.conj().swapaxes(-1, -2))),
           np.max(abs(Gx - Gx.conj().swapaxes(-1, -2)))) > 1e-12:
        raise ValueError('Hermitian output Gram and real-axis Gram first required')
    if np.min(np.linalg.eigvalsh(G)) <= 0:
        raise ValueError('positive output Gram required')
    a = apply_full_d5_source_first(germ, value, radial_derivative, time_derivative,
        value_first=value_first, radial_derivative_first=radial_derivative_first,
        time_derivative_first=time_derivative_first, energy=energy, energy_first=energy_first,
        placement='formal_product')
    n = a['value'].shape[-1]
    form, first = np.zeros((n, n), complex), np.zeros((n, n), complex)
    bilinear = lambda weight, left, gram, right: np.einsum(
        'q,qji,qjk,qkl->il', weight, left.conj(), gram, right)
    for family in range(3):
        for b in range(2):
            sl = slice((2 * family + b) * d, (2 * family + b + 1) * d)
            u, ux = a['value'][:, sl], a['first'][:, sl]
            form += bilinear(w, u, G[:, b], u)
            first += bilinear(wx, u, G[:, b], u) + bilinear(w, ux, G[:, b], u)
            first += bilinear(w, u, Gx[:, b], u) + bilinear(w, u, G[:, b], ux)
    return dict(value=form, first=first, local_positive_pairing_checked=True,
        source_axis_is_real=True, full_field_count=c['full_width'],
        full_native_domain_or_physical_outgoing_derivative_pass=False)
