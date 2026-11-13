"""On-shell charged-current sources of the actual variational Dirac cell.

The full canonical lepton evolution is evaluated as an operator.  Its
initial Cauchy coefficients remain arbitrary; no spinor, covariance or
interacting LSZ pole is selected.  The bosonic response retains all rows.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from scipy.linalg import solve

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_parent_mean_causal_action import VOLUME
from .muon_primal_trace_enriched_lepton_operator import primal_trace_enriched_lepton_operator
from .muon_primal_charged_current_response import charged_current_matrices,exact_stored_bordered_pairing
from .muon_birth_trace_enriched_action import generic_coordinate_lift
from .muon_birth_trace_enriched_phase import enriched_representation_from_values
from .muon_trace_enriched_charged_current_response import (
    enriched_bordered_current_response,enriched_midpoint_source_rows,charged_kernel_coordinates,
)


def variational_cayley_amputation(K,operator_derivatives,step):
    """Exact finite-cell identity, evaluated for supplied Hermitian operators.

    U=(I+i*h*K/2)^-1(I-i*h*K/2), V=(I+U)/2.
    i*U†*D_rU=h*V†*(D_rK)*V.  Fixed coordinate-time h is differentiated
    nowhere here.  The derivative of the on-shell action is minus the
    right-hand coefficient divided by h.
    """
    K=np.asarray(K,complex);D=np.asarray(operator_derivatives,complex)
    if K.ndim!=2 or K.shape[0]!=K.shape[1] or D.ndim!=3 or D.shape[1:]!=K.shape or not np.isfinite(step) or step==0:
        raise ValueError('complete Hermitian K/derivative family and oriented nonzero step required')
    if not np.isfinite(K).all() or not np.isfinite(D).all():raise ValueError('finite canonical Dirac coefficients required')
    scale=max(1.,float(np.max(abs(K))),float(np.max(abs(D))))
    if max(np.max(abs(K-K.conj().T)),np.max(abs(D-D.conj().transpose(0,2,1))))>1e-11*scale:
        raise ValueError('variational canonical Dirac operators must be Hermitian')
    I=np.eye(len(K),dtype=complex);C=I+1j*step*K/2
    V=solve(C,I,assume_a='gen');U=solve(C,I-1j*step*K/2,assume_a='gen')
    dU=-1j*step*np.einsum('ij,rjk,kl->ril',V,D,V)
    paired=np.einsum('ij,rjk,kl->ril',V.conj().T,D,V)
    left=1j*np.einsum('ij,rjk->rik',U.conj().T,dU)
    return dict(propagator=U,midpoint_lift=V,propagator_first_jet=dU,
        on_shell_action_source_operators=-paired,
        unit_current_propagator_defect=float(np.linalg.norm(U.conj().T@U-I)),
        midpoint_lift_identity_defect=float(np.linalg.norm(V-(I+U)/2)),
        exact_identity_evaluation_defect=float(np.linalg.norm(left-step*paired)),
        equation='i U† D_rU=h V† D_rK V; D_rS_on_shell=-V† D_rK V',
        coordinate_time_step_held_fixed=True,selected_external_spinor_or_CAR_state=False,
        physical_LSZ_residue_or_pole_selected=False)


def amputated_charged_current_action_source(raw,representation,step,*,family=1):
    """Use the actual full18 operator and fixed-Y matter/geometry jets.

    K=N H_can includes material At exactly once.  The current source is
    pulled to the normalized initial canonical Cauchy frame by V.  This
    brings the reached H vertex into the charged source without fitting Y.
    """
    a=primal_trace_enriched_lepton_operator(raw,representation)
    dN=a['proper_time_Haar_measure_first_jet']/VOLUME
    K=a['N']*a['H_can'];D=a['N']*a['H_can_raw_first_jet']+dN[:,None,None]*a['H_can']
    cayley=variational_cayley_amputation(K,D,step)
    X=charged_current_matrices(family);operators=cayley['on_shell_action_source_operators']
    traces=np.einsum('aij,rji->ra',X,operators)
    if np.max(abs(traces.imag))>1e-11*max(1.,np.max(abs(traces))):
        raise ValueError('amputated Hermitian current source must be real')
    P=generic_coordinate_lift(representation['gauge_labels'])['lift']
    source=traces.real;hs=100+2*len(representation['gauge_labels'])
    return dict(raw_source=source,master_source=P.T@source,current_matrices=X,
        lepton_application=a,canonical_coordinate_time_operator=K,
        canonical_coordinate_time_operator_first_jet=D,amputation=cayley,
        reached_fixed_Y_H_source_norm=float(np.linalg.norm(source[hs:hs+4])),
        reached_H_rate_source_norm=float(np.linalg.norm(source[hs+4:])),
        constant_angular_Haar_volume_reapplied=False,physical_external_state_selected=False,
        physical_LSZ_pole_or_local_Fermi_coefficient_assigned=False)


def retained_amputated_current_response(repository=ROOT):
    """Apply on-shell current loads to both actual358 assigned phase cells."""
    root=Path(repository);base=root/'artifacts/muon_parent_gauge_geometry_correction_20261010'
    records=[];results=[]
    def load(folder):
        blob=(folder/'result.json').read_bytes();receipt=json.loads(blob);data=(folder/'application.npz').read_bytes()
        if sha256(data).hexdigest()!=receipt['numerical_sha256']:raise ValueError('saved same-action numerical values changed')
        for name,digest in receipt['input_hashes'].items():
            if sha256((root/name).read_bytes()).hexdigest()!=digest:raise ValueError('same action owner changed: '+name)
        for name,raw in (('result.json',blob),('application.npz',data)):
            records.append(dict(path=(folder/name).relative_to(root).as_posix(),bytes=len(raw),sha256=sha256(raw).hexdigest()))
        with np.load(folder/'application.npz',allow_pickle=False) as a:arrays={k:a[k].copy() for k in a.files}
        return receipt,arrays,sha256(blob).hexdigest()
    for side in ('incoming','outgoing'):
        receipt,arrays,_=load(base/f'enriched_phase_{side}_1steps_run_1')
        if receipt['side']!=side or receipt['steps']!=1 or receipt['completed_steps']!=1 or receipt['stages'][0]['status']!='REPRESENTED_PHASE_TOLERANCE':
            raise ValueError('completed actual one-cell enriched phase required')
        if (side=='incoming')!=(receipt['span']<0):raise ValueError('common E1 temporal orientation changed')
        endpoint,edata,digest=load(root/receipt['consumed_paired_endpoint_path'])
        if digest!=receipt['consumed_receipt_sha256'] or endpoint['action_parameters']!=receipt['action_parameters']:
            raise ValueError('phase must preserve the same actual endpoint and action parameters')
        rep=enriched_representation_from_values(endpoint,edata,radial_points=receipt['radial_points'],cap_points=receipt['cap_points'])
        raw=arrays['stage_midpoint_raw'][0];h=receipt['span']
        source=amputated_charged_current_action_source(raw,rep,h)
        electron=amputated_charged_current_action_source(raw,rep,h,family=2)
        outputs=[enriched_bordered_current_response(arrays['stage_jacobian'][0],source['master_source'],h,rep,frame=frame)
            for frame in ('temporal','radial')]
        # The distinct electron-family readout is contracted against the
        # SAME already solved muon-family source, with no second inverse.
        mixed=[]
        for output in outputs:
            target=h*electron['master_source'].T@output['midpoint_response']
            be=electron['master_source'];R=output['auxiliary_Gauss_column'];C=output['frame_matrix']
            K=np.block([[arrays['stage_jacobian'][0],R],[C,np.zeros((2,2))]])
            rhs=np.vstack((-enriched_midpoint_source_rows(source['master_source'],h),np.zeros((2,8))))
            readout=np.zeros((8,360));readout[:,:106]=h*be[:106].T/2
            readout[:,212:318]=h*be[106:212].T;readout[:,318:358]=h*be[212:].T
            mixed.append(dict(paired_current_response=target,charged_kernel=charged_kernel_coordinates(target),
                exact_stored_certificate=exact_stored_bordered_pairing(K,rhs,readout)))
        results.append(dict(side=side,oriented_step=h,action_parameters=receipt['action_parameters'],
            raw_fields=raw,muon_source=source,electron_source=electron,applications=outputs,
            electron_readout_muon_source=mixed,
            charged_family_source_difference=float(np.linalg.norm(source['raw_source']-electron['raw_source'])),
            named_frame_pairing_absolute_difference=float(np.linalg.norm(outputs[0]['paired_current_response']-outputs[1]['paired_current_response'])),
            named_frame_electron_muon_pairing_absolute_difference=float(np.linalg.norm(mixed[0]['paired_current_response']-mixed[1]['paired_current_response'])),
            numerical_background_residual=float(np.linalg.norm(arrays['stage_residual'][0])),
            temporal_scope=receipt['temporal_scope'],source_profile_scope='constant midpoint current on same assigned cell',
            local_g2_over_MW_squared_substituted=False,physical_Fermi_coefficient=None))
    return dict(classification='EVALUATED_ON_SHELL_VARIATIONAL_CELL_CHARGED_CURRENT_SOURCE_ADJOINT',
        arms=results,input_records=records,original358_action_rows_retained=True,
        current_owner='ae31_c2_coexact_su2l_charged_current.weak_charged_representation_ledger',
        canonical_Cauchy_frame='complete unit-current18; no selected c-number spinor or covariance',
        on_shell_fermion_current_amputation_evaluated=True,interacting_LSZ_pole_or_residue_evaluated=False,
        physical_c_F=None,E_kappa_GeV=None,physical_low_energy_local_projection_selected=False,
        native_Pauli_evaluated=False,
        error_scope='outward exact stored bosonic linear solve; finite Cayley/source formation and field/continuum/physical matching error separate')
