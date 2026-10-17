"""Original D5 action on explicit partial sigma-collar trial functions.

The normal line and its independently supplied left trial are computational
trial maps. Their transverse derivative is mandatory. Nothing here selects
a retarded tail, fills the remaining normal integral, or identifies a finite
trace border as a physical exterior.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import expm,expm_frechet
from .muon_coupled_phase_trace_projection import _solve


def collar_spin_gauge_transport(omega,omega_first,particle,particle_inverse,
        conjugate,conjugate_inverse,particle_first,particle_inverse_first,
        conjugate_first,conjugate_inverse_first,*,full,sheet_orientation):
    """Reconstruct Spin/gauge maps and independent analytic inverse contacts."""
    eps=int(sheet_orientation)
    if eps not in(-1,1):raise ValueError('original oriented collar required')
    maps=[];duals=[];firsts=[];dual_firsts=[]
    for branch,gauge,inverse,dgauge,dinverse in(
        ('particle',particle,particle_inverse,particle_first,particle_inverse_first),
        ('conjugate',conjugate,conjugate_inverse,conjugate_first,conjugate_inverse_first)):
        G=full['gamma5D_'+branch];A=-.5*eps*G[0]@G[4]*complex(omega)
        dA=-.5*eps*G[0]@G[4]*complex(omega_first)
        S,dS=expm_frechet(A,dA);SI,dSI=expm_frechet(-A,-dA)
        maps.append(np.kron(S,gauge));duals.append(np.kron(SI,inverse))
        firsts.append(np.kron(dS,gauge)+np.kron(S,dgauge))
        dual_firsts.append(np.kron(dSI,inverse)+np.kron(SI,dinverse))
    block=lambda a:np.block([[a[0],np.zeros((64,64),complex)],[np.zeros((64,64),complex),a[1]]])
    T,L,dT,dL=map(block,(maps,duals,firsts,dual_firsts))
    return dict(spin_gauge_transport128=T,spin_gauge_analytic_dual128=L,
        spin_gauge_transport_first128=dT,spin_gauge_analytic_dual_first128=dL,
        analytic_inverse_rows=L@T-np.eye(128),analytic_inverse_first_rows=dL@T+L@dT,
        actual_source_or_trial_coefficients_conjugated=False)


def original_collar_coordinate_action(c,*,gamma,generators,right_value,
        right_normal_first,right_transverse_first,literal_left_value,
        normal_coordinate_velocity,leaf_transverse,eta_mass_outward,
        normal_timelike_outward,normal_radial_outward,sheet_orientation,
        surface_proper_clock,energy):
    """Transform both explicit trial derivatives back to the original D5.

    The two columns (leaf_transverse, normal_coordinate_velocity) give
    derivatives in the supplied collar coordinates. Their inverse supplies
    V_t and V_rho. No derivative is inferred zero from an energy ansatz.
    """
    G=np.asarray(gamma,complex);T=np.asarray(generators,complex)
    V,Vs,Vq,L=map(lambda a:np.asarray(a,complex),(right_value,right_normal_first,right_transverse_first,literal_left_value))
    if G.shape!=(5,4,4)or T.shape!=(4,16,16)or V.shape!=(64,64)or any(a.shape!=V.shape for a in(Vs,Vq,L)):
        raise ValueError('all original Spin4/SM16 trial and independent left rows required')
    F=np.asarray(normal_coordinate_velocity,complex);Xi=np.asarray(leaf_transverse,complex)
    A=np.c_[Xi,F]
    if A.shape!=(2,2)or not np.isfinite(A).all()or abs(np.linalg.det(A))<1e-20:
        raise ValueError('actual nonsingular collar coordinate Jacobian required')
    inverse=np.linalg.inv(A);Vt=inverse[0,0]*Vq+inverse[1,0]*Vs;Vr=inverse[0,1]*Vq+inverse[1,1]*Vs
    eps=int(sheet_orientation);g=np.array([np.kron(v,np.eye(16))for v in G])
    N,C,R,z=(complex(c[k])for k in('lapse','radial_coframe','radius','coordinate_shift'))
    gauge=np.array([np.kron(np.eye(4),v)for v in T]);Ac=np.einsum('fc,cij->fij',c['gauge_connection_material'],gauge)
    GN=eps*normal_radial_outward*g[4]-normal_timelike_outward*g[0]
    D=1j*g[0]*c['geometric_time_contact']+1j*eps*g[4]*c['geometric_radial_contact']+1j*GN*eta_mass_outward
    D+=np.kron(-1.5j*G[1]@G[2]@G[3],np.eye(16))/R
    D+=1j*g[0]@(Ac[0]-z*Ac[1])/N+1j*eps*g[4]@Ac[1]/C
    D+=sum(1j*g[a+1]@Ac[a+2]/R for a in range(3))
    DE=g[0]*complex(surface_proper_clock)/N
    Dr=-1j*g[0]*z/N+1j*eps*g[4]/C
    acted=(D+complex(energy)*DE)@V+1j*g[0]@Vt/N+Dr@Vr
    actedE=DE@V
    Ds=1j*g[0]*inverse[1,0]/N+Dr*inverse[1,1]
    return dict(original_D5_on_trial=acted,original_D5_energy_on_trial=actedE,
        literal_weak_integrand=L@acted,literal_energy_integrand=L@actedE,
        literal_normal_Green_integrand=L@Ds@V,actual_trial_coordinate_time=Vt,
        actual_trial_coordinate_radial=Vr,collar_coordinate_inverse=inverse,
        caller_transverse_trial_derivative_consumed=True)


def partial_two_sheet_collar_trace(action,action_energy,*,full,fixedY_mass,surface_density):
    """Keep the full two-sheet field border and once-only chiral seam.

    The supplied action ALREADY uses its independent Dirac-bar left trial.
    Hence there is no second Gamma0 multiplication. LL12/eR6 incidence is
    in coefficient coordinates, after the explicit mode/Spin point maps.
    """
    K,KE=np.asarray(action,complex),np.asarray(action_energy,complex)
    W=full['localized_lepton18_trace_lift'];D=full['localized_lepton18_literal_dual'];M=np.asarray(fixedY_mass,complex)
    if K.shape!=(2,384,384)or KE.shape!=K.shape or M.shape!=(18,18):
        raise ValueError('complete two384 field fibers and original fixedY18 seam required')
    PL=np.diag(np.r_[np.ones(12),np.zeros(6)]);PR=np.eye(18)-PL
    if np.max(abs(PL@M@PL))+np.max(abs(PR@M@PR))>1e-12:
        raise ValueError('original SH is off-diagonal in its localized LR sheets')
    B=np.c_[PL@D,PR@D];C=np.r_[W@PL,W@PR]
    zeros=np.zeros((384,384),complex);bulk=np.block([[K[0],zeros],[zeros,K[1]]]);bulkE=np.block([[KE[0],zeros],[zeros,KE[1]]])
    seam=-complex(surface_density)*C@M@B;A=bulk+seam
    border=np.block([[A,C],[B,np.zeros((18,18),complex)]])
    rhs=np.r_[np.zeros((768,18),complex),np.eye(18)]
    sol,rs,cs=_solve(border,rhs);rhsE=np.r_[-bulkE@sol[:768],np.zeros((18,18),complex)]
    solE,_,_=_solve(border,rhsE)
    modeR=np.r_[W@PL,W@PR];modeL=np.c_[PL@D,PR@D]
    return dict(partial_two_sheet_Dirac_bar_bulk_action=bulk,partial_two_sheet_Dirac_bar_Higgs_seam=seam,
        partial_two_sheet_Dirac_bar_action=A,partial_two_sheet_Dirac_bar_action_energy=bulkE,
        complete_field_and_chiral_trace_rows=border@sol-rhs,complete_field_and_chiral_trace_energy_rows=border@solE-rhsE,
        complete_field_Poisson=sol[:768],complete_field_Poisson_energy=solE[:768],
        partial_field_Gamma=-sol[768:],partial_field_Gamma_energy=-solE[768:],
        once_only_Higgs_seam_recovery_rows=modeL@seam@modeR+surface_density*M,
        original_full_field_border_row_scale=rs,original_full_field_border_column_scale=cs,
        full_complementary_field_rows_retained=750,LL12_and_conjugate_eR6_on_distinct_eta_sheets=True,
        retarded_or_normalization_admission=False)
