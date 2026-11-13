"""Bounded nonlinear all67 child finite-action shooting at fixed parent data."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_fixed_parent_finite_shooting import FixedParentFiniteShooter
from bhsm.interface.muon_coupled_phase_trace_projection import _solve
from bhsm.interface.muon_complex_coupled_reset_continuation import complex_reset_chart
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def clean(x):
    if isinstance(x,dict):return{k:clean(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return[clean(v)for v in x]
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,(complex,np.complexfloating)):return[float(x.real),float(x.imag)]
    if isinstance(x,np.generic):return x.item()
    return x


def materialize(output,max_iterations,inner_iterations,max_backtracks,gamma):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve all nonlinear finite shooting attempts')
    pins={};archives={}
    def read(folder,name,md=None):
        p=ROOT/folder/name;b=p.read_bytes();h=sha256(b).hexdigest()
        if md is not None and h!=md['archives'][name]['sha256']:raise ValueError('same retained candidate required')
        pins[p.relative_to(ROOT).as_posix()]=h
        if p.suffix=='.json':return json.loads(b)
        with np.load(p)as z:return{k:z[k].copy()for k in z.files}
    source=Path('artifacts/muon_coupled_reset_canonical_trace_20261012/run_1')
    md=read(source,'result.json');state=read(source,'application.npz',md)
    wp=next(Path(p)for p in md['input_hashes']if p.endswith('true_phase_projection_inputs.npz'))
    wb=(ROOT/wp).read_bytes()
    if sha256(wb).hexdigest()!=md['input_hashes'][wp.as_posix()]:raise ValueError('same owned state weights required')
    pins[wp.as_posix()]=sha256(wb).hexdigest()
    with np.load(ROOT/wp)as z:weights=z['state_weights'].copy();norm=z['normalization_coordinates'].copy()
    phase,_=retained_input('outgoing',pins);rep=phase['representation'];guard=2e-10
    out.mkdir(parents=True);trial_counter=0
    # Explicit finite-natural control. This is not a retarded terminal map.
    shooter=FixedParentFiniteShooter(state['raw_pair'],state['reference_pair'],rep,weights,norm,md['action_parameters'],
        terminal_matrix=np.zeros((106,106),complex),terminal_source=np.zeros(106,complex),
        step=1e-8,cells=2,guard=guard,inner_iterations=inner_iterations)
    def save(path,data):
        _compressed_npz(path,{k:v for k,v in data.items()if isinstance(v,np.ndarray)})
        if path.stat().st_size>=10*1024**2:raise ValueError('split actual shooting arrays')
        archives[path.relative_to(out).as_posix()]=dict(bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest())
    def evaluate(u,guess=None):
        nonlocal trial_counter
        number=trial_counter;trial_counter+=1;folder=out/f'trial_{number:04d}';folder.mkdir()
        def progress(stage,data=None):
            print(json.dumps(clean(dict(stage='nonlinear_fixed_parent_finite_shooting',trial=number,
                application=stage,detail=data)),sort_keys=True),flush=True)
        a=shooter.evaluate(u,surface_gamma=gamma,guess=guess,
            save=lambda name,data:save(folder/name,data),progress=progress)
        record=dict(valid=a['valid'],status=a['status'],surface_gamma=gamma,
            finite_natural_control=True,parent_reference_and_coordinate_endpoints_fixed=True)
        if a['valid']:
            save(folder/'action_and_shooting_rows.npz',dict(canonical_input210=u,residual210=a['residual'],
                inexact_Jacobian210=a['jacobian'],raw_pair=a['raw_pair'],reference_pair=a['reference_pair'],
                all_original226_birth_rows=a['birth']['residual'],named_Ward_rows=a['ward']['rows'],
                named_Ward_identity=a['ward']['original_nonlinear_identity'],independent_birth_rows=a['independent_birth_rows'],
                actual_fiber67=a['fiber'],fiber_coordinate_map=a['fiber_coordinate_map'],fiber_birth_rows=a['fiber_birth_rows'],
                canonical_embedding=a['canonical_embedding'],canonical_transfer=a['canonical_transfer'],
                terminal_master=a['terminal_master'],terminal_Pi=a['terminal_Pi'],
                **{k:v for k,v in a['work'].items()if isinstance(v,np.ndarray)}))
            w=a['work'];record.update(residual210_max=float(np.max(abs(a['residual']))),
                all_original226_max=float(np.max(abs(a['birth']['residual']))),
                child_initial_original146_max=float(np.max(abs(a['initial']['original_constitutive_rows']))),
                parent_original146_max=float(np.max(abs(a['parent']['original_constitutive_rows']))),
                complete_action67_max=float(np.max(abs(w['full_action_work']))),
                clock_scaled_complete_action67_max=float(np.max(abs(w['clock_scaled_full_action_work']))),
                clock_scaled_complete_action67_norm=float(np.linalg.norm(w['clock_scaled_full_action_work'])),
                recorded_coordinate_interval=w['recorded_coordinate_interval'].item(),
                terminal_only67_norm=float(np.linalg.norm(w['terminal_only_work'])),
                initial_cotangent67_norm=float(np.linalg.norm(w['initial_cotangent_work'])),
                complete_action67_norm=float(np.linalg.norm(w['full_action_work'])),
                full_terminal106_norm=float(np.linalg.norm(w['full_terminal_graph_residual'])),
                full_terminal106_max=float(np.max(abs(w['full_terminal_graph_residual']))),
                terminal_fiber_rank=w['terminal_fiber_rank'],terminal_fiber_condition=w['terminal_fiber_condition'],
                original_stage358_max=max(float(np.max(abs(h['stage']['application']['residual'])))for h in a['history']),
                original_endpoint146_max=max(float(np.max(abs(h['endpoint']['original_constitutive_rows'])))for h in a['history']),
                chart=complex_reset_chart(a['raw_pair']))
        else:
            for name in('parent','initial','endpoint'):
                if name in a:
                    b=a[name];record[name+'_original_rows_max']=float(np.max(abs(b['original_constitutive_rows'])))
                    save(folder/(name+'_failed_reconstitution.npz'),dict(coefficients=b['coefficients'],
                        original_constitutive_rows=b['original_constitutive_rows'],framed_rows=b['framed_rows'],
                        framed_Jacobian=b['framed_Jacobian'],canonical_momentum_target=b['canonical_momentum_target']))
            if 'stage'in a:
                b=a['stage'];record['stage_original_rows_max']=float(np.max(abs(b['application']['residual'])))
        p=folder/'result.json';p.write_text(json.dumps(clean(record),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
        archives[p.relative_to(out).as_posix()]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
        print(json.dumps(clean(dict(stage='finite_shooting_trial_complete',trial=number,**record)),sort_keys=True),flush=True)
        a['trial']=number;a['report']=record
        return a
    u=shooter.start.copy();a=evaluate(u);history=[];status='INITIAL_ACTION_OR_CONSTITUTIVE_APPLICATION_FAILED';scale=None
    if a['valid']:
        scale=1/np.maximum(np.max(abs(a['jacobian']),axis=1),1.)
        status='BOUNDED_ITERATION_LIMIT'
        for iteration in range(max_iterations+1):
            r=a['residual'];J=a['jacobian'];merit=float(np.linalg.norm(scale*r));rec=dict(iteration=iteration,
                accepted_trial=a['trial'],fixed_scaled_merit=merit,**a['report']);history.append(rec)
            print(json.dumps(clean(dict(stage='finite_shooting_iteration',**rec)),sort_keys=True),flush=True)
            if np.max(abs(r))<=guard and np.max(abs(a['birth']['residual']))<=guard:
                status='ALL_RETAINED_BIRTH_AND_FINITE_ACTION_FIBER_ROWS_TOLERANCE';break
            if iteration==max_iterations:break
            accepted=False;rec['strategies']=[]
            for strategy in('balanced_Newton','damped_linear_trust'):
                if strategy=='balanced_Newton':
                    try:correction=_solve(J,-r)[0]
                    except np.linalg.LinAlgError:continue
                else:
                    B=scale[:,None]*J;rhs=scale*r
                    correction=np.linalg.solve(B.conj().T@B+1e-4*np.eye(210),-B.conj().T@rhs)
                # A fixed computational step bound changes no equation or
                # physical normalization and guards the anchored chart.
                magnitude=float(np.max(abs(correction)))
                if magnitude>.01:correction*=.01/magnitude
                st=dict(name=strategy,correction_norm=float(np.linalg.norm(correction)),trials=[]);rec['strategies'].append(st)
                for k in range(max_backtracks):
                    damping=2.**(-k);ut=u+damping*correction
                    try:b=evaluate(ut,a['initial']['coefficients'])
                    except (ValueError,np.linalg.LinAlgError,OverflowError,FloatingPointError)as error:
                        st['trials'].append(dict(damping=damping,accepted=False,error=str(error)));continue
                    new=float(np.linalg.norm(scale*b['residual']))if b['valid']else None
                    good=b['valid']and new<merit
                    if good:
                        good=all(c['monotonicity_margin']>0 for c in b['report']['chart'])
                    st['trials'].append(dict(damping=damping,trial=b['trial'],valid=b['valid'],merit=new,accepted=bool(good)))
                    if good:u,a=ut,b;accepted=True;break
                if accepted:break
            if not accepted:status='INEXACT_NEWTON_AND_DAMPED_LINEAR_TRUST_STALL';break
    if a['valid']:
        save(out/'application.npz',dict(canonical_input210=u,raw_pair=a['raw_pair'],reference_pair=a['reference_pair'],
            all_original226_birth_rows=a['birth']['residual'],residual210=a['residual'],inexact_Jacobian210=a['jacobian'],
            terminal_master=a['terminal_master'],terminal_Pi=a['terminal_Pi'],canonical_transfer=a['canonical_transfer'],
            actual_fiber67=a['fiber'],**{k:v for k,v in a['work'].items()if isinstance(v,np.ndarray)}))
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p and Path(p).is_relative_to(ROOT):
            p=Path(p);pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for p in(Path(__file__),ROOT/'tests/test_muon_fixed_parent_finite_shooting.py'):
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('actual action/source input changed')
    record=dict(classification='EVALUATED_NONLINEAR_FIXED_PARENT_FINITE_ACTION_CHILD_SHOOTING',
        status=status,input_hashes=pins,archives=archives,history=history,last_valid_trial=a.get('trial'),
        action_parameters=dict(md['action_parameters'],surface_gamma=gamma),tolerance=guard,
        parent_own_momentum_target_unchanged=True,child_canonical_unknowns=210,independent_birth_rows=143,
        complete_action_fiber_rows=67,all_original226_and_terminal106_audited=True,
        terminal_graph='EXPLICIT Y_T=0,s_T=0 finite-natural control; not outgoing/retarded exterior',
        no_terminal_only_work_as_full_action=True,no_source252_free_stationarity=True,
        action_fiber_equations='Complete first variation divided by the fixed nonzero recorded coordinate interval; literal work and both endpoint terms retained separately. No small-interval physical force certificate.',
        parent_positive_gamma_birth_reconstitution_is_fixed_point_trial_not_common_incoming_IVP=True,
        incoming_event_time_and_physical_first_hit_not_selected=True,
        formation_energy_gamma_c_pole_and_physical_admission_completed=False,
        Newton_scope='Inexact full canonical tail sensitivity; derivative of fiber/flow-position sensitivity contracted with endpoint covectors omitted and retained as required next Newton contact. All true nonlinear residuals/gates checked on trials.',
        error_scope='Actual finite nonlinear child action/constitutive/canonical applications at fixed parent/ref/time and explicit finite-natural tail; no action coefficient, temporal truncation, retarded-domain or physical normalization enclosure.')
    p=out/'result.json';p.write_text(json.dumps(clean(record),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='finite_shooting_complete',status=status,result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--max-iterations',type=int,default=3);p.add_argument('--inner-iterations',type=int,default=6)
    p.add_argument('--max-backtracks',type=int,default=4);p.add_argument('--gamma',type=complex,default=None)
    a=p.parse_args();materialize(a.output,a.max_iterations,a.inner_iterations,a.max_backtracks,a.gamma)
