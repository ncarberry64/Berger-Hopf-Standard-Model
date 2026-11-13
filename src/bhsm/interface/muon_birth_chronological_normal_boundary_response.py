"""Full-field normal boundary response on the saved chronological action.

The numerical far face is held fixed explicitly.  Every birth trace and
algebraic action equation is retained; internal fields are solved rather
than discarded from a normal Hessian column.  This conditional application
is not the full physical event-domain formation operator.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_birth_attached_phase import load_attached_endpoint
from .muon_birth_chronological_boundary_action import retained_chronological_boundary_application
from .muon_birth_chronological_normal_inertia import true_legendre_normal_trial
from .muon_birth_phase_continuation import _compressed_npz
from .muon_birth_candidate_geometry_action import wall_geometry_snapshot
from .muon_birth_trace_enriched_action import generic_coordinate_lift


def full_birth_trace_response(cell_hessian, dynamic_count, birth_face,
                              trial_trace, central_velocity_generators, *, frame='radial'):
    """Solve birth/internal stationarity, including the original y block.

    The unknown order is (x_birth,y,three trace reactions,two frame
    reactions).  The two exact central profiles are computational frames;
    their reactions and every original equation remain in the output.
    There is no inverse of the birth velocity form or spectral deletion.
    """
    K=np.asarray(cell_hessian,float);n=int(dynamic_count);face=int(birth_face)
    B=np.asarray(trial_trace,float);Zx=np.asarray(central_velocity_generators,float)
    m=len(K)-2*n
    if (face not in (0,1) or m<1 or K.shape!=(2*n+m,)*2 or B.shape!=(3,n)
            or Zx.shape!=(n,2) or not all(np.isfinite(a).all() for a in (K,B,Zx))):
        raise ValueError('same complete chronological cell, proper traces and named central profiles required')
    if frame not in ('radial','complete'):raise ValueError('named radial or complete central frame required')
    indices=np.r_[face*n+np.arange(n),2*n+np.arange(m)]
    A=K[np.ix_(indices,indices)];trace=np.c_[B,np.zeros((3,m))]
    saddle=np.block([[A,trace.T],[trace,np.zeros((3,3))]])
    C=np.zeros((2,len(saddle)));C[:,:n]=Zx.T
    if frame=='radial':C[:,n-4:n]=0.
    bordered=np.block([[saddle,C.T],[C,np.zeros((2,2))]])
    rhs=np.zeros((len(bordered),3));rhs[n+m:n+m+3]=np.eye(3)
    row=np.max(abs(bordered),axis=1)
    if np.any(row==0):raise np.linalg.LinAlgError('literal boundary response contains an unbound action row')
    scale=1/np.sqrt(row);balanced=scale[:,None]*bordered*scale[None,:]
    solution=scale[:,None]*np.linalg.solve(balanced,scale[:,None]*rhs)
    X=solution[:n+m];residual=bordered@solution-rhs
    # Apply the literal y equations to the central boundary image as well.
    ya=A[n:,n:];yb=A[n:,:n]
    sy=1/np.sqrt(np.max(abs(ya),axis=1))
    Zy=-sy[:,None]*np.linalg.solve(sy[:,None]*ya*sy[None,:],sy[:,None]*yb@Zx)
    Z=np.vstack((Zx,Zy,np.zeros((3,2))))
    return dict(response=X.T@A@X,birth_trace_lift=X[:n],algebraic_lift=X[n:],
        original_action_block=A,trial_trace=B,original_saddle=saddle,
        framed_saddle=bordered,right_hand_side=rhs,solution=solution,row_scale=scale,
        full_original_equation_residual=saddle@solution[:-2]-rhs[:-2],
        solve_residual=residual,scaled_solve_residual=scale[:,None]*residual,
        trace_residual=B@X[:n]-np.eye(3),frame_reactions=solution[-2:],
        original_algebraic_residual=A[n:]@X,central_generators=Z,
        literal_gauge_Ward_image=saddle@Z,central_source_pairing=Z.T@rhs[:-2],
        frame_condition=C@solution[:-2],indices=indices,
        balanced_condition_number=float(np.linalg.cond(balanced)),frame=frame,
        true_Lyy_and_all_Gauss_rows_retained=True,spectral_directions_removed=0,
        numerical_far_face_fixed=True,physical_far_face_selected=False,
        reduced_normal_space_not_disproved_by_internal_field_image=True)


def spatial_slice_normal_jacobi(raw, *, stratum):
    """Apply the spatial-slice J=-Delta-(|A|^2+Ric) to constant normal.

    This is the Riemannian spatial metric at the retained chi=pi/4 wall.
    It is not the worldvolume Jacobi operator: lapse, temporal contacts and
    bulk traction remain in the separately exported weak action.  No raw
    signed Lorentzian area Hessian is substituted for this coefficient.
    """
    x=np.asarray(raw,float)
    if x.ndim!=1 or len(x)<100 or np.any(x[98:100]):
        raise ValueError('retained zero-normal/rate birth wall required')
    w=wall_geometry_snapshot(x[:37],x[37:74],x[74:98]);C=w['C']
    first,second=w['chi_first_log'],w['chi_second_log']
    if stratum=='M8':
        normA=3*(first['A']**2+first['B']**2)/C**2
        ric=-3*(second['A']+first['A']**2+second['B']+first['B']**2)/C**2
        curvature=3*(first['A']+first['B'])/C;dimension=6
        density=w['A']**3*w['B']**3
        angular={'S3_A':1/w['A']**2,'S3_B':1/w['B']**2}
    elif stratum=='M5':
        normA=3*first['R4']**2/C**2
        ric=-3*(second['R4']+first['R4']**2)/C**2
        curvature=3*first['R4']/C;dimension=3
        density=w['R4']**3;angular={'S3_quotient':1/w['R4']**2}
    else:raise ValueError('explicit M8 or M5 spatial slice required')
    return dict(constant_normal_J=float(-(normA+ric)),second_fundamental_squared=float(normA),
        spatial_Ric_normal_normal=float(ric),spatial_mean_curvature=float(curvature),
        spatial_density=float(density),spatial_dimension=dimension,gradient_coefficients=angular,
        normal='outward +C^-1 partial_chi in the positive spatial metric',
        metric_role='spatial-slice Riemannian metric; not complete Lorentzian worldvolume Jacobi',
        stratum=stratum,spatial_constant_normal_closed_by_left_SU2_symmetry=True,
        full_formation_J_or_gamma_selected=False)


def mixed_canonical_far_response(action_hessian, positive_step, birth_face,
                                 kinetic_application, representation):
    """Release the far coordinate at fixed recorded canonical covector.

    S_mixed=S_cell-g_far(base).x_far has the same Hessian as S_cell.
    Work in (x_mid,v,y), where S_cell''=h L'', to avoid subtraction of
    huge 1/h kinetic blocks.  The birth trace is x_mid +/- h v/2.
    Four time-independent central radial potentials have exactly zero
    action rows: their gauge primitives are anchored to zero at the wall.
    The two temporal central generators retain the Higgs velocity lift.
    All six named frames expose reactions; none is an eigenvector cut.

    This is a short-face mixed-canonical application.  Its source covector
    is not identified with the physical E0 boundary graph.
    """
    H=np.asarray(action_hessian,float);h=float(positive_step);face=int(birth_face)
    rep=representation;c=generic_coordinate_lift(rep['gauge_labels']);n=c['x_count'];m=c['y_count']
    if H.shape!=(2*n+m,)*2 or h<=0 or not np.isfinite(H).all() or face not in (0,1):
        raise ValueError('complete retained action and positive chronological step required')
    if kinetic_application['frame']!='temporal':
        raise ValueError('the mixed canonical application consumes the named temporal Legendre frame')
    B=np.asarray(kinetic_application['trial_trace']);A=h*H
    trace=np.zeros((3,len(A)));trace[:,:n]=B;trace[:,n:2*n]=(2*face-1)*h*B/2
    saddle=np.block([[A,trace.T],[trace,np.zeros((3,3))]])
    ar=[38+j for j,i in enumerate(c['dynamic_gauge_indices'])
        if rep['gauge_labels'][i]['field']=='A_rho' and rep['gauge_labels'][i]['internal']==3]
    if len(ar)!=4 or np.any(A[:,ar]):
        raise ValueError('this restricted material homogeneous action must retain its exact static central radial gauge identity')
    C=np.zeros((6,len(saddle)))
    # Same named temporal framing as the true Legendre application.
    C[:2,2*n:len(A)]=kinetic_application['framed_saddle'][-2:,:n+m][:,n:]
    C[2:,ar]=np.eye(4)
    framed=np.block([[saddle,C.T],[C,np.zeros((6,6))]])
    row=np.max(abs(framed),axis=1)
    if np.any(row==0):raise np.linalg.LinAlgError('unframed action row remains')
    scale=1/np.sqrt(row);balanced=scale[:,None]*framed*scale[None,:]
    rhs=np.zeros((len(framed),3));rhs[len(A):len(A)+3]=np.eye(3)
    solution=scale[:,None]*np.linalg.solve(balanced,scale[:,None]*rhs);X=solution[:len(A)]
    velocity=kinetic_application['literal_gauge_generators'][:n+m]
    Z=np.zeros((len(saddle),6));Z[n:len(A),:2]=velocity;Z[np.array(ar),2:]=np.eye(4)
    x_initial=X[:n]-h*X[n:2*n]/2;x_final=X[:n]+h*X[n:2*n]/2
    response=X.T@A@X;residual=framed@solution-rhs
    return dict(response=response,midpoint_velocity_algebraic_lift=X,
        initial_face_lift=x_initial,final_face_lift=x_final,algebraic_lift=X[2*n:],
        original_action_hessian=A,trace=trace,original_saddle=saddle,
        framed_saddle=framed,right_hand_side=rhs,solution=solution,row_scale=scale,
        solve_residual=residual,scaled_solve_residual=scale[:,None]*residual,
        original_equation_residual=saddle@solution[:-6]-rhs[:-6],
        original_y_equation_residual=A[2*n:]@X,frame_reactions=solution[-6:],
        central_generators=Z,literal_gauge_Ward_image=saddle@Z,
        central_source_pairing=Z.T@rhs[:-6],frame_condition=C@solution[:-6],
        static_central_radial_coordinate_indices=np.array(ar),
        balanced_condition_number=float(np.linalg.cond(balanced)),
        fixed_far_canonical_covector=True,numerical_far_face_coordinate_free=True,
        boundary_load_second_derivative=0.,
        actual_E0_boundary_graph_selected=False,spectral_directions_removed=0,
        action_boundary_rule='S_mixed=S_cell-g_far(base).x_far; fixed covector, coordinate free',
        static_gauge_rule='eta_j(rho)=integral_wall^rho B_j(r)dr; eta_j(wall)=0; central Ar shifts leave all curvatures and intrinsic material connection unchanged')


def materialize_boundary_normal_response(phase_directory,output,*,repository=ROOT):
    root=Path(repository);out=Path(output);out=out if out.is_absolute() else root/out
    if out.exists():raise FileExistsError('preserve earlier applications')
    a=retained_chronological_boundary_application(phase_directory,repository=root);r=a['receipt'];rep=a['representation']
    loaded=load_attached_endpoint(r['consumed_paired_endpoint_path'],side=r['side'],repository=root)
    raw=loaded['raw'];n=r['dynamic_count'];face=int(r['side']=='incoming');k=len(a['cell_hessians'])-1 if face else 0
    kinetic=true_legendre_normal_trial(a['action_hessians'][k],raw,rep)
    B=kinetic['trial_trace'];Zx=kinetic['literal_gauge_generators'][:n]
    arrays={};rows=[]
    for frame in ('radial','complete'):
        b=full_birth_trace_response(a['cell_hessians'][k],n,face,B,Zx,frame=frame)
        for name,value in b.items():
            if isinstance(value,np.ndarray):arrays[frame+'_'+name]=value
        md={name:value for name,value in b.items() if not isinstance(value,np.ndarray)}
        md.update(normal_coefficient=float(b['response'][2,2]),response=b['response'].tolist(),
            unscaled_residual_max=float(np.max(abs(b['solve_residual']))),
            balanced_residual_max=float(np.max(abs(b['scaled_solve_residual']))),
            all_y_equation_residual_max=float(np.max(abs(b['original_algebraic_residual']))),
            literal_gauge_Ward_image_max=float(np.max(abs(b['literal_gauge_Ward_image']))),
            gauge_source_pairing_max=float(np.max(abs(b['central_source_pairing']))),
            frame_reaction_max=float(np.max(abs(b['frame_reactions']))),
            full_field_lift_norms=np.linalg.norm(b['birth_trace_lift'],axis=0).tolist())
        rows.append(md)
    mixed=mixed_canonical_far_response(a['action_hessians'][k],a['signed_step'],face,kinetic,rep)
    for name,value in mixed.items():
        if isinstance(value,np.ndarray):arrays['mixed_'+name]=value
    far=1-face
    far_covector=a['cell_gradients'][k,far*n:(far+1)*n]
    arrays['mixed_recorded_far_covector']=far_covector
    mixed_md={name:value for name,value in mixed.items() if not isinstance(value,np.ndarray)}
    mixed_md.update(response=mixed['response'].tolist(),normal_coefficient=float(mixed['response'][2,2]),
        unscaled_residual_max=float(np.max(abs(mixed['solve_residual']))),
        balanced_residual_max=float(np.max(abs(mixed['scaled_solve_residual']))),
        gauge_Ward_image_max=float(np.max(abs(mixed['literal_gauge_Ward_image']))),
        gauge_source_pairing_max=float(np.max(abs(mixed['central_source_pairing']))),
        frame_reaction_max=float(np.max(abs(mixed['frame_reactions']))),
        recorded_far_covector_norm=float(np.linalg.norm(far_covector)),
        base_internal_birth_stationarity_not_asserted=True)
    slices={s:spatial_slice_normal_jacobi(raw,stratum=s) for s in ('M8','M5')}
    arrays.update(birth_raw=raw,cell_hessian=a['cell_hessians'][k],birth_trace=B)
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    refs=dict(r['input_hashes']);refs.update({p.relative_to(root).as_posix():h for p,h in a['input_refs'].items()})
    for name in ('muon_birth_chronological_normal_boundary_response','muon_birth_chronological_normal_inertia',
                 'muon_birth_chronological_boundary_action','muon_birth_candidate_geometry_action'):
        path='src/bhsm/interface/'+name+'.py';refs[path]=sha256((root/path).read_bytes()).hexdigest()
    md=dict(scope='EVALUATED_CONDITIONAL_COMPLETE_BIRTH_TRACE_NORMAL_RESPONSE',side=r['side'],steps=r['steps'],
        input_hashes=refs,numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        action_parameters=r['action_parameters'],birth_adjacent_cell=k,birth_face=face,
        response_applications=rows,mixed_canonical_far_application=mixed_md,separate_spatial_slice_Jacobi=slices,
        temporal_orientation='incoming final +Pi; outgoing initial -Pi; each Hessian differentiates its signed chronological action',
        event_drive_rule='incoming signed action Hessian retained; its negative is the parent contribution in an H_resistance-H_drive split, without assuming drive positivity',
        far_face_role='explicit numerical Dirichlet application, not physical E0/finalchild state selection',
        full_internal_response_retained=True,normal_scalar_symmetry_role='left-SU2 invariant body-frame coefficients and Haar/domain preserve the trivial angular irrep together with its internal responses',
        physical_coupled_birth_transport_and_full_formation_not_claimed=True,
        physical_r_i_drive_gamma_c_or_Pauli_selected=False,
        error_scope='binary64 complete action block solves; scaled and unscaled defects retained; no continuum or producer-rounding enclosure')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase-directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();print(json.dumps(materialize_boundary_normal_response(args.phase_directory,args.output),sort_keys=True))
