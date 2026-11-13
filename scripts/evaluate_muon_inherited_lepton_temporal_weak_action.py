"""Execute changing inherited child lepton weak action on the solved cell."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_birth_finite_normal_phase import load_finite_normal_endpoint
from bhsm.interface.muon_inherited_lepton_temporal_weak_action import inherited_temporal_weak_application
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output,source):
    src=ROOT/source;out=ROOT/output
    if out.exists():raise FileExistsError('preserve prior applications')
    receipt=json.loads((src/'result.json').read_bytes())
    if receipt['classification']!='EVALUATED_INHERITED_PROFILE_CHILD_CANONICAL_ACTION' or receipt['completed_steps']!=receipt['steps']:
        raise ValueError('completed corrected child phase required')
    if receipt['steps']!=1:raise ValueError('this first application consumes exactly the solved one-cell representation')
    refs=dict(receipt['input_hashes'])
    for p,h in refs.items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed action changed: '+p)
    if sha256((src/'application.npz').read_bytes()).hexdigest()!=receipt['numerical_sha256']:raise ValueError('phase changed')
    for name in ('result.json','application.npz'):
        p=src/name;refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    base=load_finite_normal_endpoint('artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1',side='outgoing')
    with np.load(src/'application.npz',allow_pickle=False) as f:saved={k:f[k].copy() for k in f.files}
    arrays={};records=[]
    for order in (8,16):
        a=inherited_temporal_weak_application(saved['stage_independent_raw'][0],float(saved['stage_coordinate_time'][0]),
            saved['initial_pair'],saved['reference_pair'],base['representation'],length=receipt['span'],quadrature_order=order)
        for key,value in a.items():
            if isinstance(value,np.ndarray):arrays['order_'+str(order)+'_'+key]=value
        records.append({k:v for k,v in a.items() if not isinstance(v,np.ndarray)})
        print(json.dumps(dict(order=order,**records[-1]),sort_keys=True),flush=True)
    first=arrays['order_8_weak_form'];second=arrays['order_16_weak_form']
    for name in ('muon_inherited_lepton_temporal_weak_action','muon_inherited_intrinsic_lepton_operator','muon_inherited_wall_lepton_application'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    result=dict(classification='EVALUATED_VARIABLE_INHERITED_CHILD_PROPER_CLOCK_WEAK_LEPTON_ACTION',input_hashes=refs,
        archive=dict(path='application.npz',sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),bytes=(out/'application.npz').stat().st_size),
        records=records,quadrature_weak_form_difference=float(np.linalg.norm(first-second)),
        quadrature_relative_weak_form_difference=float(np.linalg.norm(first-second)/np.linalg.norm(second)),
        total_native_or_physical_Pauli_completed=False,
        error_scope='binary64 quadrature/refinement diagnostic on the actual corrected discrete-action interpolation; not a temporal complement, exterior/native completion, LSZ or anomaly error enclosure')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--source',type=Path,default=Path('artifacts/muon_inherited_finite_normal_phase_20261011/run_1'))
    a=p.parse_args();print(json.dumps(materialize(a.output,a.source),sort_keys=True))
