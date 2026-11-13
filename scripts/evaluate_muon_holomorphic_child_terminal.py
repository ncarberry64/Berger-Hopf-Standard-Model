"""Apply full original child252 action at the actual complex global terminal."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
from scipy.integrate import solve_ivp
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action
from bhsm.interface.muon_birth_inherited_finite_normal_phase import inherited_child_finite_normal_action
from bhsm.interface.muon_profile_preserving_phase_sample import profile_preserving_raw_sample
from bhsm.interface.muon_continued_action_reality import action_reality_coefficient,_geometry
from bhsm.interface.muon_nonlinear_chronological_n0_action import chronological_n0_field_lifts
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve each actual complex action application')
    refs={};phase,_=retained_input('outgoing',refs);rep=phase['representation'];params=phase['receipt']['action_parameters']
    pair,reference=phase['arrays']['initial_pair'],phase['arrays']['reference_pair']
    out.mkdir(parents=True);archives={}
    def read(path,expected=None):
        p=ROOT/path;raw=p.read_bytes();h=sha256(raw).hexdigest()
        if expected is not None and h!=expected:raise ValueError('same terminal source changed: '+str(path))
        refs[p.relative_to(ROOT).as_posix()]=h
        if p.suffix=='.json':return json.loads(raw)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def save(name,data):
        p=out/name;_compressed_npz(p,data)
        if p.stat().st_size>10*1024**2:raise RuntimeError('split full original action rows')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    # Independent equality to the frozen real full graph, including every
    # mixed child derivative, before applying any complex terminal data.
    tm=float(phase['arrays']['stage_coordinate_time'][-1]);real=phase['arrays'][phase['stage_key']][-1]
    print(json.dumps(dict(stage='same_real_original_child_action_control',coordinate_time=tm)),flush=True)
    old=inherited_child_finite_normal_action(real,tm,pair,reference,rep,**params)
    new=holomorphic_inherited_child_action(real,tm,pair,reference,rep,**params)
    control={k:float(np.max(abs(np.asarray(new[k])-np.asarray(old[k])))/max(1.,np.max(abs(np.asarray(old[k])))))
        for k in('value','raw_gradient','raw_hessian','gradient','hessian')}
    save('same_real_original_action_control.npz',dict(old_raw_gradient=old['raw_gradient'],new_raw_gradient=new['raw_gradient'],
        old_raw_hessian=old['raw_hessian'],new_raw_hessian=new['raw_hessian'],raw_fields=real,
        old_value=np.array(old['value']),new_value=np.array(new['value'])))
    print(json.dumps(dict(stage='same_real_original_child_action_control_complete',relative_max=control)),flush=True)
    if max(control.values())>2e-9:raise ArithmeticError('literal real-owner action equality failed; no complex continuation promoted')
    base=Path('artifacts/muon_chronological_n1_field_action_20261011/run_1');md=read(base/'result.json')
    inc=read(base/'original_n1_angular_and_source_incidence.npz',md['archives']['original_n1_angular_and_source_incidence.npz']['sha256'])
    values=inc['same_n0_field_values'];ids=inc['original_value_permutation']
    if values.shape!=(1151,84):raise ValueError('complete converged original field trace required')
    graph=Path('artifacts/muon_chronological_clifford_graph_20261011/run_1');gm=read(graph/'result.json')
    last=next(k for k in gm['archives']if k.startswith('coefficient_nodes_3648'))
    coeff=read(graph/last,gm['archives'][last]['sha256']);rows=coeff['rows'][-2:]
    provenance=inc['quadrature_provenance'][-2:]
    if not np.array_equal(rows[:,0,0],np.full(2,1149))or not np.array_equal(rows[:,1,0],np.full(2,1150)):
        raise ValueError('same actual final source edge required')
    if np.any(provenance[:,6])or not np.array_equal(provenance[:,3],np.ones(2)):
        raise ValueError('this application binds the actual proper-clock source cell, not a connector clock')
    anchor=float(provenance[-1,0].real);length=complex(sum(provenance[:,2]));half=length.real/2
    if length.imag or half<=0:raise ValueError('same positive original terminal proper cell required')
    sample=profile_preserving_raw_sample(phase,anchor);rate=sample['raw_coordinate_time_derivative'].astype(complex)
    raw_center=sample['raw_fields'].astype(complex)
    def rhs(t,z):return np.array([-1j/_geometry(raw_center+z[0]*rate)['N']])
    sol=solve_ivp(rhs,(0,half),[0j],rtol=1e-11,atol=1e-17,dense_output=True,max_step=half/2)
    if not sol.success:raise ArithmeticError(sol.message)
    z=complex(sol.y[0,-1]);time=anchor+z
    qdef=[]
    for p,r in zip(provenance,rows):
        offset=(complex(r[1,1])-.5)*length
        direct=solve_ivp(rhs,(0,float(offset.real)),[0j],rtol=1e-11,atol=1e-17,max_step=abs(offset.real)/2)
        qdef.append(abs(direct.y[0,-1]-p[1]))
    raw=action_reality_coefficient(phase,anchor,z)['raw'];N=_geometry(raw)['N']
    lifts=chronological_n0_field_lifts(rep,ids);delta=values[-1]
    derivative=(values[-1]-values[-2])/length;coordinate_rate=1j*N*derivative
    gv=np.eye(84)[:80,ids];tg=gv.copy()
    for j,label in enumerate(rep['gauge_labels']):
        if label['field']=='A_tau':tg[j]=0
    raw[100:180]+=gv@delta;raw[180:260]+=tg@coordinate_rate
    raw[260:264]+=lifts['hv']@delta;raw[264:]+=lifts['hv']@coordinate_rate
    print(json.dumps(dict(stage='actual_complex_global_terminal_full_action',terminal=1150,
        coordinate_time=[time.real,time.imag],field_imaginary_max=float(np.max(abs(delta.imag))),
        original_proper_clock_ODE_point_difference_max=max(qdef))),flush=True)
    action=holomorphic_inherited_child_action(raw,time,pair,reference,rep,**params)
    P=action['coordinates']['lift'];n=action['coordinates']['x_count'];eta=P.T@raw
    if np.max(abs(P@eta-raw))>1e-12:raise ValueError('actual raw terminal must retain every original phase coordinate')
    oldp=phase['arrays']['p_final'];momentum=action['canonical_momentum'];constraint=action['algebraic_Gauss_multiplier_rows']
    save('actual_complex_terminal_full_action.npz',dict(raw_fields=raw,master_coefficients=eta,coordinate_lift=P,
        coordinate_time=np.array(time),coordinate_anchor=np.array(anchor),physical_offset=np.array(z),
        original_terminal_field_value=delta,original_terminal_field_source_derivative=derivative,
        original_terminal_field_coordinate_rate=coordinate_rate,original_value_permutation=ids,
        raw_gradient=action['raw_gradient'],raw_hessian=action['raw_hessian'],
        action_gradient=action['gradient'],action_hessian=action['hessian'],
        canonical_momentum=momentum,canonical_force=action['gradient'][:n],
        all_Gauss_multiplier_rows=constraint,retained_real_phase_p=oldp,
        full_complex_action_momentum_minus_real_phase_p=momentum-oldp,
        effective_connection_parameters=action['effective_connection_parameters'],
        child_metric_connection_baseline=action['child_metric_connection_baseline'],
        full_wall_connection=action['total_wall_connection'],R4=np.array(action['R4']),N=np.array(action['induced_lapse']),
        response_anchor_residual=action['response_chart']['implicit_residual'],
        response_anchor_third_Taylor_residual=action['response_chart']['implicit_Taylor_residual']))
    # The actual endpoint action exists before claiming that these algebraic
    # data lie on a canonical exterior constraint manifold.
    records=dict(multiplier_rows_max=float(np.max(abs(constraint[:24]))),
        A_tau_rows_max=float(np.max(abs(constraint[24:]))))
    rng=np.random.default_rng(512106);direction=P@(rng.normal(size=len(eta))+1j*rng.normal(size=len(eta)))
    direction/=np.linalg.norm(direction);epsilon=2e-6
    plus=holomorphic_inherited_child_action(raw+epsilon*direction,time,pair,reference,rep,**params)
    minus=holomorphic_inherited_child_action(raw-epsilon*direction,time,pair,reference,rep,**params)
    value_first=(plus['value']-minus['value'])/(2*epsilon)
    gradient_first=(plus['raw_gradient']-minus['raw_gradient'])/(2*epsilon)
    exact_value=action['raw_gradient']@direction;exact_gradient=action['raw_hessian']@direction
    nonreal=dict(value_direction_relative_error=float(abs(value_first-exact_value)/max(1.,abs(exact_value))),
        gradient_direction_relative_error=float(np.max(abs(gradient_first-exact_gradient))/max(1.,np.max(abs(exact_gradient)))),
        raw_Hessian_transpose_relative_defect=float(np.max(abs(action['raw_hessian']-action['raw_hessian'].T))/max(1.,np.max(abs(action['raw_hessian'])))))
    save('independent_nonreal_full_action_direction_control.npz',dict(direction=direction,epsilon=np.array(epsilon),
        finite_value_first=np.array(value_first),analytic_value_first=np.array(exact_value),
        finite_gradient_first=gradient_first,analytic_gradient_first=exact_gradient))
    print(json.dumps(dict(stage='independent_nonreal_action_direction_control_complete',**nonreal)),flush=True)
    if max(nonreal.values())>3e-6:raise ArithmeticError('nonreal full action directional control failed')
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),'scripts/evaluate_muon_continued_current_factor.py',
        'tests/test_muon_holomorphic_child_action.py'):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same complex terminal/action pins changed')
    result=dict(classification='EVALUATED_ORIGINAL_HOLOMORPHIC_FULL_CHILD252_AT_CORRECTED_COMPLEX_TERMINAL',
        input_hashes=refs,archives=archives,same_real_original_action_relative_max=control,
        independent_nonreal_direction_control=nonreal,
        original_terminal_node=1150,coordinate_time_real=time.real,coordinate_time_imag=time.imag,
        terminal_field_value_imaginary_max=float(np.max(abs(delta.imag))),
        terminal_raw_imaginary_max=float(np.max(abs(raw.imag))),
        original_proper_clock_ODE_saved_point_difference_max=max(qdef),
        canonical_momentum_norm=float(np.linalg.norm(momentum)),
        canonical_momentum_change_from_retained_real_phase_norm=float(np.linalg.norm(momentum-oldp)),
        canonical_force_norm=float(np.linalg.norm(action['gradient'][:n])),
        original_Gauss_multiplier_residual_max=float(np.max(abs(constraint))),
        original_Gauss_multiplier_residual_norm=float(np.linalg.norm(constraint)),
        algebraic_row_diagnostics=records,phase_variables=dict(x=n,v=n,y=len(constraint)),action_parameters=params,
        actual_complex_node_identified_with_real_phase_endpoint=False,
        old_real_phase_momentum_grafted=False,terminal_load_selected=False,
        geometry_and_unprojected_inherited_profiles_retained=True,
        exact_implicit_response_third_derivative_retained=True,
        native_heat_or_Hilbert_dual_inserted=False,
        canonical_exterior_constraint_stationarity_or_first_hit_selected=False,
        physical_stop_coordinate='selected same-action reduced Euler-Dirac eigenvalue s=lambda_selected; raw normal amplitude98 is not s',
        next_action='solve original complex canonical Legendre/Gauss compatibility and D_t Pi=L_x with the same complex terminal fields; then evaluate the reduced-saddle descriptor and first-hit event',
        error_scope='binary64 literal analytic action and same proper-clock terminal reconstruction; ODE/field/current representation and physical exterior/stop/Pauli errors not enclosed')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='complex_full_child_terminal_complete',result_sha256=sha256(p.read_bytes()).hexdigest(),
        canonical_force_norm=result['canonical_force_norm'],canonical_momentum_change=result['canonical_momentum_change_from_retained_real_phase_norm'],
        algebraic_residual_max=result['original_Gauss_multiplier_residual_max'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.output)
