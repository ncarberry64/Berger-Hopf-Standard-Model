"""Apply corrected magnetic source to both changing Gaussian current legs."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
from scipy.linalg import cholesky,eigh,solve_triangular

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_changing_magnetic_open_exchange import changing_magnetic_constant_columns
from bhsm.interface.muon_changing_magnetic_current_jets import magnetic_current_angular_images
from bhsm.interface.muon_coupled_magnetic_field_variation import corrected_magnetic_first_field_interpolation
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_source_directed_temporal_green import invariant_source_blocks
from bhsm.interface.muon_even_source_temporal_fermion import complete_even_fermion_blocks
from bhsm.interface.muon_magnetic_n5_return_fermion import n5_return_angular_blocks
from bhsm.interface.muon_even_coupled_temporal_field import complete_even_angular_blocks
from evaluate_muon_reached_trace_action import deterministic_archive


def retained_inputs(side,refs,*,repository=ROOT):
    folders={k:repository/'artifacts'/v for k,v in dict(
        source='muon_corrected_profile_magnetic_response_20261011/run_1',
        variation='muon_coupled_magnetic_field_variation_20261011/run_1',
        odd_field='muon_parent_positive_coupled_temporal_20261011/run_1',
        even_field='muon_even_coupled_temporal_field_20261011/run_3',
        odd_f='muon_source_directed_temporal_green_20261011/run_1',
        even_f='muon_even_source_temporal_fermion_20261011/run_1',
        n5_f='muon_magnetic_n5_return_fermion_20261011/run_1').items()}
    receipts={}
    for k,f in folders.items():
        p=f/'result.json';raw=p.read_bytes();r=json.loads(raw);receipts[k]=r
        refs[p.relative_to(repository).as_posix()]=sha256(raw).hexdigest();refs.update(r['input_hashes'])
    def load(k,name):
        p=folders[k]/name;raw=p.read_bytes();record=receipts[k].get('array_archives',receipts[k].get('numerical_files'))[name]
        if sha256(raw).hexdigest()!=record['sha256']or len(raw)!=record['bytes']:raise ValueError('retained action/source array changed: '+str(p))
        refs[p.relative_to(repository).as_posix()]=record['sha256']
        with np.load(p,allow_pickle=False)as a:return{key:a[key].copy()for key in a.files}
    source=[load('source',side+'_'+p+'.npz')for p in('primal_and_source','phase','velocity','contacts')]
    sampler=corrected_magnetic_first_field_interpolation(*source)
    phase=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'else'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
    refs.update(phase['input_hashes']);images=magnetic_current_angular_images()
    angular=retained_full_q_angular_space(repository);odd=invariant_source_blocks(angular)
    even=complete_even_fermion_blocks();n5=n5_return_angular_blocks();F=[]
    for family,fi in enumerate(odd['family_indices']):
        for k,b in enumerate(odd['angular_blocks']):
            a=load('odd_f',side+'_block_'+str(6*family+k)+'.npz');hi=b['harmonic_indices'];U=np.zeros((len(hi),56),complex);U[:,:20]=odd['real_to_complex'][hi]
            F.append(dict(name='odd_'+str(6*family+k),family=family,family_indices=fi,parity='odd',
                level=b['level'],spectator=b['spectator'],harmonic_indices=hi,
                derivatives=odd['complex_derivatives'][:,hi][:,:,hi],real_to_complex=U,eigenvalues=a['eigenvalues'],eigenvectors=a['eigenvectors']))
        for k,b in enumerate(even['angular_blocks']):
            a=load('even_f',side+'_block_'+str(9*family+k)+'.npz');hi=b['harmonic_indices']
            F.append(dict(name='even_'+str(9*family+k),family=family,family_indices=fi,parity='even',
                level=b['level'],spectator=b['spectator'],harmonic_indices=hi,
                derivatives=even['complex_derivatives'][:,hi][:,:,hi],real_to_complex=even['real_to_complex'][hi],
                eigenvalues=a['generalized_eigenvalues'],eigenvectors=a['eigenvectors']))
        for k,b in enumerate(n5['angular_blocks']):
            a=load('n5_f',side+'_block_'+str(6*family+k)+'.npz');hi=b['harmonic_indices'];U=np.zeros((len(hi),56),complex);U[:,20:]=n5['real_to_complex'][hi]
            F.append(dict(name='n5_'+str(6*family+k),family=family,family_indices=fi,parity='odd',
                level=5,spectator=k,harmonic_indices=20+hi,derivatives=n5['complex_derivatives'][:,hi][:,:,hi],
                real_to_complex=U,eigenvalues=a['generalized_eigenvalues'],eigenvectors=a['eigenvectors']))
    field=[];odd_a=load('odd_field',side+'_action.npz');odd_h=load('odd_field',side+'_hilbert.npz')
    labels=angular['harmonic_labels'];mask=np.ones((1200,1200),bool)
    for n,ks in((1,(1,)),(3,(1,3))):
        for ak in ks:
            hi=np.array([i for i,l in enumerate(labels)if l[0]==n and abs(l[2])==ak]);ids=(np.arange(60)[:,None]*20+hi).ravel();mask[np.ix_(ids,ids)]=False
            K=odd_a['coupled_action_Hessian'][np.ix_(ids,ids)];G=odd_h['coupled_action_Gram'][np.ix_(ids,ids)]
            C=cholesky(G,lower=True);P=solve_triangular(C,K,lower=True);P=solve_triangular(C,P.T,lower=True).T
            ev,V=eigh(P);U=solve_triangular(C.T,V,lower=False)
            if ev[0]<=0:raise ArithmeticError('same odd field block not positive; no shift')
            field.append(dict(name='odd_n'+str(n)+'_k'+str(ak),parity='odd',level=n,absolute_spectator=ak,
                harmonic_indices=hi,field_indices=ids,eigenvalues=ev,eigenvectors=U,
                generalized_eigen_residual=float(np.linalg.norm(K@U-(G@U)*ev)/np.linalg.norm(K@U))))
    if np.any(odd_a['coupled_action_Hessian'][mask])or np.any(odd_h['coupled_action_Gram'][mask]):
        raise ValueError('same odd field form violates its exact real spectator restriction')
    even_b=complete_even_angular_blocks()
    for j,b in enumerate(even_b['blocks']):
        a=load('even_field',side+'_block_'+str(j)+'_green.npz')
        field.append(dict(name='even_'+str(j),parity='even',level=b['level'],absolute_spectator=b['absolute_spectator'],
            harmonic_indices=b['harmonic_indices'],field_indices=b['field_indices'],eigenvalues=a['generalized_eigenvalues'],eigenvectors=a['Gram_orthonormal_eigenvectors'],even_block=j))
    # Each complete saved variation is sliced by the two exact field blocks.
    variations={}
    def direction(target,old):
        reverse=target['parity']=='odd';e,o=(old,target)if reverse else(target,old)
        key=(e['name'],o['name'])
        if key not in variations:
            kk=[];gg=[]
            for axis in range(3):
                a=load('variation',side+'_axis_'+str(axis)+'_block_'+str(e['even_block'])+'_action.npz')
                if not np.array_equal(a['field_indices'],e['field_indices']):raise ValueError('coupled source row ordering mismatch')
                kk.append(a['coupled_delta_Hessian_even_odd'][:,o['field_indices']]);gg.append(a['coupled_delta_Gram_even_odd'][:,o['field_indices']])
            variations[key]=(np.array(kk),np.array(gg))
        a,b=variations[key]
        return(a.transpose(0,2,1),b.transpose(0,2,1))if reverse else(a,b)
    sample=load('even_f',side+'_samples.npz');old_sample=load('odd_f',side+'_result.npz');n5_sample=load('n5_f',side+'_samples.npz')
    for a in(old_sample,n5_sample):
        if not np.array_equal(a['source_temporal_congruence'],sample['source_temporal_congruence']):
            raise ValueError('same fermion temporal coordinate congruence required')
    return phase,sampler,F,field,direction,sample


def materialize(output,*,cutoff=1e-11):
    out=Path(output);out=out if out.is_absolute()else ROOT/out
    if out.exists():raise FileExistsError('preserve previous paired current applications')
    out.mkdir(parents=True);refs={};files={};records=[]
    for side in('incoming','outgoing'):
        phase,sampler,F,B,direction,sample=retained_inputs(side,refs)
        app=changing_magnetic_constant_columns(phase,sampler,F,B,direction,
            times=sample['chronological_quadrature_times'],weights=sample['chronological_quadrature_weights'],
            temporal_values=sample['temporal_basis_values'],temporal_rates=sample['temporal_basis_coordinate_rates'],cutoff=cutoff,
            progress=lambda r:print(json.dumps(dict(stage='actual_changing_magnetic_open_graph',side=side,**r),sort_keys=True),flush=True))
        for placement in('forward','reverse'):
            p=out/(side+'_'+placement+'.npz');deterministic_archive(p,app[placement]);files[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
        records.append(dict(side=side,block_records=app['block_records'],external_tent_Gram=app['external_tent_Gram'],
            forward_norm=float(np.linalg.norm(app['forward']['total'])),reverse_norm=float(np.linalg.norm(app['reverse']['total'])),
            maximum_scalar_kernel_approximation_upper=app['maximum_scalar_kernel_approximation_upper'],
            parts_forward={k:float(np.linalg.norm(v))for k,v in app['forward'].items()},parts_reverse={k:float(np.linalg.norm(v))for k,v in app['reverse'].items()}))
        del app,F,B
    for p in('src/bhsm/interface/muon_changing_magnetic_open_exchange.py','src/bhsm/interface/muon_changing_magnetic_current_jets.py',
        'tests/test_muon_changing_magnetic_open_exchange.py','tests/test_muon_changing_magnetic_current_jets.py',Path(__file__).relative_to(ROOT).as_posix()):refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same source/phase changed during paired application')
    r=dict(classification='EVALUATED_CHANGING_COMPLETE_FIELD_LOOP_MAGNETIC_CONSTANT_OPEN_COLUMNS',input_hashes=refs,numerical_files=files,records=records,
        action_parameters=phase['receipt']['action_parameters'],common_probe_cutoff=float(cutoff),external_columns='n1<-n0 72x18 and literal reverse18x72, all18 fibers and three measured-charge magnetic axes',
        all_starting_field_coordinates_retained=[1200,2100],source_directed_fermion_return_harmonics='n0/n2/n4 and n1/n3/n5, all8 independent temporal functions',
        Gaussian_statistics_sign=-1,actual_field_current_chart_motion=True,both_fermion_square_placements=True,acted_trial_numerator_contact=True,
        field_Gram_and_both_current_normalization_contacts=True,independent_sector_inverses=False,
        source_clock='same corrected chronological phase and complete saved Hermite/cubic first-field interpolation; inherited profile once',
        input_momentum_columns_evaluated=False,angular_starting_loop_complement_bound=False,physical_P_strat_Wick_LSZ_Pauli_completed=False,
        physical_a_mu=None,physical_g_mu=None,error_scope='binary64 same-phase coefficient/source and Gaussian graph integration/eigen application. Scalar kernel close-pair/series allowance is separate, not a total contraction/eigen/continuum or physical soft matching enclosure.')
    (out/'result.json').write_text(json.dumps(r,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=r['classification'],records=records)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--cutoff',type=float,default=1e-11)
    a=p.parse_args();print(json.dumps(materialize(a.output,cutoff=a.cutoff),sort_keys=True))
