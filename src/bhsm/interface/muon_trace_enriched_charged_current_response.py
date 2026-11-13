"""Charged-current contraction on the actual trace-enriched phase cells.

Every saved Euler, Legendre, multiplier and Gauss row is consumed.  The
two named central frames make their auxiliary Gauss reactions explicit.
This is a finite-cell current kernel, prior to a low-energy/LSZ reduction.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from scipy.linalg import solve

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_parent_mean_causal_action import VOLUME
from .muon_birth_trace_enriched_action import generic_coordinate_lift,trace_enriched_radial_basis
from .muon_birth_trace_enriched_phase import enriched_representation_from_values
from .muon_primal_trace_enriched_lepton_operator import primal_trace_enriched_lepton_operator
from .muon_primal_charged_current_response import (
    charged_current_matrices,central_gauge_profile_coefficients,exact_stored_bordered_pairing,
)
from .muon_parent_retarded_hypercharge import WALL,ALPHA


def enriched_charged_current_action_source(raw,representation,*,family=1):
    """Differentiate the same canonical Lorentz action at fixed chi.

    The material connection and current Gram are already in the intrinsic
    operator.  Its normalized constant angular carrier integrates to one.
    """
    a=primal_trace_enriched_lepton_operator(raw,representation)
    dN=a['proper_time_Haar_measure_first_jet']/VOLUME
    vertex=-a['N']*a['H_can_raw_first_jet']-dN[:,None,None]*a['H_can']
    X=charged_current_matrices(family)
    traces=np.einsum('aij,rji->ra',X,vertex)
    if np.max(abs(traces.imag))>1e-11*max(1.,np.max(abs(traces))):
        raise ValueError('Hermitian charged-current source must be real')
    P=generic_coordinate_lift(representation['gauge_labels'])['lift']
    return dict(raw_source=traces.real,master_source=P.T@traces.real,
        coordinate_time_source_operators=vertex,current_matrices=X,lepton_application=a,
        constant_angular_Haar_volume_reapplied=False,physical_external_state_selected=False)


def enriched_central_profiles(representation):
    """Embed analytic theta/theta_r in the original polynomial slots.

    The new nonpolynomial source-complement coefficient is exactly zero;
    enrichment does not introduce another inferred gauge direction.
    """
    p=central_gauge_profile_coefficients();T=np.zeros((4,2));D=T.copy()
    T[[0,1,3]]=p['theta_coefficients'];D[[0,1,3]]=p['radial_derivative_coefficients']
    rho=WALL*np.array([.09,.29,.56,.83,1.]);B,_=trace_enriched_radial_basis(representation,rho)
    x=rho/WALL;power=ALPHA+np.array([1.,2.])
    error=max(float(np.max(abs(B@T-x[:,None]**power))),
        float(np.max(abs(B@D-power[None,:]*x[:,None]**(power-1)/WALL))))
    if error>2e-12:raise ValueError('same enriched At/Ar band must contain both analytic central profiles')
    return dict(theta_coefficients=T,radial_derivative_coefficients=D,
        profile_reconstruction_absolute_error=error,nonpolynomial_enrichment_coefficient_exact_zero=True,
        exact_functional_identity=p['exact_functional_identity'])


def enriched_midpoint_source_rows(master_source,step):
    """Action derivative of x106/p106/Legendre106/Gauss40 rows."""
    b=np.asarray(master_source)
    if not np.isrealobj(b) or b.ndim!=2 or b.shape[0]!=252 or not np.isfinite(b).all() or not np.isfinite(step) or step==0:
        raise ValueError('complete real x106/v106/y40 source and oriented nonzero step required')
    return np.vstack((np.zeros_like(b[:106]),-step*b[:106],b[106:212],b[212:]))


def charged_kernel_coordinates(kernel):
    """Exact charged recombination and metric-tensor reduction diagnostic.

    These are HS current coefficient coordinates, not LSZ external states.
    A nonzero remainder precludes treating this finite matrix as a single
    metric-tensor coefficient.  No physical c_F is assigned by projection.
    """
    K=np.asarray(kernel)
    if not np.isrealobj(K) or K.shape!=(8,8) or not np.isfinite(K).all():
        raise ValueError('complete real eight-current kernel required')
    mp=(K[:4,:4]+K[4:,4:]+1j*K[:4,4:]-1j*K[4:,:4])/2
    pp=(K[:4,:4]-K[4:,4:]+1j*K[:4,4:]+1j*K[4:,:4])/2
    metric=np.diag([1.,-1.,-1.,-1.]);coefficient=np.sum(metric*mp)/4
    remainder=mp-coefficient*metric
    return dict(Jminus_Jplus=mp,Jplus_Jminus=mp.conj(),Jplus_Jplus=pp,Jminus_Jminus=pp.conj(),
        metric_tensor_coefficient_real=float(coefficient.real),metric_tensor_coefficient_imag=float(coefficient.imag),
        metric_tensor_remainder=remainder,metric_tensor_remainder_norm=float(np.linalg.norm(remainder)),
        equal_charge_kernel_norm=float(np.linalg.norm(pp)),HS_spin_normalization='sigma_mu/sqrt2',
        physical_lorentz_current_or_LSZ_projection_selected=False,physical_c_F=None)


def enriched_bordered_current_response(jacobian,master_source,step,representation,*,frame='temporal'):
    """Full358 action rows, two explicit frames, and outward paired solve."""
    J=np.asarray(jacobian);b=np.asarray(master_source)
    if not np.isrealobj(J) or J.shape!=(358,358) or not np.isfinite(J).all():
        raise ValueError('complete real actual358 midpoint Jacobian required')
    forcing=enriched_midpoint_source_rows(b,step)
    if frame not in ('temporal','radial'):raise ValueError('named temporal or radial central frame required')
    labels=representation['gauge_labels'];coords=generic_coordinate_lift(labels);profiles=enriched_central_profiles(representation)
    at=[j for j,i in enumerate(coords['At_indices']) if labels[i]['internal']==3]
    ar=[j for j,i in enumerate(coords['dynamic_gauge_indices']) if labels[i]['field']=='A_rho' and labels[i]['internal']==3]
    if len(at)!=4 or len(ar)!=4:raise ValueError('complete enriched central At/Ar band required')
    R=np.zeros((358,2));R[318+24+np.array(at)]=profiles['theta_coefficients']
    C=np.zeros((2,358))
    if frame=='temporal':C[:,318+24+np.array(at)]=profiles['theta_coefficients'].T
    else:C[:,212+38+np.array(ar)]=profiles['radial_derivative_coefficients'].T
    K=np.block([[J,R],[C,np.zeros((2,2))]])
    rhs=np.vstack((-forcing,np.zeros((2,b.shape[1]))))
    row=1/np.maximum(np.max(abs(K),axis=1),np.finfo(float).tiny)
    col=1/np.maximum(np.max(abs(row[:,None]*K),axis=0),np.finfo(float).tiny)
    A=row[:,None]*K*col[None,:]
    response=col[:,None]*solve(A,row[:,None]*rhs,assume_a='gen')
    phase=response[:358];reaction=response[358:]
    eta=np.vstack((phase[:106]/2,phase[212:318],phase[318:]))
    readout=np.zeros((b.shape[1],360));readout[:,:106]=step*b[:106].T/2
    readout[:,212:318]=step*b[106:212].T;readout[:,318:358]=step*b[212:].T
    target=readout@response
    adjoint=row[:,None]*solve(A.T,col[:,None]*readout.T,assume_a='gen')
    backward=adjoint.T@rhs
    residual=J@phase+forcing
    U,s,_=np.linalg.svd(row[:358,None]*J*col[None,:358],full_matrices=True)
    # Diagnostic only: no row is deleted or mode removed by this threshold.
    keep=s>1e-12*max(s)
    certificate=exact_stored_bordered_pairing(K,rhs,readout)
    return dict(response_unknowns=phase,midpoint_response=eta,auxiliary_Gauss_reaction=reaction,
        paired_current_response=target,adjoint_paired_current_response=backward,
        charged_kernel=charged_kernel_coordinates(target),original358_residual=residual,
        original358_residual_norm=float(np.linalg.norm(residual)),
        auxiliary_Gauss_reaction_norm=float(np.linalg.norm(reaction)),
        frame_condition_residual_norm=float(np.linalg.norm(C@phase)),
        scaled_bordered_residual_norm=float(np.linalg.norm(row[:,None]*(K@response-rhs))),
        source_adjoint_pairing_absolute_difference=float(np.linalg.norm(target-backward)),
        diagnostic_balanced_rank=int(sum(keep)),diagnostic_singular_values=s,
        diagnostic_left_null_source_projection=U[:,~keep].T@(row[:358,None]*forcing),
        diagnostic_left_null_source_projection_norm=float(np.linalg.norm(U[:,~keep].T@(row[:358,None]*forcing))),
        rank_threshold_used_to_remove_rows_or_modes=False,balanced_condition_number=float(np.linalg.cond(A)),
        exact_stored_certificate=certificate,frame=frame,frame_matrix=C,auxiliary_Gauss_column=R,
        central_profiles=profiles,pseudoinverse_used=False,original_Gauss_rows_dropped=False,
        physical_gauge_quotient_certified=False,scalar_local_Fermi_coefficient_assigned=False)


def retained_enriched_current_response(repository=ROOT):
    """Consume actual incoming23-past/outgoing24-future phase Jacobians."""
    root=Path(repository);base=root/'artifacts/muon_parent_gauge_geometry_correction_20261010'
    records=[];results=[]
    def load(folder):
        blob=(folder/'result.json').read_bytes();receipt=json.loads(blob);data=(folder/'application.npz').read_bytes()
        if sha256(data).hexdigest()!=receipt['numerical_sha256']:raise ValueError('actual saved phase or endpoint values changed')
        for name,digest in receipt['input_hashes'].items():
            if sha256((root/name).read_bytes()).hexdigest()!=digest:raise ValueError('same action owner changed: '+name)
        for name,raw in (('result.json',blob),('application.npz',data)):
            records.append(dict(path=(folder/name).relative_to(root).as_posix(),bytes=len(raw),sha256=sha256(raw).hexdigest()))
        with np.load(folder/'application.npz',allow_pickle=False) as a:arrays={k:a[k].copy() for k in a.files}
        return receipt,arrays,sha256(blob).hexdigest()
    for side in ('incoming','outgoing'):
        receipt,arrays,_=load(base/f'enriched_phase_{side}_1steps_run_1')
        if receipt['side']!=side or receipt['steps']!=1 or receipt['completed_steps']!=1 or receipt['stages'][0]['status']!='REPRESENTED_PHASE_TOLERANCE':
            raise ValueError('completed same one-cell incoming/outgoing enriched phase required')
        if (side=='incoming')!=(receipt['span']<0):raise ValueError('common E1 temporal arm orientation changed')
        endpoint,edata,ehash=load(root/receipt['consumed_paired_endpoint_path'])
        if ehash!=receipt['consumed_receipt_sha256'] or endpoint['action_parameters']!=receipt['action_parameters']:
            raise ValueError('phase must consume the same actual endpoint fields and assigned action')
        rep=enriched_representation_from_values(endpoint,edata,
            radial_points=receipt['radial_points'],cap_points=receipt['cap_points'])
        source=enriched_charged_current_action_source(arrays['stage_midpoint_raw'][0],rep)
        electron=enriched_charged_current_action_source(arrays['stage_midpoint_raw'][0],rep,family=2)
        outputs=[enriched_bordered_current_response(arrays['stage_jacobian'][0],source['master_source'],receipt['span'],rep,frame=frame)
            for frame in ('temporal','radial')]
        results.append(dict(side=side,oriented_step=receipt['span'],action_parameters=receipt['action_parameters'],
            source=source,applications=outputs,raw_fields=arrays['stage_midpoint_raw'][0],
            numerical_background_residual=float(np.linalg.norm(arrays['stage_residual'][0])),
            charged_family_source_difference=float(np.linalg.norm(source['raw_source']-electron['raw_source'])),
            named_frame_pairing_absolute_difference=float(np.linalg.norm(outputs[0]['paired_current_response']-outputs[1]['paired_current_response'])),
            local_g2_over_MW_squared_substituted=False,physical_Fermi_coefficient=None,
            temporal_scope=receipt['temporal_scope'],source_profile_scope='constant assigned one-cell current load; no selected decay current'))
    return dict(classification='EVALUATED_CHARGED_CURRENT_SOURCE_ADJOINT_ON_ACTUAL_TRACE_ENRICHED_PHASE_CELLS',
        input_records=records,arms=results,original358_rows_retained=True,
        current_owner='ae31_c2_coexact_su2l_charged_current.weak_charged_representation_ledger',
        current_pairing='HS normalized Hermitian charged bilinear; canonical current GramI18; angular carrier1/sqrt(2pi²)',
        scale_equation='GF=c_F/E_kappa^2 after same-action low-energy LSZ decay contraction',
        physical_c_F=None,E_kappa_GeV=None,interacting_LSZ_or_low_energy_local_projection_evaluated=False,
        native_Pauli_evaluated=False,
        error_scope='outward exact stored bordered linear system; action/source formation, field/continuum and physical matching errors excluded')
