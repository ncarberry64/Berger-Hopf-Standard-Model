"""Action-owned local coefficient germs on the restored corner graph."""
from __future__ import annotations
import numpy as np
from scipy.integrate import solve_ivp
from .muon_continued_action_reality import action_reality_coefficient
from .muon_euclidean_angular_weak_action import euclidean_open_action_vertices
from .muon_piecewise_euclidean_action import FAMILY_INDICES


def restored_clifford_node_application(phase,anchor,offset,*,family,
        measure,right_clock,reflected_clock,rows,offset_sharp=None):
    z=complex(offset);zs=z.conjugate()if offset_sharp is None else complex(offset_sharp)
    a=action_reality_coefficient(phase,float(anchor),z)
    b=action_reality_coefficient(phase,float(anchor),zs)
    fi=FAMILY_INDICES[family]
    V=euclidean_open_action_vertices(a['geometry']['R4'],a['geometry']['N'],family=family)['vertices']
    Vs=euclidean_open_action_vertices(b['geometry']['R4'],b['geometry']['N'],family=family)['vertices']
    return dict(H=a['Hcan'][np.ix_(fi,fi)],Hsharp=b['Hcan'][np.ix_(fi,fi)],
        R=a['geometry']['R4'],Rsharp=b['geometry']['R4'],N=a['geometry']['N'],Nsharp=b['geometry']['N'],
        vertices=V,vertices_sharp=Vs,rows=rows,measure=measure,right_clock=right_clock,
        reflected_clock=reflected_clock,anchor=float(anchor),offset=z,offset_sharp=zs,
        raw_fields=a['raw'],raw_fields_sharp=b['raw'])


def restored_clifford_local_germ(phase,anchor,offset,*,family,part,
        coordinate_slope=None,offset_sharp=None):
    """Return a centered local weak-action sampler and exact clock convention.

    Cell parameter s is proper Euclidean time: its inverse coframe ODE is
    integrated on both independent coefficient branches. Connector s is
    the original segment parameter and t'=coordinate_slope. The measure
    density stays 1 or w respectively, rather than sqrt(w*w_sharp).
    Independent field source coefficients are never conjugated.
    """
    if part not in(0,1,2):raise ValueError('actual cell or connector leg required')
    z0=complex(offset);zs0=z0.conjugate()if offset_sharp is None else complex(offset_sharp)
    slope=None if coordinate_slope is None else complex(coordinate_slope)
    if part!=0 and(slope is None or slope==0):raise ValueError('the actual nonzero connector slope is required')
    def sample(ds=0.):
        delta=float(ds)
        if part==0:
            def integrate(z,sign):
                if delta==0:return z
                def rhs(s,y):
                    N=action_reality_coefficient(phase,float(anchor),y[0])['geometry']['N']
                    return np.array([sign*1j/N])
                r=solve_ivp(rhs,(0,delta),[z],rtol=1e-12,atol=1e-18,max_step=abs(delta)/2)
                if not r.success:raise ArithmeticError(r.message)
                return r.y[0,-1]
            z,zs=integrate(z0,-1),integrate(zs0,1);w=ws=density=1.
        else:
            z,zs=z0+slope*delta,zs0+slope.conjugate()*delta
            N=action_reality_coefficient(phase,float(anchor),z)['geometry']['N']
            Ns=action_reality_coefficient(phase,float(anchor),zs)['geometry']['N']
            w=1j*N*slope;ws=-1j*Ns*slope.conjugate();density=w
        return restored_clifford_node_application(phase,anchor,z,family=family,
            measure=density,right_clock=w,reflected_clock=ws,rows=(),offset_sharp=zs)
    return dict(sample=sample,measure_density='1 in proper cells; original holomorphic w in connector legs',
        source_coordinates='common material Lorentz At/Ar/Ai and realified H, coefficient variables not reflected',
        reflected_clock_phase='-i N_sharp conjugate(t_s)',
        cell_inverse_coframe_ODE_retained=part==0)


def original_n0_wall_coordinate_map(original_wall_map,value_permutation):
    """Recover the exact original84 n0 wall map from its common n1 lift."""
    P=np.asarray(original_wall_map,complex);pe=np.asarray(value_permutation,int)
    if P.shape!=(96,336)or pe.shape!=(336,):raise ValueError('complete original n1 wall coordinate representation required')
    cols=np.flatnonzero(pe%4==0);P0=P[np.ix_(np.arange(24)*4,cols)]
    if len(cols)!=84:raise ValueError('all84 original n0 fields required')
    for h in range(4):
        at=np.flatnonzero(pe%4==h)
        if not np.array_equal(P[np.ix_(np.arange(24)*4+h,at)],P0):
            raise ValueError('the action-owned wall map does not factor its harmonic identity')
        others=np.setdiff1d(np.arange(336),at)
        if np.any(P[np.ix_(np.arange(24)*4+h,others)]!=0):
            raise ValueError('the original wall map mixes the claimed homogeneous angular chart')
    return dict(wall_map=P0,original_coordinate_permutation=pe[cols]//4,
        original_At_count=16,original_field_count=84,
        scalar_driving_current_removed_does_not_remove_induced_H=True,
        pointwise_common_material_At_coordinate=True)
