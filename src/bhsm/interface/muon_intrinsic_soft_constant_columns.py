"""The matched constant-input half of the image-domain soft current graph."""
from __future__ import annotations
import numpy as np
from .muon_intrinsic_soft_current_columns import _vertices


def constant_input_image_data(tangent_data,mass_vertices):
    """Reuse the SAME base and Hodd/Heven domain for n0 -> n1.

    The two internal parity roles are reversed.  Constant multiplication
    is an exact identity between the corresponding inherited harmonics;
    there is no fitted Gaunt map or independently chosen state.
    """
    d=tangent_data;M=np.asarray(mass_vertices)
    if M.shape!=(4,6,6):raise ValueError('same four real fixed-Y vertices required')
    G=d['angular']['gaunts'];result=dict(length=d['length'],lapse=d['lapse'],angular=d['angular'])
    for destination,source in (('odd','even'),('even','odd')):
        for p in ('A','P','p','V'):result[p+'_'+destination]=d[p+'_'+source]
    ho=len(d['angular']['labels']['Hodd']);he=len(d['angular']['labels']['Heven'])
    fo=len(d['angular']['labels']['Fodd']);fe=len(d['angular']['labels']['Feven'])
    identity_odd=np.eye(fo,ho)[:,:,None];identity_even=np.eye(fe,he)[:,:,None]
    result.update(left_odd=_vertices(G['right_even'],M),right_even=_vertices(identity_odd,M),
        left_even=_vertices(G['right_odd'],M),right_odd=_vertices(identity_even,M),
        Xi=d['Xadj'].conj().transpose(0,2,1),Xadj=d['Xi'].conj().transpose(0,2,1))
    result['square_left']=result['A_odd'].conj().T@result['Xi']
    result['square_right']=result['Xadj']@result['A_even']
    return result
