"""Apply owned Cauchy traces before the original full-graph current inversion.

The same field operator is used for both source arms, all C6 external
columns and each complete n1 spectator. The original FE2 functions are
current tests only. No finite native heat or external pole is grafted.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys,warnings,gc
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_reached_trace_action import deterministic_archive
from bhsm.interface.muon_chronological_current_factor import factor_literal_current_chain,solve_literal_current_chain
from bhsm.interface.muon_chronological_kkt_equilibration import equilibrate_chronological_kkt
from bhsm.interface.muon_chronological_literal_current_source import literal_point_current_sources,add_literal_point_source,source_column_indices
from bhsm.interface.muon_chronological_cauchy_trace_current import cauchy_trace_point_sources
from bhsm.interface.muon_chronological_exterior_current_source import exterior_current_transfer


def materialize(action_folder,trace_folder,baseline_transfer_folder,output,*,source_side):
    family=1;current_kind="literal"
    base=ROOT/action_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve every current action application')
    refs={}
    def read(p,expected=None):
        h=sha256(p.read_bytes()).hexdigest()
        if expected is not None and h!=expected:raise ValueError('the same current operator/source changed: '+str(p))
        if out not in p.parents:refs[p.relative_to(ROOT).as_posix()]=h
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read(base/'result.json');refs.update(md['input_hashes'])
    incidence=read(base/'original_n1_angular_and_source_incidence.npz',md['archives']['original_n1_angular_and_source_incidence.npz']['sha256'])
    files=sorted(base.glob('original_reduced_n1_KKT_blocks_*.npz'),key=lambda p:int(p.stem.rsplit('_',1)[1]))
    D=np.empty((1150,176,176),complex);U=np.empty((1149,176,176),complex);L=np.empty_like(U)
    for p in files:
        a=read(p,md['archives'][p.name]['sha256']);s=int(a['node_start'])-1;e=int(a['node_stop_exclusive'])-1
        D[s:e]=a['KKT_diagonal'];U[s:s+len(a['KKT_upper'])]=a['KKT_upper'];L[s:s+len(a['KKT_lower'])]=a['KKT_lower']
    initial=read(base/'original_n1_initial_face_reactions.npz',md['archives']['original_n1_initial_face_reactions.npz']['sha256'])
    point_files=sorted(base.glob('owned_current_point_sources_*.npz'),key=lambda p:int(p.stem.rsplit('_',1)[1]))
    pieces=[read(p,md['archives'][p.name]['sha256'])for p in point_files]
    points={k:np.concatenate([a[k]for a in pieces])for k in pieces[0]};del pieces
    if len(points['measure'])!=3832:raise ValueError('all original source/corner points required')
    tracebase=ROOT/trace_folder;tm=read(tracebase/'result.json');refs.update(tm['input_hashes'])
    tracefiles=sorted(tracebase.glob('family_1_exterior_point_trace_maps_*.npz'),key=lambda p:int(p.stem.rsplit('_',1)[1]))
    shards=[read(p,tm['archives'][p.name]['sha256'])for p in tracefiles]
    traces={k:np.concatenate([a[k]for a in shards])for k in shards[0]if k!='family_indices'}
    if not np.array_equal(traces['original_quadrature_index'],np.arange(3832)):
        raise ValueError('every SAME original source point must be supplied in order')
    if not np.array_equal(traces['same_original_rows'],points['rows']):
        raise ValueError('Cauchy source maps must use SAME original field/corner incidence')
    if not np.array_equal(traces['owned_external_source_clock'],points['current_proper_clock']):
        raise ValueError('Cauchy maps and explicit phases must use SAME owned proper clock')
    fixedbase=ROOT/baseline_transfer_folder;fixedmd=read(fixedbase/'result.json');refs.update(fixedmd['input_hashes'])
    if fixedmd['source_side']!=source_side or fixedmd['family']!=family:
        raise ValueError('fixed-frame comparison must have SAME source arm and family')
    fixed=read(fixedbase/'complete288_source_transfer.npz',fixedmd['archives']['complete288_source_transfer.npz']['sha256'])
    del shards

    arm=np.asarray(incidence['quadrature_provenance'][:,5].real,int)
    at=np.flatnonzero(arm==(0 if source_side=='incoming'else 1))
    vertex_key='current_vertices'if current_kind=='literal'else'selected_EM_current_vertices'
    # Per-coordinate congruence is reversible; original residuals below
    # reload the unchanged operator rather than use the equilibrated one.
    print(json.dumps(dict(stage='original_current_KKT_equilibration',blocks=1150,rows_per_block=176)),flush=True)
    eq=equilibrate_chronological_kkt(D,U,L);del D,U,L;gc.collect()
    scales=eq['coordinate_scales'];history=eq['equilibration_history']
    with warnings.catch_warnings(record=True)as factor_warnings:
        warnings.simplefilter('always')
        f=factor_literal_current_chain(eq['diagonal'],eq['upper'],eq['lower'],consume_diagonal=True)
    del eq;gc.collect()
    warning_text=[str(w.message)for w in factor_warnings]
    if warning_text:raise ArithmeticError('original Gauss/frame chain produced LU warnings; no numerical gauge deletion permitted: '+str(warning_text))
    print(json.dumps(dict(stage='original_current_full_factor_complete',minimum_LU_pivot=float(min(f['minimum_LU_pivots'])))),flush=True)
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256(Path(path).read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),'scripts/evaluate_muon_reached_trace_action.py',
        'tests/test_muon_chronological_current_factor.py','tests/test_muon_chronological_literal_current_source.py',
        'tests/test_muon_chronological_cauchy_trace_current.py'):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    out.mkdir(parents=True);archives={};records=[]
    def save(name,data):
        p=out/name;deterministic_archive(p,data)
        if p.stat().st_size>=10*1024**2:raise ArithmeticError('split complete current columns without deleting arrays')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    save('current_source_and_operator_incidence.npz',dict(current_column_shape=np.array([6,2,6,4]),
        current_source_quadrature_indices=at,source_side=np.array(source_side),family=np.array(family),
        original_KKT_coordinate_scales=scales,original_spectator_indices=incidence['spectator_field_indices'],
        real_to_complex=incidence['real_to_complex'],minimum_LU_pivots=f['minimum_LU_pivots']))
    for spectator in range(2):
        Rlift=incidence['right_current_field_source_lifts'][spectator]
        Llift=incidence['literal_left_current_field_source_lifts'][spectator]
        for spin in range(6):
            columns=source_column_indices(external_spin=spin)
            jr=np.zeros((1150,176,48),complex);jl=np.zeros_like(jr)
            ri=np.zeros((176,48),complex);li=np.zeros_like(ri)
            jrE=np.zeros_like(jr);jlE=np.zeros_like(jl);riE=np.zeros_like(ri);liE=np.zeros_like(li)
            point_energy_cancel=0.;point_energy_contact=0.
            for iq in at:
                point={k:points[k][iq]for k in('measure','rows')}
                local=literal_point_current_sources(points[vertex_key][iq,family-1],points['current_FE2_values'][iq],Rlift,Llift)
                local=cauchy_trace_point_sources(local,points['current_proper_clock'][iq],
                    right_trace=traces['envelope_right_trace_map'][iq],
                    left_trace=traces['envelope_analytic_left_trace_map'][iq],
                    right_trace_energy_first=traces['envelope_right_trace_map_energy_first'][iq],
                    left_trace_energy_first=traces['envelope_analytic_left_trace_map_energy_first'][iq])
                point_energy_cancel=max(point_energy_cancel,float(max(np.max(abs(local['right_energy_source'])),np.max(abs(local['left_energy_source'])))))
                point_energy_contact=max(point_energy_contact,float(max(np.max(abs(local['right_phase_energy_contact'])),np.max(abs(local['left_phase_energy_contact'])))))
                add_literal_point_source(jrE,riE,point,local['right_energy_source'],columns=columns)
                add_literal_point_source(jlE,liE,point,local['left_energy_source'],columns=columns)
                add_literal_point_source(jr,ri,point,local['literal_right_source'],columns=columns)
                add_literal_point_source(jl,li,point,local['literal_left_transpose_source'],columns=columns)
            u=scales[:,:,None]*solve_literal_current_chain(f,scales[:,:,None]*jr)
            p=scales[:,:,None]*solve_literal_current_chain(f,scales[:,:,None]*jl,transpose=True)
            if not np.isfinite(u).all()or not np.isfinite(p).all():raise ArithmeticError('actual current source produced nonfinite original response')
            # Every original equation, Gauss and frame residual is applied
            # from the supplied directed blocks, including cross-shard rows.
            ur=-jr.copy();pr=-jl.copy();sizeu=abs(jr);sizep=abs(jl)
            for path in files:
                a=read(path,md['archives'][path.name]['sha256']);s=int(a['node_start'])-1;e=int(a['node_stop_exclusive'])-1
                Ad,Au,Al=(a[k]for k in('KKT_diagonal','KKT_upper','KKT_lower'))
                ur[s:e]+=Ad@u[s:e];pr[s:e]+=Ad.transpose(0,2,1)@p[s:e]
                sizeu[s:e]+=abs(Ad)@abs(u[s:e]);sizep[s:e]+=abs(Ad.transpose(0,2,1))@abs(p[s:e])
                t=s+len(Au)
                ur[s:t]+=Au@u[s+1:t+1];ur[s+1:t+1]+=Al@u[s:t]
                pr[s:t]+=Al.transpose(0,2,1)@p[s+1:t+1];pr[s+1:t+1]+=Au.transpose(0,2,1)@p[s:t]
                sizeu[s:t]+=abs(Au)@abs(u[s+1:t+1]);sizeu[s+1:t+1]+=abs(Al)@abs(u[s:t])
                sizep[s:t]+=abs(Al.transpose(0,2,1))@abs(p[s+1:t+1]);sizep[s+1:t+1]+=abs(Au.transpose(0,2,1))@abs(p[s:t])
            left_pair=np.einsum('nai,naj->ij',jl,u,optimize=True)
            transpose_pair=np.einsum('nai,naj->ij',p,jr,optimize=True)
            prefix=f'spectator_{spectator}_external_{spin}'
            for start in range(0,1150,8):
                stop=min(start+8,1150)
                save(f'{prefix}_nodes_{start+1}.npz',dict(original_node_start=np.array(start+1),original_node_stop_exclusive=np.array(stop+1),
                    source_column_indices=columns,original_literal_right_current_source=jr[start:stop],
                    original_literal_left_transpose_source=jl[start:stop],original_current_response=u[start:stop],
                    original_transpose_current_adjoint=p[start:stop],original_response_residual=ur[start:stop],
                    original_transpose_adjoint_residual=pr[start:stop],
                    exterior_right_energy_source=jrE[start:stop],exterior_left_energy_source=jlE[start:stop]))
            save(prefix+'_source_pairing_and_faces.npz',dict(source_column_indices=columns,
                literal_left_right_pairing=left_pair,literal_transpose_pairing=transpose_pair,
                original_initial_right_source_reaction=ri,original_initial_left_source_reaction=li,
                original_initial_right_energy_reaction=riE,original_initial_left_energy_reaction=liE,
                original_initial_current_reaction=initial['initial_to_first_Hessian']@u[0,:168]-ri[:168],
                original_initial_adjoint_reaction=initial['first_to_initial_Hessian'].T@p[0,:168]-li[:168],
                original_final_current_response=u[-1],original_final_transpose_adjoint=p[-1],
                original_birth_current_response=u[574],original_birth_transpose_adjoint=p[574]))
            row=dict(spectator=spectator,external_spin=spin,point_energy_phase_trace_cancellation_max=point_energy_cancel,point_individual_energy_contact_max=point_energy_contact,integrated_right_energy_source_norm=float(np.linalg.norm(jrE)),integrated_left_energy_source_norm=float(np.linalg.norm(jlE)),literal_right_source_norm=float(np.linalg.norm(jr)),
                literal_left_source_norm=float(np.linalg.norm(jl)),full_current_response_norm=float(np.linalg.norm(u)),
                full_transpose_adjoint_norm=float(np.linalg.norm(p)),induced_H_response_norm=float(np.linalg.norm(u[:,160:168])),
                induced_H_adjoint_norm=float(np.linalg.norm(p[:,160:168])),
                original_current_row_residual_max=float(np.max(abs(ur))),original_transpose_row_residual_max=float(np.max(abs(pr))),
                original_current_Gauss_residual_max=float(np.max(abs(ur[:,:32]))),
                original_transpose_Gauss_residual_max=float(np.max(abs(pr[:,:32]))),
                original_current_frame_residual_max=float(np.max(abs(ur[:,168:]))),
                original_transpose_frame_residual_max=float(np.max(abs(pr[:,168:]))),
                original_current_componentwise_backward_error_max=float(np.max(abs(ur)/np.maximum(sizeu,np.finfo(float).tiny))),
                original_transpose_componentwise_backward_error_max=float(np.max(abs(pr)/np.maximum(sizep,np.finfo(float).tiny))),
                literal_source_transpose_pairing_difference_max=float(np.max(abs(left_pair-transpose_pair))))
            records.append(row);print(json.dumps(dict(stage='original_current_complete48_test_column_batch',**row)),flush=True)
            del jr,jl,jrE,jlE,u,p,ur,pr,sizeu,sizep;gc.collect()

    # Every cross-external entry is contracted from the actual solved
    # sources, preserving the structural C6 maps before integration.
    complete={k:np.zeros((288,288),complex)for k in ('exterior_source_transfer',
        'independent_transpose_transfer','left_energy_contact','right_energy_contact',
        'operator_energy_contact','continued_energy_first','real_proper_frequency_first')}
    for spectator in range(2):
        spec={k:np.zeros_like(v)for k,v in complete.items()}
        for start in range(0,1150,8):
            arrays={k:[]for k in ('original_literal_left_transpose_source','original_literal_right_current_source',
                'original_current_response','original_transpose_current_adjoint','exterior_left_energy_source','exterior_right_energy_source')}
            for spin in range(6):
                name=f'spectator_{spectator}_external_{spin}_nodes_{start+1}.npz'
                a=read(out/name,archives[name]['sha256'])
                if not np.array_equal(a['source_column_indices'],np.arange(spin*48,(spin+1)*48)):
                    raise ValueError('all288 exact C6/internal column coordinates required')
                for k in arrays:arrays[k].append(a[k])
            a={k:np.concatenate(v,axis=2)for k,v in arrays.items()}
            t=exterior_current_transfer(*(a[k]for k in arrays),operator_energy_response=np.zeros_like(a['original_current_response']))
            for k in spec:spec[k]+=t[k]
        save(f'spectator_{spectator}_complete288_Cauchy_transfer.npz',spec)
        for k in complete:complete[k]+=spec[k]
    complete['fixed_frame_source_transfer']=fixed['source_transfer']
    complete['transported_minus_fixed_frame_source_transfer']=complete['exterior_source_transfer']-fixed['source_transfer']
    complete['same_external_C6_internal_column_shape']=np.array([6,2,6,4])
    save('complete288_Cauchy_source_transfer.npz',complete)
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same original current source changed')
    result=dict(classification='EVALUATED_COMPLETE_CAUCHY_POINT_TRACE_ORIGINAL_CHRONOLOGICAL_CURRENT',input_hashes=refs,archives=archives,records=records,
        source_side=source_side,family=family,current_kind=current_kind,original_free_temporal_nodes=1150,
        original_full_n1_field_rows=1150*336,original_At_Gauss_rows=1150*64,named_frame_rows=1150*16,
        exact_spectators=2,complete_internal_current_tests=48,complete_external_C6_columns=6,full_right_source_columns=288,
        full_induced_H_and_original_Gauss_frame_corner_returns_retained=True,source_arm_solved_on_full_joined_field_operator=True,
        source_arms_identified_by_equal_test_coefficient_indices=False,source_vertices_or_coefficients_conjugated=False,
        literal_transpose_is_Hilbert_dagger=False,A_sharp_or_fermion_inverse_folded_into_current=False,
        original_initial_face_held=0,original_final_natural_face_retained=1150,common_birth_real_node=575,
        LU_warnings=warning_text,equilibration_history=history,full_inverse_materialized=False,
        native_graded_source_or_relative_heat_or_physical_exterior_state_identified=False,
        physical_a_mu=None,physical_g_mu=None,
        exterior_point_trace_packet=trace_folder.as_posix(),fixed_frame_transfer_packet=baseline_transfer_folder.as_posix(),
        exterior_trace_maps_are_complete_initial_data_Cauchy_not_selected_bands=True,
        exterior_point_energy_anchor=0,internal_operator_energy_action_explicitly_held_zero=True,
        complete_transfer_norm=float(np.linalg.norm(complete['exterior_source_transfer'])),
        complete_current_change_norm=float(np.linalg.norm(complete['transported_minus_fixed_frame_source_transfer'])),
        complete_independent_transpose_defect_max=float(np.max(abs(complete['exterior_source_transfer']-complete['independent_transpose_transfer']))),
        complete_continued_energy_first_norm=float(np.linalg.norm(complete['continued_energy_first'])),
        envelope_phase_cancellation_is_physical_band_motion=False,
        error_scope='binary64 literal original weak source and all action/transpose/Gauss/frame residuals. The48 tests retain their owned FE2 source germ; no original source production, physical loop domain, pole/LSZ, graded own-mean or Pauli enclosure is inferred.')
    rp=out/'result.json';rp.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(rp.read_bytes()).hexdigest(),files=len(archives),max_archive_bytes=max(a['bytes']for a in archives.values()))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--action-folder',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--trace-folder',type=Path,required=True);p.add_argument('--baseline-transfer-folder',type=Path,required=True)
    p.add_argument('--source-side',choices=('incoming','outgoing'),required=True)
    a=p.parse_args();materialize(a.action_folder,a.trace_folder,a.baseline_transfer_folder,a.output,source_side=a.source_side)
