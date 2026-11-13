"""Literal local Wick pullback of the reached Maxwell and intrinsic-H actions.

This complexifies the retained REAL coefficient chart analytically.  Products
use transpose bilinear pairings, not a new conjugation after complexification.
For t=-i tau, A_E,tau=-i A_L,t, beta_E=-i beta_L and d_tau=-i d_t.
Consequently L_E=-L_L after pullback and S_E=-i S_L, including weak duals.
Real Lorentz data usually give complex Euclidean data.  No positive native
operator, Wick contour, exterior graph or physical cutoff is selected here.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .muon_matched_mechanical_source import epsilon
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation


_FIELD_ROTATION = np.array([-1j, 1, 1, 1, 1])
_DERIVATIVE_ROTATION = np.array([-1j, 1, 1, 1])


@dataclass
class _Jet:
    value: complex
    first: np.ndarray
    second: np.ndarray

    def __add__(self, other):
        if not isinstance(other, _Jet):
            other = _Jet(other, np.zeros_like(self.first), np.zeros_like(self.second))
        return _Jet(self.value+other.value, self.first+other.first, self.second+other.second)

    __radd__ = __add__

    def __neg__(self):
        return _Jet(-self.value, -self.first, -self.second)

    def __sub__(self, other):
        return self+-other if isinstance(other, _Jet) else self+(-other)

    def __rsub__(self, other):
        return -self+other

    def __mul__(self, other):
        if not isinstance(other, _Jet):
            return _Jet(self.value*other, self.first*other, self.second*other)
        return _Jet(self.value*other.value,
            self.first*other.value+self.value*other.first,
            self.second*other.value+self.value*other.second+
            np.outer(self.first, other.first)+np.outer(other.first, self.first))

    __rmul__ = __mul__


def _array(value, name, shape):
    x = np.asarray(value, complex)
    if x.shape != shape or not np.isfinite(x).all():
        raise ValueError(f'{name} needs finite shape {shape}')
    return x


def _pack(value, tangent, count):
    out = np.empty(value.shape, object)
    for index in np.ndindex(value.shape):
        out[index] = _Jet(value[index], tangent[(slice(None),)+index].copy(),
                          np.zeros((count, count), complex))
    return out


def _unpack(x):
    if isinstance(x, _Jet):
        return dict(value=x.value, first=x.first, second=x.second)
    return dict(value=np.array([z.value for z in x.flat]).reshape(x.shape),
        first=np.array([z.first for z in x.flat]).reshape(x.shape+(-1,)),
        second=np.array([z.second for z in x.flat]).reshape(x.shape+x.flat[0].second.shape))


def _dot(x, y):
    return sum((a*b for a, b in zip(x.flat, y.flat)), 0.)


def _bracket(a, b):
    result = np.empty(4, object)
    for i in range(3):
        result[i] = sum((epsilon()[i, j, k]*a[j]*b[k]*(1/np.sqrt(2))
                        for j in range(3) for k in range(3)), 0.)
    result[3] = 0*a[3]
    return result


def _curvatures(A, At, Ar, angular):
    X = At[1]-Ar[0]+_bracket(A[0], A[1])
    T = np.array([At[i+2]-angular[i, 0]+_bracket(A[0], A[i+2]) for i in range(3)])
    R = np.array([Ar[i+2]-angular[i, 1]+_bracket(A[1], A[i+2]) for i in range(3)])
    B = np.empty((3, 4), object)
    for i in range(3):
        B[i] = 2*A[i+2]
        for j in range(3):
            for k in range(3):
                B[i] += epsilon()[i, j, k]*(angular[j, k+2]+.5*_bracket(A[j+2], A[k+2]))
    return X, T, R, B


def local_field_chart():
    """All local field/first-derivative/coefficient slots, before an FE domain."""
    shapes = dict(A=(5, 4), A_time=(5, 4), A_radial=(5, 4), A_angular=(3, 5, 4),
                  H=(4,), H_derivative=(4, 4), J=(4,), densities=(5,), weights=(3,))
    spans = {}; start = 0
    for name, shape in shapes.items():
        stop = start+int(np.prod(shape)); spans[name] = (start, stop); start = stop
    return dict(shapes=shapes, spans=spans, dimension=start,
        coefficient_order='densities=(e,r,d,k,beta), weights=(wT,wS,wV)',
        field_order='A_t,A_r,A1,A2,A3; real H=(ReH1,ReH2,ImH1,ImH2)')


def local_field_direction_basis():
    chart = local_field_chart(); eye = np.eye(chart['dimension'])
    return {name:eye[:, start:stop].reshape((chart['dimension'],)+chart['shapes'][name])
            for name, (start, stop) in chart['spans'].items()}


def wick_local_slot_rotation():
    """Diagonal change of every local source/derivative/coefficient slot."""
    chart = local_field_chart(); one = {k:np.ones(shape) for k, shape in chart['shapes'].items()}
    moved = wick_local_data(one)
    return np.concatenate([moved[k].reshape(-1) for k in chart['shapes']])


def wick_local_data(data):
    """Pull back values, ordinary derivative slots and coefficient/source jets.

    Apply the same function to each directional field image.  A derivative
    with respect to an external source is not rotated; only its time-indexed
    value/derivative slots are.  Mechanical and independent connection must
    already be combined once in A.  Material A_t is not advected again.
    """
    chart = local_field_chart(); out = {name:_array(data[name], name, shape).copy()
                                     for name, shape in chart['shapes'].items()}
    out['A'] *= _FIELD_ROTATION[:, None]
    out['A_time'] *= -1j*_FIELD_ROTATION[:, None]
    out['A_radial'] *= _FIELD_ROTATION[:, None]
    out['A_angular'] *= _FIELD_ROTATION[None, :, None]
    out['H_derivative'] *= _DERIVATIVE_ROTATION[:, None]
    out['densities'][4] *= -1j
    return out


def wick_directional_images(images):
    """Same analytic pullback of ALL source/normal images, including rates."""
    count = np.shape(images['A'])[0]
    rows = [wick_local_data({name:np.asarray(value)[i] for name, value in images.items()})
            for i in range(count)]
    return {name:np.array([row[name] for row in rows]) for name in local_field_chart()['shapes']}


def wick_temporal_coefficient_jet(value, time_first, time_second):
    """Analytic germ c_L(t0-i tau)=c0-i tau*c1-tau²*c2/2.

    These are ordinary derivatives, not Taylor coefficients.  The values
    must come from the same action trajectory; this does not determine them.
    """
    values = [np.asarray(x, complex) for x in (value, time_first, time_second)]
    if len({x.shape for x in values}) != 1 or any(not np.isfinite(x).all() for x in values):
        raise ValueError('same finite analytic temporal coefficient two-jet required')
    return dict(value=values[0], first=-1j*values[1], second=-values[2])


def local_analytic_action_jet(data, images, *, lambda_H, nu_squared_action,
                              signature='lorentz'):
    """Literal action/weak/Hessian and time/radial conormal applications.

    Input images are affine parameter applications in this local jet chart.
    Nonlinear map second jets are composed by the caller, never omitted by
    declaring the source affine.  All curvature/DH/quartic second contacts
    of this action are generated here.  Sector normalization/quadrature is
    deliberately not combined: parent volume and intrinsic wall differ.
    """
    if signature not in ('lorentz', 'euclidean'):
        raise ValueError('explicit Lorentz or Euclidean action required')
    chart = local_field_chart(); count = np.shape(images['A'])[0]
    if count < 1:
        raise ValueError('at least one explicit coefficient/source image required')
    values = {}; raw = {}
    for name, shape in chart['shapes'].items():
        raw[name] = _array(data[name], name, shape)
        tangent = _array(images[name], name+' images', (count,)+shape)
        values[name] = _pack(raw[name], tangent, count)
    lam, nu = float(lambda_H), float(nu_squared_action)
    if not np.isfinite([lam, nu]).all() or lam <= 0 or nu < 0:
        raise ValueError('owned positive lambda_H and nonnegative nu² required')
    A, At, Ar, angular = [values[k] for k in ('A', 'A_time', 'A_radial', 'A_angular')]
    e, r, d, k, beta = values['densities']; wt, ws, wv = values['weights']
    spatial_sign = -1 if signature == 'lorentz' else 1
    X, T, R, B = _curvatures(A, At, Ar, angular)
    Y = np.array([[T[i, j]-beta*R[i, j] for j in range(4)] for i in range(3)])
    maxwell = .5*(k*_dot(X, X)+e*_dot(Y, Y)+spatial_sign*(r*_dot(R, R)+d*_dot(B, B)))
    H, ordinary, J = [values[z] for z in ('H', 'H_derivative', 'J')]
    generators = higgs_u2_real_representation()['real_generators']
    DH = np.empty((4, 4), object)
    for mu in range(4):
        f = 0 if mu == 0 else mu+1
        for a in range(4):
            DH[mu, a] = ordinary[mu, a]+sum((A[f, c]*generators[c, a, b]*H[b]
                for c in range(4) for b in range(4)), 0.)
    q = _dot(H, H)-nu
    potential = lam*q*q+2*_dot(H, J)
    # L_L=positive temporal-negative spatial-negative potential;
    # L_E has all positive terms.  The real2Re convention is in derivatives.
    higgs = wt*_dot(DH[0], DH[0])+spatial_sign*(ws*_dot(DH[1:], DH[1:])+wv*potential)
    pt = np.empty((5, 4), object); pr = np.empty((5, 4), object)
    for c in range(4):
        pt[0, c] = 0*X[c]; pt[1, c] = k*X[c]
        pr[0, c] = -k*X[c]; pr[1, c] = 0*X[c]
        for i in range(3):
            pt[i+2, c] = e*Y[i, c]
            pr[i+2, c] = -e*beta*Y[i, c]+spatial_sign*r*R[i, c]
    scalar_pt = np.array([2*wt*x for x in DH[0]])
    scalar_ps = np.array([[2*spatial_sign*ws*x for x in row] for row in DH[1:]])
    return dict(maxwell=_unpack(maxwell), higgs=_unpack(higgs),
        curvatures={key:_unpack(v) for key, v in zip(('Ftr', 'Ft', 'Fr', 'B'), (X, T, R, B))},
        covariant_H=_unpack(DH), gauge_temporal_momentum=_unpack(pt),
        gauge_radial_conormal=_unpack(pr), scalar_temporal_momentum=_unpack(scalar_pt),
        scalar_spatial_conormal=_unpack(scalar_ps), signature=signature,
        pairing='analytic complexification of real coefficient dual; no conjugation after pullback',
        conormal_role='IBP contacts of this derivative-form action; not appended to its weak variation',
        native_positive_operator_or_exterior_domain_identified=False)


def compare_local_wick_application(data, images, *, lambda_H, nu_squared_action):
    """Execute both owned local actions and ALL rotated weak/contact rows."""
    kw = dict(lambda_H=lambda_H, nu_squared_action=nu_squared_action)
    lorentz = local_analytic_action_jet(data, images, signature='lorentz', **kw)
    edata = wick_local_data(data); eimages = wick_directional_images(images)
    euclidean = local_analytic_action_jet(edata, eimages, signature='euclidean', **kw)
    action_errors = {f'{sector}_{order}':float(np.max(abs(lorentz[sector][order]+euclidean[sector][order])))
                     for sector in ('maxwell', 'higgs') for order in ('value', 'first', 'second')}
    contacts = {}
    # The radial dual transforms oppositely to the field rotation;
    # the time dual also carries the derivative-coordinate rotation.
    for order in ('value', 'first', 'second'):
        extra = (None,)*(np.ndim(lorentz['gauge_temporal_momentum'][order])-2)
        field = _FIELD_ROTATION[(slice(None), None)+extra]
        contacts['gauge_time_'+order] = float(np.max(abs(
            lorentz['gauge_temporal_momentum'][order]-1j*field*euclidean['gauge_temporal_momentum'][order])))
        contacts['gauge_radial_'+order] = float(np.max(abs(
            lorentz['gauge_radial_conormal'][order]+field*euclidean['gauge_radial_conormal'][order])))
        contacts['scalar_time_'+order] = float(np.max(abs(
            lorentz['scalar_temporal_momentum'][order]-1j*euclidean['scalar_temporal_momentum'][order])))
        contacts['scalar_spatial_'+order] = float(np.max(abs(
            lorentz['scalar_spatial_conormal'][order]+euclidean['scalar_spatial_conormal'][order])))
    return dict(lorentz=lorentz, euclidean=euclidean, euclidean_data=edata,
        action_continuation_residuals=action_errors, conormal_continuation_residuals=contacts,
        euclidean_coefficient_imaginary_norm=float(np.sqrt(sum(np.linalg.norm(v.imag)**2 for v in edata.values()))),
        positive_real_Euclidean_reference_is_this_continued_base=all(np.max(abs(v.imag)) == 0 for v in edata.values()),
        contour='t=t0-i tau; continued coefficient germ/source values, not real-time sign replacement',
        density_identity='L_E=-L_L after pullback; S_E=-i S_L including oriented weak duals',
        exterior_or_relative_domain_continuation_performed=False,
        physical_native_heat_or_Pauli_evaluated=False)


def local_analytic_ghost_pairing(A, metric, left, left_derivative, right,
                                  right_derivative, *, signature='lorentz'):
    """The SAME FP scalar covariant form, with both complex ghost duals.

    Metric entries are the density-weighted (gt,gr,gs,beta), not g alone.
    Left/right ghost test coordinates are independent in this bilinear
    extension.  No Grassmann expectation, ghost deletion or domain is chosen.
    """
    if signature not in ('lorentz', 'euclidean'):
        raise ValueError('explicit action signature required')
    A = _array(A, 'A', (5, 4)); gt, gr, gs, beta = _array(metric, 'metric', (4,))
    eta, chi = (_array(x, name, (4,)) for x, name in ((left, 'left'), (right, 'right')))
    derivatives = [_array(x, name, (5, 4)) for x, name in (
        (left_derivative, 'left derivative'), (right_derivative, 'right derivative'))]
    def D(value, derivative):
        return derivative+np.array([np.r_[np.cross(a[:3], value[:3])/np.sqrt(2), 0.] for a in A])
    a, b = (D(value, derivative) for value, derivative in zip((eta, chi), derivatives))
    sign = -1 if signature == 'lorentz' else 1
    return gt*((a[0]-beta*a[1])@(b[0]-beta*b[1]))+sign*(gr*(a[1]@b[1])+gs*np.sum(a[2:]*b[2:]))


def local_ghost_coefficient_matrix(A, metric, *, signature='lorentz'):
    """All 24 FP value/first-derivative slots, before a ghost form domain.

    The two independent dual ghost coordinates use this same operator.
    Statistics weight -2 is retained by the supertrace consumer, not here.
    """
    if signature not in ('lorentz', 'euclidean'):
        raise ValueError('explicit action signature required')
    A = _array(A, 'A', (5, 4)); gt, gr, gs, beta = _array(metric, 'metric', (4,))
    image = np.zeros((5, 4, 24), complex)
    for f in range(5):
        for c in range(4):
            image[f, :, c] = np.r_[np.cross(A[f, :3], np.eye(4)[c, :3])/np.sqrt(2), 0.]
        image[f, :, 4+4*f:8+4*f] = np.eye(4)
    sign = -1 if signature == 'lorentz' else 1
    temporal = image[0]-beta*image[1]
    return gt*(temporal.T@temporal)+sign*(gr*(image[1].T@image[1])+
        gs*sum(a.T@a for a in image[2:]))


def wick_canonical_gauge_higgs_rows(gauge_value, gauge_momentum,
                                     H_value, H_momentum, gauge_gauss):
    """Continue actual Cauchy trace/dual/Gauss rows without choosing faces.

    For A_L=diag(i,1,1,1,1) A_E, the oriented temporal weak dual obeys
    p_E=-i diag(i,1,1,1,1) p_L.  H_E=H_L and p_H,E=-i p_H,L.
    The density Gauss row transforms as dL_E/dA_E,t=-i dL_L/dA_L,t.
    These identities apply separately to each inherited oriented endpoint;
    they preserve its existing zero/nonzero trace and dual jump.  They do
    not replace a recorded canonical far-face by a Dirichlet heat boundary.
    """
    a, p = (_array(x, name, (5, 4)) for x, name in ((gauge_value, 'gauge trace'), (gauge_momentum, 'gauge dual')))
    h, ph, gauss = (_array(x, name, (4,)) for x, name in (
        (H_value, 'H trace'), (H_momentum, 'H dual'), (gauge_gauss, 'Gauss row')))
    return dict(gauge_value=_FIELD_ROTATION[:, None]*a,
        gauge_momentum=(-1j/_FIELD_ROTATION)[:, None]*p,
        H_value=h.copy(), H_momentum=-1j*ph, gauge_gauss=-1j*gauss,
        temporal_face_roles_preserved=True, new_terminal_domain_selected=False)


def materialize_local_wick_application(phase_directory, output, *, cell_index=0,
                                      repository=None):
    """Evaluate actual radial Maxwell and intrinsic wall analytic coefficients.

    This is a local coefficient-cell application, not a heat on 152 source
    coordinates.  Those coordinates resolve all differential coefficient
    slots before an exterior/domain application is composed.  The scalar
    action is evaluated only on the intrinsic wall; no ambient H extension
    is supplied.  The local classical body J=0 retains its actual provenance.
    """
    from hashlib import sha256
    import json
    from pathlib import Path
    from .muon_parent_gauge_geometry_correction import ROOT
    from .muon_profile_preserving_phase_sample import load_profile_preserving_phase, profile_preserving_raw_sample
    from .muon_parent_positive_coupled_field import corrected_positive_parent_reference
    from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
    from .muon_intrinsic_lepton_primal import classical_bosonic_body_source
    from .muon_parent_retarded_hypercharge import WALL
    from .muon_birth_phase_continuation import _compressed_npz

    root = Path(ROOT if repository is None else repository)
    out = Path(output); out = out if out.is_absolute() else root/out
    if out.exists():
        raise FileExistsError('preserve earlier local continuation applications')
    phase = load_profile_preserving_phase(phase_directory, repository=root)
    receipt = phase['receipt']; rep = phase['representation']
    if type(cell_index) is not int or not 0 <= cell_index < receipt['steps']:
        raise ValueError('explicit retained chronological cell index required')
    time = (cell_index+.5)*receipt['span']/receipt['steps']
    sample = profile_preserving_raw_sample(phase, time); raw = sample['raw_fields']
    optional = (dict(initial_pair=phase['arrays']['initial_pair'], reference_pair=phase['arrays']['reference_pair'])
                if receipt['side'] == 'outgoing' else {})
    ref = corrected_positive_parent_reference(raw, rep, coordinate_time=time, **optional)
    wall_rep = dict(rep, rho=np.array([WALL]), radial_quadrature=np.ones(1),
        gauge_basis=np.moveaxis(rep['wall_trace_map'], -1, 0)[None, :, None],
        gauge_radial_basis=np.moveaxis(rep['wall_radial_derivative_map'], -1, 0)[None, :, None])
    wall = corrected_positive_parent_reference(raw, wall_rep, coordinate_time=time, **optional)
    geometry = intrinsic_m4_weight_jet(12, raw[:37], raw[37:74], raw[74:98],
        source_value=raw[98], source_rate=raw[99])
    weights = np.array([geometry[k].value for k in ('wT', 'wS', 'wV')])
    chart = local_field_chart(); basis = local_field_direction_basis(); rotation = wick_local_slot_rotation()
    zero = {k:np.zeros((1,)+shape) for k, shape in chart['shapes'].items()}
    lam = float(rep['scalar_matching']['lambda_H']); nu = float(receipt['action_parameters']['nu_squared_action'])
    body = classical_bosonic_body_source(1)
    arrays = dict(raw_fields=raw, raw_coordinate_time_derivative=sample['raw_coordinate_time_derivative'],
        rho=ref['rho'], radial_quadrature=ref['radial_weights'], local_slot_rotation=rotation,
        Euclidean_ghost_slot_rotation=np.r_[np.ones(4), -1j*np.ones(4), np.ones(16)])
    packed = []; epacked = []; values = []; evalues = []; gradients = []; hessians = []
    egradients = []; ehessians = []; ptime = []; prho = []; ep_time = []; ep_rho = []
    ptime_first = []; prho_first = []; ghost_L = []; ghost_E = []; reference_values = []
    continuation = []; reality = []; wall_output = None
    count = len(ref['rho'])
    for index in range(count+1):
        source = ref if index < count else wall; j = index if index < count else 0
        data = dict(A=source['background_values'][j], A_time=source['background_time_derivatives'][j],
            A_radial=source['background_radial_derivatives'][j], A_angular=np.zeros((3, 5, 4)),
            H=raw[-8:-4], H_derivative=np.vstack((raw[-4:], np.zeros((3, 4)))),
            J=np.zeros(4), densities=source['positive_two_form_densities'][j], weights=weights)
        app = compare_local_wick_application(data, basis, lambda_H=lam, nu_squared_action=nu)
        old = local_analytic_action_jet(data, zero, lambda_H=lam, nu_squared_action=nu, signature='euclidean')
        continuation.append(max(*app['action_continuation_residuals'].values(),
                                *app['conormal_continuation_residuals'].values()))
        reality.append(app['euclidean_coefficient_imaginary_norm'])
        if index == count:
            L, E = app['lorentz']['higgs'], app['euclidean']['higgs']
            wall_output = dict(Higgs_L_value=np.asarray(L['value']), Higgs_E_value=np.asarray(E['value']),
                Higgs_L_first=L['first'], Higgs_E_first=-L['first']/rotation,
                Higgs_L_second=L['second'], Higgs_E_second=-L['second']/rotation[:, None]/rotation[None, :],
                wall_A_L=data['A'], wall_A_E=app['euclidean_data']['A'],
                H=raw[-8:-4], H_coordinate_rate=raw[-4:], weights=weights,
                Higgs_positive_real_reference_value=np.asarray(old['higgs']['value']),
                Higgs_temporal_dual_L=app['lorentz']['scalar_temporal_momentum']['value'],
                Higgs_temporal_dual_E=app['euclidean']['scalar_temporal_momentum']['value'],
                Higgs_spatial_dual_L=app['lorentz']['scalar_spatial_conormal']['value'],
                Higgs_spatial_dual_E=app['euclidean']['scalar_spatial_conormal']['value'])
            continue
        L, E = app['lorentz']['maxwell'], app['euclidean']['maxwell']
        packed.append(np.concatenate([data[k].reshape(-1) for k in chart['shapes']]))
        epacked.append(np.concatenate([app['euclidean_data'][k].reshape(-1) for k in chart['shapes']]))
        values.append(L['value']); evalues.append(E['value']); gradients.append(L['first']); hessians.append(L['second'])
        egradients.append(-L['first']/rotation); ehessians.append(-L['second']/rotation[:, None]/rotation[None, :])
        reference_values.append(old['maxwell']['value'])
        for destination, a, key, order in (
            (ptime, 'lorentz', 'gauge_temporal_momentum', 'value'), (prho, 'lorentz', 'gauge_radial_conormal', 'value'),
            (ep_time, 'euclidean', 'gauge_temporal_momentum', 'value'), (ep_rho, 'euclidean', 'gauge_radial_conormal', 'value'),
            (ptime_first, 'lorentz', 'gauge_temporal_momentum', 'first'), (prho_first, 'lorentz', 'gauge_radial_conormal', 'first')):
            destination.append(app[a][key][order])
        metric = source['positive_metric_coefficients'][j][[1, 2, 3, 4]].astype(complex)
        emetric = metric.copy(); emetric[-1] *= -1j
        ghost_L.append(local_ghost_coefficient_matrix(data['A'], metric))
        ghost_E.append(local_ghost_coefficient_matrix(app['euclidean_data']['A'], emetric, signature='euclidean'))
    arrays.update({name:np.array(value) for name, value in dict(
        local_data_L=packed, local_data_E=epacked, Maxwell_L_value=values, Maxwell_E_value=evalues,
        Maxwell_L_first=gradients, Maxwell_E_first=egradients, Maxwell_L_second=hessians, Maxwell_E_second=ehessians,
        Maxwell_positive_real_reference_value=reference_values, gauge_temporal_dual_L=ptime, gauge_temporal_dual_E=ep_time,
        gauge_radial_dual_L=prho, gauge_radial_dual_E=ep_rho,
        gauge_temporal_dual_L_first=ptime_first, gauge_radial_dual_L_first=prho_first,
        ghost_L_coefficient_matrix=ghost_L, ghost_E_coefficient_matrix=ghost_E).items()})
    arrays.update(wall_output)
    ghost_rotation = arrays['Euclidean_ghost_slot_rotation']
    ghost_defect = np.max(abs(arrays['ghost_L_coefficient_matrix']+
        ghost_rotation[None, :, None]*arrays['ghost_E_coefficient_matrix']*ghost_rotation[None, None, :]))
    refs = dict(phase['input_hashes'])
    for name in ('muon_local_wick_action', 'muon_parent_positive_coupled_field',
                 'muon_parent_positive_brst_ghost', 'muon_parent_maxwell_full_weak',
                 'muon_intrinsic_higgs_gauge_action', 'muon_intrinsic_higgs_weak_action', 'muon_intrinsic_lepton_primal'):
        p = 'src/bhsm/interface/'+name+'.py'; refs[p] = sha256((root/p).read_bytes()).hexdigest()
    out.mkdir(parents=True); _compressed_npz(out/'application.npz', arrays)
    if refs != {p:sha256((root/p).read_bytes()).hexdigest() for p in refs}:
        raise RuntimeError('consumed action changed during continuation')
    md = dict(classification='EVALUATED_LITERAL_LOCAL_GAUGE_HIGGS_GHOST_WICK_APPLICATION',
        side=receipt['side'], cell_index=cell_index, coordinate_time=time, radial_points=count,
        local_field_chart=chart, input_hashes=refs, numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        action_parameters=dict(lambda_H=lam, nu_squared_action=nu),
        local_action_and_weak_contact_continuation_residual_max=max(continuation),
        ghost_continuation_residual_max=float(ghost_defect),
        Euclidean_coefficient_imaginary_norm_max=max(reality),
        positive_real_ADM_reference_is_this_continued_base=False,
        same_real_ADM_reference_Maxwell_value_difference_norm=float(np.linalg.norm(arrays['Maxwell_E_value']-
            arrays['Maxwell_positive_real_reference_value'])),
        intrinsic_H_source_provenance=body['classification'], quantum_native_H_load_added=False,
        angular_background='actual angular-homogeneous body; all angular derivative trial/source coefficient slots retained',
        endpoint_policy='oriented trace/dual/Gauss rotations only; existing numerical canonical far-face roles preserved',
        scalar_domain='intrinsic wall only; no ambient-H normal derivative or radial extension',
        coefficient_Hessian='all local differential slots, not a heat on coefficient/source coordinates',
        source_chain='Euclidean coordinate Hessian is -diag(rotation)^-T H_L diag(rotation)^-1; external source images rotate too',
        error_scope='binary64 local analytic polynomial comparison; no analytic-contour radius, exterior/relative-domain or physical uncertainty enclosure',
        exterior_relative_domain_continuation_performed=False, positive_native_HeatPencil_or_physical_Pauli_completed=False)
    (out/'result.json').write_text(json.dumps(md, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf8', newline='\n')
    return md
