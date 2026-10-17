"""Apply literal highprecision gradient at the reached nearroot original point."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action
from bhsm.interface.muon_high_precision_constitutive_gradient import high_precision_original_constitutive_gradient
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(initial_folder,output,precision):
    source=ROOT/initial_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve every highprecision original action application')
    refs={};rb=(source/'result.json').read_bytes();md=json.loads(rb);refs.update(md['input_hashes'])
    refs[(source/'result.json').relative_to(ROOT).as_posix()]=sha256(rb).hexdigest()
    p=source/'application.npz';b=p.read_bytes();h=sha256(b).hexdigest()
    if h!=md['archives'][p.name]['sha256']:raise ValueError('same nearroot original action state changed')
    refs[p.relative_to(ROOT).as_posix()]=h
    with np.load(p,allow_pickle=False)as z:data={k:z[k].copy()for k in z.files}
    phase,_=retained_input('outgoing',refs);P=phase['coordinates']['lift'];raw=P@data['coefficients'];time=data['coordinate_time'].item()
    args=(phase['arrays']['initial_pair'],phase['arrays']['reference_pair'],phase['representation']);params=md['action_parameters']
    old=holomorphic_inherited_child_action(raw,time,*args,**params)
    print(json.dumps(dict(stage='literal_highprecision_original146_gradient',decimal_precision=precision)),flush=True)
    new=high_precision_original_constitutive_gradient(raw,time,*args,**params,decimal_precision=precision)
    target=np.r_[data['canonical_momentum_target'],np.zeros(40,complex)];r=new['constitutive_gradient']-target
    difference=new['constitutive_gradient']-old['gradient'][106:]
    out.mkdir(parents=True);p=out/'application.npz';_compressed_npz(p,dict(raw_fields=raw,coefficients=data['coefficients'],
        canonical_momentum_target=data['canonical_momentum_target'],coordinate_time=np.array(time),
        high_precision_constitutive_gradient=new['constitutive_gradient'],high_precision_gradient_decimal_strings=new['gradient_decimal_strings'],
        binary_original_constitutive_gradient=old['gradient'][106:],high_precision_original_constitutive_rows=r,
        binary_original_constitutive_rows=old['gradient'][106:]-target,high_precision_minus_binary_gradient=difference,
        original_action_Hessian=old['hessian'],original_action_force=old['gradient'][:106],
        high_precision_action_value=np.array(new['value']),binary_action_value=np.array(old['value'])))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for p_ in(Path(__file__),'tests/test_muon_high_precision_constitutive_gradient.py'):
        p_=Path(p_);p_=p_ if p_.is_absolute()else ROOT/p_;refs[p_.relative_to(ROOT).as_posix()]=sha256(p_.read_bytes()).hexdigest()
    if any(sha256((ROOT/r).read_bytes()).hexdigest()!=h for r,h in refs.items()):raise RuntimeError('same highprecision action source changed')
    result=dict(classification='EVALUATED_LITERAL_HIGH_PRECISION_ORIGINAL_CHILD146_CONSTITUTIVE_GRADIENT',input_hashes=refs,
        archives={p.name:dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())},decimal_precision=precision,
        high_precision_original_rows_max=float(np.max(abs(r))),binary_original_rows_max=float(np.max(abs(old['gradient'][106:]-target))),
        high_precision_original_momentum_rows_max=float(np.max(abs(r[:106]))),high_precision_original_algebraic_rows_max=float(np.max(abs(r[106:]))),
        original_gradient_precision_difference_max=float(np.max(abs(difference))),original_gradient_precision_difference_norm=float(np.linalg.norm(difference)),
        largest_original_row=int(np.argmax(abs(r))),all_original146_rows_evaluated=True,same_original_x_Pi_and_frame=True,
        original_x_force_or_Hessian_replaced=False,action_parameters=params,lambda_H=phase['representation']['scalar_matching']['lambda_H'],
        source_chart_and_inherited_germs=new['positional_response_and_inherited_coefficients_scope'],
        physical_branch_first_hit_Pauli_or_error_bound=False,
        error_scope='mpmath arbitraryprecision original finite signed action firstgradient with fixed positional/binary source germs; no outward upstream/domain or anomaly enclosure')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='literal_highprecision_original_gradient_complete',original_rows_max=result['high_precision_original_rows_max'],
        precision_difference_max=result['original_gradient_precision_difference_max'],result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--initial-folder',type=Path,default=Path('artifacts/muon_material_rate_canonical_geometry_20261011/continued_run_1'))
    p.add_argument('--output',type=Path,required=True);p.add_argument('--precision',type=int,default=60)
    a=p.parse_args();materialize(a.initial_folder,a.output,a.precision)
