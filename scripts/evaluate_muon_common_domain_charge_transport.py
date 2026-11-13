"""Apply the action charge germ to every actual transported source frame."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_reached_trace_action import deterministic_archive
from bhsm.interface.muon_common_domain_charge_transport import (
    holomorphic_charge_first,source_clock_higgs_first,transported_charge_application)
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
    W=read(old/'chronological_field_incidence.npz',om['archives']['chronological_field_incidence.npz']['sha256'])['original_n0_wall_coordinate_map']
    if (len(body['N'])!=3832 or not np.array_equal(body['original_rows'],source['same_original_rows'])
            or not np.array_equal(body['original_rows'],match['same_original_rows'])):
        raise ValueError('all chronological connectors, cells and original source rows must agree')
    fi=FAMILY_INDICES[1];G=lepton_unit_trace_gauge_representation()['generators'][:,fi][:,:,fi]
    maxima={};integrals={};batch=[];index=0
    for rel in (Path(__file__).relative_to(ROOT).as_posix(),
                'src/bhsm/interface/muon_common_domain_charge_transport.py',
                'tests/test_muon_common_domain_charge_transport.py',
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
        lift=W[20:]@body['field_coordinate_rate'][q]
        hs=source_clock_higgs_first(body['H_coordinate_first'][q],lift,slope,w,N)
        charge=holomorphic_charge_first(body['H_realified'][q],hs,G)
        H=body['Hcan'][q][np.ix_(fi,fi)]
        ratio=edges['proper_steps'][edge]*rows[1,2]/w
        A=ratio*edges['full18_n0_body'][edge][np.ix_(fi,fi)]
        F=source['physical_right_trace_map'][q];L=source['physical_analytic_left_trace_map'][q]
        a=transported_charge_application(charge['charge'],charge['charge_first'],H,A,F,L)
        a={k:v for k,v in a.items()if isinstance(v,np.ndarray)}
        a.update(H_source_clock_first=hs,source_chart_generator=A,actual_point_body=H,
                 original_charge=charge['charge'],original_charge_first=charge['charge_first'],
                 original_rows=rows,original_quadrature_index=q,
                 source_chart_clock_ratio=ratio,coordinate_slope=slope,
                 original_measure=body['original_measure'][q],original_right_clock=w,
                 geometric_measure=match['same_native_geometric_measure'][q])
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
            charge_source_clock_first_norm=np.linalg.norm(charge['charge_first']))
        for k,v in checks.items():maxima[k]=max(maxima.get(k,0.),float(v))
        for k in ('actual_source_chart_weak_action_residual','actual_action_covariant_charge_first',
                  'represented_source_chart_charge_first','action_minus_represented_charge_first'):
            integrals[k]=integrals.get(k,0)+body['original_measure'][q]*a[k]
        batch.append(a)
        if len(batch)==128:flush()
    flush();save('complete_complex_action_charge_test_integrals.npz',integrals)
    if any(sha256((ROOT/r).read_bytes()).hexdigest()!=h for r,h in refs.items()):raise RuntimeError('executed charge operands changed')
    if maxima['charge_match_max']>2e-14 or maxima['point_body_match_max']>2e-14:raise ValueError('different action-selected generator or body')
    result=dict(classification='EVALUATED_COMMON_DOMAIN_HOLOMORPHIC_CHARGE_AND_SOURCE_FRAME_WEAK_ACTION',
        input_hashes=refs,archives=archives,diagnostics=maxima,
        complex_integral_norms={k:float(np.linalg.norm(v))for k,v in integrals.items()},
        original_quadrature_points=3832,complete_C6_family=1,
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
                         complex_integral_norms=result['complex_integral_norms']),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    materialize(p.parse_args().output)
