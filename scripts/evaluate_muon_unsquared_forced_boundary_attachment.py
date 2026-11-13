"""Apply actual u/p source-corrected unsquared boundary/current returns."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_unsquared_forced_boundary_attachment import source_corrected_unsquared_return
from bhsm.interface.muon_native_unsquared_domain_matching import _assemble_matching_forms
from bhsm.interface.muon_chronological_current_source_images import native_images_of_current_direction
from bhsm.interface.muon_global_current_wall_loader import even_current_source_components
from bhsm.interface.muon_chronological_clifford_graph import chronological_clifford_blocks
from bhsm.interface.muon_chronological_spectral_blocks import (
    homogeneous_scalar_degree_reduction,chronological_spectral_factor,chronological_source_solve)
from bhsm.interface.muon_native_reset_friedrichs_return import chain_apply
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from bhsm.interface.muon_source_directed_em_normal_current import normal_left_current_gaunt
from bhsm.interface.muon_piecewise_euclidean_action import FAMILY_INDICES
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(output,*,source_folder,matching_folder,native_folder,action_folder,boundary_folder):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every unsquared forced-source application')
    refs={};archives={}
    def read(path,expected=None):
        p=ROOT/path;b=p.read_bytes();h=sha256(b).hexdigest()
        if expected is not None and h!=expected:raise ValueError('same source/domain pin changed: '+str(path))
        refs[p.relative_to(ROOT).as_posix()]=h
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def shard(folder,md,prefix):
        names=sorted((k for k in md['archives']if k.startswith(prefix)),
                     key=lambda k:int(Path(k).stem.rsplit('_',1)[1]))
        data=[read(folder/k,md['archives'][k]['sha256'])for k in names]
        if not data:raise ValueError('complete source/domain shard prefix required: '+prefix)
        return {k:np.concatenate([x[k]for x in data]) for k in data[0]if np.asarray(data[0][k]).ndim}
    sm,nm,mm,am,bm=(read(f/'result.json')for f in
        (source_folder,native_folder,matching_folder,action_folder,boundary_folder))
    wall=shard(source_folder,sm,'actual_global_current_wall_nodes_')
    node=shard(native_folder,nm,'native_coframe_nodes_')
    matched=shard(matching_folder,mm,'converged_body_and_dual_nodes_')
    point=shard(action_folder,am,'owned_current_point_sources_')
    if (sm['family']!=mm['family']or not np.array_equal(node['rows'],matched['same_original_rows'])
            or not np.array_equal(node['rows'],point['rows'])
            or not np.array_equal(node['measure'],matched['same_native_geometric_measure'])):
        raise ValueError('same converged body, source, original incidence and both measures required')
    family=sm['family'];fi=FAMILY_INDICES[family]
    alpha=lepton_current_hilbert_representation()['alpha'][:,fi][:,:,fi]
    gaunt=normal_left_current_gaunt()['gaunt'];q=[];components=[[]for _ in range(4)]
    for j in range(len(node['measure'])):
        qi={k:v[j]for k,v in node.items()}
        qi['rows']=tuple((int(a.real),complex(b),complex(c))for a,b,c in qi['rows'])
        qi.update(H=matched['right_body'][j],Hsharp=matched['separately_reflected_base_body'][j],
                  index=j,source_energy_clock=point['current_proper_clock'][j])
        images=[]
        for label in('u','p'):
            images.append(native_images_of_current_direction(wall[label+'_wall_coefficients'][j],
                radius=qi['R'],lapse=qi['N'],reflected_radius=qi['Rsharp'],reflected_lapse=qi['Nsharp'],
                family=family,even_field_odd_gaunt=gaunt))
        for target,a in zip(components,even_current_source_components(
                images[0]['even_from_odd_source'][0],images[1]['odd_from_even_source'][0])):
            target.append(a)
        q.append(qi)
    out.mkdir(parents=True)
    def save(name,data):
        p=out/name;_compressed_npz(p,data)
        if p.stat().st_size>10*1024**2:raise ValueError('split original source rows; archive cap exceeded')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    n=int(nm['temporal_nodes']);records=[];totals={}
    for component in components:
        degree,spectator=(component[0][k]for k in('degree','spectator'))
        E=homogeneous_scalar_degree_reduction(degree)['angular_derivatives']
        def source(qi):
            a=component[qi['index']];return a['right_source'],a['literal_left']
        def source_first(qi):
            R,L=source(qi);tau=qi['source_energy_clock'];return -tau*R,tau*L
        forms=_assemble_matching_forms(q,temporal_nodes=n,angular_derivatives=E,alpha=alpha,source_sampler=source)
        first=_assemble_matching_forms(q,temporal_nodes=n,angular_derivatives=E,alpha=alpha,source_sampler=source_first)
        prefix=f'degree_{degree}_spectator_{spectator}'
        saved=shard(boundary_folder,bm,prefix+'_source_return_nodes_')
        final_name=prefix+'_currents_and_final_source.npz'
        final=read(boundary_folder/final_name,bm['archives'][final_name]['sha256'])
        block=chronological_clifford_blocks(q,temporal_nodes=n,angular_derivatives=E,alpha=alpha)
        K=tuple(block['K_'+k]for k in('diagonal','upper','lower'))
        fN=chronological_spectral_factor(*K)
        dxN=np.asarray(chronological_source_solve(fN,first['independently_acted_source_numerator']))
        dxD=np.zeros_like(dxN)
        fD=chronological_spectral_factor(K[0][:-1],K[1][:-1],K[2][:-1])
        dxD[:-1]=np.asarray(chronological_source_solve(fD,first['independently_acted_source_numerator'][:-1]))
        P=tuple(forms['weak_factors']['analytic'][k]for k in('diagonal','upper','lower'))
        result=source_corrected_unsquared_return(P,forms['right_moments']['analytic'],forms['left_moments']['analytic'],
            saved['natural_solution'],saved['form_core_solution'],weak_factor_first=tuple(np.zeros_like(a)for a in P),
            right_moments_first=first['right_moments']['analytic'],literal_left_first=first['left_moments']['analytic'],
            natural_square_response_first=dxN,core_square_response_first=dxD)
        current_keys=[k for k in result if 'current' in k and isinstance(result[k],np.ndarray)]
        for key in current_keys:totals[key]=totals.get(key,0)+result[key]
        compact={k:result[k]for k in current_keys}
        for label,data in(('native_natural',saved['natural_solution']),('native_core',saved['form_core_solution']),
                           ('original_unsquared',result['unsquared_response'])):
            compact[label+'_birth_trace']=data[574]
            compact[label+'_final_trace']=data[-1]
        compact.update(source_corrected_square_final_conormal=final['source_corrected_final_conormal'],
            actual_final_acted_source=final['final_acted_source_numerator'],
            unsquared_core_final_range_source=result['core_range_source'][-1],
            unsquared_forced_final_source=result['forced_unsquared_boundary_source'][-1])
        save(prefix+'_boundary_current_application.npz',compact)
        for start in range(0,n-1,128):
            sl=slice(start,min(start+128,n-1))
            save(prefix+f'_original_source_return_rows_{start+1}.npz',{
                k:result[k][sl]for k in('natural_range_source','core_range_source','forced_unsquared_boundary_source',
                    'forced_unsquared_boundary_source_first','original_unsquared_rows','original_unsquared_transpose_rows')})
        maxabs=lambda a:float(np.max(abs(a)))
        norm=lambda a:float(np.linalg.norm(a))
        record=dict(degree=degree,spectator=spectator,
            actual_unsquared_current_norm=norm(result['actual_unsquared_current']),
            forced_boundary_current_norm=norm(result['forced_boundary_current']),
            forced_boundary_source_norm=norm(result['forced_unsquared_boundary_source']),
            core_range_source_norm=norm(result['core_range_source']),
            source_corrected_square_final_conormal_norm=norm(final['source_corrected_final_conormal']),
            core_source_return_current_identity_max=maxabs(result['core_square_current']-result['original_current_with_core_source_return']),
            forced_source_transpose_current_identity_max=maxabs(result['forced_boundary_current']-result['independent_forced_boundary_current']),
            forced_source_energy_transpose_identity_max=maxabs(result['forced_boundary_current_first']-result['independent_forced_boundary_current_first']),
            original_unsquared_rows_max=maxabs(result['original_unsquared_rows']),
            original_unsquared_transpose_rows_max=maxabs(result['original_unsquared_transpose_rows']),
            original_forced_source_rows_max=maxabs(result['forced_original_source_identity']),
            original_forced_source_energy_rows_max=maxabs(result['forced_original_source_first_identity']),
            stored_square_natural_rows_max=maxabs(chain_apply(*K,saved['natural_solution'])-forms['independently_acted_source_numerator']),
            stored_square_core_interior_rows_max=maxabs((chain_apply(*K,saved['form_core_solution'])-forms['independently_acted_source_numerator'])[:-1]),
            source_energy_clock_is_owned_FE2_clock=True)
        records.append(record);print(json.dumps(dict(stage='actual_unsquared_forced_boundary_application',**record),sort_keys=True),flush=True)
    save('complete_n0_n2_actual_source_boundary_currents.npz',totals)
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p:
            try:rel=Path(p).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for p in(Path(__file__),'tests/test_muon_unsquared_forced_boundary_attachment.py'):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same source/body/returned-domain pins changed')
    record=dict(classification='EVALUATED_ACTUAL_UP_UNSQUARED_FORCED_BOUNDARY_CURRENT_AND_SOURCE_ENERGY_CONTACT',
        input_hashes=refs,archives=archives,records=records,family=family,
        source_column_index=sm['source_column_index'],all_6_external_canonical_columns_retained=True,
        source_column_is_computational_test_not_physical_muon_state=True,
        source_image='full actual u/p original wall24 including induced H, complete n0+n2 three independent spectator returns',
        right_factor='A=w^-1 Ds+H on original holomorphic measure m',
        analytic_source_target_and_current_dual_conjugated=False,
        native_square_domain='same separately reflected base, geometric mu; initial value held and terminal Friedrichs core at finite edge',
        original_square_source_final_conormal_retained=True,
        square_range_source_and_forced_boundary_return_counted_once=True,
        energy_contact='source-only exp(-E tau_FE2) right and exp(+E tau_FE2) left at E0; original factor and square held',
        full_internal_operator_energy_or_magnetic_derivative_evaluated=False,
        boundary_jet_API='unsquared_boundary_source_two_jet retains all supplied trace/source/reset/exterior energy/magnetic maps; actual physical Bi/Bf unassigned',
        finite_final_core_edge_identified_with_physical_stop=False,
        square_spectral_parameter_identified_with_energy_squared=False,
        physical_reset_first_hit_pole_residue_or_Pauli_selected=False,
        error_scope='binary finite same-background source/current boundary application and original residuals; no physical exterior domain or observable enclosure')
    p=out/'result.json';p.write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='unsquared_forced_boundary_complete',result_sha256=sha256(p.read_bytes()).hexdigest(),
        total_current_norm=float(np.linalg.norm(totals['actual_unsquared_current'])),
        total_forced_return_norm=float(np.linalg.norm(totals['forced_boundary_current'])))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--source-folder',type=Path,default=Path('artifacts/muon_global_current_native_matching_20261011/incoming_family_1_column208_run_1'))
    p.add_argument('--matching-folder',type=Path,default=Path('artifacts/muon_chronological_current_matching_20261011/incoming_family_1_run_1'))
    p.add_argument('--native-folder',type=Path,default=Path('artifacts/muon_transported_native_pairing_20261011/run_1'))
    p.add_argument('--action-folder',type=Path,default=Path('artifacts/muon_chronological_n1_field_action_20261011/run_1'))
    p.add_argument('--boundary-folder',type=Path,default=Path('artifacts/muon_shifted_boundary_source_20261011/run_2'))
    a=p.parse_args();materialize(a.output,source_folder=a.source_folder,matching_folder=a.matching_folder,
        native_folder=a.native_folder,action_folder=a.action_folder,boundary_folder=a.boundary_folder)
