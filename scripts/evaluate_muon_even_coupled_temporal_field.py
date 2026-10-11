"""Evaluate complete even2100 image of the same changing coupled action."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_even_coupled_temporal_field import changing_even_coupled_field_application
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output,*,quadrature_order=6):
    out=Path(output);out=out if out.is_absolute()else ROOT/out
    if out.exists():raise FileExistsError('preserve prior angular-image applications')
    source=ROOT/'artifacts/muon_corrected_profile_magnetic_response_20261011/run_1';raw=(source/'result.json').read_bytes();receipt=json.loads(raw)
    refs=dict(receipt['input_hashes']);refs[(source/'result.json').relative_to(ROOT).as_posix()]=sha256(raw).hexdigest()
    angular_odd_n3=np.arange(4,20);files={};records=[];out.mkdir(parents=True)
    for side in ('incoming','outgoing'):
        path=source/(side+'_contacts.npz');h=sha256(path.read_bytes()).hexdigest()
        if h!=receipt['array_archives'][path.name]['sha256']:raise ValueError('retained source support arrays changed')
        refs[path.relative_to(ROOT).as_posix()]=h
        with np.load(path,allow_pickle=False)as a:
            H=a['intrinsic_H_response'].reshape(-1,4,20,8);Q=a['source_trace'].reshape(-1,5,4,20,8)
            if np.any(H[:,:,angular_odd_n3])or np.any(Q[:,:,:,angular_odd_n3]):raise ValueError('nonzero source n3 requires additional even n6; cannot compress')
        phase=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'else'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
        refs.update(phase['input_hashes'])
        app=changing_even_coupled_field_application(phase,length=abs(phase['receipt']['span']),quadrature_order=quadrature_order,
            progress=lambda r:print(json.dumps(dict(stage='complete_even_coupled_block',side=side,**r),sort_keys=True),flush=True))
        for j,block in enumerate(app['block_arrays']):
            # Complete arrays are split by purpose, not removed or rounded.
            groups={name:{k:block[k]for k in keys}for name,keys in dict(
                action=('field_indices','harmonic_indices','coupled_action_Hessian','coupled_action_Gram','one_form_curvature_contact','intrinsic_scalar_complete_Hessian'),
                green=('normalized_operator','normalized_inverse','coupled_action_Green','generalized_eigenvalues','Gram_orthonormal_eigenvectors'),
                hilbert=('one_form_Gram_per_kappa','ghost_Gram_per_kappa','weak_Lorenz_map')).items()}
            for name,values in groups.items():
                p=out/(side+'_block_'+str(j)+'_'+name+'.npz');deterministic_archive(p,values)
                if p.stat().st_size>10*1024**2:raise ValueError('lossless block exceeds publication threshold')
                files[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
        p=out/(side+'_samples.npz');deterministic_archive(p,{k:app[k]for k in ('chronological_samples','quadrature_times','quadrature_weights')});files[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
        records.append(dict(side=side,block_records=app['block_records'],off_block_derivative_max=app['off_block_derivative_max']))
        del app
    for p in ('src/bhsm/interface/muon_even_coupled_temporal_field.py','src/bhsm/interface/muon_coupled_field_angular_images.py','src/bhsm/interface/muon_coupled_higgs_magnetic_source.py',Path(__file__).relative_to(ROOT).as_posix()):refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed source/action changed')
    result=dict(classification='EVALUATED_COMPLETE_EVEN_CHANGING_COUPLED_FIELD_GREEN',input_hashes=refs,numerical_files=files,records=records,
        action_parameters=phase['receipt']['action_parameters'],quadrature_order=quadrature_order,
        full_field_count=2100,full_even_harmonics=35,angular_image='n1 magnetic source times odd n1+n3 reaches complete n0+n2+n4; n3 source allzero checked before this restriction',
        exact_reduction='real |k| Wigner spectators of the homogeneous angular body; entire2100 rows retained; gauge/H/DG sectors composed before inversion',
        geometry_clock='same chronological x-linear/vy-midpoint saved phase; child inherited value/time/radial image counted once',
        paired_DG_scalar_and_Hdot_images_retained=True,literal_YM_curvature_and_offshell_DH_contacts_retained=True,
        Lorenz_fixing='complete integrated one-form/ghost Gram map; no Rxi scalar mass',
        physical_P_strat_BRST_statistics_or_Wick_identification=False,physical_LSZ_or_Pauli_completed=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 coefficient-time/radial weak integration and inverse/eigen diagnostics; stored Neumann arithmetic does not enclose source producer/eigen/continuum errors or physical matching')
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],records=records)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--quadrature-order',type=int,default=6)
    a=p.parse_args();print(json.dumps(materialize(a.output,quadrature_order=a.quadrature_order),sort_keys=True))
