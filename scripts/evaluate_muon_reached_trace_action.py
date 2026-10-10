"""Fresh coupled Euler/Gauss application on current reached photon columns."""
from __future__ import annotations
import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED,ZipFile,ZipInfo
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_native_coupled_source_heat import retained_corrected_scalar_photon_response
from bhsm.interface.muon_native_current_component_heat import (
    current_geometric_photon_component,current_component_dual_response,
    current_component_source_history,
)
from bhsm.interface.muon_parent_gauge_geometry_correction import (
    finite_common_iterate_at_time,compact_temporal_basis,
)


def deterministic_archive(path,arrays):
    """Lossless complete compressed arrays, with fixed member metadata."""
    with ZipFile(path,'w',compression=ZIP_DEFLATED,compresslevel=9) as archive:
        for name,array in sorted(arrays.items()):
            stream=BytesIO();np.lib.format.write_array(stream,np.asarray(array),allow_pickle=False)
            member=ZipInfo(name+'.npy',date_time=(1980,1,1,0,0,0))
            member.external_attr=0o600<<16;member.compress_type=ZIP_DEFLATED
            archive.writestr(member,stream.getvalue(),compresslevel=9)
from bhsm.interface.muon_reached_trace_action import (
    coupled_reached_sample,sampled_reached_form,reached_retarded_application,
)


def predecessor_common_field_jet(response,t):
    """Evaluate all raw228 entries from the retained one common vector."""
    c,rep=response['coefficients'],response['representation']
    if rep['gauge_count']!=60 or not rep['include_scalar_mean']:
        raise ValueError('complete material60 gauge and8 scalar coefficient representation required')
    d=finite_common_iterate_at_time(t,c,rep,response['reference'])
    b,bt=compact_temporal_basis(np.array([t]),rep['length'])
    gs=rep['gauge_start'] if 'gauge_start' in rep else 62
    hs=rep['scalar_start']
    raw=np.r_[d['q'],d['qdot'],d['m'],d['normal'],d['normal_rate'],
        b[0]*c[gs:gs+60],bt[0]*c[gs:gs+60],
        b[0]*c[hs:hs+4]+c[hs+4:hs+8],bt[0]*c[hs:hs+4]]
    if raw.shape!=(228,):raise ValueError('same common raw228 field jet required')
    return raw


def materialize(output,*,time_nodes=17,time_steps=64,radial_points=None):
    out=Path(output)
    if out.exists():raise FileExistsError('preserve earlier evidence; choose new output directory')
    response=retained_corrected_scalar_photon_response(ROOT)
    if radial_points is not None and radial_points!=response['representation']['radial_points']:
        raise ValueError('reuse the source-owned radial quadrature representation')
    refs=[str(Path(__file__).relative_to(ROOT)),
        'src/bhsm/interface/muon_reached_trace_action.py',
        'src/bhsm/interface/muon_native_current_component_heat.py',
        'src/bhsm/interface/muon_parent_maxwell_corrected_retarded.py',
        'src/bhsm/interface/muon_parent_maxwell_full_retarded.py',
        'src/bhsm/interface/muon_parent_gauge_geometry_correction.py',
        'src/bhsm/interface/muon_intrinsic_m4_normal_pullback.py',
        'src/bhsm/interface/muon_parent_maxwell_geometry_weak.py',
        'src/bhsm/interface/muon_parent_maxwell_full_q_application.py',
        'src/bhsm/interface/muon_native_photon_response.py']
    hashes={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in refs}
    component=current_geometric_photon_component(response,0.)
    solved=current_component_dual_response(component,multipliers=(1.25,2.,4.))
    record=solved['records'][0]
    times=np.linspace(response['time_shift'],0,time_nodes)
    history=current_component_source_history(response,component,record,times)
    raw=np.array([predecessor_common_field_jet(response,t) for t in times])
    nu=response['receipt']['nu_squared_action_member']
    samples=[]
    for i,(r,Q,Qt) in enumerate(zip(raw,history['full400_source_Q'],history['full400_source_Qdot'])):
        print(json.dumps(dict(stage='same_action_reached_source_sample',node=i,time=float(times[i]))),flush=True)
        samples.append(coupled_reached_sample(r,response['representation'],component['angular'],Q,Qt,nu_squared_action=nu))
    form=sampled_reached_form(history['response_times'],samples,duration=response['duration'])
    applied=reached_retarded_application(form,time_steps=time_steps)
    if hashes!={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in refs}:
        raise RuntimeError('a consumed action owner changed during the application')
    arrays={k:v for k,v in applied.items() if isinstance(v,np.ndarray)}
    groups={}
    for name,value in arrays.items():
        group=('phase' if name=='state' else 'velocity' if name=='velocity' else
            'adjoint' if name=='advanced_adjoint' else 'contact')
        groups.setdefault(group,{})[name]=value
    # Every unreduced action matrix is preserved, losslessly and separately.
    for i,name in enumerate(('M','B','K')):
        groups['operator_'+name]={name:np.array([s['raw_forms'][i] for s in samples]),
            'time_nodes':history['response_times']}
    groups['source']={k:v for k,v in history.items() if isinstance(v,np.ndarray)}
    groups['source'].update(raw_common_field_jets=raw,
        current_angular_response=record['basis_response'],
        current_angular_residual=record['basis_residual'],
        current_angular_return=record['return_basis'],
        actual_gauge_gradient_weak_rows=np.array([s['gauge_weak_rows'] for s in samples]))
    out.mkdir(parents=True)
    receipts={}
    for group,values in sorted(groups.items()):
        path=out/(group+'.npz');deterministic_archive(path,values);data=path.read_bytes()
        if len(data)>10*1024**2:raise ValueError('preserve all arrays; split complete action archive')
        receipts[path.name]=dict(bytes=len(data),sha256=sha256(data).hexdigest(),arrays=sorted(values))
    result={k:v for k,v in applied.items() if not isinstance(v,np.ndarray)}
    result.update(classification='EVALUATED_FRESH_COUPLED_MAXWELL_HIGGS_RESPONSE_ON_CURRENT_REACHED_ANGULAR_COLUMNS',
        source_records=response['source_records'],input_hashes=hashes,array_archives=receipts,
        background_scope='retained corrected outgoing24 local backward numerical chart; not incoming history or full stationary physical event',
        action_parameters=dict(nu_squared_action=nu,surface_gamma=response['receipt'].get('surface_gamma')),
        source_scope='fresh current angular b-frame response at birth; moving material beta=Tb*b; all400 angular actions retained',
        conditioned_angular_shift=float(record['zeta_over_kappa1']),
        shift_is_physical_soft_momentum=False,
        original_Q8_outside_relative_norm=record['outside_original_Q8_relative_norm'],
        minimum_interior_mass_eigenvalue=form['minimum_interior_mass_eigenvalue'],
        source_motion_derivative_identity='beta_dot=gdot*Tb*b + g*(-.5*dlogR4_dt*Tb)*b',
        scalar_Maxwell_relative_normalization=8.,independent_At_Ar_Ai_retained=True,
        gauge_response_norm=float(np.linalg.norm(applied['state'][:,:320])),
        intrinsic_H_response_norm=float(np.linalg.norm(applied['intrinsic_H_response'])),
        intrinsic_H_canonical_norm=float(np.linalg.norm(applied['intrinsic_H_canonical_momenta'])),
        scalar_wall_current_norm=float(np.linalg.norm(applied['intrinsic_scalar_wall_current_pairing'])),
        gauge_Euler_reaction_norm=float(np.linalg.norm(applied['paired_gauge_Euler_reaction'])),
        time_nodes=time_nodes,time_steps=time_steps,physical_source_current_selected=False,
        error_scope='actual finite analytic action samples and DOP853 forward/adjoint residual diagnostics; quadrature/time interpolation and continuous/native-domain errors not enclosed')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--time-nodes',type=int,default=17);p.add_argument('--time-steps',type=int,default=64)
    a=p.parse_args();print(json.dumps(materialize(a.output,time_nodes=a.time_nodes,time_steps=a.time_steps),sort_keys=True))
