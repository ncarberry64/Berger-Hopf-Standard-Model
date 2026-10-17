"""Forced original canonical Jacobi action with complete shape source rows.

The stored source is prescribed. Exact-stored high/low solves retain every
Legendre/Gauss/frame row, without upgrading action or physical accuracy.
Effective p includes g_v; original Pi=p-g_v is separately exported.
"""
import numpy as np
from flint import acb,acb_mat,ctx
from .muon_stored_admission_correction import _matrix,_mid,_upper
from .muon_stored_fiber_canonical_tangent import _rows,_cat,_split


def forced_original_canonical_jacobi(H,step,F,initial_high,initial_low,source,*,precision_bits=192):
    """J dz+[0,-h g_x,g_v,g_y]+frame_reaction=0, all rows retained."""
    H,F,g=np.asarray(H,complex),np.asarray(F,complex),np.asarray(source,complex)
    hi,lo=np.asarray(initial_high,complex),np.asarray(initial_low,complex);n=hi.shape[0]//2;m=len(H)-2*n;nf=len(F);nc=hi.shape[1];d=3*n+m
    if hi.ndim!=2 or lo.shape!=hi.shape or H.shape!=(2*n+m,)*2 or F.shape!=(nf,n+m)or g.shape!=(2*n+m,)or m<1 or not step:
        raise ValueError('same complete canonical pair/source/Hessian and original frames required')
    old=ctx.prec;ctx.prec=precision_bits
    try:
        hs=acb(complex(step).real,complex(step).imag);HH,gg,FF=_matrix(H),_matrix(g),_matrix(F)
        Q=_matrix(hi)+_matrix(lo);xi,pi=_rows(Q,0,n),_rows(Q,n,2*n)
        K=acb_mat(d+nf,d+nf)
        for i in range(n):K[i,i]=1;K[i,2*n+i]=-hs;K[n+i,n+i]=1;K[2*n+i,n+i]=-.5
        for i in range(n):
            for j in range(n):K[n+i,j]=-hs*HH[i,j]/2;K[2*n+i,j]=HH[n+i,j]/2
            for j in range(n+m):K[n+i,2*n+j]=-hs*HH[i,n+j];K[2*n+i,2*n+j]=HH[n+i,n+j]
        for i in range(m):
            for j in range(n):K[3*n+i,j]=HH[2*n+i,j]/2
            for j in range(n+m):K[3*n+i,2*n+j]=HH[2*n+i,n+j]
        for i in range(nf):
            for j in range(n+m):K[2*n+j,d+i]=FF[i,j];K[d+i,2*n+j]=FF[i,j]
        # One supplied source column; a batch canonical input may share it.
        repeat=lambda a:acb_mat([[a[i,0]for _ in range(nc)]for i in range(a.nrows())])
        gx,gv,gy=(repeat(_rows(gg,a,b))for a,b in((0,n),(n,2*n),(2*n,len(g))))
        rhs=_cat(xi,pi+hs*_matrix(H[:n,:n])*xi/2+hs*gx,
            pi/2-_matrix(H[n:2*n,:n])*xi/2-gv,-_matrix(H[2*n:,:n])*xi/2-gy,acb_mat(nf,nc))
        z=K.solve(rhs);zh,zl=_split(z);z=_matrix(zh)+_matrix(zl)
        xf,pf,phase=_rows(z,0,n),_rows(z,n,2*n),_rows(z,2*n,d)
        eta=_cat((xi+xf)/2,phase);cot=HH*eta+repeat(gg)
        original=_cat(xf-xi-hs*_rows(phase,0,n),pf-pi-hs*_rows(cot,0,n),
            _rows(cot,n,2*n)-(pi+pf)/2,_rows(cot,2*n,len(H)))
        reaction=acb_mat(d,nc);rp=FF.transpose()*_rows(z,d,d+nf)
        for i in range(n+m):
            for j in range(nc):reaction[2*n+i,j]=rp[i,j]
        targets=acb_mat(d+nf,2*n)
        for i in range(2*n):targets[i,i]=1
        left=K.transpose().solve(targets);pairing=left.transpose()*rhs-_rows(z,0,2*n)
        qh,ql=_split(_cat(xf,pf));eh,el=_split(eta);ch,cl=_split(HH*eta)
        return dict(effective_canonical_final_high=qh,effective_canonical_final_low=ql,
            induced_stage_direction_high=eh,induced_stage_direction_low=el,
            original_action_cotangent_first_high=ch,original_action_cotangent_first_low=cl,
            solution_high=zh,solution_low=zl,source=np.array(g),
            original_forced_rows=_mid(original),frame_reaction_rows=_mid(reaction),framed_rows=_mid(K*z-rhs),
            original_forced_rows_upper=_upper(original),frame_reaction_rows_upper=_upper(reaction),framed_rows_upper=_upper(K*z-rhs),
            original_plus_reaction_assembly_upper=_upper(original+reaction-_rows(K*z-rhs,0,d)),
            literal_transpose_rows_upper=_upper(K.transpose()*left-targets),literal_pairing_upper=_upper(pairing),
            high_low_exact_stored_matrix_representation_only=True)
    finally:ctx.prec=old


def source_complete_true_face(H,F,effective_canonical_high,effective_canonical_low,source,rate_conormal,*,precision_bits=192):
    """Reconstitute v/y and pull back the FULL rate covector plus offset."""
    H,F,g,B=map(lambda a:np.asarray(a,complex),(H,F,source,rate_conormal))
    hi,lo=np.asarray(effective_canonical_high,complex),np.asarray(effective_canonical_low,complex);n=hi.shape[0]//2;d=len(H)-n;nf=len(F);nc=hi.shape[1]
    if lo.shape!=hi.shape or H.shape!=(n+d,)*2 or F.shape!=(nf,d)or g.shape!=(len(H),)or B.shape!=g.shape:
        raise ValueError('source-complete true-face action and full x/v/y conormal required')
    old=ctx.prec;ctx.prec=precision_bits
    try:
        Q=_matrix(hi)+_matrix(lo);x,p=_rows(Q,0,n),_rows(Q,n,2*n);gg=_matrix(g)
        repeat=lambda a:acb_mat([[a[i,0]for _ in range(nc)]for i in range(a.nrows())])
        target=_cat(p,acb_mat(d-n,nc));src=repeat(_rows(gg,n,len(g)))
        rhs=_cat(target-_matrix(H[n:,:n])*x-src,acb_mat(nf,nc))
        K=_matrix(np.block([[H[n:,n:],F.T],[F,np.zeros((nf,nf),complex)]]))
        z=K.solve(rhs);zh,zl=_split(z);z=_matrix(zh)+_matrix(zl)
        eta=_cat(x,_rows(z,0,d));eh,el=_split(eta)
        original=_matrix(H[n:])*eta+src-target;reaction=_matrix(F.T)*_rows(z,d,d+nf)
        # Literal dual includes ALL rate_v and rate_y contacts.
        bb=_matrix(B);w=K.transpose().solve(_cat(_rows(bb,n,len(B)),acb_mat(nf,1)))
        wp=_rows(w,0,d)
        canonical_covector=_cat(_rows(bb,0,n)-_matrix(H[n:,:n]).transpose()*wp,_rows(wp,0,n))
        offset=-wp.transpose()*_rows(gg,n,len(g))
        work=bb.transpose()*eta;decomposed=canonical_covector.transpose()*Q+repeat(offset)
        ph,pl=_split(_matrix(H[n:2*n])*eta)
        shifted_h,shifted_l=_split(p-repeat(_rows(gg,n,2*n)))
        return dict(induced_phase_high=eh,induced_phase_low=el,original_Pi_first_high=ph,original_Pi_first_low=pl,
            effective_p_minus_g_v_high=shifted_h,effective_p_minus_g_v_low=shifted_l,
            original_forced146_rows=_mid(original),frame_reaction_rows=_mid(reaction),framed_rows=_mid(K*z-rhs),
            full_rate_conormal=B,source_complete_canonical_rate_covector=_mid(canonical_covector)[:,0],
            rate_source_offset_contact=_mid(offset)[0,0],complete_rate_work=_mid(work),
            full_rate_work_decomposition_rows=_mid(work-decomposed),
            original_forced_rows_upper=_upper(original),frame_reaction_rows_upper=_upper(reaction),framed_rows_upper=_upper(K*z-rhs),
            full_rate_work_decomposition_upper=_upper(work-decomposed),
            original_Pi_equals_effective_p_minus_g_v_minus_velocity_frame_reaction=True,full_x_v_y_rate_covector_retained=True)
    finally:ctx.prec=old
