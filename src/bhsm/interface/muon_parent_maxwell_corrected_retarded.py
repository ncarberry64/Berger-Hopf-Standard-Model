"""Full five-component Hessian on one corrected common finite iterate.

Every independent temporal/radial/spatial connection coefficient is retained.
The complete n1+n3 angular linearization closes because this background is
angular constant.  It is a local numerical iterate, not a physical history.
The retarded fixed slice keeps its nonstationary gauge reaction explicitly.
"""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp, simpson
from scipy.interpolate import CubicSpline
from scipy.linalg import cho_factor, cho_solve

from .muon_birth_candidate_geometry_action import ROOT
from .muon_moving_geometric_action import retained_state
from .muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from .muon_parent_maxwell_full_retarded import constrained_gauss_schur, _reduced_at, _hamilton_rhs
from .muon_parent_maxwell_full_weak import M
from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from .muon_parent_gauge_geometry_correction import correction_representation, finite_common_iterate_at_time
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_parent_retarded_hypercharge import WALL, regular_radial_basis, compact_trace_pulse
from .muon_matched_mechanical_source import epsilon

DEFAULT_ITERATE = 'artifacts/muon_parent_gauge_geometry_correction_20261010/material_wall_mean_run_1'
ITERATE_RECEIPT_SHA = '3137302eb7b92d7c6b5f999095e82f84f55996ed20b2a47ec35a56c96495539c'
ITERATE_ARRAY_SHA = '4a16d56ec64eeb6c2db10000debf9695f24f7bef634e793011066ed88f8b9383'
ITERATE_BINDER_SHA = 'fa29f5764dca39196c807d64e7976d5894589e7de3ffa9d4a5ddecfb136b4816'


def _ad(a):
    if not np.isrealobj(a):raise ValueError('explicit real unit-Tr16 components required')
    a = np.asarray(a, float)
    if a.shape != (4,) or not np.isfinite(a).all():
        raise ValueError('finite unit-Tr16 four-component connection required')
    out = np.zeros((4, 4))
    out[:3, :3] = np.einsum('abc,a->cb', epsilon(), a[:3])/np.sqrt(2)
    return out


def constant_angular_curvatures(gauge, gauge_tau, gauge_rho):
    """Literal full curvature; no At, Ar or independent Ai is discarded."""
    if any(not np.isrealobj(x) for x in (gauge,gauge_tau,gauge_rho)):
        raise ValueError('explicit realification required; no complex field projection')
    A, At, Ar = [np.asarray(x, float) for x in (gauge, gauge_tau, gauge_rho)]
    if any(x.shape != (5, 4) or not np.isfinite(x).all() for x in (A, At, Ar)):
        raise ValueError('finite complete five-component value and first jets required')
    eps = epsilon()
    Ftr = At[1]-Ar[0]+_ad(A[0])@A[1]
    Ft = At[2:]+np.array([_ad(A[0])@a for a in A[2:]])
    Fr = Ar[2:]+np.array([_ad(A[1])@a for a in A[2:]])
    B = 2*A[2:].copy()
    for i, j, k in np.argwhere(eps):
        B[i] += .5*eps[i, j, k]*(_ad(A[2+j])@A[2+k])
    return dict(Ftr=Ftr, Ft=Ft, Fr=Fr, B=B)


def full_constant_angular_hessian(gauge, gauge_tau, gauge_rho, densities):
    """Exact real frame/harmonic tensor of the literal scalar Hessian.

    The tensor H[i,j,p,q,a,b] multiplies E_p^T E_q, E_0=I,
    for field jets (value,tau,rho).  It represents ALL 400 columns once
    tensored with the owned twenty real harmonics.  Curvature contacts are
    included in H[0,0,0,0], not suppressed by an on-shell assumption.
    """
    if any(not np.isrealobj(x) for x in (gauge,gauge_tau,gauge_rho,densities)):
        raise ValueError('explicit realification required; no complex action projection')
    A = np.asarray(gauge, float)
    F = constant_angular_curvatures(A, gauge_tau, gauge_rho)
    c = np.asarray(densities, float)
    if c.shape != (5,) or not np.isfinite(c).all() or np.any(c[:4] <= 0):
        raise ValueError('positive electric/radial/angular/electric-radial and finite shift required')
    e, r, d, k, beta = c
    selectors = np.eye(20).reshape(5, 4, 20)
    a0, ar, S = selectors[0], selectors[1], selectors[2:].reshape(12, 20)
    X = np.zeros((3, 4, 4, 20)); T = np.zeros((3, 4, 12, 20)); R = np.zeros_like(T)
    B = np.zeros((3, 4, 12, 20))
    X[0, 0] = _ad(A[0])@ar-_ad(A[1])@a0
    X[1, 0] = ar; X[2, 0] = -a0
    for i in range(3):
        sl = slice(4*i, 4*i+4)
        T[0, 0, sl] = _ad(A[0])@selectors[2+i]-_ad(A[2+i])@a0
        R[0, 0, sl] = _ad(A[1])@selectors[2+i]-_ad(A[2+i])@ar
        T[0, i+1, sl] = -a0; R[0, i+1, sl] = -ar
        B[0, 0, sl] = 2*selectors[2+i]
    T[1, 0] = S; R[2, 0] = S
    for i, j, h in np.argwhere(epsilon()):
        sl = slice(4*i, 4*i+4)
        B[0, j+1, sl] += epsilon()[i, j, h]*selectors[2+h]
        B[0, 0, sl] += epsilon()[i, j, h]*(_ad(A[2+j])@selectors[2+h])
    Y = T-beta*R
    H = k*np.einsum('ipxa,jqxb->ijpqab', X, X)
    H += e*np.einsum('ipxa,jqxb->ijpqab', Y, Y)
    H -= r*np.einsum('ipxa,jqxb->ijpqab', R, R)
    H -= d*np.einsum('ipxa,jqxb->ijpqab', B, B)
    C = np.zeros((20, 20))
    def contact(i, j, f):
        # f.[u_i,v_j]+f.[v_i,u_j], real symmetric scalar Hessian.
        z = np.einsum('abc,c->ab', epsilon(), np.asarray(f)[:3])/np.sqrt(2)
        block = np.zeros((4, 4)); block[:3, :3] = z
        C[4*i:4*i+4, 4*j:4*j+4] += block
        C[4*j:4*j+4, 4*i:4*i+4] += block.T
    contact(0, 1, k*F['Ftr'])
    for i in range(3):
        contact(0, 2+i, e*(F['Ft'][i]-beta*F['Fr'][i]))
        contact(1, 2+i, -e*beta*(F['Ft'][i]-beta*F['Fr'][i])-r*F['Fr'][i])
    for i, j, h in np.argwhere(epsilon()):
        # Ordered j,h counts both magnetic mixed contractions: .5 here.
        contact(2+j, 2+h, -.5*d*epsilon()[i, j, h]*F['B'][i])
    H[0, 0, 0, 0] += C
    return dict(tensor=H, curvature_contact=C, X=X, electric=Y,
                radial=R, magnetic=B, curvatures=F, densities=c)


def _lift_tensor(tensor, harmonic_products):
    return np.einsum('pqab,pqnm->anbm', tensor, harmonic_products).reshape(400, 400)


def _integrated_time_forms(local, w, H, Hr, Q, harmonic_products):
    def block(i, j, left, right):
        result = np.zeros((408, 408))
        for l, ls in enumerate(left):
            for r, rs in enumerate(right):
                tensor = np.einsum('r,rpqab->pqab', w*ls*rs, local[:, i, j])
                matrix = _lift_tensor(tensor, harmonic_products)
                if l == 0 and r == 0: result[:400, :400] += matrix
                elif l == 0: result[:400, 400:] += matrix@Q
                elif r == 0: result[400:, :400] += Q.T@matrix
                else: result[400:, 400:] += Q.T@matrix@Q
        return result
    values = H.T; derivatives = Hr.T
    mass = block(1, 1, values, values)
    mixed = block(0, 1, values, values)+block(2, 1, derivatives, values)
    stiffness = (block(0, 0, values, values)+block(0, 2, values, derivatives)
        +block(2, 0, derivatives, values)+block(2, 2, derivatives, derivatives))
    return mass, mixed, (stiffness+stiffness.T)/2


def _gauge_rows(local, gauge, w, H, Hr, Q, E):
    """Same-action D_A eta weak rows; use exact delta F=[F,eta].

    Gauge eta has radial profile phi and a freely differentiated temporal
    coefficient.  Its eta_dot coefficient contributes At and curvature
    contacts; full derivative first variations cancel, not their Euler row.
    """
    out = np.zeros((4, 80, 408)); I = np.eye(20)
    for j, (row, A) in enumerate(zip(local, gauge)):
        phi, lift = H[j]; phir, liftr = Hr[j]
        e, r, d, k, beta = row['densities']; F = row['curvatures']
        L = [(k, _ad(F['Ftr']), row['X']),
             (e, np.vstack([_ad(f) for f in F['Ft']-beta*F['Fr']]), row['electric']),
             (-r, np.vstack([_ad(f) for f in F['Fr']]), row['radial']),
             (-d, np.vstack([_ad(f) for f in F['B']]), row['magnetic'])]
        G = np.zeros((4, 20, 4))
        for h in range(5): G[0, h*4:h*4+4] = phi*_ad(A[h])
        G[0, 4:8] += phir*np.eye(4)
        for h in range(3): G[h+1, (2+h)*4:(3+h)*4] = phi*np.eye(4)
        Gdot = np.zeros((20, 4)); Gdot[:4] = phi*np.eye(4)
        for derivative, profile in ((0, H[j]), (2, Hr[j]), (1, H[j])):
            kernel = np.zeros((4, 4, 20))
            for density, curvature_ad, maps in L:
                kernel += density*phi*np.einsum('xa,pxb->pab', curvature_ad, maps[derivative])
            if derivative == 0:
                kernel += np.einsum('pca,cb->pab', G, row['curvature_contact'])
            target = 1 if derivative == 1 else 0
            for source, amount in enumerate(profile):
                matrix = sum(np.kron(kernel[p], E[p] if p else I) for p in range(4))
                # First curvature term uses E_p; G^T contact uses E_p^T.
                if derivative == 0:
                    correction = np.einsum('pca,cb->pab', G, row['curvature_contact'])
                    matrix += sum(np.kron(correction[p], E[p].T-E[p]) for p in range(1, 4))
                if source == 0: out[target, :, :400] += w[j]*amount*matrix
                else: out[target, :, 400:] += w[j]*amount*(matrix@Q)
        kernel = Gdot.T@row['curvature_contact']
        matrix = np.kron(kernel, I)
        out[2, :, :400] += w[j]*phi*matrix
        out[2, :, 400:] += w[j]*lift*(matrix@Q)
    return out


def load_corrected_iterate(repository=ROOT, application=DEFAULT_ITERATE):
    repository = Path(repository); path = repository/application
    receipt_bytes = (path/'result.json').read_bytes()
    if application == DEFAULT_ITERATE and sha256(receipt_bytes).hexdigest() != ITERATE_RECEIPT_SHA:
        raise ValueError('pinned canonical common iterate receipt mismatch')
    binder = repository/'src/bhsm/interface/muon_parent_gauge_geometry_correction.py'
    if sha256(binder.read_bytes()).hexdigest() != ITERATE_BINDER_SHA:
        raise ValueError('canonical common iterate requires its frozen coefficient binder')
    receipt = json.loads(receipt_bytes)
    if receipt.get('gauge_trace_chart')!='MATERIAL_REFERENCE_ONE_FORM' or receipt.get('temporal_order')!=1:
        raise ValueError('material-chart first temporal trial is required by this coefficient binder')
    for source, expected in receipt['input_hashes'].items():
        if sha256((repository/source).read_bytes()).hexdigest() != expected:
            raise ValueError('corrected common iterate input/source hash mismatch: '+source)
    payload = (path/'application.npz').read_bytes()
    if sha256(payload).hexdigest() != receipt['numerical_sha256']:
        raise ValueError('corrected common coefficient receipt hash mismatch')
    if application == DEFAULT_ITERATE and sha256(payload).hexdigest() != ITERATE_ARRAY_SHA:
        raise ValueError('pinned canonical common iterate coefficient mismatch')
    with np.load(path/'application.npz', allow_pickle=False) as data:
        coefficients = np.array(data['updated_coefficients'])
    rep = correction_representation(repository=repository,
        length=receipt['numerical_local_interval_length'],
        time_points=receipt['temporal_quadrature_order'], radial_points=receipt['radial_quadrature_order'],
        radial_order=receipt['gauge_unknowns']//20-int(receipt['include_wall_lift']),
        cap_points=receipt['cap_quadrature_order'], include_wall_lift=receipt['include_wall_lift'],
        include_scalar_mean=receipt.get('include_scalar_mean', False))
    if coefficients.shape != (rep['count'],) or not np.isfinite(coefficients).all():
        raise ValueError('complete corrected common coefficient vector required')
    if rep['count']!=receipt['count'] or rep['geometry_count']!=receipt['geometry_unknowns'] or rep['scalar_count']!=receipt['scalar_unknowns']:
        raise ValueError('corrected common blocks disagree with the coefficient basis')
    return coefficients, rep, receipt


def corrected_retarded_form(repository=ROOT, *, application=DEFAULT_ITERATE,
                            time_nodes=17, radial_points=48):
    if type(time_nodes) is not int or time_nodes < 5 or type(radial_points) is not int or radial_points < 12:
        raise ValueError('resolved explicit numerical quadrature required')
    coefficients, rep, receipt = load_corrected_iterate(repository, application)
    angular = retained_full_q_angular_space(repository); Q = angular['source_coefficients']
    E = np.concatenate((np.eye(20)[None], angular['derivative_matrices']))
    products = np.array([[a.T@b for b in E] for a in E])
    x, w = leggauss(radial_points); rho = (x+1)*WALL/2; w *= WALL/2
    H, Hr = regular_radial_basis(rho, 1); times = np.linspace(0, rep['length'], time_nodes)
    reference = retained_state(repository); raw=[]; rows=[]; field_values=[]; geom=[]; density=[]; grads=[]; normal_h=[]
    for u in times:
        data = finite_common_iterate_at_time(u-rep['length'], coefficients, rep, reference, rho=rho)
        c = geometric_connection_coefficient_jets(12, data['q'], data['qdot'], data['m'], rho,
            source_value=data['normal'], source_rate=data['normal_rate'], clock='coordinate_time')
        A, At, Ar = [data['fields'][k][:, 0].copy() for k in ('gauge','gauge_tau','gauge_rho')]
        for j, row in enumerate(c['rows']):
            A[j, 2:] += M*(row['connection_lambda'].value-1)
            At[j, 2:] += M*row['lambda_tau'].value
            Ar[j, 2:] += M*row['lambda_rho'].value
        den = np.array([[row[k].value for k in ('electric','radial','angular','electric_radial','shift')] for row in c['rows']])
        local = [full_constant_angular_hessian(A[j], At[j], Ar[j], den[j]) for j in range(radial_points)]
        raw.append(_integrated_time_forms(np.array([a['tensor'] for a in local]), w, H, Hr, Q, products))
        rows.append(_gauge_rows(local, A, w, H, Hr, Q, E))
        field_values.append(np.array([A, At, Ar])); density.append(den)
        geom.append(np.r_[data['q'], data['qdot'], data['m'], data['normal'], data['normal_rate']])
        grads.append(np.array([[row[k].gradient for k in ('electric','radial','angular','electric_radial','shift')] for row in c['rows']]))
        normal_h.append(np.array([[row[k].hessian[:, -2:] for k in ('electric','radial','angular','electric_radial','shift')] for row in c['rows']]))
    forms = [constrained_gauss_schur(*matrices, 80) for matrices in raw]
    result = dict(angular=angular, rho=rho, quadrature=w, H=H, Hr=Hr,
        time_nodes=times, duration=rep['length']/3, final_time=rep['length'],
        gauge_weak_rows=CubicSpline(times, np.array(rows)),
        raw_forms=raw, forms=forms, corrected_coefficients=coefficients,
        corrected_geometry=np.array(geom), full_background_values=np.array(field_values),
        density_values=np.array(density), density_geometric_jacobian=np.array(grads),
        density_normal_hessian_columns=np.array(normal_h), iterate_receipt=receipt,
        application=application, represented_time_shift=-rep['length'])
    result['background_spline'] = CubicSpline(times, result['full_background_values'])
    result['density_spline'] = CubicSpline(times, result['density_values'])
    for i, name in enumerate(('raw_M','raw_B','raw_K')):
        result[name] = CubicSpline(times, np.array([f[i] for f in raw]))
    result['minimum_interior_mass_eigenvalue'] = min(float(np.linalg.eigvalsh(f['M'][:320,:320])[0]) for f in forms)
    if result['minimum_interior_mass_eigenvalue'] <= 0:
        raise ArithmeticError('positive finite interior kinetic form required')
    return result


def _mean_bracket(fields, eta_profile):
    u = np.asarray(fields).reshape(5, 4, 20, 8).transpose(3, 0, 1, 2)
    out = np.zeros((8, 80, 5, 4))
    for a, b, c in np.argwhere(epsilon()):
        out[:, b*20:(b+1)*20, :, c] += eta_profile*epsilon()[a,b,c]*u[:,:,a,:].transpose(0,2,1)/np.sqrt(2)
    return out


def intrinsic_scalar_trace_hessian(H, H_tau, gauge_trace, metric_weights, *, lambda_H, nu_squared_action, angular):
    """Literal real scalar Hessian on all80 odd scalar and400 gauge traces.

    Coordinates are (H80, gauge400, H_tau80).  Gauge traces are material
    one-form components: the fixed material wall consumes At_ref exactly
    once.  Its temporal pullback has no additional wall-rate*Ar_ref term.
    This routine returns the exact coefficient matrix, not a chosen state.
    """
    if any(not np.isrealobj(x) for x in (H,H_tau,gauge_trace,metric_weights)):
        raise ValueError('explicit realification required; no complex scalar projection')
    H,Ht,A=(np.asarray(x,float) for x in (H,H_tau,gauge_trace))
    weights=np.asarray(metric_weights,float)
    if (H.shape!=(4,) or Ht.shape!=(4,) or A.shape!=(5,4) or weights.shape!=(3,)
        or any(not np.isfinite(x).all() for x in (H,Ht,A,weights)) or np.any(weights<=0)
        or not np.isfinite([lambda_H,nu_squared_action]).all() or lambda_H<=0 or nu_squared_action<0):
        raise ValueError('complete real Higgs/background/metric and explicit potential coefficient required')
    T=higgs_u2_real_representation()['real_generators']
    Omega=np.einsum('fc,cij->fij',A,T)
    E=angular['derivative_matrices']; I=np.eye(20)
    generators_on_H=np.einsum('cij,j->ic',T,H)
    ordinary_Ht=Ht+Omega[0]@H
    spatial_H=np.einsum('aij,j->ai',Omega[2:],H)
    time=np.zeros((80,560));time[:,:80]=np.kron(Omega[0],I)
    time[:,80:160]=np.kron(generators_on_H,I)
    time[:,480:]=np.eye(80)
    spatial=np.zeros((3,80,560))
    for a in range(3):
        spatial[a,:,:80]=np.kron(np.eye(4),E[a])+np.kron(Omega[2+a],I)
        spatial[a,:,80+(2+a)*80:80+(3+a)*80]=np.kron(generators_on_H,I)
    wt,ws,wv=weights; volume=2*np.pi**2
    matrix=2*volume*(wt*(time.T@time)-ws*sum(x.T@x for x in spatial))
    potential=lambda_H*(8*np.outer(H,H)+4*(H@H-nu_squared_action)*np.eye(4))
    matrix[:80,:80]-=volume*wv*np.kron(potential,I)
    # δ²(DH)=δOmega δH.  These mixed contacts survive on an off-shell H.
    for direction,base,weight in [(0,ordinary_Ht,wt)]+[(2+a,spatial_H[a],-ws) for a in range(3)]:
        mixed=2*volume*weight*np.einsum('i,cij->jc',base,T)
        block=np.kron(mixed,I)
        start=80+direction*80
        matrix[:80,start:start+80]+=block
        matrix[start:start+80,:80]+=block.T
    return dict(matrix=matrix,nu_squared_coefficient=4*volume*wv*lambda_H*np.eye(80),
        H_covariant_time=ordinary_Ht,H_covariant_spatial=spatial_H,
        scalar_count=80,gauge_trace_count=400,pairing='real2Re; unitHaar*2pi^2 once',
        gauge_trace_chart='material_reference',extra_wall_advection_count=0,
        complete_interacting_physical_operator=False)


def corrected_gauge_euler_reaction(form, time, state, velocity):
    """Independent literal native Ward/Euler contact, sampled estimate only."""
    g, gd, _ = compact_trace_pulse(time, form['duration']); Q=form['angular']['source_coefficients']
    count=form.get('spatial_interior_unknowns',320)
    z=np.vstack((state[:count],g*np.eye(8))); dz=np.vstack((velocity,gd*np.eye(8)))
    current=_reduced_at(form,time)
    at=current['At_value_map']@z+current['At_velocity_map']@dz
    # At_tau drops out of the action's first variation of [u,eta], since
    # no derivative tau of its temporal component occurs.  No At jet is
    # silently omitted from a curvature that actually consumes it.
    full=np.vstack((at,z[:320],z[count:])); full_dot=np.vstack((np.zeros_like(at),dz[:320],dz[count:]))
    A, At, Ar=form['background_spline'](time); density=form['density_spline'](time)
    result=np.zeros((80,8))
    for j,(background, bt, br, den, w) in enumerate(zip(A,At,Ar,density,form['quadrature'])):
        p,l=form['H'][j]; pr,lr=form['Hr'][j]
        u=p*full[:400]+l*(Q@full[400:])
        ut=p*full_dot[:400]+l*(Q@full_dot[400:])
        ur=pr*full[:400]+lr*(Q@full[400:])
        W=_mean_bracket(u,p*g)
        Wt=_mean_bracket(ut,p*g)+_mean_bracket(u,p*gd)
        Wr=_mean_bracket(ur,p*g)+_mean_bracket(u,pr*g)
        F=constant_angular_curvatures(background,bt,br)
        # Haar mean angular derivative of the commutator product is zero;
        # its constant internal covariant connection action survives.
        X=Wt[:,:,1]-Wr[:,:,0]+W[:,:,1]@_ad(background[0]).T-W[:,:,0]@_ad(background[1]).T
        T=Wt[:,:,2:].copy(); R=Wr[:,:,2:].copy(); B=2*W[:,:,2:].copy()
        for i in range(3):
            T[:,:,i]+=W[:,:,2+i]@_ad(background[0]).T-W[:,:,0]@_ad(background[2+i]).T
            R[:,:,i]+=W[:,:,2+i]@_ad(background[1]).T-W[:,:,1]@_ad(background[2+i]).T
        for i,h,k in np.argwhere(epsilon()):
            B[:,:,i]+=epsilon()[i,h,k]*(W[:,:,2+k]@_ad(background[2+h]).T)
        e,r,d,k,beta=den
        contact=k*np.einsum('c,abc->ab',F['Ftr'],X)
        contact+=e*np.einsum('ic,abic->ab',F['Ft']-beta*F['Fr'],T-beta*R)
        contact-=r*np.einsum('ic,abic->ab',F['Fr'],R)
        contact-=d*np.einsum('ic,abic->ab',F['B'],B)
        result-=w*contact.T
    return result


def augment_intrinsic_scalar_forms(maxwell_forms, scalar_hessian, source_coefficients):
    """Add intrinsic H80 and all source/Schur cross blocks to one action.

    Parent interior trials have zero walltrace; the prescribed wall source
    is the only independent boundary gauge coordinate in this Dirichlet
    application.  H is intrinsic, not another radial bulk field.  In the
    per-kappa1 Maxwell convention the intrinsic action multiplier is8,
    derived from their common cap normalization, not fitted to data.
    """
    if any(not np.isrealobj(x) for x in (*maxwell_forms,scalar_hessian,source_coefficients)):
        raise ValueError('explicit realification required; no complex mixed-action projection')
    M0,B0,K0=(np.asarray(x,float) for x in maxwell_forms)
    S=np.asarray(scalar_hessian,float);Q=np.asarray(source_coefficients,float)
    if any(x.shape!=(408,408) or not np.isfinite(x).all() for x in (M0,B0,K0)) or S.shape!=(560,560) or Q.shape!=(400,8):
        raise ValueError('complete same-action full Maxwell/scalar and eight source maps required')
    matrices=[];indices=np.r_[np.arange(400),np.arange(480,488)]
    for old in (M0,B0,K0):
        new=np.zeros((488,488));new[np.ix_(indices,indices)]=old;matrices.append(new)
    value=np.zeros((560,488));velocity=np.zeros_like(value)
    value[:80,400:480]=np.eye(80);value[80:480,480:]=Q
    velocity[480:,400:480]=np.eye(80)
    matrices[0]+=8*(velocity.T@S@velocity)
    matrices[1]+=8*(value.T@S@velocity)
    matrices[2]+=8*(value.T@S@value)
    return tuple(matrices)


def _corrected_hamiltonian_rhs(form,t,y):
    count=form.get('spatial_interior_unknowns',320)
    state=np.asarray(y).reshape(2*count,8);x,p=state[:count],state[count:]
    current=_reduced_at(form,t);mass,mixed,stiffness=(current[k] for k in ('M','B','K'))
    g,gd,_=compact_trace_pulse(t,form['duration'])
    velocity=cho_solve(cho_factor(mass[:count,:count]),p-mixed[:count,:count].T@x
        -g*mixed[count:,:count].T-gd*mass[:count,count:])
    force=(mixed[:count,:count]@velocity+g*stiffness[:count,count:]
        +gd*mixed[:count,count:]+stiffness[:count,:count]@x)
    return np.concatenate((velocity,force)).ravel()


def coupled_corrected_retarded_form(repository=ROOT,*,application=DEFAULT_ITERATE,time_nodes=17,radial_points=48):
    """Parent+intrinsic H Dirichlet-to-Neumann application on one iterate.

    The source boundary trace is prescribed.  A child/interface/exterior
    return is not replaced by an invented free-wall boundary law.  This is
    the actual total parent and intrinsic scalar action coefficient; its
    final physical graph and native loads remain distinct obligations.
    """
    form=corrected_retarded_form(repository,application=application,time_nodes=time_nodes,radial_points=radial_points)
    coefficients,rep,receipt=load_corrected_iterate(repository,application)
    nu=receipt['action_parameters']['nu_squared_action']
    if nu is None:raise ValueError('coupled scalar retarded member needs its explicit common nu_squared_action')
    scalar_coefficients=coefficients[rep['scalar_start']:]
    if not rep['include_scalar_mean'] or scalar_coefficients.shape!=(8,):
        raise ValueError('same complete compact and mean scalar coefficient vector required')
    from .muon_parent_gauge_geometry_correction import compact_temporal_basis
    reference=retained_state(repository);raw=[];scalar_forms=[];scalar_matrices=[];scalar_values=[];metric_values=[];metric_jac=[];metric_normal=[]
    for index,u in enumerate(form['time_nodes']):
        t=u-rep['length'];data=finite_common_iterate_at_time(t,coefficients,rep,reference,rho=np.array([WALL]))
        weights=intrinsic_m4_weight_jet(12,data['q'],data['qdot'],data['m'],source_value=data['normal'],source_rate=data['normal_rate'])
        b,bt=compact_temporal_basis(np.array([t]),rep['length'])
        H=b[0]*scalar_coefficients[:4]+scalar_coefficients[4:];Ht=bt[0]*scalar_coefficients[:4]
        A=data['fields']['gauge'][0,0].copy()
        A[2:]+=M*(weights['mechanical_connection_lambda'].value-1)
        w=np.array([weights[k].value for k in ('wT','wS','wV')])
        scalar=intrinsic_scalar_trace_hessian(H,Ht,A,w,lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=nu,angular=form['angular'])
        raw.append(augment_intrinsic_scalar_forms(form['raw_forms'][index],scalar['matrix'],form['angular']['source_coefficients']))
        scalar_forms.append(augment_intrinsic_scalar_forms((np.zeros((408,408)),)*3,scalar['matrix'],form['angular']['source_coefficients']))
        scalar_matrices.append(scalar['matrix']);scalar_values.append(np.r_[H,Ht]);metric_values.append(w)
        metric_jac.append(np.array([weights[k].gradient for k in ('wT','wS','wV')]))
        metric_normal.append(np.array([weights[k].hessian[:,-2:] for k in ('wT','wS','wV')]))
    rows=form['gauge_weak_rows'](form['time_nodes'])
    expanded=np.zeros((time_nodes,4,80,488));expanded[:,:,:,:400]=rows[:,:,:,:400];expanded[:,:,:,480:]=rows[:,:,:,400:]
    form['gauge_weak_rows']=CubicSpline(form['time_nodes'],expanded)
    form.update(raw_forms=raw,forms=[constrained_gauss_schur(*x,80) for x in raw],
        spatial_interior_unknowns=400,intrinsic_scalar_unknowns=80,
        intrinsic_scalar_matrices=np.array(scalar_matrices),intrinsic_H_values=np.array(scalar_values),
        intrinsic_metric_values=np.array(metric_values),intrinsic_metric_geometric_jacobian=np.array(metric_jac),
        intrinsic_metric_normal_hessian_columns=np.array(metric_normal),nu_squared_action_member=nu,
        scalar_Maxwell_relative_normalization=8.,scalar_trace_chart='material_reference')
    for i,key in enumerate(('raw_M','raw_B','raw_K')):
        form[key]=CubicSpline(form['time_nodes'],np.array([x[i] for x in raw]))
        form['intrinsic_'+key]=CubicSpline(form['time_nodes'],np.array([x[i][80:,80:] for x in scalar_forms]))
    form['minimum_interior_mass_eigenvalue']=min(float(np.linalg.eigvalsh(x['M'][:400,:400])[0]) for x in form['forms'])
    # A homogeneous background and geometry deformation are even under
    # g->-g.  Every represented field/test and its E_i derivative is odd.
    # Thus linear geometry/odd-field mixed rows integrate exactly to zero.
    means=form['angular']['Haar_weights']@form['angular']['basis_values']
    derivative_means=np.einsum('p,pin->in',form['angular']['Haar_weights'],form['angular']['basis_derivative_values'])
    form['Haar_odd_geometry_mixed_audit']=dict(
        exact_reason='homogeneous even background times one n1/n3 odd field or E_i derivative; Haar antipodal symmetry',
        represented_basis_mean_max=float(np.max(abs(means))),represented_derivative_mean_max=float(np.max(abs(derivative_means))),
        limited_to_this_homogeneous_background_and_linearization=True,
        arbitrary_angular_geometry_or_nonlinear_closure_proved=False)
    return form


def corrected_retarded_application(form,*,time_steps=128,rtol=2e-9,atol=2e-11):
    """Apply eight actual angular traces to the full finite retarded operator."""
    T,D=form['final_time'],form['duration'];count=form.get('spatial_interior_unknowns',320)
    if type(time_steps) is not int or time_steps<16:
        raise ValueError('resolved retarded computational time grid required')
    sol=solve_ivp(lambda t,y:_corrected_hamiltonian_rhs(form,t,y),(0,T),np.zeros(2*count*8),method='DOP853',
        rtol=rtol,atol=atol,max_step=D/time_steps,dense_output=True)
    if not sol.success:raise ArithmeticError('full constrained retarded application failed: '+sol.message)
    times=np.linspace(0,T,3*time_steps+1);states=sol.sol(times).T.reshape(-1,2*count,8)
    velocities=np.array([_corrected_hamiltonian_rhs(form,t,s.ravel()).reshape(2*count,8)[:count] for t,s in zip(times,states)])
    gauss=[];At=[];reactions=[];native_contacts=[];wall=[];bilinear=[];gauss_relative=[]
    for t,s,xd in zip(times,states,velocities):
        g,gd,_=compact_trace_pulse(t,D);z=np.vstack((s[:count],g*np.eye(8)));zd=np.vstack((xd,gd*np.eye(8)))
        current=_reduced_at(form,t)
        y=current['At_value_map']@z+current['At_velocity_map']@zd;At.append(y)
        parts=(current['Gauss_matrix']@y,current['Gauss_value_row']@z,current['Gauss_velocity_row']@zd)
        gauss.append(sum(parts));gauss_relative.append(float(np.max(abs(sum(parts)))/(1+sum(np.max(abs(a)) for a in parts))))
        full_z=np.vstack((y,z));full_velocity=np.vstack((np.zeros_like(y),zd))
        G0z,G0v,G1z,G1v=form['gauge_weak_rows'](t)
        reactions.append(g*(G0z@full_z+G0v@full_velocity)+gd*(G1z@full_z+G1v@full_velocity))
        native_contacts.append(corrected_gauge_euler_reaction(form,t,s,xd))
        mass,mixed,stiffness=(current[k] for k in ('M','B','K'))
        momentum=mass@zd+mixed.T@z
        wall.append(-gd*momentum[count:]-g*(mixed[count:]@zd+stiffness[count:]@z))
        bilinear.append(zd.T@mass@zd+z.T@mixed@zd+zd.T@mixed.T@z+z.T@stiffness@z)
    # Symplectic first-order action provides a direct forward/advanced
    # contraction test without a guessed Pauli tensor or boundary adjoint.
    Q=form['angular']['source_coefficients'][160:]
    H,_=regular_radial_basis(np.array([.75*WALL]),1)
    readout=np.zeros((8,2*count));readout[:,80:320]=H[0,0]*Q.T
    readout_scope='retained angularQ pairing with gauge field at3/4wall'
    if count==400:
        # Actual terminal scalar-current contraction on the boundary.  No
        # arbitrary F2 tensor or sum of field/current units is assigned.
        readout[:]=0.
        readout[:,:count]=form['intrinsic_raw_K'](T)[count:,:count]
        readout_scope='intrinsic scalar wall-current linear contraction at terminal numerical time'
    def adjoint_rhs(t,z):
        z=z.reshape(2*count,8);current=_reduced_at(form,t);M,B,K=(current[k] for k in ('M','B','K'))
        Mi=cho_factor(M[:count,:count]);Bi=B[:count,:count];Ki=K[:count,:count]
        # A^T(zx,zp)=(-B Mi zx+(K-B Mi B^T)^T zp, Mi zx+Mi B^T zp).
        v=cho_solve(Mi,z[:count]+Bi.T@z[count:])
        return np.concatenate((Bi@v-Ki.T@z[count:],-v)).ravel()
    adj=solve_ivp(adjoint_rhs,(T,0),readout.T.ravel(),method='DOP853',rtol=rtol,atol=atol,
        max_step=D/time_steps,dense_output=True)
    if not adj.success:raise ArithmeticError('full constrained advanced adjoint failed')
    az=adj.sol(times).T.reshape(-1,2*count,8);integrand=[]
    for t,z in zip(times,az):
        zero=_corrected_hamiltonian_rhs(form,t,np.zeros(2*count*8)).reshape(2*count,8)
        integrand.append(z.T@zero)
    contraction=simpson(np.array(integrand),x=times,axis=0);output=readout@states[-1]
    wall_pairing=simpson(np.array(wall),x=times,axis=0)
    endpoint=states[-1,:count].T@states[-1,count:]-states[0,:count].T@states[0,count:]
    action_boundary=endpoint-simpson(np.array(bilinear),x=times,axis=0)
    result=dict(times=times,state=states,velocity=velocities,A_tau=np.array(At),
        Gauss_residual=np.array(gauss),gauge_Euler_reaction_integrand=np.array(reactions),
        paired_gauge_Euler_reaction=simpson(np.array(reactions),x=times,axis=0),
        native_Ward_Euler_contact_estimate=simpson(np.array(native_contacts),x=times,axis=0),
        finite_row_native_Ward_contact_maximum_difference=float(np.max(abs(simpson(np.array(reactions)-np.array(native_contacts),x=times,axis=0)))),
        wall_trace_reaction_pairing=wall_pairing,action_temporal_endpoint=endpoint,
        action_boundary_pairing=action_boundary,
        action_boundary_maximum_defect=float(np.max(abs(wall_pairing-action_boundary))),
        action_boundary_relative_defect=float(np.max(abs(wall_pairing-action_boundary))/(1+np.max(abs(wall_pairing)))),
        advanced_adjoint=az,adjoint_output=output,adjoint_source_pairing=contraction,
        adjoint_pairing_maximum_defect=float(np.max(abs(output-contraction))),
        Gauss_residual_maximum=float(np.max(abs(np.array(gauss)))),
        Gauss_residual_maximum_relative=max(gauss_relative),
        numerical_integrator=dict(method='DOP853',rtol=rtol,atol=atol,evaluations=sol.nfev),
        source_scope='CONTROL_ONLY compact walltrace; actual8 angular Q directions; no physical interval/source profile selected',
        retarded_initial_data='zero perturbation field and canonical momentum before source support',
        stationary_background=False,physical_gauge_quotient_closed=False,native_heat_evaluated=False,physical_Pauli_form=None)
    result.update(adjoint_readout_map=readout,adjoint_readout_scope=readout_scope)
    if count==400:
        scalar_reaction=[]
        for t,state,velocity in zip(times,states,velocities):
            g,gd,_=compact_trace_pulse(t,D)
            z=np.vstack((state[:count],g*np.eye(8)));dz=np.vstack((velocity,gd*np.eye(8)))
            M,B,K=(form['intrinsic_'+key](t) for key in ('raw_M','raw_B','raw_K'))
            scalar_reaction.append(-gd*(M@dz+B.T@z)[count:]-g*(B[count:]@dz+K[count:]@z))
        result.update(intrinsic_H_response=states[:,320:400],intrinsic_H_canonical_momenta=states[:,count+320:count+400],
            intrinsic_scalar_wall_current_pairing=simpson(np.array(scalar_reaction),x=times,axis=0),
            intrinsic_scalar_temporal_endpoint=states[-1,320:400].T@states[-1,count+320:count+400],
            prescribed_trace_parent_plus_scalar_response=True,
            free_wall_child_interface_exterior_return_included=False)
    return result


def _write_array_archives(output, response_arrays, operator_arrays):
    """Lossless complete response/operator split with deterministic bytes."""
    output=Path(output)
    if set(response_arrays)&set(operator_arrays):
        raise ValueError('response and operator array names must be disjoint')
    receipts={}
    for filename,arrays in (('application.npz',response_arrays),('operator.npz',operator_arrays)):
        with ZipFile(output/filename,'w',compression=ZIP_DEFLATED,compresslevel=9) as archive:
            for name,value in sorted(arrays.items()):
                stream=BytesIO();np.lib.format.write_array(stream,np.asarray(value),allow_pickle=False)
                member=ZipInfo(name+'.npy',date_time=(1980,1,1,0,0,0))
                member.external_attr=0o600<<16;member.compress_type=ZIP_DEFLATED
                archive.writestr(member,stream.getvalue(),compresslevel=9)
        raw=(output/filename).read_bytes()
        if len(raw)>10*1024**2:
            raise ValueError('complete array archive exceeds the 10MiB publication limit')
        receipts[filename]=dict(bytes=len(raw),sha256=sha256(raw).hexdigest(),arrays=sorted(arrays))
    return receipts


def materialize(output, repository=ROOT):
    """Independent-process replays of the complete corrected finite response."""
    output=Path(output); repository=Path(repository)
    if output.exists(): raise FileExistsError('preserve prior evidence; use a new output directory')
    parent=load_corrected_iterate(repository)[2]
    refs=list(parent['input_hashes'])+[
        DEFAULT_ITERATE+'/result.json', DEFAULT_ITERATE+'/application.npz',
        'src/bhsm/interface/muon_parent_maxwell_corrected_retarded.py',
        'src/bhsm/interface/muon_parent_maxwell_full_retarded.py',
        'src/bhsm/interface/muon_parent_maxwell_full_q_application.py']
    hashes={name:sha256((repository/name).read_bytes()).hexdigest() for name in refs}
    form=coupled_corrected_retarded_form(repository); response=corrected_retarded_application(form)
    response_arrays={name:value for name,value in response.items() if isinstance(value,np.ndarray)}
    arrays={}
    arrays.update({name:form[name] for name in (
        'rho','quadrature','time_nodes','corrected_coefficients','corrected_geometry',
        'full_background_values','density_values','density_geometric_jacobian','density_normal_hessian_columns')})
    arrays.update({name:form[name] for name in ('intrinsic_scalar_matrices','intrinsic_H_values','intrinsic_metric_values',
        'intrinsic_metric_geometric_jacobian','intrinsic_metric_normal_hessian_columns')})
    arrays['represented_background_times']=form['time_nodes']+form['represented_time_shift']
    arrays['source_Gram']=form['angular']['source_gram']
    for i,key in enumerate(('unreduced_action_M','unreduced_action_B','unreduced_action_K')):
        arrays[key]=np.array([matrices[i] for matrices in form['raw_forms']])
    arrays['actual_gauge_gradient_weak_rows']=form['gauge_weak_rows'](form['time_nodes'])
    output.mkdir(parents=True)
    archive_receipts=_write_array_archives(output,response_arrays,arrays)
    receipt={name:value for name,value in response.items() if not isinstance(value,np.ndarray)}
    receipt.update(scope='EVALUATED_FULL5_PARENT_MAXWELL_PLUS_INTRINSIC_H_CONSTRAINED_RETARDED_DTN_APPLICATION_ON_CORRECTED_COMMON_FINITE_ITERATE',
        input_hashes=hashes,application_sha256=archive_receipts['application.npz']['sha256'],
        operator_sha256=archive_receipts['operator.npz']['sha256'],array_archives=archive_receipts,
        corrected_common_iterate=DEFAULT_ITERATE,corrected_coefficient_count=len(form['corrected_coefficients']),
        independent_gauge_coefficients=parent['gauge_unknowns'],
        independent_At_Ar_Ai_retained=True,all_curvature_contacts_retained=True,
        full_angular_space=400,scalar_harmonics='complete n1+n3 real shells',
        angular_reference_linearization_invariant=True,nonlinear_truncation_invariant=False,
        At_Gauss_rows=80,spatial_gauge_interior_unknowns=320,intrinsic_scalar_unknowns=80,actual_gauge_gradient_columns=80,
        gauge_Euler_reaction_norm=float(np.linalg.norm(response['paired_gauge_Euler_reaction'])),
        minimum_interior_mass_eigenvalue=form['minimum_interior_mass_eigenvalue'],
        corrected_projected_residual=parent['final_scaled_residual'],
        corrected_total_assigned_constraint_density_max=parent['updated_constraint_density_max'],
        corrected_total_assigned_constraint_density_rms=parent['updated_constraint_density_rms'],
        corrected_constraint_density_scope=parent['constraint_density_scope'],
        corrected_mean_H=form['corrected_coefficients'][-4:].tolist(),
        Higgs_sector_in_retarded_operator=True,nu_squared_action_member=form['nu_squared_action_member'],
        scalar_Maxwell_relative_normalization=form['scalar_Maxwell_relative_normalization'],
        scalar_trace_chart=form['scalar_trace_chart'],homogeneous_geometry_to_odd_mixed_rows=form['Haar_odd_geometry_mixed_audit'],
        operator_scope='full parent Maxwell plus intrinsic H Hessian on the common finite member; prescribed trace, not a free-wall child/exterior photon inverse; fermion/native loads remain distinct',
        Maxwell_background_energy_added_again=False,
        domain_scope='same finite positive radial formcore; radial order1 and compact walltrace are numerical coordinates, not physical mode/clock selection',
        coefficient_interpolation='one unreduced SAME-action Hessian sampled at corrected coefficient nodes; cubic spline then exact Gauss Schur at every evaluation',
        coefficient_policy='q,qdot,m,normal,normal_rate and independent At/Ar/Ai derive from the same frozen130-vector; no frozen lambda_tau or dropped independent connection',
        computational_gauge_slice='fixed independent-field radial section; actual D_A eta rows retained as reaction tests; no physical quotient closure',
        native_Ward_estimate_scope='independent actual-background coefficient interpolation diagnostic; not exact between nodes and not an enclosure',
        radial_trial_order=1,radial_quadrature_count=48,time_coefficient_nodes=17,
        time_response_steps=128,duration=form['duration'],final_time=form['final_time'],
        represented_background_time_interval=[form['represented_time_shift'],0.],
        retarded_application_time_interval=[0.,form['final_time']],
        retained_geometry_side='outgoing_C2_E1plus_branch24 local finite germ',
        backward_local_coefficient_interval_is_incoming_C1_history=False,
        external_E0_birth_trace_variation_introduced=False,
        physical_history_reconstructed=False,physical_unit_assigned=False,
        error_scope='finite same-action interpolation/quadrature and ODE application; no continuum, complete coupled primal, native heat or physical Pauli enclosure')
    if hashes!={name:sha256((repository/name).read_bytes()).hexdigest() for name in refs}:
        raise RuntimeError('consumed input changed during application; replay with frozen inputs')
    (output/'result.json').write_text(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return receipt


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(materialize(args.output),sort_keys=True))
