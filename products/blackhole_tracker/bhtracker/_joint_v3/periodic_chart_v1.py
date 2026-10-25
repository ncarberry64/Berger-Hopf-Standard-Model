"""Numerical covering coordinates only; physical angular circle is unchanged."""
import math
import numpy as np

def canonical_angle(value):
    if isinstance(value,(bool,np.bool_)) or not math.isfinite(value):
        raise ValueError('Finite real angle required')
    return math.remainder(float(value),2*math.pi)

def native_from_chart(state,center,lower,upper):
    values=np.asarray(state)
    if values.dtype.kind not in 'iuf' or values.ndim!=1 or len(values)<4 or not np.isfinite(values).all():
        raise ValueError('Finite real chart vector required')
    x=np.array(values,dtype=float,copy=True)
    for j in range(len(x)):
        if j!=3 and not lower[j]<=x[j]<=upper[j]:raise ValueError('Nonperiodic coordinate outside unchanged domain')
    x[3]=canonical_angle(float(center)+x[3])
    if not lower[3]<=x[3]<=upper[3]:raise ValueError('Canonical angle outside original physical representation')
    return x

def chart_seed(seed):
    x=np.array(seed,dtype=float,copy=True);center=float(x[3]);x[3]=0.
    return x,center
