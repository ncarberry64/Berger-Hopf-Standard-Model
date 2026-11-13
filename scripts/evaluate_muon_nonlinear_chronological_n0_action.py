"""Apply the original nonlinear field action on the complete chronological graph.

The heat source ledger is explicit. No resolvent point, birth-window heat
underflow, or unavailable graded-sector cotangent is assigned to g_total.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
from scipy.interpolate import CubicSpline
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from evaluate_muon_reached_trace_action import deterministic_archive
from evaluate_muon_coupled_lorentz_radial_green import encode
from bhsm.interface.muon_parent_positive_coupled_field import corrected_positive_parent_reference
from bhsm.interface.muon_continued_action_reality import action_reality_coefficient,_analytic_polynomial
from bhsm.interface.muon_parent_maxwell_full_weak import M
from bhsm.interface.muon_nonlinear_chronological_n0_action import (
    nonlinear_chronological_n0_action,chronological_field_KKT_blocks)


def chronological_n0_classical_binding(*,repository=ROOT,graph_folder=
        'artifacts/muon_chronological_clifford_graph_20261011/run_1'):
    """Bind written-once whole-graph files, preserving their exact incidence.

    Bulk connection values/rates/radial derivatives and density are the
    SAME five-real-node cubic extension as the frozen birth-window literal
    action. Wall/coframe/H use the exact affine coefficient germ. This is
    an explicit numerical coefficient extension at fixed geometry.
    """
    root=Path(repository);refs={}
    def read(p):
        p=Path(p);p=p if p.is_absolute()else root/p
        refs[p.relative_to(root).as_posix()]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    folder=root/graph_folder;graph=read(folder/'chronological_graph_incidence.npz')
    edge=graph['edge_incidence'];pr=graph['quadrature_provenance'];corners=graph['corner_incidence']
    if edge.shape!=(1150,5)or pr.shape!=(3832,9)or corners.shape!=(383,5):
        raise ValueError('the exact complete 384-cell, 383-corner chronological graph is required')
    if not np.array_equal(edge[:,:2],np.c_[np.arange(1150),np.arange(1,1151)]):
        raise ValueError('every original temporal trace and directed neighbor must be retained')
    birth=corners[np.flatnonzero(corners[:,3]==0),1]
    if len(birth)!=1 or int(birth[0].real)!=575:raise ValueError('same owned real common birth trace required')
    old=read(root/'artifacts/muon_restored_clifford_heat_cotangent_20261011/birth_refinement_2_run_1/graph_and_angular_incidence.npz')
    ids=old['original_n0_coordinate_permutation'];wall_map=old['original_n0_wall_coordinate_map']
    files=sorted(folder.glob('coefficient_nodes_*.npz'),key=lambda p:int(p.stem.rsplit('_',1)[1]))
    if [int(p.stem.rsplit('_',1)[1])for p in files]!=list(range(0,len(pr),192)):
        raise ValueError('all complete chronological coefficient shards are required')
    shards=[read(p)for p in files];keys=shards[0].keys()
    coefficients={k:np.concatenate([a[k]for a in shards])for k in keys}
    if any(len(v)!=len(pr)for v in coefficients.values()):raise ValueError('complete coefficient/node alignment required')
    for j,key in ((2,'measure'),(3,'right_clock'),(4,'reflected_clock')):
        if not np.array_equal(coefficients[key],pr[:,j]):raise ValueError('original coframe provenance changed: '+key)
    phases={};data={};real_checks=[];rep=None
    source=root/'artifacts/muon_corrected_profile_magnetic_response_20261011/run_1';sm=read(source/'result.json')
    for side in('incoming','outgoing'):
        phase,_=retained_input(side,refs);phases[side]=phase;r=phase['representation']
        if rep is None:rep=r
        elif any(not np.array_equal(rep[k],r[k])for k in('gauge_basis','gauge_radial_basis','wall_trace_map','radial_quadrature')):
            raise ValueError('one original radial representation required')
        primal=read(source/f'{side}_primal_and_source.npz');background=read(source/f'{side}_background.npz')
        for name in(f'{side}_primal_and_source.npz',f'{side}_background.npz'):
            if refs[(source/name).relative_to(root).as_posix()]!=sm['array_archives'][name]['sha256']:
                raise ValueError('the actual corrected coefficient source changed')
        dens=[]
        for t,raw,bg in zip(primal['coordinate_times'],primal['raw_fields'],background['full_background_values']):
            kw={}if side=='incoming'else dict(initial_pair=phase['arrays']['initial_pair'],reference_pair=phase['arrays']['reference_pair'])
            reference=corrected_positive_parent_reference(raw,r,coordinate_time=float(t),**kw)
            dens.append(reference['positive_two_form_densities'])
            real_checks.append(dict(side=side,time=float(t),bulk_value_rate_radial_max_difference=float(np.max(abs(
                bg-np.array([reference[k]for k in('background_values','background_time_derivatives','background_radial_derivatives')]))))))
        data[side]=dict(background=CubicSpline(primal['times'],background['full_background_values']),
            density=CubicSpline(primal['times'],np.asarray(dens)))
    rows=[];body_checks=dict(raw_max_difference=0.,lapse_max_difference=0.,radius_max_difference=0.)
    for iq,p in enumerate(pr):
        anchor,z,measure,w,ws,arm,part,cell,slope=p;side='incoming'if arm.real==0 else'outgoing'
        if arm.imag or arm.real not in(0,1):raise ValueError('original arm provenance required')
        anchor=float(anchor.real);phase=phases[side]
        u=anchor+(abs(phase['receipt']['span'])if side=='incoming'else 0.)
        bg=_analytic_polynomial(data[side]['background'],u,z);density=_analytic_polynomial(data[side]['density'],u,z)
        body=action_reality_coefficient(phase,anchor,z);geo=body['geometry']
        for name,got,saved in(('raw',body['raw'],coefficients['raw_fields'][iq]),
            ('lapse',geo['N'],coefficients['N'][iq]),('radius',geo['R4'],coefficients['R'][iq])):
            d=float(np.max(abs(got-saved)));body_checks[name+'_max_difference']=max(body_checks[name+'_max_difference'],d)
            if d!=0.:raise ValueError('the whole graph must use the identical action germ: '+name)
        wall=body['wall_independent_plus_inherited'].copy();wall[2:]+=M*(geo['mechanical_lambda']-1)
        incidence=coefficients['rows'][iq]
        if np.any(incidence[:,0].imag)or np.any(incidence[:,0].real!=np.round(incidence[:,0].real)):
            raise ValueError('literal integer original node labels required')
        rows.append(dict(A=bg[0],At=bg[1],Ar=bg[2],densities=density,wall_A=wall,H=body['raw'][-8:-4],
            Hdot=body['raw'][-4:],weights=np.array([geo['R4']**3/geo['N'],geo['N']*geo['R4'],geo['N']*geo['R4']**3]),
            N=geo['N'],measure=measure,right_clock=w,reflected_clock=ws,
            lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=4.,
            rows=tuple((int(j.real),complex(a),complex(d))for j,a,d in incidence)))
    return dict(quadrature=rows,representation=rep,temporal_nodes=1151,value_permutation=ids,
        original_n0_wall_coordinate_map=wall_map,input_hashes=refs,graph=graph,
        row_incidence=coefficients['rows'],real_node_checks=real_checks,identical_body_checks=body_checks,
        source_domain='all 384 source cells and 383 restored two-leg corners; original initial trace held; final natural trace free',
        coefficient_extension='five-real-node cubic bulk A/At/Ar/density extension; identical affine wall/coframe/H coefficient germ')


def native_source_ledger():
    """Unavailable sector cotangents cannot be represented by numeric zeros."""
    return dict(g_total=None,graded_total_supplied=False,
        closed_three_lepton_Clifford=dict(status='whole chronological heat contour unresolved; executed nonaccretive branch counterexample',cotangent=None),
        Maxwell_Higgs_native=dict(status='native bosonic loop cotangent not supplied by this classical action',cotangent=None),
        ghost_BRST_native=dict(status='graded ghost/BRST cotangent not supplied',cotangent=None),
        relative_exterior_domain=dict(status='same physical heat/relative-domain cotangent not evaluated',cotangent=None),
        resolvent_points_used_as_heat_gradient=False,birth_window_underflow_used_as_zero=False,
        old_FE2_native_gradient_grafted=False)


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every chronological action application')
    a=chronological_n0_classical_binding()
    print(json.dumps(dict(stage='whole_graph_literal_n0_binding',quadrature_nodes=len(a['quadrature']),
        original_trace_nodes=a['temporal_nodes'],original_free_fields=(a['temporal_nodes']-1)*84)),flush=True)
    refs=a['input_hashes'];archives={}
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            p=Path(path)
            try:rel=p.relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256(p.read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_nonlinear_chronological_n0_action.py',
        'scripts/evaluate_muon_continued_current_factor.py','scripts/evaluate_muon_reached_trace_action.py',
        'scripts/evaluate_muon_coupled_lorentz_radial_green.py'):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    x=np.zeros((a['temporal_nodes']-1,84),complex)
    def progress(done,total):print(json.dumps(dict(stage='literal_n0_field_action',quadrature_nodes=done,total=total)),flush=True)
    action=nonlinear_chronological_n0_action(x,a['quadrature'],a['representation'],temporal_nodes=a['temporal_nodes'],
        value_permutation=a['value_permutation'],progress=progress)
    kkt=chronological_field_KKT_blocks(action)
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same chronological action source changed')
    out.mkdir(parents=True)
    def save(name,arrays):
        p=out/name;deterministic_archive(p,arrays)
        if p.stat().st_size>=10*1024**2:raise ArithmeticError('split complete chronological arrays before publication')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    for start in range(0,len(kkt['diagonal']),16):
        stop=min(start+16,len(kkt['diagonal']));ns=max(0,min(stop,len(kkt['upper']))-start)
        save(f'original_KKT_blocks_{start}.npz',dict(node_start=np.array(start+1),node_stop_exclusive=np.array(stop+1),
            KKT_diagonal=kkt['diagonal'][start:stop],KKT_upper=kkt['upper'][start:start+ns],KKT_lower=kkt['lower'][start:start+ns],
            original_action_gradient=action['gradient'][start:stop],original_frame_constraint=action['frame_constraint'][start:stop],
            classical_KKT_residual=kkt['residual'][start:stop]))
    save('chronological_field_incidence.npz',dict(**a['graph'],row_incidence=a['row_incidence'],
        field_coefficients=x,frame_rows_per_node=action['frame_rows_per_node'],frame_indices=action['frame_indices'],
        Gauss_indices_per_node=action['Gauss_indices_per_node'],value_permutation=a['value_permutation'],
        original_n0_wall_coordinate_map=a['original_n0_wall_coordinate_map'],
        initial_face_gradient=action['initial_face_gradient'],initial_face_Hessian=action['initial_face_Hessian'],
        initial_to_first_Hessian=action['initial_to_first_Hessian']))
    # Euler and row residuals are recorded in original coordinates; no
    # stationarity is inferred from small scaled ratios or an absent g.
    g=action['gradient'];row=np.max(abs(g),axis=1);gauss=g[:,:16]
    result=dict(classification='EVALUATED_COMPLETE_CHRONOLOGICAL_LITERAL_N0_CLASSICAL_RESIDUAL_AND_DIRECTED_KKT_BLOCKS',
        input_hashes=refs,archives=archives,source_domain=a['source_domain'],coefficient_extension=a['coefficient_extension'],
        real_node_checks=a['real_node_checks'],identical_whole_graph_body_checks=a['identical_body_checks'],
        source_cells=384,restored_corners=383,temporal_trace_nodes=1151,free_original_field_rows=1150*84,
        original_At_Gauss_rows=1150*16,named_frame_rows=1150*4,directed_KKT_block_width=88,
        initial_only_trace_removed=0,final_natural_trace_retained=1150,birth_real_trace_node=575,
        classical_action_value=encode(action['value']),classical_gradient_norm=float(np.linalg.norm(g)),
        classical_gradient_max_entry=float(np.max(abs(g))),classical_Gauss_gradient_norm=float(np.linalg.norm(gauss)),
        initial_reaction_norm=float(np.linalg.norm(action['initial_face_gradient'])),
        final_natural_gradient_norm=float(np.linalg.norm(g[-1])),
        named_frame_residual_norm=float(np.linalg.norm(action['frame_constraint'])),
        nonzero_original_gradient_nodes=int(np.count_nonzero(row)),
        directed_upper_lower_transpose_max=float(np.max(abs(action['Hessian_upper']-action['Hessian_lower'].transpose(0,2,1)))),
        original_Hessian_diagonal_norm=float(np.linalg.norm(action['Hessian_diagonal'])),
        original_Hessian_upper_norm=float(np.linalg.norm(action['Hessian_upper'])),
        source_ledger=native_source_ledger(),native_gradient_supplied=False,quantum_stationary_Newton_solve_completed=False,
        classical_background_source_subtracted=False,geometric_or_physical_domain_stationarity_claimed=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='exact analytic field polynomials assembled in binary64 on declared bulk coefficient extension; native graded heat source, physical relative/domain, geometry and matching remain unresolved')
    rp=out/'result.json';rp.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(rp.read_bytes()).hexdigest(),**{k:v for k,v in result.items()if k not in('input_hashes','archives','real_node_checks')}),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    materialize(p.parse_args().output)
