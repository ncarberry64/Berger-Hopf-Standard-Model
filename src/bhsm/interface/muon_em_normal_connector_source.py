"""Analytic continuation of the executed proper-clock wall field chart.

This retains the original FE2 coefficient variables and independent
reflected source placement.  It does not join distinct field traces by an
assigned identity, choose a new source, or supply a global exterior state.
"""
from __future__ import annotations
import numpy as np


def analytic_proper_clock(phase, anchor, offset, proper_center, *, reflected=False,
                          quadrature_order=12):
    """Continue the existing proper-clock germ by its action coframe.

    On the right, tau=tau_center+i*integral N dt.  On the independently
    reflected coordinate, tau_sharp=tau_center-i*integral N_sharp dt_sharp.
    No conjugation of the field coefficient variables accompanies this map.
    """
    from .muon_continued_action_reality import action_reality_coefficient
    z=complex(offset)
    q=quadrature_order
    if type(q) is not int or q<2 or not np.isfinite([float(anchor),float(proper_center)]).all():
        raise ValueError('an actual regular source-cell proper-clock chart is required')
    x,w=np.polynomial.legendre.leggauss(q)
    N=np.array([action_reality_coefficient(phase,float(anchor),z*(s+1)/2)['geometry']['N']for s in x])
    integral=z/2*np.dot(w,N)
    return complex(proper_center)+(-1j if reflected else 1j)*integral


def analytic_FE2_values(proper_time, total_proper_clock, source_element):
    """The fixed original field element, evaluated at a complex clock.

    The element is selected by the original real source-cell center before
    continuation.  Complex values are not clipped or used to select a
    different element, and the fixed initial right field trace stays zero.
    """
    total=float(total_proper_clock)
    if total<=0 or type(source_element) is not int or source_element not in (0,1):
        raise ValueError('the original positive clock and FE2 element are required')
    h=total/2;s=(complex(proper_time)-source_element*h)/h
    values=np.zeros(2,complex)
    if source_element==0:values[0]=s
    else:values[:]=(1-s,s)
    return values


def source_cell_field_chart(nodes, source_cell):
    """Recover the retained field chart from executed proper-node weights."""
    if type(source_cell) is not int or source_cell<0:
        raise ValueError('an actual integer source cell is required')
    at=np.flatnonzero(np.asarray(nodes['source_cell'])==source_cell)
    if not len(at):raise ValueError('the actual source cell is absent')
    w=np.asarray(nodes['weight'],float)[at]
    center=float(np.dot(w,np.asarray(nodes['proper_time'])[at])/sum(w))
    anchor=np.asarray(nodes['coordinate_anchor'])[at]
    if np.max(abs(anchor-anchor[0]))!=0:
        raise ValueError('one independently anchored source germ is required')
    total=float(nodes['total_proper_clock'])
    if not np.isfinite(total) or total <= 0:
        raise ValueError('the original positive field clock is required')
    element=min(int(center/total*2),1)
    node_elements=np.minimum((np.asarray(nodes['proper_time'])[at]/total*2).astype(int),1)
    if np.any(node_elements != element):
        raise ValueError('split a source germ at the original field FE corner before continuation')
    return dict(coordinate_anchor=float(anchor[0]),proper_center=center,
                total_proper_clock=total,source_element=element)


def connector_wall_source_coefficients(phase, chart, coordinate_time, *, family,
                                       quadrature_order=12):
    """Evaluate all192 wall coefficients on both original action branches.

    The temporal proper At field coordinate is converted by At_L=i*N*At_E
    separately on each branch.  Thus its vertex is G on both branches.
    The temporal FE coefficients remain complex bilinear variables; they
    are never conjugated.  Ar is retained as a field coordinate although
    the intrinsic Dirac pullback has zero direct Ar vertex in this chart.
    """
    from .muon_continued_action_reality import action_reality_coefficient
    from .muon_euclidean_angular_weak_action import euclidean_open_action_vertices
    if family not in (0,1,2):raise ValueError('the actual fixed lepton family is required')
    anchor=float(chart['coordinate_anchor']);z=complex(coordinate_time)-anchor
    right=action_reality_coefficient(phase,anchor,z)
    sharp=action_reality_coefficient(phase,anchor,z.conjugate())
    clocks=[];values=[];vertices=[]
    for app,offset,reflected in((right,z,False),(sharp,z.conjugate(),True)):
        tau=analytic_proper_clock(phase,anchor,offset,chart['proper_center'],
                                 reflected=reflected,quadrature_order=quadrature_order)
        basis=analytic_FE2_values(tau,chart['total_proper_clock'],chart['source_element'])
        N,R=app['geometry']['N'],app['geometry']['R4']
        v=euclidean_open_action_vertices(R,N,family=family)['vertices'].copy()
        v[:4]*=1j*N
        clocks.append(tau);values.append(basis);vertices.append(v)
    # Harmonic dependence remains a separate complete real Gaunt map.
    return dict(proper_clock=clocks[0],reflected_proper_clock=clocks[1],
        temporal_values=values[0],reflected_temporal_values=values[1],
        vertices=vertices[0],vertices_sharp=vertices[1],
        body=right['Hcan'],body_sharp=sharp['Hcan'],
        right_geometry=right['geometry'],reflected_geometry=sharp['geometry'],
        source_coordinate_order=('FE2 coefficient','wall field24','n1 harmonic4'),
        source_coefficient_count=192,source_coefficients_conjugated=False,
        proper_clock_recentered=False,initial_trace_zero_from_original_field_chart=True,
        physical_corner_field_trace_identity_imposed=False)


def apply_wall_source_branch(coefficients, wall_coefficients, *, reflected=False):
    """Apply the full intrinsic vertices to an actual wall coefficient set.

    Input has axes (FE2,wall24,n1harmonic4,direction).  This can be the
    original p/u wall lift or a source basis; no photon direction is selected.
    """
    w=np.asarray(wall_coefficients,complex)
    if w.ndim!=4 or w.shape[:3]!=(2,24,4) or not np.isfinite(w).all():
        raise ValueError('the complete original proper-clock wall coefficients are required')
    p=coefficients['reflected_temporal_values' if reflected else 'temporal_values']
    v=coefficients['vertices_sharp' if reflected else 'vertices']
    field=np.einsum('l,lchb->chb',p,w)
    return np.einsum('cij,chb->hijb',v,field,optimize=True)
