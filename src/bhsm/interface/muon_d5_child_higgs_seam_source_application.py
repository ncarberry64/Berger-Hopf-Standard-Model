"""Consume the once-only child Higgs seam on evaluated parent trace columns.

These are independent-normal-profile NUMERATOR coefficients.  The known
lepton restriction of the joint Spin/SU2/U1 lift is derived here, rather
than extending an arbitrary hypercharge root to the whole SM carrier.
No child section, h, profile, density or physical outer state is selected.
"""
from __future__ import annotations

import numpy as np

from .muon_common_higgs_seam_insertion import fixed_intrinsic_higgs_vertices
from .muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace


def operator_consumed_lepton_lift():
    """All Spin4 L6/7 and conjugate e_c14, not the retained pair36."""
    indices=[];powers=[]
    for family in range(3):
        for spin in range(4):
            for internal in (6,7):
                indices.append(128*family+16*spin+internal);powers.append(-1)
        for spin in range(4):
            indices.append(128*family+64+16*spin+14);powers.append(-2)
    return np.eye(384)[:,indices],np.asarray(powers)


def lepton_middle_jet(known_middle128,known_middle_first128,unit_Higgs_phase):
    """Known joint middle and seven unassigned map-source coefficients.

    Y_L/Y_H=-1, Y_eR/Y_H=-2.  Hence only integer powers of the already
    solved Higgs phase are consumed. The common Spin-cover sign remains
    unselected and multiplies the resulting section coefficients.
    """
    C,powers=operator_consumed_lepton_lift();K=np.asarray(known_middle128)
    Kx=np.asarray(known_middle_first128);u=complex(unit_Higgs_phase)
    if K.shape!=(128,128) or Kx.shape!=(6,128,128) or abs(abs(u)-1)>2e-12:
        raise ValueError('actual joint128 middle, six source columns and unit Higgs phase required')
    phase=np.diag(u**powers);base=C.T@np.kron(np.eye(3),K)@C
    value=base@phase
    free=np.array([C.T@np.kron(np.eye(3),a)@C@phase for a in Kx]
        +[value@np.diag(1j*powers)])
    return value,free


def child_seam_factors(endpoint,child_density,full=None):
    """Recover action-owned factors from held E1 values, without replay.

    Bulk child gauge is inherited pp-rp+rc, but the original action's
    intrinsic H vertex depends only on own H and wall geometry. This
    recovery therefore does not reuse the endpoint's own-gauge audits.
    """
    f=full_d5_localized_lepton_trace() if full is None else full
    W=f['localized_lepton18_trace_lift'];G0=np.kron(np.eye(3),f['gamma5D_self_dual128'][0])
    G4=np.kron(np.eye(3),f['gamma5D_self_dual128'][4]);rho=complex(child_density)
    if rho.imag!=0 or rho.real<=0:raise ValueError('positive original induced surface density required')
    S=np.kron(np.eye(3),np.asarray(endpoint['outgoing_plus_spin_boost128']))
    SI=np.linalg.inv(S);B=np.asarray(endpoint['outgoing_Bhat'])
    Chat=G0@S@G0@W;J=1j*rho.real*G0@S@G4@SI
    JC=np.linalg.solve(J,Chat);Cbar=G0@Chat
    V=fixed_intrinsic_higgs_vertices();H=np.asarray(endpoint['outgoing_raw268'])[260:264]
    mass=np.einsum('c,cij->ij',H,V)
    return dict(B=B,Chat=Chat,J=J,jump_factor=JC,action_factor=-Cbar,
        density=rho.real,vertices=V,mass=mass,Gamma0=G0,
        plus_spin=S,plus_spin_inverse=SI)


def apply_ordered_event_seam(left,D_child_inverse,middle,D_parent,coordinates):
    """Ordered application conditional on full event-map lepton closure.

    This routine has no identity-map defaults. A formal normalized kernel
    contraction below is not a substitute for this physical application.
    """
    L,Dc,K,Dp,q=map(np.asarray,(left,D_child_inverse,middle,D_parent,coordinates))
    if L.shape[-1]!=36 or any(a.shape!=(36,36) for a in (Dc,K,Dp)) or q.shape[0]!=36:
        raise ValueError('explicit same-domain36 child inverse/parent event maps required')
    return L@Dc@K@Dp@q


def apply_ordered_full_event_seam(left,D_child_inverse,middle,D_parent,coordinates):
    """Unrestricted ordered application with every physical map explicit."""
    L,Dc,K,Dp,q=map(np.asarray,(left,D_child_inverse,middle,D_parent,coordinates))
    if L.shape[-1]!=384 or any(a.shape!=(384,384) for a in (Dc,K,Dp)) or q.shape[0]!=384:
        raise ValueError('explicit same-domain384 child inverse/middle/parent event maps required')
    return L@Dc@K@Dp@q


def consume_child_higgs_seam(endpoint,affine,joint,parent_h):
    """Execute deltaH seam and known state/map products on saved traces.

    All output rows18 are exact low-rank factors: deltaN Gamma=JC rows18,
    deltaSbar Gamma=-Gamma0 Chat rows18.  Their independent LR/RL normal
    factors, moving density/frame, total deltaF_B and outer rows stay open.
    """
    rho=complex(affine['wall_child_wall_lapse'])*complex(affine['wall_child_wall_radius'])**3
    sf=child_seam_factors(endpoint,rho);C,_=operator_consumed_lepton_lift()
    Sc=np.kron(np.eye(3),np.asarray(affine['wall_child_spin_boost128']))
    BScC=sf['B']@Sc@C
    annihilator=sf['B']@Sc@(np.eye(384)-C@C.T)
    if np.max(abs(annihilator))>2e-13:
        raise ValueError('seam consumes an additional carrier; partial hypercharge lift is insufficient')
    names=('plus_seed','minus_seed','minus_LR','minus_RL','plus_homogeneous','minus_homogeneous')
    output=dict(consumed_lepton_lift384x36=C,child_canonical_J384=sf['J'],
        child_jump_left_factor384x18=sf['jump_factor'],
        child_action_left_factor384x18=sf['action_factor'],child_Bhat18x384=sf['B'],
        child_surface_density=np.array(sf['density']))
    PL=np.diag(np.r_[np.ones(12),np.zeros(6)]);PR=np.eye(18)-PL
    report=[]
    for family,index in enumerate(np.asarray(joint['initial_candidate_index'],int)):
        K,Kx=lepton_middle_jet(joint['known_middle128'][family],
            joint['known_middle_free_rotation_first128'][family],joint['Higgs_unit_phase'][family])
        dH=np.column_stack((joint['child_raw_field_Higgs_source_correction'][family,260:264],
            joint['child_raw_field_Higgs_free_rotation_phase_coefficients'][family,260:264])).T
        dM=np.einsum('xc,cij->xij',dH,sf['vertices'])
        base='candidate'+str(int(index))+'_'
        output[base+'known_middle36']=K;output[base+'known_middle_free_first36']=Kx
        output[base+'Higgs_source_real4']=dH
        channel_reports={}
        for channel,L,R in (('LR',PL,PR),('RL',PR,PL)):
            prefix=base+channel+'_';T=sf['density']*L@sf['mass']@R
            Tx=sf['density']*np.einsum('ij,xjk,kl->xil',L,dM,R,optimize=True)
            value_rows=T@BScC@K
            Hrows=np.einsum('xij,jk,kl->xil',Tx,BScC,K,optimize=True)
            maprows=np.einsum('ij,jk,xkl->xil',T,BScC,Kx,optimize=True)
            # A low-rank representation retains all original384 row contacts.
            output[prefix+'background_rows18x36']=value_rows
            output[prefix+'Higgs_source_rows8x18x36']=Hrows
            output[prefix+'map_source_rows7x18x36']=maprows
            output[prefix+'background_left_kernel18x36']=T@BScC
            output[prefix+'Higgs_source_left_kernels8x18x36']=np.einsum('xij,jk->xik',Tx,BScC,optimize=True)
            output[prefix+'background_left_kernel18x384']=T@sf['B']@Sc
            output[prefix+'Higgs_source_left_kernels8x18x384']=np.einsum('xij,jk->xik',Tx,sf['B']@Sc,optimize=True)
            N=sf['jump_factor']@T@sf['B']
            cached=np.asarray(endpoint['outgoing_'+channel+'_Nhat'])
            details={}
            for label in names:
                q=np.asarray(affine[label+'_value']);q36=C.T@q
                output[base+label+'_actual_parent_coordinates36']=q36
                output[label+'_actual_parent_coordinates384']=q
                val=value_rows@q36;newH=np.einsum('xij,jk->xik',Hrows,q36,optimize=True)
                mapfirst=np.einsum('xij,jk->xik',maprows,q36,optimize=True)
                output[prefix+label+'_background_rows18']=val
                output[prefix+label+'_Higgs_source_rows18']=newH
                output[prefix+label+'_map_source_rows18']=mapfirst
                # Original J deltaN + Gamma0 deltaSbar=0 with Gamma0 once.
                weak=(sf['J']@sf['jump_factor']-sf['Chat'])@newH[0]
                entry=dict(columns=q.shape[1],Higgs_particular_norm=float(np.linalg.norm(newH[0])),
                    Higgs_particular_max=float(np.max(abs(newH[0]))),
                    Higgs_map_columns_max=float(np.max(abs(newH[1:]))),
                    original_weak_first_max=float(np.max(abs(weak))),
                    background_row_rank=int(np.linalg.matrix_rank(val,tol=1e-12)),
                    new_Higgs_particular_row_rank=int(np.linalg.matrix_rank(newH[0],tol=1e-12)))
                if 'homogeneous' in label:
                    side=label.split('_')[0]
                    if not np.array_equal(q,np.asarray(parent_h[side+'_h_value'])):
                        raise ValueError('retained h value identity changed')
                    qx=C.T@np.asarray(parent_h[side+'_h_corrected_source'])
                    output[base+label+'_actual_parent_corrected_source36']=qx
                    output[label+'_actual_parent_corrected_source384']=np.asarray(parent_h[side+'_h_corrected_source'])
                    state=value_rows@qx
                    known=newH.copy();known[0]+=state;known[1:]+=mapfirst
                    output[prefix+label+'_corrected_parent_state_rows18']=state
                    output[prefix+label+'_known_joint_source_rows18']=known
                    entry['corrected_parent_state_max']=float(np.max(abs(state)))
                    entry['remaining_h']=q.shape[1]
                details[label]=entry
            channel_reports[channel]=dict(saved_seam_value_identity_max=float(np.max(abs(N-cached))),
                consumed_direction_operator_rank=int(np.linalg.matrix_rank(Hrows[0],tol=1e-12)),
                background_operator_norm2=float(np.linalg.norm(value_rows,2)),
                Higgs_source_operator_norm2=float(np.linalg.norm(Hrows[0],2)),operands=details)
        report.append(dict(initial_candidate_index=int(index),channels=channel_reports))
    checks=dict(original_J_inverse_factor_max=float(np.max(abs(sf['J']@sf['jump_factor']-sf['Chat']))),
        exactly_annihilated_other_carrier_max=float(np.max(abs(annihilator))))
    record=dict(classification='EXECUTED_NEW_CHILD_HIGGS_SEAM_SOURCE_ON_ACTUAL_PARENT_TRACE_FAMILY',
        original_equations='J deltaN Gamma=Chat rho deltaM B Gamma; deltaSbar Gamma=-Gamma0 Chat rho deltaM B Gamma',
        normalization='rows are independent LR/RL profile-separated numerators; no uL/uR or density-incidence factor assigned',
        normal_factors=dict(LR='1/(u_L_plus*u_R_minus)',RL='1/(u_L_minus*u_R_plus)'),
        numerical_contraction_scope='FORMAL_UNNORMALIZED_COEFFICIENT_CONTRACTIONS only; reported L K q products are not physical event reconstructions and do not assign event D_child_inverse or D_parent',
        ordered_physical_application='L18x36 D_child_inverse36 K36 D_parent36 q36; both independent event density/normal maps and their derivatives remain unassigned, in this order',
        lepton_restriction_condition='the36 ordered application is conditional on both complete event D maps preserving the consumed lepton36; vertex annihilation alone does not prove that closure',
        unrestricted_physical_application='L18x384 D_child_inverse384 K_full384 D_parent384 q384; full left kernels and actual384 parent values/sources retained, complete D maps and K outside the derived lepton block unassigned',
        ordered_physical_Jacobi='deltaL Dc^-1 K Dp q + L delta(Dc^-1) K Dp q + L Dc^-1 deltaK Dp q + L Dc^-1 K deltaDp q + L Dc^-1 K Dp [deltaq + (dq composed F_B) total_deltaF_B]; moving child point included only in total_deltaF_B',
        known_parent_state_product='formal normalized coefficient old N times corrected fixed-E1 parent q_source; its physical application retains ordered D_child_inverse K D_parent and their derivatives',
        known_map_product='formal normalized coefficient old N times all7 known middle rotation/phase source columns; physical product retains both event D maps; no map-source coordinate selected',
        event_D_child_inverse=None,event_D_parent=None,event_D_derivatives=None,
        full_D_lepton_block_closure_proved=False,full_middle_outside_consumed_lepton_block=None,
        free_state_product='background_rows18 multiplies independent deltaa and deltah; all366h per time node retained',
        moving_point_scope='fixed E1 local factors; complete parent gradient times total deltaF_B and child frame/density variations remain independent and are not appended twice',
        source_extension='joint equation-derived H and wall-gauge additions have constant own raw coefficient extension only; extra own coordinate-time source held zero for this provisional finite application',
        inherited_child_scope='pp-rp+rc bulk gauge inheritance does not replace own intrinsic H seam; own-gauge endpoint audits not reused',
        consumed_carrier='all Spin4 particle L6/7 and conjugate e_c14 across3families; distinct from retained particle/antiparticle36',
        phase_rule='u_H^-1 on L, u_H^-2 on e_R; integer powers require no full-SM fractional phase selection',
        checks=checks,candidates=report,physical_map_selected=False,normal_profile_normalization=None,
        child_section_or_h_selected=False,complete_physical_derivative=False,physical_admission=False,physical_guard=2e-10,
        once_only_local_accounting='existing Higgs seam source only; no bulk D5 Higgs mass or second Maxwell/Higgs subtraction',
        remaining='ordered event D maps and derivatives, child D5 section/source, normal/profile derivatives, total base pullback, moving frame/density, outer/formation/native/cutoff equations and physical state',
        error_scope='finite coefficient arithmetic, with saved parent bulk/source nonpasses retained; no continuum bound or physical residual inferred',
        NEXT_OPERAND='consume these new seam coefficients with the corrected child operator and complete base/frame/density/profile contacts in the existing event/formation equations')
    return output,record
