"""Complete represented mean rows for the current moving-source contraction.

The source chart contributes to geometry rows; all gauge, Gauss, scalar
and canonical rows are also retained before any causal elimination.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicSpline
from .muon_current_source_motion_cubic import current_source_cubic_application,_real,current_face_source_jets
from .muon_parent_maxwell_source_mean_forcing import maxwell_mean_cotangents,higgs_mean_cotangents
from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from .muon_parent_maxwell_full_weak import M,FIELD_ORDER
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP,VOLUME
from .muon_parent_retarded_hypercharge import regular_radial_basis,WALL,compact_trace_pulse


def current_source_complete_mean_load(raw_fields,representation,angular,b_coefficients,
        profile,profile_rate,*,first_gauge,first_gauge_rate,first_gauge_radial,
        first_wall_gauge,first_H,first_H_rate,nu_squared_action):
    """Return D³S plus source-chart motion on every represented raw row.

    This is the actual load supplied to a joint mixed-response problem,
    not an inversion or a restriction to scalar/geometry rows.  The raw
    coordinate order and computational radial frame are those of the
    supplied actual background and total first-response arrays.
    """
    rep=representation;N=len(rep['gauge_labels']);nr=108+2*N;hs=100+2*N
    raw=_real(raw_fields,'common raw fields',(nr,))
    args=dict(first_gauge=first_gauge,first_gauge_rate=first_gauge_rate,first_gauge_radial=first_gauge_radial,
        first_wall_gauge=first_wall_gauge,first_H=first_H,first_H_rate=first_H_rate,nu_squared_action=nu_squared_action)
    geometry=current_source_cubic_application(raw,rep,angular,b_coefficients,profile,profile_rate,**args)
    u,ut,ur=(_real(x,'total first connection') for x in (first_gauge,first_gauge_rate,first_gauge_radial))
    count=u.shape[1];load=np.zeros((nr,count,count));load[:100]=geometry['complete_geometry_cubic_at_fixed_interior_first_coefficients']
    gb,gr=rep['gauge_basis'],rep['gauge_radial_basis']
    A=np.einsum('rj...,j->r...',gb,raw[100:100+N])[:,0]
    At=np.einsum('rj...,j->r...',gb,raw[100+N:hs])[:,0]
    Ar=np.einsum('rj...,j->r...',gr,raw[100:100+N])[:,0]
    E=angular['derivative_matrices']
    geo=geometric_connection_coefficient_jets(12,raw[:37],raw[37:74],raw[74:98],rep['rho'],source_value=raw[98],source_rate=raw[99])
    value=np.zeros((N,count,count));rate=value.copy()
    for j,row in enumerate(geo['rows']):
        A[j,2:]+=M*(row['connection_lambda'].value-1);At[j,2:]+=M*row['lambda_tau'].value;Ar[j,2:]+=M*row['lambda_rho'].value
        d=np.array([row[k].value for k in ('electric','radial','angular','electric_radial','shift')])
        result=maxwell_mean_cotangents(A[j],At[j],Ar[j],u[j],ut[j],ur[j],E,d)
        test=gb[j,:,0];radial=gr[j,:,0];quad=rep['radial_quadrature'][j]
        value+=quad*(np.einsum('jfc,fcab->jab',test,result['value'].reshape(5,4,count,count))+np.einsum('jfc,fcab->jab',radial,result['radial'].reshape(5,4,count,count)))
        rate+=quad*np.einsum('jfc,fcab->jab',test,result['time'].reshape(5,4,count,count))
    w=current_face_source_jets(raw[:100])['intrinsic_weights']
    if 'wall_trace_map' in rep:wallmap=rep['wall_trace_map']
    else:
        wb,_=regular_radial_basis(np.array([WALL]),rep['radial_order']);wallmap=np.zeros((5,4,N))
        for j,label in enumerate(rep['gauge_labels']):wallmap[FIELD_ORDER.index(label['field']),label['internal'],j]=wb[0,label['radial']]
    wall=np.einsum('fcj,j->fc',wallmap,raw[100:100+N]);wall[2:]+=M*(w['mechanical_connection_lambda'].value-1)
    scalar=higgs_mean_cotangents(raw[hs:hs+4],raw[hs+4:],wall,first_H,first_H_rate,first_wall_gauge,E,
        np.array([w[k].value for k in ('wT','wS','wV')]),lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=nu_squared_action)
    scalar_gauge=np.einsum('fcj,fcab->jab',wallmap,scalar['gauge_value'].reshape(5,4,count,count))/VOLUME**2
    load[100:100+N]=MAXWELL_TO_CAP*value+scalar_gauge
    load[100+N:hs]=MAXWELL_TO_CAP*rate
    load[hs:hs+4]=scalar['scalar_value']/VOLUME**2;load[hs+4:]=scalar['scalar_time']/VOLUME**2
    return dict(raw_mean_cotangent=load,geometry_application=geometry,
        Maxwell_gauge_value_cotangent=MAXWELL_TO_CAP*value,
        Maxwell_gauge_rate_cotangent=MAXWELL_TO_CAP*rate,
        scalar_gauge_value_cotangent=scalar_gauge,
        scalar_value_cotangent=load[hs:hs+4],scalar_rate_cotangent=load[hs+4:],
        all_represented_mean_rows_retained=True,At_Gauss_rows_removed=False,
        raw_coordinate_order='geometry100, independent gaugeN, gauge_rateN, Hreal4, Hrate4',
        source_motion_geometry_only_reason='owned Tb chart depends on geometry100 only; source coefficient basis and radial frame held fixed',
        paired_derivative_divided_by_two=False,mean_second_response_solved=False,
        continuum_angular_gravity_first_rows_filled_zero=False,complete_native_or_Pauli=False)


def prescribed_source_complete_mean_load(raw_fields,representation,angular,b_coefficients,
        profile,profile_rate,*,nu_squared_action):
    """Explicit fixed-H/interior source restriction; no solved response substitution."""
    raw=_real(raw_fields,'common raw fields');b=_real(b_coefficients,'source400')
    if b.ndim!=2 or b.shape[0]!=400:raise ValueError('complete inherited source400 columns required')
    rep=representation;chart=current_face_source_jets(raw[:100]);T,Td=chart['T_b'].value,chart['T_b_dot'].value
    if 'radial_value_map' in rep:lift=rep['radial_value_map'][:,-1];lr=rep['radial_derivative_map'][:,-1]
    else:
        bv,br=regular_radial_basis(rep['rho'],rep['radial_order']);lift,lr=bv[:,-1],br[:,-1]
    B=b.T.reshape(b.shape[1],5,4,20);zeros=np.zeros((b.shape[1],4,20))
    return current_source_complete_mean_load(raw,rep,angular,b,profile,profile_rate,
        first_gauge=lift[:,None,None,None,None]*T*profile*B[None],
        first_gauge_rate=lift[:,None,None,None,None]*(Td*profile+T*profile_rate)*B[None],
        first_gauge_radial=lr[:,None,None,None,None]*T*profile*B[None],
        first_wall_gauge=T*profile*B,first_H=zeros,first_H_rate=zeros,
        nu_squared_action=nu_squared_action)


def load_enriched_reached_mean_inputs(directory, *, repository):
    """Verify and bind the freshly solved enriched-phase response archives.

    Only the explicit numerical one-cell response is consumed.  Its fields
    are unknowns solved by the retained source problem, not replaced by a
    source-only or historical zero-background restriction.
    """
    root=Path(repository);folder=Path(directory)
    if not folder.is_absolute():folder=root/folder
    data=(folder/'result.json').read_bytes();receipt=json.loads(data)
    if receipt['classification']!='EVALUATED_FRESH_COUPLED_REACHED_RESPONSE_ON_ACTUAL_ENRICHED_PHASE':
        raise ValueError('actual fresh enriched response required')
    if receipt['old_source_or_H_response_substituted'] or receipt['source_motion_count']!=1:
        raise ValueError('fresh response with exactly one source-motion application required')
    hashes=dict(receipt['input_hashes'])
    for name,digest in hashes.items():
        if sha256((root/name).read_bytes()).hexdigest()!=digest:raise ValueError('consumed owner changed: '+name)
    hashes[folder.relative_to(root).as_posix()+'/result.json']=sha256(data).hexdigest()
    loaded={}
    for name in ('primal_and_source.npz','phase.npz','velocity.npz','contacts.npz'):
        data=(folder/name).read_bytes();info=receipt['array_archives'][name]
        if len(data)!=info['bytes'] or sha256(data).hexdigest()!=info['sha256']:raise ValueError('response archive changed: '+name)
        hashes[folder.relative_to(root).as_posix()+'/'+name]=info['sha256']
        with np.load(folder/name,allow_pickle=False) as a:loaded[name]={key:a[key].copy() for key in a.files}
    s,phase,velocity,contacts=(loaded[name] for name in ('primal_and_source.npz','phase.npz','velocity.npz','contacts.npz'))
    times=_real(phase['times'],'fresh response times');nt=len(times)
    if times.ndim!=1 or times[0]!=0 or np.any(np.diff(times)<=0):raise ValueError('increasing future-coordinate response time grid required')
    if not np.array_equal(times,velocity['times']) or not np.array_equal(times,contacts['times']):raise ValueError('response time grids differ')
    _real(phase['state'],'complete first phase',(nt,800,8));_real(velocity['velocity'],'complete first velocity',(nt,400,8))
    _real(contacts['A_tau'],'complete solved Gauss field',(nt,80,8))
    if not np.array_equal(contacts['intrinsic_H_response'],phase['state'][:,320:400]):raise ValueError('intrinsic scalar response is not the same phase')
    b=_real(s['b_source_coefficients'],'inherited full source',(400,8))
    if np.any(b[:160]):raise ValueError('inherited spatial source required')
    for index,t in enumerate(s['times']):
        chart=current_face_source_jets(s['raw_fields'][index,:100])
        if not np.array_equal(s['Q'][index],chart['T_b'].value*b) or not np.array_equal(s['Qdot'][index],chart['T_b_dot'].value*b):
            raise ValueError('source and source-rate do not use the same actual phase chart')
    from .muon_birth_trace_enriched_phase import load_enriched_endpoint
    candidates=[name for name in hashes if name.endswith('/result.json') and 'enriched_phase_'+receipt['side']+'_' in name]
    if len(candidates)!=1:raise ValueError('unique consumed enriched primal phase required')
    phase_receipt=json.loads((root/candidates[0]).read_bytes())
    rep=load_enriched_endpoint(phase_receipt['consumed_paired_endpoint_path'],side=receipt['side'],repository=root)['representation']
    for name in ('gauge_basis','gauge_radial_basis','wall_trace_map'):
        if not np.array_equal(s[name],rep[name]):raise ValueError('saved enriched background frame differs: '+name)
    return dict(receipt=receipt,representation=rep,source=s,phase=phase,velocity=velocity,contacts=contacts,
        input_hashes=hashes,directory=folder,times=times,
        Gauss_time_interpolant=CubicSpline(times,contacts['A_tau']))


def enriched_reached_first_fields(inputs, response_time):
    """Apply the saved complete first fields at an exact retained time node.

    The Gauss field has no independent temporal derivative in this action.
    Its saved interpolant derivative is exported in that unused coordinate;
    no unknown required rate is assigned zero.  All other rates are the
    actual solved canonical velocity.  Incoming past integration never
    reverses the future-coordinate field derivatives.  The incoming
    source clock is coordinate_time=u-L, so dcoordinate_time/du=+1.
    """
    t=float(response_time);times=inputs['times']
    if not np.isfinite(t):raise ValueError('finite retained response time required')
    indices=np.flatnonzero(times==t)
    if len(indices)!=1:raise ValueError('exact retained response node required; no field interpolation')
    index=int(indices[0]);s=inputs['source'];nodes=s['times'];hits=np.flatnonzero(nodes==t)
    if len(hits)!=1:raise ValueError('exact retained primal/source node required')
    j=int(hits[0]);raw=s['raw_fields'][j];rep=inputs['representation']
    state=inputs['phase']['state'][index];velocity=inputs['velocity']['velocity'][index]
    interior=np.r_[inputs['contacts']['A_tau'][index],state[:320]].T.reshape(8,5,4,20)
    interior_rate=np.r_[inputs['Gauss_time_interpolant'](t,1),velocity[:320]].T.reshape(8,5,4,20)
    wall=inputs['contacts']['source_trace'][index].T.reshape(8,5,4,20)
    wall_rate=inputs['contacts']['source_trace_rate'][index].T.reshape(8,5,4,20)
    basis,derivative=regular_radial_basis(rep['rho'],1)
    u=basis[:,0,None,None,None,None]*interior+basis[:,1,None,None,None,None]*wall
    ut=basis[:,0,None,None,None,None]*interior_rate+basis[:,1,None,None,None,None]*wall_rate
    ur=derivative[:,0,None,None,None,None]*interior+derivative[:,1,None,None,None,None]*wall
    h=state[320:400].T.reshape(8,4,20);ht=velocity[320:400].T.reshape(8,4,20)
    p,pt,_=compact_trace_pulse(t,inputs['receipt']['source_pulse_duration'])
    return dict(raw_fields=raw,response_time=t,coordinate_time=float(s['coordinate_times'][j]),
        profile=float(p),profile_rate=float(pt),first_gauge=u,first_gauge_rate=ut,
        first_gauge_radial=ur,first_wall_gauge=wall,first_H=h,first_H_rate=ht,
        At_time_derivative_scope='derivative of saved Gauss interpolant; unused by literal Maxwell/Higgs action',
        source_coordinate_clock='incoming coordinate_time=u-L; outgoing coordinate_time=u; both future-oriented with derivative+1',
        all_solved_first_fields_used=True,physical_history_selected=False)
