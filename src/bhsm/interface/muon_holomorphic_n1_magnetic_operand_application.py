"""Literal contractions of reached signed magnetic third-action operands."""
from __future__ import annotations
import numpy as np


PLACEMENTS=('K','B_forward','B_reverse','M')


def homogeneous_original_field_trial(raw_direction,value_permutation,even_labels):
    """Map the supplied homogeneous original raw268 direction to even n0.

    The other nine even harmonics vanish ONLY for this supplied homogeneous
    trial. Algebraic At coordinate rates remain supplied but the action's
    Pt lift suppresses them; no dynamic/At or scalar row is removed here.
    High/low source columns are mapped separately without adding them.
    """
    d=np.asarray(raw_direction,complex);p=np.asarray(value_permutation,int)
    labels=np.asarray(even_labels)
    if (d.ndim!=2 or d.shape[0]!=268 or p.shape!=(84,)or
            sorted(p.tolist())!=list(range(84))or labels.shape!=(10,4)):
        raise ValueError('original raw268 source columns and complete original84/even0/2 labels required')
    zero=np.flatnonzero(labels[:,0].astype(int)==0)
    if len(zero)!=1:raise ValueError('one owned constant harmonic required')
    value=np.zeros((84,10,d.shape[1]),complex);rate=value.copy()
    value[:,zero[0]]=np.r_[d[100:180],d[260:264]][p]
    rate[:,zero[0]]=np.r_[d[180:260],d[264:268]][p]
    return dict(field=value.reshape(840,d.shape[1]),coordinate_rate=rate.reshape(840,d.shape[1]),
        n0_harmonic_index=int(zero[0]),other_even_trial_harmonics_zero_for_supplied_homogeneous_direction=True)


def signed_point_mixed_action(operands,even_field,even_coordinate_rate,odd_field,odd_coordinate_rate):
    """D3S[B_a, even trial_s, B_b], retaining every literal rate placement.

    Result arrays are [source_term, first_magnetic_axis, second_magnetic_axis].
    No left coefficient is conjugated. This is a classical source-action
    contraction, with geometry and coframe motion excluded from this partial.
    """
    e,et,o,ot=[np.asarray(x,complex)for x in(even_field,even_coordinate_rate,odd_field,odd_coordinate_rate)]
    if e.ndim!=2 or e.shape[0]!=840 or et.shape!=e.shape or o.shape!=(336,3)or ot.shape!=o.shape:
        raise ValueError('complete even840 source columns and odd336 magnetic fields/rates required')
    result={}
    for prefix in('','Maxwell_','intrinsic_','intrinsic_off_shell_DH_'):
        for name,left,right in zip(PLACEMENTS,(e,e,et,et),(o,ot,o,ot)):
            D=np.asarray(operands[prefix+'delta_'+name],complex)
            if D.shape!=(3,840,336):raise ValueError('all three source axes and complete rectangular action block required')
            result[prefix+name]=np.einsum('es,aef,fb->sab',left,D,right,optimize=True)
        result[prefix+'total']=sum(result[prefix+n]for n in PLACEMENTS)
    result['literal_magnetic_axis_symmetry_defect']=result['total']-result['total'].swapaxes(1,2)
    return result


def signed_two_trace_temporal_block(operands,shape_values,coordinate_shape_rates,measure):
    """Pull literal Lorentz D3 blocks to one original two-trace action cell.

    measure is the caller's literal action pullback (here saved -i dt weight).
    No absolute-square/reflection replacement or chosen boundary enters.
    Returns [left_trace2,right_trace2,magnetic_axis3,even840,odd336].
    """
    p,v=np.asarray(shape_values),np.asarray(coordinate_shape_rates)
    if p.shape!=(2,)or v.shape!=(2,):raise ValueError('two exact cell value/rate shape maps required')
    D=[np.asarray(operands['delta_'+n],complex)for n in PLACEMENTS]
    return complex(measure)*(p[:,None,None,None,None]*p[None,:,None,None,None]*D[0]
        +p[:,None,None,None,None]*v[None,:,None,None,None]*D[1]
        +v[:,None,None,None,None]*p[None,:,None,None,None]*D[2]
        +v[:,None,None,None,None]*v[None,:,None,None,None]*D[3])
