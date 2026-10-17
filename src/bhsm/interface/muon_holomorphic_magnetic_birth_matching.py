"""Action-owned magnetic face reconstruction and original birth field audits."""
from __future__ import annotations
import numpy as np
from scipy.linalg import solve


def signed_field_face_reconstruction(forms,interior_lift,wall_lift,wall_germ,state,interior_At_count):
    """Reconstruct a stored canonical face using its literal signed action.

    Interior x/p are preserved. At is eliminated by its original Gauss rows;
    known wall value/rate/second remain literal supplied source functions.
    Momentum is Lorentz M*rate+BR*field, with no Hilbert adjoint.
    """
    S,L,z=np.asarray(interior_lift,complex),np.asarray(wall_lift,complex),np.asarray(state,complex)
    na=int(interior_At_count);nd=S.shape[1]-na;ns=z.shape[1]
    if z.shape!=(2*nd,ns)or L.shape[0]!=S.shape[0]:raise ValueError('same complete interior canonical source face required')
    K,BF,BR,M=[np.asarray(forms[n],complex)for n in('K','B_forward','B_reverse','M')]
    kr,bf,br,m=(S.T@a@S for a in(K,BF,BR,M));Sa,Sd=S[:,:na],S[:,na:]
    if max(np.max(abs(m[:na])),np.max(abs(m[:,:na])),np.max(abs(br[:na])),np.max(abs(bf[:,:na])))>1e-13:
        raise ValueError('At must remain algebraic in the original signed action')
    gauss=lambda b:solve(kr[:na,:na],b,assume_a='gen')
    U,V=gauss(kr[:na,na:]),gauss(bf[:na,na:])
    Kr=kr[na:,na:]-kr[na:,:na]@U;Fr=bf[na:,na:]-kr[na:,:na]@V
    Rr=br[na:,na:]-br[na:,:na]@U;Mr=m[na:,na:]-br[na:,:na]@V
    if len(wall_germ)not in(2,3):raise ValueError('literal source value/rate, optionally actual second source germ required')
    known=[L@np.asarray(a,complex).reshape(L.shape[1],ns)for a in wall_germ]
    a,at=known[:2]
    gv=S.T@(K@a+BF@at);gt=S.T@(BR@a+M@at)
    ag=gauss(gv[:na])
    value=gv[na:]-kr[na:,:na]@ag;rate=gt[na:]-br[na:,:na]@ag
    x,p=z[:nd],z[nd:]
    v=solve(Mr,p-Rr@x-rate,assume_a='gen');pd=Kr@x+Fr@v+value
    algebraic=-gauss(kr[:na,na:]@x+bf[:na,na:]@v+gv[:na])
    field=Sa@algebraic+Sd@x+a;coordinate_rate=Sd@v+at
    result={}
    if len(known)==3:
        att=known[2];gvt=S.T@(K@at+BF@att);gtt=S.T@(BR@at+M@att)
        agt=gauss(gvt[:na]);rate_time=gtt[na:]-br[na:,:na]@agt
        vd=solve(Mr,pd-Rr@v-rate_time,assume_a='gen')
        algebraic_rate=-gauss(kr[:na,na:]@v+bf[:na,na:]@vd+gvt[:na])
        coordinate_rate+=Sa@algebraic_rate
        acceleration=Sd@vd+att # At acceleration never appears in this action.
        momentum_time=M@acceleration+BR@coordinate_rate
        result.update(canonical_momentum_time=momentum_time,interior_At_coordinate_rate=algebraic_rate)
    momentum=M@coordinate_rate+BR@field;force=K@field+BF@coordinate_rate
    if len(known)==3:result['original_unbordered_Euler_rows']=force-result['canonical_momentum_time']
    result.update(total_field=field,total_coordinate_rate=coordinate_rate,canonical_momentum=momentum,
        original_action_force=force,original_interior_Gauss_rows=Sa.T@force,
        original_interior_momentum_rows=Sd.T@momentum-p,canonical_state=z,
        reduced_K=Kr,reduced_M=Mr,reduced_B_forward=Fr,reduced_B_reverse=Rr,
        interior_At=algebraic,original_interior_dynamic_coordinate_rate=v,known_wall_field=a,known_wall_coordinate_rate=at,
        algebraic_At_time_rate_computed=len(known)==3,
        unknown_At_rate_placeholder_unused_in_original_Gauss_and_momentum_only=len(known)==2)
    return result


def inherited_birth_interior_reconstitution(forms,S,L,parent_field,parent_momentum,child_wall_germ,interior_At_count):
    """Conditional action-defined child interior solve at inherited q/p.

    Only the known-wall decomposition is used. Original FULL dynamic value,
    momentum and all At Gauss rows are independently returned for guarding;
    an interior solve cannot hide imposed-wall or named-frame reactions.
    """
    S=np.asarray(S,complex);na=int(interior_At_count);Sd=S[:,na:]
    q=np.asarray(parent_field,complex);p=np.asarray(parent_momentum,complex)
    known=L@np.asarray(child_wall_germ[0]).reshape(L.shape[1],q.shape[1])
    state=np.r_[Sd.T@(q-known),Sd.T@p]
    a=signed_field_face_reconstruction(forms,S,L,child_wall_germ,state,na)
    a['inherited_field_value_residual']=a['total_field']-q
    a['inherited_canonical_momentum_residual']=a['canonical_momentum']-p
    return a


def original_birth_field_rows(parent,child,value_permutation,gauge_labels,harmonics=4):
    """Original dynamic64/H4 reset trace and Pi_parent-Pi_child readout.

    Fixed affine offset has B derivative zero at held geometry. At is NOT
    silently included in the dynamic trace; its original Gauss stays audited.
    """
    ids=np.asarray(value_permutation,int);labels=gauge_labels;nh=int(harmonics)
    dynamic=[i for i,j in enumerate(ids)if j<80 and labels[j]['field']!='A_tau']
    H=[i for i,j in enumerate(ids)if j>=80]
    if len(dynamic)!=64 or len(H)!=4:raise ValueError('all original dynamic64/H4 rows required')
    selector=lambda rows:(np.array(rows)[:,None]*nh+np.arange(nh)).ravel()
    g,h=selector(dynamic),selector(H)
    return dict(gauge_trace=child['total_field'][g]-parent['total_field'][g],
        Higgs_trace=child['total_field'][h]-parent['total_field'][h],
        gauge_temporal_dual=parent['canonical_momentum'][g]-child['canonical_momentum'][g],
        Higgs_temporal_dual=parent['canonical_momentum'][h]-child['canonical_momentum'][h],
        original_dynamic_field_indices=g,original_Higgs_field_indices=h)
