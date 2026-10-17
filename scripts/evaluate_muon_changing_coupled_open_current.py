"""Apply both changing-phase finite Green factors to literal open vertices."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_changing_coupled_open_current import changing_coupled_open_current_application
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output,*,field_directory,cutoff=1e-11):
    out=Path(output);out=out if out.is_absolute()else ROOT/out
    if out.exists():raise FileExistsError('preserve all prior mixed applications')
    folder=Path(field_directory);folder=folder if folder.is_absolute()else ROOT/folder
    receipt=json.loads((folder/'result.json').read_bytes())
    if receipt['classification']!='EVALUATED_CHANGING_SAME_PHASE_COUPLED_GAUGE_HIGGS_FIELD_GREEN_AND_CANONICAL_CURRENT':raise ValueError('same changing coupled field application required')
    refs=dict(receipt['input_hashes']);p=(folder/'result.json').relative_to(ROOT).as_posix();refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    for p,h in refs.items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed owner changed: '+p)
    angular=retained_full_q_angular_space(ROOT);files={};rows=[];out.mkdir(parents=True)
    for side in ('incoming','outgoing'):
        phase=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'else'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
        refs.update(phase['input_hashes']);r=next(r for r in receipt['records']if r['side']==side)
        if receipt['action_parameters']!=phase['receipt']['action_parameters']:raise ValueError('same assigned action member required')
        arrays={}
        for name in ('action','hilbert'):
            path=folder/(side+'_'+name+'.npz');entry=receipt['numerical_files'][path.name]
            raw=path.read_bytes();h=sha256(raw).hexdigest()
            if h!=entry['sha256']:raise ValueError('coupled field numeric data changed')
            refs[path.relative_to(ROOT).as_posix()]=h
            with np.load(path,allow_pickle=False)as a:arrays.update({k:a[k].copy()for k in a.files})
        print(json.dumps(dict(stage='changing_full18_source_adjoint_and_two_Greens',side=side),sort_keys=True),flush=True)
        a=changing_coupled_open_current_application(phase,angular,arrays['coupled_action_Hessian'],arrays['coupled_action_Gram'],
            length=r['length'],quadrature_order=r['quadrature_order'],cutoff=cutoff)
        groups=dict(fermion_form={k:a[k]for k in('fermion_weak_form','fermion_proper_time_Gram','fermion_normalized_operator',
            'fermion_generalized_eigenvalues','fermion_Gram_orthonormal_eigenvectors')},
            result={k:a[k]for k in('signed_gaussian_open_exchange','source_projection_residual_norm_squared','source_norm_squared','chronological_quadrature_samples','field_generalized_eigenvalues')})
        for j in range(2):
            groups['field_modes_'+str(j)]=dict(field_Gram_orthonormal_eigenvectors=a['field_Gram_orthonormal_eigenvectors'][:,600*j:600*(j+1)],column_indices=np.arange(600*j,600*(j+1)))
            groups['source_'+str(j)]=dict(literal_left_vertex_map=a['literal_left_vertex_map'][:,360*j:360*(j+1)],
                source_adjoint_right_vertex_map=a['source_adjoint_right_vertex_map'][360*j:360*(j+1)],
                source_value_projection_map=a['source_value_projection_map'][360*j:360*(j+1)])
        for name,values in groups.items():
            path=out/(side+'_'+name+'.npz');deterministic_archive(path,values)
            if path.stat().st_size>10*1024**2:raise ValueError('complete lossless source archive exceeds publication threshold: '+path.name)
            files[path.name]=dict(bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest(),arrays=sorted(values))
        row=dict(side=side,cutoff=float(cutoff),external_tent_Gram=a['external_tent_Gram'],
            signed_gaussian_open_exchange_norm=float(np.linalg.norm(a['signed_gaussian_open_exchange'])),
            signed_gaussian_open_exchange_Hermitian_defect=float(np.linalg.norm(a['signed_gaussian_open_exchange']-a['signed_gaussian_open_exchange'].conj().T)),
            fermion_minimum_generalized_eigenvalue=float(a['fermion_generalized_eigenvalues'][0]),
            field_minimum_generalized_eigenvalue=float(a['field_generalized_eigenvalues'][0]),
            source_projection_relative_norm=a['source_projection_relative_norm'],
            independent_scalar_source_projection_relative_norm=a['independent_scalar_source_projection_relative_norm'],
            common_kernel_approximation_upper=a['common_kernel_approximation_upper'],
            fermion_generalized_eigen_residual=a['fermion_generalized_eigen_residual'],
            field_generalized_eigen_residual=a['field_generalized_eigen_residual'],
            normalized_fermion_symmetry_defect=a['normalized_fermion_symmetry_defect'])
        rows.append(row);print(json.dumps(dict(stage='changing_open_exchange_completed',**row),sort_keys=True),flush=True)
        del a,arrays
    names=('muon_changing_coupled_open_current','muon_corrected_profile_magnetic_response','muon_profile_preserving_phase_sample',
        'muon_parent_positive_coupled_field','muon_parent_positive_coupled_temporal','muon_parent_positive_brst_ghost',
        'muon_magnetic_open_lepton_vertex','muon_native_dirac_hamiltonian','muon_intrinsic_scalar_temporal_image',
        'muon_common_cutoff_green_kernel','muon_intrinsic_scalar_regulator_correction')
    for name in names:
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    for p in(Path(__file__).relative_to(ROOT).as_posix(),'scripts/evaluate_muon_reached_trace_action.py'):
        refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed action/operator changed')
    result=dict(classification='EVALUATED_CHANGING_COUPLED_FIELD_FERMION_OPEN_EXCHANGE',input_hashes=refs,array_archives=files,records=rows,
        action_parameters=receipt['action_parameters'],common_cutoff=float(cutoff),physical_cutoff_selected=False,
        temporal_trial='SAME piecewise-linear Dirichlet tent b as changing1200 field; internal fermion Span{b,b²}, bprime/2bbprime retained',
        angular_basis='full odd n1+n3 20 harmonics times all18 components (360); modesY/sqrt(V), external constant1/sqrt(V)',
        external_time_pairing='external b/sqrt(int N b²), common proper Ndt measure once',
        factor='A=partial_t/N+Omega_tau+W, actual coefficient-time weak integration; no separate -Wtau subtraction',
        source_right='int Ndt (A V)^dagger deltaA_field b_external; source adjoint acts before fermion inverse',
        source_left='literal int Ndt b_external deltaA_field V; temporal gauge anti-Hermitian vertex is not replaced by its adjoint',
        temporal_gauge_vertex='G/N in positive A; distinct from Lorentz Hcan -iG/N',
        quantum_algebra_scope='formal Gaussian open exchange sign -1 on the declared first-order-factor/real-field finite reference; not assigned full P_strat mixed-square/statistics completion',
        two_Green_kernel='ONE coupled1200 gauge-H field generalized spectrum and full720 fermion FE spectrum; common total-time L2 kernel applied before contraction',
        inherited_profile_value_time_radial_and_chronological_rates_retained=True,
        independent_scalar_b_times_b_source_in_trial_exact=True,
        gauge_DG_products_and_variable_coefficients_not_claimed_temporal_image_closed=True,
        actual_magnetic_derivative_applied=False,external_LSZ_or_normalized_soft_Pauli_completed=False,
        complete_P_strat_BRST_relative_statistics_or_physical_Wick_identity=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='Binary64 actual coefficient-time weak/source integration, Gram/eigen normalization and finite common-cutoff kernel. Temporal source projection remainder is evaluated, not a readout/continuum bound. Kernel algebraic truncation bound excludes entry/eigen/assembly rounding; no physical anomaly enclosure.')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],records=rows,array_archives=files)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--field-directory',type=Path,default='artifacts/muon_parent_positive_coupled_temporal_20261011/run_1');p.add_argument('--cutoff',type=float,default=1e-11)
    a=p.parse_args();print(json.dumps(materialize(a.output,field_directory=a.field_directory,cutoff=a.cutoff),sort_keys=True))
