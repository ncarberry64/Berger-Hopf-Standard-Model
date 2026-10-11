"""Apply the continued current factor on the actual inherited phase."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_continued_current_factor import continued_current_coefficients,squared_current_inverse
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_coupled_magnetic_field_variation import corrected_magnetic_first_field_interpolation
from bhsm.interface.muon_changing_magnetic_current_jets import magnetic_current_angular_images
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def retained_input(side,refs):
    folder=ROOT/'artifacts/muon_corrected_profile_magnetic_response_20261011/run_1'
    p=folder/'result.json';md=json.loads(p.read_bytes());refs.update(md['input_hashes'])
    refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest();arrays=[]
    for stem in('primal_and_source','phase','velocity','contacts'):
        p=folder/(side+'_'+stem+'.npz');h=md['array_archives'][p.name]['sha256']
        if sha256(p.read_bytes()).hexdigest()!=h:raise ValueError('actual source/response changed')
        refs[p.relative_to(ROOT).as_posix()]=h
        with np.load(p,allow_pickle=False)as a:arrays.append({k:a[k].copy()for k in a.files})
    phase=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'
        if side=='incoming'else'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
    refs.update(phase['input_hashes'])
    return phase,corrected_magnetic_first_field_interpolation(*arrays)


def materialize(output,*,refinements=(16,32,64)):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve earlier current applications')
    refs={};files={};records=[];pending=[]
    derivative=magnetic_current_angular_images()['derivatives']['field_odd'][:,:4,:4]
    for side in('incoming','outgoing'):
        phase,sampler=retained_input(side,refs);previous=None
        for steps in refinements:
            c=continued_current_coefficients(phase,steps,first_field_sampler=sampler)
            # Y0 is a Taylor operator coefficient on the actual fixed fields,
            # not a physical H=0 or a selected massless fermion state.
            a=squared_current_inverse(c,0.,c['source_right_map'],c['target_left_map'])
            arrays={k:v for k,v in c.items()if isinstance(v,np.ndarray)}
            arrays.update({k:v for k,v in a.items()if isinstance(v,np.ndarray)})
            arrays['n1_right_body_derivatives']=derivative
            # n1<-n0 angular insertion and literal reverse, spin-major order.
            for degree in(0,1):
                xi=c['magnetic_Xi'+str(degree)][:,:3,:4]
                arrays['magnetic_right_Y'+str(degree)]=xi.transpose(0,1,3,2,4).reshape(steps,3,24,6)
                arrays['magnetic_left_Y'+str(degree)]=xi.transpose(0,1,3,4,2).reshape(steps,3,6,24)
            name=f'{side}_{steps}.npz';pending.append((name,arrays))
            r=dict(side=side,steps=steps,family_reconstruction_max=c['family_reconstruction_max'],
                inverse_identity_max=a['inverse_identity_max'],
                first_order_residual_max=a['first_order_residual_max'],
                squared_original_residual_max=a['squared_original_residual_max'],
                squared_variational_residual_max=a['squared_variational_residual_max'],
                current_adjoint_pairing_max=a['current_adjoint_pairing_max'],
                actual_free_final_value_norm=float(np.linalg.norm(a['actual_free_final_value'])),
                literal_current_contraction_norm=float(np.linalg.norm(a['literal_left_current_contraction'])),
                current_refinement_difference=None if previous is None else float(np.linalg.norm(a['literal_left_current_contraction']-previous)),
                magnetic_Xi0_norm=float(np.linalg.norm(c['magnetic_Xi0'])),magnetic_Xi1_norm=float(np.linalg.norm(c['magnetic_Xi1'])))
            previous=a['literal_left_current_contraction'];records.append(r)
            print(json.dumps(dict(stage='same_domain_continued_current_factor',**r),sort_keys=True),flush=True)
    for name in('muon_continued_current_factor','muon_intrinsic_fermion_wick_application',
                'muon_coupled_magnetic_field_variation','muon_changing_magnetic_current_jets'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed source changed')
    out.mkdir(parents=True)
    for name,arrays in pending:
        p=out/name;_compressed_npz(p,arrays);files[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    result=dict(classification='EVALUATED_ACTUAL_CONTINUED_C6_CURRENT_FACTOR_AND_CANONICAL_MAGNETIC_Y_COEFFICIENTS',
        input_hashes=refs,array_archives=files,records=records,
        chronological_orientation='incoming numerical past to birth; outgoing birth to future',
        contour='tau=i*(t-t0); continued A_E=-canonical D_L',
        common_family_coefficients='exact LR-grading Y0 and unit-Y Hermitian LR mass Y1 on fixed actual H/gauge/geometry',
        magnetic_Xi_kind='canonical delta H_can, with temporal -i G/N and fixed-Y scalar vertex; positive-factor At G/N not reused',
        magnetic_source_axes=[0,1,2],magnetic_charge_added_again=False,
        current_source='actual unit-coupling temporal EM generator -Q; constant coefficient source basis, no external pole/state or physical drive selected',
        domain='inhomogeneous first-order initial-zero inverse; final trace free and adjoint-generated final squared row retained',
        common_current_Gram='unit C6 canonical current; proper-clock residual-test Gram h*N; unit-Haar constant normalization already in coefficient basis',
        squared_factor='K=A†G_source A on this SAME finite domain; K^-1 A†G_source R=A^-1 R',
        finite_c_native_regulator_or_relative_completion_identified=False,
        angular_magnetic_source_image='exact retained n1 coefficients from actual first response, full20 source entries preserved; n1<-n0 and reverse exported separately',
        physical_external_shell_or_LSZ_or_Pauli_completed=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 profile-bound first-order/squared inverse identity and source dual/refinement diagnostics; no temporal continuum, native exterior/relative-domain, finite-c, or physical uncertainty certificate')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--refinements',type=int,nargs='+',default=[16,32,64]);a=p.parse_args()
    print(json.dumps(materialize(a.output,refinements=tuple(a.refinements)),sort_keys=True))
