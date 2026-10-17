"""Identify original canonical equations in an evaluated full146 residual."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(folder,output):
    source=ROOT/folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve every original equation identification')
    rb=(source/'result.json').read_bytes();md=json.loads(rb);refs=dict(md['input_hashes'])
    refs[(source/'result.json').relative_to(ROOT).as_posix()]=sha256(rb).hexdigest()
    p=source/'application.npz';b=p.read_bytes();h=sha256(b).hexdigest()
    if h!=md['archives'][p.name]['sha256']:raise ValueError('same original constitutive application changed')
    refs[p.relative_to(ROOT).as_posix()]=h
    with np.load(p,allow_pickle=False)as z:a={k:z[k].copy()for k in z.files}
    phase,_=retained_input('outgoing',refs);labels=phase['representation']['gauge_labels'];c=phase['coordinates'];n=106
    names=['log_radius']+[f'u_cos_{k}'for k in range(1,13)]+[f'w_cos_{k}'for k in range(12)]+[f'b_cos_{k}'for k in range(12)]+['normal_amplitude']
    names += [f"gauge_{labels[i]['field']}_radial_{labels[i]['radial']}_internal_{labels[i]['internal']}"for i in c['dynamic_gauge_indices']]
    names += [f'Hreal_{k}'for k in range(4)]
    if len(names)!=n:raise ValueError('all original coordinate labels required')
    rows=[f'Lv_{name}-Pi_{name}'for name in names]
    rows += [f'Ly_lapse_cos_{k}=0'for k in range(1,13)]+[f'Ly_shift_cos_{k}=0'for k in range(12)]
    rows += [f"Ly_At_radial_{labels[i]['radial']}_internal_{labels[i]['internal']}=0"for i in c['At_indices']]
    target=np.r_[a['canonical_momentum_target'],np.zeros(40,complex)];G=a['action_gradient'][n:]
    r=a['original_constitutive_rows']
    if not np.array_equal(G-target,r):raise ArithmeticError('stored residual is not the original canonical/zero target equation')
    top=[]
    for i in np.argsort(abs(r))[::-1][:10]:
        i=int(i);raw_indices=np.flatnonzero(c['lift'][:,n+i])
        top.append(dict(original_constitutive_row=i,master_gradient_row=n+i,original_raw_coefficient_rows=raw_indices.tolist(),
            inherited_equation=rows[i],residual_real=float(r[i].real),residual_imag=float(r[i].imag),residual_abs=float(abs(r[i])),
            actual_gradient_real=float(G[i].real),actual_gradient_imag=float(G[i].imag),
            original_target_real=float(target[i].real),original_target_imag=float(target[i].imag)))
    out.mkdir(parents=True);p=out/'application.npz';_compressed_npz(p,dict(original_constitutive_row_labels=np.array(rows),
        original_constitutive_rows=r,actual_original_gradient_rows=G,original_target_rows=target))
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/r).read_bytes()).hexdigest()!=h for r,h in refs.items()):raise RuntimeError('original row-label source changed')
    result=dict(classification='EVALUATED_NAMED_ORIGINAL_CANONICAL_RESIDUAL_ROWS',input_hashes=refs,
        archives={p.name:dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())},largest_original_rows=top,
        full_original146_row_identity_verified=True,physical_constraint_convergence_claimed=False,
        error_scope='exact stored original row identification, no changed source or analytic/physical error enclosure')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='original_named_row_residual_complete',largest=top[0],result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--folder',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.folder,a.output)
