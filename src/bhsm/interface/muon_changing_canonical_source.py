"""Source derivative of the actual nonlinear canonical midpoint application.

The callback has already evaluated the action at the changing stage. Sources
are action gradient directions at that same stage, before field restriction.
Two-term coefficient solutions prevent a rounded state from silently losing
the admitted fixed-matrix residual. Acb bounds cover supplied coefficients.
"""
from __future__ import annotations
import numpy as np
from flint import acb, acb_mat, ctx
from .muon_stored_admission_correction import _matrix, _mid, _upper


def split_action(matrix, high, low, *, precision_bits=192):
    """Contract supplied matrix with both terms of a retained source direction."""
    old=ctx.prec;ctx.prec=precision_bits
    try:
        z=_matrix(matrix)*(_matrix(high)+_matrix(low));hi=_mid(z)[:,0]
        return hi,_mid(z-_matrix(hi))[:,0]
    finally:ctx.prec=old


def constitutive_source_two_term(H,dx,dp,g,gl,C,frame_value,*,dx_low,dp_low,
        frame_value_low,precision_bits=192):
    """Reassemble a source restriction without changing its x/Pi/frame data.

    An inherited source can change when its parent solution is corrected;
    that is a new action application, separate from a fixed-rhs check.
    """
    H=np.asarray(H,complex);n=len(dx);C=np.asarray(C,complex);d=len(H)-n
    K=np.block([[H[n:,n:],C.T],[C,np.zeros((len(C),len(C)),complex)]])
    old=ctx.prec;ctx.prec=precision_bits
    try:
        xx=_matrix(dx)+_matrix(dx_low);pp=_matrix(np.r_[dp,np.zeros(d-n)])+_matrix(np.r_[dp_low,np.zeros(d-n)])
        gg=_matrix(g)+_matrix(gl);rhs=pp-_matrix(H[n:,:n])*xx-acb_mat([[gg[i,0]]for i in range(n,len(H))])
        ff=_matrix(frame_value)+_matrix(frame_value_low)
        rr=acb_mat([[v[i,0]]for v in(rhs,ff)for i in range(v.nrows())]);KK=_matrix(K);z=KK.solve(rr)
        zh=_mid(z)[:,0];zl=_mid(z-_matrix(zh))[:,0];pair=_matrix(zh)+_matrix(zl)
        eta=acb_mat([[xx[i,0]]for i in range(n)]+[[pair[i,0]]for i in range(d)])
        eh=_mid(eta)[:,0];el=_mid(eta-_matrix(eh))[:,0]
        original=_matrix(H[n:,:])*eta+acb_mat([[gg[i,0]]for i in range(n,len(H))])-pp
        reaction=_matrix(C.T)*acb_mat([[pair[i,0]]for i in range(d,d+len(C))])
        return dict(direction_high=eh,direction_low=el,solution_high=zh,solution_low=zl,
            original_rows=_mid(original)[:,0],original_rows_upper=_upper(original),
            framed_rows_upper=_upper(KK*pair-rr),frame_reaction_rows_upper=_upper(reaction),
            canonical_momentum_target_high=np.asarray(dp),canonical_momentum_target_low=np.asarray(dp_low),
            source_gradient_high=np.asarray(g),source_gradient_low=np.asarray(gl))
    finally:ctx.prec=old


def changing_stage_source(base, delta_x, delta_p, source_high, source_low,
        frame, frame_value_high, frame_value_low, normal_covector, *,
        delta_x_low, delta_p_low, precision_bits=192):
    """Differentiate every original x/Pi/Legendre/Gauss row at a solved stage.

    All first data are explicit, including low terms and frame/source motion.
    This retained frame C is fixed; the moving literal gauge generators are
    audited by the producer. No birth/reset trace is a continuous bulk row.
    """
    a=base['application'];H=np.asarray(a['action']['hessian'],complex)
    dx=np.asarray(delta_x,complex);dp=np.asarray(delta_p,complex);n=len(dx)
    J=np.asarray(a['jacobian'],complex);C=np.asarray(frame,complex)
    g=np.asarray(source_high,complex);gl=np.asarray(source_low,complex)
    if (dp.shape!=dx.shape or H.shape!=(len(g),len(g)) or gl.shape!=g.shape
            or J.shape!=(len(g)+n,)*2 or C.shape[1]!=len(g)-n
            or np.asarray(normal_covector).shape!=(n,)):
        raise ValueError('same complete stage, original source and named frame required')
    h=complex(base['step']);nf=len(C);d=len(J)
    E=np.zeros((d,nf),complex);E[2*n:]=C.T
    F=np.zeros((nf,d),complex);F[:,2*n:]=C
    K=np.block([[J,E],[F,np.zeros((nf,nf),complex)]])
    old=ctx.prec;ctx.prec=int(precision_bits)
    try:
        xx=_matrix(dx)+_matrix(delta_x_low);pp=_matrix(dp)+_matrix(delta_p_low)
        gg=_matrix(g)+_matrix(gl);HH=_matrix(H)
        # These are the literal derivatives of the SAME midpoint equations.
        hx=_matrix(H[:n,:n])*xx/2
        hv=_matrix(H[n:2*n,:n])*xx/2
        hy=_matrix(H[2*n:,:n])*xx/2
        bv=pp/2-hv-acb_mat([[gg[i,0]]for i in range(n,2*n)])
        bp=pp+acb(h.real,h.imag)*(hx+acb_mat([[gg[i,0]]for i in range(n)]))
        by=-hy-acb_mat([[gg[i,0]]for i in range(2*n,len(g))])
        ft=_matrix(frame_value_high)+_matrix(frame_value_low)
        rhs=acb_mat([[v[i,0]]for v in (xx,bp,bv,by,ft)for i in range(v.nrows())])
        KK=_matrix(K);z=KK.solve(rhs)
        hi=_mid(z)[:,0];lo=_mid(z-_matrix(hi))[:,0]
        pair=_matrix(hi)+_matrix(lo)
        rr=KK*pair-rhs;reaction=(_matrix(E)*acb_mat([[pair[i,0]]for i in range(d,d+nf)])) if nf else acb_mat(d,1)
        assembled_original=acb_mat([[rr[i,0]]for i in range(d)])-reaction
        eta=acb_mat([[(xx[i,0]+pair[i,0])/2]for i in range(n)]
            +[[pair[i,0]]for i in range(2*n,d)])
        cot=HH*eta+gg
        hs=acb(h.real,h.imag)
        dxf=acb_mat([[pair[i,0]]for i in range(n)])
        dpf=acb_mat([[pair[i,0]]for i in range(n,2*n)])
        dv=acb_mat([[pair[i,0]]for i in range(2*n,3*n)])
        cx=acb_mat([[cot[i,0]]for i in range(n)])
        cv=acb_mat([[cot[i,0]]for i in range(n,2*n)])
        cy=acb_mat([[cot[i,0]]for i in range(2*n,len(g))])
        original=acb_mat([[v[i,0]]for v in(dxf-xx-hs*dv,dpf-pp-hs*cx,cv-(pp+dpf)/2,cy)for i in range(v.nrows())])
        initial=acb(h.real,h.imag)*acb_mat([[cot[i,0]]for i in range(n)])/2-acb_mat([[cot[i,0]]for i in range(n,2*n)])
        final=acb(h.real,h.imag)*acb_mat([[cot[i,0]]for i in range(n)])/2+acb_mat([[cot[i,0]]for i in range(n,2*n)])
        normal=_matrix(normal_covector).transpose()
        test=normal*acb_mat([[pair[i,0]]for i in range(n)])
        ell=np.zeros(d+nf,complex);ell[:n]=normal_covector
        left=KK.transpose().solve(_matrix(ell))
        dual=left.transpose()*rhs
        # Export the two-term stage FIELD direction, not only its coefficient test.
        eh=_mid(eta)[:,0];el=_mid(eta-_matrix(eh))[:,0]
        sh=_mid(cot)[:,0];sl=_mid(cot-_matrix(sh))[:,0]
        return dict(arrays=dict(stage_Hessian=H,stage_original_Jacobian=J,
            stage_bordered_operator=K,stage_rhs_high=_mid(rhs)[:,0],
            stage_rhs_low=_mid(rhs-_matrix(_mid(rhs)[:,0]))[:,0],
            stage_solution_high=hi,stage_solution_low=lo,
            stage_direction_high=eh,stage_direction_low=el,
            action_gradient_direction_high=sh,action_gradient_direction_low=sl,
            original_rows=_mid(original)[:,0],framed_rows=_mid(rr)[:,0],
            assembled_original_rows=_mid(assembled_original)[:,0],
            original_assembly_difference=_mid(original-assembled_original)[:,0],
            named_frame_reaction_rows=_mid(reaction)[:,0],
            source_gradient_high=g,source_gradient_low=gl,
            literal_transpose_solution_high=_mid(left)[:,0],
            literal_transpose_solution_low=_mid(left-_matrix(_mid(left)[:,0]))[:,0],
            initial_action_dual_high=_mid(initial)[:,0],final_action_dual_high=_mid(final)[:,0],
            delta_x_initial_high=dx,delta_x_initial_low=np.asarray(delta_x_low),
            delta_Pi_initial_high=dp,delta_Pi_initial_low=np.asarray(delta_p_low),
            proper_normal_covector=np.asarray(normal_covector)),
            original_rows_upper=_upper(original),framed_rows_upper=_upper(rr),
            original_assembly_difference_upper=_upper(original-assembled_original),
            frame_reaction_rows_upper=_upper(reaction),
            initial_action_dual_error_upper=_upper(initial+pp),
            final_action_dual_error_upper=_upper(final-acb_mat([[pair[i,0]]for i in range(n,2*n)])),
            transpose_rows_upper=_upper(KK.transpose()*left-_matrix(ell)),
            pairing_difference_upper=_upper(test-dual),normal_pairing=complex(_mid(test)[0,0]),
            precision_bits=precision_bits,all_original_rows_retained=True,
            reset_endpoint_rows_used_as_continuous_constraints=False,
            error_scope='exact supplied binary stage Hessian, Jacobian and two-term source solve; no action, stage truncation, domain or physical Pauli enclosure')
    finally:ctx.prec=old
