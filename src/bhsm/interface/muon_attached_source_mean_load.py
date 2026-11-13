"""Bind the executed full-attachment response to the retained cubic consumer.

The frozen enriched218 binder remains unchanged.  Here the same field
applications consume the actual full220 attachment and its saved one-cell
phase, including its complete Gauss, gauge and Higgs responses.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicSpline

from .muon_current_source_motion_cubic import _real,current_face_source_jets
from .muon_birth_attached_phase import load_attached_endpoint


def load_attached_reached_mean_inputs(directory, *, repository):
    """Verify the SAME full220 phase, source motion and solved first fields."""
    root=Path(repository);folder=Path(directory)
    if not folder.is_absolute():folder=root/folder
    data=(folder/'result.json').read_bytes();receipt=json.loads(data)
    if receipt['classification']!='EVALUATED_FRESH_COUPLED_REACHED_RESPONSE_ON_ACTUAL_ATTACHED_PHASE':
        raise ValueError('actual fresh attached response required')
    if receipt['side'] not in ('incoming','outgoing'):
        raise ValueError('actual oriented attached arm required')
    if receipt['old_source_or_H_response_substituted'] or receipt['source_motion_count']!=1:
        raise ValueError('fresh response with exactly one source-motion application required')
    hashes=dict(receipt['input_hashes'])
    for name,digest in hashes.items():
        if sha256((root/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('consumed owner changed: '+name)
    hashes[folder.relative_to(root).as_posix()+'/result.json']=sha256(data).hexdigest()
    loaded={}
    for name in ('primal_and_source.npz','phase.npz','velocity.npz','contacts.npz'):
        data=(folder/name).read_bytes();info=receipt['array_archives'][name]
        if len(data)!=info['bytes'] or sha256(data).hexdigest()!=info['sha256']:
            raise ValueError('response archive changed: '+name)
        hashes[folder.relative_to(root).as_posix()+'/'+name]=info['sha256']
        with np.load(folder/name,allow_pickle=False) as a:
            loaded[name]={key:a[key].copy() for key in a.files}
    s,phase,velocity,contacts=(loaded[name] for name in ('primal_and_source.npz','phase.npz','velocity.npz','contacts.npz'))
    times=_real(phase['times'],'fresh response times');nt=len(times)
    if times.ndim!=1 or times[0]!=0 or np.any(np.diff(times)<=0):
        raise ValueError('increasing future-coordinate response time grid required')
    if not np.array_equal(times,velocity['times']) or not np.array_equal(times,contacts['times']):
        raise ValueError('response time grids differ')
    _real(phase['state'],'complete first phase',(nt,800,8))
    _real(velocity['velocity'],'complete first velocity',(nt,400,8))
    _real(contacts['A_tau'],'complete solved Gauss field',(nt,80,8))
    if not np.array_equal(contacts['intrinsic_H_response'],phase['state'][:,320:400]):
        raise ValueError('intrinsic scalar response is not the same phase')
    b=_real(s['b_source_coefficients'],'inherited full source',(400,8))
    if np.any(b[:160]):raise ValueError('inherited spatial source required')
    source_times=_real(s['times'],'actual coefficient times')
    raw=_real(s['raw_fields'],'actual coefficient fields',(len(source_times),268))
    expected_clock=source_times-times[-1] if receipt['side']=='incoming' else source_times
    if not np.array_equal(s['coordinate_times'],expected_clock):
        raise ValueError('future coordinate source clock differs from the attached arm')
    for index in range(len(source_times)):
        chart=current_face_source_jets(raw[index,:100])
        if not np.array_equal(s['Q'][index],chart['T_b'].value*b) or not np.array_equal(s['Qdot'][index],chart['T_b_dot'].value*b):
            raise ValueError('source and source-rate do not use the same actual phase chart')
    candidates=[name for name in hashes if name.endswith('/result.json')
        and 'attached_phase_'+receipt['side']+'_' in name]
    if len(candidates)!=1:raise ValueError('unique consumed attached primal phase required')
    phase_path=root/candidates[0];phase_receipt=json.loads(phase_path.read_bytes())
    if phase_receipt['steps']!=1 or phase_receipt['completed_steps']!=1 or phase_receipt['stages'][0]['status']!='REPRESENTED_PHASE_TOLERANCE':
        raise ValueError('evaluated complete attached one-cell phase required')
    if phase_receipt['span']!=receipt['actual_phase_span']:
        raise ValueError('source and primal phase spans differ')
    rep=load_attached_endpoint(phase_receipt['consumed_paired_endpoint_path'],side=receipt['side'],repository=root)['representation']
    for name in ('gauge_basis','gauge_radial_basis','wall_trace_map'):
        if not np.array_equal(s[name],rep[name]):
            raise ValueError('saved attached background frame differs: '+name)
    with np.load(phase_path.parent/'application.npz',allow_pickle=False) as a:
        if not np.array_equal(s['source_phase_jacobian'],a['stage_jacobian'][0]):
            raise ValueError('source consumer and native adjoint use different phase Jacobians')
    return dict(receipt=receipt,representation=rep,source=s,phase=phase,velocity=velocity,contacts=contacts,
        input_hashes=hashes,directory=folder,times=times,
        Gauss_time_interpolant=CubicSpline(times,contacts['A_tau']),
        actual_attached_phase_path=phase_path.parent,
        consumed_full_attachment=True,physical_history_selected=False)
