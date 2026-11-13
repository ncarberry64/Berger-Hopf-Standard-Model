"""Bind the reached local magnetic first jet without changing frozen EM files.

The measured canonical e and R4-squared source normalization are already
included by the source owner.  The three active columns are magnetic
axes; the five padding columns are exact representation zeros.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicSpline
from .muon_current_source_motion_cubic import _real
from .muon_electromagnetic_source_mean_load import electromagnetic_source_complete_mean_load

def magnetic_source_complete_mean_load(*args, **kwargs):
    """Apply the same literal cubic chain rule to the physical magnetic jet."""
    result=electromagnetic_source_complete_mean_load(*args,**kwargs)
    result.update(actual_local_magnetic_first_jet=True,
        source_motion_scope='actual e R4^2/2 magnetic source and future rate; homogeneous H/Hdot/geometry raw268 jets',
        source_normalization='measured e and R4^2/2 already inserted once by source owner; no extra Tb or electric charge',
        magnetic_axes=[0,1,2],inactive_padded_source_axes=[3,4,5,6,7],
        nonlinear_full_angular_charge_source_family_claimed=False,
        physical_external_Pauli_vertex_evaluated=False)
    return result


def load_magnetic_reached_mean_inputs(directory, *, repository):
    """Bind the fresh local magnetic solve and its complete source first jets."""
    from .muon_primal_electromagnetic_source import retained_phase_source_inputs
    from .muon_electromagnetic_soft_magnetic_source import uniform_magnetic_source_first_jets
    from .muon_parent_maxwell_full_q_application import retained_full_q_angular_space
    root=Path(repository);folder=Path(directory)
    if not folder.is_absolute():folder=root/folder
    data=(folder/'result.json').read_bytes();receipt=json.loads(data)
    allowed=('EVALUATED_HIGGS_ALIGNED_LOCAL_MAGNETIC_JET_FULL488_RESPONSE',
             'EVALUATED_COMMON_BIRTH_LOCAL_MAGNETIC_JET_FULL488_CONTINUATION')
    if receipt['classification'] not in allowed:
        raise ValueError('fresh actual local magnetic first-jet response required')
    if receipt['classification']==allowed[1] and (receipt['side']!='outgoing' or
            not receipt['birth_source_matching']['actual_source_initial_state_supplied_from_incoming_birth']):
        raise ValueError('outgoing magnetic application requires actual incoming canonical birth state')
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
    electric_charge=float(receipt['electric_charge'])
    if not np.isfinite(electric_charge) or electric_charge<=0 or receipt['active_source_indices']!=[0,1,2]:
        raise ValueError('selected canonical charge and complete three magnetic axes required')
    if np.any(source['Q'][:,:,3:]) or np.any(source['Qdot'][:,:,3:]):
        raise ValueError('inactive padded magnetic axes must vanish by probe definition')
    for j in range(ns):
        actual=uniform_magnetic_source_first_jets(raw[j],angular,electric_charge=electric_charge)
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
        raise ValueError('magnetic response and attached phase spans differ')
    rep=bound['representation']
    for key in ('gauge_basis','gauge_radial_basis','wall_trace_map'):
        if not np.array_equal(source[key],rep[key]):
            raise ValueError('saved actual background frame changed: '+key)
    if not np.array_equal(source['source_phase_jacobian'],bound['cell']['jacobian']):
        raise ValueError('magnetic response and chronological native adjoint use different phase Jacobians')
    return dict(receipt=receipt,representation=rep,source=source,source_first_jets=jet,
        phase=phase,velocity=velocity,contacts=contacts,input_hashes=hashes,
        directory=folder,times=times,Gauss_time_interpolant=CubicSpline(times,contacts['A_tau']),
        actual_attached_phase_path=phase_path.parent,consumed_full_attachment=True,
        actual_H_selected_EM_source=True,actual_local_magnetic_first_jet=True,
        electric_charge=electric_charge,active_source_indices=[0,1,2],
        physical_history_selected=False)


def magnetic_source_jet_at_node(inputs, response_time):
    """Return the exact retained analytic source jet at a consumed node."""
    source=inputs['source'];jet=inputs['source_first_jets']
    hits=np.flatnonzero(source['times']==float(response_time))
    if len(hits)!=1:
        raise ValueError('exact retained H-selected source node required')
    j=int(hits[0])
    return dict(Q=source['Q'][j],Qdot=source['Qdot'][j],
        Q_first_jet=jet['Q_first_jet'][j],Qdot_first_jet=jet['Qdot_first_jet'][j])


def magnetic_reached_first_fields(inputs, response_time):
    """Apply the saved solved fields with their actual plateau source law.

    The incoming coordinate clock is u-L with derivative +1.  Both the
    source rate and the solved field rates retain that future orientation.
    The old compact pulse is used by neither the source nor its motion.
    """
    from .muon_electromagnetic_soft_magnetic_source import magnetic_turn_on_profile
    from .muon_parent_retarded_hypercharge import regular_radial_basis
    receipt=inputs['receipt'];t=float(response_time);times=inputs['times']
    hits=np.flatnonzero(times==t)
    if not np.isfinite(t) or len(hits)!=1:
        raise ValueError('exact retained magnetic response node required')
    index=int(hits[0]);s=inputs['source'];hits=np.flatnonzero(s['times']==t)
    if len(hits)!=1:raise ValueError('exact retained primal and magnetic source node required')
    j=int(hits[0]);rep=inputs['representation']
    state=inputs['phase']['state'][index];velocity=inputs['velocity']['velocity'][index]
    interior=np.r_[inputs['contacts']['A_tau'][index],state[:320]].T.reshape(8,5,4,20)
    rate=np.r_[inputs['Gauss_time_interpolant'](t,1),velocity[:320]].T.reshape(8,5,4,20)
    wall=inputs['contacts']['source_trace'][index].T.reshape(8,5,4,20)
    wall_rate=inputs['contacts']['source_trace_rate'][index].T.reshape(8,5,4,20)
    basis,derivative=regular_radial_basis(rep['rho'],1)
    b=basis[:,0,None,None,None,None];l=basis[:,1,None,None,None,None]
    r=derivative[:,0,None,None,None,None];lr=derivative[:,1,None,None,None,None]
    fields=dict(raw_fields=s['raw_fields'][j],response_time=t,coordinate_time=float(s['coordinate_times'][j]),
        first_gauge=b*interior+l*wall,first_gauge_rate=b*rate+l*wall_rate,
        first_gauge_radial=r*interior+lr*wall,first_wall_gauge=wall,
        first_H=state[320:400].T.reshape(8,4,20),first_H_rate=velocity[320:400].T.reshape(8,4,20),
        At_time_derivative_scope='derivative of saved Gauss interpolant; unused by literal Maxwell/Higgs action',
        source_coordinate_clock='incoming coordinate_time=u-L; outgoing coordinate_time=u; future derivative+1',
        all_solved_first_fields_used=True,physical_history_selected=False)
    profile=receipt['source_temporal_profile']
    if profile=='smooth_retarded_turn_on_then_constant_magnetic_trace':
        p,pt,_=magnetic_turn_on_profile(t,receipt['turn_on_duration'])
    elif profile=='constant_magnetic_trace_inherited_from_incoming_birth' and receipt['side']=='outgoing':
        p,pt=1.,0.
    else:
        raise ValueError('actual retarded magnetic turn-on and plateau required')
    jet=magnetic_source_jet_at_node(inputs,response_time)
    expected=p*jet['Q'];expected_rate=pt*jet['Q']+p*jet['Qdot']
    actual=fields['first_wall_gauge'].reshape(8,400).T
    if not np.array_equal(actual,expected) or not np.array_equal(
            inputs['contacts']['source_trace_rate'][index],expected_rate):
        raise ValueError('saved magnetic field and rate differ from their actual source law')
    fields.update(profile=float(p),profile_rate=float(pt),
        source_temporal_profile=inputs['receipt']['source_temporal_profile'],
        actual_local_magnetic_first_jet=True,
        active_source_indices=[0,1,2],inactive_source_indices=[3,4,5,6,7])
    return fields
