"""Apply source-corrected Friedrichs and external trace charts on saved data."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
from scipy.linalg import expm
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_shifted_boundary_source import (
    shifted_boundary_forms,source_corrected_form_core_return,cauchy_external_trace_maps)
from bhsm.interface.muon_native_unsquared_domain_matching import _assemble_matching_forms
from bhsm.interface.muon_chronological_current_source_images import native_images_of_current_direction
from bhsm.interface.muon_global_current_wall_loader import even_current_source_components
from bhsm.interface.muon_chronological_spectral_blocks import homogeneous_scalar_degree_reduction
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from bhsm.interface.muon_source_directed_em_normal_current import normal_left_current_gaunt
from bhsm.interface.muon_piecewise_euclidean_action import FAMILY_INDICES
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(output,*,source_folder,matching_folder,native_folder,action_folder,amputation_folder):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every boundary/source application')
    refs={};archives={};out.mkdir(parents=True)
    def read(path,expected=None):
        p=ROOT/path;raw=p.read_bytes();h=sha256(raw).hexdigest()
        if expected is not None and h!=expected:raise ValueError('same boundary/source pin changed: '+str(path))
        refs[p.relative_to(ROOT).as_posix()]=h
        if p.suffix=='.json':return json.loads(raw)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def shards(folder,prefix):
        md=read(folder/'result.json');names=sorted((k for k in md['archives']if k.startswith(prefix)),
            key=lambda k:int(Path(k).stem.rsplit('_',1)[1]))
        a=[read(folder/k,md['archives'][k]['sha256'])for k in names]
        if not a:raise ValueError('complete saved source/clock rows required')
        return md,{k:np.concatenate([b[k]for b in a])for k in a[0]if np.asarray(a[0][k]).ndim}
    def save(name,data):
        p=out/name;_compressed_npz(p,data)
        if p.stat().st_size>=10*1024**2:raise RuntimeError('split complete source return rows')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    sm,walls=shards(source_folder,'actual_global_current_wall_nodes_')
    nm,nodes=shards(native_folder,'native_coframe_nodes_')
    mm,matched=shards(matching_folder,'converged_body_and_dual_nodes_')
    _,sourcepoints=shards(action_folder,'owned_current_point_sources_')
    if (sm['family']!=mm['family']or not np.array_equal(nodes['rows'],matched['same_original_rows'])
            or not np.array_equal(nodes['rows'],sourcepoints['rows'])
            or not np.array_equal(nodes['measure'],matched['same_native_geometric_measure'])):
        raise ValueError('same corrected body, incidence, source and positive reference measure required')
    family=sm['family'];fi=FAMILY_INDICES[family]
    alpha=lepton_current_hilbert_representation()['alpha'][:,fi][:,:,fi]
    G=normal_left_current_gaunt()['gaunt'];q=[];components=[[]for _ in range(4)]
    for j in range(len(nodes['measure'])):
        qi={k:v[j]for k,v in nodes.items()}
        qi['rows']=tuple((int(a.real),complex(b),complex(c))for a,b,c in qi['rows'])
        qi.update(H=matched['right_body'][j],Hsharp=matched['separately_reflected_base_body'][j],source_point_index=j)
        def image(label):
            return native_images_of_current_direction(walls[label+'_wall_coefficients'][j],
                radius=qi['R'],lapse=qi['N'],reflected_radius=qi['Rsharp'],reflected_lapse=qi['Nsharp'],
                family=family,even_field_odd_gaunt=G)
        u,p=image('u'),image('p')
        c=even_current_source_components(u['even_from_odd_source'][0],p['odd_from_even_source'][0])
        for k,a in enumerate(c):components[k].append(a)
        q.append(qi)
    records=[];totals={};n=int(nm['temporal_nodes'])
    for ci,component in enumerate(components):
        degree=component[0]['degree'];spectator=component[0]['spectator']
        Eang=homogeneous_scalar_degree_reduction(degree)['angular_derivatives']
        def source(qi):
            a=component[qi['source_point_index']];return a['right_source'],a['literal_left']
        f=shifted_boundary_forms(q,temporal_nodes=n,angular_derivatives=Eang,alpha=alpha,source_sampler=source)
        a=_assemble_matching_forms(q,temporal_nodes=n,angular_derivatives=Eang,alpha=alpha,source_sampler=source)
        base=f['forms']['native_reflected_envelope'][0]
        blocks={'K_'+key:value for key,value in base.items()}
        blocks.update({'M_'+key:np.zeros_like(value)for key,value in base.items()})
        P=tuple(a['weak_factors']['geometric'][k]for k in('diagonal','upper','lower'))
        r=source_corrected_form_core_return(blocks,f['acted_source_numerator'],f['analytic_literal_left_moments'],
            weak_factor=P,source_moments=f['geometric_source_moments'])
        currents={k:r[k]for k in('natural_literal_current','form_core_literal_current','forced_return_literal_current',
            'independent_natural_transpose_current','independent_form_core_transpose_current')}
        for k,v in currents.items():totals[k]=totals.get(k,0)+v
        save(f'degree_{degree}_spectator_{spectator}_currents_and_final_source.npz',dict(currents,
            source_corrected_final_conormal=r['source_corrected_final_conormal'],
            final_acted_source_numerator=f['acted_source_numerator'][-1],
            source_corrected_final_conormal_omitting_source=r['source_corrected_final_conormal_omitting_source'],
            final_face_Green=r['final_face_Green'],final_return_amplitude=r['final_return_amplitude']))
        for start in range(0,n-1,128):
            stop=min(start+128,n-1);sl=slice(start,stop)
            data={k:r[k][sl]for k in('natural_solution','form_core_solution','forced_final_face_return',
                'natural_square_transpose_adjoint','form_core_square_transpose_adjoint',
                'unsquared_forced_source_return','form_core_unsquared_source_rows')}
            save(f'degree_{degree}_spectator_{spectator}_source_return_nodes_{start+1}.npz',data)
            poly={f'{name}_order_{order}_{key}':value[sl] for name,series in f['forms'].items()
                for order,b in enumerate(series)for key,value in b.items()}
            save(f'degree_{degree}_spectator_{spectator}_energy_polynomials_nodes_{start+1}.npz',poly)
        norm=lambda x:float(np.linalg.norm(x))
        diagnostic=dict(degree=degree,spectator=spectator,
            natural_current_norm=norm(r['natural_literal_current']),
            form_core_current_norm=norm(r['form_core_literal_current']),
            current_forced_return_norm=norm(r['forced_return_literal_current']),
            actual_source_conormal_contact_norm=norm(f['acted_source_numerator'][-1]),
            natural_current_transpose_defect_max=float(np.max(abs(r['natural_literal_current']-r['independent_natural_transpose_current']))),
            form_core_current_transpose_defect_max=float(np.max(abs(r['form_core_literal_current']-r['independent_form_core_transpose_current']))),
            independent_restriction_defect_max=float(np.max(abs(r['independent_restriction_defect']))),
            core_bulk_original_rows_max=float(np.max(abs(r['form_core_original_row_residual'][:-1]))),
            core_final_trace_max=float(np.max(abs(r['terminal_Dirichlet_trace']))),
            source_corrected_final_conormal_norm=norm(r['source_corrected_final_conormal']),
            unsquared_forced_source_return_norm=norm(r['unsquared_forced_source_return']),
            native_reflected_vs_true_Hilbert_square_max=max(float(np.max(abs(base[k]-f['forms']['Hilbert_shift'][0][k])))for k in base),
            analytic_envelope_vs_Hilbert_energy_first_norm=sum(norm(f['forms']['analytic_envelope'][1][k]-f['forms']['Hilbert_shift'][1][k])for k in base),
            independent_reflected_body_defect=f['independent_reflected_body_defect'])
        records.append(diagnostic);print(json.dumps(dict(stage='actual_boundary_source_return',**diagnostic),sort_keys=True),flush=True)
    save('complete_n0_n2_source_corrected_currents.npz',totals)
    _,edges=shards(amputation_folder,'original_full_body_edge_germs_')
    trace_records=[]
    for degree,key in((0,'full18_n0_body'),(1,'full36_n1_spectator_body')):
        transport=cauchy_external_trace_maps(edges['proper_steps'],edges[key],energy=0.)
        fields={k:v for k,v in transport.items()if isinstance(v,np.ndarray)}
        for start in range(0,len(edges[key])+1,128):
            save(f'fullbody_degree_{degree}_external_trace_nodes_{start}.npz',
                {k:v[start:start+128]for k,v in fields.items()if v.shape[0]==len(edges[key])+1})
        boundary=transport['initial_and_terminal_Dirichlet_boundary_residual']
        save(f'fullbody_degree_{degree}_finite_boundary_maps.npz',dict(
            rectangular_initial_and_terminal_Dirichlet_boundary_residual=boundary,
            initial_zero_free_final_boundary_initial=np.eye(len(edges[key][0])),
            initial_zero_free_final_boundary_final=np.zeros_like(edges[key][0]),
            source_final_endpoint_transport=transport['physical_right_trace_map'][-1]))
        trace_records.append(dict(degree=degree,dimension=edges[key].shape[-1],
            rectangular_boundary_rows=boundary.shape[0],rectangular_boundary_rank=int(np.linalg.matrix_rank(boundary)),
            smallest_boundary_singular_value=float(np.linalg.svd(boundary,compute_uv=False)[-1]),
            analytic_dual_pairing_residual_max=float(np.max(abs(transport['analytic_dual_pairing_residual']))),
            physical_external_energy_phase_cancellation_max=float(np.max(abs(transport['physical_right_trace_map_energy_first'])))))
        if degree==0:
            pointR=[];pointL=[]
            for j,qi in enumerate(q):
                edge=qi['rows'][0][0];fraction=qi['rows'][1][1]
                R=expm(-fraction*edges['proper_steps'][edge]*edges[key][edge])@transport['physical_right_trace_map'][edge]
                L=np.linalg.solve(R.T,np.eye(18))
                pointR.append(R[np.ix_(fi,fi)]);pointL.append(L[np.ix_(fi,fi)])
            pointR=np.array(pointR);pointL=np.array(pointL);tau=sourcepoints['current_proper_clock']
            for start in range(0,len(q),128):
                sl=slice(start,start+128)
                save(f'family_{family}_exterior_point_trace_maps_{start}.npz',dict(
                    envelope_right_trace_map=pointR[sl],envelope_analytic_left_trace_map=pointL[sl],
                    envelope_right_trace_map_energy_first=tau[sl,None,None]*pointR[sl],
                    envelope_analytic_left_trace_map_energy_first=-tau[sl,None,None]*pointL[sl],
                    physical_right_trace_map=pointR[sl],physical_analytic_left_trace_map=pointL[sl],
                    physical_right_trace_map_energy_first=np.zeros_like(pointR[sl]),
                    physical_analytic_left_trace_map_energy_first=np.zeros_like(pointL[sl]),
                    original_quadrature_index=np.arange(len(q))[sl],same_original_rows=nodes['rows'][sl],
                    owned_external_source_clock=tau[sl],family_indices=np.asarray(fi)))
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p:
            try:rel=Path(p).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_shifted_boundary_source.py'):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('actual source/operator pins changed')
    result=dict(classification='EVALUATED_SHIFTED_BOUNDARY_SOURCE_AND_ACTUAL_FINITE_FRIEDRICHS_RETURN',
        input_hashes=refs,archives=archives,records=records,external_trace_records=trace_records,
        family=family,original_source_column=sm['source_column_index'],source_column_is_named_test_not_physical_state=True,
        angular_image='complete n0+n2 with all three n2 source spectator applications',
        common_canonical_reset_chart='identity as declared by existing graph; raw-Psi density reset is not inferred',
        native_body='actual updated chronological W+Omega; independent separately reflected base retained',
        energy_anchor=0.,energy_polynomials_before_boundary_restriction=True,
        analytic_external_envelope='right A-E; independent left A_sharp+E*w/ws, SAME forward clock',
        true_Hilbert_shift='(A-E)^dagger geometric_G (A-E) for real E; no spectral z=E^2 substitution',
        point_trace_maps='envelope phi at E0, with +tau/-tau jets; physical chi phase cancels exactly in the declared Cauchy graph',
        point_body_scope='same explicit whole-full18 edge-average germ; within-edge variation inherited as unbounded operand',
        finite_Friedrichs_edge_identified_with_physical_stop=False,
        first_order_exterior_pole_or_physical_mass_selected=False,
        full_source_corrected_conormal_and_original_square_transpose_retained=True,
        square_spectral_z_identified_with_external_energy_squared=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 source-return and boundary identities on the saved finite graph; no physical pole/LSZ, contour, continuum or Pauli error bound')
    result['total_natural_current_norm']=float(np.linalg.norm(totals['natural_literal_current']))
    result['total_form_core_current_norm']=float(np.linalg.norm(totals['form_core_literal_current']))
    result['total_forced_return_current_norm']=float(np.linalg.norm(totals['forced_return_literal_current']))
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='shifted_boundary_source_complete',result_sha256=sha256(p.read_bytes()).hexdigest(),
        total_natural_current_norm=result['total_natural_current_norm'],total_form_core_current_norm=result['total_form_core_current_norm'],
        total_forced_return_current_norm=result['total_forced_return_current_norm'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--source-folder',type=Path,default=Path('artifacts/muon_global_current_native_matching_20261011/incoming_family_1_column208_run_1'))
    p.add_argument('--matching-folder',type=Path,default=Path('artifacts/muon_chronological_current_matching_20261011/incoming_family_1_run_1'))
    p.add_argument('--native-folder',type=Path,default=Path('artifacts/muon_transported_native_pairing_20261011/run_1'))
    p.add_argument('--action-folder',type=Path,default=Path('artifacts/muon_chronological_n1_field_action_20261011/run_1'))
    p.add_argument('--amputation-folder',type=Path,default=Path('artifacts/muon_chronological_current_amputation_20261011/run_1'))
    a=p.parse_args();materialize(a.output,source_folder=a.source_folder,matching_folder=a.matching_folder,
        native_folder=a.native_folder,action_folder=a.action_folder,amputation_folder=a.amputation_folder)
