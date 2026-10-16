"""Literal causal profile/source applications on a saved action cell.

The inhomogeneous response has a zero response seed; the independent birth
Cauchy data enter through a separate homogeneous solution. Neither is a
condition on the exterior environment.
"""
import numpy as np
from flint import ctx,acb_mat
from .muon_stored_admission_correction import _matrix,_upper
from .muon_stored_fiber_canonical_tangent import _rows,_cat,_split
from .muon_fixed_source_forced_canonical import conditional_canonical_force_cell


def literal_retarded_profile_cell(Hcc,Hcp,Hpc,Hpp_source,profile_map,step,frames,
        source_high,source_low,response_high,response_low,
        homogeneous_high,homogeneous_low,*,precision_bits=192):
    """Apply only the supplied columns and retain every original cell row."""
    Hcc,Hcp,Hpc,Hpp,J,F=map(lambda z:np.asarray(z,complex),
        (Hcc,Hcp,Hpc,Hpp_source,profile_map,frames))
    old=ctx.prec;ctx.prec=int(precision_bits)
    try:
        S=_matrix(source_high)+_matrix(source_low)
        qi=_matrix(response_high)+_matrix(response_low)
        qh=_matrix(homogeneous_high)+_matrix(homogeneous_low)
        ns,nc=S.nrows(),S.ncols();n=qi.nrows()//2;d=len(Hcc)
        if (Hcp.shape!=(d,ns)or Hpc.shape!=(ns,d)or Hpp.shape!=(ns,ns)
                or J.shape!=(ns,ns)or qh.nrows()!=2*n or qh.ncols()!=nc):
            raise ValueError('same action cell, independent cross blocks and source columns required')
        g=_matrix(Hcp)*_matrix(J)*S
        gh,gl=_split(g);zh=np.zeros((2*n,nc),complex)
        rhi=conditional_canonical_force_cell(Hcc,step,F,response_high,response_low,gh,
            precision_bits=precision_bits)
        rlo=conditional_canonical_force_cell(Hcc,step,F,zh,zh,gl,precision_bits=precision_bits)
        hom=conditional_canonical_force_cell(Hcc,step,F,homogeneous_high,homogeneous_low,
            np.zeros((d,nc),complex),precision_bits=precision_bits)
        exact=lambda app,k:_matrix(app['arrays'][k+'_high'])+_matrix(app['arrays'][k+'_low'])
        er=exact(rhi,'stage')+exact(rlo,'stage');eh=exact(hom,'stage')
        qr=exact(rhi,'final_canonical')+exact(rlo,'final_canonical')
        qhnext=exact(hom,'final_canonical')
        h=_matrix([[step]])[0,0]
        def rows(q0,q1,eta,force):
            cot=_matrix(Hcc)*eta+force
            return _cat(_rows(q1,0,n)-_rows(q0,0,n)-h*_rows(eta,n,2*n),
                _rows(q1,n,2*n)-_rows(q0,n,2*n)-h*_rows(cot,0,n),
                _rows(cot,n,2*n)-(_rows(q0,n,2*n)+_rows(q1,n,2*n))/2,
                _rows(cot,2*n,d))
        ro=rows(qi,qr,er,g);ho=rows(qh,qhnext,eh,acb_mat(d,nc))
        direct=h*_matrix(J).transpose()*_matrix(Hpp)*_matrix(J)*S
        induced=h*_matrix(J).transpose()*_matrix(Hpc)*er
        birth=h*_matrix(J).transpose()*_matrix(Hpc)*eh
        values=dict(literal_Hcp_profile_source=g,retarded_stage=er,homogeneous_stage=eh,
            retarded_final_Cauchy=qr,homogeneous_final_Cauchy=qhnext,
            retarded_original_rows=ro,homogeneous_original_rows=ho,
            retarded_frame_rows=_matrix(F)*_rows(er,n,d),
            homogeneous_frame_rows=_matrix(F)*_rows(eh,n,d),
            retarded_reaction_rows=exact(rhi,'named_reaction_rows')+exact(rlo,'named_reaction_rows'),
            homogeneous_reaction_rows=exact(hom,'named_reaction_rows'),
            direct_profile_source_return=direct,retarded_profile_source_return=induced,
            homogeneous_profile_source_return=birth,total_profile_source_return=direct+induced+birth)
        out={}
        for name,value in values.items():out[name+'_high'],out[name+'_low']=_split(value)
        return dict(arrays=out,retarded_original_upper=_upper(ro),homogeneous_original_upper=_upper(ho),
            retarded_frame_upper=_upper(values['retarded_frame_rows']),
            homogeneous_frame_upper=_upper(values['homogeneous_frame_rows']),
            analytic_independent_Hpc_used=True,physical_outer_condition_selected=False)
    finally:ctx.prec=old
