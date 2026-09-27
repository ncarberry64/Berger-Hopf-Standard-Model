"""Signed action Jacobian and implicit history jet at the coupled center."""
import argparse
import io
import json
from pathlib import Path
import time

import solve_n12_gate7_fiber_constrained_center as solve
import numpy as np
from flint import arb, arb_mat, ctx
from bhsm.interface.physical_hs_value import restore_balls, rational_balls
from checkpoint_n12_gate7_66d_tangent_binding import amat, bound, digest, encoded
from diagnose_n12_gate7_eight_reaction_center import block, identity
from compare_n12_gate7_reduced_fiber_tangents import comparison


def save_arrays(path, data):
    arrays={}
    for key,value in data.items():
        if isinstance(value,arb_mat):value=solve.array(value)
        m,r=rational_balls(value);arrays[key+'_mid_q']=m;arrays[key+'_rad_q']=r
    buffer=io.BytesIO();np.savez_compressed(buffer,**arrays);path.write_bytes(buffer.getvalue())


def calculate(center,out,uniform_from=None):
    ctx.prec=512;problem=solve.load_problem();data={};points={}
    if uniform_from is not None:
        certified=json.loads((uniform_from/'report.json').read_bytes())
        if (certified['status']!='LOCAL_COUPLED_CENTER_NEIGHBORHOOD_CERTIFIED'
                or digest(center/'arrays.npz') not in certified['source_SHA256'].values()):
            raise ValueError('matching certified center neighborhood required')
    with np.load(center/'arrays.npz') as z:
        for name in ('left_endpoint','right_endpoint','midpoint'):
            data[name]=restore_balls(z[name+'_mid_q'],z[name+'_rad_q'])
    for name in ('left_endpoint','right_endpoint','midpoint'):
        start=time.monotonic()
        # Cache each local derivative separately to survive interruptions.
        cache=out/(name+'.npz')
        if uniform_from is not None:
            source_name={'left_endpoint':'left','right_endpoint':'right'}.get(name,name)
            source=uniform_from/(source_name+'.npz')
            if digest(source)!=certified['local_derivative_SHA256'][source_name]:
                raise ValueError('certified uniform derivative hash mismatch')
            with np.load(source) as z:
                points[name]={k[:-6]:restore_balls(z[k],z[k[:-6]+'_rad_q'])
                              for k in z.files if k.endswith('_mid_q')}
            if not cache.exists():cache.write_bytes(source.read_bytes())
        elif cache.exists():
            metadata=json.loads((out/(name+'.json')).read_bytes())
            if (metadata['state_SHA256']!=digest(center/'arrays.npz')
                    or metadata['source_SHA256']!=digest(Path(solve.__file__))
                    or metadata['derivative_SHA256']!=digest(cache)):
                raise ValueError('cached local derivative is for a different source or center')
            with np.load(cache) as z:
                points[name]={k[:-6]:restore_balls(z[k],z[k[:-6]+'_rad_q'])
                              for k in z.files if k.endswith('_mid_q')}
        else:
            p=solve.point(data[name],problem['w'],problem['reference'],np.eye(99))
            points[name]={k:p[k] for k in ('rate','derivative','covector','DC','constraints')}
            save_arrays(cache,points[name])
            (out/(name+'.json')).write_bytes(encoded(dict(
                state_SHA256=digest(center/'arrays.npz'),derivative_SHA256=digest(cache),
                eigenpair_proof=p['eigenpair_proof'],source_SHA256=digest(Path(solve.__file__)))))
            # Use the same outward serialization path on fresh and cached runs.
            with np.load(cache) as z:
                points[name]={k[:-6]:restore_balls(z[k],z[k[:-6]+'_rad_q'])
                              for k in z.files if k.endswith('_mid_q')}
        print(name,'local derivative ready',round(time.monotonic()-start,2),flush=True)
    pl,pr,pm=[points[k] for k in ('left_endpoint','right_endpoint','midpoint')]
    jl,jr,jm=[solve.matrix(p['derivative']) for p in (pl,pr,pm)]
    h=problem['h'];eye=identity(99)
    dl=-eye-jl*(h/6)-jm*(eye/2+jl*(h/8))*(2*h/3)
    dr=eye-jr*(h/6)-jm*(eye/2-jr*(h/8))*(2*h/3)
    left_dc,right_dc=[solve.matrix(p['DC']) for p in (pl,pr)]
    L,R,test=problem['L'],problem['R'],problem['test']
    J=arb_mat(125,125)
    c0=left_dc*block(L,range(98),range(26))
    c1=right_dc*block(R,range(98),range(99))
    hl,hr=test*dl*L,test*dr*R
    g=arb_mat(1,98,list(pl['covector']))
    gf=g*block(L,range(98),range(26))/arb(1e-7)
    gf[0,25]-=1
    for i in range(25):
        for j in range(26):J[i,j]=c0[i,j]/problem['scales'][0,i]
        for j in range(99):J[25+i,26+j]=c1[i,j]/problem['scales'][1,i]
    for i in range(74):
        for j in range(26):J[50+i,j]=hl[i,j]
        for j in range(99):J[50+i,26+j]=hr[i,j]
    for j in range(26):J[124,j]=gf[0,j]
    inv=J.inv();proposal=arb_mat(125,125,[v.mid() for v in inv.entries()])
    # Eliminate the right constraint normals inside the derivative, retaining
    # the inherited 73 tangent coordinates, then append the left fiber row.
    with np.load(solve.ROOT/solve.PHYSICAL) as z:B=amat(z['endpoint_physical_tangent_action'][14])
    right_normal=right_dc.transpose()
    lift=B-right_normal*(right_dc*right_normal).solve(right_dc*B)
    E=arb_mat(99,74)
    for i in range(98):
        for j in range(73):E[i,j]=lift[i,j]
    E[98,73]=arb(1e-7)
    M=test*dr*E;n=test*dl*block(L,range(99),[25])
    K=arb_mat(75,75)
    for i in range(74):
        K[i,0]=n[i,0]
        for j in range(74):K[i,1+j]=M[i,j]
    K[74,0]=-1
    # 66 independent left chart parameters; normal and descriptor response
    # are solved together with right history. This is the fiber graph jet;
    # a fixed-label first-hit restriction is a distinct parameterization.
    with np.load(solve.BASE/'gate7_66d_checkpoint_20260926/binding/arrays.npz') as z:
        T=amat(z['node_013_child_state'])
    forcing=arb_mat(125,66)
    cp=left_dc*T
    ep=arb_mat(99,66)
    for i in range(98):
        for j in range(66):ep[i,j]=T[i,j]
    hp=test*dl*ep;fp=g*T/arb(1e-7)
    for i in range(25):
        for j in range(66):forcing[i,j]=cp[i,j]/problem['scales'][0,i]
    for i in range(74):
        for j in range(66):forcing[50+i,j]=hp[i,j]
    for j in range(66):forcing[124,j]=fp[0,j]
    response=-J.solve(forcing)
    left=ep+L*block(response,range(26),range(66))
    right=R*block(response,range(26,125),range(66))
    fiberjet=g*block(left,range(98),range(66))-block(left,[98],range(66))
    singular=np.linalg.svd(solve.mid(solve.array(K)),compute_uv=False)
    ki=K.inv();kp=arb_mat(75,75,[v.mid() for v in ki.entries()])
    with np.load(solve.BASE/'gate7_8reaction_center_20260926/arrays.npz') as z:P=amat(z['trial_transform'])
    Pi=P.inv();MP=Pi*M*P
    mpp=block(MP,range(66),range(66));mpq=block(MP,range(66),range(66,74))
    mqp=block(MP,range(66,74),range(66));mqq=block(MP,range(66,74),range(66,74))
    schur=mpp-mpq*mqq.solve(mqp)
    jetpair=np.vstack((solve.mid(solve.array(block(left,range(98),range(66)))),
                       solve.mid(solve.array(block(right,range(98),range(66))))))
    # Fixed-label first-hit chart: the existing normalized flow replaces the
    # independent left descriptor coordinate INSIDE the coupled system.
    # Base label is the solved center's s13. Its variation is exactly zero.
    Lfixed=arb_mat(L.tolist())
    for i in range(98):Lfixed[i,25]=pl['rate'][i]
    Lfixed[98,25]=0
    if uniform_from is not None:
        with np.load(uniform_from/'arrays.npz') as z:
            Lfixed=solve.matrix(restore_balls(z['left_phase_chart_mid_q'],z['left_phase_chart_rad_q']))
    Jfixed=arb_mat(J.tolist())
    phase=block(Lfixed,range(99),[25])
    dcphase=left_dc*block(phase,range(98),[0])
    hsphase=test*dl*phase
    for i in range(25):Jfixed[i,25]=dcphase[i,0]/problem['scales'][0,i]
    for i in range(74):Jfixed[50+i,25]=hsphase[i,0]
    phase_slope=(g*block(phase,range(98),[0]))[0,0]
    Jfixed[124,25]=phase_slope/arb(1e-7)
    if phase_slope.contains(0):raise ArithmeticError('first-hit phase transversality unresolved')
    fixed_response=-Jfixed.solve(forcing)
    fixed_left=ep+Lfixed*block(fixed_response,range(26),range(66))
    fixed_right=R*block(fixed_response,range(26,125),range(66))
    fixedpair=np.vstack((solve.mid(solve.array(block(fixed_left,range(98),range(66)))),
                         solve.mid(solve.array(block(fixed_right,range(98),range(66))))))
    fi=Jfixed.inv();fi0=arb_mat(125,125,[v.mid() for v in fi.entries()])
    # A and B remain frozen comparisons. The new C columns come from the
    # current coupled Jacobian, including constraint and first-hit reactions.
    with np.load(solve.BASE/'gate7_reduced_fiber_tangents_20260926/arrays.npz') as z:
        old={k:z[k] for k in ('original_left_history','original_right_history',
                             'owner_consistent_left_history','owner_consistent_right_history')}
    with np.load(solve.ROOT/solve.PHYSICAL) as z:Bs=z['endpoint_physical_tangent_action'][13:15]
    oldA=np.vstack((Bs[0]@old['original_left_history'][:73],Bs[1]@old['original_right_history'][:73]))
    oldB=np.vstack((Bs[0]@old['owner_consistent_left_history'][:73],Bs[1]@old['owner_consistent_right_history'][:73]))
    comparisons={name:comparison(v,fixedpair) for name,v in [('A_vs_C',oldA),('B_vs_C',oldB)]}
    fixed_gram=block(fixed_left,range(98),range(66)).transpose()*block(fixed_left,range(98),range(66))
    fixed_gram_inverse=fixed_gram.inv()
    paired=arb_mat(block(fixed_left,range(98),range(66)).tolist()+block(fixed_right,range(98),range(66)).tolist())
    projector=paired*(paired.transpose()*paired).inv()*paired.transpose()
    projector_uncertainty=bound(arb_mat(196,196,[v.rad().upper() for v in projector.entries()]))
    right_fiber_jet=arb_mat(1,98,list(pr['covector']))*block(fixed_right,range(98),range(66))-block(fixed_right,[98],range(66))
    stage_source=Path('C:/Users/carbe/Downloads/BHSM_GATE7_STAGEB_RANK_REFINEMENT_20260925_173630.npz')
    with np.load(stage_source) as z:interface=z['node_013_R23']
    interface=interface/np.linalg.norm(interface,axis=1)[:,None]
    with np.load(solve.ROOT/solve.FIXED) as z:C13=z['endpoint_constraint_tangent_action'][13]
    interface_map=amat(interface)*amat(C13.T)
    boundary_fixed=interface_map*block(fixed_left,range(98),range(66))
    save_arrays(out/'arrays.npz',dict(J125=J,K75=K,M74=M,N_left_descriptor=n,
        right_constraint_lift=E,Mqq=mqq,reduced_Schur=schur,forcing=forcing,response=response,
        left_history=left,right_history=right,fiber_jet_residual=fiberjet,
        center_inverse=proposal,left_covector=g,Jfixed125=Jfixed,fixed_label_response=fixed_response,
        fixed_label_left_history=fixed_left,fixed_label_right_history=fixed_right,
        fixed_label_Gram_inverse=fixed_gram_inverse,
        frozen_interface_fixed_label_response=boundary_fixed))
    report=dict(status='COUPLED_CENTER_UNIFORM_JACOBIAN_AND_FIBER_GRAPH_JET' if uniform_from else 'COUPLED_CENTER_POINT_JACOBIAN_AND_FIBER_GRAPH_JET',
        uniform_root_certificate_SHA256=digest(uniform_from/'report.json') if uniform_from else None,
        center_SHA256=digest(center/'arrays.npz'),arrays_SHA256=digest(out/'arrays.npz'),
        source_SHA256={str(p.relative_to(solve.ROOT)):digest(p) for p in (Path(__file__),Path(solve.__file__))},
        consumed_SHA256={str(p):digest(p) for p in (solve.ROOT/solve.FIXED,solve.ROOT/solve.PHYSICAL,
            stage_source,solve.BASE/'gate7_66d_checkpoint_20260926/binding/arrays.npz',
            solve.BASE/'gate7_8reaction_center_20260926/arrays.npz',
            solve.BASE/'gate7_reduced_fiber_tangents_20260926/arrays.npz')},
        local_derivative_SHA256={n:digest(out/(n+'.npz')) for n in ('left_endpoint','right_endpoint','midpoint')},
        current_Jacobian_shape=[125,125],inverse_left_defect=bound(identity(125)-proposal*J),
        inverse_right_defect=bound(identity(125)-J*proposal),reduced_shape=[75,75],
        reduced_rank_diagnostic=int(np.linalg.matrix_rank(solve.mid(solve.array(K)))),
        reduced_sigma_min=float(singular[-1]),reduced_condition=float(singular[0]/singular[-1]),
        reduced_inverse_left_defect=bound(identity(75)-kp*K),
        reduced_inverse_right_defect=bound(identity(75)-K*kp),
        singular_spectrum=singular.tolist(),reaction8_shape=[8,8],
        reaction8_condition_diagnostic=float(np.linalg.cond(solve.mid(solve.array(mqq)))),
        signed_implicit_equation_residual=bound(J*response+forcing),fiber_jet_residual=bound(fiberjet),
        graph_history_rank_diagnostic=int(np.linalg.matrix_rank(jetpair)),
        graph_descriptor_response_norm=bound(block(left,[98],range(66))),
        fixed_label_tangent_constructed=True,
        fixed_label_scope='Implicit derivative in the C2 flow-aligned chart; label is fixed. Uniform coefficients are provided when a neighborhood packet is supplied. Extension to the full physical parameter tube remains open.',
        fixed_label_phase_source='Existing normalized cancelled Euler-Dirac state rate at the corrected left point; phase is a first-hit coordinate, not an extra physical input.',
        fixed_label_descriptor_variation=bound(block(fixed_left,[98],range(66))),
        fixed_label_fiber_derivative=bound(g*block(fixed_left,range(98),range(66))),
        fixed_label_equation_replay=bound(Jfixed*fixed_response+forcing),
        right_fiber_derivative_defect=bound(right_fiber_jet),
        right_fiber_scope='Retained discrete HS fiber drift; the right owner fiber is evaluated, not silently substituted for the integrated descriptor row.',
        fixed_label_rank_diagnostic=int(np.linalg.matrix_rank(fixedpair)),
        fixed_label_left_rank_certified_by_Gram_inverse=66,
        fixed_label_phase_slope_lower=str(phase_slope.lower().fmpq()),
        fixed_label_phase_slope_diagnostic=float(phase_slope.mid()),
        fixed_label_inverse_left_defect=bound(identity(125)-fi0*Jfixed),
        fixed_label_inverse_right_defect=bound(identity(125)-Jfixed*fi0),
        action_metric_comparisons=comparisons,
        paired_projector_uncertainty_Frobenius_upper=projector_uncertainty,
        comparison_scope='Angles are binary64 diagnostics of midpoint subspaces in the paired positive action norm. The new projector has the separately reported outward coefficient uncertainty. Frozen A/B physical transfer errors are not silently removed.',
        frozen_interface_response_row_norms=[bound(block(boundary_fixed,[i],range(66))) for i in range(7)],
        interface_interpretation='These nonzero derivatives require phase-transported environment/interface data for a physical 66D fixed-label interpretation. With the seven historical interface data held fixed, do not promote this chart to the Stage-B child tangent.',
        tangent_scope='66-parameter fiber graph jet of the declared coupled residual at a corrected point. ds=g*dY is slaved, not an independent input. Not yet the fixed-label first-hit jet.',
        center_existence_neighborhood_certified=uniform_from is not None,seven_nonlinear_boundary_rows_identified_with_HS=False,
        Layer_C_rebound=False,tolerances_changed=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    (out/'report.json').write_bytes(encoded(report))
    print(json.dumps({k:report[k] for k in ('status','reduced_rank_diagnostic','reduced_condition',
        'reduced_sigma_min','graph_history_rank_diagnostic','graph_descriptor_response_norm')},indent=2))
    return report


def main():
    p=argparse.ArgumentParser();p.add_argument('--center',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--uniform-from',type=Path);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True);calculate(a.center,a.out,a.uniform_from)


if __name__=='__main__':main()
