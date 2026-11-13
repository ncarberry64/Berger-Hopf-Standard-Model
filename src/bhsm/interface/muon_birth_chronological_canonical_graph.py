"""Canonical boundary propagation of the same retained chronological action.

Each cell supplies its complete two-face action Hessian and literal algebraic
rows.  The equations are -delta Pi_initial=K00 dx0+K01 dx1 and
delta Pi_final=K10 dx0+K11 dx1.  A named central radial coordinate frame
retains its reaction, so incompatible initial canonical directions remain
explicit equations rather than being removed by a numerical null projection.
The saved finite incoming prefix is not identified with the actual E0 face.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_birth_chronological_boundary_action import (
    retained_chronological_boundary_application, algebraic_boundary_response,
)
from .muon_birth_trace_enriched_action import generic_coordinate_lift
from .muon_trace_enriched_charged_current_response import enriched_central_profiles
from .muon_birth_phase_continuation import _compressed_npz


def _stored_midpoint_arb_application(H0,h0,C0,*,precision_bits=160):
    """Outward arithmetic for the literal stored H,h,C action relation.

    No Hessian symmetrization is performed. Its binary64 antisymmetry is
    retained as a separately displayed reciprocity term. These intervals
    exclude producer rounding, nonlinear and representation errors.
    """
    from flint import arb,arb_mat,ctx
    old=ctx.prec;ctx.prec=precision_bits
    try:
        H=arb_mat(H0.tolist());h=arb(float(h0));n=C0.shape[1];f=len(C0)
        C=arb_mat(C0.tolist()) if f else arb_mat(0,n)
        m=H.nrows()-2*n
        Z=lambda r,c:arb_mat(r,c)
        def block(a,r0,r1,c0,c1):
            return arb_mat([[a[i,j] for j in range(c0,c1)] for i in range(r0,r1)]) if r1>r0 else arb_mat(0,c1-c0)
        def stack(rows):return arb_mat([[v for a in row for v in [a[i,j] for j in range(a.ncols())]] for row in rows for i in range(row[0].nrows())])
        xx=block(H,0,n,0,n);xv=block(H,0,n,n,2*n);xy=block(H,0,n,2*n,2*n+m)
        vx=block(H,n,2*n,0,n);vv=block(H,n,2*n,n,2*n);vy=block(H,n,2*n,2*n,2*n+m)
        yx=block(H,2*n,2*n+m,0,n);yv=block(H,2*n,2*n+m,n,2*n);yy=block(H,2*n,2*n+m,2*n,2*n+m)
        eye=arb_mat(np.eye(n).tolist());zero=Z(n,n)
        A=stack([[vv+h*(vx-xv)/2-h*h*xx/4,vy-h*xy/2,-C.transpose()],
            [yv+h*yx/2,yy,Z(m,f)],[C,Z(f,m),Z(f,f)]])
        rhs=stack([[-vx+h*xx/2,eye],[-yx,Z(m,n)],[Z(f,n),Z(f,n)]])
        X=A.solve(rhs)
        if not all(X[i,j].is_finite() for i in range(X.nrows()) for j in range(X.ncols())):
            raise ArithmeticError('literal framed canonical action inverse was not certified')
        v=block(X,0,n,0,2*n);dy=block(X,n,n+m,0,2*n);rho=block(X,n+m,n+m+f,0,2*n)
        x0=stack([[eye,zero]]);p0=stack([[zero,eye]])
        x1=x0+h*v;eta=stack([[x0+h*v/2],[v],[dy]])
        dLx=block(H,0,n,0,2*n+m)*eta;dLv=block(H,n,2*n,0,2*n+m)*eta
        p1=dLv+h*dLx/2;E=h*dLx/2-dLv+p0;ydef=block(H,2*n,2*n+m,0,2*n+m)*eta
        M=stack([[x1],[p1]]);Omega=stack([[zero,eye],[-eye,zero]])
        raw_reciprocity=M.transpose()*Omega*M-Omega-(E.transpose()*x0-x0.transpose()*E)
        action_skew=h*eta.transpose()*(H-H.transpose())*eta
        upper=lambda a:max((float(np.nextafter(float(abs(a[i,j]).upper()),np.inf)) for i in range(a.nrows()) for j in range(a.ncols())),default=0.)
        def exported(a):
            mid=np.array([[float(a[i,j].mid()) for j in range(a.ncols())] for i in range(a.nrows())]).reshape(a.nrows(),a.ncols())
            err=np.array([[float(np.nextafter(float(abs(a[i,j]-arb(float(mid[i,j]))).upper()),np.inf)) for j in range(a.ncols())] for i in range(a.nrows())]).reshape(a.nrows(),a.ncols())
            return mid,err
        result={}
        for name,a in dict(solution=X,canonical_map=M,final_coordinate_map=x1,final_momentum_map=p1,
            midpoint_velocity_algebraic_lift=eta,algebraic_lift=dy,frame_reaction_map=rho,
            action_antisymmetry_reciprocity_term=action_skew).items():
            result[name],result[name+'_export_error_upper']=exported(a)
        result['stored_action_arithmetic_certificate']=dict(precision_bits=precision_bits,
            framed_operator_certified_invertible=True,
            literal_equation_residual_upper=upper(A*X-rhs),
            initial_canonical_reaction_identity_upper=upper(E+C.transpose()*rho),
            all_algebraic_equations_residual_upper=upper(ydef),
            frame_equations_residual_upper=upper(C*v),
            reciprocity_after_explicit_action_antisymmetry_upper=upper(raw_reciprocity-action_skew),
            retained_action_antisymmetry_reciprocity_term_upper=upper(action_skew),
            exact_input_convention='stored binary64 H,h,C interpreted as exact real coefficients; all subsequent assembly, solve and contacts use Arb',
            physical_continuum_or_producer_rounding_error_enclosed=False)
        return result
    finally:ctx.prec=old


def canonical_boundary_step_action(boundary_hessian, dynamic_count, frame_covectors=None,*,action_hessian=None,positive_step=None):
    """Apply the full action relation to every initial (x,Pi) direction.

    The frame condition C(dx1-dx0)=0 is a coefficient velocity choice. Its
    reaction rho is retained in K00 dx0+K01 dx1+dPi0=-C.T rho.  Thus
    rho(input)=0 is the exact represented compatibility equation, not a
    claim that arbitrary initial canonical data satisfy all constraints.
    The original algebraic equations are solved and returned without an
    additional density or Gram factor; Pi is already the action covector.
    """
    K=np.asarray(boundary_hessian,float);n=int(dynamic_count)
    if n<1 or K.ndim!=2 or K.shape[0]!=K.shape[1] or len(K)<=2*n or not np.isfinite(K).all():
        raise ValueError('complete two-face same-action Hessian required')
    C=np.zeros((0,n)) if frame_covectors is None else np.asarray(frame_covectors,float)
    if C.ndim!=2 or C.shape[1]!=n or not np.isfinite(C).all():
        raise ValueError('explicit final-coordinate frame covectors required')
    response=algebraic_boundary_response(K,n);D=response['DtN'];f=len(C)
    if (action_hessian is None)!=(positive_step is None):raise ValueError('action Hessian and positive step must be supplied together')
    stable=action_hessian is not None
    x0=np.c_[np.eye(n),np.zeros((n,n))];p0=np.c_[np.zeros((n,n)),np.eye(n)]
    if stable:
        H=np.asarray(action_hessian,float);h=float(positive_step);m=len(K)-2*n
        if H.shape!=K.shape or not np.isfinite(H).all() or not np.isfinite(h) or h<=0:raise ValueError('same full action Hessian and positive chronological step required')
        # Lv-p0-h Lx/2=0, Ly=0, evaluated at delta x_mid=dx0+h dv/2.
        # This avoids subtracting two O(1/h) endpoint kinetic blocks.
        Avv=H[n:2*n,n:2*n]+h*(H[n:2*n,:n]-H[:n,n:2*n])/2-h*h*H[:n,:n]/4
        Avy=H[n:2*n,2*n:]-h*H[:n,2*n:]/2
        Ayv=H[2*n:,n:2*n]+h*H[2*n:,:n]/2
        A=np.block([[Avv,Avy,-C.T],[Ayv,H[2*n:,2*n:],np.zeros((m,f))],[C,np.zeros((f,m+f))]])
        rhs=np.zeros((n+m+f,2*n));rhs[:n]=p0-(H[n:2*n,:n]-h*H[:n,:n]/2)@x0
        rhs[n:n+m]=-H[2*n:,:n]@x0
    else:
        A=np.block([[D[:n,n:],C.T],[C,np.zeros((f,f))]])
        rhs=np.zeros((n+f,2*n));rhs[:n,:n]=-D[:n,:n];rhs[:n,n:]=-np.eye(n);rhs[n:,:n]=C
    row=np.max(abs(A),axis=1)
    if np.any(row==0):raise np.linalg.LinAlgError('unbound literal canonical boundary row')
    sr=1/row;col=np.max(abs(sr[:,None]*A),axis=0)
    if np.any(col==0):raise np.linalg.LinAlgError('unbound literal canonical boundary column')
    sc=1/col;balanced=sr[:,None]*A*sc[None,:]
    solution=sc[:,None]*np.linalg.solve(balanced,sr[:,None]*rhs)
    certified=_stored_midpoint_arb_application(H,h,C) if stable else {}
    if stable:solution=certified['solution']
    if stable:
        v=solution[:n];dy=solution[n:n+m];rho=solution[n+m:];x1=x0+h*v
        eta=np.r_[x0+h*v/2,v,dy];dLx=H[:n]@eta;dLv=H[n:2*n]@eta
        x1=certified['final_coordinate_map'];p1=certified['final_momentum_map'];initial_defect=h*dLx/2-dLv+p0
        final_defect=dLv+h*dLx/2-p1;algebraic_defect=H[2*n:]@eta
    else:
        x1=solution[:n];rho=solution[n:];p1=D[n:,:n]@x0+D[n:,n:]@x1
        faces=np.r_[x0,x1];dy=response['algebraic_response_map']@faces
        eta=np.empty((0,2*n));initial_defect=K[:n]@np.r_[faces,dy]+p0
        final_defect=K[n:2*n]@np.r_[faces,dy]-p1;algebraic_defect=K[2*n:]@np.r_[faces,dy]
    faces=np.r_[x0,x1];lift=np.r_[faces,dy]
    Omega=np.block([[np.zeros((n,n)),np.eye(n)],[-np.eye(n),np.zeros((n,n))]])
    M=np.r_[x1,p1]
    # Boundary reciprocity is exact on the compatible, framed domain. Off
    # that domain its explicit initial-face reaction accounts for the defect.
    reciprocity=M.T@Omega@M-Omega
    reaction_identity=reciprocity-(initial_defect.T@x0-x0.T@initial_defect)
    result=dict(canonical_map=M,initial_coordinate_map=x0,initial_momentum_map=p0,
        final_coordinate_map=x1,final_momentum_map=p1,full_boundary_algebraic_lift=lift,
        algebraic_lift=dy,frame_reaction_map=rho,compatibility_equations=rho,
        frame_covectors=C,framed_matrix=A,right_hand_side=rhs,solution=solution,
        row_scale=sr,column_scale=sc,solve_residual=A@solution-rhs,
        scaled_solve_residual=sr[:,None]*(A@solution-rhs),
        original_initial_canonical_defect=initial_defect,
        original_final_canonical_defect=final_defect,original_algebraic_defect=algebraic_defect,
        midpoint_velocity_algebraic_lift=eta,stable_midpoint_action_application=stable,
        endpoint_matrix_arithmetic_defect=K@lift-np.r_[initial_defect-p0,p1,algebraic_defect*(positive_step if stable else 1.)],
        reaction_defect=initial_defect+C.T@rho,frame_defect=C@(x1-x0),
        symplectic_defect=reciprocity,canonical_reciprocity_identity_defect=reaction_identity,
        complete_two_face_DtN=D,balanced_condition_number=float(np.linalg.cond(balanced)),
        true_Lyy_and_all_algebraic_rows_retained=True,spectral_directions_removed=0,
        physical_E0_boundary_or_normal_mode_selected=False,
        canonical_pairing_rule='initial action contact=-Pi_initial; final action contact=+Pi_final; Pi is the existing coefficient-dual density')
    result.update(certified)
    return result


def chronological_canonical_graph(cell_hessians,dynamic_count,frame_covectors=None,*,action_hessians=None,positive_step=None):
    """Compose every chronological cell and all compatibility equations."""
    cells=np.asarray(cell_hessians,float);n=int(dynamic_count)
    if cells.ndim!=3 or len(cells)<1:raise ValueError('nonempty complete chronological action cells required')
    M=np.eye(2*n);steps=[];compat=[];lifts=[];maps=[]
    if (action_hessians is None)!=(positive_step is None):raise ValueError('complete stable action cells and positive step must be supplied together')
    for k,K in enumerate(cells):
        opts={} if action_hessians is None else dict(action_hessian=action_hessians[k],positive_step=positive_step)
        a=canonical_boundary_step_action(K,n,frame_covectors,**opts)
        compat.append(a['compatibility_equations']@M)
        lifts.append(a['full_boundary_algebraic_lift']@M)
        M=a['canonical_map']@M;maps.append(M.copy());steps.append(a)
    return dict(canonical_map=M,compatibility_equations=np.concatenate(compat),
        cell_full_boundary_algebraic_lifts=np.array(lifts),chronological_partial_maps=np.array(maps),
        cell_applications=steps,initial_boundary_graph_replaced=False,
        boundary_composition_rule='a supplied initial action graph is propagated by these equations; compatibility rows remain equations of that graph, not extra prescribed trace data')


def retained_chronological_canonical_graph(phase_directory,*,repository=ROOT):
    """Execute the canonical graph on the saved corrected full-field phase."""
    a=retained_chronological_boundary_application(phase_directory,repository=repository)
    rep=a['representation'];c=generic_coordinate_lift(rep['gauge_labels']);n=c['x_count']
    radial=enriched_central_profiles(rep)['radial_derivative_coefficients']
    Ar=[j for j,i in enumerate(c['dynamic_gauge_indices'])
        if rep['gauge_labels'][i]['field']=='A_rho' and rep['gauge_labels'][i]['internal']==3]
    if len(Ar)!=4:raise ValueError('actual complete enriched central radial frame required')
    C=np.zeros((2,n));C[:,38+np.array(Ar)]=radial.T
    graph=chronological_canonical_graph(a['cell_hessians'],n,C,action_hessians=a['action_hessians'],positive_step=a['signed_step'])
    graph.update(boundary_application=a,frame_rule='two named central A_rho velocity profile covectors; all original reactions retained',
        physical_E0_identification=False)
    return graph


def materialize_chronological_canonical_graph(phase_directory,output,*,repository=ROOT):
    root=Path(repository);out=Path(output);out=out if out.is_absolute() else root/out
    if out.exists():raise FileExistsError('preserve previous canonical applications')
    g=retained_chronological_canonical_graph(phase_directory,repository=root)
    a=g['boundary_application'];r=a['receipt'];n=r['dynamic_count']
    arrays={k:g[k] for k in ('canonical_map','compatibility_equations','cell_full_boundary_algebraic_lifts','chronological_partial_maps')}
    rows=[]
    for k,b in enumerate(g['cell_applications']):
        for name,value in b.items():
            if isinstance(value,np.ndarray):arrays[f'cell_{k:04d}_'+name]=value
        md={name:value for name,value in b.items() if not isinstance(value,np.ndarray)}
        for name in ('solve_residual','scaled_solve_residual','reaction_defect','original_algebraic_defect',
            'frame_defect','canonical_reciprocity_identity_defect'):
            md[name+'_max']=float(np.max(abs(b[name]),initial=0.))
        md['original_initial_canonical_defect_norm']=float(np.linalg.norm(b['original_initial_canonical_defect']))
        md['compatibility_equation_norm']=float(np.linalg.norm(b['compatibility_equations']))
        rows.append(md)
    arrays.update(raw_chronological_midpoints=a['raw_chronological_midpoints'],cell_hessians=a['cell_hessians'])
    refs=dict(r['input_hashes']);refs.update({p.relative_to(root).as_posix():h for p,h in a['input_refs'].items()})
    for name in ('muon_birth_chronological_canonical_graph','muon_birth_chronological_boundary_action','muon_trace_enriched_charged_current_response'):
        path='src/bhsm/interface/'+name+'.py';refs[path]=sha256((root/path).read_bytes()).hexdigest()
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    md=dict(scope='EVALUATED_COMPLETE_CHRONOLOGICAL_CANONICAL_GRAPH_APPLICATION',side=r['side'],steps=r['steps'],
        input_hashes=refs,numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        dynamic_count=n,algebraic_count=r['algebraic_count'],action_parameters=r['action_parameters'],cell_applications=rows,
        chronological_role='incoming prefix far-to-E1; outgoing prefix E1-to-future numerical face',
        physical_E0_identification=False,physical_boundary_graph_or_normal_mode_selected=False,
        all_y_Gauss_contacts_and_frame_compatibility_equations_retained=True,
        initial_Dirichlet_restriction_columns=list(range(n,2*n)),
        Dirichlet_restriction_role='available action application only; external BRST fermion E0 trace zero does not impose all full-field coordinate traces zero',
        event_second_mean_role='input and birth graph cotangent/source derivatives must be composed; canonical transfer alone does not erase nonlinear reset contacts',
        error_scope='binary64 action graph solves with explicit original-row and reciprocity defects; no continuum, state selection or producer-rounding enclosure')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase-directory',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    args=p.parse_args();print(json.dumps(materialize_chronological_canonical_graph(args.phase_directory,args.output),sort_keys=True))
