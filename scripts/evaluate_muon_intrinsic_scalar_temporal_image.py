"""Execute the exact b-squared Yukawa image on frozen actual magnetic fields."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_intrinsic_scalar_temporal_image import temporal_image_source_application
from bhsm.interface.muon_magnetic_mixed_green import _mixed_vertices,mixed_green_spectral_derivative
from bhsm.interface.muon_current_source_motion_cubic import current_face_source_jets
from evaluate_muon_reached_trace_action import deterministic_archive
from evaluate_muon_intrinsic_scalar_regulator_correction import source_record


def materialize(output,*,source):
    folder=Path(source);folder=folder if folder.is_absolute() else ROOT/folder
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve previous temporal applications')
    raw=(folder/'result.json').read_bytes();md=json.loads(raw)
    if md['classification']!='EVALUATED_MAGNETIC_SOURCE_DIRECTED_INTRINSIC_HIGGS_LEPTON_MIXED_GREEN_DERIVATIVE':
        raise ValueError('same actual all-family mixed source owner required')
    hashes=dict(md['input_hashes']);hashes[(folder/'result.json').relative_to(ROOT).as_posix()]=sha256(raw).hexdigest()
    for p,h in hashes.items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed action changed: '+p)
    archives={}
    for name,info in md['array_archives'].items():
        raw=(folder/name).read_bytes()
        if len(raw)!=info['bytes'] or sha256(raw).hexdigest()!=info['sha256']:raise ValueError('consumed archive changed: '+name)
        hashes[(folder/name).relative_to(ROOT).as_posix()]=info['sha256']
        with np.load(folder/name,allow_pickle=False) as f:archives[name]={k:f[k].copy() for k in f.files}
    arrays={};rows=[];ss=archives['scalar_sources.npz'];cutoff=md['common_cutoff_probe']
    for side in ('incoming','outgoing'):
        row=next(r for r in md['records'] if r['side']==side);L=row['length']
        weights=current_face_source_jets(ss[side+'_raw_fields'][:100])['intrinsic_weights']
        lapse=float(weights['induced_lapse'].value)
        scalar={k:ss[side+'_'+k] for k in ('positive_H_odd','positive_H_even','delta_positive_H_even_odd')}
        scalar['action_Gram_scalar']=row['action_Gram_scalar'];G=ss[side+'_gaunt_even_odd_source']
        families={}
        for family in range(3):
            prefix=side+'_family_'+str(family)+'_'
            data={k[len(prefix):]:v for k,v in archives[side+'_family_'+str(family)+'_fermion_operators.npz'].items()}
            B0,B1,B1H=_mixed_vertices(G,ss[prefix+'bare_scalar_mass_vertices'])
            data.update(mixed_vertex_n0_odd=B0,mixed_vertex_n1_Hodd=B1,mixed_vertex_n1_Heven=B1H)
            original=mixed_green_spectral_derivative(data,scalar,cutoff,series_terms=md['refined_series_terms'])
            application=temporal_image_source_application(data,scalar,length=L,lapse=lapse,cutoff=cutoff)
            families[str(family)]=application
            for place in ('forward','reverse'):
                for name,value in application[place].items():
                    arrays[prefix+place+'_'+name]=value
                    old=original[place][name]
                    arrays[prefix+'original_retained_temporal_projection_'+place+'_'+name]=old
                    arrays[prefix+'temporal_enrichment_difference_'+place+'_'+name]=value-old
            t=application['temporal_image']
            for name in ('Gram','derivative_Gram','external_source_pairing','temporal_eigenvalues','temporal_eigenvectors','normalized_vertex_coefficients'):
                arrays['temporal_'+name]=t[name]
            for branch in application['branches']:
                for place in ('forward','reverse'):
                    for name,value in branch[place].items():arrays[prefix+'temporal_branch_'+str(branch['mode'])+'_'+place+'_'+name]=value
            rows.append(dict(side=side,family=family,length=L,lapse=lapse,cutoff_probe=cutoff,
                enlarged_forward_norm=float(np.linalg.norm(application['forward']['total'])),
                enlarged_reverse_norm=float(np.linalg.norm(application['reverse']['total'])),
                original_projected_forward_norm=float(np.linalg.norm(original['forward']['total'])),
                temporal_enrichment_forward_difference_norm=float(np.linalg.norm(arrays[prefix+'temporal_enrichment_difference_forward_total'])),
                component_forward_norms={name:float(np.linalg.norm(v)) for name,v in application['forward'].items()},
                exact_stored_contracted_kernel_approximation_upper=application['exact_stored_kernel_approximation_contracted_upper'],
                branch_kinetic=[b['normalized_temporal_kinetic'] for b in application['branches']],
                branch_kernel_methods=[b['kernel_methods'] for b in application['branches']],
                temporal_source_image_b_squared_exact=True,
                original_starting_scalar_domain_unchanged=True))
        for place in ('forward','reverse'):
            for name in families['1'][place]:
                value=families['1'][place][name]-families['2'][place][name]
                arrays[side+'_paired_middle_minus_light_'+place+'_'+name]=value
                old=archives['application.npz'][side+'_paired_middle_minus_light_'+place+'_'+name+'_refined']
                arrays[side+'_paired_temporal_enrichment_difference_'+place+'_'+name]=value-old
        print(json.dumps(dict(side=side,paired_temporal_enlarged_forward_norm=float(np.linalg.norm(arrays[side+'_paired_middle_minus_light_forward_total'])),
            paired_temporal_enrichment_difference_norm=float(np.linalg.norm(arrays[side+'_paired_temporal_enrichment_difference_forward_total'])),lapse=lapse),sort_keys=True),flush=True)
    source_records=[source_record(p,symbols) for p,symbols in (
        ('src/bhsm/interface/muon_intrinsic_scalar_temporal_image.py',['temporal_yukawa_source_image','temporal_image_green_kernel','temporal_image_source_application']),
        ('src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py',['action_composition_contract']),
        ('src/bhsm/interface/muon_intrinsic_higgs_positive_green.py',['intrinsic_higgs_cell_jacobi']),
    )]
    for record in source_records:hashes[record['path']]=record['sha256']
    hashes[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in hashes.items()):raise RuntimeError('consumed source changed during application')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    if (out/'application.npz').stat().st_size>10*1024**2:raise ValueError('lossless temporal result exceeds public cap')
    result=dict(classification='EVALUATED_EXACT_TEMPORAL_YUKAWA_SOURCE_IMAGE_GREEN_APPLICATION',
        input_hashes=hashes,source_records=source_records,records=rows,
        archive=dict(path='application.npz',bytes=(out/'application.npz').stat().st_size,sha256=sha256((out/'application.npz').read_bytes()).hexdigest()),
        source_image='existing scalar b times external fermion b equals internal b²; internal fermion trial span(b,b²)',
        temporal_moments=dict(Gram=[['1/3','1/4'],['1/4','1/5']],kinetic=[['4','4'],['4','16/3']],source=['1/4','1/5']),
        derivative_images='bprime and 2*b*bprime retained through exact positive kinetic moments; all mixed derivative moments vanish by reflection parity only on this constant-coefficient trial',
        scalar_trial_not_enlarged=True,complete_angular_source_images_and_all_three_fixed_Y_families=True,
        old_attached_phase_fields_preserved=True,corrected_finite_normal_phase_not_substituted=True,
        cutoff_common_to_both_arms=True,cutoff_role='same explicit numerical probe, not selected formation cutoff',
        no_fermion_state_or_Pauli_error_selected_from_source_norm=True,
        differential_temporal_domain_and_starting_full_loop_sum_completed=False,
        Gaussian_statistics_sign_or_complete_native_P_strat_claimed=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='outward exact-stored Green kernel approximation and norm-product bounds only; binary Hermite/series/contraction rounding, eigensystem/action formation, scalar/fermion differential complement, full native/relative completion/external pole/Pauli excluded')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],archive=result['archive'],records=rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--source',type=Path,default=Path('artifacts/muon_magnetic_mixed_green_20261011/run_3'))
    a=p.parse_args();print(json.dumps(materialize(a.output,source=a.source),sort_keys=True))
