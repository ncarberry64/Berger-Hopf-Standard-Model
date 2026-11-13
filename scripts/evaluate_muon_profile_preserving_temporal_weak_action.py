"""Continue the same inherited temporal weak action through1/2/4 solved cells."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
from scipy.linalg import eigh
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase,profile_preserving_lepton_sample
from bhsm.interface.muon_inherited_lepton_temporal_weak_action import smooth_temporal_trial
from evaluate_muon_reached_trace_action import deterministic_archive


def integrate(phase,order):
    r=phase['receipt'];L=r['span'];h=L/r['steps']
    if L<=0:raise ValueError('same corrected outgoing orientation required')
    x,w=np.polynomial.legendre.leggauss(order)
    K=np.zeros((36,36),complex);G=K.copy();samples=[]
    for cell in range(r['steps']):
        for t,weight in zip((cell+(x+1)/2)*h,w*h/2):
            a=profile_preserving_lepton_sample(phase,float(t));op=a['operator']
            b,d=smooth_temporal_trial(t,L);V=np.hstack([z*np.eye(18)for z in b]);Dt=np.hstack([z*np.eye(18)for z in d])
            A=Dt/op['N']+(op['W']+op['Omega_tau'])@V
            K+=weight*op['N']*(A.conj().T@A);G+=weight*op['N']*(V.conj().T@V)
            samples.append((t,op['N'],op['R4'],np.linalg.norm(a['time_derivatives']['W']['proper_time'])))
    K=(K+K.conj().T)/2;G=(G+G.conj().T)/2;p,U=eigh(K,G)
    if p[0]<=0:raise ArithmeticError('actual full18 proper-clock factor not positive')
    return dict(K=K,G=G,p=p,U=U,samples=np.array(samples))


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve previous calculations')
    sources=('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',
        'artifacts/muon_profile_preserving_phase_sample_20261011/outgoing_2steps_run_1',
        'artifacts/muon_profile_preserving_phase_sample_20261011/outgoing_4steps_run_1')
    arrays={};records=[];refs={}
    for source in sources:
        phase=load_profile_preserving_phase(source);steps=phase['receipt']['steps'];refs.update(phase['input_hashes'])
        apps={order:integrate(phase,order)for order in (8,16)}
        for order,a in apps.items():
            for k,v in a.items():arrays[f'cells_{steps}_order_{order}_{k}']=v
        a=apps[16];defect=np.linalg.norm(a['K']@a['U']-(a['G']@a['U'])*a['p'])/np.linalg.norm(a['K']@a['U'])
        rec=dict(cells=steps,minimum_generalized_eigenvalue=float(a['p'][0]),
            generalized_eigen_relative_residual=float(defect),
            Gram_orthonormality_defect=float(np.linalg.norm(a['U'].conj().T@a['G']@a['U']-np.eye(36))),
            quadrature_relative_difference=float(np.linalg.norm(apps[8]['K']-a['K'])/np.linalg.norm(a['K'])))
        if records:
            prior=records[-1]['cells'];rec['prior_cells']=prior
            rec['prior_cell_weak_form_difference']=float(np.linalg.norm(a['K']-arrays[f'cells_{prior}_order_16_K']))
            rec['prior_cell_Gram_difference']=float(np.linalg.norm(a['G']-arrays[f'cells_{prior}_order_16_G']))
        records.append(rec);print(json.dumps(rec,sort_keys=True),flush=True)
    for name in ('muon_profile_preserving_phase_sample','muon_inherited_lepton_temporal_weak_action'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    result=dict(classification='EVALUATED_REFINED_CHRONOLOGICAL_INHERITED_PROPER_CLOCK_WEAK_ACTION',input_hashes=refs,
        archive=dict(path='application.npz',sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),bytes=(out/'application.npz').stat().st_size),records=records,
        whole18_constant_angular_current_component_retained=True,proper_clock_Gram_used=True,
        separate_W_tau_contact_added=False,
        physical_cutoff_or_exterior_Pauli_state_selected=False,
        error_scope='actual same-action1/2/4-cell chronological representation and8/16-point weak quadrature diagnostics; no continuous-Euler, temporal-complement, native-domain, LSZ or anomaly enclosure')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    print(json.dumps(materialize(a.output),sort_keys=True))
