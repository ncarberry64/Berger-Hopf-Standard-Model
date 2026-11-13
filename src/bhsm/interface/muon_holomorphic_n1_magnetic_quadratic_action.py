"""All supplied coefficient and both response slots of a signed field action."""
from __future__ import annotations
import numpy as np


def signed_magnetic_quadratic_source_motion(forms,forms_first,field,coordinate_rate,field_first,coordinate_rate_first):
    """Differentiate .5 B_a.T Forms B_b, with independent literal slots.

    The source columns (including high/low) are never conjugated or combined.
    Geometry/profile/coframe/H contacts already belong to forms_first; the
    prescribed magnetic source and induced response belong to field_first.
    Numerical integration/time-face motion is an external caller operation.
    """
    f,ft,df,dft=[np.asarray(x,complex)for x in(field,coordinate_rate,field_first,coordinate_rate_first)]
    if f.ndim!=2 or ft.shape!=f.shape or df.ndim!=3 or df.shape[1:]!=f.shape or dft.shape!=df.shape:
        raise ValueError('same full field/value-rate and independent source columns required')
    n=len(f);k=len(df);result={}
    for name,left,right,dleft,dright in zip(('K','B_forward','B_reverse','M'),
            (f,f,ft,ft),(f,ft,f,ft),(df,df,dft,dft),(df,dft,df,dft)):
        F=np.asarray(forms[name],complex);dF=np.asarray(forms_first[name],complex)
        if F.shape!=(n,n)or dF.shape!=(k,n,n):raise ValueError('same complete signed action form and source first required')
        result['base_'+name]=.5*np.einsum('ia,ij,jb->ab',left,F,right,optimize=True)
        result['coefficient_motion_'+name]=.5*np.einsum('ia,sij,jb->sab',left,dF,right,optimize=True)
        result['left_response_motion_'+name]=.5*np.einsum('sia,ij,jb->sab',dleft,F,right,optimize=True)
        result['right_response_motion_'+name]=.5*np.einsum('ia,ij,sjb->sab',left,F,dright,optimize=True)
        result['total_first_'+name]=sum(result[pre+name]for pre in('coefficient_motion_','left_response_motion_','right_response_motion_'))
    for pre in('base_','coefficient_motion_','left_response_motion_','right_response_motion_','total_first_'):
        result[pre+'total']=sum(result[pre+n]for n in('K','B_forward','B_reverse','M'))
    return result
