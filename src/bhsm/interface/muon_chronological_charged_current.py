"""Chronological current amputation on the actual full220 attached cell.

The incoming saved action cell is reversed by exchanging its canonical
endpoints, retaining the future-coordinate midpoint fields and rates.
The operator-valued initial Cauchy current is transported, not selected.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_birth_attached_phase import load_attached_endpoint
from .muon_charged_current_cell_amputation import amputated_charged_current_action_source
from .muon_charged_current_fermi_reduction import transported_fermi_template,exact_stored_fermi_template_fit
from .muon_primal_charged_current_response import exact_stored_bordered_pairing
from .muon_primal_native_phase_adjoint import chronological_native_phase_jacobian,native_phase_midpoint_map
from .muon_trace_enriched_charged_current_response import (
    enriched_bordered_current_response,enriched_midpoint_source_rows,charged_kernel_coordinates,
)


def chronological_phase_cell(jacobian,stored_unknowns,initial_master,initial_p,representation,span):
    """Reorient the same cell, including its endpoints, in increasing time.

    The saved unknowns are (x_final,p_final,v_mid,y_mid).  For a negative
    stored step, the new initial endpoint is that saved final endpoint
    and the new unknown endpoint is the saved initial endpoint.  Both
    midpoint velocities and algebraic coordinates remain unchanged.
    """
    maps=native_phase_midpoint_map(representation);coords=maps['coordinates']
    n=coords['x_count'];m=coords['y_count'];P=coords['lift']
    vectors=[np.asarray(v) for v in (stored_unknowns,initial_master,initial_p)]
    sizes=(3*n+m,2*n+m,n)
    if any(not np.isrealobj(v) or v.shape!=(size,) or not np.isfinite(v).all() for v,size in zip(vectors,sizes)):
        raise ValueError('complete real saved cell and canonical initial endpoint required')
    z,eta0,p0=vectors
    result=chronological_native_phase_jacobian(jacobian,representation,span)
    initial_x=eta0[:n].copy();initial_momentum=p0.copy();unknowns=z.copy()
    if span<0:
        initial_x=z[:n].copy();initial_momentum=z[n:2*n].copy()
        unknowns[:n]=eta0[:n];unknowns[n:2*n]=p0
    midpoint=np.r_[(initial_x+unknowns[:n])/2,unknowns[2*n:3*n],unknowns[3*n:]]
    original=np.r_[(eta0[:n]+z[:n])/2,z[2*n:3*n],z[3*n:]]
    if not np.array_equal(midpoint,original):raise ValueError('chronological reversal must preserve the identical midpoint action')
    result.update(initial_x=initial_x,initial_p=initial_momentum,unknowns=unknowns,
        midpoint_master=midpoint,midpoint_raw=P@midpoint,
        initial_Cauchy_data_transported_not_selected=True,
        canonical_fermion_convention='chi_hat=R4^(3/2)psi/(2pi²), unit current Gram')
    return result


def chronological_current_cell_response(cell,representation):
    """Evaluate the full18 on-shell source and complete358 current inverse.

    The electron-family readout contracts the already solved muon-family
    source.  The two named central frames retain every original Gauss row
    and report their reactions.  A local Fermi template is tested in the
    identical transported Cauchy frame, with no W-mass substitution.
    """
    raw=cell['midpoint_raw'];J=cell['jacobian'];h=cell['step']
    if not h>0:raise ValueError('increasing-time cell with positive step required')
    source=amputated_charged_current_action_source(raw,representation,h)
    electron=amputated_charged_current_action_source(raw,representation,h,family=2)
    maps=native_phase_midpoint_map(representation);M=maps['master_from_phase']
    op=source['lepton_application']
    template=transported_fermi_template(source['amputation']['midpoint_lift'],N=op['N'],R4=op['R4'],step=h)
    outputs=[];mixed=[]
    for frame in ('temporal','radial'):
        out=enriched_bordered_current_response(J,source['master_source'],h,representation,frame=frame)
        K=np.block([[J,out['auxiliary_Gauss_column']],[out['frame_matrix'],np.zeros((2,2))]])
        rhs=np.vstack((-enriched_midpoint_source_rows(source['master_source'],h),np.zeros((2,8))))
        target=h*electron['master_source'].T@out['midpoint_response']
        readout=np.c_[h*electron['master_source'].T@M,np.zeros((8,2))]
        cert=exact_stored_bordered_pairing(K,rhs,readout)
        fit=exact_stored_fermi_template_fit(template['template_tensor'],cert['paired_current_lower'],cert['paired_current_upper'])
        mixed.append(dict(frame=frame,paired_current_response=target,charged_kernel=charged_kernel_coordinates(target),
            exact_stored_certificate=cert,local_Fermi_template_fit=fit))
        outputs.append(out)
    return dict(muon_source=source,electron_source=electron,applications=outputs,
        electron_readout_muon_source=mixed,fermi_template=template,
        named_frame_pairing_absolute_difference=float(np.linalg.norm(outputs[0]['paired_current_response']-outputs[1]['paired_current_response'])),
        named_frame_electron_muon_pairing_absolute_difference=float(np.linalg.norm(mixed[0]['paired_current_response']-mixed[1]['paired_current_response'])),
        current_direction='past endpoint to birth for incoming23; birth to future endpoint for outgoing24',
        canonical_current_unit_Gram_no_extra_volume_squared_factor=True,
        physical_low_energy_Wilson_coefficient_or_LSZ_evaluated=False,physical_c_F=None)


def retained_chronological_current(repository=ROOT):
    """Consume both completed one-cell continuations of the full220 endpoint."""
    root=Path(repository);base=root/'artifacts/muon_parent_gauge_geometry_correction_20261010'
    records=[];arms=[]
    for side in ('incoming','outgoing'):
        folder=base/f'attached_phase_{side}_1steps_run_1'
        raw_receipt=(folder/'result.json').read_bytes();receipt=json.loads(raw_receipt)
        blob=(folder/'application.npz').read_bytes()
        if sha256(blob).hexdigest()!=receipt['numerical_sha256']:raise ValueError('attached phase values changed')
        if receipt['scope']!='EVALUATED_ATTACHED_FULL_FIELD_ACTION_PHASE_CONTINUATION' or receipt['side']!=side or receipt['steps']!=1 or receipt['completed_steps']!=1 or receipt['stages'][0]['status']!='REPRESENTED_PHASE_TOLERANCE':
            raise ValueError('completed actual full220 attached phase required')
        if (side=='incoming')!=(receipt['span']<0):raise ValueError('actual incoming/outgoing E1 time orientation required')
        for path,digest in receipt['input_hashes'].items():
            if sha256((root/path).read_bytes()).hexdigest()!=digest:raise ValueError('attached phase action owner changed: '+path)
        endpoint=load_attached_endpoint(receipt['consumed_paired_endpoint_path'],side=side,repository=root,
            radial_points=receipt['radial_points'],cap_points=receipt['cap_points'])
        if endpoint['receipt_sha256']!=receipt['consumed_receipt_sha256'] or endpoint['receipt']['action_parameters']!=receipt['action_parameters'] or endpoint['receipt']['row_count']!=220:
            raise ValueError('phase must bind the same full220 action attachment')
        rep=endpoint['representation']
        with np.load(folder/'application.npz',allow_pickle=False) as a:arrays={k:a[k].copy() for k in a.files}
        if not np.array_equal(arrays['initial_master'],endpoint['master']):raise ValueError('phase initial fields must equal the attached endpoint')
        cell=chronological_phase_cell(arrays['stage_jacobian'][0],arrays['stage_unknowns'][0],
            arrays['initial_master'],arrays['initial_p'],rep,receipt['span'])
        if not np.array_equal(cell['midpoint_raw'],arrays['stage_midpoint_raw'][0]):raise ValueError('identical saved midpoint action required')
        application=chronological_current_cell_response(cell,rep)
        arms.append(dict(side=side,oriented_step=cell['step'],stored_oriented_step=receipt['span'],
            chronological_cell=cell,application=application,action_parameters=receipt['action_parameters'],
            numerical_background_residual=float(np.linalg.norm(arrays['stage_residual'][0])),
            temporal_scope=receipt['temporal_scope'],source_profile_scope='constant chronological midpoint current, operator-valued initial Cauchy frame',
            physical_formation_or_final_child_boundary_selected=False))
        for directory in (folder,endpoint['source']):
            for name in ('result.json','application.npz'):
                data=(directory/name).read_bytes();records.append(dict(path=(directory/name).relative_to(root).as_posix(),bytes=len(data),sha256=sha256(data).hexdigest()))
    return dict(classification='EVALUATED_CHRONOLOGICAL_FULL220_ATTACHED_CELL_CURRENT_SOURCE_ADJOINT_AND_FERMI_TEMPLATE',
        arms=arms,input_records=records,complete358_action_rows_retained=True,
        incoming_midpoint_rates_and_Legendre_Gauss_rows_unchanged=True,
        independent_Yukawa_fit_or_local_W_mass_formula_used=False,physical_c_F=None,E_kappa_GeV=None,
        physical_low_energy_projection_or_LSZ_completed=False,native_Pauli_evaluated=False,
        error_scope='outward exact-stored bosonic source/adjoint pairing and template fit; source/Cayley/metric formation, field, continuum and physical LSZ errors separate')
