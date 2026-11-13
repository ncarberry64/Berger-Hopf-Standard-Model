"""Apply exact local charge matching to the reached magnetic restriction."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_local_charge_matching_response import local_charge_matching_identity,source_form_charge_restriction
from bhsm.interface.muon_magnetic_source_photon_action import executed_magnetic_photon_quadratic_action
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out=Path(output);out=out if out.is_absolute()else ROOT/out
    if out.exists():raise FileExistsError('preserve prior current matching applications')
    folder=ROOT/'artifacts/muon_chronological_native_return_20261011/run_3'
    p=folder/'result.json';data=p.read_bytes();receipt=json.loads(data)
    if receipt['classification']!='EVALUATED_SAME_ACTION_MAGNETIC_NATIVE_RETURN_WITH_TRUE_BIRTH_CHRONOLOGICAL_MEAN':
        raise ValueError('same background/current/chronological native source application required')
    refs=dict(receipt['input_hashes']);refs[p.relative_to(ROOT).as_posix()]=sha256(data).hexdigest()
    p=folder/receipt['archive']['path'];data=p.read_bytes()
    if len(data)!=receipt['archive']['bytes']or sha256(data).hexdigest()!=receipt['archive']['sha256']:
        raise ValueError('retained chronological source form changed')
    refs[p.relative_to(ROOT).as_posix()]=sha256(data).hexdigest()
    with np.load(p,allow_pickle=False)as a:forms={k:a[k]for k in a.files}
    arrays={};rows=[]
    for side in ('incoming','outgoing'):
        source=[p for p in refs if p.endswith('/result.json')and '/muon_electromagnetic_soft_magnetic_source_'in p and '/'+side+'_run_'in p]
        if len(source)!=1:raise ValueError('same magnetic source owner not unique')
        bare=executed_magnetic_photon_quadratic_action((ROOT/source[0]).parent,repository=ROOT)
        refs.update(bare['input_hashes']);K=bare['Maxwell_source_quadratic_action'][:3,:3]
        for row in (x for x in receipt['records']if x['side']==side):
            tag=side+'_q_'+str(row['q_probe']).replace('.','p')
            lo=forms[tag+'_applied_native_real_lower'][:3,:3];hi=forms[tag+'_applied_native_real_upper'][:3,:3]
            imaginary=forms[tag+'_applied_native_imaginary'][:3,:3]
            R=(lo+hi)/2+1j*imaginary
            r=source_form_charge_restriction(K,R)
            for k,v in r.items():
                if isinstance(v,np.ndarray):arrays[tag+'_'+k]=v
            arrays[tag+'_tested_Maxwell_source_form']=K;arrays[tag+'_actual_native_real_lower']=lo;arrays[tag+'_actual_native_real_upper']=hi
            # A linear coefficient interval for the retained entry bounds.
            # It is a binary diagnostic; no upstream formation enclosure.
            coeff=K.real/np.vdot(K,K).real
            zl=float(np.sum(np.where(coeff>=0,coeff*lo,coeff*hi)))
            zu=float(np.sum(np.where(coeff>=0,coeff*hi,coeff*lo)))
            rows.append(dict(side=side,q_probe=row['q_probe'],common_cutoff_probe=row['common_cutoff_probe'],
                real_proportional_restriction_coefficient=r['real_proportional_coefficient'],
                real_coefficient_entry_interval_diagnostic=[zl,zu],
                surviving_nonproportional_complex_source_form_norm=r['restriction_residual_norm'],
                surviving_restriction_relative_norm=r['surviving_restriction_relative_norm'],
                scalar_charge_cancellation_arithmetic_defect=r['scalar_charge_cancellation_arithmetic_defect'],
                Maxwell_source_form_eigenvalues=np.linalg.eigvalsh(K).tolist(),
                physical_locality_not_inferred=True,subtraction_applied=False))
            print(json.dumps(rows[-1],sort_keys=True),flush=True)
    for p in ('src/bhsm/interface/muon_local_charge_matching_response.py','tests/test_muon_local_charge_matching_response.py',Path(__file__).relative_to(ROOT).as_posix()):
        refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('reached action/current changed during matching restriction')
    out.mkdir(parents=True);p=out/'application.npz';deterministic_archive(p,arrays)
    r=dict(classification='EVALUATED_LOCAL_CHARGE_MATCHING_IDENTITY_AND_ACTUAL_MAGNETIC_RESTRICTION',
        input_hashes=refs,archive=dict(path=p.name,bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest()),records=rows,
        exact_local_action_identity=local_charge_matching_identity(),
        current_source='actual same-background graded+1/2 direct/both-insertion/true-birth mean and complete source Maxwell action; original attached numerical domain retained',
        source_charge_normalization='physical magnetic source already includes measured e once; no second e inserted in source forms',
        calibrated_alpha_or_local_QED_ledger_changed=False,
        proportional_restriction_does_not_establish_a_local_F_squared_coefficient=True,
        nonproportional_and_momentum_dependent_remainder_retained=True,
        same_source_local_overlap_subtracted=False,
        overlap='momentum-dependent local lepton VP belongs to the photon/current sector and remains retained; intrinsic scalar loop requires its own fixed-Y scalar overlap, not VP',
        physical_Lorentz_quantum_covariance_or_normalized_soft_Pauli_completed=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='exact symbolic local rescaling cancellation plus binary actual source restriction; entry coefficient intervals are diagnostics, no outward action/locality/continuum or observable bound')
    (out/'result.json').write_text(json.dumps(r,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=r['classification'],records=rows,archive=r['archive'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    print(json.dumps(materialize(p.parse_args().output),sort_keys=True))
