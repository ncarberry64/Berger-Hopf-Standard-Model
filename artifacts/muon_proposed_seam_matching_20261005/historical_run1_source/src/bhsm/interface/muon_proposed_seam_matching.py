"""Direct localized matching of the NOT-ADOPTED dynamic seam proposal.

Only cached node3 actions and the instantaneous metric reconstruction are
used. No parent production, complement elimination or native solve occurs.
The physical e_R radial coefficients follow the proposed common scalar
inclusion; this is not a completed conjugate-carrier/global realization.
"""
from __future__ import annotations
import numpy as np
from flint import arb, ctx
from bhsm.interface.muon_parent_maxwell_velocity import current_parent_fields
from bhsm.interface.muon_proposed_dynamic_seam import charged_left_projector


def enclosure(x):
    return dict(arb=str(x), interval=[float(np.nextafter(float(x.lower()),-np.inf)),
                                    float(np.nextafter(float(x.upper()),np.inf))])


def coefficients(point, wall, cut, receipt, grid):
    """Full-cap first-action coefficients in one fixed node3 convention.

    The metric producer supplies missing r,A,B values, not a new trajectory
    or field action. Time jets are the saved node3 proper-clock jets.
    """
    ctx.prec=192
    if not np.array_equal(point['actual_state'],wall['actual_state']):
        raise ValueError('node3 state mismatch')
    if not np.array_equal(point['Y_tau'],wall['actual_Y_tau']):
        raise ValueError('node3 proper-clock mismatch')
    f=current_parent_fields(point['actual_state'][None],
        np.array([np.log(float(wall['radius']))]),grid)
    rho=cut['points'];cells=cut['cells'];w=cut['radial_weights']
    if len(rho)!=512 or set(cells.tolist())!=set(range(64)):
        raise ValueError('required full-cap512-point cache absent')
    x=(rho-grid[cells])/np.diff(grid)[cells]
    interp=lambda z:z[cells]*(1-x)+z[cells+1]*x
    r,C,A,B=(interp(f[key][0]) for key in ('base_radius','C_rho','A','B'))
    nu=point['volume']/point['Cauchy']
    bg=-B/(A*np.hypot(A,B))
    Ct=interp(point['C_tau_nodes']);rt=interp(point['r_tau_nodes'])
    I=arb(receipt['I']['arb']);Idot=arb(receipt['I_tau']['arb'])
    H=arb(float(receipt['H']));Rb=arb(float(wall['radius']));Tb=arb(float(receipt['T_b']))
    mu=arb(float(wall['M4']));vol=point['volume'];u=point['u']
    probability=[arb(float(a))*arb(float(b))*arb(float(c))**2/mu for a,b,c in zip(w,vol,u)]
    moment=lambda array:sum((p*arb(float(a)) for p,a in zip(probability,array)),arb(0))
    nv=moment(np.ones(len(w)));at=moment(1/nu);aa=moment(1/r)
    ag=moment(bg);a0=moment(point['a0'])
    # Preserve the action-generated direct Fourier lapse jet and I_tau.
    dl=[arb(float(ct))/arb(float(cc))-Idot/I for ct,cc in zip(Ct,C)]
    at_tau=sum((p*(d-arb(float(l)))/arb(float(v))
                for p,d,l,v in zip(probability,dl,point['Lnu_direct'],nu)),arb(0))
    aa_tau=sum((p*(d/arb(float(rr))-arb(float(dr))/arb(float(rr))**2)
                for p,d,rr,dr in zip(probability,dl,r,rt)),arb(0))
    nv_tau=sum((p*d for p,d in zip(probability,dl)),arb(0))
    Z=1+at;N=1+nv;spatial=aa+1/Rb
    if not Z>0 or not N>0:raise ArithmeticError('positive actual scalar residues required')
    c=1/Z.sqrt();c_tau=-at_tau*c/(2*Z)
    wallg=arb(float(wall['wall_bg_reference']))
    result=dict(parent_volume_norm=nv,parent_time=at,parent_angular=aa,
        parent_commonA=ag,parent_raw_zero_time=a0,parent_volume_norm_tau=nv_tau,
        parent_time_tau=at_tau,parent_angular_tau=aa_tau,
        joint_volume_norm=N,joint_Cauchy_norm=Z,Z_L=Z,Z_R=Z,Z_H=arb(1),
        canonical_field_C=c,canonical_field_C_tau=c_tau,
        canonical_volume_norm=N/Z,canonical_Cauchy_norm=arb(1),
        raw_spatial=spatial,canonical_spatial=spatial/Z,target_spatial=1/Rb,
        spatial_ratio=Rb*spatial/Z,spatial_residual=(aa-at/Rb)/Z,
        raw_commonA=ag+wallg,canonical_commonA=(ag+wallg)/Z,
        target_commonA=wallg,commonA_residual=(ag-at*wallg)/Z,
        raw_photon=Tb*spatial,canonical_photon=Tb*spatial/Z,target_photon=Tb/Rb,
        photon_residual=Tb*(aa-at/Rb)/Z,
        raw_photon_tau=Tb*(aa_tau-H*aa/2-3*H/(2*Rb)),
        canonical_photon_tau=Tb*(aa_tau-H*aa/2-3*H/(2*Rb))/Z
                             -Tb*spatial*at_tau/Z**2,
        raw_Yukawa_factor=arb(1),canonical_Yukawa_factor=1/Z,
        Yukawa_factor_residual=1/Z-1,canonical_Yukawa_factor_tau=-at_tau/Z**2,
        raw_time_comparison=a0+3*H/2,
        raw_time_symmetric=(at_tau+3*H*Z)/2,
        raw_time_comparison_defect=a0+3*H/2-(at_tau+3*H*Z)/2,
        canonical_time_symmetric=3*H/2,
        canonical_time_comparison=(a0+3*H/2-at_tau/2)/Z,
        log_Grassmann_Jacobian_density_symbolic_coefficient=Z.log())
    z=float(Z.mid());cz=float(c.mid());ct=float(c_tau.mid())
    fields=dict(rho=rho,cells=cells,quadrature_weights=w,nu=nu,r=r,C=C,A=A,B=B,
        C_tau=Ct,r_tau=rt,Lnu_direct=point['Lnu_direct'],probability=np.array([float(p.mid()) for p in probability]),
        actual_state=point['actual_state'],actual_Y_tau=point['Y_tau'],
        physical_chiral_Z=np.array([z,z]),canonical_field_C=np.array([cz,cz]),
        canonical_field_C_tau=np.array([ct,ct]),source_coordinates=wall['source_coordinates'])
    guards=dict(nu_relative_reconstruction=float(np.max(np.abs(nu-interp(f['proper_lapse'][0]))/nu)),
        volume_relative_reconstruction=float(np.max(np.abs(vol-2*np.pi**2*nu*C*r**3)/vol)),
        all64_cap_cells=True,source_supported_only_norm=False,
        full_cap_I_input=receipt['I'],full_cap_I_tau_input=receipt['I_tau'],
        derivative_clock='same node3 branch24 boundary proper tau; cached Y_tau/C_tau_nodes/r_tau_nodes and direct Fourier Lnu',
        all_total_photon_state_jets_evaluated=False)
    return result,fields,guards


def actual_maps(coeff,wall,radial,contact,proposal,Y):
    """New first-order coefficient maps, not squared wall/native Grams."""
    if not np.array_equal(proposal['actual_state'],wall['actual_state']) or not np.array_equal(proposal['source_coordinates'],wall['source_coordinates']):
        raise ValueError('proposed readout/source frame is not node3')
    G=radial['common_parent_Gamma'];g0=G[0];P=charged_left_projector()
    val=lambda k:float(coeff[k].mid())
    Z=val('Z_L');aa=val('parent_angular');ag=val('parent_commonA');a0=val('parent_raw_zero_time')
    data=dict(Y_owned=Y,Y_canonical=Y/Z,Y_residual=(1/Z-1)*Y,
        Y_canonical_tau=val('canonical_Yukawa_factor_tau')*Y,
        chiral_projector_L=P,common_parent_Gamma=G)
    proof={};max_cancel=0.
    for n in (1,3):
        xi=wall[f'normalized_wall_W_input_n{n}'];E=radial[f'angular_E_n{n}']
        app=lambda m,z:np.einsum('oi,imkj->omkj',m,z,optimize=True)
        angular=sum(np.einsum('oi,imkj,vm->ovkj',1j*G[a+1],xi,E[a],optimize=True) for a in range(3))
        angular+=app(radial['angular_spin'],xi)
        parent0=app(a0*1j*G[0]+ag*radial['commonA_gauge_unit'],xi)+aa*angular
        wall0=wall[f'kinetic_reference_W_0_n{n}']
        raw0=parent0+wall0
        rawt=val('Z_L')*app(1j*G[0],xi)
        # This retains the supplied unsymmetrized compression as comparison.
        # The symmetric action's temporal connection is recorded separately.
        canonical0=app(g0,raw0)/Z-.5*val('parent_time_tau')/Z*1j*xi
        symmetric0=canonical0+1j*(val('raw_time_symmetric')-val('raw_time_comparison'))/Z*xi
        canonicalt=app(g0,rawt)/Z
        target0=app(g0,wall0)
        data.update({f'parent_localized_D0_n{n}':parent0,
            f'joint_raw_D0_n{n}':raw0,f'joint_raw_Dtau_n{n}':rawt,
            f'canonical_action_A0_comparison_n{n}':canonical0,
            f'canonical_action_A0_symmetric_n{n}':symmetric0,
            f'canonical_action_Atau_n{n}':canonicalt,
            f'target_action_A0_n{n}':target0,
            f'canonical_action_residual_comparison_n{n}':canonical0-target0})
        data[f'canonical_action_residual_symmetric_n{n}']=symmetric0-target0
        # Reuse the accepted conditional J; independently use cached WBp.
        wb=app(P,wall[f'normalized_wall_p_input_n{n}'])
        chi=proposal[f'J_chi_left_n{n}']
        total=wb+chi
        max_cancel=max(max_cancel,float(np.max(np.abs(total))))
        data.update({f'F_L_WBp_n{n}':wb,f'F_L_chi_reused_n{n}':chi,
            f'F_L_compact_p_n{n}':np.zeros_like(wb),f'F_L_full_field_identity_residual_n{n}':total,
            f'canonical_F_L_full_field_identity_residual_n{n}':np.sqrt(Z)*total})
        # Actual same b-source kernels; all retained rank16 input/output
        # channels remain. These are not a complete physical e_R realization.
        unit=contact[f'Xi_A_unit_n{n}']
        action=np.einsum('oi,Aicmk->Aocmk',g0,unit,optimize=True)
        data.update({f'raw_same_b_vertex_kernel_n{n}':val('raw_photon')*action,
            f'canonical_same_b_vertex_kernel_n{n}':val('canonical_photon')*action,
            f'target_same_b_vertex_kernel_n{n}':val('target_photon')*action,
            f'same_b_vertex_residual_kernel_n{n}':val('photon_residual')*action})
    proof['full_compact_source_readout_cancellation_max_abs']=max_cancel
    proof['old_conditional_J_recomputed']=False
    proof['source_zero_reason']='compact hat has separated material support; matched linear trace readout applied to FULL p gives zero'
    proof['e_R_scope']='same scalar radial Z_R from the proposed opposite-orientation physical singlet inclusion; e_c kernels kept as ledger bookkeeping, no extra quantum trace or full e_R/global-domain claim'
    return data,proof


def cached_action_comparison(coeff,wall,point,radial,cut):
    """Contract saved selected DW/DtauW, rather than regenerate parent actions."""
    result={};mu=float(wall['M4']);weights=cut['radial_weights']*point['volume']*point['u']/mu
    c=wall['source_coordinates'];g0=radial['common_parent_Gamma'][0]
    for n in (1,3):
        xi=np.einsum('omki,i->omk',wall[f'normalized_wall_W_input_n{n}'],c,optimize=True)
        saved0=np.einsum('g,gomk->omk',weights,point[f'DWp_n{n}'],optimize=True)
        savedt=np.einsum('g,gomk->omk',weights,point[f'DtauW_n{n}'],optimize=True)
        E=radial[f'angular_E_n{n}'];G=radial['common_parent_Gamma']
        angular=sum(np.einsum('oi,imk,vm->ovk',1j*G[a+1],xi,E[a]) for a in range(3))
        angular+=np.einsum('oi,imk->omk',radial['angular_spin'],xi)
        a0,ag,aa,at=[float(coeff[k].mid()) for k in ('parent_raw_zero_time','parent_commonA','parent_angular','parent_time')]
        expected0=np.einsum('oi,imk->omk',a0*1j*G[0]+ag*radial['commonA_gauge_unit'],xi)+aa*angular
        expectedt=at*np.einsum('oi,imk->omk',1j*G[0],xi)
        result[f'n{n}']=dict(saved_full_parent_zero_action_projection_residual=float(np.linalg.norm(saved0-expected0)),
            saved_full_parent_time_action_projection_residual=float(np.linalg.norm(savedt-expectedt)))
    return result
