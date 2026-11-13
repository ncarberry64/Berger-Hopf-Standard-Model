"""Apply the corrected actual source-cell clock without changing frozen charge outputs."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_reached_trace_action import deterministic_archive
from bhsm.interface.muon_common_domain_charge_transport import (
    holomorphic_charge_first,source_clock_higgs_first,transported_charge_application)
from bhsm.interface.muon_common_domain_charge_source_clock import (
    corrected_source_clock_higgs_first,charge_clock_direction_effect)
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from bhsm.interface.muon_piecewise_euclidean_action import FAMILY_INDICES


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve each common-domain charge application')
    refs={};archives={}
    def read(p,expected=None):
        p=ROOT/p;h=sha256(p.read_bytes()).hexdigest()
        if expected is not None and h!=expected:raise ValueError('same charge transport operand changed')
        refs[p.relative_to(ROOT).as_posix()]=h
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    def shards(folder,prefix):
        folder=Path(folder);m=read(folder/'result.json')
        names=sorted((k for k in m['archives']if k.startswith(prefix)),key=lambda s:int(Path(s).stem.rsplit('_',1)[1]))
        a=[read(folder/k,m['archives'][k]['sha256'])for k in names]
        if not a:raise ValueError('complete original quadrature/source provenance required')
        return {k:(np.concatenate([b[k]for b in a])if a[0][k].ndim else a[0][k])for k in a[0]}
    body=shards('artifacts/muon_chronological_current_body_20261011/run_1','corrected_full18_body_points_')
    source=shards('artifacts/muon_shifted_boundary_source_20261011/run_1','family_1_exterior_point_trace_maps_')
    match=shards('artifacts/muon_chronological_current_matching_20261011/incoming_family_1_run_1','converged_body_and_dual_nodes_')
    edges=shards('artifacts/muon_chronological_current_amputation_20261011/run_1','original_full_body_edge_germs_')
    old=Path('artifacts/muon_nonlinear_chronological_n0_action_20261011/run_2');om=read(old/'result.json')
    incidence=read(old/'chronological_field_incidence.npz',om['archives']['chronological_field_incidence.npz']['sha256'])
    W=incidence['original_n0_wall_coordinate_map'];provenance=incidence['quadrature_provenance']
    legacy_folder='artifacts/muon_common_domain_charge_transport_20261011/run_3'
    legacy=shards(legacy_folder,'common_domain_charge_and_weak_action_points_')
    legacy_receipt=read(Path(legacy_folder)/'result.json')
    legacy_integrals=read(Path(legacy_folder)/'complete_complex_action_charge_test_integrals.npz',
        legacy_receipt['archives']['complete_complex_action_charge_test_integrals.npz']['sha256'])
    clock_evidence_path=Path('artifacts/muon_holomorphic_child_terminal_20261011/run_2/result.json')
    read(clock_evidence_path)
    if (len(body['N'])!=3832 or not np.array_equal(body['original_rows'],source['same_original_rows'])
            or not np.array_equal(body['original_rows'],match['same_original_rows'])
            or not np.array_equal(body['original_rows'],legacy['original_rows'])
            or provenance.shape!=(3832,9)
            or not np.array_equal(body['coordinate_slope'],provenance[:,8])
            or not np.array_equal(body['original_right_clock'],provenance[:,3])):
        raise ValueError('all chronological connectors, cells and original source rows must agree')
    fi=FAMILY_INDICES[1];G=lepton_unit_trace_gauge_representation()['generators'][:,fi][:,:,fi]
    maxima={};integrals={};correction_integrals={};batch=[];index=0;part_counts={}
    for rel in (Path(__file__).relative_to(ROOT).as_posix(),
                'src/bhsm/interface/muon_common_domain_charge_transport.py',
                'tests/test_muon_common_domain_charge_transport.py',
                'scripts/evaluate_muon_common_domain_charge_transport.py',
                'src/bhsm/interface/muon_common_domain_charge_source_clock.py',
                'tests/test_muon_common_domain_charge_source_clock.py',
                'src/bhsm/interface/muon_piecewise_euclidean_action.py',
                'scripts/evaluate_muon_chronological_clifford_graph.py',
                'src/bhsm/interface/muon_chronological_current_body.py',
                'src/bhsm/interface/muon_source_directed_em_normal_current.py',
                'src/bhsm/interface/muon_native_product_factor_graph.py',
                'scripts/evaluate_muon_reached_trace_action.py'):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    out.mkdir(parents=True)
    def save(name,data):
        p=out/name;deterministic_archive(p,data)
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    def flush():
        nonlocal batch,index
        if not batch:return
        save(f'common_domain_charge_and_weak_action_points_{index}.npz',{k:np.array([r[k]for r in batch])for k in batch[0]})
        index+=len(batch);batch=[]
    for q in range(3832):
        rows=body['original_rows'][q];edge=int(rows[0,0].real)
        w=body['original_right_clock'][q];N=body['N'][q];slope=body['coordinate_slope'][q]
        part=int(provenance[q,6].real);side='incoming'if provenance[q,5].real==0 else'outgoing'
        group=f'{side}_part_{part}';part_counts[group]=part_counts.get(group,0)+1
        lift=W[20:]@body['field_coordinate_rate'][q]
        clock=corrected_source_clock_higgs_first(body['H_coordinate_first'][q],lift,part,slope,w,N)
        hs=clock['H_source_clock_first']
        hs_old=source_clock_higgs_first(body['H_coordinate_first'][q],lift,slope,w,N)
        charge=holomorphic_charge_first(body['H_realified'][q],hs,G)
        charge_old=holomorphic_charge_first(body['H_realified'][q],hs_old,G)
        delta_charge=charge['charge_first']-charge_old['charge_first']
        H=body['Hcan'][q][np.ix_(fi,fi)]
        ratio=edges['proper_steps'][edge]*rows[1,2]/w
        A=ratio*edges['full18_n0_body'][edge][np.ix_(fi,fi)]
        F=source['physical_right_trace_map'][q];L=source['physical_analytic_left_trace_map'][q]
        a=transported_charge_application(charge['charge'],charge['charge_first'],H,A,F,L)
        a={k:v for k,v in a.items()if isinstance(v,np.ndarray)}
        directions=charge_clock_direction_effect(charge['charge'],delta_charge,F,L)
        a.update(H_source_clock_first=hs,source_chart_generator=A,actual_point_body=H,
                 original_charge=charge['charge'],original_charge_first=charge['charge_first'],
                 original_rows=rows,original_quadrature_index=q,
                 source_chart_clock_ratio=ratio,coordinate_slope=slope,graph_part=part,
                 source_side=0 if side=='incoming'else 1,
                 analytic_coordinate_source_clock_rate=clock['analytic_coordinate_source_clock_rate'],
                 inherited_H_source_clock_first=clock['inherited_H_source_clock_first'],
                 nodal_H_source_clock_first=clock['nodal_H_source_clock_first'],
                 legacy_H_source_clock_first=hs_old,H_source_clock_first_correction=hs-hs_old,
                 original_charge_first_correction=delta_charge,
                 original_measure=body['original_measure'][q],original_right_clock=w,
                 geometric_measure=match['same_native_geometric_measure'][q])
        a.update(directions)
        checks=dict(charge_match_max=np.max(abs(charge['charge']-match['selected_charge'][q])),
            charge_idempotence_max=np.max(abs(charge['charge']@charge['charge']+charge['charge'])),
            charge_first_idempotence_max=np.max(abs(charge['charge']@charge['charge_first']+charge['charge_first']@charge['charge']+charge['charge_first'])),
            point_body_match_max=np.max(abs(H-match['right_body'][q])),
            analytic_source_dual_pairing_max=np.max(abs(a['analytic_dual_pairing_residual'])),
            action_source_chart_weak_residual_norm=np.linalg.norm(a['actual_source_chart_weak_action_residual']),
            action_minus_represented_charge_first_norm=np.linalg.norm(a['action_minus_represented_charge_first']),
            actual_covariant_charge_first_norm=np.linalg.norm(a['actual_action_covariant_charge_first']),
            original_charge_exchange_norm=np.linalg.norm(a['original_charge_exchange']),
            represented_source_chart_charge_first_norm=np.linalg.norm(a['represented_source_chart_charge_first']),
            charge_source_clock_first_norm=np.linalg.norm(charge['charge_first']),
            legacy_H_first_reconstruction_max=np.max(abs(hs_old-legacy['H_source_clock_first'][q])),
            legacy_charge_first_reconstruction_max=np.max(abs(charge_old['charge_first']-legacy['original_charge_first'][q])),
            H_source_clock_first_correction_norm=np.linalg.norm(hs-hs_old),
            original_charge_first_correction_norm=np.linalg.norm(delta_charge),
            analytic_direction_dual_difference_max=np.max(abs(directions['analytic_dual_direction_difference'])),
            connector_charge_first_change_max=(np.max(abs(delta_charge))if part!=0 else 0.),
            source_clock_chain_difference_max=(np.max(abs(hs+1j*body['H_coordinate_first'][q]/N))if part==0 else 0.))
        for k,v in checks.items():maxima[k]=max(maxima.get(k,0.),float(v))
        for k in ('actual_source_chart_weak_action_residual','actual_action_covariant_charge_first',
                  'represented_source_chart_charge_first','action_minus_represented_charge_first'):
            integrals[k]=integrals.get(k,0)+body['original_measure'][q]*a[k]
        for k,v in directions.items():
            for prefix in ('total',group):
                key=prefix+'_'+k
                correction_integrals[key]=correction_integrals.get(key,0)+body['original_measure'][q]*v
        batch.append(a)
        if len(batch)==128:flush()
    flush();save('complete_complex_action_charge_test_integrals.npz',integrals)
    correction_integrals['complete_C6_coordinate_direction_tests']=np.eye(6,dtype=complex)
    for k in ('actual_action_covariant_charge_first','represented_source_chart_charge_first'):
        correction_integrals['legacy_'+k]=legacy_integrals[k]
        correction_integrals['corrected_'+k]=integrals[k]
        correction_integrals['actual_corrected_minus_legacy_'+k]=integrals[k]-legacy_integrals[k]
    save('complete_source_clock_correction_integrals.npz',correction_integrals)
    if any(sha256((ROOT/r).read_bytes()).hexdigest()!=h for r,h in refs.items()):raise RuntimeError('executed charge operands changed')
    if maxima['charge_match_max']>2e-14 or maxima['point_body_match_max']>2e-14:raise ValueError('different action-selected generator or body')
    if maxima['legacy_H_first_reconstruction_max']!=0 or maxima['legacy_charge_first_reconstruction_max']!=0:
        raise ValueError('legacy clock application no longer matches its frozen point packet')
    if maxima['connector_charge_first_change_max']!=0:
        raise ValueError('connector source-clock application changed under a source-cell correction')
    result=dict(classification='EVALUATED_CORRECTED_SOURCE_CELL_CLOCK_COMMON_DOMAIN_HOLOMORPHIC_CHARGE_WEAK_ACTION',
        input_hashes=refs,archives=archives,diagnostics=maxima,
        complex_integral_norms={k:float(np.linalg.norm(v))for k,v in integrals.items()},
        original_quadrature_points=3832,complete_C6_family=1,
        source_clock_part_counts=part_counts,
        source_clock_equation='part0: dz/dtau_E=-i/N; parts1/2: dz/dtau=coordinate_slope/right_clock; dH=rate*(H_coordinate_first-field_coordinate_rate)+field_coordinate_rate/(iN)',
        source_cell_zero_saved_slope_is_bookkeeping_not_analytic_coefficient_derivative=True,
        independent_terminal_source_clock_evidence=clock_evidence_path.as_posix(),
        frozen_legacy_application=legacy_folder,
        frozen_legacy_result_sha256=refs[legacy_folder+'/result.json'],
        frozen_legacy_sources_or_outputs_modified=False,
        complete_C6_source_directions_and_charge_neutral_return_retained=True,
        directional_correction_integral_column_norms=np.linalg.norm(
            correction_integrals['total_source_direction_clock_correction'],axis=0).tolist(),
        correction_integral_norms={k:float(np.linalg.norm(v))for k,v in correction_integrals.items()
            if k!='complete_C6_coordinate_direction_tests'},
        source_chart='same saved full18 n0 edge-average Cauchy map, restricted to full muon C6; actual pointwise action defect exported',
        generator_equation='Q=i s_c(H) G_c with the retained holomorphic Higgs-selected neutral line',
        source_chart_equation='Qbar=F^-1 Q F; D_tau Qbar=F^-1(Q_tau+[A_chart,Q])F',
        physical_action_equation='F^-1(Q_tau+[H_can,Q])F; difference from represented chart kept',
        constant_coordinate_connectors_keep_nodal_field_motion=True,
        independent_analytic_dual_not_Hilbert_adjoint=True,
        gauge_charge_exchange_discarded=False,complex_contacts_discarded=False,
        physical_pole_charge_body_or_LSZ_normalization_assigned=False,
        complete_native_contribution=None,complete_a_mu=None,complete_g_mu=None,
        error_scope='binary action coefficient/first-germ application on every actual source-chart point; the edge-average weak residual is an approximation residual, not a continuum or physical matching enclosure')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),**maxima,
                         complex_integral_norms=result['complex_integral_norms'],
                         correction_integral_norms=result['correction_integral_norms']),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    materialize(p.parse_args().output)
