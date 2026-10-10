"""Weak Maxwell Euler and off-shell Ward applications at retained E1+.

The singular birth Hessian is not inverted to manufacture a pointwise
acceleration.  This application uses the actual connection value and
first time/radial derivatives.  Its derivative-form Euler rows and
oriented action contacts are inputs to a coupled history solve.

The mechanical connection and the saved Q reference lifts are evaluated
in their owned right Maurer coframe.  This is a predecessor Maxwell
component, not the complete native action or an on-shell Pauli kernel.
"""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo

import numpy as np
from numpy.polynomial.legendre import leggauss

from .muon_birth_candidate_geometry_action import ROOT, RESET_RECEIPT, STATE_SOURCE
from .muon_matched_mechanical_source import angular_blocks, epsilon, lambda_jets
from .muon_moving_geometric_action import retained_state
from .muon_parent_retarded_hypercharge import (
    SOURCE, WALL, frozen_e1_coefficients, regular_radial_basis,
)


def retained_connection_first_jet(rho, repository=ROOT):
    """Bind lambda, lambda_tau and lambda_rho to actual outgoing q,v,m.

    tau is boundary proper time.  The rates come from the retained velocity
    coordinates; they are not set to zero when an application is evaluated
    at a single event.  No second time derivative is asserted at that event.
    """
    data = frozen_e1_coefficients(rho, repository)
    fields = data['geometry']
    A, B = fields['A'][0], fields['B'][0]
    lam = A*A/(A*A+B*B)
    q, v, m = retained_state(repository)
    lt, lr = lambda_jets(np.concatenate((q, v, m)), np.asarray(rho), lam,
                         float(fields['boundary_lapse'][0]))
    normal = lt-data['shift']*lr
    return dict(**data, connection_lambda=lam, lambda_tau=lt, lambda_rho=lr,
                normal_lambda_rate=normal, actual_first_jet=True,
                second_time_derivative_assigned=False)


def background_weak_application(data, quadrature, test, test_rho, test_tau):
    """Apply delta S to an independent connection-amplitude test h.

    In the SAME unit-Tr16 internal basis as the photon application,
    jmath_i=sqrt(8)H_i and sum_i|jmath_i|^2=24.  Thus
    L=12e(Dlambda)^2-12r lambda_rho^2-48d lambda^2(lambda-1)^2.
    The returned derivative-form row already is the full action variation;
    the displayed IBP contacts are not appended a second time.
    """
    w = np.asarray(quadrature, float)
    h, hr, ht = (np.asarray(x, float) for x in (test, test_rho, test_tau))
    if h.ndim == 1:
        h, hr, ht = h[:, None], hr[:, None], ht[:, None]
    if h.shape != hr.shape or h.shape != ht.shape or h.shape[0] != len(w):
        raise ValueError('same quadrature-indexed test values and derivatives required')
    e, r, d, shift, lam, lr, normal = (np.asarray(data[k]) for k in (
        'electric', 'radial', 'angular', 'shift', 'connection_lambda',
        'lambda_rho', 'normal_lambda_rate'))
    p = 24*e*normal
    pr = -24*(e*shift*normal+r*lr)
    potential = -96*d*lam*(lam-1)*(2*lam-1)
    residual = np.einsum('q,qj->j', w, p[:, None]*ht+pr[:, None]*hr+potential[:, None]*h)
    return dict(weak_Euler=residual,
                temporal_momentum_test=np.einsum('q,qj->j', w*p, h),
                temporal_momentum_density=p, radial_momentum_density=pr,
                potential_Euler_density=potential,
                temporal_contact='[integral p*h d_rho]_(initial)^(final): final plus, initial minus',
                radial_contact='[pi_rho*h]_(pole)^(wall): wall plus, pole minus',
                contacts_already_appended_to_derivative_form=False,
                background_generator_Gram=8*np.eye(3),
                mechanical_component_normalized_weak_Euler=residual/8,
                strong_point_Euler_at_singular_birth=None,
                common_normalization='per kappa1/SAME connection embedding index; unit-Tr16 internal basis; not assigned')


def _bracket(a, b):
    """Bracket in the actual unit-Tr16 weak basis and central hypercharge.

    H_a=-i T_a/sqrt(2), so [H_a,H_b]=eps_abc H_c/sqrt(2).
    jmath_a=-2i T_a=sqrt(8) H_a gives the owned ad_jmath=2 eps.
    """
    out = np.zeros(np.broadcast_shapes(np.shape(a), np.shape(b)), dtype=complex)
    out[..., :3] = np.cross(np.asarray(a)[..., :3], np.asarray(b)[..., :3])/np.sqrt(2)
    return out


def _curl_linear(background, value, angular_derivative):
    result = 2*np.asarray(value, complex).copy()
    eps = epsilon()
    for i in range(3):
        for j in range(3):
            for k in range(3):
                if eps[i, j, k]:
                    result[..., i, :] += eps[i, j, k]*(
                        angular_derivative[..., j, k, :]
                        +_bracket(background[..., j, :], value[..., k, :]))
    return result


def _curl_mixed(a, b):
    result = np.zeros_like(a, dtype=complex)
    eps = epsilon()
    for i in range(3):
        for j in range(3):
            for k in range(3):
                if eps[i, j, k]:
                    result[..., i, :] += eps[i, j, k]*_bracket(a[..., j, :], b[..., k, :])
    return result


def angular_ward_probe():
    """Evaluate all eight saved n1 Q lifts and a gauge test exactly on S3.

    The +/- coordinate-axis S3 rule integrates their degree-two products
    exactly in Haar measure.  The real n1 gauge test is a numerical gauge
    variation, not a physical source/state or a selected particle mode.
    """
    quaternions = np.concatenate((np.eye(4), -np.eye(4)))
    x0, x1, x2, x3 = quaternions.T
    a, b = x0+1j*x3, x2+1j*x1
    D = np.array([[a, b], [-b.conj(), a.conj()]]).transpose(2, 0, 1)
    phi = np.sqrt(2)*D.conj()
    _, _, _, J, _ = angular_blocks(1)
    E = 2j*J
    eta = np.zeros((4, 2, 2), complex)
    eta[0, 0, 0] = 1

    def derivative(coefficients, index):
        return np.einsum('mn,...nk->...mk', E[index], coefficients)

    def evaluate(coefficients):
        # Taking the real section commutes with the real vector fields.
        return np.einsum('...mk,pmk->...p', coefficients, phi).real

    return dict(evaluate=evaluate, derivative=derivative,
                eta=evaluate(eta).T,
                eta_angular=np.array([evaluate(derivative(eta, i)).T for i in range(3)]).transpose(1, 0, 2),
                eta_second=np.array([[evaluate(derivative(derivative(eta, i), j)).T
                                      for i in range(3)] for j in range(3)]).transpose(2, 0, 1, 3),
                Haar_weights=np.full(8, 1/8), gauge_probe_scope='CONTROL_ONLY real n1 gauge parameter')


def off_shell_gauge_ward_application(data, quadrature, source, source_tau,
                                     source_rho, source_angular, probe):
    """Evaluate S''[a,D_A eta]+S'[[a,eta]] on the actual first jet.

    All source arrays have (radial,source,Haar_point,spatial,internal) axes;
    source_angular inserts derivative-index before spatial.  Temporal and
    radial source one-forms are zero for these saved spatial lift probes.
    Both the full curvature Hessian contact and the nonzero background
    Euler application are retained.  No on-shell Gauss identity is imposed.
    """
    a, at, ar, ea = (np.asarray(x, complex) for x in (
        source, source_tau, source_rho, source_angular))
    lam, lt, lr, shift, e, r, d = (np.asarray(data[k], float) for k in (
        'connection_lambda', 'lambda_tau', 'lambda_rho', 'shift',
        'electric', 'radial', 'angular'))
    internal = np.column_stack((np.eye(3), np.zeros(3)))
    reshape = lambda v: v[:, None, None, None, None]
    bg = np.sqrt(8)*reshape(lam-1)*internal
    ft = np.sqrt(8)*reshape(lt)*internal
    fr = np.sqrt(8)*reshape(lr)*internal
    magnetic = 2*np.sqrt(8)*reshape(lam*(lam-1))*internal
    eta = probe['eta'][None, None, :, None, :]
    eta_e = probe['eta_angular'][None, None]
    z = eta_e+_bracket(bg, eta)
    zt, zr = _bracket(ft, eta), _bracket(fr, eta)
    ez = probe['eta_second'][None, None]+_bracket(bg[..., None, :, :], eta_e[..., :, None, :])
    ba, bz = _curl_linear(bg, a, ea), _curl_linear(bg, z, ez)
    contact = _curl_mixed(a, z)
    q = _bracket(a, eta)
    qt, qr = _bracket(at, eta), _bracket(ar, eta)
    eq = _bracket(ea, eta[..., None, :, :])+_bracket(a[..., None, :, :], eta_e[..., :, None, :])
    bq = _curl_linear(bg, q, eq)
    normal_a, normal_z = at-reshape(shift)*ar, zt-reshape(shift)*zr
    normal_bg = ft-reshape(shift)*fr

    def inner(x, y):
        return np.einsum('...ic,...ic->...', np.conjugate(x), y).real

    electric = e[:, None, None]*inner(normal_a, normal_z)
    radial = -r[:, None, None]*inner(ar, zr)
    magnetic_pair = -d[:, None, None]*inner(ba, bz)
    curvature_contact = -d[:, None, None]*inner(magnetic, contact)
    background_Euler = (e[:, None, None]*inner(normal_bg, qt-reshape(shift)*qr)
                        -r[:, None, None]*inner(fr, qr)-d[:, None, None]*inner(magnetic, bq))
    hessian = electric+radial+magnetic_pair+curvature_contact
    total = hessian+background_Euler
    integrate = lambda values: np.einsum('r,p,rAp->A', np.asarray(quadrature), probe['Haar_weights'], values)
    h, b, c, residual = (integrate(x) for x in (hessian, background_Euler, curvature_contact, total))
    return dict(hessian_on_gauge_tangent=h, background_Euler_commutator=b,
                curvature_Hessian_contact=c, Ward_pairing=residual,
                Ward_max_density_defect=float(np.max(abs(total))),
                Ward_relative_density_defect=float(np.max(abs(total))/(1+np.max(abs(hessian))+np.max(abs(background_Euler)))),
                gauge_test=probe['gauge_probe_scope'],
                overall_normalization='per kappa1/SAME connection embedding index; not assigned',
                physical_source_identification=False, complete_native_action=False)


def evaluate_retained_background(repository=ROOT, *, quadrature_order=256, test_order=8):
    nodes, weights = leggauss(quadrature_order)
    rho, weights = WALL*(nodes+1)/2, WALL*weights/2
    data = retained_connection_first_jet(rho, repository)
    H, Hr = regular_radial_basis(rho, test_order)
    weak = background_weak_application(data, weights, H, Hr, np.zeros_like(H))
    probe = angular_ward_probe()
    with np.load(Path(repository)/SOURCE, allow_pickle=False) as z:
        coefficients = np.array(z['original_n1'])
    val = probe['evaluate'](coefficients).transpose(0, 3, 1, 2)
    source_Gram = np.einsum('Apic,Bpic,p->AB', val, val, probe['Haar_weights'])
    source_Gram_defect = float(np.linalg.norm(source_Gram-(16/3)*np.eye(8)))
    if source_Gram_defect > 2e-11:
        raise ValueError('Haar rule or saved real Q source representation changed')
    ev = np.array([probe['evaluate'](probe['derivative'](coefficients, i)).transpose(0, 3, 1, 2)
                   for i in range(3)]).transpose(1, 2, 0, 3, 4)
    source = H[:, 0, None, None, None, None]*val[None]
    source_rho = Hr[:, 0, None, None, None, None]*val[None]
    source_angular = H[:, 0, None, None, None, None, None]*ev[None]
    ward = off_shell_gauge_ward_application(data, weights, source, np.zeros_like(source),
                                           source_rho, source_angular, probe)
    wall = retained_connection_first_jet(np.array([WALL]), repository)
    contact = background_weak_application(wall, np.ones(1), np.ones(1), np.zeros(1), np.zeros(1))
    return dict(rho=rho, quadrature=weights, connection=data, weak=weak, Ward=ward,
                source_Gram=source_Gram, source_Gram_defect=source_Gram_defect,
                contact_wall=dict(temporal_momentum_density=float(contact['temporal_momentum_density'][0]),
                                  outward_radial_action_flux=float(contact['radial_momentum_density'][0]),
                                  unit_test_DtN_reaction=float(-contact['radial_momentum_density'][0]),
                                  radial_pole_action_flux=0.,
                                  pole_zero_role='derived regular-pole density limit; not an extra boundary condition'),
                scope='EVALUATED_RETAINED_E1_PLUS_MAXWELL_FIRST_JET_WEAK_EULER_AND_OFF_SHELL_WARD',
                primal_acceleration_evaluated=False, native_Pauli_evaluated=False)


def materialize(output, repository=ROOT):
    path = Path(output)
    if path.exists():
        raise FileExistsError('preserve prior evidence; use a new output directory')
    result = evaluate_retained_background(repository)
    path.mkdir(parents=True)
    arrays = dict(rho=result['rho'], quadrature=result['quadrature'])
    arrays['actual_saved_Q_source_Haar_Gram'] = result['source_Gram']
    for group in ('weak', 'Ward'):
        arrays.update({group+'_'+k:v for k,v in result[group].items() if isinstance(v, np.ndarray)})
    arrays.update({k:result['connection'][k] for k in (
        'connection_lambda','lambda_tau','lambda_rho','normal_lambda_rate','electric','radial','angular','shift')})
    with ZipFile(path/'application.npz', 'w', compression=ZIP_STORED) as archive:
        for name, value in sorted(arrays.items()):
            stream = BytesIO(); np.lib.format.write_array(stream, np.asarray(value), allow_pickle=False)
            member = ZipInfo(name+'.npy', date_time=(1980,1,1,0,0,0)); member.external_attr=0o600 << 16
            archive.writestr(member, stream.getvalue())
    refs = [STATE_SOURCE, RESET_RECEIPT, SOURCE, 'src/bhsm/interface/muon_parent_maxwell_background_euler.py',
        'src/bhsm/interface/muon_parent_retarded_hypercharge.py',
        'src/bhsm/interface/muon_matched_mechanical_source.py',
        'src/bhsm/interface/muon_moving_geometric_action.py']
    receipt = dict(scope=result['scope'], input_hashes={p:sha256((Path(repository)/p).read_bytes()).hexdigest() for p in refs},
        weak_Euler=result['weak']['weak_Euler'].tolist(), temporal_momentum_test=result['weak']['temporal_momentum_test'].tolist(),
        background_generator_Gram=result['weak']['background_generator_Gram'].tolist(),
        common_normalization=result['weak']['common_normalization'],
        Ward={k:v.tolist() if isinstance(v,np.ndarray) else v for k,v in result['Ward'].items()},
        source_Haar_Gram_defect=result['source_Gram_defect'], wall_contacts=result['contact_wall'],
        representation=dict(radial_test_order=8, radial_quadrature_order=256,
                            angular_rule='eight +/- quaternion axes; exact Haar integration through degree two',
                            source='all eight saved Q lifts before moving-frame transport; no central projection',
                            gauge_probe='real n1 numerical gauge test; not a physical external source'),
        temporal_contact=result['weak']['temporal_contact'], radial_contact=result['weak']['radial_contact'],
        strong_point_Euler_at_singular_birth=None, primal_acceleration_evaluated=False,
        actual_velocity_first_jet=True, physical_Pauli_contraction=False,
        derivation='S_second[a,D_A_eta]+S_first[[a,eta]]=0; background Euler term retained off shell',
        error_scope='binary64 exact finite n1 representation and Gauss radial quadrature; not a continuum tail enclosure')
    (path/'result.json').write_text(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+'\n', encoding='utf8', newline='\n')
    return receipt


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(); print(json.dumps(materialize(args.output),sort_keys=True))
