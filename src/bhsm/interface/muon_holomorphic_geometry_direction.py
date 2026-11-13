"""Exact first applications of the material coframe on complex branches.

The original real coordinates are complexified before differentiating.
Neither the Eulerian raw direction nor its embedding/clock contribution
is conjugated inside the coefficient map.  The opposite branch is a
separate application of the same formulas.
"""
from __future__ import annotations
import numpy as np
from .aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0
from .muon_continued_action_reality import _geometry,_higgs_mass_realified,_affine_raw
from .muon_parent_maxwell_full_weak import M
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation


class _First:
    def __init__(self,value,first):self.value=complex(value);self.first=np.asarray(first,complex)
    def _as(self,b):return b if isinstance(b,_First)else _First(b,np.zeros_like(self.first))
    def __add__(self,b):
        b=self._as(b);return _First(self.value+b.value,self.first+b.first)
    __radd__=__add__
    def __neg__(self):return _First(-self.value,-self.first)
    def __sub__(self,b):return self+-self._as(b)
    def __rsub__(self,b):return self._as(b)+-self
    def __mul__(self,b):
        b=self._as(b);return _First(self.value*b.value,self.first*b.value+self.value*b.first)
    __rmul__=__mul__
    def __truediv__(self,b):
        b=self._as(b);return _First(self.value/b.value,(self.first*b.value-self.value*b.first)/b.value**2)
    def __rtruediv__(self,b):return self._as(b)/self
    def exp(self):
        v=np.exp(self.value);return _First(v,v*self.first)
    def sin(self):return _First(np.sin(self.value),np.cos(self.value)*self.first)
    def cos(self):return _First(np.cos(self.value),-np.sin(self.value)*self.first)
    def sqrt(self):
        v=np.sqrt(self.value);return _First(v,self.first/(2*v))


def geometry_first_application(raw,directions):
    """Differentiate every consumed coframe factor from the existing action."""
    raw=np.asarray(raw,complex);D=np.asarray(directions,complex)
    if raw.ndim!=1 or len(raw)<100 or D.ndim!=2 or D.shape[0]!=len(raw)or not np.isfinite([raw]).all()or not np.isfinite(D).all():
        raise ValueError('complete raw material vector and its finite directions required')
    x=[_First(a,d)for a,d in zip(raw,D)];q,v,m=x[:37],x[37:74],x[74:98]
    k=np.arange(1,13);j=np.arange(12)
    dot=lambda a,b:sum(u*w for u,w in zip(a,b))
    Cstar=RADIUS0*(q[0]+dot(q[1:13],(-1.)**k)+dot(q[13:25],(-1.)**j)).exp()
    logdot=v[0]+dot(v[1:13],(-1.)**k)+dot(v[13:25],(-1.)**j)
    delta=x[98]/Cstar;rate=(x[99]-logdot*x[98])/Cstar;chi=np.pi/4+delta
    ck=[(4*a*chi).cos()for a in k];cj=[(4*a*chi).cos()for a in j];window=(2*chi).sin();window=window*window
    u=dot(q[1:13],ck);b=window*dot(q[25:37],cj);w=window*dot(q[13:25],cj)
    radius=RADIUS0*q[0].exp();C=radius*(u+w).exp();A=radius*(u+b).exp()*chi.cos();B=radius*(u-b).exp()*chi.sin()
    N=dot(m[:12],ck).exp();beta=(4*chi).sin()*dot(m[12:],cj);den=A*A+B*B
    R=A*B/den.sqrt();U=C*(rate+beta)/N;lapse=N*(1-U*U).sqrt();lam=A*A/den
    values=dict(R4=R,N=lapse,mechanical_lambda=lam,Cstar=Cstar,delta=delta,wall=chi,wall_rate=rate,U=U,C=C,A=A,B=B,lapse_base=N)
    return dict(value={key:a.value for key,a in values.items()},first={key:a.first for key,a in values.items()},
        complex_parameter_conjugated=False,raw_direction_count=D.shape[1])


def canonical_body_first_application(raw,directions,representation,*,coordinate_time=0j,
        coordinate_time_first=None,initial_pair=None,reference_pair=None,parent_initial_first=None):
    """Apply the full wall-body jet, including inherited parent/frame motion.

    A supplied coordinate-time direction acts on the explicit inherited
    affine parent/reference germs.  Its action on the child raw curve is
    already in directions and is not added twice.
    """
    raw=np.asarray(raw,complex);D=np.asarray(directions,complex);geo=geometry_first_application(raw,D)
    a,da=geo['value'],geo['first'];nr=D.shape[1];ng=representation['gauge_count']
    trace=np.einsum('fcj,j->fc',representation['wall_trace_map'],raw[100:100+ng])
    dtrace=np.einsum('fcj,ja->afc',representation['wall_trace_map'],D[100:100+ng])
    lam=a['mechanical_lambda'];dlam=da['mechanical_lambda']
    if initial_pair is not None:
        if reference_pair is None:raise ValueError('same inherited reference pair required')
        dt=np.zeros(nr,complex)if coordinate_time_first is None else np.asarray(coordinate_time_first,complex)
        parent=np.zeros((len(raw),nr),complex)if parent_initial_first is None else np.asarray(parent_initial_first,complex)
        if dt.shape!=(nr,)or parent.shape!=(len(raw),nr):raise ValueError('same clock and parent variation directions required')
        def affine_first(base,first):
            out=first.copy();out[:37]+=coordinate_time*first[37:74]+np.asarray(base)[37:74,None]*dt
            out[98]+=coordinate_time*first[99]+np.asarray(base)[99]*dt
            return out
        p=geometry_first_application(_affine_raw(initial_pair[0],coordinate_time),affine_first(initial_pair[0],parent))
        rp,rc=[geometry_first_application(_affine_raw(base,coordinate_time),affine_first(base,np.zeros_like(parent)))for base in reference_pair]
        inherited=p['value']['mechanical_lambda']-lam-rp['value']['mechanical_lambda']+rc['value']['mechanical_lambda']
        dinherited=p['first']['mechanical_lambda']-dlam-rp['first']['mechanical_lambda']+rc['first']['mechanical_lambda']
        trace[2:]+=M*inherited;dtrace[:,2:]+=dinherited[:,None,None]*M
    trace[2:]+=M*(lam-1);dtrace[:,2:]+=dlam[:,None,None]*M
    G=lepton_unit_trace_gauge_representation()['generators'];rep=lepton_current_hilbert_representation()
    connection=np.einsum('ac,cij->aij',trace[2:],G);dconnection=np.einsum('dac,cij->daij',dtrace[:,2:],G)
    spin=-1j*np.einsum('aij,ajk->ik',rep['alpha'],connection)+1.5*rep['gamma5']
    W=spin/a['R4']+_higgs_mass_realified(raw[-8:-4]);Omega=np.einsum('c,cij->ij',trace[0],G)/a['N']
    dW=-1j*np.einsum('aij,dajk->dik',rep['alpha'],dconnection)/a['R4']-da['R4'][:,None,None]*spin/a['R4']**2
    # The realified Higgs action is exactly linear in these FOUR original
    # real coordinates. Complexifying their coefficients does not take a
    # conjugate and does not choose a background Higgs section.
    hmaps=np.array([_higgs_mass_realified(e)for e in np.eye(4)])
    dW+=np.einsum('da,aij->dij',D[-8:-4].T,hmaps)
    dOmega=np.einsum('dc,cij->dij',dtrace[:,0],G)/a['N']-da['N'][:,None,None]*Omega/a['N']
    return dict(Hcan=W-1j*Omega,Hcan_first=dW-1j*dOmega,geometry=a,geometry_first=da,
        same_action_wall_trace=trace,same_action_wall_trace_first=dtrace,
        inherited_profile_and_mechanical_connection_count=1,
        child_clock_added_to_raw_direction_again=False)
