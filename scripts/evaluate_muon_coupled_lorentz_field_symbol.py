"""Evaluate original coupled field action at the same incoming/child birth."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_coupled_lorentz_field_symbol import coupled_field_symbol
from bhsm.interface.muon_birth_finite_normal_trace_graph import pointwise_finite_normal_action
from bhsm.interface.muon_birth_inherited_finite_normal_phase import inherited_child_finite_normal_action
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase,profile_preserving_lepton_sample
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out=Path(output);out=out if out.is_absolute()else ROOT/out
    if out.exists():raise FileExistsError('preserve earlier coupled signed applications')
    refs={};arrays={};records=[]
    for side,folder in (('incoming','artifacts/muon_finite_normal_phase_20261011/incoming_run_1'),
                        ('outgoing','artifacts/muon_inherited_finite_normal_phase_20261011/run_1')):
        phase=load_profile_preserving_phase(folder);refs.update(phase['input_hashes'])
        s=profile_preserving_lepton_sample(phase,0.);raw=s['sample']['raw_fields'];rep=phase['representation']
        opts=phase['receipt']['action_parameters']
        print(json.dumps(dict(stage='original_signed_coupled_action',side=side)),flush=True)
        if side=='incoming':a=pointwise_finite_normal_action(raw,rep,**opts)
        else:a=inherited_child_finite_normal_action(raw,0.,phase['arrays']['initial_pair'],phase['arrays']['reference_pair'],rep,**opts)
        r=coupled_field_symbol(a,rep,lapse=s['operator']['N'],H=raw[-8:-4]);records.append({k:v for k,v in r.items()if not isinstance(v,np.ndarray)}|dict(side=side,lapse=s['operator']['N'],radius=s['operator']['R4']))
        for k,v in r.items():
            if isinstance(v,np.ndarray):arrays[side+'_'+k]=v
        arrays[side+'_raw_fields']=raw;arrays[side+'_full_action_gradient']=a['gradient'];arrays[side+'_full_action_hessian']=a['hessian']
        print(json.dumps(dict(stage='coupled_signed_symbol_complete',side=side,
            field_dimension=r['joint_trace_map'].shape[1],quotient_dimension=r['field_quotient_lift'].shape[1],
            field_gradient_norm=float(np.linalg.norm(r['field_action_gradient'])))),flush=True)
    for name in ('muon_coupled_lorentz_field_symbol','muon_local_normal_action_symbol',
                 'muon_birth_finite_normal_trace_graph','muon_birth_inherited_finite_normal_phase'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    for p in (Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_coupled_lorentz_field_symbol.py'):
        refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same signed action changed')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    md=dict(classification='EVALUATED_ORIGINAL_COUPLED_CAP_RADIAL_FIELD_FREQUENCY_APPLICATION',
        input_hashes=refs,records=records,archive=dict(path='application.npz',bytes=(out/'application.npz').stat().st_size,
        sha256=sha256((out/'application.npz').read_bytes()).hexdigest()),
        consumer='full gauge/Higgs radial and wall Schur Green, actual scalar residue, local Lorentz overlap restriction',
        physical_overlap_subtracted=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='exact original finite signed action derivatives in binary64; computational radial frame not promoted to BRST, complement or global pole enclosure')
    (out/'result.json').write_text(json.dumps(md,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(classification=md['classification'],archive=md['archive']),sort_keys=True),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args();materialize(args.output)
