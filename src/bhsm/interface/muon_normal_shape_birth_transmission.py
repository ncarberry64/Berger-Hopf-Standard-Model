"""Named conditional canonical transmission of a complete action source.

Every row is supplied by the caller.  The selected rows are the endpoint
trace/field-dual equations; held coordinates are declared controls, never
an exterior or an energy/formation selection.  Original full images and
source/frame reactions remain separate from the square solve.
"""
import numpy as np
from flint import acb_mat,ctx
from .muon_stored_admission_correction import _matrix,_mid,_upper
from .muon_stored_fiber_canonical_tangent import _cat,_rows,_split


def canonical_source_transmission(H,F,E,Jparent,Jchild,parent_high,parent_low,
        source_high,source_low,direct_high,direct_low,extra_rows,selected_rows,
        held_coordinates,held_values,*,precision_bits=192):
    H,F,E,Jp,Jc=map(lambda a:np.asarray(a,complex),(H,F,E,Jparent,Jchild))
    n=E.shape[0]//2;d=len(H)-n;nf=len(F);nu=E.shape[1]
    C=np.asarray(held_coordinates,complex);ids=np.asarray(selected_rows,int)
    if H.shape!=(n+d,n+d)or F.shape!=(nf,d)or Jc.shape[1]!=len(H)or Jp.shape!=Jc.shape or C.shape[1]!=nu or len(ids)+len(C)!=nu:
        raise ValueError('all selected action rows plus explicit held coordinates must close the canonical chart')
    old=ctx.prec;ctx.prec=precision_bits
    try:
        HH,FF,EE=_matrix(H),_matrix(F),_matrix(E)
        p=_matrix(parent_high)+_matrix(parent_low);g=_matrix(source_high)+_matrix(source_low)
        b=_matrix(direct_high)+_matrix(direct_low)
        K=_matrix(np.block([[H[n:,n:],F.T],[F,np.zeros((nf,nf),complex)]]))
        # True constitutive lift, including every algebraic row and source.
        rhs_map=_cat(-_matrix(H[n:,:n])*_rows(EE,0,n)+_cat(_rows(EE,n,2*n),acb_mat(d-n,nu)),acb_mat(nf,nu))
        zmap=K.solve(rhs_map);R=_cat(_rows(EE,0,n),_rows(zmap,0,d))
        offset=K.solve(_cat(-_rows(g,n,len(H)),acb_mat(nf,1)))
        s=_cat(acb_mat(n,1),_rows(offset,0,d))
        Aall=_matrix(Jc)*R
        r0=_matrix(Jp)*p+_matrix(Jc)*(b+s)+_matrix(extra_rows)
        AA=acb_mat([[Aall[i,j]for j in range(nu)]for i in ids])
        rr=acb_mat([[r0[i,0]]for i in ids])
        system=_cat(AA,_matrix(C));rhs=_cat(-rr,_matrix(held_values))
        u=system.solve(rhs);Q=EE*u;eta=R*u+s;total=b+eta
        allrows=_matrix(Jp)*p+_matrix(Jc)*total+_matrix(extra_rows)
        z=zmap*u+offset
        target=_cat(_rows(Q,n,2*n),acb_mat(d-n,1))
        original=_matrix(H[n:])*eta+_rows(g,n,len(H))-target
        reaction=_matrix(F.T)*_rows(z,d,d+nf)
        targets=acb_mat(nu,1);targets[0,0]=1
        adj=system.transpose().solve(targets)
        pairing=adj.transpose()*rhs-targets.transpose()*u
        arrays={}
        for key,value in(dict(canonical_coordinates=u,effective_canonical=Q,induced_phase=eta,total_phase=total,
            constitutive_action_embedding=R,constitutive_source_offset=s,source_frame_reactions=_rows(z,d,d+nf),
            all_original_state_and_known_source_rows=allrows,original_constitutive_rows=original,
            frame_reaction_rows=reaction,selected_original_rows=acb_mat([[allrows[i,0]]for i in ids]),
            held_coordinate_rows=_matrix(C)*u-_matrix(held_values),square_operator=system,square_rhs=rhs,
            initial_parent_phase=p,source=g,direct_phase=b).items()):
            if key in('square_operator','constitutive_action_embedding'):
                arrays[key]=_mid(value)
            else:
                arrays[key+'_high'],arrays[key+'_low']=_split(value)
        return dict(arrays=arrays,selected_rows_upper=_upper(AA*u+rr),held_rows_upper=_upper(_matrix(C)*u-_matrix(held_values)),
            original_constitutive_upper=_upper(original),frame_reaction_upper=_upper(reaction),
            original_plus_reaction_upper=_upper(original+reaction),square_residual_upper=_upper(system*u-rhs),
            transpose_rows_upper=_upper(system.transpose()*adj-targets),literal_pairing_upper=_upper(pairing),
            all_original_image_upper=_upper(allrows),conditional_named_coordinate_completion_only=True)
    finally:ctx.prec=old
