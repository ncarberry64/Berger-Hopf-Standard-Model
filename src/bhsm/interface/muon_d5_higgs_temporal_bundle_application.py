"""Execute original Higgs trace and local temporal bundle equations at E1.

The central factor on the Higgs representation is derived as a necessary
phase, with its perpendicular residual retained. Its lift to the full gauge
group is not selected. Child Higgs field-source coordinates respond through
their original trace equation; no fermion trace or native load is fitted.
"""
from __future__ import annotations
import numpy as np
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation


def complex_higgs(realified):
    a=np.asarray(realified)
    if a.shape!=(4,):raise ValueError('original ReH1,ReH2,ImH1,ImH2 order required')
    return a[:2]+1j*a[2:]


def real_higgs(value):
    a=np.asarray(value)
    if a.shape!=(2,):raise ValueError('one Higgs fundamental section required')
    return np.r_[a.real,a.imag]


def necessary_higgs_phase(parent,child,su2_lift):
    """A necessary unit phase from Hc=u K Hp, with the full residual exposed.

    No argument/logarithm branch or full-SM hypercharge lift is selected.
    If the sections are not parallel, this does not solve their trace law.
    """
    p,c,K=map(np.asarray,(parent,child,su2_lift))
    if p.shape!=(2,) or c.shape!=p.shape or K.shape!=(2,2):
        raise ValueError('same-action Higgs sections and solved SU2 factor required')
    v=K@p;z=np.vdot(v,c)
    if min(np.linalg.norm(p),np.linalg.norm(c),abs(z))<1e-14:
        raise ValueError('nonzero identified Higgs phase operand required')
    phase=z/abs(z)
    return phase,c-phase*v


def temporal_bundle_jet(Ap,Ac,U,kappa,*,Ap_first,Ac_first,kappa_first,U_first):
    """Solve Dt U+Ac U-kappa U Ap=0 and its complete supplied Jacobi row."""
    Ap,Ac,U,Apx,Acx,Ux=map(np.asarray,(Ap,Ac,U,Ap_first,Ac_first,U_first))
    if U.shape!=(2,2) or any(a.shape!=U.shape for a in (Ap,Ac,Apx,Acx,Ux)):
        raise ValueError('all Higgs-representation bundle and vertex firsts required')
    Ut=-Ac@U+kappa*U@Ap
    Utx=(-Acx@U-Ac@Ux+kappa_first*U@Ap+kappa*Ux@Ap+kappa*U@Apx)
    return dict(time=Ut,time_first=Utx,
        original_row=Ut+Ac@U-kappa*U@Ap,
        original_first_row=Utx+Acx@U+Ac@Ux-kappa_first*U@Ap-kappa*Ux@Ap-kappa*U@Apx)


def execute_higgs_temporal_bundle(parent_coefficients,child_coefficients,
        spatial_application,wall_incidence,*,parent_H_time,child_H_time):
    """Execute every algebraic orientation family, without selecting one.

    The field-source particular holds the independent rotation/central/
    moving-point correction slots only in its particular term. Their
    nonzero coefficient matrices are returned and remain free.
    """
    p,c=parent_coefficients,child_coefficients
    Hp,Hc=(complex_higgs(a['intrinsic_H_realified']) for a in (p,c))
    Hpx,Hcx=(complex_higgs(a['intrinsic_H_realified_first'][0]) for a in (p,c))
    Hpt,Hct=map(complex_higgs,(parent_H_time,child_H_time))
    k=complex(wall_incidence['material_clock_differential'])
    kx=complex(wall_incidence['material_clock_differential_first'])
    generators=higgs_u2_real_representation()['complex_generators']
    a0p,a0c=(a['gauge_connection_material'][0,0] for a in (p,c))
    a0px,a0cx=(a['gauge_connection_material_first'][0,0,0] for a in (p,c))
    Ap,Ac,Apx,Acx=(np.einsum('a,aij->ij',a,generators) for a in (a0p,a0c,a0px,a0cx))
    # Unit angular velocities use -i sigma/2, in the fixed original U2 frame.
    J2=np.sqrt(2)*generators[:3]
    fields=[];raws=[];phases=[];before=[];after=[];free=[];temporals=[];temporalx=[];tfree=[];audits=[];middle=[];sources=[];timeports=[]
    reports=[]
    for index,K in enumerate(spatial_application['gauge_SU2_lifts']):
        phase,row=necessary_higgs_phase(Hp,Hc,K);U=phase*K
        source=Hcx-U@Hpx
        correction=-source
        raw=np.zeros(268);raw[260:264]=real_higgs(correction)
        # [base omega3, gauge omega3, Higgs phase angle1]. Base motion acts
        # through angular gradients, which vanish for this represented H0.
        Uf=np.zeros((7,2,2),complex)
        Uf[3:6]=np.array([a@U for a in J2]);Uf[6]=1j*U
        hfree=np.array([a@Hp for a in Uf]).T
        zero=np.zeros((2,2),complex)
        jet=temporal_bundle_jet(Ap,Ac,U,k,Ap_first=Apx,Ac_first=Acx,
            kappa_first=kx,U_first=zero)
        time_free=[]
        for ux in Uf:
            j=temporal_bundle_jet(Ap,Ac,U,k,Ap_first=np.zeros_like(Ap),
                Ac_first=np.zeros_like(Ac),kappa_first=0.,U_first=ux)
            time_free.append(j['time_first'])
        fields.append(real_higgs(correction));raws.append(raw);phases.append(phase)
        before.append(row);after.append(source+correction);free.append(hfree)
        temporals.append(jet['time']);temporalx.append(jet['time_first']);tfree.append(time_free)
        audits.append([np.max(abs(jet['original_row'])),np.max(abs(jet['original_first_row']))]);middle.append(U);sources.append(source)
        timeports.append(np.c_[U@Hpt,-Hct])
        reports.append(dict(candidate_index=index,necessary_Higgs_unit_phase_real_imag=[float(phase.real),float(phase.imag)],
            full_Higgs_value_residual_max=float(np.max(abs(row))),
            before_Higgs_source_residual_max=float(np.max(abs(source))),
            after_Higgs_field_source_residual_max=float(np.max(abs(source+correction))),
            child_Higgs_field_source_correction_max=float(np.max(abs(correction))),
            temporal_bundle_rate_norm=float(np.linalg.norm(jet['time'])),
            temporal_bundle_Xi_rate_norm=float(np.linalg.norm(jet['time_first'])),
            temporal_original_row_max=float(np.max(abs(jet['original_row']))),
            temporal_original_Xi_row_max=float(np.max(abs(jet['original_first_row']))),
            source_child_Higgs_pivot_real_rank=4,physical_map_or_phase_branch_selected=False))
    arrays=dict(parent_Higgs=Hp,child_Higgs=Hc,parent_Higgs_first=Hpx,child_Higgs_first=Hcx,
        parent_temporal_connection=Ap,child_temporal_connection=Ac,
        parent_temporal_connection_first=Apx,child_temporal_connection_first=Acx,
        material_clock_differential=np.array(k),material_clock_differential_first=np.array(kx),
        Higgs_norm_squared_difference=np.array(np.vdot(Hc,Hc)-np.vdot(Hp,Hp)),
        Higgs_necessary_unit_phases=np.array(phases),Higgs_known_middle2=np.array(middle),
        Higgs_value_rows=np.array(before),Higgs_source_rows_before=np.array(sources),
        child_Higgs_field_source_corrections=np.array(fields),child_Higgs_raw_source_corrections=np.array(raws),
        Higgs_source_rows_after=np.array(after),child_Higgs_free_rotation_phase_coefficients=np.array(free),
        Higgs_total_time_pullback_coefficients=np.array(timeports),
        temporal_bundle_time=np.array(temporals),temporal_bundle_time_first_particular=np.array(temporalx),
        temporal_bundle_time_first_free_rotation_phase=np.array(tfree),temporal_bundle_original_rows=np.array(audits))
    report=dict(classification='EXECUTED_ORIGINAL_HIGGS_TRACE_SOURCE_AND_LOCAL_TEMPORAL_BUNDLE_JET',
        original_Higgs_equation='H_child=U_H (H_parent composed with F_B), U_H=u_H K_SU2',
        original_temporal_equation='Dt U_H+A_child,0 U_H-kappa U_H A_parent,0=0',
        phase_condition='u_H=<K Hp,Hc>/abs(<K Hp,Hc>) is necessary; perpendicular full value residual is independently retained',
        phase_periodicity_scope='only a unit factor in Y_H=1/2 representation; no argument branch or full-SM/global gauge lift is selected',
        candidates=reports,source_rotation_phase_coordinates_retained=7,
        moving_point_source='returned parent/child time-gradient coefficients multiply total event-point variations exactly once; no moving point is assigned',
        child_field_correction_scope='four original child H coordinates respond to their trace source equation, with all map/phase/time contacts retained free',
        child_field_source_extension='constant raw intrinsic H correction as a provisional finite source extension; extra own time derivative zero, not a physical state prescription',
        Higgs_normalization='original same-action unnormalized Higgs field; no unit spinor, calibration or unknown normal-profile substitution',
        temporal_scope='local E1 two-sided jet only; no integration into unavailable parent future or child past',
        derivative_scope='both corrected normal/field Xi directions in the original vertices, moving kappa, and all U_first placements; full physical derivative remains open',
        Higgs_bulk_D5_mass_added=False,once_only_intrinsic_Higgs_seam_obligation=True,
        parent_homogeneous_coordinates_retained=3660,outer_conditions_solved=False,physical_admission=False)
    return arrays,report
