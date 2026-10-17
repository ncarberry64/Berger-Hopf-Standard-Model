"""Execute the changing temporal heat target and chronological mean adjoint."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_changing_closed_fermion_mean import changing_n0_heat_mean_target,contract_changing_phase_mean
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output,cutoff):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve earlier temporal targets')
    folder=ROOT/'artifacts/muon_corrected_profile_mean_load_20261011/run_1'
    source=json.loads((folder/'result.json').read_bytes());refs=dict(source['input_hashes'])
    if source['classification']!='EVALUATED_CORRECTED_PROFILE_ALL_RAW268_CUBIC_MEAN_LOAD':raise ValueError('same corrected full268 cubic load required')
    for name in('application.npz','result.json'):
        p=folder/name;h=sha256(p.read_bytes()).hexdigest()
        if name=='application.npz'and h!=source['archive']['sha256']:raise ValueError('actual mean load changed')
        refs[p.relative_to(ROOT).as_posix()]=h
    with np.load(folder/'application.npz',allow_pickle=False)as a:loads={k:a[k].copy()for k in a.files}
    arrays={};rows=[]
    for side in('incoming','outgoing'):
        phase=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'
            else'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
        refs.update(phase['input_hashes']);targets={}
        for order in(12,16):
            print(json.dumps(dict(stage='changing_closed_fermion_target',side=side,order=order)),flush=True)
            t=changing_n0_heat_mean_target(phase,cutoff=cutoff,quadrature_order=order);targets[order]=t
            label=side+'_quadrature_'+str(order)
            for k,v in t.items():
                if isinstance(v,np.ndarray):arrays[label+'_'+k]=v
            frames=[]
            for frame in('temporal','radial'):
                r=contract_changing_phase_mean(t['paired_phase_gradient'],loads[side+'_raw_mean_cotangent'],phase,frame=frame)
                for k,v in r.items():
                    if isinstance(v,np.ndarray):arrays[label+'_'+frame+'_'+k]=v
                frames.append(dict(frame=frame,ungraded_mean_contact_norm=float(np.linalg.norm(r['ungraded_mean_contact'])),
                    ungraded_mean_contact_trace=float(np.trace(r['ungraded_mean_contact'])),
                    original_adjoint_residual_norm=float(np.linalg.norm(r['original_adjoint_residual'])),
                    balanced_condition_number=r['balanced_condition_number']))
            row=dict(side=side,quadrature_order=order,cutoff_probe=float(cutoff),
                paired_Y2_heat_value=t['paired_Y2_value'],paired_phase_cotangent_norm=float(np.linalg.norm(t['paired_phase_gradient'])),
                generalized_eigen_residual=t['generalized_eigen_residual'],Gram_orthonormality_defect=t['Gram_orthonormality_defect'],frames=frames)
            rows.append(row);print(json.dumps(dict(stage='chronological_changing_target_applied',**row),sort_keys=True),flush=True)
        rows[-1]['quadrature12_16_phase_gradient_difference']=float(np.linalg.norm(targets[12]['paired_phase_gradient']-targets[16]['paired_phase_gradient']))
        rows[-1]['quadrature12_16_heat_value_difference']=float(targets[16]['paired_Y2_value']-targets[12]['paired_Y2_value'])
    for p in('src/bhsm/interface/muon_changing_closed_fermion_mean.py','tests/test_muon_changing_closed_fermion_mean.py',
        Path(__file__).relative_to(ROOT).as_posix()):refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed action changed')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    r=dict(classification='EVALUATED_CHANGING_CLOSED_FERMION_HEAT_CHRONOLOGICAL_MEAN_ADJOINT',input_hashes=refs,records=rows,
        archive=dict(path='application.npz',bytes=(out/'application.npz').stat().st_size,sha256=sha256((out/'application.npz').read_bytes()).hexdigest()),
        target_domain='same n0 constant-angular C6 and all8 source-product temporal functions on changing corrected phase',
        target_pullback='quadrature-node raw map includes affine state motion and shared lapse Gram variation; no midpoint-only raw target substituted',
        mean_equation='K^T p=(integrated phase heat target,0); response=-p_original^T F_source',
        action_load='fresh corrected-profile full488 first fields and all268 D3/source-motion rows',
        family_pairing='exact common Y0 background, stable middle-minus-light Y² coefficient',
        statistics_factor_applied=False,full_birth_second_mean_or_complete_Y4_or_native_domain_or_overlap_or_Pauli_completed=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 functional calculus, generalized pairing and same-action finite chronological adjoint; quadrature and residual diagnostics exclude coefficient production, Y4, starting-loop, domain/completion, physical overlap and observable uncertainty')
    (out/'result.json').write_text(json.dumps(r,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(classification=r['classification'],archive=r['archive']),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--cutoff',type=float,default=1e-11)
    a=p.parse_args();materialize(a.output,a.cutoff)
