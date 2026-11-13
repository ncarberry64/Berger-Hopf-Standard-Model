"""Targeted same-action kinetic crossing diagnostics.

Diagnostic directions are never a proposed gauge quotient. Higher precision
and spatial refinement test actual retained scalar pairings; the outward
Schur certificate applies only to exact stored constitutive matrices.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import json
import math
import numpy as np
import mpmath as mp
from bhsm.interface.muon_parent_mean_causal_action import mean_action_family
from bhsm.interface.muon_parent_gauge_geometry_correction import finite_common_iterate_at_time,compact_temporal_basis
from bhsm.interface.muon_parent_retarded_hypercharge import WALL,regular_radial_basis
from bhsm.interface.muon_parent_maxwell_full_weak import FIELD_ORDER,M
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0,HOPF_ORBIT_VOLUME
from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import standard_model_casimir_coefficient
from bhsm.interface.muon_birth_candidate_geometry_action import ROOT

SOURCE='artifacts/muon_mean_legendre_certificate_20261010/run_2'
PI=mp.mpf(float(np.pi))
VOLUME=float(2*np.pi**2);MAX_SCALE=float(1/(8*VOLUME**2));SCALAR_SCALE=float(VOLUME/VOLUME**2)
GEN=np.array(higgs_u2_real_representation()['real_generators'],float)


def retained_kinetic_data(repository=ROOT):
    root=Path(repository);directory=root/SOURCE;raw=(directory/'result.json').read_bytes();receipt=json.loads(raw)
    for filename,key in (('application.npz','application_sha256'),('action_samples.npz','action_samples_sha256')):
        if sha256((directory/filename).read_bytes()).hexdigest()!=receipt[key]:
            raise ValueError('retained kinetic sample archive hash mismatch')
    for filename,digest in receipt['input_hashes'].items():
        if sha256((root/filename).read_bytes()).hexdigest()!=digest:
            raise ValueError('retained action input changed: '+filename)
    with np.load(directory/'application.npz',allow_pickle=False) as f:stored={k:f[k].copy() for k in f.files}
    with np.load(directory/'action_samples.npz',allow_pickle=False) as f:
        Q=f['full_to_restricted_lift'].copy();samples={k:f[k].copy() for k in f.files}
    family=mean_action_family(root)
    if family['surface_gamma'] is not None:
        raise ValueError('this diagnostic preserves the unassigned area coefficient')
    return dict(family=family,stored=stored,Q=Q,P=family['coordinates']['lift'],receipt=receipt,samples=samples,
        source_receipt_sha256=sha256(raw).hexdigest())


def fixed_wall_velocity_basis_identity(order=12):
    """Exact W_j=(1-z)T_j/2 inclusion and ADM congruence, no gauge deletion."""
    import sympy as S
    if type(order) is not int or order<1:raise ValueError('positive exact Galerkin order required')
    B=S.zeros(order+1,order)
    for j in range(order):
        B[j,j]+=S.Rational(1,2);B[j+1,j]-=S.Rational(1,4);B[abs(j-1),j]-=S.Rational(1,4)
    hessian=S.Matrix([[-42,-6,0],[-6,0,0],[0,0,6]])
    return dict(W_into_U=B,rank=B.rank(),endpoint_left_null=S.ones(1,order+1)*B,
        velocity_hessian_h_w_b=hessian,pointwise_determinant=hessian.det(),
        geometric_velocity_signature=dict(positive=2*order,negative=order+1,zero=0),
        Schur_W_coefficient=S.Rational(6,7),
        equation='L_ADM=(volume/2N)*(-42*h^2-12*h*w+6*b^2); G>0, rank(G B)=rank(B)',
        metric_map='logA/logB determine scale+u and v; logC then determines w',
        exact_coordinate_redundancy=False,physical_gauge_quotient_proved=False,
        scope='fixed-wall metric velocity Gram before added sectors and algebraic constraints')

def dot(a,b):return sum((x*y for x,y in zip(a,b)),mp.mpf(0))
def norm(a):return dot(a,a)
def bracket(a,b):return [(a[1]*b[2]-a[2]*b[1])/mp.sqrt(2),(a[2]*b[0]-a[0]*b[2])/mp.sqrt(2),(a[0]*b[1]-a[1]*b[0])/mp.sqrt(2),mp.mpf(0)]
def add(a,b):return [x+y for x,y in zip(a,b)]
def sub(a,b):return [x-y for x,y in zip(a,b)]
def scale(a,b):return [a*x for x in b]

def fields(q,v,m,chi):
    ck=[mp.cos(4*j*chi) for j in range(1,13)];cj=[mp.cos(4*j*chi) for j in range(12)]
    sk=[mp.sin(4*j*chi) for j in range(1,13)];sj=[mp.sin(4*j*chi) for j in range(12)]
    window=mp.sin(2*chi)**2;wp=2*mp.sin(4*chi)
    u=dot(q[1:13],ck);w=window*dot(q[13:25],cj);b=window*dot(q[25:37],cj)
    up=dot(q[1:13],[-4*j*x for j,x in enumerate(sk,1)])
    wpc=[wp*x-4*j*window*y for j,(x,y) in enumerate(zip(cj,sj))]
    bp=dot(q[25:37],wpc);cp=up+dot(q[13:25],wpc)
    ap=up+bp-mp.tan(chi);bp=up-bp+1/mp.tan(chi)
    radius=mp.mpf(RADIUS0)*mp.exp(q[0]);C=radius*mp.exp(u+w)
    A=radius*mp.exp(u+b)*mp.cos(chi);B=radius*mp.exp(u-b)*mp.sin(chi)
    N=mp.exp(dot(m[:12],ck));np_=dot(m[:12],[-4*j*x for j,x in enumerate(sk,1)])
    beta=mp.sin(4*chi)*dot(m[12:],cj)
    betap=4*mp.cos(4*chi)*dot(m[12:],cj)+mp.sin(4*chi)*dot(m[12:],[-4*j*x for j,x in enumerate(sj)])
    h=v[0]+dot(v[1:13],ck);wd=window*dot(v[13:25],cj);bd=window*dot(v[25:37],cj)
    return dict(C=C,A=A,B=B,N=N,cp=cp,ap=ap,bp=bp,np=np_,beta=beta,betap=betap,lc=h+wd,la=h+bd,lb=h-bd)

def profile(chi,s,k):
    a=21*mp.sin(2*chi)+5*mp.sin(6*chi)
    sigma0=-mp.mpf('.5')+2*chi/PI-mp.sin(4*chi)/(2*PI)
    sigma1=k*(52*mp.sin(2*chi)-14*mp.sin(6*chi)-2*mp.sin(10*chi))/PI
    sigma2=k*k*(982*mp.sin(4*chi)-256*mp.sin(8*chi)-140*mp.sin(12*chi)-mp.mpf('12.5')*mp.sin(16*chi))/PI
    return chi+s*k*a,sigma0+s*sigma1+s*s*sigma2/2,a

def _action_context(data,index,points):
    F=data["family"];REP=F["representation"];STORED=data["stored"]
    u=STORED['times'][index];t=u-F['length'];data=finite_common_iterate_at_time(t,F['coefficients'],REP,F['reference'])
    wall=finite_common_iterate_at_time(t,F['coefficients'],REP,F['reference'],rho=np.array([WALL]))
    b,bt=compact_temporal_basis(np.array([t]),REP['length']);sc=F['coefficients'][REP['scalar_start']:]
    z,w=np.polynomial.legendre.leggauss(points);rho=(z+1)*WALL/2;rw=w*WALL/2
    radial=finite_common_iterate_at_time(t,F['coefficients'],REP,F['reference'],rho=rho)
    gb=np.zeros((points,60,5,4));gr=gb.copy();rb,rr=regular_radial_basis(rho,REP['radial_order'])
    for j,label in enumerate(REP['gauge_labels']):
        gb[:,j,FIELD_ORDER.index(label['field']),label['internal']]=rb[:,label['radial']]
        gr[:,j,FIELD_ORDER.index(label['field']),label['internal']]=rr[:,label['radial']]
    wallb,_=regular_radial_basis(np.array([WALL]),REP['radial_order']);wallmap=np.zeros((60,5,4))
    for j,label in enumerate(REP['gauge_labels']):wallmap[j,FIELD_ORDER.index(label['field']),label['internal']]=wallb[0,label['radial']]
    return dict(data=data,H=b[0]*sc[:4]+sc[4:],Ht=bt[0]*sc[:4],fields=radial['fields'],wallgauge=wall['fields']['gauge'][0,0],
        z=z,w=w,rho=rho,rw=rw,gb=gb,gr=gr,wallmap=wallmap,family=F,representation=REP)

def _action_parts(epsilon,direction,ctx):
    REP=ctx["representation"]
    data=ctx['data'];q=[mp.mpf(x) for x in data['q']]
    v=[mp.mpf(x)+epsilon*mp.mpf(y) for x,y in zip(data['qdot'],direction[37:74])]
    m=[mp.mpf(x)+epsilon*mp.mpf(y) for x,y in zip(data['m'],direction[74:98])]
    s=mp.mpf(data['normal']);sr=mp.mpf(data['normal_rate'])+epsilon*mp.mpf(direction[99])
    Cstar=mp.mpf(RADIUS0)*mp.exp(q[0]+dot(q[1:13],[(-1)**j for j in range(1,13)])+dot(q[13:25],[(-1)**j for j in range(12)]))
    k=-1/(16*Cstar);kdot=-k*(v[0]+dot(v[1:13],[(-1)**j for j in range(1,13)])+dot(v[13:25],[(-1)**j for j in range(12)]))
    wall=PI/4-16*k*s;wallrate=-16*(k*sr+kdot*s)
    bulk=mp.mpf(0);inertia=mp.mpf(0)
    for yy,ww in zip((ctx['z']+1)/2,ctx['w']/2):
        chi=wall*mp.mpf(yy);f=fields(q,v,m,chi);eta,sigma,a=profile(chi,s,k)
        fp=1+s*k*(42*mp.cos(2*chi)+30*mp.cos(6*chi));fdot=(sr*k+s*kdot)*a
        C,A,B,N=(f[z] for z in ('C','A','B','N'))
        Hc=(f['lc']-f['beta']*f['cp']-f['betap'])/N
        Ha=(f['la']-f['beta']*f['ap'])/N;Hb=(f['lb']-f['beta']*f['bp'])/N
        adm=Hc*Hc+3*Ha*Ha+3*Hb*Hb-(Hc+3*Ha+3*Hb)**2
        fn=(fdot-f['beta']*fp)/N
        X=fp**2/C**2+3*mp.cos(eta)**2/A**2+3*mp.sin(eta)**2/B**2-fn**2
        loc=1-4*sigma*sigma;volume=C*A**3*B**3;spatial=A**3*B**3
        grav=3*spatial/C*N*(f['np']*(f['ap']+f['bp'])+f['ap']**2+f['bp']**2+3*f['ap']*f['bp'])
        alg=N*volume*(3/A**2+3/B**2-mp.mpf(.5)*mp.mpf(15*5**(1/3)/4)-loc*(X/2+X**4/8)+adm/2)
        bulk+=mp.mpf(ww)*wall*(grav+alg);inertia+=mp.mpf(ww)*wall*volume*loc*(1+X**3)/N
    FR=-mp.mpf('.25')/(2*mp.mpf(HOPF_ORBIT_VOLUME)**2*inertia)
    fw=fields(q,v,m,wall);A,B,N=(fw[z] for z in ('A','B','N'))
    R4=A*B/mp.sqrt(A*A+B*B);casimir=-mp.mpf(standard_model_casimir_coefficient())/R4*N
    U=fw['C']*(wallrate+fw['beta'])/N;rho=A**3*B**3
    rhorate=3*rho*(fw['la']+fw['lb']+(fw['ap']+fw['bp'])*wallrate)
    GHY=-mp.atanh(U)*rhorate;maxwell=mp.mpf(0)
    for i,(rr,ww) in enumerate(zip(ctx['rho'],ctx['rw'])):
        chi=mp.mpf(rr)/mp.mpf(WALL)*wall;f=fields(q,v,m,chi)
        LF=mp.sqrt(f['A']**2+f['B']**2);r=f['A']*f['B']/LF;Crho=f['C']/2
        _,sigma,_=profile(chi,s,k);jac=2*wall/mp.mpf(WALL)
        common=mp.mpf(float(2*np.pi**4))*LF**5*(1-4*sigma*sigma)
        e=jac*common*Crho*r/f['N'];rad=common*f['N']*r/(Crho*jac)
        d=jac*common*f['N']*Crho/r;ktr=common*r**3/(f['N']*Crho*jac)
        adv=2*mp.mpf(rr)/mp.mpf(WALL)*wallrate;beta=(2*f['beta']+adv)/jac
        lam=f['A']**2/LF**2;lr=lam*(1-lam)*(f['ap']-f['bp']);lt=2*lam*(1-lam)*(f['la']-f['lb'])+adv*lr;lr*=jac
        av=ctx['fields']['gauge'][i,0];at=ctx['fields']['gauge_tau'][i,0];ar=ctx['fields']['gauge_rho'][i,0]
        gv=np.einsum('jfc,j->fc',ctx['gb'][i],direction[100:160]);gt=np.einsum('jfc,j->fc',ctx['gb'][i],direction[160:220]);gr=np.einsum('jfc,j->fc',ctx['gr'][i],direction[100:160])
        aa=[[mp.mpf(av[j,c])+epsilon*mp.mpf(gv[j,c]) for c in range(4)] for j in range(5)]
        tt=[[mp.mpf(at[j,c])+epsilon*mp.mpf(gt[j,c]) for c in range(4)] for j in range(5)]
        rrr=[[mp.mpf(ar[j,c])+epsilon*mp.mpf(gr[j,c]) for c in range(4)] for j in range(5)]
        for j in range(3):
            for c in range(4):aa[j+2][c]+=(lam-1)*mp.mpf(M[j,c]);tt[j+2][c]+=lt*mp.mpf(M[j,c]);rrr[j+2][c]+=lr*mp.mpf(M[j,c])
        X=add(sub(tt[1],rrr[0]),bracket(aa[0],aa[1]))
        Ft=[add(tt[j+2],bracket(aa[0],aa[j+2])) for j in range(3)]
        Fr=[add(rrr[j+2],bracket(aa[1],aa[j+2])) for j in range(3)]
        BB=[add(scale(2,aa[j+2]),bracket(aa[k+2],aa[l+2])) for j,k,l in ((0,1,2),(1,2,0),(2,0,1))]
        full=(ktr*norm(X)+e*sum(norm(sub(T,scale(beta,R))) for T,R in zip(Ft,Fr))-rad*sum(norm(R) for R in Fr)-d*sum(norm(Bv) for Bv in BB))/2
        # Same geometry reference, including derivatives, is subtracted.
        BGt=[scale(lt,row) for row in M];BGr=[scale(lr,row) for row in M];BGb=[scale(2*lam*(lam-1),row) for row in M]
        bg=(e*sum(norm(sub(T,scale(beta,R))) for T,R in zip(BGt,BGr))-rad*sum(norm(R) for R in BGr)-d*sum(norm(Bv) for Bv in BGb))/2
        maxwell+=mp.mpf(ww)*(full-bg)
    H=[mp.mpf(x) for x in ctx['H']];Ht=[mp.mpf(x)+epsilon*mp.mpf(y) for x,y in zip(ctx['Ht'],direction[224:228])]
    dwall=np.einsum('jfc,j->fc',ctx['wallmap'],direction[100:160])
    gauge=[[mp.mpf(ctx['wallgauge'][j,c])+epsilon*mp.mpf(dwall[j,c]) for c in range(4)] for j in range(5)]
    lam=A*A/(A*A+B*B)
    for j in range(3):
        for c in range(4):gauge[j+2][c]+=(lam-1)*mp.mpf(M[j,c])
    DH=[]
    for j in (0,2,3,4):DH.append([sum(gauge[j][c]*mp.mpf(GEN[c,i,k])*H[k] for c in range(4) for k in range(4)) for i in range(4)])
    DH[0]=add(DH[0],Ht);lapse=N*mp.sqrt(1-U*U)
    wt=R4**3/lapse;ws=lapse*R4;wv=lapse*R4**3
    scalar=wt*norm(DH[0])-ws*sum(norm(row) for row in DH[1:])-wv*mp.mpf(REP['scalar_matching']['lambda_H'])*(norm(H)-mp.mpf(ctx['family']['nu_squared_action']))**2
    return dict(bulk=bulk,FR=FR,casimir=casimir,GHY=GHY,Maxwell=mp.mpf(MAX_SCALE)*maxwell,Higgs=mp.mpf(SCALAR_SCALE)*scalar)


def targeted_action_pairing(data,index,eigenvalue_index,*,decimal_digits=70,quadrature_points=48):
    """Apply a diagnostic direction to the literal scalar action, not a solver."""
    if type(decimal_digits) is not int or decimal_digits<50:
        raise ValueError('at least50 decimal digits for the cancellation diagnostic')
    if type(quadrature_points) is not int or quadrature_points<24:
        raise ValueError('explicit spatial quadrature order>=24 required')
    if type(index) is not int or not 0<=index<len(data['stored']['times']):
        raise ValueError('retained time sample required')
    D=data['stored']['restricted_legendre_matrices'][index]
    if type(eigenvalue_index) is not int or not 0<=eigenvalue_index<len(D):
        raise ValueError('retained sorted eigenvector index required for this diagnostic')
    scale_=1/np.sqrt(np.max(abs(D),axis=1));e,V=np.linalg.eigh(scale_[:,None]*D*scale_)
    z=scale_*V[:,eigenvalue_index];direction=data['P']@data['Q'][:,74:]@z
    names=('bulk','FR','casimir','GHY','Maxwell','Higgs')
    with mp.workdps(decimal_digits):
        context=_action_context(data,index,quadrature_points)
        def literal(epsilon):
            values=_action_parts(epsilon,direction,context)
            return mp.matrix([values[name] for name in names])
        values=mp.diff(literal,mp.mpf(0),2);total=sum(values)
        result=dict(total=mp.nstr(total,45),parts={k:mp.nstr(v,45) for k,v in zip(names,values)})
    result.update(index=index,time=float(data['stored']['times'][index]),eigenvalue_index=eigenvalue_index,
        decimal_digits=decimal_digits,quadrature_points=quadrature_points,
        stored_pairing=float(z@D@z),stored_balanced_eigenvalue=float(e[eigenvalue_index]),
        direction_full_raw=direction.tolist(),direction_selected_for_diagnostic_only=True,
        direction_removed_or_quotiented=False,conditional_nu_squared_action=data['family']['nu_squared_action'],
        surface_gamma=None,physical_primal_or_continuum_enclosure=False)
    return result


def _arb_frobenius_upper(matrix):
    """Upper norm uses absolute upper endpoints even for zero-centred balls."""
    from flint import arb
    return sum((matrix[i,j].abs_upper()**2 for i in range(matrix.nrows())
                for j in range(matrix.ncols())),arb(0)).sqrt()


def certify_constraint_schur(matrix,*,velocity_count=74,precision_bits=192):
    """Outward exact-stored A/K inertia; all velocities remain represented."""
    from flint import arb,arb_mat,ctx
    if not np.isrealobj(matrix):raise ValueError('explicit real stored Hessian required')
    D=np.asarray(matrix,float)
    if (D.ndim!=2 or D.shape[0]!=D.shape[1] or not np.isfinite(D).all()
            or not np.array_equal(D,D.T)):
        raise ValueError('finite exactly symmetric stored Hessian required')
    if type(velocity_count) is not int or not 0<velocity_count<len(D):
        raise ValueError('both velocity and algebraic action blocks required')
    if type(precision_bits) is not int or precision_bits<96:
        raise ValueError('at least96 bits outward arithmetic required')
    M,N,A=D[:velocity_count,:velocity_count],D[:velocity_count,velocity_count:],D[velocity_count:,velocity_count:]
    def balls(a):return arb_mat([[arb(float(v)) for v in r] for r in a])
    def upper(a):return float(np.nextafter(float(a.upper()),np.inf))
    def sign_certificate(matrix,reference):
        rows=np.max(abs(reference),axis=1)
        if np.any(rows==0):raise ArithmeticError('zero constitutive row; no regularizer applied')
        scale_=1/np.sqrt(rows);balanced=scale_[:,None]*reference*scale_
        e,V=np.linalg.eigh((balanced+balanced.T)/2);VV=balls(V);SS=balls(np.diag(scale_))
        gram=_arb_frobenius_upper(VV.transpose()*VV-balls(np.eye(len(e))))
        defect=_arb_frobenius_upper(VV.transpose()*SS*matrix*SS*VV-balls(np.diag(e)))
        gap=arb(float(min(abs(e))))
        return dict(congruence_inertia_certified=bool(gram<1 and defect<gap),
            congruence_error_upper=upper(defect),Gram_defect_upper=upper(gram),reference_gap=float(min(abs(e))),
            positive=int(sum(e>0)),negative=int(sum(e<0)),balanced_condition=float(max(abs(e))/min(abs(e))),
            smallest_balanced_signed_eigenvalue=float(e[np.argmin(abs(e))]))
    previous=ctx.prec;ctx.prec=precision_bits
    try:
        MM,NN,AA=map(balls,(M,N,A))
        try:
            AI=AA.inv();reference_K=M-N@np.linalg.solve(A,N.T)
        except (ZeroDivisionError,np.linalg.LinAlgError) as error:
            raise ArithmeticError('algebraic action block not invertible; no pseudoinverse') from error
        KK=MM-NN*AI*NN.transpose()
        result=dict(A_inverse_residual_upper=upper(_arb_frobenius_upper(AA*AI-balls(np.eye(len(A))))),
            A=sign_certificate(AA,A),K=sign_certificate(KK,reference_K),precision_bits=precision_bits,
            retained_velocity_count=velocity_count,algebraic_count=len(A),small_modes_removed=False,
            equation='A=Lyy; K=Lvv−Lvy*A^-1*Lyv; inertia(D)=inertia(A)+inertia(K)',
            physical_gauge_quotient_selected=False,producer_rounding_or_continuum_enclosed=False)
    finally:ctx.prec=previous
    return result


def spline_crossing_compatibility(data,*,bracket_indices=(10,11),eigenvalue_index=24):
    """Numerical necessary compatibility row at one retained spline crossing.

    l^T D=0 requires l^T(R*[x,p]−[Jv,Jy])=0.  The phase is not supplied
    here, so a nonzero source row is not a failed compatibility verdict.
    """
    from scipy.interpolate import CubicSpline
    from scipy.optimize import brentq
    times=data['stored']['times'];Q=data['Q'];n=74
    if (len(bracket_indices)!=2 or any(type(i) is not int or not 0<=i<len(times) for i in bracket_indices)
            or bracket_indices[0]>=bracket_indices[1]):
        raise ValueError('ordered retained crossing bracket indices required')
    h=np.einsum('ia,tij,jb->tab',Q,data['samples']['master_hessians'],Q)
    h=(h+h.transpose(0,2,1))/2
    j=np.einsum('ia,tiAB->taAB',Q,data['samples']['master_source_cotangents'])
    HS=CubicSpline(times,h);JS=CubicSpline(times,j)
    if type(eigenvalue_index) is not int or not 0<=eigenvalue_index<h.shape[1]-n:
        raise ValueError('retained sorted constitutive eigenvalue index required')
    def eigenvalue(t):
        D=HS(t)[n:,n:];s=1/np.sqrt(np.max(abs(D),axis=1))
        return np.linalg.eigvalsh(s[:,None]*D*s)[eigenvalue_index]
    lo,hi=times[list(bracket_indices)]
    if eigenvalue(lo)*eigenvalue(hi)>=0:raise ValueError('the retained bracket must have opposite signs')
    root=brentq(eigenvalue,lo,hi,xtol=2e-13,rtol=1e-12)
    H=HS(root);D=H[n:,n:];s=1/np.sqrt(np.max(abs(D),axis=1));e,V=np.linalg.eigh(s[:,None]*D*s)
    l=s*V[:,eigenvalue_index];l/=np.linalg.norm(l)
    R=np.vstack((np.column_stack((-H[n:2*n,:n],np.eye(n))),
        np.column_stack((-H[2*n:,:n],np.zeros((H.shape[0]-2*n,n))))))
    source=JS(root)[n:].reshape(len(D),64)
    return dict(bracket_indices=list(bracket_indices),bracket_times=[float(lo),float(hi)],
        bracket_balanced_eigenvalues=[float(eigenvalue(lo)),float(eigenvalue(hi))],
        numerical_root_time=float(root),balanced_eigenvalue_at_root=float(e[eigenvalue_index]),
        constitutive_null_covector=l.tolist(),null_covector_normalization='Euclidean norm1 in retained v74/y32 numerical units',
        null_residual_norm=float(np.linalg.norm(D@l)),
        null_residual_relative=float(np.linalg.norm(D@l)/np.linalg.norm(D,2)),
        simple_crossing_slope_pairing=float(l@HS(root,1)[n:,n:]@l),
        phase_row=(l@R).tolist(),source_row=(-l@source).reshape(8,8).tolist(),
        phase_order='x74,p74; Hreal x70:74',
        source_order='raw betaPhoton A,B0..7, no half factor',
        compatibility_equation='phase_row*[x,p]+source_row=0 is necessary for bounded [v,y] at a simple crossing',
        source_row_alone_is_not_a_failure_verdict=True,phase_or_compatibility_evaluated=False,
        floating_spline_root_not_an_outward_root_enclosure=True,
        physical_background_or_domain_selected=False)


def materialize(output,*,repository=ROOT):
    """Replay the reached finite-action cancellation and exact stored Schur."""
    root=Path(repository);out=Path(output)
    if not out.is_absolute():out=root/out
    if out.exists():raise FileExistsError('preserve earlier diagnostic; choose a new output')
    data=retained_kinetic_data(root)
    refs=dict(data['receipt']['input_hashes'])
    for name in ('src/bhsm/interface/muon_mean_kinetic_crossing_diagnostic.py',
        'src/bhsm/interface/aether_post_cut_nonround_lorentzian_cap_v15_48.py',
        'src/bhsm/interface/aether_m4_standard_model_zeta_backreaction_v15_51.py'):
        refs[name]=sha256((root/name).read_bytes()).hexdigest()
    for filename in ('result.json','application.npz','action_samples.npz'):
        name=SOURCE+'/'+filename;refs[name]=sha256((root/name).read_bytes()).hexdigest()
    pairings=[]
    for index,j in ((0,25),(0,26),(1,24),(2,27),(10,24),(11,24),(16,25),(16,26)):
        applications=[targeted_action_pairing(data,index,j,decimal_digits=precision,quadrature_points=points)
            for precision,points in ((70,48),(90,48),(70,96),(70,192))]
        pairings.append(dict(index=index,eigenvalue_index=j,applications=applications,
            precision70_90_agree_at45_reported_digits=applications[0]['total']==applications[1]['total'],
            refinement48_192_absolute_difference=abs(float(applications[0]['total'])-float(applications[3]['total'])),
            refinement96_192_absolute_difference=abs(float(applications[2]['total'])-float(applications[3]['total']))))
    schur=[dict(index=i,time=float(data['stored']['times'][i]),
        **certify_constraint_schur(data['stored']['restricted_legendre_matrices'][i])) for i in (0,1,2,10,11,16)]
    identity=fixed_wall_velocity_basis_identity()
    identity={k:([[str(v) for v in row] for row in value.tolist()] if hasattr(value,'tolist') else
        str(value) if hasattr(value,'is_number') else value) for k,value in identity.items()}
    for name,digest in refs.items():
        if sha256((root/name).read_bytes()).hexdigest()!=digest:
            raise RuntimeError('diagnostic input changed during replay: '+name)
    compatibility=spline_crossing_compatibility(data)
    result=dict(scope='EVALUATED_TARGETED_SAME_ACTION_KINETIC_CROSSING_DIAGNOSTIC',
        input_hashes=refs,source_receipt_sha256=data['source_receipt_sha256'],
        exact_basis_identity=identity,targeted_pairings=pairings,constraint_Schur=schur,
        numerical_crossing_compatibility=compatibility,
        background_scope=data['family']['scope'],conditional_nu_squared_action=data['family']['nu_squared_action'],surface_gamma=None,
        constants_scope='retained binary64 action constants/nodes interpreted exactly with high-precision elementary functions',
        diagnostic_directions_not_a_reduction=True,causal_mean_response_solved=False,
        physical_gauge_quotient_or_primal_selected=False,complete_native_or_Pauli_evaluated=False,
        error_scope='Arb encloses exact stored algebraic Schur only; high-precision scalar pairings and spatial refinement are diagnostics, not producer-rounding or continuum enclosures')
    out.mkdir(parents=True)
    (out/'diagnostic.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result

