"""Apply true birth canonical means to the same changing native heat target."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_joined_chronological_heat_mean import joined_phase_heat_mean
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve prior joined mean')
    refs={};data={}
    for key,stem in (('canonical','muon_corrected_birth_canonical_mean'),('mean','muon_corrected_profile_mean_load'),('heat','muon_changing_closed_fermion_mean')):
        folder=ROOT/'artifacts'/(stem+'_20261011')/'run_1';md=json.loads((folder/'result.json').read_bytes());refs.update(md['input_hashes'])
        for name in ('result.json','application.npz'):
            p=folder/name;h=sha256(p.read_bytes()).hexdigest();refs[p.relative_to(ROOT).as_posix()]=h
            if name=='application.npz'and h!=md.get('numerical_sha256',md.get('archive',{}).get('sha256')):raise ValueError('consumed joined input changed')
        with np.load(folder/'application.npz',allow_pickle=False)as a:data[key]={k:a[k].copy()for k in a.files}
    arrays={};records=[];c=data['canonical']
    for arm,side in enumerate(('incoming','outgoing')):
        phase=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'else'artifacts/muon_inherited_finite_normal_phase_20261011/run_1');refs.update(phase['input_hashes'])
        if not np.array_equal(c['coordinate_lift'],phase['coordinates']['lift']):raise ValueError('same canonical trace lift required')
        initial=phase['arrays']['initial_raw']if side=='incoming'else phase['arrays']['initial_independent_raw']
        if not np.array_equal(initial,c['initial_pair'][arm]):raise ValueError('truebirth and phase base mismatch')
        prefix=side+'_quadrature_16_';heat={k[len(prefix):]:v for k,v in data['heat'].items()if k.startswith(prefix)}
        for frame in ('temporal','radial'):
            print(json.dumps(dict(stage='joined_chronological_birth_mean',side=side,frame=frame)),flush=True)
            r=joined_phase_heat_mean(phase,heat,data['mean'][side+'_raw_mean_cotangent'],c['canonical_states'][arm],
                parent_gradient_forcing=c['midpoint_raw_gradient_forcing']if arm else None,
                initial_parent_mean=c['raw_mean_correction'][0]if arm else None,frame=frame)
            for k,v in r.items():
                if isinstance(v,np.ndarray):arrays[side+'_'+frame+'_'+k]=v
            for k,v in r['inherited_parameter_application'].items():
                if isinstance(v,np.ndarray):arrays[side+'_'+frame+'_'+k]=v
            row=dict(side=side,frame=frame,total_ungraded_heat_contact_trace=float(np.trace(r['paired_total_heat_mean_contact'])),
                total_ungraded_heat_contact_norm=float(np.linalg.norm(r['paired_total_heat_mean_contact'])),
                inherited_parameter_contact_norm=float(np.linalg.norm(r['paired_inherited_parameter_target_contact'])),
                explicit_initial_target_contact_norm=float(np.linalg.norm(r['paired_explicit_initial_target_contact'])),
                actual_far_canonical_mean_norm=float(np.linalg.norm(r['actual_far_canonical_mean'])),
                original_residual_norm=float(np.linalg.norm(r['original_residual'])),chronological_primal_residual_norm=float(np.linalg.norm(r['chronological_primal_residual'])),
                chronological_adjoint_residual_norm=float(np.linalg.norm(r['chronological_adjoint_residual'])),
                primal_adjoint_difference_norm=float(np.linalg.norm(r['phase_primal_adjoint_difference'])))
            records.append(row);print(json.dumps(dict(stage='joined_chronological_birth_mean_evaluated',**row),sort_keys=True),flush=True)
    for p in ('src/bhsm/interface/muon_joined_chronological_heat_mean.py','tests/test_muon_joined_chronological_heat_mean.py',Path(__file__).relative_to(ROOT).as_posix()):
        refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed action changed')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    md=dict(classification='EVALUATED_JOINED_TRUE_BIRTH_CHRONOLOGICAL_HEAT_MEAN',input_hashes=refs,records=records,
        archive=dict(path='application.npz',bytes=(out/'application.npz').stat().st_size,sha256=sha256((out/'application.npz').read_bytes()).hexdigest()),
        cutoff_probe=1e-11,statistics_factor_applied=False,higher_even_Y_bounded_on_stored_pencil=True,
        incoming_far_mean_role='actual output of the original signed canonical cell, reused as its chronological initial mean; no zero-before-source or physical E0 assertion',
        source_count='truebirth H_v delta+g_v once; same corrected midpoint D3/Q/Qdot load; child inherited affine gradient and native parameter contacts once',
        physical_a_mu=None,physical_g_mu=None,complete_observable=False,
        error_scope='Binary64 original/chronological primal-adjoint applications, same changing n0/C6 temporal8 target and actual moving226 birth mean; producer/quadrature/causal far-domain/native completion/Pauli uncertainties remain separate')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(classification=md['classification'],archive=md['archive']),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();materialize(a.output)
