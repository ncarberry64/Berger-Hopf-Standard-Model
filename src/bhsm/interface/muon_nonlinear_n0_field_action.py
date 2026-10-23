"""Literal nonlinear homogeneous field action on the restored corner graph.

Geometry, coefficient extension and corner incidence are held at the
caller-supplied same base.  At/Gauss and all radial gauge profiles remain;
only the original initial face and named central-Ar frame are restricted.
This finite field equation is not full quantum background stationarity.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import solve
from .muon_matched_mechanical_source import epsilon
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from .muon_literal_euclidean_wall_action import intrinsic_natural_wall_hessian,VOLUME
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP


def _ad(a):
    z=np.zeros((4,4),complex);z[:3,:3]=np.einsum('abc,a->cb',epsilon(),a[:3])/np.sqrt(2)
    return z


def analytic_constant_maxwell_jet(gauge,gauge_time,gauge_radial,densities):
    """Exact quartic action/gradient/Hessian in the complexified REAL chart."""
    A,At,Ar,c=[np.asarray(x,complex)for x in(gauge,gauge_time,gauge_radial,densities)]
    if any(a.shape!=(5,4)for a in(A,At,Ar))or c.shape!=(5,)or any(not np.isfinite(a).all()for a in(A,At,Ar,c)):
        raise ValueError('complete finite local complex coefficient data required')
    e,r,d,k,beta=c;eps=epsilon();S=np.eye(20).reshape(5,4,20)
    X=At[1]-Ar[0]+_ad(A[0])@A[1]
    T=At[2:]+np.array([_ad(A[0])@a for a in A[2:]])
    R=Ar[2:]+np.array([_ad(A[1])@a for a in A[2:]])
    B=2*A[2:].copy()
    for i,j,h in np.argwhere(eps):B[i]+=.5*eps[i,j,h]*(_ad(A[2+j])@A[2+h])
    JX=np.zeros((4,60),complex);JT=np.zeros((12,60),complex);JR=JT.copy();JB=JT.copy()
    JX[:,:20]=_ad(A[0])@S[1]-_ad(A[1])@S[0];JX[:,20:40]=S[1];JX[:,40:]=-S[0]
    for i in range(3):
        sl=slice(4*i,4*i+4)
        JT[sl,:20]=_ad(A[0])@S[2+i]-_ad(A[2+i])@S[0];JT[sl,20:40]=S[2+i]
        JR[sl,:20]=_ad(A[1])@S[2+i]-_ad(A[2+i])@S[1];JR[sl,40:]=S[2+i]
        JB[sl,:20]=2*S[2+i]
    for i,j,h in np.argwhere(eps):JB[4*i:4*i+4,:20]+=eps[i,j,h]*_ad(A[2+j])@S[2+h]
    Y=T-beta*R;JY=JT-beta*JR
    value=.5*(k*(X@X)+e*np.sum(Y*Y)-r*np.sum(R*R)-d*np.sum(B*B))
    gradient=k*JX.T@X+e*JY.T@Y.ravel()-r*JR.T@R.ravel()-d*JB.T@B.ravel()
    H=k*JX.T@JX+e*JY.T@JY-r*JR.T@JR-d*JB.T@JB;C=np.zeros((20,20),complex)
    def contact(i,j,f):
        b=np.zeros((4,4),complex);b[:3,:3]=np.einsum('abc,c->ab',eps,f[:3])/np.sqrt(2)
        C[4*i:4*i+4,4*j:4*j+4]+=b;C[4*j:4*j+4,4*i:4*i+4]+=b.T
    contact(0,1,k*X)
    for i in range(3):contact(0,2+i,e*Y[i]);contact(1,2+i,-e*beta*Y[i]-r*R[i])
    for i,j,h in np.argwhere(eps):contact(2+j,2+h,-.5*d*eps[i,j,h]*B[i])
    H[:20,:20]+=C
    return dict(value=value,gradient=gradient,hessian=H,curvature_contact=C,
        curvatures=dict(Ftr=X,Ft=T,Fr=R,B=B),pairing='analytic transpose, no coefficient conjugation')


def analytic_intrinsic_n0_jet(connection,H,Hdot,weights,*,lambda_H,nu_squared_action):
    """All real-H4/wall20/Hdot4 rows with the action's single 1/V."""
    A,h,hd,w=[np.asarray(a,complex)for a in(connection,H,Hdot,weights)]
    if A.shape!=(5,4)or h.shape!=(4,)or hd.shape!=(4,)or w.shape!=(3,):raise ValueError('complete intrinsic wall fields required')
    if any(not np.isfinite(a).all()for a in(A,h,hd,w)):raise ValueError('finite intrinsic fields required')
    T=higgs_u2_real_representation()['real_generators'];O=np.einsum('fc,cij->fij',A,T)
    DH=np.r_[(hd+O[0]@h)[None],np.einsum('aij,j->ai',O[2:],h)]
    wt,ws,wv=w;lam=float(lambda_H);nu=float(nu_squared_action);q=h@h-nu
    value=(wt*(DH[0]@DH[0])-ws*np.sum(DH[1:]*DH[1:])-wv*lam*q*q)/VOLUME
    g=np.zeros(28,complex);g[:4]=2*wt*O[0].T@DH[0]-2*ws*np.einsum('aji,aj->i',O[2:],DH[1:])-4*wv*lam*q*h
    U=np.einsum('cij,j->ic',T,h)
    for f,df,weight in((0,DH[0],wt),*((j+2,DH[j+1],-ws)for j in range(3))):g[4+4*f:8+4*f]=2*weight*U.T@df
    g[24:]=2*wt*DH[0];g/=VOLUME
    H2=intrinsic_natural_wall_hessian(A,h,hd,np.zeros((3,1,1)),metric_weights=w,
        lambda_H=lam,nu_squared_action=nu)['hessian']
    return dict(value=value,gradient=g,hessian=H2,covariant_H=DH)


def nonlinear_n0_field_action(coefficients,quadrature,representation,*,temporal_nodes,value_permutation):
    """Evaluate a finite nodal field displacement before taking derivatives.

    Each quadrature row supplies local Lorentz base A/At/Ar and density5
    on the original48 radial points, actual wall A/H/Hdot/weights, lapse,
    holomorphic proper measure, right clock and original corner rows.
    The field derivative uses dtau=i*N*dt.  No algebraic At rate is added.
    """
    n=temporal_nodes;ids=np.asarray(value_permutation,int);x=np.asarray(coefficients,complex)
    if type(n)is not int or n<2 or ids.shape!=(84,)or sorted(ids.tolist())!=list(range(84))or x.shape!=((n-1)*84,)or not np.isfinite(x).all():
        raise ValueError('complete original84 coordinate nodal field and incidence required')
    rep=representation;G=np.asarray(rep['gauge_basis'])[:,:,0];Gr=np.asarray(rep['gauge_radial_basis'])[:,:,0]
    wall=np.asarray(rep['wall_trace_map']).reshape(20,80);rw=np.asarray(rep['radial_quadrature'])
    L=np.eye(84)[:,ids];gv=L[:80];hv=L[80:];time_gv=gv.copy()
    for j,label in enumerate(rep['gauge_labels']):
        if label['field']=='A_tau':time_gv[j]=0
    P=np.einsum('rgfc,ga->rfca',G,gv).reshape(len(rw),20,84)
    Pr=np.einsum('rgfc,ga->rfca',Gr,gv).reshape(len(rw),20,84)
    Pt=np.einsum('rgfc,ga->rfca',G,time_gv).reshape(len(rw),20,84)
    W=wall@gv;full=np.r_[np.zeros((1,84),complex),x.reshape(n-1,84)]
    size=len(x);gradient=np.zeros(size,complex);hessian=np.zeros((size,size),complex);value=0j
    for row in quadrature:
        N=complex(row['N']);clock=complex(row['right_clock']);measure=complex(row['measure'])
        if N==0 or clock==0:raise ValueError('nonzero actual coframe/clock required')
        v=sum(p*full[j]for j,p,_ in row['rows']);dt=(1j*N/clock)*sum(d*full[j]for j,_,d in row['rows'])
        blocks=[(j,p,(1j*N/clock)*d)for j,p,d in row['rows']if j!=0]
        scale=-measure/N
        for r,weight in enumerate(rw):
            A=row['A'][r]+(P[r]@v).reshape(5,4);At=row['At'][r]+(Pt[r]@dt).reshape(5,4);Ar=row['Ar'][r]+(Pr[r]@v).reshape(5,4)
            a=analytic_constant_maxwell_jet(A,At,Ar,row['densities'][r]);factor=scale*weight*MAXWELL_TO_CAP
            value+=factor*a['value']
            maps=[(j,np.r_[p*P[r],d*Pt[r],p*Pr[r]])for j,p,d in blocks]
            for j,J in maps:
                sj=slice((j-1)*84,j*84);gradient[sj]+=factor*J.T@a['gradient']
                for k,K in maps:hessian[sj,slice((k-1)*84,k*84)]+=factor*J.T@a['hessian']@K
        A=row['wall_A']+(W@v).reshape(5,4);h=row['H']+hv@v;hd=row['Hdot']+hv@dt
        a=analytic_intrinsic_n0_jet(A,h,hd,row['weights'],lambda_H=row['lambda_H'],nu_squared_action=row['nu_squared_action'])
        value+=scale*a['value'];maps=[(j,np.r_[p*hv,p*W,d*hv])for j,p,d in blocks]
        for j,J in maps:
            sj=slice((j-1)*84,j*84);gradient[sj]+=scale*J.T@a['gradient']
            for k,K in maps:hessian[sj,slice((k-1)*84,k*84)]+=scale*J.T@a['hessian']@K
    return dict(value=value,gradient=gradient,hessian=hessian,field_displacement=x,
        original_At_Gauss_and_all_four_radial_profiles_retained=True,
        fixed_geometry_background_subtraction_not_applied_inside_action=True,
        finite_field_action_not_full_quantum_stationarity=True)


def nonlinear_source_directed_newton(classical,native_gradient,initial,frame_rows,*,native_hessian=None,
                                    tolerance=1e-10,max_iterations=12,max_halvings=18):
    """Solve the background-subtracted same-domain field equation.

    A native gradient callback must re-evaluate its corrected K/M on each
    candidate.  Supplying a frozen gradient is an explicitly different
    numerical equation; the callback owner is retained by the producer.
    """
    x=np.asarray(initial,complex).copy();C=np.asarray(frame_rows,complex);base=classical(np.zeros_like(x))
    if C.ndim!=2 or C.shape[1]!=len(x)or not np.isfinite(C).all():raise ValueError('named same-domain frame rows required')
    records=[];reaction=np.zeros(len(C),complex)
    def evaluate(z):
        a=classical(z);g=np.asarray(native_gradient(z),complex)
        if g.shape!=z.shape or not np.isfinite(g).all():raise ValueError('actual same-domain native gradient callback required')
        r=a['gradient']-base['gradient']+g
        return a,g,r
    for it in range(max_iterations+1):
        a,g,r=evaluate(x);res=np.r_[r+C.T@reaction,C@x];merit=float(np.linalg.norm(res))
        records.append(dict(iteration=it,residual_norm=merit,native_gradient_norm=float(np.linalg.norm(g)),field_norm=float(np.linalg.norm(x))))
        if merit<=tolerance:return dict(status='REPRESENTED_NONLINEAR_FIELD_TOLERANCE',coefficients=x,frame_reaction=reaction,records=records,residual=res)
        if it==max_iterations:break
        H=a['hessian']+(np.asarray(native_hessian(x),complex)if native_hessian is not None else 0)
        K=np.block([[H,C.T],[C,np.zeros((len(C),len(C)),complex)]])
        step=solve(K,-res,assume_a='gen');accepted=False
        for half in range(max_halvings+1):
            alpha=2.**(-half);trial=x+alpha*step[:len(x)];rho=reaction+alpha*step[len(x):]
            _,_,rr=evaluate(trial);m=float(np.linalg.norm(np.r_[rr+C.T@rho,C@trial]))
            if m<merit:
                records[-1].update(step_fraction=alpha,accepted_residual_norm=m);x,reaction=trial,rho;accepted=True;break
        if not accepted:return dict(status='NONLINEAR_FIELD_LINE_SEARCH_NO_DECREASE',coefficients=x,frame_reaction=reaction,records=records,residual=res)
    return dict(status='NONLINEAR_FIELD_ITERATION_LIMIT',coefficients=x,frame_reaction=reaction,records=records,residual=res)
