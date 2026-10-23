"""Full retained D5 differential coefficients and weak trial forms.

The original ordered Lorentz expression is retained.  A separately named
covariant product placement D_tau+W is exported; it is not identified with
the completed AE4 native operator or a Wick-continued physical action.
All three families, particle/conjugate Spin4 x SM16 fibres and supplied
angular modes remain.  Identical family blocks are applied, not projected.
"""
from __future__ import annotations

import numpy as np


def _finite(a,shape,name):
    a=np.asarray(a,complex)
    if a.shape!=shape or not np.isfinite(a).all():
        raise ValueError(name+": finite explicit shape "+str(shape)+" required")
    return a


def full_d5_differential_coefficients(c,angular_derivatives,*,sheet_orientation,
        full_representation=None,sigma_eta_contacts=None):
    """Bind the actual source coefficient schema to full strong expressions.

    sigma_eta_contacts, when given, contains explicit particle/conjugate
    (q,64h,64h) matrices. Otherwise the existing sigma-foliation owner is
    called using c's actual sigma derivatives. No radial eta substitute.
    These are coefficient values; total source jets are not fabricated.
    """
    from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
    from bhsm.interface.muon_holomorphic_d5_trace_action import d5_sigma_foliation_eta
    eps=int(sheet_orientation)
    if eps!=sheet_orientation or eps not in(-1,1):raise ValueError("original eta orientation required")
    E=np.asarray(angular_derivatives,complex)
    if E.ndim!=3 or E.shape[0]!=3 or E.shape[1]!=E.shape[2] or not E.shape[1] or not np.isfinite(E).all():
        raise ValueError("all three same-space angular coefficient derivatives required")
    h=E.shape[1];q=len(np.asarray(c['lapse']));d=64*h
    f=full_d5_localized_lepton_trace() if full_representation is None else full_representation
    names=('lapse','radial_coframe','radius','coordinate_shift',
           'geometric_time_contact','geometric_radial_contact','surface_proper_clock_rate','volume_density')
    scalar={name:_finite(c[name],(q,),name) for name in names}
    gauge=_finite(c['gauge_connection_material'],(q,5,4),'material gauge connection')
    if any(np.any(scalar[name]==0) for name in ('lapse','radial_coframe','radius')):
        raise ValueError("nonnull original regular coframe required")
    blocks={}
    for branch in ('particle','conjugate'):
        gamma=_finite(f['gamma5D_'+branch],(5,4,4),'owned Clifford')
        generators=np.asarray(f['unitTr16_gauge_particle'],complex)
        if branch=='conjugate':generators=generators.conj()
        g=np.array([np.kron(a,np.eye(16*h)) for a in gamma]);I=np.eye(d,dtype=complex)
        internal=np.array([np.kron(np.eye(4),np.kron(a,np.eye(h))) for a in generators])
        if sigma_eta_contacts is None:
            eta=d5_sigma_foliation_eta(c,gamma=gamma,carrier_count=16,
                angular_count=h,sheet_orientation=eps)['sigma_normal_eta_contact']
        else:eta=_finite(sigma_eta_contacts[branch],(q,d,d),'actual sigma eta contact')
        angular=sum(np.kron(np.kron(1j*gamma[a+1],np.eye(16)),E[a]) for a in range(3))
        spin=np.kron(-1.5j*gamma[1]@gamma[2]@gamma[3],np.eye(16*h))
        records={name:[] for name in ('time','radial','body','energy','Dtau_time','Dtau_radial',
                  'Dtau_body','W_radial','W_body','A_time','A_radial','A_body','A_energy')}
        for r in range(q):
            N,C,R,z,h0,h4,ell=(scalar[name][r] for name in names[:-1])
            A=np.einsum('fc,cij->fij',gauge[r],internal)
            dt=I/N;dr=-z*I/N;db=h0*I+(A[0]-z*A[1])/N
            wr=-1j*eps*g[0]@g[4]/C
            wb=-g[0]@(1j*eps*g[4]*h4+eta[r]+(spin+angular)/R
                +1j*eps*g[4]@A[1]/C+sum(1j*g[a+1]@A[a+2]/R for a in range(3)))
            values=dict(time=1j*g[0]@dt,radial=g[0]@(1j*dr-wr),
                body=g[0]@(1j*db-wb),energy=g[0]*ell/N,
                Dtau_time=dt,Dtau_radial=dr,Dtau_body=db,W_radial=wr,W_body=wb,
                A_time=dt,A_radial=dr+wr,A_body=db+wb,A_energy=-1j*ell*I/N)
            for name,value in values.items():records[name].append(value)
        blocks[branch]={name:np.array(value) for name,value in records.items()}
        blocks[branch].update(gamma0=g[0],sigma_eta_contact=eta,
            angular_Dirac_matrix=angular,round_spin_Dirac_matrix=spin)
    return dict(blocks=blocks,angular_derivatives=E,angular_count=h,radial_count=q,
        block_width=d,full_width=6*d,carrier_order='family3,(particle SM16,conjugate SM16),Spin4,internal16,angular',
        volume_density=scalar['volume_density'],sheet_orientation=eps,
        original_Lorentz_split='D_L(E)=Gamma0*(i D_tau-W)+E*Gamma0*ell_Sigma/N',
        candidate_product_placement='A_formal=D_tau+W; formal same-Lorentz-phase contact A_E=-i ell_Sigma/N',
        explicit_native_conversion_required=(
            'Bind the actual native time/coframe map, metric-compatible density/frame isometry, '
            'both output/input positive pairings, full trace/adjoint domain, and physical-E dictionary; '
            'the formal Lorentz phase insertion is not automatically a Euclidean/native energy insertion.'),
        same_reduced18_body_substituted=False,all_families_and_angular_rows_retained=True,
        source_coefficient_jets_evaluated=False,physical_native_or_AE4_identification=False,
        physical_outgoing_or_convergence_claimed=False,source_coefficients_conjugated=False)


def apply_full_d5_expression(coefficients,value,radial_derivative,time_derivative,*,
        energy=0j,placement='lorentz'):
    """Apply all full-fibre blocks to arbitrary, possibly mixed trial columns."""
    c=coefficients;q,d,D=c['radial_count'],c['block_width'],c['full_width']
    V=np.asarray(value,complex)
    if V.ndim!=3 or V.shape[:2]!=(q,D):raise ValueError("full q x 384h x columns trial required")
    V=_finite(V,V.shape,'trial');Vr=_finite(radial_derivative,V.shape,'radial derivative')
    Vt=_finite(time_derivative,V.shape,'coordinate-time derivative')
    energy=complex(energy)
    if not np.isfinite(energy):raise ValueError("finite explicit phase frequency required")
    if placement not in('lorentz','formal_product'):raise ValueError("explicit Lorentz or formal_product placement required")
    prefix='' if placement=='lorentz' else 'A_'
    out=np.empty_like(V)
    for family in range(3):
        for branch_index,branch in enumerate(('particle','conjugate')):
            sl=slice((2*family+branch_index)*d,(2*family+branch_index+1)*d);b=c['blocks'][branch]
            out[:,sl]=np.einsum('qij,qjk->qik',b[prefix+'time'],Vt[:,sl])
            out[:,sl]+=np.einsum('qij,qjk->qik',b[prefix+'radial'],Vr[:,sl])
            out[:,sl]+=np.einsum('qij,qjk->qik',b[prefix+'body']+energy*b[prefix+'energy'],V[:,sl])
    return out


def full_d5_weak_trial_action(coefficients,value,radial_derivative,time_derivative,
        independent_left,radial_weights,*,energy=0j,placement='lorentz'):
    """Original density-weighted ordered form; the left map is never conjugated."""
    c=coefficients;V=np.asarray(value,complex);q,D=V.shape[:2]
    L=np.asarray(independent_left,complex)
    if L.ndim!=3 or L.shape[0]!=q or L.shape[2]!=D or not np.isfinite(L).all():
        raise ValueError("explicit independent q x test rows x full fibre left map required")
    w=np.asarray(radial_weights,float)
    if w.shape!=(q,) or not np.isfinite(w).all():raise ValueError("same explicit radial weights required")
    acted=apply_full_d5_expression(c,V,radial_derivative,time_derivative,energy=energy,placement=placement)
    measure=w*c['volume_density']
    action=np.einsum('q,qij,qjk->ik',measure,L,acted)
    energy_action=np.empty_like(V);d=c['block_width']
    for family in range(3):
        for b,branch in enumerate(('particle','conjugate')):
            sl=slice((2*family+b)*d,(2*family+b+1)*d)
            key='energy' if placement=='lorentz' else 'A_energy'
            energy_action[:,sl]=np.einsum('qij,qjk->qik',c['blocks'][branch][key],V[:,sl])
    return dict(action=action,phase_frequency_first=np.einsum('q,qij,qjk->ik',measure,L,energy_action),
        point_expression_on_trial=acted,independent_left_map=L,
        source_left_conjugated=False,placement=placement,
        physical_native_or_AE4_identification=False,physical_E_or_B_total_derivative=False)


def explicit_positive_trial_form(coefficients,value,radial_derivative,time_derivative,
        *,positive_coordinate_weights,positive_output_block_grams,energy=0j):
    """Mathematical positive form on EXPLICIT supplied real positive pairing.

    The input/output density and time maps remain the caller's declared
    representation. This does not turn the candidate placement into AE4.
    Grams use the exact repeated-family structure, with both 64h branches.
    """
    c=coefficients;q,d,D=c['radial_count'],c['block_width'],c['full_width']
    w=np.asarray(positive_coordinate_weights,float)
    if w.shape!=(q,) or not np.isfinite(w).all() or np.any(w<=0):raise ValueError("explicit positive finite coordinate weights required")
    G=_finite(positive_output_block_grams,(q,2,d,d),'positive output block Grams')
    if np.max(abs(G-G.conj().swapaxes(-1,-2)))>1e-12 or np.min(np.linalg.eigvalsh(G))<=0:
        raise ValueError("actual positive Hermitian output pairing required")
    acted=apply_full_d5_expression(c,value,radial_derivative,time_derivative,energy=energy,placement='formal_product')
    form=np.zeros((acted.shape[-1],acted.shape[-1]),complex)
    for family in range(3):
        for b in range(2):
            z=acted[:,(2*family+b)*d:(2*family+b+1)*d]
            form+=np.einsum('q,qji,qjk,qkl->il',w,z.conj(),G[:,b],z)
    return dict(form=form,point_expression_on_trial=acted,positive_pairing_checked=True,
        physical_native_or_AE4_identification=False,full_fibre_count=D,
        repeated_families_applied=3,physical_derivative_gate=False)
