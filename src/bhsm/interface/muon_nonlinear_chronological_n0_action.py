"""Literal nonlinear n0 action on every retained chronological field node.

The output is a directed neighbor Hessian, retaining all 84 original
field/Gauss coordinates and four named central-Ar frame rows per node.
No local window native gradient is substituted for the whole heat source.
"""
from __future__ import annotations
import numpy as np
from .muon_nonlinear_n0_field_action import analytic_intrinsic_n0_jet
from .muon_matched_mechanical_source import epsilon
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP


def _ad_batch(a):
    x=np.asarray(a,complex);z=np.zeros(x.shape[:-1]+(4,4),complex)
    z[...,:3,:3]=np.einsum('abc,...a->...cb',epsilon(),x[...,:3])/np.sqrt(2)
    return z


def analytic_constant_maxwell_batch(A,At,Ar,densities):
    """Exact analytic quartic jets, with the original radial rows batched."""
    A,At,Ar,c=[np.asarray(x,complex)for x in(A,At,Ar,densities)]
    n=len(A)
    if A.shape!=(n,5,4)or At.shape!=A.shape or Ar.shape!=A.shape or c.shape!=(n,5)or any(not np.isfinite(x).all()for x in(A,At,Ar,c)):
        raise ValueError('complete finite complex local radial coefficient arrays required')
    e,r,d,k,beta=c.T;eps=epsilon();S=np.eye(20).reshape(5,4,20)
    ad=_ad_batch(A);X=At[:,1]-Ar[:,0]+np.einsum('rij,rj->ri',ad[:,0],A[:,1])
    T=At[:,2:]+np.einsum('rij,raj->rai',ad[:,0],A[:,2:])
    R=Ar[:,2:]+np.einsum('rij,raj->rai',ad[:,1],A[:,2:]);B=2*A[:,2:].copy()
    for i,j,h in np.argwhere(eps):B[:,i]+=.5*eps[i,j,h]*np.einsum('rab,rb->ra',ad[:,2+j],A[:,2+h])
    JX=np.zeros((n,4,60),complex);JT=np.zeros((n,12,60),complex);JR=JT.copy();JB=JT.copy()
    JX[:,:,:20]=ad[:,0]@S[1]-ad[:,1]@S[0];JX[:,:,20:40]=S[1];JX[:,:,40:]=-S[0]
    for i in range(3):
        sl=slice(4*i,4*i+4)
        JT[:,sl,:20]=ad[:,0]@S[2+i]-ad[:,2+i]@S[0];JT[:,sl,20:40]=S[2+i]
        JR[:,sl,:20]=ad[:,1]@S[2+i]-ad[:,2+i]@S[1];JR[:,sl,40:]=S[2+i]
        JB[:,sl,:20]=2*S[2+i]
    for i,j,h in np.argwhere(eps):JB[:,4*i:4*i+4,:20]+=eps[i,j,h]*(ad[:,2+j]@S[2+h])
    Y=T-beta[:,None,None]*R;JY=JT-beta[:,None,None]*JR
    def square(J,w):return J.swapaxes(1,2)@(w[:,None,None]*J)
    H=square(JX,k)+square(JY,e)-square(JR,r)-square(JB,d)
    def first(J,v,w):return w[:,None]*np.einsum('ria,ri->ra',J,v.reshape(n,-1))
    g=first(JX,X,k)+first(JY,Y,e)-first(JR,R,r)-first(JB,B,d)
    C=np.zeros((n,20,20),complex)
    def contact(i,j,f):
        z=np.zeros((n,4,4),complex);z[:,:3,:3]=np.einsum('abc,rc->rab',eps,f[:,:3])/np.sqrt(2)
        C[:,4*i:4*i+4,4*j:4*j+4]+=z;C[:,4*j:4*j+4,4*i:4*i+4]+=z.swapaxes(1,2)
    contact(0,1,k[:,None]*X)
    for i in range(3):
        contact(0,2+i,e[:,None]*Y[:,i]);contact(1,2+i,-(e*beta)[:,None]*Y[:,i]-r[:,None]*R[:,i])
    for i,j,h in np.argwhere(eps):contact(2+j,2+h,-.5*d[:,None]*eps[i,j,h]*B[:,i])
    H[:,:20,:20]+=C
    value=.5*(k*np.sum(X*X,axis=1)+e*np.sum(Y*Y,axis=(1,2))-r*np.sum(R*R,axis=(1,2))-d*np.sum(B*B,axis=(1,2)))
    return dict(value=value,gradient=g,hessian=H,curvature_contact=C)


def chronological_n0_field_lifts(representation,value_permutation):
    """Keep the original material At chart and all four radial profiles."""
    rep=representation;ids=np.asarray(value_permutation,int)
    if ids.shape!=(84,)or sorted(ids.tolist())!=list(range(84)):raise ValueError('complete original84 permutation required')
    L=np.eye(84)[:,ids];gv=L[:80];hv=L[80:];tg=gv.copy()
    for j,label in enumerate(rep['gauge_labels']):
        if label['field']=='A_tau':tg[j]=0
    P=np.einsum('rgfc,ga->rfca',np.asarray(rep['gauge_basis'])[:,:,0],gv).reshape(-1,20,84)
    Pr=np.einsum('rgfc,ga->rfca',np.asarray(rep['gauge_radial_basis'])[:,:,0],gv).reshape(-1,20,84)
    Pt=np.einsum('rgfc,ga->rfca',np.asarray(rep['gauge_basis'])[:,:,0],tg).reshape(-1,20,84)
    z=np.zeros_like(P);Jv=np.concatenate((P,z,Pr),axis=1);Jt=np.concatenate((z,Pt,z),axis=1)
    W=np.asarray(rep['wall_trace_map']).reshape(20,80)@gv
    Sv=np.r_[hv,W,np.zeros_like(hv)];St=np.r_[np.zeros_like(hv),np.zeros_like(W),hv]
    frame_raw=[j for j,l in enumerate(rep['gauge_labels'])if l['field']=='A_rho'and l['internal']==3]
    frame=np.array([int(np.flatnonzero(ids==j)[0])for j in frame_raw])
    if len(frame)!=4 or np.any(ids[:16]>=80)or any(rep['gauge_labels'][j]['field']!='A_tau'for j in ids[:16]):
        raise ValueError('all16 original Gauss and four named central-Ar rows required')
    return dict(P=P,Pr=Pr,Pt=Pt,W=W,hv=hv,Jv=Jv,Jt=Jt,Sv=Sv,St=St,
        radial_weights=np.asarray(rep['radial_quadrature']),frame_rows=np.eye(84)[frame],frame_indices=frame)


def nonlinear_n0_point_jet(row,value,coordinate_rate,lifts):
    """Differentiate the literal field action before temporal FE assembly."""
    v,t=[np.asarray(x,complex)for x in(value,coordinate_rate)]
    if v.shape!=(84,)or t.shape!=(84,):raise ValueError('all original field values and rates required')
    P,Pr,Pt,W,hv=(lifts[k]for k in('P','Pr','Pt','W','hv'))
    A=row['A']+(P@v).reshape(-1,5,4);At=row['At']+(Pt@t).reshape(-1,5,4);Ar=row['Ar']+(Pr@v).reshape(-1,5,4)
    q=analytic_constant_maxwell_batch(A,At,Ar,row['densities']);weights=MAXWELL_TO_CAP*lifts['radial_weights']
    Jv,Jt=lifts['Jv'],lifts['Jt'];Hv=q['hessian']@Jv;Ht=q['hessian']@Jt
    def bilinear(J,Z):return np.einsum('ria,rib,r->ab',J,Z,weights,optimize=True)
    K=bilinear(Jv,Hv);B=bilinear(Jv,Ht);M=bilinear(Jt,Ht)
    gv=np.einsum('ria,ri,r->a',Jv,q['gradient'],weights,optimize=True)
    gt=np.einsum('ria,ri,r->a',Jt,q['gradient'],weights,optimize=True)
    value=np.sum(weights*q['value'])
    s=analytic_intrinsic_n0_jet(row['wall_A']+(W@v).reshape(5,4),row['H']+hv@v,row['Hdot']+hv@t,
        row['weights'],lambda_H=row['lambda_H'],nu_squared_action=row['nu_squared_action'])
    Sv,St=lifts['Sv'],lifts['St'];Hs=s['hessian']
    K+=Sv.T@Hs@Sv;B+=Sv.T@Hs@St;M+=St.T@Hs@St
    gv+=Sv.T@s['gradient'];gt+=St.T@s['gradient'];value+=s['value']
    return dict(value=value,value_gradient=gv,rate_gradient=gt,K=K,B=B,M=M)


def nonlinear_chronological_n0_action(coefficients,quadrature,representation,*,temporal_nodes,value_permutation,progress=None):
    """All original rows on the complete directed chronological graph.

    Initial node zero is the only removed trace; final and every corner
    trace have their original natural action rows. Output Hessian blocks
    are in the 84-field order. At/Gauss rows stay INSIDE those blocks.
    """
    n=int(temporal_nodes);x=np.asarray(coefficients,complex)
    if type(temporal_nodes)is not int or n<2 or x.shape!=(n-1,84)or not np.isfinite(x).all():
        raise ValueError('all same-graph free nodal field coefficients required')
    lifts=chronological_n0_field_lifts(representation,value_permutation);full=np.r_[np.zeros((1,84),complex),x]
    gradient=np.zeros_like(full);D=np.zeros((n-1,84,84),complex);U=np.zeros((n-2,84,84),complex);L=U.copy()
    initial_Hessian=np.zeros((84,84),complex);initial_to_first=np.zeros((84,84),complex);value=0j
    count=len(quadrature)
    for iq,row in enumerate(quadrature):
        rows=row['rows']
        if len(rows)!=2 or rows[1][0]!=rows[0][0]+1:raise ValueError('the original complete nearest-neighbor incidence is required')
        if any(type(j)is not int or not 0<=j<n for j,_,_ in rows):raise ValueError('original temporal node indices required')
        clock=complex(row['right_clock']);N=complex(row['N']);scale=-complex(row['measure'])/N
        if clock==0 or N==0:raise ValueError('both original coframe and action clock must be nonzero')
        v=sum(p*full[j]for j,p,_ in rows);t=(1j*N/clock)*sum(d*full[j]for j,_,d in rows)
        a=nonlinear_n0_point_jet(row,v,t,lifts);value+=scale*a['value']
        for j,pj,dj in rows:
            tj=1j*N*dj/clock;gradient[j]+=scale*(pj*a['value_gradient']+tj*a['rate_gradient'])
            for k,pk,dk in rows:
                tk=1j*N*dk/clock
                H=scale*(pj*pk*a['K']+pj*tk*a['B']+tj*pk*a['B'].T+tj*tk*a['M'])
                if j==0:
                    if k==0:initial_Hessian+=H
                    elif k==1:initial_to_first+=H
                elif k==0:pass
                elif j==k:D[j-1]+=H
                elif k==j+1:U[j-1]+=H
                elif j==k+1:L[k-1]+=H
                else:raise ArithmeticError('a non-neighbor action contact appeared')
        if progress is not None and(iq%192==191 or iq==count-1):progress(iq+1,count)
    return dict(value=value,gradient=gradient[1:],Hessian_diagonal=D,Hessian_upper=U,Hessian_lower=L,
        initial_face_gradient=gradient[0],initial_face_Hessian=initial_Hessian,initial_to_first_Hessian=initial_to_first,
        frame_rows_per_node=lifts['frame_rows'],frame_indices=lifts['frame_indices'],
        frame_constraint=x@lifts['frame_rows'].T,Gauss_indices_per_node=np.arange(16),
        initial_only_trace_removed=True,final_natural_cotangent_retained=True,
        temporal_nodes=n,free_field_rows=(n-1)*84,
        geometry_and_native_gradient_not_changed_by_this_classical_application=True)


def chronological_field_KKT_blocks(action,reaction=None,native_gradient=None):
    """Produce directed88 blocks, keeping all16 Gauss rows in each84."""
    g=action['gradient'];n=len(g);C=action['frame_rows_per_node'];rho=np.zeros((n,4),complex)if reaction is None else np.asarray(reaction,complex)
    source=np.zeros_like(g)if native_gradient is None else np.asarray(native_gradient,complex)
    if C.shape!=(4,84)or rho.shape!=(n,4)or source.shape!=g.shape:raise ValueError('same-field whole graph source and named frame reaction required')
    D=np.zeros((n,88,88),complex);U=np.zeros((n-1,88,88),complex);L=U.copy()
    D[:,:84,:84]=action['Hessian_diagonal'];U[:,:84,:84]=action['Hessian_upper'];L[:,:84,:84]=action['Hessian_lower']
    D[:,:84,84:]=C.T;D[:,84:,:84]=C
    residual=np.c_[g+source+rho@C,action['frame_constraint']]
    return dict(diagonal=D,upper=U,lower=L,residual=residual,
        At_Gauss_rows_inside_original84=True,frame_rows_are_the_four_named_original_Ar_slices=True,
        native_gradient_supplied=native_gradient is not None)
