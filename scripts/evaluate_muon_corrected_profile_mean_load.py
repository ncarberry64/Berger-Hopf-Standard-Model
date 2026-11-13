"""Evaluate corrected-profile cubic mean loads on the actual full488 magnetic fields."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
from scipy.interpolate import CubicSpline
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_corrected_profile_magnetic_response import corrected_magnetic_source_sample
from bhsm.interface.muon_corrected_profile_mean_load import corrected_profile_mean_load
from bhsm.interface.muon_parent_retarded_hypercharge import regular_radial_basis
from bhsm.interface.muon_electromagnetic_soft_magnetic_source import magnetic_turn_on_profile
from evaluate_muon_reached_trace_action import deterministic_archive


def bind(side):
    folder=ROOT/'artifacts/muon_corrected_profile_magnetic_response_20261011/run_1'
    md=json.loads((folder/'result.json').read_bytes());refs=dict(md['input_hashes'])
    refs[(folder/'result.json').relative_to(ROOT).as_posix()]=sha256((folder/'result.json').read_bytes()).hexdigest()
    if md['classification']!='EVALUATED_CORRECTED_PROFILE_SAME_BIRTH_LOCAL_MAGNETIC_FULL488_RETARDED_RESPONSE':
        raise ValueError('corrected same-birth first response required')
    arrays={}
    for stem in('primal_and_source','phase','velocity','contacts'):
        p=folder/(side+'_'+stem+'.npz');data=p.read_bytes();entry=md['array_archives'][p.name]
        if sha256(data).hexdigest()!=entry['sha256']:raise ValueError('actual first fields changed')
        refs[p.relative_to(ROOT).as_posix()]=entry['sha256']
        with np.load(p,allow_pickle=False)as a:arrays[stem]={k:a[k].copy()for k in a.files}
    phase=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'
        else'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
    refs.update(phase['input_hashes'])
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise ValueError('consumed owner changed')
    return md,phase,arrays,refs


def actual_first_fields(side,phase,arrays,coordinate_time,angular,electric_charge):
    span=abs(phase['receipt']['span']);u=float(coordinate_time+(span if side=='incoming'else 0.))
    times=arrays['phase']['times'];hits=np.flatnonzero(times==u)
    if len(hits)!=1:raise ValueError('actual retained response node required')
    index=int(hits[0]);state=arrays['phase']['state'][index];velocity=arrays['velocity']['velocity'][index]
    source=corrected_magnetic_source_sample(phase,coordinate_time,angular,electric_charge=electric_charge)['source']
    p,pt,_=magnetic_turn_on_profile(u,span/4)if side=='incoming'else(1.,0.,0.)
    interior=np.r_[arrays['contacts']['A_tau'][index],state[:320]].T[:3].reshape(3,5,4,20)
    gaussrate=CubicSpline(times,arrays['contacts']['A_tau'])(u,1)
    rate=np.r_[gaussrate,velocity[:320]].T[:3].reshape(3,5,4,20)
    wall=(p*source['connection_source']).T[:3].reshape(3,5,4,20)
    wallrate=(pt*source['connection_source']+p*source['connection_source_rate']).T[:3].reshape(3,5,4,20)
    if not np.array_equal(wall,arrays['contacts']['source_trace'][index].T[:3].reshape(wall.shape)):
        raise ValueError('same analytic source and actual solved wall fields required')
    b,br=regular_radial_basis(phase['representation']['rho'],1)
    args=dict(first_gauge=b[:,0,None,None,None,None]*interior+b[:,1,None,None,None,None]*wall,
        first_gauge_rate=b[:,0,None,None,None,None]*rate+b[:,1,None,None,None,None]*wallrate,
        first_gauge_radial=br[:,0,None,None,None,None]*interior+br[:,1,None,None,None,None]*wall,
        first_wall_gauge=wall,first_H=state[320:400].T[:3].reshape(3,4,20),
        first_H_rate=velocity[320:400].T[:3].reshape(3,4,20))
    return source,p,pt,args


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve prior corrected loads')
    angular=retained_full_q_angular_space(ROOT);refs={};arrays={};rows=[]
    config=ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json';charge=np.sqrt(4*np.pi*json.loads(config.read_bytes())['alpha_consumer']['value'])
    refs[config.relative_to(ROOT).as_posix()]=sha256(config.read_bytes()).hexdigest()
    for side in('incoming','outgoing'):
        md,phase,a,more=bind(side);refs.update(more);L=abs(phase['receipt']['span'])
        # Beginning with the actual same-action midpoint, no saved-center D3 transplanted.
        t=(-L/2 if side=='incoming'else L/2)
        source,p,pt,fields=actual_first_fields(side,phase,a,t,angular,charge)
        from bhsm.interface.muon_profile_preserving_phase_sample import profile_preserving_raw_sample
        raw=profile_preserving_raw_sample(phase,t)['raw_fields']
        kw=dict(initial_pair=phase['arrays']['initial_pair'],reference_pair=phase['arrays']['reference_pair'])if side=='outgoing'else{}
        r=corrected_profile_mean_load(raw,phase['representation'],angular,dict(Q_first_jet=source['Q_first_jet'],Qdot_first_jet=source['Qdot_first_jet']),
            p,pt,**fields,coordinate_time=t,nu_squared_action=phase['receipt']['action_parameters']['nu_squared_action'],**kw)
        for k,v in r.items():
            if isinstance(v,np.ndarray):arrays[side+'_'+k]=v
        for k,v in fields.items():arrays[side+'_'+k]=v
        row=dict(side=side,coordinate_time=t,raw_mean_norm=float(np.linalg.norm(r['raw_mean_cotangent'])),
            fixed_field_mean_norm=float(np.linalg.norm(r['fixed_field_raw_mean_cotangent'])),
            source_motion_norm=float(np.linalg.norm(r['source_motion_cotangent'])),
            pair_symmetry_defect=float(np.linalg.norm(r['raw_mean_cotangent']-r['raw_mean_cotangent'].swapaxes(-1,-2))),
            child_partial_connection_derivative_norm=float(np.linalg.norm(r['background_geometry_connection_first_jet'])),
            inherited_parent_connection_derivative_norm=float(np.linalg.norm(r['inherited_parent_geometry_first_jet'])))
        rows.append(row);print(json.dumps(dict(stage='corrected_action_D3_mean',**row),sort_keys=True),flush=True)
    for p in('src/bhsm/interface/muon_corrected_profile_mean_load.py',Path(__file__).relative_to(ROOT).as_posix(),
        'tests/test_muon_corrected_profile_mean_load.py'):
        refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed owner changed')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    r=dict(classification='EVALUATED_CORRECTED_PROFILE_ALL_RAW268_CUBIC_MEAN_LOAD',records=rows,input_hashes=refs,
        archive=dict(path='application.npz',bytes=(out/'application.npz').stat().st_size,sha256=sha256((out/'application.npz').read_bytes()).hexdigest()),
        action_chain_rule='D3S[z,uA,uB]+D2S[D_z uA,uB]+D2S[uA,D_z uB]',
        active_magnetic_axes=[0,1,2],source_motion_count=1,all268_mean_rows_retained=True,
        parent_reference_binding='per-arm child partial holds explicit incoming/reference values; parent connection cotangent exported, joint birth second-mean application remains distinct',
        physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 exact owned-action contractions on saved radial/first-response point values; original Hessian directional checks and pair symmetry are diagnostics, not native/domain/Pauli bounds')
    (out/'result.json').write_text(json.dumps(r,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(classification=r['classification'],archive=r['archive']),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.output)
