"""Literal current sources on the original whole chronological field graph.

The two retained FE2 functions are computational current tests, continued
from their original source cell. They do not become extra field unknowns.
The field chart is material Lorentz At, so its vertex -iG/N is not rotated
again. Harmonic U and U* are the right and literal-transpose source maps;
neither the continued vertex nor a source coefficient is conjugated.
"""
from __future__ import annotations
import numpy as np


def literal_point_current_sources(vertices, temporal_values, right_lift, literal_left_lift):
    """Return all288 literal right/left columns per angular spectator.

    Columns are (external C6, owned FE2 test, internal C6, real n1).
    The left vertex is the literal reversed matrix placement V[i,f].
    The current contains no A-sharp numerator or fermion inverse.
    """
    V,b,R,L=(np.asarray(x,complex)for x in(vertices,temporal_values,right_lift,literal_left_lift))
    if (V.shape!=(24,6,6)or b.shape!=(2,)or R.ndim!=2 or R.shape[1]!=96
            or L.shape!=R.shape or any(not np.isfinite(x).all()for x in(V,b,R,L))):
        raise ValueError('complete original wall24/C6/n1 and two owned test functions required')
    r=np.einsum('ach,cfi->aifh',R.reshape(-1,24,4),V,optimize=True)
    l=np.einsum('ach,cif->aifh',L.reshape(-1,24,4),V,optimize=True)
    r=np.einsum('aifh,t->aitfh',r,b).reshape(len(R),288)
    l=np.einsum('aifh,t->aitfh',l,b).reshape(len(L),288)
    return dict(literal_right_source=r,literal_left_transpose_source=l,
        column_shape=np.array([6,2,6,4]),source_column_count=288,
        source_coefficients_or_vertex_conjugated=False,A_sharp_inserted_in_literal_source=False)


def add_literal_point_source(rhs,initial_reaction,point,point_source,*,columns):
    """Integrate one current point on ALL original nodes, including corners.

    Initial node0 is held in the field solve and exported as a source
    reaction. The free-final source is retained. No spatial/tent clipping,
    final Dirichlet deletion, or corner replacement is made.
    """
    out=np.asarray(rhs);reaction=np.asarray(initial_reaction);S=np.asarray(point_source,complex)
    ix=np.asarray(columns)
    if (out.ndim!=3 or out.shape[1]<len(S)or reaction.shape!=(out.shape[1],out.shape[2])
        or S.shape!=(168,288)or ix.ndim!=1 or not np.issubdtype(ix.dtype,np.integer)
        or len(ix)!=out.shape[2]or np.any(ix<0)or np.any(ix>=288)):
        raise ValueError('original176-row chronological source and explicit source column subset required')
    measure=complex(point['measure'])
    for node,value,derivative in point['rows']:
        j=complex(node)
        if j.imag or j.real!=int(j.real)or not 0<=j.real<=len(out):
            raise ValueError('all exact original node labels required')
        row=measure*complex(value)*S[:,ix]
        if j.real==0:reaction[:168]+=row
        else:out[int(j.real)-1,:168]+=row
    return out,reaction


def source_column_indices(*,external_spin=None):
    """An exact index restriction; no rank/SVD deletion of internal tests."""
    if external_spin is None:return np.arange(288)
    if type(external_spin)is not int or not 0<=external_spin<6:
        raise ValueError('one explicit complete C6 external input is required')
    return np.arange(external_spin*48,(external_spin+1)*48)
