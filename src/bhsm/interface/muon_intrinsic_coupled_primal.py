"""Same-vector first-order scalar/geometry primal applications.

This driver distinguishes the numerical coefficient space from a closed
physical boundary-value problem.  It never solves the instantaneous
(q,qdot,m) matrix.  Unbound action parameters and event Cauchy applications
are explicit failures of a physical Newton request, even at an iterate
whose Higgs Euler row happens to vanish.
"""
from __future__ import annotations

import numpy as np

from .muon_intrinsic_scalar_discretization import (
    realify_coefficients, unrealify_coefficients,
    tensor_product_scalar_fields,
)
from .muon_intrinsic_higgs_weak_action import retained_higgs_spin_charge_representation
from .muon_intrinsic_lepton_primal import classical_bosonic_body_source
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet


class UnboundPhysicalApplication(ValueError):
    """An exact reached application, not an assertion of underdetermination."""
    def __init__(self, operand, consumer, producer):
        self.operand, self.consumer, self.producer = operand, consumer, producer
        super().__init__(f'{operand}: consumed by {consumer}; producer {producer}')


def coupled_coefficient_layout(angular, temporal, *, geometric_order=12):
    """One real vector with scalar, momentum, geometry and connection blocks.

    The scalar/connection angular band is a computational representation.
    The lepton body has no odd variables; generator coefficient equations
    are separately implemented in muon_intrinsic_lepton_primal.  The
    response is eliminated by its anchored normalized integral in the
    retained geometric chart, rather than setting its multiplier to zero.
    """
    if set(temporal) != {'parent', 'child'}:
        raise ValueError('parent and child temporal spaces required')
    if type(geometric_order) is not int or geometric_order < 1:
        raise ValueError('positive geometric order required')
    blocks = {}; offset = 0; nq = 1+3*geometric_order; nm = 2*geometric_order
    for side in ('parent', 'child'):
        nt=temporal[side]['coefficient_count']; na=angular['scalar_count']
        for name,shape,complex_block in (
                ('H',(nt,na,2),True), ('p_H',(nt,na,2),True),
                ('q',(nt,nq),False), ('m',(nt,nm),False),
                ('normal_chart',(nt,),False),
                # Four spacetime components in anti-Hermitian u(2).
                ('gauge',(nt,na,4,4),False)):
            count=int(np.prod(shape))*(2 if complex_block else 1)
            blocks[f'{side}.{name}']=dict(start=offset,stop=offset+count,
                shape=shape,complex=complex_block)
            offset+=count
    return dict(blocks=blocks,size=offset,geometric_order=geometric_order,
        source_representation='CLASSICAL_BOSONIC_BODY',
        scalar_state_selected=False,physical_cauchy_data_selected=False,
        anchored_response_role='exact elimination within retained coordinate-normalized chart',
        gauge_role='real u(2) component fields in the complete normalized real scalar harmonic basis')


def block_coefficients(coefficients, layout, name):
    c=np.asarray(coefficients,dtype=float)
    if c.shape != (layout['size'],) or not np.isfinite(c).all():
        raise ValueError('finite one real coupled coefficient vector required')
    b=layout['blocks'][name]; value=c[b['start']:b['stop']]
    return unrealify_coefficients(value,b['shape']) if b['complex'] else value.reshape(b['shape'])


def set_block(coefficients, layout, name, value):
    """Set an iterate block.  This does not prescribe a boundary condition."""
    b=layout['blocks'][name]; a=np.asarray(value)
    if a.shape != b['shape'] or not np.isfinite(a).all():
        raise ValueError('iterate block shape/finite value mismatch')
    coefficients[b['start']:b['stop']]=realify_coefficients(a) if b['complex'] else a.ravel()


def branch_fields_from_coefficients(coefficients,layout,angular,temporal,side,
                                    *, interpolation=False):
    """Construct all scalar derivatives/momenta and qdot from the SAME vector.

    The current production application uses the homogeneous radial chart.
    Angularly moving graph G^{ti} is not silently discarded: it belongs to
    the separate graph application below.  The remaining gauge field is
    an unknown, including its time component; its zero at an iterate is
    not an action-derived absence of a physical fluctuation.
    """
    if side not in ('parent','child'):raise ValueError('owned branch required')
    t=temporal[side]
    if interpolation:
        t=dict(t,basis_values=np.eye(t['coefficient_count']),
               basis_time_derivatives=t['nodal_time_derivative_matrix'],
               quadrature_weights=np.ones(t['coefficient_count']))
    H=tensor_product_scalar_fields(angular,t,block_coefficients(coefficients,layout,f'{side}.H'))
    p=tensor_product_scalar_fields(angular,t,block_coefficients(coefficients,layout,f'{side}.p_H'))
    B,Bt=t['basis_values'],t['basis_time_derivatives']
    q=block_coefficients(coefficients,layout,f'{side}.q')
    m=block_coefficients(coefficients,layout,f'{side}.m')
    a=block_coefficients(coefficients,layout,f'{side}.normal_chart')
    qv=B@q; qdot=Bt@q; mv=B@m; av=B@a; adot=Bt@a
    weights=[intrinsic_m4_weight_jet(layout['geometric_order'],x,v,z,
             source_value=float(s),source_rate=float(sr))
             for x,v,z,s,sr in zip(qv,qdot,mv,av,adot)]
    gc=block_coefficients(coefficients,layout,f'{side}.gauge')
    gauge_values=np.einsum('tl,an,lnmu->tamu',B,angular['real_basis_values'],gc)
    sigma=2*retained_higgs_spin_charge_representation()['higgs_su2_generators']
    u2=np.concatenate((-1j*sigma,-.5j*np.eye(2)[None]),axis=0)
    A=np.einsum('tamu,uij->tamij',gauge_values,u2)
    # The retained mechanical connection has spatial theta components;
    # the independently varied A_t is supplied by the same gauge block.
    for k,w in enumerate(weights):
        kap=w['mechanical_connection_lambda'].value-(side=='parent')
        R=np.broadcast_to(np.eye(3),angular['adjoint_rotations'].shape) if side=='parent' else angular['adjoint_rotations']
        A[k,:,1:]+=kap*np.einsum('pad,dij->paij',R,-1j*sigma)
    h=H['field_values']; pv=p['field_values']
    DH=np.concatenate((H['coordinate_time_derivatives'][:,:,None],H['unit_s3_derivatives']),axis=2)
    DH+=np.einsum('tamij,taj->tami',A,h)
    Dtp=p['coordinate_time_derivatives']+np.einsum('taij,taj->tai',A[:,:,0],pv)
    V=angular['basis_values']; EV=angular['basis_derivative_values']
    # Test columns are complex component directions; realification/2Re is
    # performed at the consumer, once.
    phi=np.einsum('an,ij->ainj',V,np.eye(2)).reshape(len(V),2,-1)
    Dphi=np.einsum('amn,ij->aminj',EV,np.eye(2)).reshape(len(V),3,2,-1)
    covDphi=Dphi[None]+np.einsum('tamij,ajn->tamin',A[:,:,1:],phi)
    return dict(H=h,p_H=pv,DH=DH,Dtp_H=Dtp,q=qv,qdot=qdot,m=mv,
        normal=av,normal_rate=adot,weight_nodes=weights,connection=A,
        phi=phi,Dphi_spatial=covDphi,
        J_H=classical_bosonic_body_source(h.shape[0]*h.shape[1])['J_H_body'].reshape(h.shape),
        source_provenance=classical_bosonic_body_source(1),
        all_values_and_derivatives_from_same_vector=True,
        gauge_zero_is_only_an_iterate=True,stationary_base=False,
        angular_representation='scalar Peter-Weyl tensor weak C2',
        child_connection='pointwise Ad_g in the same right coframe')


def scalar_first_order_rows(fields,angular,*,lambda_H,nu_squared):
    """Galerkin canonical definition and first-order momentum Euler rows.

    These are complex equations; their real weak cotangent is 2Re.  p_H
    itself never receives that extra factor.  At each temporal sample the
    entire angular basis is projected, not one chosen test contraction.
    """
    if lambda_H is None:
        raise UnboundPhysicalApplication('lambda_H',
            'scalar momentum Jacobian and -lambda_H*nu^4*wV geometric action',
            'aether_unified_m5_m4_pushforward_v15_69.common_derivative_ledger.Higgs_mass_and_quartic')
    lam=float(lambda_H); nu=float(nu_squared)
    if not np.isfinite([lam,nu]).all() or lam<=0 or nu<0:
        raise ValueError('positive lambda_H and nonnegative nu_squared in action units required')
    w=angular['unit_s3_weights']; phi=fields['phi']; h=fields['H']; DH=fields['DH']
    nt=len(h); kin=[]; mom=[]
    for k in range(nt):
        wt,ws,wv=(fields['weight_nodes'][k][name].value for name in ('wT','wS','wV'))
        force=2*lam*(np.sum(abs(h[k])**2,axis=1)-nu)[:,None]*h[k]+fields['J_H'][k]
        kin.append(np.einsum('ain,ai,a->n',phi.conj(),wt*DH[k,:,0]-fields['p_H'][k],w))
        mom.append(np.einsum('ain,ai,a->n',phi.conj(),fields['Dtp_H'][k]+wv*force,w)
                   +ws*np.einsum('amin,ami,a->n',fields['Dphi_spatial'][k].conj(),DH[k,:,1:],w))
    return dict(kinematic=np.array(kin),momentum=np.array(mom),
        canonical_momentum_rule='p_H=wT D_tH, complex momentum without an extra two',
        pairing='2 Re only on the final real cotangent',
        physical_stationarity_claim=False)


def graph_canonical_time_application(*,G,H,p_H,spatial_covariant_derivatives):
    """Pointwise graph Legendre application; no diagonal approximation."""
    g=np.asarray(G,dtype=float); h=np.asarray(H,complex);p=np.asarray(p_H,complex)
    d=np.asarray(spatial_covariant_derivatives,complex)
    if h.ndim!=2 or h.shape[1]!=2 or p.shape!=h.shape or d.shape!=(len(h),3,2) or g.shape!=(len(h),4,4):
        raise ValueError('common graph density, doublet, momentum and spatial derivatives required')
    if not all(np.isfinite(x).all() for x in (g,h,p,d)) or np.any(g[:,0,0]<=0):
        raise ValueError('finite future nondegenerate graph density required')
    dt=(p-np.einsum('pa,pai->pi',g[:,0,1:],d))/g[:,0,0,None]
    flux=np.einsum('pa,pi->pai',g[:,1:,0],dt)+np.einsum('pab,pbi->pai',g[:,1:,1:],d)
    return dict(DtH=dt,spatial_density_flux=flux,
                momentum_reconstruction=g[:,0,0,None]*dt+np.einsum('pa,pai->pi',g[:,0,1:],d),
                physical_base_claim=False)


def temporal_momentum_contraction(fields,angular,temporal,tests):
    """Reached 2Re integral (D_t phi)^dagger p, from coefficient tests."""
    t=tensor_product_scalar_fields(angular,temporal,tests)
    Dt=t['coordinate_time_derivatives']+np.einsum('taij,taj->tai',fields['connection'][:,:,0],t['field_values'])
    return float(2*np.real(np.sum(t['spacetime_quadrature_weights'][:,:,None]*Dt.conj()*fields['p_H'])))


def causal_collocation_rows(rows):
    """Interior equations only; the past Cauchy row stays a boundary unknown.

    Collocating an Nt-1 degree polynomial at all Nt points can spuriously
    select the zero homogeneous solution.  Keeping Nt-1 future rows leaves
    exactly the endpoint variables which the physical event must close.
    """
    if len(rows['kinematic'])<2:raise ValueError('at least two future time nodes required')
    return np.concatenate((rows['kinematic'][1:].ravel(),rows['momentum'][1:].ravel()))


def require_physical_solve_binding(binding):
    """Fail on the first reached numeric coefficient, then boundary operators.

    A parameter-family operator can be assembled without these numeric
    values.  This guard concerns a numerical PHYSICAL stationary solve.
    lambda is an action coefficient, never a new Euler unknown to minimize.
    """
    required=(
        ('lambda_H','coupled geometric lapse/potential row and scalar mass/cubic Jacobian',
         'same normalized boundary functional fourth variation, v15.69.common_derivative_ledger'),
        ('nu_squared_action_units','retained Higgs potential in the geometric action units',
         'ae31_c2_intrinsic_m4_lepton_action.conditional_higgs_saddle plus owned unit conversion'),
        ('surface_gamma','surface lapse and full common formation action',
         'covariant_bubble_interface_mechanics.surface_tension_contract'),
        ('incoming_scalar_event_load','past scalar Cauchy cotangent/parent-event Euler rows',
         'current event/environment B_s and parent E0 field solve'),
        ('worldvolume_bundle_conditions','scalar T and paired dual at E1',
         'current mechanics solved worldvolume/bundle correspondence'),
        ('complete_gauge_response_boundary_application','same-action full Euler/constraint assembly',
         'retained gauge Hessian, anchored response adjoint and event boundary actions'),
    )
    for key,consumer,producer in required:
        if binding.get(key) is None:raise UnboundPhysicalApplication(key,consumer,producer)
    return binding


def residual_driven_newton(coefficients,application,*,binding,tolerance,max_steps=12):
    """Execute Newton ONLY for an action-bound, closed represented application.

    Application returns the actual residual and common-vector Jacobian,
    including boundary/constraint rows.  This is not an instantaneous
    geometry inversion; the caller supplies the assembled temporal problem.
    """
    require_physical_solve_binding(binding)
    c=np.asarray(coefficients,dtype=float).copy(); history=[]
    if not np.isfinite(c).all() or tolerance<=0:raise ValueError('finite iterate/positive tolerance required')
    for _ in range(max_steps):
        a=application(c);r=np.asarray(a['residual'],float);J=np.asarray(a['jacobian'],float)
        if r.shape!=c.shape or J.shape!=(len(c),len(c)) or not np.isfinite(r).all() or not np.isfinite(J).all():
            raise ValueError('closed common-vector residual/Jacobian required')
        before=float(np.linalg.norm(r));entry=dict(initial_residual=before)
        if before<=tolerance:
            entry.update(correction_norm=0.,updated_residual=before);history.append(entry)
            return dict(coefficients=c,history=history,converged=True,application=a)
        delta=np.linalg.solve(J,-r);step=1.
        for _ in range(20):
            updated=application(c+step*delta)
            after=float(np.linalg.norm(updated['residual']))
            if after<before:break
            step*=.5
        else:raise RuntimeError('closed action Newton correction did not reduce residual')
        c+=step*delta;entry.update(correction_norm=float(np.linalg.norm(step*delta)),
                                 step=step,updated_residual=after);history.append(entry)
    return dict(coefficients=c,history=history,converged=False,application=application(c))


def geometry_euler_from_local_jet(action,velocity,acceleration,multiplier_rate,
                                   *,normal_rate=0.,normal_acceleration=0.):
    """Actual temporal Euler row L_q-D_t L_qdot at a coefficient iterate.

    D_t is the chain rule on the common signed action, including m and
    normal motion.  It is not minimization over independent qdot slots.
    """
    nq=(len(action.gradient)-2-len(multiplier_rate))//2
    v=np.asarray(velocity,float);acc=np.asarray(acceleration,float);md=np.asarray(multiplier_rate,float)
    if v.shape!=(nq,) or acc.shape!=(nq,):raise ValueError('same q and derivative dimensions required')
    tangent=np.concatenate((v,acc,md,[normal_rate,normal_acceleration]))
    if tangent.shape!=action.gradient.shape:raise ValueError('common local action/time tangent required')
    return dict(F_q=action.gradient[:nq]-action.hessian[nq:2*nq]@tangent,
        F_m=action.gradient[2*nq:-2],
        F_normal=action.gradient[-2]-action.hessian[-1]@tangent,
        canonical_geometry_momentum=action.gradient[nq:2*nq],
        time_tangent=tangent,stationary_base_claim=False)
