"""Apply actual global u/p source images to their same-base native return.

This is a direction-resolved finite source/current application. The named
canonical column is not assigned a physical muon pole or Pauli spin state.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_global_current_wall_loader import (
    GlobalCurrentWallLoader,even_current_source_components)
from bhsm.interface.muon_native_unsquared_domain_matching import native_unsquared_domain_matching
from bhsm.interface.muon_chronological_spectral_blocks import homogeneous_scalar_degree_reduction
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from bhsm.interface.muon_source_directed_em_normal_current import normal_left_current_gaunt
from bhsm.interface.muon_piecewise_euclidean_action import FAMILY_INDICES
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(output,*,current_folder,action_folder,matching_folder,native_folder,column):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve prior actual source applications')
    loader=GlobalCurrentWallLoader(ROOT/current_folder,ROOT/action_folder)
    if loader.current['current_kind']!='literal':raise ValueError('complete literal current source and induced H required')
    refs={};archives={};out.mkdir(parents=True)
    def read_family(folder,prefix):
        folder=ROOT/folder;rp=folder/'result.json';md=json.loads(rp.read_bytes())
        refs[rp.relative_to(ROOT).as_posix()]=sha256(rp.read_bytes()).hexdigest()
        names=sorted((name for name in md['archives']if name.startswith(prefix)),
                     key=lambda s:int(Path(s).stem.rsplit('_',1)[-1]))
        shards=[]
        for name in names:
            p=folder/name;h=sha256(p.read_bytes()).hexdigest()
            if h!=md['archives'][name]['sha256']:raise ValueError('same corrected node/source changed')
            refs[p.relative_to(ROOT).as_posix()]=h
            with np.load(p,allow_pickle=False)as z:shards.append({k:z[k].copy()for k in z.files})
        return md,{k:np.concatenate([s[k]for s in shards])for k in shards[0]if np.asarray(shards[0][k]).ndim}
    nm,nodes=read_family(native_folder,'native_coframe_nodes_')
    mm,matched=read_family(matching_folder,'converged_body_and_dual_nodes_')
    if (not np.array_equal(nodes['rows'],matched['same_original_rows'])
            or not np.array_equal(nodes['measure'],matched['same_native_geometric_measure'])
            or not np.array_equal(nodes['original_holomorphic_measure'],matched['same_original_measure'])
            or loader.current['family']!=mm['family']):
        raise ValueError('same converged base, family, original incidence and both measures required')
    family=mm['family'];fi=FAMILY_INDICES[family]
    alpha=lepton_current_hilbert_representation()['alpha'][:,fi][:,:,fi]
    G=normal_left_current_gaunt()['gaunt'];q=[];components=[[]for _ in range(4)]
    source_nodes={k:[]for k in('u_wall_coefficients','p_wall_coefficients',
        'u_wall_coordinate_rate','p_wall_coordinate_rate','u_frame_reactions_by_spectator','p_frame_reactions_by_spectator')}
    source_norms={k:[]for k in('u_gauge','p_gauge','u_H','p_H')}
    def save(name,data):
        p=out/name;_compressed_npz(p,data)
        if p.stat().st_size>10*1024**2:raise RuntimeError('split actual source rows under publication cap')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    for j in range(len(nodes['measure'])):
        qi={k:v[j]for k,v in nodes.items()}
        qi['rows']=tuple((int(a.real),complex(b),complex(c))for a,b,c in qi['rows'])
        qi.update(H=matched['right_body'][j],Hsharp=matched['separately_reflected_base_body'][j],source_point_index=j)
        a=loader.node_images(qi,[column],family=family,even_field_odd_gaunt=G)
        for k in source_nodes:source_nodes[k].append(a[k])
        for label in('u','p'):
            source_norms[label+'_gauge'].append(np.linalg.norm(a[label+'_wall_coefficients'][:20]))
            source_norms[label+'_H'].append(np.linalg.norm(a[label+'_wall_coefficients'][20:]))
        c=even_current_source_components(a['u_native_images']['even_from_odd_source'][0],
                                       a['p_native_images']['odd_from_even_source'][0])
        for k,entry in enumerate(c):components[k].append(entry)
        q.append(qi)
        if (j+1)%512==0:print(json.dumps(dict(stage='actual_global_current_source_images',points=j+1)),flush=True)
    for start in range(0,len(q),128):
        save(f'actual_global_current_wall_nodes_{start}.npz',
             {k:np.array(v[start:start+128])for k,v in source_nodes.items()})
    print(json.dumps(dict(stage='actual_global_current_complete_image_ready',source_column=column,
        induced_H_max=max(source_norms['u_H']),points=len(q))),flush=True)
    totals={};records=[]
    for ci,component in enumerate(components):
        degree=component[0]['degree'];spectator=component[0]['spectator']
        E=homogeneous_scalar_degree_reduction(degree)['angular_derivatives']
        def source(qi):
            a=component[qi['source_point_index']];return a['right_source'],a['literal_left']
        r=native_unsquared_domain_matching(q,temporal_nodes=nm['temporal_nodes'],
            angular_derivatives=E,alpha=alpha,source_sampler=source)
        currents={k:v for k,v in r.items()if k.endswith('_current')}
        for k,v in currents.items():totals[k]=totals.get(k,0)+v
        save(f'degree_{degree}_spectator_{spectator}_currents.npz',currents)
        # Preserve actual operator directions and weak source/dual/range
        # rows, without materializing a full chronological inverse.
        for key in('native_factor_response','analytic_weak_response','analytic_transpose_adjoint',
            'geometric_weak_response','acted_source_range_contact','square_range_contact_on_actual_response',
            'analytic_factor_weak_equation_defect','independently_acted_source_numerator'):
            for start in range(0,len(r[key]),128):
                save(f'degree_{degree}_spectator_{spectator}_{key}_nodes_{start+1}.npz',
                     {key:r[key][start:start+128]})
        norm=lambda a:float(np.linalg.norm(a))
        record=dict(degree=degree,spectator=spectator,actual_complete_source_columns=24,
            native_response_norm=norm(r['native_factor_response']),
            original_response_norm=norm(r['analytic_weak_response']),
            original_vs_native_response_norm=norm(r['analytic_weak_response']-r['native_factor_response']),
            original_current_norm=norm(r['analytic_current']),
            original_vs_native_same_target_current_norm=norm(r['analytic_current']-r['analytic_factor_current']),
            acted_source_range_norm=norm(r['acted_source_range_contact']),
            range_identity_original_row_residual_max=float(np.max(abs(r['range_identity_original_row_residual']))),
            native_original_row_residual_max=float(np.max(abs(r['native_original_square_residual']))),
            original_unsquared_row_residual_max=float(np.max(abs(r['analytic_original_weak_rows']))),
            original_transpose_row_residual_max=float(np.max(abs(r['analytic_original_transpose_rows']))),
            original_current_transpose_defect_max=float(np.max(abs(r['analytic_current']-r['analytic_independent_transpose_current']))))
        records.append(record);print(json.dumps(record,sort_keys=True),flush=True)
    save('complete_n0_n2_same_source_currents.npz',totals)
    for p,h in loader.verify_consumed_hashes().items():refs[Path(p).relative_to(ROOT).as_posix()]=h
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256(Path(path).read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_global_current_wall_loader.py'):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same source/operator changed')
    norm=lambda a:float(np.linalg.norm(a))
    md=dict(classification='EVALUATED_ACTUAL_GLOBAL_CURRENT_AND_ADJOINT_NATIVE_SOURCE_RANGE_RETURN',
        input_hashes=refs,archives=archives,records=records,family=family,
        source_column_index=column,source_column_multi_index=list(np.unravel_index(column,(6,2,6,4))),
        source_column_role='named canonical current TEST column; no physical pole/spin assignment',
        source_side=loader.current['source_side'],complete_288_columns_accessible=True,
        actual_current_response_and_transpose_adjoint_consumed=True,induced_H_source_retained=True,
        source_harmonics=4,complete_reached_even_harmonics=10,n2_spectators_summed_individually=True,
        source_or_analytic_left_coefficients_conjugated=False,
        original_initial_trace_held=0,original_free_final_trace=loader.free_nodes,all_corner_rows_retained=True,
        actual_source_range_and_independently_acted_numerator_evaluated=True,
        total_original_current_norm=norm(totals['analytic_current']),
        total_original_vs_native_same_target_current_norm=norm(totals['analytic_current']-totals['analytic_factor_current']),
        total_transpose_current_defect_max=float(np.max(abs(totals['analytic_current']-totals['analytic_independent_transpose_current']))),
        source_norm_max={k:max(v)for k,v in source_norms.items()},
        heat_or_physical_Pauli_or_exterior_LSZ_identified=False,
        error_scope='actual saved global field source, complete reached angular image and same-base finite inverse/range applications; binary64 row diagnostics are not a physical Pauli or continuum error enclosure')
    # unravel_index returns NumPy scalars, which are exact integers here.
    md['source_column_multi_index']=[int(v)for v in md['source_column_multi_index']]
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='actual_source_return_complete',result_sha256=sha256((out/'result.json').read_bytes()).hexdigest(),
        total_original_current_norm=md['total_original_current_norm'],
        total_original_vs_native_same_target_current_norm=md['total_original_vs_native_same_target_current_norm'])),flush=True)
    return md


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--column',type=int,default=208)
    p.add_argument('--current-folder',type=Path,default=Path('artifacts/muon_chronological_literal_current_20261011/incoming_family_1_run_1'))
    p.add_argument('--action-folder',type=Path,default=Path('artifacts/muon_chronological_n1_field_action_20261011/run_1'))
    p.add_argument('--matching-folder',type=Path,default=Path('artifacts/muon_chronological_current_matching_20261011/incoming_family_1_run_1'))
    p.add_argument('--native-folder',type=Path,default=Path('artifacts/muon_transported_native_pairing_20261011/run_1'))
    a=p.parse_args();materialize(a.output,current_folder=a.current_folder,action_folder=a.action_folder,
        matching_folder=a.matching_folder,native_folder=a.native_folder,column=a.column)
