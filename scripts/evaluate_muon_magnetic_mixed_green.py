"""Execute actual magnetic mixed Green insertions at one COMMON cutoff probe."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_magnetic_mixed_green import magnetic_mixed_green_application
from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
from bhsm.interface.muon_magnetic_open_lepton_vertex import magnetic_open_fields_at_node
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output,*,cutoff,series_terms=4,refined_series_terms=6):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve prior magnetic operator applications')
    if not np.isfinite(cutoff) or cutoff<=0:raise ValueError('one explicit common positive numerical cutoff probe required')
    angular=retained_full_q_angular_space(ROOT);hashes={};arrays={};operators={};sources={};rows=[]
    for side in ('incoming','outgoing'):
        bound=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/'+side+'_run_1',repository=ROOT)
        hashes.update(bound['input_hashes']);t=bound['source']['times'][2]
        fields=magnetic_open_fields_at_node(bound,t)
        rep=dict(bound['representation'],native_positive_nu_squared_action=bound['receipt']['action_parameters']['nu_squared_action'])
        L=bound['receipt']['chronological_response_span']
        a=magnetic_mixed_green_application(fields,rep,angular,length=L,cutoff=cutoff,series_terms=series_terms)
        refined=magnetic_mixed_green_application(fields,rep,angular,length=L,cutoff=cutoff,series_terms=refined_series_terms)
        for placement in ('full18_forward','full18_reverse','paired_middle_minus_light_forward','paired_middle_minus_light_reverse'):
            for name,value in a[placement].items():
                arrays[side+'_'+placement+'_'+name]=value
                arrays[side+'_'+placement+'_'+name+'_refined']=refined[placement][name]
        scalar=a['scalar_source']
        for key in ('gaunt_even_odd_source','positive_H_odd','positive_H_even','delta_positive_H_even_odd',
            'delta_temporal_connection_even_odd','delta_spatial_even_odd','delta_potential_even_odd',
            'odd_derivative_matrices','even_derivative_matrices','source_derivative_matrices',
            'scalar_product_image_residual','source_wall_gauge','source_H'):
            sources[side+'_'+key]=scalar[key]
        for key in ('raw_fields','first_wall_gauge','first_H','first_H_rate'):
            sources[side+'_'+key]=fields[key]
        records=[]
        for family,r in a['families'].items():
            prefix=side+'_family_'+family+'_';d=r['operators'];v=r['contraction']
            # Gaunt and four bare mass vertices reconstruct every B entry
            # exactly by the frozen multiplication convention.  Store
            # those factors rather than many repeated zero/tensor entries.
            for key,value in d.items():
                if isinstance(value,np.ndarray) and not key.startswith('mixed_vertex_'):operators.setdefault(side+'_family_'+family,{})[prefix+key]=value
            from bhsm.interface.muon_magnetic_open_lepton_vertex import canonical_open_field_vertices
            ids=d['fiber_indices'];op=a['vertices']['operator']
            sources[prefix+'bare_scalar_mass_vertices']=canonical_open_field_vertices(op['R4'],op['N'])['scalar'][:,ids][:,:,ids]
            records.append(dict(family=int(family),fermion_minimum_eigenvalue=d['squared_factor_minimum_eigenvalue'],
                forward_component_norms={k:float(np.linalg.norm(z)) for k,z in v['forward'].items()},
                reverse_component_norms={k:float(np.linalg.norm(z)) for k,z in v['reverse'].items()},
                kernel_positive_series_tail_upper=v['kernel_positive_series_tail_upper'],
                contracted_series_tail_majorant_estimates=v['contracted_series_tail_majorant_estimates'],
                exact_stored_contracted_series_tail_upper=v['exact_stored_contracted_series_tail_upper'],
                exact_stored_series_tail_norm_products_outward=True,
                contracted_tail_norm_arithmetic_outward=False))
        row=dict(side=side,response_time=float(t),coordinate_time=fields['coordinate_time'],length=L,
            common_cutoff_probe=cutoff,source_n3_exactly_zero=scalar['source_n3_exactly_zero'],
            source_maximum_level=scalar['source_maximum_level'],
            complete_odd_scalar_coordinate_count=len(scalar['positive_H_odd']),
            complete_even_scalar_coordinate_count=len(scalar['positive_H_even']),
            odd_harmonic_labels=scalar['odd_harmonic_labels'],even_harmonic_labels=scalar['even_harmonic_labels'],
            external_output_harmonic_labels=a['external_output_harmonic_labels'],
            action_Gram_scalar=scalar['action_Gram_scalar'],
            Higgs_odd_minimum_eigenvalue=float(np.linalg.eigvalsh(scalar['positive_H_odd'])[0]),
            Higgs_even_minimum_eigenvalue=float(np.linalg.eigvalsh(scalar['positive_H_even'])[0]),
            product_image_residual_max=float(np.max(scalar['scalar_product_image_residual'])),
            paired_middle_minus_light_forward_norm=float(np.linalg.norm(a['paired_middle_minus_light_forward']['total'])),
            paired_middle_minus_light_reverse_norm=float(np.linalg.norm(a['paired_middle_minus_light_reverse']['total'])),
            full18_forward_norm=float(np.linalg.norm(a['full18_forward']['total'])),
            full18_reverse_norm=float(np.linalg.norm(a['full18_reverse']['total'])),
            series_refinement_absolute_difference=float(np.linalg.norm(a['full18_forward']['total']-refined['full18_forward']['total'])),
            paired_series_refinement_absolute_difference=float(np.linalg.norm(a['paired_middle_minus_light_forward']['total']-refined['paired_middle_minus_light_forward']['total'])),
            scalar_potential_source_norm=float(np.linalg.norm(scalar['delta_potential_even_odd'])),
            families=records)
        rows.append(row);print(json.dumps(dict(stage='actual_magnetic_mixed_Green',**row),sort_keys=True),flush=True)
    for name in ('muon_magnetic_mixed_green','muon_intrinsic_higgs_positive_source','muon_intrinsic_higgs_positive_green',
        'muon_common_cutoff_green_kernel','muon_magnetic_open_lepton_vertex','muon_primal_cell_reached_source_heat',
        'muon_primal_trace_enriched_lepton_operator','muon_intrinsic_scalar_discretization'):
        p='src/bhsm/interface/'+name+'.py';hashes[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    hashes[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    out.mkdir(parents=True);archive_records={}
    for name,data in dict(application=arrays,scalar_sources=sources,**{s+'_fermion_operators':d for s,d in operators.items()}).items():
        p=out/(name+'.npz');deterministic_archive(p,data)
        if p.stat().st_size>10*1024**2:raise ValueError('lossless archive exceeds publication limit: '+p.name)
        archive_records[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest(),keys=sorted(data))
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in hashes.items()):raise RuntimeError('consumed source changed')
    result=dict(classification='EVALUATED_MAGNETIC_SOURCE_DIRECTED_INTRINSIC_HIGGS_LEPTON_MIXED_GREEN_DERIVATIVE',
        input_hashes=hashes,array_archives=archive_records,records=rows,
        common_cutoff_probe=float(cutoff),cutoff_common_to_both_arms=True,
        cutoff_role='explicit numerical proper-time probe; no formation cutoff or cutoff jet selected',
        primitive_source='actual e R4²/2 Higgs-aligned magnetic source and solved gauge/H first response; e once',
        mixed_vertex_normalization='bare real4 fixed-Y LR mass vertices times int b³/int b²=3/4; unit Haar product maps',
        factor_order='P_F^-1 A_F dagger; no nonnormal reorder',
        derivative_equation='-L3 deltaP_F A_F dagger + L2 deltaA_F dagger - L3 deltaP_H; scalar action Gram once',
        deltaP_F_placements='A_even dagger Xi_even,odd + Xi_odd,even dagger A_odd, separately archived',
        both_open_vertex_placements_retained=True,all18_leptons_and_three_fixed_Y_families=True,
        bare_mixed_vertex_first_derivative_zero_provenance='Yukawa is linear in H; fixed real4/canonical coframe Hessian vertex has no H or gauge argument',
        starting_component='virtual intrinsic Higgs n1+n3 real80; its full magnetic even image retained, not all internal field shells or a full loop sum',
        omitted_starting_even_scalar_loop_not_filled_zero=True,
        temporal_domain='same actual midpoint coefficient cell and existing finite Dirichlet tent; int b² bprime=0 only its projected moment',
        temporal_differential_complement_evaluated=False,odd_angular_geometry_source_completed=False,
        statistics_factor_inserted=False,complete_graded_P_cycle_or_native_square_contacts_derived=False,
        EC_HS_ghost_exterior_relative_eta_completion_included=False,
        quantum_Sigma_external_pole_LSZ_or_Pauli_completed=False,physical_a_mu=None,physical_g_mu=None,
        series_terms=series_terms,refined_series_terms=refined_series_terms,
        error_scope='kernel series tails outward for exact stored spectra only; contraction norm estimates/binary assembly/eigensystem, source/basis/tent/continuum and physical matching errors separate and unenclosed')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],array_archives=archive_records,records=rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--cutoff',type=float,required=True);p.add_argument('--series-terms',type=int,default=4)
    p.add_argument('--refined-series-terms',type=int,default=6);a=p.parse_args()
    print(json.dumps(materialize(a.output,cutoff=a.cutoff,series_terms=a.series_terms,refined_series_terms=a.refined_series_terms),sort_keys=True))
