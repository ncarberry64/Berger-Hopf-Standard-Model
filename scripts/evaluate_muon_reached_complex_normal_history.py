"""Bounded original child canonical action at an actually reached complex time.

This compares the original analytic action continuation with the finite C1
interpolation at the same time. It does not identify either as a retarded
exterior or replace a failed canonical stage by interpolated coefficients.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_complex_canonical_midpoint import solve_complex_canonical_midpoint
from bhsm.interface.muon_warm_complex_canonical_compatibility import warm_complex_constitutive_compatibility
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action,_affine_geometry
from bhsm.interface.muon_holomorphic_child_clock_application import holomorphic_child_explicit_clock_application
from bhsm.interface.muon_coupled_phase_trace_projection import _solve
from bhsm.interface.muon_holomorphic_current_source import holomorphic_current_stage
from bhsm.interface.muon_sigma_normal_collar_transport import CanonicalC1History,sigma_geometry_point
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from evaluate_muon_d5_finite_trace_pole_match import clean


def materialize(trial,normal_flow,output,steps,nu_squared,surface_gamma):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every actual complex continuation')
    if steps<1 or steps>4:raise ValueError('bounded reached source region: one to four original steps')
    pins={};archives={}
    def read(path):
        path=ROOT/path if not path.is_absolute()else path
        pins[path.relative_to(ROOT).as_posix()]=sha256(path.read_bytes()).hexdigest()
        with np.load(path)as z:return{k:z[k].copy()for k in z.files}
    data=read(ROOT/trial/'candidate.npz')
    hist=read(ROOT/normal_flow/'actual_C1_history.npz')
    normal_result_path=ROOT/normal_flow/'result.json'
    pins[normal_result_path.relative_to(ROOT).as_posix()]=sha256(normal_result_path.read_bytes()).hexdigest()
    normal_result=json.loads(normal_result_path.read_bytes())
    prefix_name=next(reversed(normal_result['archives']))
    # The numerical face is read from the actual last normal prefix,
    # never chosen from a desired pole or a real projection of its time.
    prefix_name=sorted(n for n in normal_result['archives']if n.startswith('normal_prefix_'))[-1]
    flow=read(ROOT/normal_flow/prefix_name)
    target=complex(flow['coordinate_time'][-1]);rho=complex(flow['material_rho'][-1])
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=ROOT)
    pins.update(phase['input_hashes']);rep=phase['representation'];coords=phase['coordinates'];P=coords['lift']
    history=CanonicalC1History(hist['coordinate_times'],hist['raw_fields'],hist['canonical_raw_time'],coords)
    interpolated,interpolated_rate=history.value(target)
    frame=canonical_central_frame(data['raw_pair'][1],rep);frame_reference=data['master_child'][106:].copy()
    eta=data['master_child'].copy();pi=data['own_child_Pi'].copy();h=target/steps
    pars=dict(nu_squared_action=nu_squared,surface_gamma=surface_gamma)
    callback=lambda x,t:holomorphic_inherited_child_action(P@x,t,data['raw_pair'],data['reference_pair'],rep,**pars)
    out.mkdir(parents=True)
    def save(name,a):
        p=out/name;_compressed_npz(p,{k:v for k,v in a.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>=10*1024**2:raise ValueError('compact reached action result required')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    records=[];passed=True
    for j in range(steps):
        tm=(j+.5)*h;te=(j+1)*h
        def progress(i,z,reaction,a,f,K,scale,hh):
            print(json.dumps(clean(dict(step=j,stage='original_complex358',time=tm,detail=hh[-1])),sort_keys=True),flush=True)
        step=solve_complex_canonical_midpoint(eta[:106],pi,eta.copy(),h,lambda x:callback(x,tm),frame,
            frame_reference=frame_reference,tolerance=2e-10,max_iterations=6,checkpoint=progress)
        a=step['application'];r=a['residual']
        save(f'step_{j:04d}_stage.npz',dict(stage_master=a['midpoint_coefficients'],stage_raw=P@a['midpoint_coefficients'],
            stage_gradient=a['action']['gradient'],stage_Hessian=a['action']['hessian'],original358_rows=r,
            frame_rows=step['framed_rows'][-2:],frame_reactions=step['frame_reactions'],coordinate_time=np.array(tm),coordinate_step=np.array(h)))
        record=dict(stage_status=step['status'],stage_time=tm,original358_rows_max=float(np.max(abs(r))),
            largest_original358_row=int(np.argmax(abs(r))),canonical_history=step['history'])
        if step['status']!='ALL_ORIGINAL_COMPLEX_CANONICAL_ROWS_TOLERANCE':
            records.append(record);passed=False;break
        guess=np.r_[a['x_new'],a['v_mid'],a['y_mid']]
        end=warm_complex_constitutive_compatibility(guess,a['p_new'],lambda x:callback(x,te),frame,
            frame_reference=frame_reference,tolerance=2e-10,max_iterations=6)
        record.update(endpoint_status=end['status'],endpoint_time=te,
            original146_rows_max=float(np.max(abs(end['original_constitutive_rows']))),
            largest_original146_row=int(np.argmax(abs(end['original_constitutive_rows']))))
        save(f'step_{j:04d}_endpoint.npz',dict(endpoint_master=end['coefficients'],endpoint_raw=P@end['coefficients'],
            endpoint_Pi=a['p_new'],original146_rows=end['original_constitutive_rows'],frame_rows=end['framed_rows'][-2:],coordinate_time=np.array(te)))
        records.append(record)
        print(json.dumps(clean(dict(stage='original_complex_endpoint',step=j,**{k:v for k,v in record.items()if k!='canonical_history'})),sort_keys=True),flush=True)
        if end['status']!='ALL_ORIGINAL_COMPLEX_CONSTITUTIVE_ROWS_TOLERANCE':passed=False;break
        eta=end['coefficients'];pi=a['p_new']
    comparison=None
    if passed:
        raw=P@eta
        clock=holomorphic_child_explicit_clock_application(raw,target,data['raw_pair'],data['reference_pair'],rep,**pars)
        D=clock['canonical_tangent_operator'];rhs=clock['canonical_tangent_rhs'];F=canonical_central_frame(raw,rep)['named_frame_covectors']
        K=np.block([[D,F.T],[F,np.zeros((2,2),complex)]]);right=np.r_[rhs,np.zeros(2,complex)]
        tangent=_solve(K,right)[0];rawtime=P@np.r_[eta[106:212],tangent[:146]]
        parent=_affine_geometry(data['raw_pair'][0],target)
        refs=np.array([_affine_geometry(v,target)for v in data['reference_pair']])
        affine=lambda v:np.r_[v[37:74],np.zeros(61),v[99],np.zeros(169)]
        parent_time=affine(data['raw_pair'][0]);refs_time=np.array([affine(v)for v in data['reference_pair']])
        bind=lambda x,v:holomorphic_current_stage(x,v[:,None],parent,parent_time[:,None],refs,refs_time[:,:,None],rep,side='child')
        actual=bind(raw,rawtime);interpolation=bind(interpolated,interpolated_rate)
        c=sigma_geometry_point(raw,rawtime,rho);ci=sigma_geometry_point(interpolated,interpolated_rate,rho)
        names=('Hcan','Hcan_first','R4','induced_lapse','wall_U','canonical_wall_current_vertices','canonical_wall_current_vertices_first')
        differences={name:float(np.linalg.norm(actual[name]-interpolation[name]))for name in names}
        geometry_differences={name:float(np.linalg.norm(c[name]-ci[name]))for name in c}
        save('actual_complex_endpoint_comparison.npz',dict(actual_raw=raw,actual_raw_time=rawtime,interpolated_raw=interpolated,
            interpolated_raw_time=interpolated_rate,raw_difference=raw-interpolated,raw_time_difference=rawtime-interpolated_rate,
            actual_Hcan=actual['Hcan'],interpolated_Hcan=interpolation['Hcan'],actual_Hcan_time=actual['Hcan_first'],
            interpolated_Hcan_time=interpolation['Hcan_first'],actual_current_vertices=actual['canonical_wall_current_vertices'],
            interpolated_current_vertices=interpolation['canonical_wall_current_vertices'],canonical_time_original_rows=K@tangent-right,
            actual_sigma_geometry=np.array([c[k].ravel()for k in c if not k.endswith('_first')]),
            interpolated_sigma_geometry=np.array([ci[k].ravel()for k in ci if not k.endswith('_first')]),
            reached_time=np.array(target),reached_material_rho=np.array(rho)))
        comparison=dict(raw_difference_norm=float(np.linalg.norm(raw-interpolated)),raw_difference_max=float(np.max(abs(raw-interpolated))),
            raw_time_difference_norm=float(np.linalg.norm(rawtime-interpolated_rate)),body_current_differences=differences,
            sigma_geometry_differences=geometry_differences,original_tangent_rows_max=float(np.max(abs(K@tangent-right))),
            original_tangent_uncancelled_scale_max=float(np.max(abs(K)@abs(tangent)+abs(right))))
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p and Path(p).is_relative_to(ROOT):
            p=Path(p);pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=v for p,v in pins.items()):raise ValueError('same executed coefficients/source bytes required')
    result=dict(classification='EVALUATED_BOUNDED_REACHED_ORIGINAL_COMPLEX_CANONICAL_ACTION',input_hashes=pins,archives=archives,
        actual_reached_complex_time=target,actual_reached_material_rho=rho,steps=steps,action_parameters=pars,
        original_action_rows_guard=2e-10,all_steps_and_endpoints_passed=passed,records=records,actual_endpoint_comparison=comparison,
        C1_complex_interpolation_not_used_as_action_source=True,parent_reference_affine_motion_composed_once=True,
        all_original_Gauss_frames_and_momenta_retained=True,finite_step_and_binary_action_errors_not_enclosed=True,
        physical_normalization_retarded_tail_matched_pole_or_Pauli_admitted=False,physical_a_mu=None,physical_g_mu=None)
    p=out/'result.json';p.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),all_steps_and_endpoints_passed=passed)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--trial',type=Path,required=True);p.add_argument('--normal-flow',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--steps',type=int,default=2);p.add_argument('--nu-squared',type=float,required=True);p.add_argument('--surface-gamma',type=float)
    a=p.parse_args();materialize(a.trial,a.normal_flow,a.output,a.steps,a.nu_squared,a.surface_gamma)
