"""Enrich actual changing-current products before the same coupled Green."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_source_directed_temporal_green import source_directed_temporal_exchange
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output,*,reference_directory,quadrature_order=12,cutoff=1e-11):
    out=Path(output);out=out if out.is_absolute()else ROOT/out
    if out.exists():raise FileExistsError('preserve earlier source-image applications')
    folder=Path(reference_directory);folder=folder if folder.is_absolute()else ROOT/folder
    original=(folder/'result.json').read_bytes();receipt=json.loads(original)
    if receipt['classification']!='EVALUATED_CHANGING_COUPLED_FIELD_FERMION_OPEN_EXCHANGE':raise ValueError('same changing source/field reference required')
    refs=dict(receipt['input_hashes']);refs[(folder/'result.json').relative_to(ROOT).as_posix()]=sha256(original).hexdigest()
    for path,h in refs.items():
        if sha256((ROOT/path).read_bytes()).hexdigest()!=h:raise ValueError('consumed owner changed: '+path)
    out.mkdir(parents=True);angular=retained_full_q_angular_space(ROOT);files={};rows=[]
    for side in ('incoming','outgoing'):
        phase=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'else'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
        refs.update(phase['input_hashes']);data={};modes=[]
        for name in ('result','field_modes_0','field_modes_1'):
            path=folder/(side+'_'+name+'.npz');raw=path.read_bytes();h=sha256(raw).hexdigest()
            if h!=receipt['array_archives'][path.name]['sha256']:raise ValueError('changing reference arrays changed')
            refs[path.relative_to(ROOT).as_posix()]=h
            with np.load(path,allow_pickle=False)as z:
                if name=='result':data={k:z[k].copy()for k in z.files}
                else:modes.append(z['field_Gram_orthonormal_eigenvectors'].copy())
        UB=np.concatenate(modes,axis=1);L=abs(phase['receipt']['span'])
        app=source_directed_temporal_exchange(phase,angular,data['field_generalized_eigenvalues'],UB,length=L,
            quadrature_order=quadrature_order,cutoff=cutoff,progress=lambda r:print(json.dumps(dict(side=side,stage='complete_invariant_fermion_block',**r),sort_keys=True),flush=True))
        arrays={k:app[k]for k in ('signed_gaussian_open_exchange','source_projection_residual_norm_squared','source_norm_squared',
            'source_temporal_Gram','source_temporal_congruence','chronological_quadrature_times','chronological_quadrature_weights')}
        for j,values in enumerate(app['block_forms']):
            name=side+'_block_'+str(j)+'.npz';path=out/name;deterministic_archive(path,{**values,'eigenvalues':app['block_eigenvalues'][j]})
            files[name]=dict(bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest())
        path=out/(side+'_result.npz');deterministic_archive(path,arrays);files[path.name]=dict(bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest())
        row={k:app[k]for k in ('source_projection_relative_norm','independent_scalar_projection_relative_norm','external_tent_Gram',
            'temporal_Gram_condition','temporal_basis_count','total_fermion_FE_dimension','maximum_invariant_block_dimension','block_records',
            'spectator_off_block_max','complex_frame_unitary_residual','common_kernel_approximation_upper')}
        row.update(side=side,signed_gaussian_open_exchange_norm=float(np.linalg.norm(app['signed_gaussian_open_exchange'])),
            signed_gaussian_open_exchange_Hermitian_defect=float(np.linalg.norm(app['signed_gaussian_open_exchange']-app['signed_gaussian_open_exchange'].conj().T)),
            reference_open_exchange_difference_norm=float(np.linalg.norm(app['signed_gaussian_open_exchange']-data['signed_gaussian_open_exchange'])))
        rows.append(row);print(json.dumps(dict(stage='source_enrichment_completed',**row),sort_keys=True),flush=True)
        del app,data,UB,modes
    for p in ('src/bhsm/interface/muon_source_directed_temporal_green.py',Path(__file__).relative_to(ROOT).as_posix()):refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('source/operator changed')
    if any(r['bytes']>10*1024**2 for r in files.values()):raise ValueError('lossless archive exceeds publication threshold')
    result=dict(classification='EVALUATED_SOURCE_DIRECTED_CHANGING_TEMPORAL_OPEN_EXCHANGE',input_hashes=refs,numerical_files=files,records=rows,
        action_parameters=receipt['action_parameters'],common_probe_cutoff=float(cutoff),source_quadrature_order=quadrature_order,
        field_quadrature_scope='same preserved complete1200 coupled field form at its original order6; new source and fermion weak moments at declared refined order',
        source_temporal_trial='b*P_k(2u/L-1), k0..6, plus b²; all true weak coordinate rates; no rank/spectrum deletion',
        exact_reductions='fixed diagonal family Y and complete complex-Wigner spectator blocks; full odd20 times18 retained',
        normalization='Y_h/sqrt(V), external constant1/sqrt(V), external b normalized in same Ndt; no extra V/e factor',
        operator='A=partial_t/N+Omega_tau+W; source right (AV)^dagger deltaA precedes inverse; literal non-Hermitian source left retained',
        quantum_scope='formal Gaussian sign -1 component on declared positive product/ADM reference; adopted P_strat mixed completion/LSZ/physical Wick identity not asserted',
        exact_polynomial_ghost_and_affine_H_products_in_trial=True,variable_coefficient_source_closure_claimed=False,
        one_coupled_field_Green=True,numerical_rank_or_small_mode_deletion=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 coefficient-time source/weak integration and Gram/eigen application; projection is an evaluated coordinate source norm, not a paired observable or continuum bound. Upstream assembly/eigen and physical matching errors remain separate.')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],records=rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--reference-directory',type=Path,default='artifacts/muon_changing_coupled_open_current_20261011/run_1')
    p.add_argument('--quadrature-order',type=int,default=12);p.add_argument('--cutoff',type=float,default=1e-11)
    a=p.parse_args();print(json.dumps(materialize(a.output,reference_directory=a.reference_directory,quadrature_order=a.quadrature_order,cutoff=a.cutoff),sort_keys=True))
