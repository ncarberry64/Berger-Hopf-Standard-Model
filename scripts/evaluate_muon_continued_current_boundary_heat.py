"""Apply the retained-domain heat/current return and both magnetic contacts."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_continued_current_boundary_heat import (
    joined_magnetic_heat_inputs,spectral_action_factor,boundary_regulated_current,
    magnetic_boundary_return,boundary_resolvent_schur)
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(output, *, input_folder=Path('artifacts/muon_continued_current_factor_20261011/run_1'),
                refinements=(16,32), cutoff_probe=1.0329133712274834e-11):
    out=ROOT/output;folder=ROOT/input_folder
    if out.exists():raise FileExistsError('preserve earlier continued-domain heat contacts')
    md=json.loads((folder/'result.json').read_bytes());refs=dict(md['input_hashes'])
    refs[(folder/'result.json').relative_to(ROOT).as_posix()]=sha256((folder/'result.json').read_bytes()).hexdigest()
    records=[];pending=[];previous=None
    for steps in refinements:
        inputs=[]
        for side in ('incoming','outgoing'):
            path=folder/f'{side}_{steps}.npz';expected=md['array_archives'][path.name]['sha256']
            if sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('frozen actual coefficient changed')
            refs[path.relative_to(ROOT).as_posix()]=expected
            with np.load(path,allow_pickle=False)as a:inputs.append({k:a[k].copy()for k in a.files})
        Y=float(inputs[0]['family_Y'][1]);data=joined_magnetic_heat_inputs(*inputs,Y=Y)
        print(json.dumps(dict(stage='canonical_Gram_squared_factor',steps_per_arm=steps,actual_fixed_Y=Y)),flush=True)
        source=spectral_action_factor(data['source_A'],data['weights'],6)
        target=spectral_action_factor(data['target_A'],data['weights'],24)
        arrays=dict(source_eigenvalues=source['eigenvalues'],target_eigenvalues=target['eigenvalues'],
            proper_cell_weights=data['weights'],actual_fixed_Y=np.array(Y),
            current_target=data['literal_current_target'],source_right=data['source_R'])
        checks=[]
        for c,label in ((0.,'c0'),(cutoff_probe,'cprobe')):
            current=boundary_regulated_current(source,data['source_R'],data['literal_current_target'],c=c,dimension=6)
            for key,value in current.items():arrays[label+'_'+key]=value
            for axis in range(3):
                mag=magnetic_boundary_return(source,target,data['source_R'],
                    data['magnetic_forward'][axis],data['magnetic_reverse'][axis],
                    c=c,source_dimension=6,target_dimension=24)
                for key in ('response','square_contact','numerator_contact','c0_direct_inverse_derivative',
                            'Dirichlet_reference_response','boundary_return_response'):
                    arrays[f'{label}_magnetic_{axis}_'+key]=mag[key]
                # These source-rate/current maps are held at the SAME fixed
                # geometry.  No geometry Gram/source motion is dropped by
                # renaming this as a total branch derivative.
                checks.append(dict(cutoff_probe=c,source_axis=axis,
                    magnetic_response_norm=float(np.linalg.norm(mag['response'])),
                    square_contact_norm=float(np.linalg.norm(mag['square_contact'])),
                    numerator_contact_norm=float(np.linalg.norm(mag['numerator_contact'])),
                    magnetic_boundary_return_norm=float(np.linalg.norm(mag['boundary_return_response'])),
                    magnetic_Dirichlet_reference_norm=float(np.linalg.norm(mag['Dirichlet_reference_response'])),
                    c0_inverse_derivative_difference=None if c else float(np.max(abs(mag['response']-mag['c0_direct_inverse_derivative'])))))
        arrays['spectral_boundary_Schur_c0']=boundary_resolvent_schur(source,0.,dimension=6)
        arrays['spectral_boundary_Schur_minus_inverse_cutoff']=boundary_resolvent_schur(source,-1/cutoff_probe,dimension=6)
        curr=arrays['cprobe_current_full'];row=dict(steps_per_arm=steps,cutoff_probe=cutoff_probe,
            fixed_muon_Y=Y,source_lowest_squared_eigenvalue=float(source['eigenvalues'][0]),
            target_lowest_squared_eigenvalue=float(target['eigenvalues'][0]),
            source_variable_Gram_identity_max=source['variable_Gram_identity_max'],
            target_variable_Gram_identity_max=target['variable_Gram_identity_max'],
            source_Hermitian_rounding_max=source['hermitian_rounding_max'],
            target_Hermitian_rounding_max=target['hermitian_rounding_max'],
            c0_current_norm=float(np.linalg.norm(arrays['c0_current_full'])),
            regulated_current_norm=float(np.linalg.norm(curr)),
            regulated_Dirichlet_reference_current_norm=float(np.linalg.norm(arrays['cprobe_current_Dirichlet_reference'])),
            regulated_boundary_return_current_norm=float(np.linalg.norm(arrays['cprobe_current_boundary_return'])),
            frequency_boundary_Schur_change_norm=float(np.linalg.norm(arrays['spectral_boundary_Schur_minus_inverse_cutoff']-arrays['spectral_boundary_Schur_c0'])),
            regulated_current_refinement_difference=None if previous is None else float(np.linalg.norm(curr-previous)),
            magnetic_contacts=checks)
        previous=curr;records.append(row);pending.append((f'joined_{steps}.npz',arrays))
        print(json.dumps(dict(stage='continued_current_boundary_heat_applied',**row),sort_keys=True),flush=True)
    for p in ('src/bhsm/interface/muon_continued_current_boundary_heat.py','tests/test_muon_continued_current_boundary_heat.py',
              Path(__file__).relative_to(ROOT).as_posix()):refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed action changed')
    out.mkdir(parents=True);files={}
    for name,arrays in pending:
        path=out/name;_compressed_npz(path,arrays)
        files[name]=dict(bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest())
    result=dict(classification='EVALUATED_CONTINUED_CANONICAL_CURRENT_RELATIVE_DOMAIN_HEAT_AND_MAGNETIC_CONTACTS',
        input_hashes=refs,array_archives=files,records=records,
        canonical_variable_Gram='exact piecewise-linear temporal L2 with actual proper-clock cell weights; initial coordinate zero, final free',
        source_test_Gram='piecewise-constant residual-test proper-clock cell weights',
        generalized_square='P=M^-1/2 A†G A M^-1/2; stiffness K is not heated without M',
        relative_domain='full mixed first-order-adjoint domain minus additional final-Dirichlet reference on SAME K,M',
        spectral_return='K-zM Schur including offdiagonal measure; finite-c return computed spectrally, not fromS(0)',
        magnetic_contact='dK10=dA01†G0A0+A1†G1dA10; source numerator dA01†G0R retained; c0 cancels to actual first-order inverse derivative',
        actual_source_axes=[0,1,2],actual_fixed_middle_family_Y=True,
        variable_Gram_first_direction_zero_scope='actual odd magnetic gauge/H direction at fixed even geometry; not total branch motion',
        common_birth_frame_scope='represented homogeneous canonical T=I with one shared birth trace; global F_B/U not selected here',
        cutoff_scope='explicit retained numerical probe coordinate; no physical c=I/R or gamma selected',
        real_Euclidean_sectorial_contour_deformation_proved=False,
        full_stratified_relative_exterior_or_log_phase_completed=False,
        complete_L2_L3_quantum_loop_or_Pauli_completed=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 generalized spectral applications, c0 cancellations and temporal refinements; no eigensolver, coefficient, continuum, contour, exterior, or physical Pauli certificate')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--refinements',type=int,nargs='+',default=[16,32])
    p.add_argument('--cutoff-probe',type=float,default=1.0329133712274834e-11)
    a=p.parse_args();print(json.dumps(materialize(a.output,refinements=tuple(a.refinements),cutoff_probe=a.cutoff_probe),sort_keys=True))
