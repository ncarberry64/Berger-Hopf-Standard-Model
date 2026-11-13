"""Owned lepton operator and geometric/field first jets on actual raw fields.

This binds the general primal fields, rather than reconstructing an old
compact scalar profile.  The normalized constant-angular trial space is
an invariant operator subspace on these angular-homogeneous fields.  Its
computational basis does not choose a fermionic state or covariance.
"""
from __future__ import annotations
import numpy as np

from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_parent_maxwell_full_weak import FIELD_ORDER,M
from .muon_parent_retarded_hypercharge import WALL,regular_radial_basis
from .muon_native_dirac_hamiltonian import (
    canonical_lepton_hamiltonian_maps,lepton_current_hilbert_representation,
    fixed_y_higgs_hamiltonian,
)
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation


def primal_intrinsic_lepton_operator(raw_fields,representation):
    """Apply the retained all-family operator and every raw228 first jet.

    Material temporal trace is At_ref, divided by the induced lapse once.
    Eulerian radial advection is not added again.  The spin connection,
    all independent wall gauge components, and fixed Y*H remain active.
    chi=R4**(3/2)*psi has current Gram I18; the proper-time FE measure is
    N_induced*dt*2*pi², whose variation is separately returned.
    """
    if raw_fields is None or not np.isrealobj(raw_fields):
        raise ValueError('explicit real common raw228 fields required')
    raw=np.asarray(raw_fields,float)
    if raw.shape!=(228,) or not np.isfinite(raw).all():
        raise ValueError('finite common raw228 fields required')
    rep=representation
    if len(rep['gauge_labels'])!=60:
        raise ValueError('complete independent five-component mean representation required')
    w=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
    invR=1/w['R4'];invN=1/w['induced_lapse'];lam=w['mechanical_connection_lambda']
    basis,_=regular_radial_basis(np.array([WALL]),rep['radial_order'])
    trace=np.zeros((5,4));trace_map=np.zeros((5,4,60))
    for j,label in enumerate(rep['gauge_labels']):
        f=FIELD_ORDER.index(label['field']);c=label['internal'];b=basis[0,label['radial']]
        trace[f,c]+=b*raw[100+j];trace_map[f,c,j]=b
    generators=lepton_unit_trace_gauge_representation()['generators']
    spatial=trace[2:]+M*(lam.value-1)
    Ot=np.einsum('c,cij->ij',trace[0],generators)
    Os=np.einsum('ac,cij->aij',spatial,generators)
    H=(raw[220:222]+1j*raw[222:224])[None]
    connection=np.concatenate(((invN.value*Ot)[None],Os))[None]
    owned=canonical_lepton_hamiltonian_maps(value_map=np.eye(18)[None],
        spatial_derivative_map=np.zeros((1,3,18,18)),H=H,
        R4=w['R4'].value,gauge_connection=connection)
    hilbert=lepton_current_hilbert_representation()
    alpha=hilbert['alpha'];gamma5=hilbert['gamma5']
    spatial_connection=-1j*np.einsum('aij,ajk->ik',alpha,Os)
    mechanical_slope=-1j*np.einsum('aij,ac,cjk->ik',alpha,M,generators)
    constant=spatial_connection+1.5*gamma5
    dW=np.zeros((228,18,18),complex)
    dW[:100]=invR.gradient[:,None,None]*constant+invR.value*lam.gradient[:,None,None]*mechanical_slope
    dOs=np.einsum('acj,cuv->jauv',trace_map[2:],generators)
    dW[100:160]=-1j*invR.value*np.einsum('aij,bajk->bik',alpha,dOs)
    for k in range(4):
        direction=np.zeros((1,2),complex);direction[0,k%2]=1 if k<2 else 1j
        dW[220+k]=fixed_y_higgs_hamiltonian(direction)[0]
    dOt=np.einsum('cj,cuv->juv',trace_map[0],generators)
    dOmega=np.zeros_like(dW)
    dOmega[:100]=invN.gradient[:,None,None]*Ot
    dOmega[100:160]=invN.value*dOt
    measure=2*np.pi**2*w['induced_lapse'].value
    measure_gradient=np.zeros(228);measure_gradient[:100]=2*np.pi**2*w['induced_lapse'].gradient
    return dict(W=owned['spatial_mass_hamiltonian_map'][0],
        H_can=owned['hamiltonian_map'][0],Omega_t=Ot,Omega_tau=invN.value*Ot,
        W_raw_first_jet=dW,Omega_tau_raw_first_jet=dOmega,
        H_can_raw_first_jet=dW-1j*dOmega,
        current_Gram=np.eye(18),proper_time_Haar_measure=measure,
        proper_time_Haar_measure_first_jet=measure_gradient,
        R4=w['R4'].value,N=w['induced_lapse'].value,H=H[0],
        raw_fields=raw,wall_trace=trace,
        angular_scope='homogeneous all-family C18 tensor constant scalar, invariant under this actual W; no state or covariance selected',
        temporal_trace_rule='material At_ref/N_induced; Eulerian radial advection cancels once',
        zero_application_provenance='W and Omega_tau have no explicit independent gauge-rate/H-rate coordinates in the first-order Dirac action; total coefficient-time derivatives still include field motion',
        factor_temporal_connection=invN.value*Ot,
        Lorentz_H_can_is_positive_factor_connection=False,
        complete_native_domain_or_LSZ_selected=False,physical_Pauli_value=False)
