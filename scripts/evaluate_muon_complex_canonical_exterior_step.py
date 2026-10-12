"""Execute one original complex canonical step from compatible terminal data."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action
from bhsm.interface.muon_holomorphic_child_clock_application import holomorphic_child_explicit_clock_application
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_complex_canonical_midpoint import solve_complex_canonical_midpoint
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(initial_folder,output,step,max_iterations,tolerance):
    out=ROOT/output;source=ROOT/initial_folder
    if out.exists():raise FileExistsError('preserve every original complex canonical application')
    refs={}
    def read(name):
        p=source/name;b=p.read_bytes();h=sha256(b).hexdigest();refs[p.relative_to(ROOT).as_posix()]=h
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read('result.json');refs.update(md['input_hashes']);data=read('application.npz')
    if refs[(source/'application.npz').relative_to(ROOT).as_posix()]!=md['archives']['application.npz']['sha256']:
        raise ValueError('supplied compatible initial canonical data changed')
    phase,_=retained_input('outgoing',refs);P=phase['coordinates']['lift'];n=106;h=complex(step)
    eta=data['coefficients'];p0=data['canonical_momentum_target'];time=data['coordinate_time'].item()
    reference=data.get('original_frame_reference',data['original_terminal_master'][n:])
    params=phase['receipt']['action_parameters'];rep=phase['representation'];pair=phase['arrays']['initial_pair'];ref=phase['arrays']['reference_pair']
    initial=holomorphic_child_explicit_clock_application(P@eta,time,pair,ref,rep,**params)
    a0=initial['action'];r0=np.r_[a0['gradient'][n:2*n]-p0,a0['gradient'][2*n:]]
    # An optimizer status or a small scaled merit is insufficient.
    if np.max(abs(r0))>tolerance:raise ValueError('all original initial constitutive/Gauss/multiplier rows must pass before exterior continuation')
    frame=canonical_central_frame(P@eta,rep);C=frame['named_frame_covectors'];D=initial['canonical_tangent_operator']
    B=np.block([[D,C.T],[C,np.zeros((2,2),complex)]]);rhs=np.r_[initial['canonical_tangent_rhs'],np.zeros(2,complex)]
    s=1/np.sqrt(np.maximum(np.max(abs(B),axis=1),np.finfo(float).tiny))
    tangent=s*np.linalg.solve(s[:,None]*B*s[None,:],s*rhs)
    vp,yp=tangent[:n],tangent[n:-2];gx=a0['gradient'][:n];v=eta[n:2*n]
    force_first=a0['Lxx']@v+a0['Lxv']@vp+a0['Lxy']@yp+initial['gradient_clock_first'][:n]
    prediction=np.r_[eta[:n]+h*v+h*h*vp/2,p0+h*gx+h*h*force_first/2,v+h*vp/2,eta[2*n:]+h*yp/2]
    guess=np.r_[eta[:n],prediction[2*n:]]
    evaluate=lambda e:holomorphic_inherited_child_action(P@e,time+h/2,pair,ref,rep,**params)
    out.mkdir(parents=True);archives={}
    def save(name,arrays):
        p=out/name;_compressed_npz(p,arrays)
        if p.stat().st_size>10*1024**2:raise RuntimeError('split all original canonical rows')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    save('original_coordinate_time_canonical_tangent.npz',dict(initial_master=eta,initial_raw=P@eta,
        initial_Pi=p0,initial_constitutive_rows=r0,gradient_clock_first=initial['gradient_clock_first'],
        canonical_tangent_operator=D,canonical_tangent_rhs=initial['canonical_tangent_rhs'],
        tangent_velocity_algebraic=tangent[:-2],named_tangent_frame_reactions=tangent[-2:],
        original_tangent_rows=D@tangent[:-2]-initial['canonical_tangent_rhs'],
        framed_tangent_rows=B@tangent-rhs,literal_gauge_tangent_source=frame['literal_generators'].T@rhs[:-2],
        initial_coordinate_time=np.array(time),coordinate_time_step=np.array(h),prediction=prediction))
    def checkpoint(i,z,rho,a,f,K,scale,history):
        save(f'iteration_{i:04d}.npz',dict(unknowns=z,midpoint_raw=P@a['midpoint_coefficients'],
            residual=a['residual'],jacobian=a['jacobian'],frame_reactions=rho,
            framed_rows=f,framed_Jacobian=K,row_scale=scale))
        print(json.dumps(dict(stage='original_complex_canonical_exterior_step',**history[-1]),sort_keys=True),flush=True)
    result=solve_complex_canonical_midpoint(eta[:n],p0,guess,h,evaluate,frame,
        frame_reference=reference,start_reaction=data['frame_reactions'],initial_unknowns=prediction,
        tolerance=tolerance,max_iterations=max_iterations,checkpoint=checkpoint)
    a=result['application'];final_eta=np.r_[a['x_new'],a['v_mid'],a['y_mid']]
    save('application.npz',dict(initial_master=eta,initial_Pi=p0,unknowns=result['unknowns'],
        stage_midpoint_master=a['midpoint_coefficients'],stage_midpoint_raw=P@a['midpoint_coefficients'],
        x_final=a['x_new'],p_final=a['p_new'],endpoint_stage_guess=final_eta,
        coordinate_time_initial=np.array(time),coordinate_time_midpoint=np.array(time+h/2),coordinate_time_final=np.array(time+h),
        original_rows=a['residual'],original_jacobian=a['jacobian'],frame_reactions=result['frame_reactions'],
        framed_rows=result['framed_rows'],initial_action_cotangent=a['initial_action_cotangent'],
        final_action_cotangent=a['final_action_cotangent'],all_algebraic_action_cotangent=a['algebraic_action_cotangent']))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for p in(Path(__file__),'tests/test_muon_complex_canonical_midpoint.py'):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/r).read_bytes()).hexdigest()!=v for r,v in refs.items()):raise RuntimeError('same full canonical action changed')
    md=dict(classification='EVALUATED_ORIGINAL_COMPLEX_FULL_CANONICAL_EXTERIOR_MIDPOINT_STEP',input_hashes=refs,archives=archives,
        status=result['status'],history=result['history'],tolerance=tolerance,step_coordinate_time=[h.real,h.imag],
        initial_original_rows_max=float(np.max(abs(r0))),all_original_stage_rows_max=float(np.max(abs(a['residual']))),
        initial_action_Pi_contact_max=float(np.max(abs(a['initial_action_cotangent']+p0))),
        final_action_Pi_contact_max=float(np.max(abs(a['final_action_cotangent']-a['p_new']))),
        original_Gauss_multiplier_max=float(np.max(abs(a['residual'][3*n:]))),
        named_frame_reaction_max=float(np.max(abs(result['frame_reactions']))),
        explicit_inherited_clock_contact_retained=True,old_real_momentum_grafted=False,
        all_original_Gauss_multiplier_geometry_profile_rows_retained=True,
        initial_state_compatible=True,endpoint_held_stage_guess_not_constitutive_reconstruction=True,
        physical_stop_selected=False,physical_stop_coordinate='selected same-action Euler-Dirac eigenvalue, not normal amplitude98 or numerical exhaustion node1150',
        error_scope='binary64 original complex coordinate-time canonical midpoint and exact explicit-clock tangent; no selected physical exterior/stop or Pauli enclosure')
    p=out/'result.json';p.write_text(json.dumps(md,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='original_complex_canonical_step_complete',status=result['status'],
        original_stage_rows_max=md['all_original_stage_rows_max'],result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--initial-folder',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--step',type=complex,default=1e-8)
    p.add_argument('--max-iterations',type=int,default=12);p.add_argument('--tolerance',type=float,default=2e-10)
    a=p.parse_args();materialize(a.initial_folder,a.output,a.step,a.max_iterations,a.tolerance)
