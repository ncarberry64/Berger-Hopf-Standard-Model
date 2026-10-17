"""Source-driven canonical mean application of the retained full-field action.

The source is the literal paired derivative D_z S_AB, including its source
motion contacts.  The canonical momentum includes g_v once.  A numerical
prefix is not identified with E0, and a fixed-reference birth identity is
not the differentiated moving full-field reset graph.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_birth_chronological_boundary_action import retained_chronological_boundary_application
from .muon_birth_trace_enriched_action import generic_coordinate_lift
from .muon_trace_enriched_charged_current_response import enriched_central_profiles
from .muon_birth_phase_continuation import _compressed_npz


def _forced_arb_application(H0,h0,g0,s0,C0,*,precision_bits=160):
    """Enclose the literal stored coefficients and every inhomogeneous row."""
    from flint import arb,arb_mat,ctx
    previous=ctx.prec;ctx.prec=precision_bits
    try:
        H=arb_mat(H0.tolist());h=arb(float(h0));n=C0.shape[1];f=len(C0)
        g=arb_mat(g0.tolist());s=arb_mat(s0.tolist());m=H.nrows()-2*n;b=g.ncols()
        Z=lambda r,c:arb_mat(r,c)
        def block(a,r0,r1,c0,c1):
            return arb_mat([[a[i,j] for j in range(c0,c1)] for i in range(r0,r1)]) if r1>r0 else Z(0,c1-c0)
        def stack(rows):
            return arb_mat([[a[i,j] for a in row for j in range(a.ncols())]
                for row in rows for i in range(row[0].nrows())])
        xx=block(H,0,n,0,n);xv=block(H,0,n,n,2*n);xy=block(H,0,n,2*n,2*n+m)
        vx=block(H,n,2*n,0,n);vv=block(H,n,2*n,n,2*n);vy=block(H,n,2*n,2*n,2*n+m)
        yx=block(H,2*n,2*n+m,0,n);yv=block(H,2*n,2*n+m,n,2*n);yy=block(H,2*n,2*n+m,2*n,2*n+m)
        C=arb_mat(C0.tolist()) if f else Z(0,n)
        x0=block(s,0,n,0,b);p0=block(s,n,2*n,0,b)
        gx=block(g,0,n,0,b);gv=block(g,n,2*n,0,b);gy=block(g,2*n,2*n+m,0,b)
        A=stack([[vv+h*(vx-xv)/2-h*h*xx/4,vy-h*xy/2,-C.transpose()],
                 [yv+h*yx/2,yy,Z(m,f)],[C,Z(f,m),Z(f,f)]])
        rhs=stack([[p0-(vx-h*xx/2)*x0-gv+h*gx/2],[-yx*x0-gy],[Z(f,b)]])
        X=A.solve(rhs)
        if not all(X[i,j].is_finite() for i in range(X.nrows()) for j in range(b)):
            raise ArithmeticError('stored forced canonical inverse was not certified')
        v=block(X,0,n,0,b);y=block(X,n,n+m,0,b);rho=block(X,n+m,n+m+f,0,b)
        x1=x0+h*v;eta=stack([[x0+h*v/2],[v],[y]])
        Lx=block(H,0,n,0,2*n+m)*eta+gx
        Lv=block(H,n,2*n,0,2*n+m)*eta+gv
        Ly=block(H,2*n,2*n+m,0,2*n+m)*eta+gy
        p1=Lv+h*Lx/2;reaction=h*Lx/2-Lv+p0+C.transpose()*rho
        upper=lambda a:max((float(np.nextafter(float(abs(a[i,j]).upper()),np.inf))
            for i in range(a.nrows()) for j in range(a.ncols())),default=0.)
        def exported(a):
            mid=np.array([[float(a[i,j].mid()) for j in range(a.ncols())]
                for i in range(a.nrows())]).reshape(a.nrows(),a.ncols())
            error=np.array([[float(np.nextafter(float(abs(a[i,j]-arb(float(mid[i,j]))).upper()),np.inf))
                for j in range(a.ncols())] for i in range(a.nrows())]).reshape(a.nrows(),a.ncols())
            return mid,error
        result={}
        for name,a in dict(final_canonical_state=stack([[x1],[p1]]),
            midpoint_velocity_algebraic_lift=eta,frame_reactions=rho,solution=X).items():
            result[name],result[name+'_export_error_upper']=exported(a)
        result['stored_action_arithmetic_certificate']=dict(precision_bits=precision_bits,
            framed_operator_certified_invertible=True,literal_equation_residual_upper=upper(A*X-rhs),
            initial_canonical_reaction_identity_upper=upper(reaction),
            all_algebraic_equations_residual_upper=upper(Ly),frame_equations_residual_upper=upper(C*v),
            canonical_evolution_identity_upper=upper(p1-p0-h*Lx-C.transpose()*rho),
            exact_input_convention='stored binary64 H,h,g,initial_state,C interpreted as exact real coefficients; assembly, solve and contacts use Arb',
            physical_continuum_or_producer_rounding_error_enclosed=False)
        return result
    finally:ctx.prec=previous


def inhomogeneous_canonical_step(action_hessian,positive_step,mean_cotangent,
        initial_canonical_state,frame_covectors=None,*,certify=True):
    """Solve every x/v/y row with the positive chronological source g.

    With eta=(x0+h*v/2,v,y), the rows are
    Lv(eta)+g_v-p0-h*(Lx(eta)+g_x)/2=C.T*rho and
    Ly(eta)+g_y=0, C*v=0.  The final momentum is
    p1=Lv(eta)+g_v+h*(Lx(eta)+g_x)/2.  Momentum is already the
    action coefficient dual, including its density and scalar 2Re factor.
    """
    H=np.asarray(action_hessian,float);h=float(positive_step)
    g=np.asarray(mean_cotangent,float);s=np.asarray(initial_canonical_state,float)
    if s.ndim<2 or s.shape[0]%2:raise ValueError('initial coordinate and canonical-dual rows required')
    n=s.shape[0]//2;shape=s.shape[1:];m=len(H)-2*n
    if n<1 or m<1 or H.shape!=(2*n+m,2*n+m) or g.shape!=(2*n+m,)+shape:
        raise ValueError('complete same-action Hessian and x/v/y source required')
    if not np.isfinite(h) or h<=0 or not all(np.isfinite(a).all() for a in (H,g,s)):
        raise ValueError('finite coefficients and positive chronological step required')
    C=np.zeros((0,n)) if frame_covectors is None else np.asarray(frame_covectors,float)
    if C.ndim!=2 or C.shape[1]!=n or not np.isfinite(C).all():raise ValueError('explicit finite velocity-frame covectors required')
    f=len(C);flat=g.reshape(len(H),-1);initial=s.reshape(2*n,-1);x0,p0=initial[:n],initial[n:]
    gx,gv,gy=flat[:n],flat[n:2*n],flat[2*n:]
    A=np.block([[H[n:2*n,n:2*n]+h*(H[n:2*n,:n]-H[:n,n:2*n])/2-h*h*H[:n,:n]/4,
                 H[n:2*n,2*n:]-h*H[:n,2*n:]/2,-C.T],
                [H[2*n:,n:2*n]+h*H[2*n:,:n]/2,H[2*n:,2*n:],np.zeros((m,f))],
                [C,np.zeros((f,m+f))]])
    rhs=np.r_[p0-(H[n:2*n,:n]-h*H[:n,:n]/2)@x0-gv+h*gx/2,
              -H[2*n:,:n]@x0-gy,np.zeros((f,flat.shape[1]))]
    row=np.max(abs(A),axis=1)
    if np.any(row==0):raise np.linalg.LinAlgError('unbound original canonical row')
    sr=1/row;col=np.max(abs(sr[:,None]*A),axis=0)
    if np.any(col==0):raise np.linalg.LinAlgError('unbound original canonical column')
    sc=1/col;balanced=sr[:,None]*A*sc[None,:]
    X=sc[:,None]*np.linalg.solve(balanced,sr[:,None]*rhs)
    certified=_forced_arb_application(H,h,flat,initial,C) if certify else {}
    if certify:X=certified['solution']
    v,y,rho=X[:n],X[n:n+m],X[n+m:]
    eta=np.r_[x0+h*v/2,v,y];total=H@eta+flat;Lx,Lv,Ly=total[:n],total[n:2*n],total[2*n:]
    final=np.r_[x0+h*v,Lv+h*Lx/2]
    if certify:final=certified['final_canonical_state']
    def shaped(a):return a.reshape((len(a),)+shape)
    result=dict(final_canonical_state=shaped(final),midpoint_velocity_algebraic_lift=shaped(eta),
        frame_reactions=shaped(rho),initial_canonical_state=s.copy(),mean_cotangent=g.copy(),
        literal_framed_operator=A,literal_framed_rhs=rhs,
        solve_residual=shaped(A@X-rhs),scaled_solve_residual=shaped(sr[:,None]*(A@X-rhs)),
        original_algebraic_defect=shaped(Ly),frame_defect=shaped(C@v),
        initial_canonical_reaction_defect=shaped(h*Lx/2-Lv+p0+C.T@rho),
        canonical_evolution_defect=shaped(final[n:]-p0-h*Lx-C.T@rho),
        positive_step=h,balanced_condition_number=float(np.linalg.cond(balanced)),
        true_Lyy_and_all_original_rows_retained=True,spectral_directions_removed=0,
        momentum_source_count=1,physical_E0_or_birth_graph_selected=False)
    for name,value in certified.items():
        if name=='solution':continue
        result[name]=shaped(value) if isinstance(value,np.ndarray) else value
    return result


def retained_magnetic_midpoint_mean_application(mean_directory,*,repository=ROOT):
    """Bind and apply the actual one-cell D3 loads on their identical phase."""
    root=Path(repository);folder=Path(mean_directory);folder=folder if folder.is_absolute() else root/folder
    data=(folder/'mean_load.json').read_bytes();receipt=json.loads(data)
    if receipt['classification']!='EVALUATED_TOTAL_RAW268_CUBIC_MEAN_LOAD_FROM_FRESH_SAME_PHASE_RESPONSES':
        raise ValueError('actual complete raw268 source mean load required')
    refs=dict(receipt['input_hashes'])
    for name,digest in refs.items():
        if sha256((root/name).read_bytes()).hexdigest()!=digest:raise ValueError('consumed mean owner changed: '+name)
    path=folder/receipt['archive']['path'];rawbytes=path.read_bytes()
    if len(rawbytes)!=receipt['archive']['bytes'] or sha256(rawbytes).hexdigest()!=receipt['archive']['sha256']:
        raise ValueError('actual source mean archive changed')
    refs[folder.relative_to(root).as_posix()+'/mean_load.json']=sha256(data).hexdigest()
    refs[path.relative_to(root).as_posix()]=sha256(rawbytes).hexdigest()
    with np.load(path,allow_pickle=False) as saved:arrays={k:saved[k].copy() for k in saved.files}
    outputs={};incoming=None
    for side in ('incoming','outgoing'):
        candidates=[p for p in refs if p.endswith('/result.json') and 'attached_phase_'+side+'_' in p]
        if len(candidates)!=1:raise ValueError('unique same-arm actual attached phase required')
        a=retained_chronological_boundary_application((root/candidates[0]).parent,repository=root)
        if a['receipt']['steps']!=1:raise ValueError('this source receipt owns exactly its one-cell midpoint')
        if not np.array_equal(a['raw_chronological_midpoints'][0],arrays[side+'_raw268']):
            raise ValueError('mean source and action midpoint are not identical')
        rep=a['representation'];c=generic_coordinate_lift(rep['gauge_labels']);P=c['lift'];n=c['x_count']
        source=np.einsum('ij,iab->jab',P,arrays[side+'_raw_mean_cotangent'])
        radial=enriched_central_profiles(rep)['radial_derivative_coefficients']
        Ar=[j for j,i in enumerate(c['dynamic_gauge_indices'])
            if rep['gauge_labels'][i]['field']=='A_rho' and rep['gauge_labels'][i]['internal']==3]
        if len(Ar)!=4:raise ValueError('complete named central radial frame required')
        C=np.zeros((2,n));C[:,38+np.array(Ar)]=radial.T
        app=inhomogeneous_canonical_step(a['action_hessians'][0],a['signed_step'],source,np.zeros((2*n,8,8)),C)
        app.update(action_hessian=a['action_hessians'][0],raw_midpoint=arrays[side+'_raw268'],
            raw_mean_cotangent=arrays[side+'_raw_mean_cotangent'],coordinate_lift=P,frame_covectors=C)
        outputs[side]=app
        if side=='incoming':incoming=app['final_canonical_state']
        else:
            outputs['fixed_reference_identity_birth_diagnostic']=inhomogeneous_canonical_step(
                a['action_hessians'][0],a['signed_step'],source,incoming,C)
    outputs.update(input_hashes=refs,source_receipt=receipt,
        zero_initial_mean_role='particular source application at the finite initial face; not an E0 state selection',
        identity_birth_role='fixed-reference coordinate/canonical-dual identity diagnostic only; nonlinear moving birth trace, cotangent and energy contacts remain separate')
    return outputs


def materialize_magnetic_midpoint_mean_application(mean_directory,output,*,repository=ROOT):
    root=Path(repository);out=Path(output);out=out if out.is_absolute() else root/out
    if out.exists():raise FileExistsError('preserve previous inhomogeneous applications')
    a=retained_magnetic_midpoint_mean_application(mean_directory,repository=root);arrays={};rows={}
    for side in ('incoming','outgoing','fixed_reference_identity_birth_diagnostic'):
        b=a[side];arrays.update({side+'_'+k:v for k,v in b.items() if isinstance(v,np.ndarray)})
        md={k:v for k,v in b.items() if not isinstance(v,np.ndarray)}
        for name in ('solve_residual','scaled_solve_residual','original_algebraic_defect','frame_defect',
            'initial_canonical_reaction_defect','canonical_evolution_defect'):
            md[name+'_max']=float(np.max(abs(b[name]),initial=0.))
        md.update(final_canonical_state_norm=float(np.linalg.norm(b['final_canonical_state'])),
            frame_reaction_norm=float(np.linalg.norm(b['frame_reactions'])),
            mean_cotangent_norm=float(np.linalg.norm(b['mean_cotangent'])))
        rows[side]=md
    refs=dict(a['input_hashes'])
    for name in ('muon_birth_inhomogeneous_canonical_mean','muon_birth_chronological_boundary_action',
        'muon_birth_trace_enriched_action','muon_trace_enriched_charged_current_response'):
        path='src/bhsm/interface/'+name+'.py';refs[path]=sha256((root/path).read_bytes()).hexdigest()
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    md=dict(classification='EVALUATED_SOURCE_DRIVEN_SAME_ACTION_CANONICAL_MEAN_APPLICATION',input_hashes=refs,
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),applications=rows,
        action_equations='Lv+g_v-p0-h*(Lx+g_x)/2=C.T rho; Ly+g_y=0; C v=0; p1=Lv+g_v+h*(Lx+g_x)/2',
        source_derivative_convention='paired D_z S_AB; no factor1/2 and no extra charge, Gram, volume or scalar2Re',
        zero_initial_mean_role=a['zero_initial_mean_role'],identity_birth_role=a['identity_birth_role'],
        true_E1_birth_contacts_consumed=False,physical_E0_boundary_selected=False,physical_formation_or_Pauli_completed=False,
        error_scope='Arb bounds exact stored action/source arithmetic only; physical action rounding, continuum, branch and birth graph errors excluded')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mean-directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();print(json.dumps(materialize_magnetic_midpoint_mean_application(args.mean_directory,args.output),sort_keys=True))
