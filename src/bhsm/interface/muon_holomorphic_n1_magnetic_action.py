"""Signed original n1 field action and its prescribed magnetic wall trace.

The complete gauge trace is prescribed, while the Higgs has its original
natural action rows. Continued coefficients use analytic transpose. No
positive reference inverse, old first field, or physical exterior is used.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import solve,expm,expm_frechet
from .muon_holomorphic_current_source import holomorphic_current_stage, _wall_coframe
from .muon_holomorphic_normal_geometry import holomorphic_geometry_rows
from .muon_holomorphic_em_current import holomorphic_unit_em_moments
from .muon_chronological_harmonic_field_action import analytic_homogeneous_original_field_forms
from .muon_nonlinear_chronological_n0_action import chronological_n0_field_lifts
from .muon_parent_maxwell_full_weak import M
from .muon_electromagnetic_soft_magnetic_source import local_magnetic_wavefunctions
from .muon_intrinsic_scalar_discretization import scalar_s3_discretization
from .muon_electromagnetic_soft_magnetic_source import magnetic_turn_on_profile


def original_field_permutation(representation):
    labels=representation['gauge_labels']
    if len(labels)!=80:raise ValueError('all original four radial gauge profiles required')
    at=[j for j,l in enumerate(labels)if l['field']=='A_tau']
    if len(at)!=16:raise ValueError('all sixteen material At/Gauss coordinates required')
    return np.array(at+[j for j in range(80)if j not in at]+list(range(80,84)))


def original_signed_stage(raw,raw_first,parent_raw,parent_first,reference_pair,
        reference_first,representation,*,side,lambda_H,nu_squared_action):
    """Rebuild A/At/Ar, density and wall jets on the actual supplied stage."""
    x,dx=np.asarray(raw,complex),np.asarray(raw_first,complex)
    stage=holomorphic_current_stage(x,dx,parent_raw,parent_first,reference_pair,
        reference_first,representation,side=side)
    k=dx.shape[1];nr=len(representation['rho'])
    gb=np.asarray(representation['gauge_basis'])[:,:,0].reshape(nr,80,5,4)
    gr=np.asarray(representation['gauge_radial_basis'])[:,:,0].reshape(nr,80,5,4)
    A=np.einsum('rjfc,j->rfc',gb,x[100:180])
    At=np.einsum('rjfc,j->rfc',gb,x[180:260])
    Ar=np.einsum('rjfc,j->rfc',gr,x[100:180])
    dA=np.einsum('rjfc,jk->krfc',gb,dx[100:180])
    dAt=np.einsum('rjfc,jk->krfc',gb,dx[180:260])
    dAr=np.einsum('rjfc,jk->krfc',gr,dx[100:180])
    for a,da,j,offset in ((A,dA,0,1),(At,dAt,1,0),(Ar,dAr,2,0)):
        a[:,2:]+=M[None]*(stage['total_profile'][:nr,j,None,None]-offset)
        da[:,:,2:]+=M[None,None]*stage['total_profile_first'][:,:nr,j,None,None]
    geometry=holomorphic_geometry_rows(x[:100],representation['rho'])
    names=('electric','radial','angular','electric_radial','shift')
    densities=np.array([[r[n].value for n in names]for r in geometry['rows']])
    ddensities=np.array([[r[n].gradient@dx[:100]for n in names]for r in geometry['rows']]).transpose(2,0,1)
    R,N,_=_wall_coframe(x);weights=(R**3/N,N*R,N*R**3)
    row=dict(A=A,At=At,Ar=Ar,densities=densities,wall_A=stage['full_wall_connection'],
        H=x[260:264],Hdot=x[264:268],weights=np.array([q.value for q in weights]),
        lambda_H=float(lambda_H),nu_squared_action=float(nu_squared_action))
    first=dict(A=dA,At=dAt,Ar=dAr,densities=ddensities,wall_A=stage['full_wall_connection_first'],
        H=dx[260:264].T,Hdot=dx[264:268].T,
        weights=np.array([q.gradient@dx[:100]for q in weights]).T)
    ids=original_field_permutation(representation);lifts=chronological_n0_field_lifts(representation,ids)
    return dict(row=row,row_first=first,stage=stage,lifts=lifts,value_permutation=ids,
        parent_reference_composed_before_wall=True,mechanical_profile_count=1)


def magnetic_angular_trace():
    """Owned exact quaternion n1 wave, including the longitudinal image."""
    a=scalar_s3_discretization(3);labels=a['real_basis_labels']
    odd=np.flatnonzero([l[0]in(1,3)for l in labels]);one=np.flatnonzero([l[0]==1 for l in labels])
    source=local_magnetic_wavefunctions(dict(harmonic_labels=[labels[j]for j in odd]))
    return dict(wave=source['wavefunctions'][:,:4,:3],
        derivative_matrices=a['real_angular_derivative_matrices'][:,one][:,:,one],
        harmonic_labels=np.array([labels[j]for j in one]),
        reconstruction_max=source['angular_reconstruction_maximum'])


def _charge_coefficient_rate_first(h,hd,dh,dhd):
    matrices=np.zeros((3,4,4))
    matrices[0,0,1]=matrices[0,1,0]=matrices[0,2,3]=matrices[0,3,2]=1
    matrices[1,0,3]=matrices[1,3,0]=1;matrices[1,2,1]=matrices[1,1,2]=-1
    matrices[2]=np.diag([1,-1,1,-1])
    q=h@h;qt=2*h@hd;dq=2*h@dh;dqt=2*(hd@dh+h@dhd)
    n=np.einsum('i,aij,j->a',h,matrices,h);nt=2*np.einsum('i,aij,j->a',hd,matrices,h)
    dn=2*np.einsum('i,aij,jk->ak',h,matrices,dh)
    dnt=2*(np.einsum('ik,aij,j->ak',dhd,matrices,h)+np.einsum('i,aij,jk->ak',hd,matrices,dh))
    rate=np.r_[-np.sqrt(2)*(nt/q-n*qt/q**2),0j]
    first=np.zeros((dh.shape[1],4),complex)
    first[:,:3]=(-np.sqrt(2)*(dnt/q-nt[:,None]*dq/q**2-dn*qt/q**2
        -n[:,None]*dqt/q**2+2*n[:,None]*qt*dq/q**3)).T
    return rate,first


def holomorphic_local_B_trace(raw,raw_first,stage,*,electric_charge,angular=None):
    """Apply e R4²/2 once, with actual coordinate-time and source derivatives."""
    x,dx=np.asarray(raw,complex),np.asarray(raw_first,complex);e=float(electric_charge)
    if x.shape!=(268,)or dx.ndim!=2 or dx.shape[0]!=268 or e<=0 or not np.isfinite(e):
        raise ValueError('original stage and positive independently calibrated electric charge required')
    angular=magnetic_angular_trace()if angular is None else angular
    R,N,_=_wall_coframe(x);k=dx.shape[1]
    coordinate=np.zeros(100,complex);coordinate[:37]=x[37:74];coordinate[98]=x[99]
    dcoordinate=np.zeros((100,k),complex);dcoordinate[:37]=dx[37:74];dcoordinate[98]=dx[99]
    Rt=R.gradient@coordinate;dR=R.gradient@dx[:100]
    dRt=coordinate@R.hessian@dx[:100]+R.gradient@dcoordinate
    factor=e*R.value**2/2;factor_time=e*R.value*Rt
    df=e*R.value*dR;dft=e*(dR*Rt+R.value*dRt)
    moments=holomorphic_unit_em_moments(x[260:264],dx[260:264],N.value,stage['induced_lapse_first'])
    s,ds=moments['unit_Tr16_coefficients'],moments['unit_Tr16_coefficients_first']
    st,dst=_charge_coefficient_rate_first(x[260:264],x[264:268],dx[260:264],dx[264:268])
    wave=angular['wave'];base=np.einsum('fhb,c->fchb',wave,s)
    base_t=np.einsum('fhb,c->fchb',wave,st)
    dbase=np.einsum('fhb,kc->kfchb',wave,ds);dbase_t=np.einsum('fhb,kc->kfchb',wave,dst)
    Q=factor*base;Qt=factor_time*base+factor*base_t
    dQ=df[:,None,None,None,None]*base+factor*dbase
    dQt=dft[:,None,None,None,None]*base+factor_time*dbase+df[:,None,None,None,None]*base_t+factor*dbase_t
    if np.any(Q[:2])or np.any(Qt[:2]):raise ArithmeticError('the complete prescribed At/Ar trace is zero')
    return dict(Q=Q,Q_coordinate_time=Qt,Q_first=dQ,Q_coordinate_time_first=dQt,
        unit_charge_coefficients=s,unit_charge_coefficient_time=st,
        canonical_magnetic_factor=np.array(factor),canonical_magnetic_factor_time=np.array(factor_time),
        R4_coordinate_time=np.array(Rt),R4_coordinate_time_first=dRt,
        electric_charge=np.array(e),harmonic_labels=angular['harmonic_labels'],
        electric_charge_count=1,physical_thomson_or_LSZ_matching_proved=False,
        source_domain='complete prescribed20 gauge trace, At/Ar target zero; H natural')


def signed_n1_forms(binding,angular=None):
    angular=magnetic_angular_trace()if angular is None else angular
    # The row already contains the supplied raw fields. Add zero here.
    return analytic_homogeneous_original_field_forms(binding['row'],np.zeros(84),np.zeros(84),
        binding['lifts'],angular['derivative_matrices'])


def signed_n1_form_first(binding,angular=None):
    """Extract the exact degree-five row polynomial's linear coefficient.

    Geometry/profile jets have already been differentiated by their
    action owner. M/B/K have degree at most5 in a LINEAR row germ:
    electric e*(T-beta*R)^2 includes the moving beta² contact.
    Six evaluations cancel cubic and quintic coefficients algebraically. This
    is binary polynomial coefficient arithmetic, not a finite physical
    field perturbation or an outward error certificate. Small high/low
    columns are separately scaled before any row addition.
    """
    angular=magnetic_angular_trace()if angular is None else angular
    row,first=binding['row'],binding['row_first'];keys=('M','B_forward','B_reverse','K')
    values={n:[]for n in keys};scales=[]
    for j in range(len(first['H'])):
        rate=max(np.max(abs(first[n][j]))/(1+np.max(abs(row[n])))for n in first)
        h=.05/rate if rate else 1.
        points=[]
        for s in (h,-h,2*h,-2*h,3*h,-3*h):
            moved={n:(a+s*first[n][j]if n in first else a)for n,a in row.items()}
            points.append(analytic_homogeneous_original_field_forms(moved,np.zeros(84),np.zeros(84),
                binding['lifts'],angular['derivative_matrices']))
        for n in keys:values[n].append((45*(points[0][n]-points[1][n])-9*(points[2][n]-points[3][n])
            +(points[4][n]-points[5][n]))/(60*h))
        scales.append(h)
    return dict(**{n:np.array(v)for n,v in values.items()},row_polynomial_coefficient_scales=np.array(scales),
        exact_row_polynomial_degree_upper=5,binary_coefficient_arithmetic_not_outward=True)


def complete_gauge_wall_constraints(lifts,harmonics):
    """Border named rows, removing only the proven duplicate central-Ar wall row."""
    W=np.asarray(lifts['W'],complex);C=np.asarray(lifts['frame_rows'],complex)
    if W.shape!=(20,84)or C.shape!=(4,84):raise ValueError('original complete gauge wall and frame maps required')
    duplicate=7 # A_rho, internal central generator3.
    factors=W[duplicate]@C.T
    if np.max(abs(W[duplicate]-factors@C))>2e-13:raise ValueError('named central-Ar redundancy must be proved, not selected numerically')
    keep=np.array([j for j in range(20)if j!=duplicate])
    allrows=np.kron(W,np.eye(harmonics));frame=np.kron(C,np.eye(harmonics))
    bordered=np.r_[np.kron(W[keep],np.eye(harmonics)),frame]
    return dict(constraint=bordered,all_gauge_wall=allrows,frame=frame,
        kept_wall_indices=keep,duplicate_wall_index=duplicate,duplicate_frame_coefficients=factors)


def prescribed_weak_trace_response(forms,coordinate_steps,wall_targets,initial_field,*,lapse):
    """Solve a supplied initial-held/final-natural signed temporal FE action.

    Initial coefficients and every free-node complete gauge wall target
    are mandatory operands. This interface does not choose a magnetic
    ramp, initial Cauchy momentum, birth reset, or physical exterior.
    Piecewise constant stage coefficients are integrated exactly against
    linear nodal tests. The original algebraic At/Gauss rows remain inside
    the field block; named frame and wall reactions are returned.
    """
    h=np.asarray(coordinate_steps,complex);N=np.asarray(lapse,complex);q=len(forms)
    if h.shape!=(q,)or N.shape!=(q,)or q==0 or np.any(h==0)or np.any(N==0):raise ValueError('same signed finite stage clocks required')
    n=forms[0]['K'].shape[0];nh=n//84
    W=forms[0]['wall_value_map'][:20*nh];F=forms[0]['frame_rows']
    keep=np.array([j for j in range(20)if j!=7]);Ci=np.r_[W.reshape(20,nh,n)[keep].reshape(19*nh,n),F]
    targets=np.asarray(wall_targets,complex);x0=np.asarray(initial_field,complex)
    if targets.ndim!=4 or targets.shape[:3]!=(q,20,nh)or x0.shape!=(n,targets.shape[-1]):raise ValueError('all free gauge traces and explicit full initial field required')
    duplicate=W.reshape(20,nh,n)[7]
    if np.max(abs(duplicate-duplicate@F.T@F))>2e-13:raise ValueError('named central-Ar wall redundancy must be proved')
    if np.any(targets[:,7])or np.max(abs(F@x0))>2e-13:raise ValueError('the central-Ar frame/source redundancy must remain zero')
    count=Ci.shape[0];total=q*(n+count);K=np.zeros((total,total),complex);rhs=np.zeros((total,x0.shape[1]),complex)
    # The holomorphic L_E=-L_L and d_tau=iN*d_t rule cancel to the
    # original signed coordinate action weight -i dt. Keep both B sides.
    quadrature=np.polynomial.legendre.leggauss(2)
    for j,(f,dt)in enumerate(zip(forms,h)):
        for z,w in zip(*quadrature):
            p=np.array([(1-z)/2,(1+z)/2]);v=np.array([-1/dt,1/dt]);scale=-1j*dt*w/2
            for a in range(2):
                nodea=j+a
                if nodea==0:continue
                sa=slice((nodea-1)*(n+count),(nodea-1)*(n+count)+n)
                for b in range(2):
                    block=scale*(p[a]*p[b]*f['K']+p[a]*v[b]*f['B_forward']
                        +v[a]*p[b]*f['B_reverse']+v[a]*v[b]*f['M'])
                    nodeb=j+b
                    if nodeb==0:rhs[sa]-=block@x0
                    else:
                        sb=slice((nodeb-1)*(n+count),(nodeb-1)*(n+count)+n);K[sa,sb]+=block
    for j in range(q):
        off=j*(n+count);s=slice(off,off+n);r=slice(off+n,off+n+count)
        K[s,r]=Ci.T;K[r,s]=Ci
        rhs[r]=np.r_[targets[j,keep].reshape(19*nh,-1),np.zeros((4*nh,x0.shape[1]),complex)]
    # Reversible coordinate congruence; report original rows afterward.
    d=np.ones(total)
    for _ in range(8):
        row=np.max(abs(d[:,None]*K*d[None]),axis=1)
        if np.any(row==0):raise ValueError('an unowned zero action row cannot be deleted')
        d/=np.sqrt(row)
    answer=d[:,None]*solve(d[:,None]*K*d[None],d[:,None]*rhs,assume_a='gen')
    primal=answer.reshape(q,n+count,-1);fields=primal[:,:n];reactions=primal[:,n:]
    rows=K@answer-rhs
    return dict(field_coefficients=fields,initial_field=x0,wall_reactions=reactions[:,:19*nh],
        frame_reactions=reactions[:,19*nh:],full_solution=answer,original_rhs=rhs,
        original_action_rows=rows,all_gauge_wall_rows=np.einsum('ac,qcb->qab',W,fields)-targets.reshape(q,20*nh,-1),
        named_frame_rows=np.einsum('ac,qcb->qab',F,fields),
        bordered_Gauss_balance_rows=rows.reshape(q,n+count,-1)[:,:16*nh],
        unbordered_field_rows=rows.reshape(q,n+count,-1)[:,:n]-np.einsum('ac,qcb->qab',Ci.T,reactions),
        unbordered_Gauss_rows=(rows.reshape(q,n+count,-1)[:,:n]-np.einsum('ac,qcb->qab',Ci.T,reactions))[:,:16*nh],
        signed_original_temporal_action=True,physical_retarded_or_exterior_domain_selected=False)


def original_named_wall_lift(representation,value_permutation):
    """Use the owned wall_lift radial coordinate, not a fitted right inverse."""
    labels=representation['gauge_labels'];ids=np.asarray(value_permutation,int)
    names={'A_tau':0,'A_rho':1,'A_1':2,'A_2':3,'A_3':4};L=np.zeros((84,20))
    found=[]
    for j,l in enumerate(labels):
        if l.get('wall_lift',False):
            slot=4*names[l['field']]+l['internal'];L[int(np.flatnonzero(ids==j)[0]),slot]=1;found.append(slot)
    W=np.asarray(representation['wall_trace_map']).reshape(20,80)@np.eye(84)[:,ids][:80]
    if sorted(found)!=list(range(20))or np.max(abs(W@L-np.eye(20)))>2e-13:
        raise ValueError('twenty named original independent wall-lift coordinates required')
    return L


def known_wall_source_weak_response(forms,forms_first,coordinate_steps,magnetic_sources,
        representation,value_permutation):
    """Apply the owned C2 ramp on the declared finite two-stage control span.

    Full wall Q and its coordinate derivative are lifted before the weak
    action. Unknown gauge traces are zero; H remains natural. Incoming
    negative coordinate steps retain their backward control orientation.
    No physical adiabatic, initial momentum, reset, or exterior is chosen.
    """
    h=np.asarray(coordinate_steps,complex);q=len(forms);n=forms[0]['K'].shape[0];nh=n//84
    if q!=2 or h.shape!=(q,)or h[0]==0 or h[1]!=h[0]or len(magnetic_sources)!=q:
        raise ValueError('the actual equal-step two-stage control prefix is required')
    k=len(forms_first[0]['K']);ns=magnetic_sources[0]['Q'].shape[-1]
    lifts=chronological_n0_field_lifts(representation,value_permutation)
    cs=complete_gauge_wall_constraints(lifts,nh);C=cs['constraint'];nc=len(C);b=n+nc;size=q*b
    L=np.kron(original_named_wall_lift(representation,value_permutation),np.eye(nh))
    A=np.zeros((size,size),complex);dA=np.zeros((k,size,size),complex)
    rhs=np.zeros((size,ns),complex);drhs=np.zeros((k,size,ns),complex)
    source_records=[];z,w=np.polynomial.legendre.leggauss(5);total=np.sum(h)
    # One polynomial sews the two actual midpoint Q/Qdot germs. Both
    # value and derivative come from that SAME polynomial; independent
    # stage-centered affine sources would in general jump at the corner.
    def hermite(sigma,key,ratekey):
        t=(sigma-.25)/.5
        p=np.array([2*t**3-3*t**2+1,t**3-2*t**2+t,-2*t**3+3*t**2,t**3-t**2])
        dp=np.array([6*t*t-6*t,3*t*t-4*t+1,-6*t*t+6*t,3*t*t-2*t])/(.5*total)
        operands=(magnetic_sources[0][key],.5*total*magnetic_sources[0][ratekey],
            magnetic_sources[1][key],.5*total*magnetic_sources[1][ratekey])
        return sum(a*b for a,b in zip(p,operands)),sum(a*b for a,b in zip(dp,operands))
    broken_jump=magnetic_sources[1]['Q']-.5*h[1]*magnetic_sources[1]['Q_coordinate_time']\
        -magnetic_sources[0]['Q']-.5*h[0]*magnetic_sources[0]['Q_coordinate_time']
    broken_first=magnetic_sources[1]['Q_first']-.5*h[1]*magnetic_sources[1]['Q_coordinate_time_first']\
        -magnetic_sources[0]['Q_first']-.5*h[0]*magnetic_sources[0]['Q_coordinate_time_first']
    for cell,(f,df,source,dt)in enumerate(zip(forms,forms_first,magnetic_sources,h)):
        # Split at the OWNED turn-on end so each integrand is polynomial.
        lo,hi=cell/q,(cell+1)/q;cuts=sorted(set((lo,hi)+((.25,)if lo<.25<hi else())))
        for left,right in zip(cuts[:-1],cuts[1:]):
            for point,weight in zip(z,w):
                sigma=(left+right)/2+(right-left)*point/2
                local=q*sigma-cell;offset=(local-.5)*dt
                g,gs,_=magnetic_turn_on_profile(sigma,.25);gt=gs/total
                Q,Qt=hermite(sigma,'Q','Q_coordinate_time')
                dQ,dQt=hermite(sigma,'Q_first','Q_coordinate_time_first')
                wall=g*Q;wallt=gt*Q+g*Qt;dwall=g*dQ;dwallt=gt*dQ+g*dQt
                av=L@wall.reshape(20*nh,ns);at=L@wallt.reshape(20*nh,ns)
                dav=np.einsum('ij,kjs->kis',L,dwall.reshape(k,20*nh,ns))
                dat=np.einsum('ij,kjs->kis',L,dwallt.reshape(k,20*nh,ns))
                p=np.array([1-local,local]);v=np.array([-1/dt,1/dt])
                scale=-1j*total*(right-left)*weight/2
                source_records.append(dict(cell=cell,sigma=sigma,coordinate_offset=offset,scale=scale,
                    known_field=av,known_coordinate_rate=at,known_field_first=dav,known_coordinate_rate_first=dat,
                    complete_wall_source=wall,complete_wall_source_rate=wallt))
                for a in range(2):
                    j=cell+a
                    if j==0:continue
                    sj=slice((j-1)*b,(j-1)*b+n)
                    load=p[a]*(f['K']@av+f['B_forward']@at)+v[a]*(f['B_reverse']@av+f['M']@at)
                    rhs[sj]-=scale*load
                    drhs[:,sj]-=scale*(p[a]*(df['K']@av+f['K']@dav+df['B_forward']@at+f['B_forward']@dat)
                        +v[a]*(df['B_reverse']@av+f['B_reverse']@dav+df['M']@at+f['M']@dat))
                    for c in range(2):
                        jj=cell+c
                        if jj==0:continue
                        sk=slice((jj-1)*b,(jj-1)*b+n)
                        A[sj,sk]+=scale*(p[a]*p[c]*f['K']+p[a]*v[c]*f['B_forward']+v[a]*p[c]*f['B_reverse']+v[a]*v[c]*f['M'])
                        dA[:,sj,sk]+=scale*(p[a]*p[c]*df['K']+p[a]*v[c]*df['B_forward']+v[a]*p[c]*df['B_reverse']+v[a]*v[c]*df['M'])
    for j in range(q):
        sl=slice(j*b,j*b+n);sc=slice(j*b+n,(j+1)*b);A[sl,sc]=C.T;A[sc,sl]=C
    d=np.ones(size)
    for _ in range(8):
        norm=np.max(abs(d[:,None]*A*d[None]),axis=1)
        if np.any(norm==0):raise ValueError('an original zero row is not an authorized domain reduction')
        d/=np.sqrt(norm)
    eq=d[:,None]*A*d[None];answer=d[:,None]*solve(eq,d[:,None]*rhs,assume_a='gen')
    first=np.array([d[:,None]*solve(eq,d[:,None]*(drhs[j]-dA[j]@answer),assume_a='gen')for j in range(k)])
    fields=answer.reshape(q,b,ns)[:,:n];dfields=first.reshape(k,q,b,ns)[:,:,:n]
    initial=np.zeros((1,n,ns),complex);full=np.r_[initial,fields];dfull=np.concatenate((np.zeros((k,1,n,ns)),dfields),axis=1)
    point=[]
    for r in source_records:
        j=r['cell'];local=q*r['sigma']-j;p=np.array([1-local,local]);v=np.array([-1/h[j],1/h[j]])
        x=np.einsum('i,ias->as',p,full[j:j+2])+r['known_field']
        xd=np.einsum('i,ias->as',v,full[j:j+2])+r['known_coordinate_rate']
        dx=np.einsum('i,kias->kas',p,dfull[:,j:j+2])+r['known_field_first']
        dxd=np.einsum('i,kias->kas',v,dfull[:,j:j+2])+r['known_coordinate_rate_first']
        point.append(dict(**r,total_field=x,total_coordinate_rate=xd,total_field_first=dx,total_coordinate_rate_first=dxd,
            original_full_wall_rows=cs['all_gauge_wall']@x-r['complete_wall_source'].reshape(20*nh,ns),
            original_full_wall_rate_rows=cs['all_gauge_wall']@xd-r['complete_wall_source_rate'].reshape(20*nh,ns)))
    rows=A@answer-rhs;drows=dA@answer+A@first-drhs
    reaction=answer.reshape(q,b,ns)[:,n:];traction=np.einsum('ac,qcb->qab',C.T,reaction)
    unbordered=rows.reshape(q,b,ns)[:,:n]-traction
    frame_ids=set(lifts['frame_indices'].tolist());ids=np.asarray(value_permutation,int)
    kept=[i for i,j in enumerate(ids)if i not in frame_ids and(j>=80 or not representation['gauge_labels'][j].get('wall_lift',False))]
    N0=(np.eye(84)-original_named_wall_lift(representation,value_permutation)@lifts['W'])@np.eye(84)[:,kept]
    free=np.kron(N0,np.eye(nh))
    if len(kept)!=61 or np.max(abs(C@free))>2e-13:raise ValueError('named complete zero-wall/frame interior lift required')
    interior=np.einsum('ac,qcb->qab',free.T,unbordered)
    return dict(field_coefficients=fields,field_coefficients_first=dfields,all_original_solution=answer,
        all_original_solution_first=first,original_rows=rows,original_first_rows=drows,
        bordered_Gauss_balance_rows=rows.reshape(q,b,ns)[:,:16*nh],
        unbordered_field_rows=unbordered,unbordered_Gauss_rows=unbordered[:,:16*nh],
        field_wall_and_frame_reaction=traction,
        original_free_interior_lift=free,unbordered_free_interior_rows=interior,
        unbordered_free_interior_Gauss_rows=interior[:,:12*nh],
        original_rowwise_balance_estimate=abs(rows)/(abs(A)@abs(answer)+abs(rhs)+np.finfo(float).tiny),
        wall_reactions=answer.reshape(q,b,ns)[:,n:n+19*nh],
        frame_reactions=answer.reshape(q,b,ns)[:,n+19*nh:],
        source_rhs=rhs,source_rhs_first=drhs,point_sources=point,
        prescribed_full_gauge_unknown_wall_rows=np.einsum('ac,qcb->qab',cs['all_gauge_wall'],fields),
        named_frame_rows=np.einsum('ac,qcb->qab',cs['frame'],fields),
        C2_ramp_initial_value_and_rate=np.array(magnetic_turn_on_profile(0,.25)[:2]),
        unused_stage_affine_wall_corner_jump=broken_jump,unused_stage_affine_wall_corner_jump_first=broken_first,
        unused_stage_affine_wall_rate_jump=magnetic_sources[1]['Q_coordinate_time']-magnetic_sources[0]['Q_coordinate_time'],
        source_midpoint_Q_Qdot_joined_by_one_Hermite_polynomial=True,
        source_common_corner_value_and_rate=hermite(.5,'Q','Q_coordinate_time'),
        computational_ramp_duration_fraction=.25,backward_prefix_control=bool(h[0].real<0 or(h[0].real==0 and h[0].imag<0)),
        physical_retarded_first_field_or_exterior_or_Pauli_selected=False)


def magnetic_unsquared_unit_em_current(bindings,coordinate_steps,response):
    """Consume actual B fields in kernel, right-current and literal-left slots.

    n0+n1 fermion coordinate tests and every full18 neutral/charged fiber
    are retained. Unit-Haar constant phi0=1 fixes the n1 multiplication.
    This is J.T A^-1 J on the same finite initial-held/free-final prefix,
    with LT=JR.T the declared test dual. It is not a Gaussian loop, pole,
    charge normalization, contact with a closed mean, or soft Pauli form.
    """
    angular=magnetic_angular_trace();E=angular['derivative_matrices'];d=90
    from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
    alpha=lepton_current_hilbert_representation()['alpha']
    k=len(response['point_sources'][0]['total_field_first'])if 'total_field_first'in response['point_sources'][0]else 0
    stages=[]
    for b in bindings:
        s=b['stage'];R=s['R4'].item();N=s['induced_lapse'].item();H=s['Hcan'];h=b['row']['H']
        dh=b['row_first']['H'].T if k else np.zeros((4,1));dN=s['induced_lapse_first']if k else np.zeros(1)
        em=holomorphic_unit_em_moments(h,dh,N,dN)
        body=np.zeros((d,d),complex);J=body.copy();L=body.copy()
        body[:18,:18]=H;body[18:,18:]=np.kron(H,np.eye(4))-1j*sum(np.kron(a,e)for a,e in zip(alpha,E))/R
        J[:18,:18]=em['literal_right'];J[18:,18:]=np.kron(em['literal_right'],np.eye(4))
        L[:18,:18]=em['literal_left'];L[18:,18:]=np.kron(em['literal_left'],np.eye(4))
        st=dict(B=-1j*N*body,F=1j*N*J,T=1j*N*L,N=N,h=h,vertices=s['canonical_wall_current_vertices'])
        if k:
            dbody=np.zeros((k,d,d),complex);dJ=dbody.copy();dL=dbody.copy()
            dbody[:,:18,:18]=s['Hcan_first']
            for a in range(k):
                dbody[a,18:,18:]=np.kron(s['Hcan_first'][a],np.eye(4))+1j*sum(np.kron(ai,ei)for ai,ei in zip(alpha,E))*s['R4_first'][a]/R**2
                dJ[a,:18,:18]=em['literal_right_first'][a];dJ[a,18:,18:]=np.kron(em['literal_right_first'][a],np.eye(4))
                dL[a,:18,:18]=em['literal_left_first'][a];dL[a,18:,18:]=np.kron(em['literal_left_first'][a],np.eye(4))
            st.update(B_first=-1j*dN[:,None,None]*body-1j*N*dbody,
                F_first=1j*dN[:,None,None]*J+1j*N*dJ,T_first=1j*dN[:,None,None]*L+1j*N*dL,
                N_first=dN,H_first=dh,vertices_first=s['canonical_wall_current_vertices_first'])
        stages.append(st)
    def segment(j,dt):
        s=stages[j];A=np.zeros((2*d,2*d),complex);A[:d,:d]=s['B'];A[:d,d:]=np.eye(d)
        if k:
            derivative=[];Z=None
            for a in range(k):
                dA=np.zeros_like(A);dA[:d,:d]=s['B_first'][a]
                value,dvalue=expm_frechet(dt*A,dt*dA)
                if Z is None:Z=value
                derivative.append(dvalue)
            derivative=np.array(derivative);dU=derivative[:,:d,:d];dM0=derivative[:,:d,d:]
        else:Z=expm(dt*A)
        U=Z[:d,:d];M0=Z[:d,d:];out=dict(U=U,r=M0@s['F'],L=s['T']@M0)
        if k:out.update(U_first=dU,r_first=dM0@s['F']+M0@s['F_first'],
            L_first=s['T_first']@M0+s['T']@dM0)
        return out
    h=np.asarray(coordinate_steps,complex);full=[segment(j,dt)for j,dt in enumerate(h)]
    terms={n:np.zeros((3,d,d),complex)for n in('operator_insertion','right_current_motion','literal_left_motion')}
    first_terms={n:np.zeros((k,3,d,d),complex)for n in terms}
    Xi_points=[];source_points=[]
    for r in response['point_sources']:
        j=r['cell'];local=2*r['sigma']-j
        earlier=segment(j,local*h[j]);U0=earlier['U'];u=earlier['r']
        if k:du=earlier['r_first'];dU0=earlier['U_first']
        for prev in range(j-1,-1,-1):
            # There are exactly two stages; retain general ordered prefix.
            if k:
                du+=dU0@full[prev]['r']+U0@full[prev]['r_first']
                dU0=dU0@full[prev]['U']+U0@full[prev]['U_first']
            u+=U0@full[prev]['r'];U0=U0@full[prev]['U']
        later_segment=segment(j,(1-local)*h[j]);Uf=later_segment['U'];p=later_segment['L']
        if k:dp=later_segment['L_first'];dUf=later_segment['U_first']
        for later in range(j+1,len(full)):
            if k:
                dp+=full[later]['L_first']@Uf+full[later]['L']@dUf
                dUf=full[later]['U_first']@Uf+full[later]['U']@dUf
            p+=full[later]['L']@Uf;Uf=full[later]['U']@Uf
        # p is the literal left integral, not its Hilbert adjoint.
        W=np.r_[bindings[j]['lifts']['W'],bindings[j]['lifts']['hv']]
        wall=np.einsum('ca,ahb->chb',W,r['total_field'].reshape(84,4,3))
        coeff=np.einsum('chb,cij->bhij',wall,stages[j]['vertices'])
        Hfirst=wall[20:].reshape(4,12)
        em=holomorphic_unit_em_moments(stages[j]['h'],Hfirst,stages[j]['N'],np.zeros(12))
        dJ=em['literal_right_first'].reshape(4,3,18,18).transpose(1,0,2,3)
        dL=em['literal_left_first'].reshape(4,3,18,18).transpose(1,0,2,3)
        Xi=np.zeros((3,d,d),complex);JR=Xi.copy();LT=Xi.copy()
        if k:
            dwall=np.einsum('ca,kahb->kchb',W,r['total_field_first'].reshape(k,84,4,3))
            dcoeff=np.einsum('kchb,cij->kbhij',dwall,stages[j]['vertices'])+np.einsum('chb,kcij->kbhij',wall,stages[j]['vertices_first'])
            dJB=_mixed_H_selected_EM_source(stages[j]['h'],stages[j]['H_first'],Hfirst,
                dwall[:,20:].reshape(k,4,12),N=stages[j]['N'],N_first=stages[j]['N_first'])
            dLB=dJB.swapaxes(-1,-2)
            dJB=dJB.reshape(k,4,3,18,18).transpose(0,2,1,3,4)
            dLB=dLB.reshape(k,4,3,18,18).transpose(0,2,1,3,4)
            dXi=np.zeros((k,3,d,d),complex);dJR=dXi.copy();dLT=dXi.copy()
        for a in range(3):
            Xi[a,18:,:18]=coeff[a].transpose(1,0,2).reshape(72,18)
            Xi[a,:18,18:]=coeff[a].transpose(1,2,0).reshape(18,72)
            JR[a,18:,:18]=dJ[a].transpose(1,0,2).reshape(72,18)
            JR[a,:18,18:]=dJ[a].transpose(1,2,0).reshape(18,72)
            LT[a,18:,:18]=dL[a].transpose(1,0,2).reshape(72,18)
            LT[a,:18,18:]=dL[a].transpose(1,2,0).reshape(18,72)
            if k:
                dXi[:,a,18:,:18]=dcoeff[:,a].transpose(0,2,1,3).reshape(k,72,18)
                dXi[:,a,:18,18:]=dcoeff[:,a].transpose(0,2,3,1).reshape(k,18,72)
                dJR[:,a,18:,:18]=dJB[:,a].transpose(0,2,1,3).reshape(k,72,18)
                dJR[:,a,:18,18:]=dJB[:,a].transpose(0,2,3,1).reshape(k,18,72)
                dLT[:,a,18:,:18]=dLB[:,a].transpose(0,2,1,3).reshape(k,72,18)
                dLT[:,a,:18,18:]=dLB[:,a].transpose(0,2,3,1).reshape(k,18,72)
        weight=1j*r['scale'];N=stages[j]['N']
        terms['operator_insertion']+=weight*(p@(-1j*N*Xi)@u)
        terms['right_current_motion']+=weight*(p@(1j*N*JR))
        terms['literal_left_motion']+=weight*((1j*N*LT)@u)
        if k:
            for c in range(k):
                dN=stages[j]['N_first'][c]
                first_terms['operator_insertion'][c]+=weight*(dp[c]@(-1j*N*Xi)@u
                    +p@(-1j*dN*Xi-1j*N*dXi[c])@u+p@(-1j*N*Xi)@du[c])
                first_terms['right_current_motion'][c]+=weight*(dp[c]@(1j*N*JR)+p@(1j*dN*JR+1j*N*dJR[c]))
                first_terms['literal_left_motion'][c]+=weight*((1j*dN*LT+1j*N*dLT[c])@u+(1j*N*LT)@du[c])
        Xi_points.append(Xi);source_points.append(JR)
    total=sum(terms.values())
    total_first=sum(first_terms.values())
    return dict(**terms,**{n+'_first':v for n,v in first_terms.items()},total=total,total_first=total_first,
        forward_n1_from_n0=total[:,18:,:18],reverse_n0_from_n1=total[:,:18,18:],
        forward_n1_from_n0_first=total_first[:,:,18:,:18],reverse_n0_from_n1_first=total_first[:,:,:18,18:],
        actual_Xi_n0_n1=np.array(Xi_points),actual_EM_right_source_motion=np.array(source_points),
        literal_left_is_declared_test_transpose=True,all_three_families_and_neutral_return_retained=True,
        standalone_density_zero_only_for_defined_unsquared_bilinear=True,
        actual_quantum_Gamma2_or_physical_LSZ_Pauli_completed=False)


def _mixed_H_selected_EM_source(h,dh,hB,hB_first,*,N,N_first):
    """Normal variation of the magnetic H-selected source, analytic on both branches."""
    q=h@h;dq=2*h@dh;qb=2*h@hB;dqb=2*(dh.T@hB+np.einsum('i,kij->kj',h,hB_first))
    hp,hm=h[:2]+1j*h[2:],h[:2]-1j*h[2:]
    np_,nm=dh[:2]+1j*dh[2:],dh[:2]-1j*dh[2:]
    bp,bm=hB[:2]+1j*hB[2:],hB[:2]-1j*hB[2:]
    dbp,dbm=hB_first[:,:2]+1j*hB_first[:,2:],hB_first[:,:2]-1j*hB_first[:,2:]
    P=np.outer(hp,hm)/q
    dP=np.array([(np.outer(a,hm)+np.outer(hp,b))/q-P*c/q for a,b,c in zip(np_.T,nm.T,dq)])
    num=np.einsum('ia,j->aij',bp,hm)+np.einsum('i,ja->aij',hp,bm)
    dnum=np.einsum('kia,j->kaij',dbp,hm)+np.einsum('ia,jk->kaij',bp,nm)\
        +np.einsum('ik,ja->kaij',np_,bm)+np.einsum('i,kja->kaij',hp,dbm)
    dPb=dnum/q-num[None]*dq[:,None,None,None]/q**2-dP[:,None]*qb[None,:,None,None]/q\
        -P[None,None]*dqb[:,:,None,None]/q+P[None,None]*qb[None,:,None,None]*dq[:,None,None,None]/q**2
    Pb=num/q-P[None]*qb[:,None,None]/q
    Qb=np.zeros((hB.shape[1],18,18),complex);dQb=np.zeros((dh.shape[1],hB.shape[1],18,18),complex)
    Qb[:,:12,:12]=-np.array([np.kron(a,np.eye(6))for a in Pb])
    dQb[:,:,:12,:12]=-np.array([[np.kron(a,np.eye(6))for a in row]for row in dPb])
    return -dQb/N+Qb[None]*N_first[:,None,None,None]/N**2
