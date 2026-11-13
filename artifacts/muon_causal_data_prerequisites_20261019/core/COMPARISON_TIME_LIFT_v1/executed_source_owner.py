"""Original time/gauge lift on the saved homogeneous comparison component.

This is a necessary local comparison application, not an incoming physical
state, a selected vacuum, a collider chart, or a stationary-past extension.
The old native pencil and its heat spectrum are never used as frequencies.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import qr

from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from .muon_native_dirac_hamiltonian import canonical_lepton_hamiltonian_maps
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_stationary_native_reference_load import factor_twojet
from .muon_primal_electromagnetic_source import higgs_aligned_charge
from .muon_magnetic_open_lepton_vertex import canonical_open_field_vertices


def stationary_gauge_lift_rows(theta):
    """Original D_mu lambda=0, lambda_H H=0 for stationary components.

    The proper material observer is K=ell^-1 partial_t, from the actual
    intrinsic metric diag(ell²,-R² I3). Ordinary field Lie derivatives
    vanish ONLY on this retained stationary comparison. No comparison
    extension to the actual moving parent is made here.
    """
    t=np.asarray(theta)
    if t.shape!=(22,) or not np.isrealobj(t) or min(t[:2])<=0:
        raise ValueError('actual real22 comparison coefficients required')
    G=higgs_u2_real_representation()['complex_generators']
    A=np.einsum('mc,cij->mij',np.r_[t[2:6][None]/t[1],t[6:18].reshape(3,4)],G)
    H=t[18:20]+1j*t[20:22]
    columns=[]
    for gen in G:
        comm=A@gen-gen@A;section=gen@H
        z=np.r_[comm.ravel(),section]
        columns.append(np.r_[z.real,z.imag])
    return np.column_stack(columns),A,H


def execute_stationary_time_lift(theta):
    """Use a square ORIGINAL row pivot; retain rank failure as failure.

    A rank4 result forces lambda=0 in represented U2, rather than assuming
    temporal gauge or an arbitrary chemical-potential shift. The Lie-time
    source is0 only on this stationary coefficient family. Strong/family,
    spatial clock incidence and full-domain time lifts are not supplied.
    """
    C,A,H=stationary_gauge_lift_rows(theta)
    _,_,p=qr(C.T,pivoting=True,mode='economic');pivot=np.asarray(p[:4])
    singular=np.linalg.svd(C,compute_uv=False)
    if singular[-1]<=1e-12*singular[0]:
        raise ValueError('stationary comparison has unresolved gauge time-lift freedom')
    lam=np.linalg.solve(C[pivot],np.zeros(4))
    return dict(original_symmetry_matrix=C,original_row_pivots=pivot,
        gauge_compensator=lam,original_symmetry_rows=C@lam,
        singular_values=singular,pivot_condition=np.array(np.linalg.cond(C[pivot])),
        proper_material_clock_inverse=np.array(1/float(theta[1])),
        Higgs_connection=A,Higgs_section=H,
        represented_time_gauge_lift_rank=np.array(4))


def causal_comparison_coefficients(theta,theta_gradient):
    """Original causal H and its static-field source, no native heat call."""
    t,g=np.asarray(theta),np.asarray(theta_gradient)
    if t.shape!=(22,) or g.ndim!=2 or g.shape[0]!=22:
        raise ValueError('same22 coefficients and complete declared source map required')
    f=factor_twojet(t);W,Omega=f['W'][0],f['Omega'][0]
    h=W-1j*Omega;hg=np.einsum('jab,jk->kab',f['W'][1]-1j*f['Omega'][1],g)
    generators=lepton_unit_trace_gauge_representation()['generators']
    connection=np.empty((1,4,18,18),complex);connection[0,0]=Omega
    connection[0,1:]=np.einsum('ac,cij->aij',t[6:18].reshape(3,4),generators)
    original=canonical_lepton_hamiltonian_maps(value_map=np.eye(18)[None],
        spatial_derivative_map=np.zeros((1,3,18,18)),H=(t[18:20]+1j*t[20:22])[None],
        R4=t[0],gauge_connection=connection)
    return dict(H=h,H_source=hg,W=W,Omega=Omega,
        original_causal_coefficient_rows=original['hamiltonian_map'][0]-h,
        Hermiticity_rows=h-h.conj().T,
        physical_unit_source_is_positive_rescaling_only=True)


def sector_projector_source(H,H_source):
    """Adopted sign boundary component and its Sylvester derivatives.

    No line inside a degenerate sector is chosen as a physical mode.
    Zero modes are rejected rather than relabeled as antiparticles.
    """
    h,x=np.asarray(H),np.asarray(H_source)
    if h.ndim!=2 or h.shape[0]!=h.shape[1] or x.shape[1:]!=h.shape:
        raise ValueError('same causal operator and full source required')
    if np.max(abs(h-h.conj().T))>1e-12*max(1.,np.max(abs(h))):
        raise ValueError('self-adjoint comparison component required')
    e,V=np.linalg.eigh(h)
    if np.min(abs(e))<=1e-12:raise ValueError('zero sector needs its original separate boundary rule')
    mask=e>0;U,N=V[:,mask],V[:,~mask];P=U@U.conj().T;I=np.eye(len(h))
    E=np.einsum('ai,kab,bj->kij',U.conj(),x,N)
    Z=E/(e[mask][:,None]-e[~mask][None,:])[None]
    dP=np.einsum('ai,kij,bj->kab',U,Z,N.conj())
    dP=dP+dP.conj().swapaxes(-1,-2)
    comm=h@dP-dP@h+x@P-P@x
    return dict(positive=P,negative=I-P,positive_source=dP,negative_source=-dP,
        eigenvalues=e,positive_dimension=np.array(mask.sum()),negative_dimension=np.array((~mask).sum()),
        original_projector_commutator_rows=h@P-P@h,
        original_projector_source_rows=comm,
        original_idempotent_source_rows=P@dP+dP@P-dP,
        original_CAR_completeness_rows=P+(I-P)-I,
        original_CAR_opposite_rows=P@(I-P))


def execute_electron_comparison(theta,theta_gradient):
    """Consume time lift in the original causal/charge/current equations.

    Results are the FULL electron-family6 operator component. A charged4
    algebraic fiber is only tested for reduction; it is never imposed as
    an incoming spectral subspace or copied into the muon family.
    """
    t,g=np.asarray(theta),np.asarray(theta_gradient)
    lift=execute_stationary_time_lift(t);causal=causal_comparison_coefficients(t,g)
    C=np.eye(18)[:,[4,5,10,11,16,17]];Pe=C@C.T;outside=np.eye(18)-Pe
    h=C.T@causal['H']@C;x=np.einsum('ai,kab,bj->kij',C,causal['H_source'],C)
    sectors=sector_projector_source(h,x);H=t[18:20]+1j*t[20:22]
    qdata=higgs_aligned_charge(H,np.zeros(2,complex));Q=C.T@qdata['charge']@C
    qx=[]
    for direction in g.T:
        Hx=direction[18:20]+1j*direction[20:22]
        qx.append(C.T@higgs_aligned_charge(H,Hx)['charge_rate']@C)
    qx=np.asarray(qx);Pch=-Q;Pc=sectors['positive'];Pm=sectors['negative']
    charge=h@Q-Q@h;chargex=x@Q-Q@x+h@qx-qx@h
    G=lepton_unit_trace_gauge_representation()['generators']
    field=np.r_[t[2:6][None]/t[1],t[6:18].reshape(3,4)]
    A=np.einsum('mc,cij->mij',field,G);connectioncharge=A@qdata['charge']-qdata['charge']@A
    vertices=canonical_open_field_vertices(t[0],t[1]);V=np.concatenate((vertices['gauge'].reshape(20,18,18),vertices['scalar']))
    Ve=np.einsum('ai,vab,bj->vij',C,V,C)
    # These are actual current OPERATOR blocks, not state contractions.
    pair_vertex=Pc@Ve@Pm
    Vx=np.zeros((g.shape[1],24,18,18),complex)
    Vx[:,:4]=-g[1,:,None,None,None]/t[1]*V[None,:4]
    Vx[:,8:20]=-g[0,:,None,None,None]/t[0]*V[None,8:20]
    Vex=np.einsum('ai,kvab,bj->kvij',C,Vx,C)
    dPc=sectors['positive_source']
    pair_vertex_source=(dPc[:,None]@Ve[None]@Pm
        +Pc@Vex@Pm-Pc@Ve[None]@dPc[:,None])
    out=dict(**lift,**causal,**{'electron_'+k:v for k,v in sectors.items()},
        proper_material_clock_inverse_source=-g[1]/t[1]**2,
        gauge_compensator_source=np.zeros((g.shape[1],4)),
        electron_family_lift=C,electron_family_reducing_rows=outside@causal['H']@C,
        electron_family_source_reducing_rows=outside@causal['H_source']@C,
        electron_H=h,electron_H_source=x,electron_Higgs_charge=Q,electron_charge_source=qx,
        electron_charge_evolution_rows=charge,electron_charge_evolution_source_rows=chargex,
        electron_charged_to_neutral_rows=(np.eye(6)-Pch)@h@Pch,
        full_local_parallel_charge_rows=connectioncharge,
        positive_boundary_charged_image=Pc@Pch,negative_boundary_charged_image=Pm@Pch,
        original_current_pair_operator_blocks=pair_vertex,
        original_current_pair_operator_source=pair_vertex_source,
        original_current_vertices_electron6=Ve,
        original_current_positive_operator_blocks=Pc@Ve@Pc,
        original_current_negative_operator_blocks=Pm@Ve@Pm,
        comparison_physical_to_canonical_scale=np.array(t[0]**1.5),
        canonical_scale_source=1.5*t[0]**.5*g[0],
        physical_constant_section18=np.eye(18)/np.sqrt(2*np.pi**2*t[0]**3),
        complete_constant_Haar_Cauchy_Gram_rows=np.eye(18)*(2*np.pi**2*t[0]**3)/(2*np.pi**2*t[0]**3)-np.eye(18))
    return out
