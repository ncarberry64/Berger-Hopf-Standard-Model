"""Original-(u,v) geometric M8 Dirac expressions on explicit four-jets.

This is the untwisted geometric component on the source cohomogeneity
coframe, not a choice of native statistics, SM twisting or extra species.
No adapted horizontal/fibre spin frame or KK body is mixed into this
original-frame expression. All temporal and seven spatial directions,
both S3 spin triples and all supplied source contacts remain.
"""
from __future__ import annotations

import numpy as np

JETS = ('value', 'x', 'y', 'xy')
SCALARS = ('lapse', 'radial_coframe', 'orbit_A', 'orbit_B',
           'coordinate_shift', 'geometric_time_contact',
           'geometric_radial_contact', 'volume_density')


def _jet(a, shape, name):
    if set(a) != set(JETS):
        raise ValueError(name + ': explicit value/x/y/xy required')
    out = {k: np.asarray(a[k], complex) for k in JETS}
    if any(v.shape != shape or not np.isfinite(v).all() for v in out.values()):
        raise ValueError(name + ': finite same-shape jets required')
    return out


def _inverse(a):
    v = a['value']
    if np.any(v == 0):
        raise ValueError('regular nonzero coframe required')
    return dict(value=1/v, x=-a['x']/v**2, y=-a['y']/v**2,
                xy=2*a['x']*a['y']/v**3-a['xy']/v**2)


def _multiply(a, b, action):
    return dict(value=action(a['value'], b['value']),
        x=action(a['x'], b['value'])+action(a['value'], b['x']),
        y=action(a['y'], b['value'])+action(a['value'], b['y']),
        xy=action(a['xy'], b['value'])+action(a['x'], b['y'])
           +action(a['y'], b['x'])+action(a['value'], b['xy']))


def _scale(a, matrix):
    return {k: a[k][:, None, None]*matrix for k in JETS}


def original_m8_clifford(gamma5_base):
    """Fixed complete Spin16 algebra; base order (0,chi,u1,u2,u3)."""
    g = np.asarray(gamma5_base, complex)
    if g.shape != (5, 4, 4) or not np.isfinite(g).all():
        raise ValueError('finite fixed (+----) gamma5 required')
    p = np.array([[[0, 1], [1, 0]], [[0, -1j], [1j, 0]],
                  [[1, 0], [0, -1]]], complex)
    G = np.array([np.kron(np.kron(a, np.eye(2)), p[0]) for a in g]
        + [np.kron(np.kron(np.eye(4), 1j*a), p[1]) for a in p])
    signature = (1, -1, -1, -1, -1, -1, -1, -1)
    residual = max(np.max(abs(G[a]@G[b]+G[b]@G[a]
        -(2*signature[a]*np.eye(16) if a == b else 0)))
        for a in range(8) for b in range(8))
    if residual > 5e-12*max(1., np.max(abs(G))**2):
        raise ValueError('supplied gamma algebra does not give Cl(1,7)')
    return G


def original_left_maurer_coefficient_maps(right_maps, scalar_labels):
    """Original left-Maurer duals on the SAME phi=sqrt(n+1)conj(D_mk).

    The source right-body maps act on m. Right multiplication of the SU2
    argument acts on k with +2i J*, giving +2epsilon commutators. The
    permutation swaps m,k within each complete PW level; no mode is lost.
    """
    labels = [tuple(a) for a in scalar_labels]
    index = {a: i for i, a in enumerate(labels)}
    if len(index) != len(labels):
        raise ValueError('distinct complete PW labels required')
    try:
        perm = [index[n, k, m] for n, m, k in labels]
    except (KeyError, ValueError) as error:
        raise ValueError('PW space must retain its m,k-swap image') from error
    E = np.asarray(right_maps, complex)
    if E.shape != (3, len(labels), len(labels)) or not np.isfinite(E).all():
        raise ValueError('same complete right-body maps and PW labels required')
    return -E.conj()[:, perm][:, :, perm]


def original_m8_geometric_expression_jets(c, angular_u, angular_v, *, gamma5_base):
    """Assemble geometric D_L and A=D_tau+W on the supplied material chart.

    c contains explicit four-jets of N,C_material,A,B,z,h08,hchi8,mu8.
    The original spin densities must already be pulled to that chart;
    they are not inferred from selected inverse scales. Angular maps are
    LEFT Maurer duals with [U_a,U_b]=+2epsilon_abc U_c, on complete supplied
    unit-Haar coefficient spaces. Original left triples have PLUS signs.
    """
    if set(c) != set(SCALARS):
        raise ValueError('complete original geometric coefficient schema required')
    q = len(np.asarray(c['lapse']['value']))
    if q < 1:
        raise ValueError('nonempty supplied geometric germ required')
    s = {name: _jet(c[name], (q,), name) for name in SCALARS}
    angular = []
    for a in (angular_u, angular_v):
        a = np.asarray(a, complex)
        if a.ndim != 3 or a.shape[0] != 3 or a.shape[1] != a.shape[2] or not a.shape[1] or not np.isfinite(a).all():
            raise ValueError('complete finite left-Maurer angular maps required')
        scale = max(1., np.max(abs(a))**2)
        if max(np.max(abs(a[i]@a[(i+1)%3]-a[(i+1)%3]@a[i]-2*a[(i+2)%3])) for i in range(3)) > 5e-12*scale:
            raise ValueError('original angular commutator must be +2epsilon')
        angular.append(a)
    U, V = angular
    hu, hv = U.shape[1], V.shape[1]
    G8 = original_m8_clifford(gamma5_base)
    d = 16*hu*hv
    G = np.array([np.kron(a, np.eye(hu*hv)) for a in G8])
    spin_u = 1.5j*G[2]@G[3]@G[4]
    spin_v = 1.5j*G[5]@G[6]@G[7]
    Du = spin_u + sum(np.kron(np.kron(1j*G8[a+2], U[a]), np.eye(hv)) for a in range(3))
    Dv = spin_v + sum(np.kron(np.kron(1j*G8[a+5], np.eye(hu)), V[a]) for a in range(3))
    n, r, aa, bb = (_inverse(s[name]) for name in ('lapse', 'radial_coframe', 'orbit_A', 'orbit_B'))
    shift = _multiply(s['coordinate_shift'], n, lambda a, b: -a*b)
    dt, dr = _scale(n, np.eye(d)), _scale(shift, np.eye(d))
    db = _scale(s['geometric_time_contact'], np.eye(d))
    spatial = {k: _scale(s['geometric_radial_contact'], 1j*G[1])[k]
               +_scale(aa, Du)[k]+_scale(bb, Dv)[k] for k in JETS}
    wr = _scale(r, -1j*G[0]@G[1])
    wb = {k: -G[0]@spatial[k] for k in JETS}
    coefficients = {}
    for name in ('time', 'radial', 'body', 'Dtau_time', 'Dtau_radial',
                 'Dtau_body', 'W_radial', 'W_body', 'A_time', 'A_radial', 'A_body'):
        coefficients[name] = {}
    for k in JETS:
        values = dict(time=1j*G[0]@dt[k],
            radial=1j*G[0]@dr[k]+_scale(r, 1j*G[1])[k],
            body=1j*G[0]@db[k]+spatial[k],
            Dtau_time=dt[k], Dtau_radial=dr[k], Dtau_body=db[k],
            W_radial=wr[k], W_body=wb[k],
            A_time=dt[k], A_radial=dr[k]+wr[k], A_body=db[k]+wb[k])
        for name, value in values.items():
            coefficients[name][k] = value
    return dict(coefficients=coefficients, volume_density=s['volume_density'],
        radial_count=q, width=d, gamma8_original=G8,
        original_angular_u=U, original_angular_v=V,
        original_u_spin_triple=spin_u, original_v_spin_triple=spin_v,
        order='Spin16, original u PW, original v PW',
        geometric_component_only=True, internal_twist_or_endomorphism_evaluated=False,
        adapted_KK_or_horizontal_spin_body_added=False,
        native_statistics_or_SM_multiplicity_selected=False,
        source_coefficients_conjugated=False,
        physical_outgoing_or_total_response_claimed=False)


def apply_original_m8_expression_jets(operator, value, radial, time, *, placement):
    """Apply every coefficient/contact to explicit moving trial four-jets."""
    if placement not in ('lorentz', 'plus_product'):
        raise ValueError('explicit lorentz or plus_product placement required')
    shape = np.asarray(value['value']).shape
    if len(shape) != 3 or shape[:2] != (operator['radial_count'], operator['width']):
        raise ValueError('same q x full Spin16*hu*hv x columns required')
    maps = [_jet(a, shape, name) for a, name in ((value, 'value'), (radial, 'radial'), (time, 'time'))]
    prefix = '' if placement == 'lorentz' else 'A_'
    action = lambda a, b: np.einsum('qij,qjk->qik', a, b)
    terms = [_multiply(operator['coefficients'][prefix+name], trial, action)
             for name, trial in zip(('body', 'radial', 'time'), maps)]
    return {k: sum(t[k] for t in terms) for k in JETS}


def original_m8_ordered_weak_jets(operator, value, radial, time, *, independent_left,
                                  coordinate_weights, placement):
    """Density-weighted independent analytic left/right ordered action."""
    acted = apply_original_m8_expression_jets(operator, value, radial, time, placement=placement)
    shape = np.asarray(independent_left['value']).shape
    if len(shape) != 3 or shape[0] != operator['radial_count'] or shape[2] != operator['width']:
        raise ValueError('explicit independent q x left rows x full width required')
    left = _jet(independent_left, shape, 'independent left')
    weights = _jet(coordinate_weights, (shape[0],), 'coordinate weights')
    density = _multiply(weights, operator['volume_density'], lambda a, b: a*b)
    integrand = _multiply(left, acted, lambda a, b: np.einsum('qij,qjk->qik', a, b))
    return _multiply(density, integrand, lambda a, b: np.einsum('q,qij->ij', a, b))
