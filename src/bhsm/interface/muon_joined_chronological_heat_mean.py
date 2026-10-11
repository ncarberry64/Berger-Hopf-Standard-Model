"""Join the true moving-birth mean to the changing temporal heat adjoint.

The incoming far canonical mean is computed by the original signed
variational cell, then retained in its increasing-time adjoint. It is an
output of this finite chart, not a selected physical E0 boundary value.
"""
from __future__ import annotations
import numpy as np
from .muon_primal_native_phase_adjoint import (native_phase_midpoint_map,native_phase_named_border,
    native_phase_load_rows,chronological_native_phase_jacobian)
from .muon_profile_preserving_phase_sample import profile_preserving_lepton_sample
from .muon_changing_closed_fermion_mean import even_y_trace_duals
from .muon_corrected_birth_canonical_mean import affine_mean_lift
from .muon_birth_finite_normal_trace_graph import affine_connection_profile_two_jet
from .muon_birth_inherited_finite_normal_phase import affine_geometry_germ
from .muon_primal_intrinsic_lepton_operator import primal_intrinsic_lepton_operator
from .muon_primal_trace_enriched_lepton_operator import intrinsic_wall_coordinate_reduction
from .muon_native_mean_core_heat_target import _unit_lepton_mass6
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_source_directed_temporal_green import source_product_temporal_values
from .muon_parent_maxwell_full_weak import M
from .muon_parent_retarded_hypercharge import WALL


def canonical_initial_mean_rows(J,n,delta_x,delta_p):
    """Differentiate actual initial x/p in all midpoint residual rows."""
    A=np.asarray(J,float);x=np.asarray(delta_x,float);p=np.asarray(delta_p,float)
    if A.ndim!=2 or A.shape[0]!=A.shape[1]or x.shape!=p.shape or x.shape[0]!=n or A.shape[0]<3*n:
        raise ValueError('same complete variational cell and canonical paired means required')
    result=np.einsum('ij,j...->i...',A[:,:n],x)
    result[:n]=-x;result[n:2*n]-=p;result[2*n:3*n]-=p/2
    return result


def _solve(A,rhs,*,adjoint=False):
    row=1/np.maximum(np.max(abs(A),axis=1),np.finfo(float).tiny)
    col=1/np.maximum(np.max(abs(row[:,None]*A),axis=0),np.finfo(float).tiny)
    balanced=row[:,None]*A*col[None,:]
    return (row*np.linalg.solve(balanced.T,col*rhs)if adjoint
        else col[:,None]*np.linalg.solve(balanced,row[:,None]*rhs))


def inherited_heat_parameter_contact(phase,heat,initial_parent_mean,*,cutoff,quadrature_order=16):
    """Apply the native target to the actual inherited parent profile motion."""
    if phase['receipt']['side']!='outgoing':raise ValueError('child inherited profile only')
    L=abs(phase['receipt']['span']);z,w=np.polynomial.legendre.leggauss(quadrature_order)
    times=np.concatenate(((z+1)*L/4,(z+3)*L/4));weights=np.tile(w*L/4,2)
    points=[profile_preserving_lepton_sample(phase,float(t))for t in times]
    tf=source_product_temporal_values(times,L)
    Gt=np.einsum('t,t,ta,tb->ab',weights,np.array([a['operator']['N']for a in points]),tf['value'],tf['value'])
    from scipy.linalg import cholesky,solve_triangular
    T=solve_triangular(cholesky(Gt,lower=True).T,np.eye(8),lower=False)
    values=tf['value']@T;rates=tf['coordinate_rate']@T
    d=even_y_trace_duals(*[heat[k]for k in ('weak_P0','weak_P1','weak_P2','temporal_Gram')],cutoff)
    D0,D1,_=d['action_duals'];fi=np.array([2,3,8,9,14,15]);S=np.diag([1]*4+[-1]*2);I=np.eye(6)
    total=np.zeros((3,3));node_contacts=[];node_profile_means=[]
    pair=phase['arrays']['initial_pair'];rep=phase['representation']
    for j,(t,a)in enumerate(zip(times,points)):
        raw=a['sample']['raw_fields'];op=a['operator'];N=op['N']
        parent=affine_geometry_germ(pair[0],float(t));profile=affine_connection_profile_two_jet(np.array([parent,raw]),np.array([WALL]))
        parent_mean=np.einsum('ij,jab->iab',affine_mean_lift(268,float(t)),initial_parent_mean)
        delta_lambda=np.einsum('i,iab->ab',profile['first'][0,0,:100],parent_mean[:100])
        wall=M[:,:,None,None]*delta_lambda[None,None]
        direction=np.zeros((228,3,3));direction[100:160]=np.einsum('ij,jab->iab',op['trace_realization'],
            np.concatenate((np.zeros((8,3,3)),wall.reshape(12,3,3)),axis=0))
        reduced=primal_intrinsic_lepton_operator(op['intrinsic_reduced_raw_fields'],intrinsic_wall_coordinate_reduction(rep)['original_representation'])
        derivative=np.einsum('jab,juv->abuv',direction,reduced['W_raw_first_jet']+reduced['Omega_tau_raw_first_jet'])[:,:,fi][:,:,:,fi]
        derivative=(derivative+np.einsum('ij,abjk,kl->abil',S,derivative,S))/2
        A=op['W'][np.ix_(fi,fi)]+op['Omega_tau'][np.ix_(fi,fi)];A=(A+S@A@S)/2
        V=np.concatenate([v*I for v in values[j]],axis=1);Vd=np.concatenate([v*I for v in rates[j]],axis=1)
        F0=Vd/N+A@V;Fm=_unit_lepton_mass6(op['H'])@V
        cotangent=F0@D0+Fm@D1;deltaF=np.einsum('abij,jk->abik',derivative,V)
        value=2*weights[j]*N*np.einsum('ij,abij->ab',cotangent.conj(),deltaF).real
        total+=value;node_contacts.append(value);node_profile_means.append(delta_lambda)
    Y=np.diag(lepton_current_hilbert_representation()['family_Y']).real;difference=Y[1]**2-Y[2]**2
    return dict(paired_inherited_parameter_contact=difference*total,
        paired_node_inherited_parameter_contacts=difference*np.array(node_contacts),
        inherited_profile_means=np.array(node_profile_means),
        parent_only_operator_measure_derivative_exact_zero='N and geometric Haar measure depend on held child raw geometry; this parent parameter enters only the owned spatial profile increment')


def joined_phase_heat_mean(phase,heat,raw_mean_load,birth_canonical_mean,*,parent_gradient_forcing=None,
        initial_parent_mean=None,cutoff=1e-11,frame='temporal'):
    """Execute original and chronological adjoints with the same birth source."""
    maps=native_phase_midpoint_map(phase['representation']);n=maps['coordinates']['x_count']
    canonical=np.asarray(birth_canonical_mean,float)
    if canonical.shape!=(2*n,3,3):raise ValueError('actual truebirth x/p mean in the same trace lift required')
    load=np.asarray(raw_mean_load,float)
    if parent_gradient_forcing is not None:load=load+np.asarray(parent_gradient_forcing,float)
    original=phase['arrays']['stage_jacobian'][0];h=phase['receipt']['span']
    F=native_phase_load_rows(load,phase['representation'],h)
    start=canonical_initial_mean_rows(original,n,canonical[:n],canonical[n:])
    K=native_phase_named_border(original,phase['representation'],frame=frame)['matrix']
    rhs=np.concatenate(((F+start).reshape(len(K)-2,9),np.zeros((2,9))),axis=0)
    response=-_solve(K,rhs);delta=response[:-2].reshape(len(K)-2,3,3)
    far=delta[:2*n].copy()
    # Reconstruct the same trajectory in increasing physical time.
    if h<0:
        chronological=np.concatenate((canonical,delta[2*n:]),axis=0);initial=far
    else:chronological=delta;initial=canonical
    chrono=chronological_native_phase_jacobian(original,phase['representation'],h)
    Fc=native_phase_load_rows(load,phase['representation'],chrono['step'])
    Fc+=canonical_initial_mean_rows(chrono['jacobian'],n,initial[:n],initial[n:])
    Kc=native_phase_named_border(chrono['jacobian'],phase['representation'],frame=frame)['matrix']
    rhsc=np.concatenate((Fc.reshape(len(Kc)-2,9),np.zeros((2,9))),axis=0)
    G=heat['paired_phase_gradient'];adj=_solve(Kc,np.r_[G,0.,0.],adjoint=True)
    adjoint_contact=(-adj@rhsc).reshape(3,3)
    # x_mid=(x_initial+x_final)/2; retain the explicit initial-state target.
    raw_initial=np.einsum('ij,jab->iab',maps['coordinates']['lift'][:,:n]/2,initial[:n])
    explicit_initial=np.einsum('ti,iab->ab',heat['paired_raw_quadrature_cotangents'],raw_initial)
    direct_phase=np.einsum('i,iab->ab',G,chronological)
    inherited=np.zeros((3,3));inherited_arrays={}
    if phase['receipt']['side']=='outgoing':
        if initial_parent_mean is None:raise ValueError('actual inherited parent mean required, not zero')
        inherited_arrays=inherited_heat_parameter_contact(phase,heat,initial_parent_mean,cutoff=cutoff)
        inherited=inherited_arrays['paired_inherited_parameter_contact']
    return dict(phase_mean=delta,chronological_phase_mean=chronological,original_mean_response=response,
        original_source_rows=F,original_initial_canonical_rows=start,original_residual=K@response+rhs,
        actual_far_canonical_mean=far,chronological_initial_mean=initial,
        chronological_source_rows=Fc,chronological_adjoint=adj,
        chronological_adjoint_residual=Kc.T@adj-np.r_[G,0.,0.],
        chronological_primal_residual=chrono['jacobian']@chronological.reshape(len(Kc)-2,9)+Fc.reshape(len(Kc)-2,9)+Kc[:-2,-2:]@response[-2:],
        original_frame_reactions=response[-2:].reshape(2,3,3),
        paired_phase_contact=adjoint_contact,paired_direct_phase_contact=direct_phase,
        phase_primal_adjoint_difference=adjoint_contact-direct_phase,
        paired_explicit_initial_target_contact=explicit_initial,
        paired_inherited_parameter_target_contact=inherited,
        paired_total_heat_mean_contact=adjoint_contact+explicit_initial+inherited,
        inherited_parameter_application=inherited_arrays,
        incoming_far_mean_filled_zero=False,statistics_factor_applied=False,
        error_scope='Actual binary64 signed/chronological variational applications of the same finite changing target and moving226 birth mean; far trace is an output, not selected physical E0; native continuum/completion/Pauli remain separate.')
