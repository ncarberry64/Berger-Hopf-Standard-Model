"""Full cubic pullback for the action-bound Higgs-selected EM source.

The source changes with geometry and with the scalar charge direction.
Its explicit first jet is consumed before any mean-response elimination.
The fixed action third variation and the two source-motion contacts are
kept separately.  No mean inverse or external Pauli vertex is inferred.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicSpline

from .muon_current_source_motion_cubic import (
    _real, current_face_source_jets, maxwell_cross_hessian,
    higgs_cross_hessian,
)
from .muon_current_source_motion_mean_load import current_source_complete_mean_load
from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from .muon_parent_maxwell_full_weak import M
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP, VOLUME


def source_jet_motion_contact(raw_fields, representation, angular, source_jet,
        profile, profile_rate, *, first_gauge, first_gauge_rate,
        first_gauge_radial, first_wall_gauge, first_H, first_H_rate,
        nu_squared_action):
    """Apply both D2S contacts of an explicit raw268 Q/Qdot first jet.

    Q and Qdot are the unpulsed, normalized full400 source maps.
    The derivatives use the future coordinate clock on both arms.
    Thus D_z u=p*lift*D_z Q and
    D_z u_t=lift*(p_t*D_z Q+p*D_z Qdot).  H-selected charge motion,
    its time derivative, and the geometric Tb derivative occur once.
    """
    rep=representation;N=len(rep['gauge_labels']);size=108+2*N;hs=100+2*N
    raw=_real(raw_fields,'common raw fields',(size,))
    if N!=80:
        raise ValueError('actual enriched raw268 representation required')
    p,pt=_real([profile,profile_rate],'explicit pulse value/rate',(2,))
    Q=_real(source_jet.get('Q'),'same-chart source',(400,8))
    _real(source_jet.get('Qdot'),'same-chart future source rate',Q.shape)
    dQ=_real(source_jet.get('Q_first_jet'),'raw268 source first jet',(size,400,8))
    dQt=_real(source_jet.get('Qdot_first_jet'),'raw268 source-rate first jet',dQ.shape)
    if np.any(Q[:160]) or np.any(dQ[:,:160]) or np.any(dQt[:,:160]):
        raise ValueError('this inherited source application requires spatial gauge traces')
    R=len(rep['rho']);u=_real(first_gauge,'total first gauge',(R,8,5,4,20))
    ut=_real(first_gauge_rate,'total first gauge rate',u.shape)
    ur=_real(first_gauge_radial,'total first gauge radial derivative',u.shape)
    aw=_real(first_wall_gauge,'total first wall gauge',(8,5,4,20))
    h=_real(first_H,'total first scalar',(8,4,20))
    ht=_real(first_H_rate,'total first scalar rate',h.shape)
    E=_real(angular['derivative_matrices'],'inherited angular derivative',(3,20,20))
    maxwell=np.zeros((size,8,8));scalar=np.zeros_like(maxwell)
    # Outside pulse support both explicit source-motion contacts vanish.
    # This is an evaluated support property, not a zero first response.
    if p==0 and pt==0:
        return dict(Maxwell_source_motion_cotangent=maxwell,
                    scalar_source_motion_cotangent=scalar,
                    source_motion_cotangent=maxwell+scalar,
                    source_motion_zero_reason='both pulse value and future-coordinate rate are exactly zero')
    lift=_real(rep['radial_value_map'],'actual radial lift')[:,-1]
    lift_r=_real(rep['radial_derivative_map'],'actual radial derivative')[:,-1]
    A=np.einsum('rj...,j->r...',rep['gauge_basis'],raw[100:100+N])[:,0]
    At=np.einsum('rj...,j->r...',rep['gauge_basis'],raw[100+N:hs])[:,0]
    Ar=np.einsum('rj...,j->r...',rep['gauge_radial_basis'],raw[100:100+N])[:,0]
    geo=geometric_connection_coefficient_jets(12,raw[:37],raw[37:74],raw[74:98],
        rep['rho'],source_value=raw[98],source_rate=raw[99])
    for j,row in enumerate(geo['rows']):
        A[j,2:]+=M*(row['connection_lambda'].value-1)
        At[j,2:]+=M*row['lambda_tau'].value
        Ar[j,2:]+=M*row['lambda_rho'].value
    weights=current_face_source_jets(raw[:100])['intrinsic_weights']
    wall=np.einsum('fcj,j->fc',rep['wall_trace_map'],raw[100:100+N])
    wall[2:]+=M*(weights['mechanical_connection_lambda'].value-1)
    w=np.array([weights[k].value for k in ('wT','wS','wV')])
    active=np.flatnonzero(np.any(dQ,axis=(1,2))|np.any(dQt,axis=(1,2)))
    # Batch independent cotangent directions; neither source ordering is
    # identified with a Hermitian conjugate or divided by two.
    for start in range(0,len(active),16):
        indices=active[start:start+16];count=len(indices)
        q=dQ[indices].transpose(0,2,1).reshape(count*8,5,4,20)
        qt=dQt[indices].transpose(0,2,1).reshape(q.shape)
        for j,row in enumerate(geo['rows']):
            dens=np.array([row[k].value for k in ('electric','radial','angular','electric_radial','shift')])
            C=maxwell_cross_hessian(A[j],At[j],Ar[j],u[j],ut[j],ur[j],
                p*lift[j]*q, lift[j]*(pt*q+p*qt), p*lift_r[j]*q,E,dens)
            C=C.reshape(8,count,8).transpose(1,0,2)
            maxwell[indices]+=rep['radial_quadrature'][j]*(C+C.swapaxes(-1,-2))
        zero=np.zeros((count*8,4,20))
        C=higgs_cross_hessian(raw[hs:hs+4],raw[hs+4:],wall,h,ht,aw,
            zero,zero,p*q,E,w,lambda_H=rep['scalar_matching']['lambda_H'],
            nu_squared_action=nu_squared_action)
        C=C.reshape(8,count,8).transpose(1,0,2)
        scalar[indices]=C+C.swapaxes(-1,-2)
    maxwell*=MAXWELL_TO_CAP;scalar/=VOLUME**2
    return dict(Maxwell_source_motion_cotangent=maxwell,
                scalar_source_motion_cotangent=scalar,
                source_motion_cotangent=maxwell+scalar,
                source_motion_zero_reason=None)


def electromagnetic_source_complete_mean_load(raw_fields, representation,
        angular, source_jet, profile, profile_rate, *, first_gauge,
        first_gauge_rate, first_gauge_radial, first_wall_gauge,
        first_H, first_H_rate, nu_squared_action):
    """Literal full action cubic plus the actual EM source first-jet pullback."""
    raw=_real(raw_fields,'common raw fields',(268,))
    Q=_real(source_jet.get('Q'),'same-chart source',(400,8))
    Tb=current_face_source_jets(raw[:100])['T_b'].value
    arguments=dict(first_gauge=first_gauge,first_gauge_rate=first_gauge_rate,
        first_gauge_radial=first_gauge_radial,first_wall_gauge=first_wall_gauge,
        first_H=first_H,first_H_rate=first_H_rate,nu_squared_action=nu_squared_action)
    # Suppressing explicit motion here isolates D3S at the actual TOTAL
    # first fields.  It does not suppress any solved Higgs/Gauss response.
    fixed=current_source_complete_mean_load(raw,representation,angular,Q/Tb,0.,0.,**arguments)
    motion=source_jet_motion_contact(raw,representation,angular,source_jet,
        profile,profile_rate,**arguments)
    result=dict(fixed)
    result.update(motion)
    result['fixed_field_raw_mean_cotangent']=fixed['raw_mean_cotangent']
    result['raw_mean_cotangent']=fixed['raw_mean_cotangent']+motion['source_motion_cotangent']
    result.update(source_motion_count=1,
        source_motion_geometry_only_reason=None,
        source_motion_scope='actual normalized Q(H,geometry) and its future-coordinate Qdot first jets; all raw268 rows',
        action_chain_rule='D_z S_AB=D3S[z,u_A,u_B]+D2S[D_z u_A,u_B]+D2S[u_A,D_z u_B]',
        selected_EM_source_not_replaced_by_old_Q8=True,
        physical_external_Pauli_vertex_evaluated=False)
    return result


def load_electromagnetic_reached_mean_inputs(directory, *, repository):
    """Bind the fresh H-selected EM solve and its complete source first jets."""
    from .muon_primal_electromagnetic_source import (
        higgs_aligned_source_first_jets, retained_phase_source_inputs,
    )
    from .muon_parent_maxwell_full_q_application import retained_full_q_angular_space
    root=Path(repository);folder=Path(directory)
    if not folder.is_absolute():folder=root/folder
    data=(folder/'result.json').read_bytes();receipt=json.loads(data)
    if receipt['classification']!='EVALUATED_HIGGS_ALIGNED_ELECTROMAGNETIC_FULL488_SAME_ACTION_RESPONSE':
        raise ValueError('fresh actual H-selected EM response required')
    if receipt['side'] not in ('incoming','outgoing') or receipt['source_motion_count']!=1 or receipt['old_transported_Q8_inverse_substituted']:
        raise ValueError('oriented fresh EM source with exactly one source-motion application required')
    if not receipt['source_first_jets_are_analytic'] or not receipt['b_source_coefficients_time_dependent']:
        raise ValueError('analytic full H-selected source and rate jets required')
    hashes=dict(receipt['input_hashes'])
    for name,digest in hashes.items():
        if sha256((root/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('consumed owner changed: '+name)
    hashes[folder.relative_to(root).as_posix()+'/result.json']=sha256(data).hexdigest()
    loaded={}
    for name in ('primal_and_source.npz','source_first_jets.npz','phase.npz','velocity.npz','contacts.npz'):
        data=(folder/name).read_bytes();record=receipt['array_archives'][name]
        if len(data)!=record['bytes'] or sha256(data).hexdigest()!=record['sha256']:
            raise ValueError('fresh EM response archive changed: '+name)
        hashes[folder.relative_to(root).as_posix()+'/'+name]=record['sha256']
        with np.load(folder/name,allow_pickle=False) as a:
            loaded[name]={key:a[key].copy() for key in a.files}
    source,jet,phase,velocity,contacts=(loaded[name] for name in
        ('primal_and_source.npz','source_first_jets.npz','phase.npz','velocity.npz','contacts.npz'))
    times=_real(phase['times'],'fresh response times');nt=len(times)
    if times.ndim!=1 or times[0]!=0 or np.any(np.diff(times)<=0):
        raise ValueError('increasing chronological response grid required')
    if not np.array_equal(times,velocity['times']) or not np.array_equal(times,contacts['times']):
        raise ValueError('response time grids differ')
    _real(phase['state'],'complete first phase',(nt,800,8))
    _real(velocity['velocity'],'complete first velocity',(nt,400,8))
    _real(contacts['A_tau'],'complete solved Gauss field',(nt,80,8))
    if not np.array_equal(contacts['intrinsic_H_response'],phase['state'][:,320:400]):
        raise ValueError('intrinsic scalar response is not the same phase')
    nodes=_real(source['times'],'actual source nodes');ns=len(nodes)
    raw=_real(source['raw_fields'],'actual common fields',(ns,268))
    _real(source['b_source_coefficients'],'actual time-dependent charge source',(ns,400,8))
    _real(source['Q'],'actual normalized EM source',(ns,400,8))
    _real(source['Qdot'],'actual normalized EM source rate',(ns,400,8))
    _real(jet['Q_first_jet'],'actual raw268 source first jets',(ns,268,400,8))
    _real(jet['Qdot_first_jet'],'actual raw268 source-rate jets',(ns,268,400,8))
    if not np.array_equal(nodes,jet['times']):
        raise ValueError('source and first-jet grids differ')
    expected_clock=nodes-times[-1] if receipt['side']=='incoming' else nodes
    if not np.array_equal(source['coordinate_times'],expected_clock):
        raise ValueError('future coordinate source clock differs from attached arm')
    angular=retained_full_q_angular_space(root)
    for j in range(ns):
        actual=higgs_aligned_source_first_jets(raw[j],angular)
        for saved,computed in (('Q','connection_source'),('Qdot','connection_source_rate'),
                               ('b_source_coefficients','source')):
            if not np.array_equal(source[saved][j],actual[computed]):
                raise ValueError('H-selected source changed: '+saved)
        for key in ('Q_first_jet','Qdot_first_jet'):
            if not np.array_equal(jet[key][j],actual[key]):
                raise ValueError('H-selected source first jet changed: '+key)
    candidates=[name for name in hashes if name.endswith('/result.json')
        and 'attached_phase_'+receipt['side']+'_' in name]
    if len(candidates)!=1:
        raise ValueError('unique consumed actual attached phase required')
    phase_path=root/candidates[0]
    bound=retained_phase_source_inputs(phase_path.parent,repository=root)
    if bound['receipt']['span']!=receipt['actual_phase_span']:
        raise ValueError('EM response and attached phase spans differ')
    rep=bound['representation']
    for key in ('gauge_basis','gauge_radial_basis','wall_trace_map'):
        if not np.array_equal(source[key],rep[key]):
            raise ValueError('saved actual background frame changed: '+key)
    if not np.array_equal(source['source_phase_jacobian'],bound['cell']['jacobian']):
        raise ValueError('EM response and chronological native adjoint use different phase Jacobians')
    return dict(receipt=receipt,representation=rep,source=source,source_first_jets=jet,
        phase=phase,velocity=velocity,contacts=contacts,input_hashes=hashes,
        directory=folder,times=times,Gauss_time_interpolant=CubicSpline(times,contacts['A_tau']),
        actual_attached_phase_path=phase_path.parent,consumed_full_attachment=True,
        actual_H_selected_EM_source=True,physical_history_selected=False)


def electromagnetic_source_jet_at_node(inputs, response_time):
    """Return the exact retained analytic source jet at a consumed node."""
    source=inputs['source'];jet=inputs['source_first_jets']
    hits=np.flatnonzero(source['times']==float(response_time))
    if len(hits)!=1:
        raise ValueError('exact retained H-selected source node required')
    j=int(hits[0])
    return dict(Q=source['Q'][j],Qdot=source['Qdot'][j],
        Q_first_jet=jet['Q_first_jet'][j],Qdot_first_jet=jet['Qdot_first_jet'][j])
