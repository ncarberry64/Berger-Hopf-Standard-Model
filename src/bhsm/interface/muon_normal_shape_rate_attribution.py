"""One bounded stored-rate attribution, preserving all original action rows."""
import numpy as np
from flint import acb_mat,ctx
from .muon_stored_admission_correction import bounded_stored_admission_correction,_matrix,_mid,_upper
from .muon_stored_fiber_canonical_tangent import _rows,_cat,_split


def bounded_normal_shape_rate_attribution(H,G,fixed_velocity,explicit_clock,F,
        stored_rhs,initial_solution,*,precision_bits=192):
    """Compare fixed-rhs correction with exact product assembly of same data.

    The second result retains a low rhs term; its original target G_x and
    source clock are unchanged. No higher-precision action is evaluated.
    """
    H,G=np.asarray(H,complex),np.asarray(G,complex);v=np.asarray(fixed_velocity,complex)
    clock=np.asarray(explicit_clock,complex);F=np.asarray(F,complex);n=len(v);d=len(H)-n;nf=len(F)
    K=np.block([[H[n:,n:],F.T],[F,np.zeros((nf,nf),complex)]])
    target=np.r_[G[:n],np.zeros(d-n,complex)]
    A=bounded_stored_admission_correction(K,stored_rhs,initial_solution,d,
        action_rows=H[n:],fixed_x=v,source_rows=clock[n:],target_rows=target,
        correction_count=1,precision_bits=precision_bits)
    old=ctx.prec;ctx.prec=precision_bits
    try:
        rhs=_cat(_matrix(target)-_matrix(H[n:,:n])*_matrix(v)-_matrix(clock[n:]),acb_mat(nf,1))
        z=_matrix(K).solve(rhs);zh,zl=_split(z);zh=zh[:,0];zl=zl[:,0];pair=_matrix(zh)+_matrix(zl)
        phase=_rows(pair,0,d);reaction=_matrix(F.T)*_rows(pair,d,d+nf)
        direction=_cat(_matrix(v),phase)
        original=_matrix(H[n:])*direction+_matrix(clock[n:])-_matrix(target)
        rrh,rrl=_split(rhs)
        return dict(fixed_rhs=A,exact_assembly_solution_high=zh,exact_assembly_solution_low=zl,
            exact_assembly_rhs_high=rrh[:,0],exact_assembly_rhs_low=rrl[:,0],
            exact_assembly_original_rows=_mid(original)[:,0],exact_assembly_frame_reaction_rows=_mid(reaction)[:,0],
            exact_assembly_original_upper=_upper(original),exact_assembly_frame_reaction_upper=_upper(reaction),
            exact_assembly_bordered_upper=_upper(_matrix(K)*pair-rhs),
            fixed_target_and_clock_preserved=True,
            exact_assembly_minus_stored_rhs=_mid(rhs-_matrix(stored_rhs))[:,0])
    finally:ctx.prec=old


def exact_stored_shape_bulk_pairing(H,G,Ha,Ga,clock,rate_high,rate_low,
        shape_coefficient,shape_gradient,shape_Hessian,phase_high,phase_low,
        *,normal_position=289,normal_velocity=395,precision_bits=192):
    """Reapply source and area with corrected rate high+low, same phase test.

    The equality g_eta-Dt g_rate=H b+(L_s-DtPi_s)Da is exact for these
    supplied coefficients. All temporal boundary g_rate tests are returned.
    """
    old=ctx.prec;ctx.prec=precision_bits
    try:
        HH,gg,AA,ga=map(_matrix,(H,G,Ha,Ga));r=_matrix(rate_high)+_matrix(rate_low)
        da=_matrix(shape_gradient);dd=_matrix(shape_Hessian)
        u=_matrix(phase_high)+_matrix(phase_low);d=len(G);s=int(normal_position);v=int(normal_velocity)
        b=acb_mat(d,1);b[s,0]=complex(shape_coefficient);b[v,0]=(da.transpose()*r)[0,0]
        results={}
        for name,M,g,t in (('base',HH,gg,_matrix(clock)),('area',AA,ga,acb_mat(d,1))):
            Gt=M*r+t;equation=g[s,0]-Gt[v,0]
            bulk=M*b+equation*da;boundary=g[v,0]*da
            val=bulk.transpose()*u;face=boundary.transpose()*u
            vh,vl=_split(val);fh,fl=_split(face)
            results[name]=dict(bulk_pairing_high=vh,bulk_pairing_low=vl,
                boundary_pairing_high=fh,boundary_pairing_low=fl,
                normal_EL_residual=_mid(acb_mat([[equation]]))[0,0],
                bulk_source=_mid(bulk)[:,0],boundary_source=_mid(boundary)[:,0])
        return results
    finally:ctx.prec=old
