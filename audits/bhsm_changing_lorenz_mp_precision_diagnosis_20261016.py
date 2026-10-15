"""Separate floating solve error from integrated-operand error at failed entries."""
from pathlib import Path
from hashlib import sha256
from io import BytesIO
import sys
import json
import numpy as np
import mpmath as mp

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'audits'))
sys.path.insert(0,str(ROOT/'src'))
from bind_muon_real_changing_gauge_transport_20261016 import archive_bytes,matrix
from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
BASE=ROOT/'artifacts/muon_real_changing_gauge_transport_20261016'


def scalar_gram(a):
    blocks=a.reshape(4,80,4,80).transpose(0,2,1,3)
    g=blocks[:,:,0,0]
    defect=float(np.max(abs(blocks-g[:,:,None,None]*np.eye(80))))
    if defect!=0:raise ValueError('Exact scalar Gram tensor identity required')
    return g,defect


def mm(a):return mp.matrix([[mp.mpf(float(x))for x in row]for row in a])


def entry(G,B,i,j):
    # F=Gghost^-1 B, with Gghost=G4 tensor I80 exactly.
    alpha,k=divmod(i,80)
    return sum(G[alpha,a]*mp.mpf(float(B[a*80+k,j]))for a in range(4))


def fixing(G,B,i,j):
    return sum(mp.mpf(float(B[a*80+k,i]))*G[a,b]*mp.mpf(float(B[b*80+k,j]))
        for k in range(80)for a in range(4)for b in range(4))


def execute(out,fast_validation):
    FAST=Path(fast_validation).resolve()
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    records=[];pins={}
    report=json.loads((FAST/'result.json').read_bytes())
    raw=archive_bytes(BASE,'stable_time6_run_1/changing_forms.npz')
    with np.load(BytesIO(raw),allow_pickle=False)as old:
        for side in('incoming','outgoing'):
            prefix=side+'_radial32_';folder=FAST/(side+'_radial32')
            with np.load(folder/'forms.npz',allow_pickle=False)as new:
                left={n:matrix(old,prefix+n).toarray()for n in('ghost_Gram_per_kappa','weak_gradient_pairing','weak_Lorenz','finite_Lorenz_fixing')}
                right={n:matrix(new,n).toarray()for n in left}
            result=next(r for r in report['records']if r['side']==side)
            gl,dl=scalar_gram(left['ghost_Gram_per_kappa']);gr,dr=scalar_gram(right['ghost_Gram_per_kappa'])
            Bl,Br=left['weak_gradient_pairing'],right['weak_gradient_pairing']
            r=dict(side=side,ghost_Gram_exact_tensor_defect=[dl,dr],
                ghost_Gram_condition_2=[float(np.linalg.cond(gl)),float(np.linalg.cond(gr))],
                ghost_Gram4_eigenvalues=[np.linalg.eigvalsh(g).tolist()for g in(gl,gr)],
                integrated_Gram4_max_absolute=float(np.max(abs(gl-gr))),
                integrated_B_max_absolute=float(np.max(abs(Bl-Br))),controls={})
            with mp.workdps(80):
                inverses=[mm(g)**-1 for g in(gl,gr)]
                action_factor=mp.mpf(float(MAXWELL_TO_CAP))
                r['owned_common_action_factor']=float(action_factor)
                for name,fn in(('weak_Lorenz',entry),('finite_Lorenz_fixing',fixing)):
                    i,j=result['matrix_comparisons'][name]['index']
                    values=[fn(g,b,i,j)*(action_factor if name=='finite_Lorenz_fixing'else 1)
                        for g,b in((inverses[0],Bl),(inverses[1],Bl),(inverses[0],Br),(inverses[1],Br))]
                    binary=[mp.mpf(float(x[name][i,j]))for x in(left,right)]
                    r['controls'][name]=dict(index=[i,j],binary_values=list(map(float,binary)),
                        MP80_values_order='oldG_oldB,newG_oldB,oldG_newB,newG_newB',
                        MP80_values=[mp.nstr(v,65)for v in values],
                        old_binary_vs_MP80=float(abs(binary[0]-values[0])),
                        new_binary_vs_MP80=float(abs(binary[1]-values[3])),
                        change_due_to_integrated_G_only=float(values[1]-values[0]),
                        change_due_to_integrated_B_only=float(values[2]-values[0]),
                        change_in_MP80_from_both_operands=float(values[3]-values[0]),
                        no_recomputed_physical_field_or_derivative=True)
            records.append(r)
            pins['retained_inputs/fast_validation/'+side+'_radial32/forms.npz']=sha256((folder/'forms.npz').read_bytes()).hexdigest()
    result=dict(classification='MP80_DIAGNOSIS_OF_LORENZ_COMPONENT_PRECISION_ONLY',records=records,
        original_time6_npz_sha256=sha256(raw).hexdigest(),input_archive_sha256=pins,
        actual_action_factor_source_sha256=sha256((ROOT/'src/bhsm/interface/muon_parent_mean_causal_action.py').read_bytes()).hexdigest(),
        new_coefficient_selected=False,full_physical_derivative_pass=False,coupled_corrections=0,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        fast_validation_receipt_sha256=sha256((FAST/'result.json').read_bytes()).hexdigest())
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(records,indent=2))


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fast-validation',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();execute(a.output,a.fast_validation)
