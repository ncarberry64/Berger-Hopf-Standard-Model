"""Stream original n1 field action on the converged whole chronological base.

The native heat domain is not changed by this classical action application.
Exact FE2 current test functions are analytically continued from their
owned source cell; all1151 field traces and restored corners remain.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_nonlinear_chronological_n0_action import chronological_n0_classical_binding
from evaluate_muon_continued_current_factor import retained_input
from evaluate_muon_reached_trace_action import deterministic_archive
from bhsm.interface.muon_chronological_harmonic_field_action import analytic_homogeneous_original_field_forms
from bhsm.interface.muon_nonlinear_chronological_n0_action import chronological_n0_field_lifts
from bhsm.interface.muon_chronological_spectral_blocks import homogeneous_scalar_degree_reduction
from bhsm.interface.muon_em_normal_connector_source import source_cell_field_chart,analytic_proper_clock,analytic_FE2_values
from bhsm.interface.muon_euclidean_angular_weak_action import euclidean_open_action_vertices
from bhsm.interface.muon_source_directed_em_normal_current import holomorphic_charge_projection


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every global n1 action application')
    a=chronological_n0_classical_binding();refs=a['input_hashes'];folder=ROOT/'artifacts/muon_chronological_n0_nonlinear_newton_20261011/run_1'
    def read(p):
        refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read(folder/'result.json');refs.update(md['input_hashes'])
    if not md['actual_classical_residual_max']<=md['classical_only_residual_tolerance']:
        raise ValueError('the literal complete-graph nonlinear classical base is required')
    shards=[]
    for p in sorted(folder.glob('iteration_1_state_*.npz'),key=lambda p:int(p.stem.rsplit('_',1)[1])):
        z=read(p)
        if refs[p.relative_to(ROOT).as_posix()]!=md['archives'][p.name]['sha256']:raise ValueError('same literal nonlinear base changed')
        shards.append(z['field_coefficients'])
    x=np.r_[np.zeros((1,84),complex),np.concatenate(shards)]
    if x.shape!=(1151,84):raise ValueError('every original n0 field trace must bind the n1 germ')
    reduction=homogeneous_scalar_degree_reduction(1);E=reduction['angular_derivatives'];U=reduction['real_to_complex_coefficient_map']
    lifts=chronological_n0_field_lifts(a['representation'],a['value_permutation']);C=np.kron(lifts['frame_rows'],np.eye(2))
    wall=np.kron(np.r_[lifts['W'],lifts['hv']],np.eye(4));change=np.kron(np.eye(84),U)
    field_indices=np.array([(np.arange(84)[:,None]*4+np.arange(2)[None]*2+k).ravel()for k in range(2)])
    source_lifts=np.array([(change@wall.T)[ids]for ids in field_indices])
    source_duals=np.array([(change.conj()@wall.T)[ids]for ids in field_indices])
    phases={};charts={};nodes={};source_base=ROOT/'artifacts/muon_piecewise_euclidean_action_20261011/run_2';sm=read(source_base/'result.json')
    for side in('incoming','outgoing'):
        phases[side],_=retained_input(side,refs);nodes[side]=read(source_base/f'{side}_nodes.npz')
        nodes[side]['total_proper_clock']=next(r['total_proper_clock']for r in sm['records']if r['side']==side)
        charts[side]={j:source_cell_field_chart(nodes[side],j)for j in range(192)}
    grouped=[[]for _ in range(1150)]
    for iq,row in enumerate(a['quadrature']):
        edge=row['rows'][0][0]
        if row['rows'][1][0]!=edge+1:raise ValueError('same chronological directed neighbors required')
        grouped[edge].append(iq)
    if any(not g for g in grouped):raise ValueError('no original source or corner edge may be omitted')
    # Pin executable dependencies before any long point application.
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256(Path(path).read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),'scripts/evaluate_muon_nonlinear_chronological_n0_action.py',
        'scripts/evaluate_muon_continued_current_factor.py','tests/test_muon_chronological_harmonic_field_action.py'):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    out.mkdir(parents=True);archives={}
    def save(name,data):
        p=out/name;deterministic_archive(p,data)
        if p.stat().st_size>=10*1024**2:raise ArithmeticError('split every original complete n1 array')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    save('original_n1_angular_and_source_incidence.npz',dict(**a['graph'],real_to_complex=U,angular_derivatives=E,
        full_real_angular_derivatives=reduction['full_real_angular_derivatives'],spectator_field_indices=field_indices,
        original_wall_map_real=wall,right_current_field_source_lifts=source_lifts,
        literal_left_current_field_source_lifts=source_duals,frame_rows_per_reduced_node=C,
        same_n0_field_values=x,original_value_permutation=a['value_permutation']))
    D=[];upper=[];lower=[];pending=np.zeros((168,168),complex);start=1;point_sources=[];point_start=0
    initial=np.zeros_like(pending);initial_up=initial.copy();initial_low=initial.copy();processed=0
    def border(K):
        q=np.zeros((176,176),complex);q[:168,:168]=K;q[:168,168:]=C.T;q[168:,:168]=C;return q
    def edge_border(K):
        q=np.zeros((176,176),complex);q[:168,:168]=K;return q
    def flush_blocks():
        nonlocal start,D,upper,lower
        if not D:return
        save(f'original_reduced_n1_KKT_blocks_{start}.npz',dict(node_start=np.array(start),node_stop_exclusive=np.array(start+len(D)),
            KKT_diagonal=np.array(D),KKT_upper=np.array(upper),KKT_lower=np.array(lower)))
        start+=len(D);D=[];upper=[];lower=[]
    def flush_points():
        nonlocal point_start,point_sources
        if not point_sources:return
        save(f'owned_current_point_sources_{point_start}.npz',{k:np.array([r[k]for r in point_sources])for k in point_sources[0]})
        point_start+=len(point_sources);point_sources=[]
    for edge,indices in enumerate(grouped):
        dl=pending.copy();dr=np.zeros_like(dl);up=np.zeros_like(dl);low=np.zeros_like(dl)
        for iq in indices:
            row=a['quadrature'][iq];N=complex(row['N']);clock=complex(row['right_clock']);scale=-complex(row['measure'])/N
            (j,pj,dj),(k,pk,dk)=row['rows'];v=pj*x[j]+pk*x[k];t=1j*N/clock*(dj*x[j]+dk*x[k])
            f=analytic_homogeneous_original_field_forms(row,v,t,lifts,E);tj=1j*N*dj/clock;tk=1j*N*dk/clock
            def weak(p,d,q,e):return scale*(p*q*f['K']+p*e*f['B_forward']+d*q*f['B_reverse']+d*e*f['M'])
            dl+=weak(pj,tj,pj,tj);dr+=weak(pk,tk,pk,tk);up+=weak(pj,tj,pk,tk);low+=weak(pk,tk,pj,tj)
            provenance=a['graph']['quadrature_provenance'][iq];side='incoming'if provenance[5].real==0 else'outgoing'
            cell=int(provenance[7].real);chart=charts[side][cell];anchor=float(provenance[0].real);z=complex(provenance[1])
            if chart['coordinate_anchor']!=anchor:raise ValueError('owned FE2 test function anchor changed')
            tau=analytic_proper_clock(phases[side],anchor,z,chart['proper_center'])
            values=analytic_FE2_values(tau,chart['total_proper_clock'],chart['source_element'])
            H=row['H']+lifts['hv']@v;projection=holomorphic_charge_projection(H)['projection']
            vertices=[];selected=[]
            # Radius is reconstructed from the exact intrinsic action
            # density wS=N*R; no new metric or matching input is inserted.
            Rradius=row['weights'][1]/N
            for family in(1,2):
                V=euclidean_open_action_vertices(Rradius,N,family=family)['vertices'];Vs=np.zeros_like(V)
                Vs[:20]=np.einsum('cd,fcij->fdij',projection,V[:20].reshape(5,4,6,6)).reshape(20,6,6)
                vertices.append(V);selected.append(Vs)
            point_sources.append(dict(original_quadrature_index=iq,rows=np.array(row['rows'],complex),measure=row['measure'],
                N=N,R=Rradius,current_FE2_values=values,current_proper_clock=tau,
                original_FE2_element=chart['source_element'],current_vertices=np.array(vertices),selected_EM_current_vertices=np.array(selected),
                updated_H_realified=H,current_EM_projection=projection))
            processed+=1
            if len(point_sources)==128:flush_points()
        if edge==0:initial=dl;initial_up=up;initial_low=low
        else:
            D.append(border(dl));upper.append(edge_border(up));lower.append(edge_border(low))
            if len(D)==4:flush_blocks()
        pending=dr
        if edge%32==31 or edge==1149:print(json.dumps(dict(stage='original_n1_action_and_owned_current_points',edges=edge+1,total_edges=1150,quadrature_nodes=processed,total_quadrature=3832)),flush=True)
    D.append(border(pending));flush_blocks();flush_points()
    save('original_n1_initial_face_reactions.npz',dict(initial_face_Hessian=initial,initial_to_first_Hessian=initial_up,first_to_initial_Hessian=initial_low))
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same global n1 source changed')
    result=dict(classification='EVALUATED_GLOBAL_ORIGINAL_N1_FIELD_ACTION_AND_EXACT_OWNED_CURRENT_TEST_LIFT',input_hashes=refs,archives=archives,
        original_temporal_nodes=1151,reduced_field_rows_per_node=168,reduced_Gauss_rows_per_node=32,reduced_frame_rows_per_node=8,
        exact_spectator_multiplicity=2,all_original_full_field_rows=386400,all_original_Gauss_rows=73600,named_frame_rows=18400,
        initial_only_trace_removed=0,final_natural_trace_retained=1150,birth_real_trace_node=575,
        classical_base=folder.relative_to(ROOT).as_posix(),classical_base_actual_max_residual=md['actual_classical_residual_max'],
        original_scalar_gauge_cross_and_curvature_contacts_retained=True,independent_complex_B_reverse_retained=True,
        current_test_equation='owned2 FE2 functions analytically continued using the original proper-clock germ; full C6 x realn1 gives48 internal tests, not82800 new unknown tests',
        actual_current_source_full_right_columns=288,complete_C_left_columns_per_axis=2520,
        current_sources_have_full_induced_H_inverse_image=True,current_scalar_driving_rows_zero_by_declared_EM_current_selection=True,
        current_source_functions_recentered_or_clipped=False,source_coefficients_conjugated=False,
        existing_FE2_current_kernel_or_native_heat_mean_grafted=False,
        source_adjoint_solver_application_in_this_stage=False,physical_exterior_pole_or_native_relative_domain_identified=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 complete original field action and owned source point germs on converged fixed-geometry1151-node classical graph; physical domain/native loop, source frequency and pole/LSZ matching outside this action stage')
    rp=out/'result.json';rp.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(rp.read_bytes()).hexdigest(),archive_count=len(archives),max_archive_bytes=max(r['bytes']for r in archives.values())),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    materialize(p.parse_args().output)
