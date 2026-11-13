"""Evaluate the restored-graph Clifford operator and full field heat cotangent."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_connector_field_action import (
    CASES,actual_field_corner_quadrature,retained_input,actual_source_curve_coefficients,
    saved_original_wall_coefficient_family,_compressed_npz)
from bhsm.interface.muon_restored_clifford_node_application import (
    restored_clifford_node_application,original_n0_wall_coordinate_map)
from bhsm.interface.muon_restored_clifford_heat_cotangent import (
    restored_clifford_coefficient_forms,restored_clifford_heat_field_cotangent)
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization


def materialize(output,*,case,refinement):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve previous action/operator applications')
    refs={};archives={};records=[]
    def read(p):
        refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    ep=ROOT/'artifacts/muon_piecewise_euclidean_action_20261011/run_2';er=read(ep/'result.json');c=er['cutoff']
    phases,curves,nodes={}, {}, {}
    for side in('incoming','outgoing'):
        phases[side],_=retained_input(side,refs)
        curves[side]=actual_source_curve_coefficients(*(read(ROOT/f'artifacts/muon_corrected_profile_magnetic_response_20261011/run_1/{side}_{name}.npz')for name in('phase','velocity','contacts')))
        nodes[side]=read(ep/(side+'_nodes.npz'))
        nodes[side]['total_proper_clock']=next(r['total_proper_clock']for r in er['records']if r['side']==side)
    ff=saved_original_wall_coefficient_family(repository=ROOT);refs.update(ff['input_hashes'])
    graph=actual_field_corner_quadrature(phases,curves,nodes,ff,case=case,family=1,refinement=refinement)
    a=scalar_s3_discretization(4);labels=a['real_basis_labels'];levels=np.array([l[0]for l in labels])
    E=a['real_angular_derivative_matrices'];mean=np.array([i for i,l in enumerate(labels)if l[0]in(0,2)])
    y=a['real_basis_values'];G=np.einsum('qi,qj,qh,q->ijh',y,y,y[:,mean],a['haar_weights'],optimize=True)
    for rel in('src/bhsm/interface/muon_restored_clifford_heat_cotangent.py',
        'src/bhsm/interface/muon_restored_clifford_node_application.py',
        'src/bhsm/interface/muon_continued_connector_field_action.py',
        'scripts/evaluate_muon_continued_connector_field_action.py',
        'tests/test_muon_restored_clifford_heat_cotangent.py',Path(__file__).relative_to(ROOT).as_posix()):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path is not None:
            p=Path(path)
            try:rel=p.relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256(p.read_bytes()).hexdigest()
    out.mkdir(parents=True)
    def save(name,v):
        p=out/name;_compressed_npz(p,v)
        if p.stat().st_size>=10*1024**2:raise RuntimeError('split complete operator arrays before publication')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    old=ff['arms'][CASES[case][0]]['arrays'];P0=original_n0_wall_coordinate_map(graph['wall_trace_map'],old['value_permutation'])
    save('graph_and_angular_incidence.npz',dict(quadrature_provenance=graph['quadrature_provenance'],
        row_incidence=np.array([q['rows']for q in graph['quadrature']],complex),
        connector_nodes=graph['connector_nodes'],angular_derivatives=E,mean_source_gaunt=G,
        angular_degree_labels=levels,mean_source_degree_labels=levels[mean],
        mean_source_labels=np.asarray([labels[j]for j in mean],str),
        original_n0_wall_coordinate_map=P0['wall_map'],original_n0_coordinate_permutation=P0['original_coordinate_permutation'],
        original_n1_wall_coordinate_map=graph['wall_trace_map']))
    sumg=sumgc=None
    for family in(0,1,2):
        q=[]
        for app,provenance in zip(graph['quadrature'],graph['quadrature_provenance']):
            anchor,z,weight,w,ws,side,part=provenance;side='incoming'if side.real==0 else'outgoing'
            q.append(restored_clifford_node_application(phases[side],float(anchor.real),z,family=family,
                measure=weight,right_clock=w,reflected_clock=ws,rows=app['rows']))
        save(f'loop_family_{family}_clifford_quadrature.npz',{k:np.array([r[k]for r in q])
            for k in('H','Hsharp','R','Rsharp','N','Nsharp','vertices','vertices_sharp','measure',
                      'right_clock','reflected_clock','anchor','offset','offset_sharp','raw_fields','raw_fields_sharp')})
        print(json.dumps(dict(stage='same_graph_clifford_nodes',loop_family=family,nodes=len(q),
            restored_free_trace_nodes=graph['temporal_nodes']-1,source_range_harmonics=55,starting_loop_harmonics=30)),flush=True)
        coeff=restored_clifford_coefficient_forms(q,temporal_nodes=graph['temporal_nodes'],angular_derivatives=E,
            mean_source_gaunt=G,angular_levels=levels,starting_loop_max_level=3,family=family)
        result=restored_clifford_heat_field_cotangent(coeff,c)
        for key in('original_K','original_M'):
            m=result[key]
            for start in range(0,len(m),48):save(f'loop_family_{family}_{key}_{start}.npz',
                {key:m[start:start+48],'row_start':np.array(start),'full_shape':np.array(m.shape)})
        arrays={k:v for k,v in result.items()if isinstance(v,np.ndarray)and k not in('original_K','original_M')}
        if result['heat_cotangent_evaluated']:
            g,gc=(result[k]for k in('closed_field_cotangent','closed_field_cotangent_fixed_cutoff_partial'))
            arrays['original_n0_field_cotangent']=g[:,:,0]@P0['wall_map']
            arrays['original_n0_field_cotangent_fixed_cutoff_partial']=gc[:,:,0]@P0['wall_map']
            sumg=g.copy()if sumg is None else sumg+g;sumgc=gc.copy()if sumgc is None else sumgc+gc
        save(f'loop_family_{family}_heat_cotangent.npz',arrays)
        r={k:v for k,v in result.items()if not isinstance(v,np.ndarray)}
        r.update(loop_family=family,starting_loop_harmonics=30,reached_operator_harmonics=55,
            minimum_cutoff_times_real_eigenvalue=c*result['minimum_real_eigenvalue'])
        if result['heat_cotangent_evaluated']:
            r.update(cotangent_norm=float(np.linalg.norm(g)),fixed_cutoff_partial_norm=float(np.linalg.norm(gc)),
                nonconstant_mean_source_norm=float(np.linalg.norm(g[:,:,1:])))
        records.append(r);print(json.dumps(r,sort_keys=True),flush=True)
    if all(r['heat_cotangent_evaluated']for r in records):
        save('all_closed_lepton_field_cotangent.npz',dict(closed_field_cotangent=sumg,
            closed_field_cotangent_fixed_cutoff_partial=sumgc,
            original_n0_field_cotangent=sumg[:,:,0]@P0['wall_map'],
            original_n0_field_cotangent_fixed_cutoff_partial=sumgc[:,:,0]@P0['wall_map']))
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed action changed')
    record=dict(classification='EVALUATED_RESTORED_GRAPH_CLIFFORD_SQUARE_AND_ACCRETIVE_BRANCH_FIELD_COTANGENT_APPLICATION',
        input_hashes=refs,archives=archives,case=case,refinement=refinement,cutoff_probe=c,records=records,
        temporal_trace_nodes=graph['temporal_nodes'],initial_trace_node=0,free_final_trace_node=3,
        current_coordinates='material At_L,Ar_L,Ai_L,realified H; temporal vertex -iG/N on both analytic source branches',
        original_n0_field_order='84 At-first original field coefficients per free trace; 16 At and 68 other gauge/H coordinates',
        original_holomorphic_measure_and_independent_reflected_clock_retained=True,
        induced_H_field_directions_included=True,old_FE2_g_or_uniform_B_mean_grafted=False,
        complete_starting_angular_complement_or_relative_exterior_or_overlap_included=False,
        physical_contour_domain_cutoff_or_Pauli_identified=False,physical_a_mu=None,
        action_domain_scope='restored two-cell corner window on the actual retained corrected coefficient germs; not the entire chronological source graph',
        germ_sampler='muon_restored_clifford_node_application.restored_clifford_local_germ; proper-cell inverse-coframe ODE or actual connector coordinate slope',
        error_scope='binary64 coefficient/eigen/gradient diagnostics, no native remainder or projected observable enclosure')
    (out/'result.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    return record


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--case',choices=list(CASES),required=True);p.add_argument('--refinement',type=int,choices=(2,4),required=True)
    a=p.parse_args();materialize(a.output,case=a.case,refinement=a.refinement)
