"""Charged-current action contraction on the corrected inherited cells.

The first-order lepton and complete Euler/Legendre/Gauss cell come from
one preserved phase.  The old attached wall operator is not substituted.
The local Fermi template is tested as a tensor, rather than being assigned
as the calibration coefficient from a scalar fit.
"""
from __future__ import annotations
import numpy as np

from .muon_profile_preserving_phase_sample import profile_preserving_lepton_sample
from .muon_charged_current_cell_amputation import variational_cayley_amputation
from .muon_primal_charged_current_response import charged_current_matrices, exact_stored_bordered_pairing
from .muon_primal_native_phase_adjoint import chronological_native_phase_jacobian, native_phase_midpoint_map
from .muon_trace_enriched_charged_current_response import enriched_bordered_current_response, enriched_midpoint_source_rows
from .muon_charged_current_fermi_reduction import transported_fermi_template, exact_stored_fermi_template_fit


def corrected_charged_current_action_source(phase, coordinate_time, step, *, family=1):
    """Apply i U† dU=h V† dK V with the actual full inherited operator.

    K=N H_can and its child raw derivative use the exact wall image and
    material temporal connection.  The parent/reference germ is held at
    the same declared coefficient time in the outgoing restriction.
    """
    if type(family) is not int or family not in (1, 2):
        raise ValueError('explicit middle or light current family required')
    if not np.isfinite(step) or step <= 0:
        raise ValueError('positive chronological variational cell required')
    sample = profile_preserving_lepton_sample(phase, coordinate_time)
    op = sample['operator']
    volume = 2 * np.pi**2
    dN = op['proper_time_Haar_measure_first_jet'] / volume
    K = op['N'] * op['H_can']
    dK = op['N'] * op['H_can_raw_first_jet'] + dN[:, None, None] * op['H_can']
    amputation = variational_cayley_amputation(K, dK, step)
    currents = charged_current_matrices(family)
    trace = np.einsum('aij,rji->ra', currents, amputation['on_shell_action_source_operators'])
    if np.max(abs(trace.imag)) > 1e-11 * max(1., np.max(abs(trace))):
        raise ArithmeticError('actual Hermitian charged-current action trace is unresolved')
    lift = phase['coordinates']['lift']
    if lift.shape[0] != len(trace):
        raise ValueError('operator and complete phase coordinate domain must agree')
    return dict(raw_source=trace.real, master_source=lift.T @ trace.real,
        current_matrices=currents, canonical_operator=K, canonical_operator_first_jet=dK,
        amputation=amputation, N=op['N'], R4=op['R4'],
        raw_fields=sample['sample']['raw_fields'],
        inherited_wall_image_count=1, canonical_angular_volume_reapplied=False,
        selected_spinor_or_covariance=False, physical_pole_or_LSZ_identified=False)


def corrected_charged_current_cell(phase, *, stage=0):
    """Evaluate both named full-row inverses and the transported local row.

    No physical scale is derived unless the actual low-energy current
    reduction supplies the Fermi coefficient.  A nonzero template
    remainder is retained as an evaluated tensor, including its interval.
    """
    r = phase['receipt']
    if type(stage) is not int or stage < 0 or stage >= r['steps']:
        raise ValueError('a saved completed stage is required')
    h = r['span'] / r['steps']
    time = (stage + .5) * h
    rep = phase['representation']
    cell = chronological_native_phase_jacobian(phase['arrays']['stage_jacobian'][stage], rep, h)
    step = cell['step']
    muon = corrected_charged_current_action_source(phase, time, step, family=1)
    electron = corrected_charged_current_action_source(phase, time, step, family=2)
    midpoint = native_phase_midpoint_map(rep)['master_from_phase']
    template = transported_fermi_template(muon['amputation']['midpoint_lift'],
        N=muon['N'], R4=muon['R4'], step=step)
    rows = []
    for frame in ('temporal', 'radial'):
        response = enriched_bordered_current_response(cell['jacobian'],
            muon['master_source'], step, rep, frame=frame)
        border = np.block([[cell['jacobian'], response['auxiliary_Gauss_column']],
            [response['frame_matrix'], np.zeros((2, 2))]])
        forcing = np.vstack((-enriched_midpoint_source_rows(muon['master_source'], step), np.zeros((2, 8))))
        readout = np.c_[step * electron['master_source'].T @ midpoint, np.zeros((8, 2))]
        paired = step * electron['master_source'].T @ response['midpoint_response']
        certificate = exact_stored_bordered_pairing(border, forcing, readout)
        fit = exact_stored_fermi_template_fit(template['template_tensor'],
            certificate['paired_current_lower'], certificate['paired_current_upper'])
        rows.append(dict(frame=frame, response=response, electron_muon_current=paired,
            electron_muon_exact_stored_certificate=certificate, local_Fermi_template_fit=fit))
    return dict(side=r['side'], stage=stage, coordinate_midpoint=time,
        stored_step=h, chronological_step=step, muon_source=muon, electron_source=electron,
        applications=rows, local_Fermi_template=template,
        named_frame_electron_muon_difference=float(np.linalg.norm(
            rows[0]['electron_muon_current'] - rows[1]['electron_muon_current'])),
        all_original_358_rows_retained=True, inherited_wall_image_count=1,
        physical_low_energy_Fermi_coefficient=None, physical_E_kappa=None,
        physical_mass_unit_or_Pauli_completed=False,
        error_scope='Exact-stored bordered solve/template intervals; source/Cayley/action formation, finite time/angular representation and physical low-energy current reduction are separate.')
