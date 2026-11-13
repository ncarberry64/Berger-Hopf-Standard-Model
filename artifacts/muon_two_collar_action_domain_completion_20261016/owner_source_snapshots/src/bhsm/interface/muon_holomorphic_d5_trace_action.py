"""Original D5 coframe coefficients on a trial complex canonical history.

These are the signed unsquared Dirac coefficients, rebuilt from raw268 and
the supplied same-stage parent/reference profiles. Their finite weak trace
realization uses explicit caller trial/dual maps and full Clifford/carrier
matrices. It does not turn a temporal Volterra trace into a field exterior.
"""
from __future__ import annotations

import numpy as np

from .muon_holomorphic_normal_geometry import (
    _geometry_variables, _fields, _sqrt, _response, _compose, _sin, anchored_holomorphic_chart,
)
from .muon_holomorphic_current_source import _profile
from .muon_parent_retarded_hypercharge import WALL
from .muon_parent_maxwell_full_weak import M


def _value_and_first(jet, directions):
    return jet.value, jet.gradient @ directions


def d5_trial_stage_coefficients(raw, raw_first, parent_raw, parent_first,
        reference_pair, reference_first, representation, radial_points, *, side):
    """Rebuild N,C,R,shift, spin density, eta and every gauge placement.

    The fixed reference rho chart has chi=(rho/WALL)*wall and C_rho=C*wall/WALL.
    Its moving-coordinate shift is (beta+rho*wall_dot/WALL)/(wall/WALL).
    The temporal/radial geometric Dirac contacts reduce exactly to
      h0=(lc+3 lR-beta*(cp+3 Rchi/R)-betap)/(2N),
      h4=(Nchi/N+3 Rchi/R)/(2C).
    Thus the coordinate motion is included once, and not confused with an
    independent lapse. The eta profile is the action's current sin(f_eta)
    from the same anchored material chart; no frozen radial profile is used.

    H4 remains the intrinsic seam field, not a second bulk Yukawa mass.
    The full independent 80 gauge coordinates plus pp-rp+rc mechanical
    profile are composed before their values enter this D5 coefficient.
    """
    x = np.asarray(raw, complex);dx = np.asarray(raw_first, complex)
    p = np.asarray(parent_raw, complex);dp = np.asarray(parent_first, complex)
    refs = np.asarray(reference_pair, complex);drefs = np.asarray(reference_first, complex)
    rho = np.asarray(radial_points, float)
    if (x.shape != (268,) or dx.ndim != 2 or dx.shape[0] != 268 or not dx.shape[1]
            or p.shape != x.shape or dp.shape != dx.shape or refs.shape != (2, 268)
            or drefs.shape != (2, 268, dx.shape[1]) or rho.ndim != 1 or not len(rho)
            or np.any(rho <= 0) or np.any(rho > WALL)
            or any(not np.isfinite(a).all() for a in (x, dx, p, dp, refs, drefs, rho))):
        raise ValueError("complete same-stage raw268/parent/reference directions and original positive radial points required")
    if side not in ("parent", "child"):
        raise ValueError("explicit original parent or inherited child required")
    q, v, m, delta, wall_rate, wall, _ = _geometry_variables(x[:100])
    chart = anchored_holomorphic_chart(delta.value)
    wall_fields = _fields(12, q, v, m, wall)
    wall_speed = wall_fields['C']*(wall_rate+wall_fields['beta'])/wall_fields['N']
    surface_clock = wall_fields['N']*_sqrt(1-wall_speed**2)
    names = ("lapse", "radial_coframe", "radius", "coordinate_shift",
             "geometric_time_contact", "geometric_radial_contact", "eta_radial_contact",
             "volume_density", "Cauchy_density", "material_wall", "coordinate_wall_rate",
             "surface_proper_clock_rate", "eta_profile", "eta_profile_radial",
             "radius_log_radial", "lapse_log_radial", "eta_profile_coordinate_time",
             "material_wall_velocity", "sigma", "sigma_radial", "sigma_coordinate_time",
             "sigma_radial_second", "radial_coframe_log_radial", "coordinate_shift_radial")
    values = {k: [] for k in names};first = {k: [] for k in names}
    for r in rho:
        chi = (r/WALL)*wall;f = _fields(12, q, v, m, chi)
        R = f["A"]*f["B"]/_sqrt(f["A"]**2+f["B"]**2)
        lR = f["la"]+f["lb"]-(f["A"]**2*f["la"]+f["B"]**2*f["lb"])/(f["A"]**2+f["B"]**2)
        Rchi = f["ap"]+f["bp"]-(f["A"]**2*f["ap"]+f["B"]**2*f["bp"])/(f["A"]**2+f["B"]**2)
        Crho = f["C"]*wall/WALL
        shift = (f["beta"]+(r/WALL)*wall_rate)/(wall/WALL)
        h0 = (f["lc"]+3*lR-f["beta"]*(f["cp"]+3*Rchi)-f["betap"])/(2*f["N"])
        h4 = (f["np"]+3*Rchi)/(2*f["C"])
        eta = _response(chi, delta, wall_rate, chart)
        Z=_compose(delta,chart['normalization'],*chart['normalization_derivatives'][:2])
        sigma_radial=.25*_sin(2*eta['f'])**2/Z*wall/WALL
        sigma_rr=.5*_sin(4*eta['f'])*eta['fprime']/Z*(wall/WALL)**2
        # sigma depends on the original position geometry, so its exact
        # coordinate-time motion uses xdot=v and sdot=raw99. It does not
        # require an unprovided multiplier acceleration or conjugation.
        position_rate=np.zeros(100,complex);position_rate[:37]=x[37:74];position_rate[98]=x[99]
        sigma=eta['sigma']
        sigma_time=type(sigma)(sigma.gradient@position_rate,
            sigma.hessian@position_rate+np.r_[np.zeros(37),sigma.gradient[:37],np.zeros(25),sigma.gradient[98]],
            np.zeros((100,100),complex))
        # _cos/_sin are already encoded in f_eta through the analytic Jet.
        feta = eta["f"];sine = np.sin(feta.value);cosine = np.cos(feta.value)
        if abs(sine) < 1e-14:
            raise ValueError("radial eta chart singularity must be handled by its owned regular trial lift")
        cot = type(feta)(cosine/sine, -feta.gradient/sine**2,
            -feta.hessian/sine**2+2*cosine*np.outer(feta.gradient, feta.gradient)/sine**3)
        meta = -eta["fprime"]*cot/f["C"]
        point = dict(lapse=f["N"], radial_coframe=Crho, radius=R, coordinate_shift=shift,
            geometric_time_contact=h0, geometric_radial_contact=h4, eta_radial_contact=meta,
            volume_density=f["N"]*Crho*R**3, Cauchy_density=Crho*R**3,
            material_wall=wall, coordinate_wall_rate=wall_rate,
            surface_proper_clock_rate=surface_clock, eta_profile=eta['f'],
            eta_profile_radial=eta['fprime']*wall/WALL,
            radius_log_radial=Rchi*wall/WALL, lapse_log_radial=f['np']*wall/WALL,
            eta_profile_coordinate_time=eta['fdot']+eta['fprime']*(r/WALL)*wall_rate,
            material_wall_velocity=wall_speed,sigma=sigma,sigma_radial=sigma_radial,
            sigma_coordinate_time=sigma_time,sigma_radial_second=sigma_rr,
            radial_coframe_log_radial=f['cp']*wall/WALL,
            coordinate_shift_radial=f['betap']+wall_rate/wall)
        for key in names:
            val, dval = _value_and_first(point[key], dx[:100])
            values[key].append(val);first[key].append(dval)
    result = {k: np.array(v) for k, v in values.items()}
    result.update({k+"_first": np.array(v).T for k, v in first.items()})
    own, down = _profile(x, dx, rho)
    if side == "parent":
        profile, dprofile = own, down
    else:
        pp, dpp = _profile(p, dp, rho)
        rp, drp = _profile(refs[0], drefs[0], rho)
        rc, drc = _profile(refs[1], drefs[1], rho)
        profile, dprofile = pp-rp+rc, dpp-drp+drc
    # The representation's radial functions are fixed coordinate maps,
    # not frozen physical fields. Require their actual rho grid explicitly.
    grid = np.asarray(representation["rho"], float)
    if not np.array_equal(grid, rho):
        raise ValueError("same original radial value/rate maps at each requested point required")
    P = np.asarray(representation["gauge_basis"], complex)
    if P.shape != (len(rho), 80, 1, 5, 4):
        raise ValueError("full original80 coordinate radial gauge lift required")
    gauge = np.einsum('rjfac,j->rfac', P, x[100:180])[:, 0]
    dgauge = np.einsum('rjfac,jk->krfac', P, dx[100:180])[:, :, 0]
    gauge[:, 2:] += M[None]*(profile[:, 0, None, None]-1)
    dgauge[:, :, 2:] += M[None, None]*dprofile[:, :, 0, None, None]
    result.update(radial_points=rho, gauge_connection_material=gauge,
        gauge_connection_material_first=dgauge, mechanical_profile=profile,
        mechanical_profile_first=dprofile, intrinsic_H_realified=x[260:264].copy(),
        intrinsic_H_realified_first=dx[260:264].T.copy(),
        source_complete_profile_composed_before_restriction=True,
        bulk_Higgs_mass_added=False, positive_square_or_heat_used=False)
    return result


def d5_sigma_foliation_eta(coefficients, *, gamma, carrier_count,
        angular_count, sheet_orientation):
    """Execute the unit normal of the actual sigma level-set field.

    sigma_0=(sigma_t-zeta sigma_rho)/N, sigma_4=sigma_rho/Crho.
    n=(-sigma_0 e0+sigma_4 e4)/sqrt(sigma_4²-sigma_0²), with the
    originating outward branch. The eta derivative acts on f along n.
    This is a genuine sigma-foliation contact in the original D5 action,
    not a constant wall boost or a proof that radial u/J is its zero mode.
    Full collar flow/density, its normalization and exterior remain to be
    consumed separately. Source firsts retain every analytic placement.
    """
    c=coefficients;G=np.asarray(gamma,complex);nc,nh=int(carrier_count),int(angular_count)
    eps=int(sheet_orientation)
    if G.ndim!=3 or G.shape[0]!=5 or G.shape[1]!=G.shape[2] or nc<1 or nh<1 or eps not in(-1,1):
        raise ValueError('all five Clifford/full carrier/angular maps and original orientation required')
    N,C,z=(c[k]for k in('lapse','radial_coframe','coordinate_shift'))
    dN,dC,dz=(c[k+'_first']for k in('lapse','radial_coframe','coordinate_shift'))
    st,sr=(c[k]for k in('sigma_coordinate_time','sigma_radial'))
    dst,dsr=(c[k+'_first']for k in('sigma_coordinate_time','sigma_radial'))
    s0=(st-z*sr)/N;s4=sr/C
    ds0=(dst-dz*sr-z*dsr)/N-s0*dN/N;ds4=dsr/C-s4*dC/C
    square=s4*s4-s0*s0;root=np.sqrt(square)
    if np.any(abs(root)<1e-14)or np.any((root/s4).real<=0)or not np.isfinite(root).all():
        raise ValueError('sigma gradient left the inherited nonnull outward analytic normal chart')
    droot=(s4*ds4-s0*ds0)/root
    n0,n4=-s0/root,s4/root
    dn0=-ds0/root-n0*droot/root;dn4=ds4/root-n4*droot/root
    f,df=c['eta_profile'],c['eta_profile_first']
    ft,fr=(c[k]for k in('eta_profile_coordinate_time','eta_profile_radial'))
    dft,dfr=(c[k+'_first']for k in('eta_profile_coordinate_time','eta_profile_radial'))
    f0=(ft-z*fr)/N;f4=fr/C
    df0=(dft-dz*fr-z*dfr)/N-f0*dN/N;df4=dfr/C-f4*dC/C
    cot=1/np.tan(f);dcot=-df/np.sin(f)**2
    fn=n0*f0+n4*f4;dfn=dn0*f0+n0*df0+dn4*f4+n4*df4
    mass=-cot*fn;dmass=-dcot*fn-cot*dfn
    g0,gr=(np.kron(G[j],np.eye(nc*nh))for j in(0,4))
    # Principal-normal Clifford follows the OWN coframe derivative:
    # e0=(X_T-U X_s)/sqrt, e4=(X_s-U X_T)/sqrt. Thus its
    # normal coefficient is eps*n4 Gamma4-n0 Gamma0. The
    # vector normal and its Clifford coefficient are distinct placements.
    gn=-n0[:,None,None]*g0+eps*n4[:,None,None]*gr
    dgn=-dn0[:,:,None,None]*g0+eps*dn4[:,:,None,None]*gr
    contact=1j*gn*mass[:,None,None]
    dcontact=1j*(dgn*mass[None,:,None,None]+gn[None]*dmass[:,:,None,None])
    return dict(sigma_normal_timelike_component=n0,sigma_normal_radial_component=n4,
        sigma_normal_timelike_component_first=dn0,sigma_normal_radial_component_first=dn4,
        sigma_normal_coordinate_time=n0/N,sigma_normal_coordinate_radial=n4/C-z*n0/N,
        sigma_normal_mass=mass,sigma_normal_mass_first=dmass,
        sigma_normal_Clifford=gn,sigma_normal_eta_contact=contact,
        sigma_normal_eta_contact_first=dcontact,
        sigma_normal_unit_rows=n0*n0-n4*n4+1,
        sigma_normal_defining_rows=n0*s0+n4*s4-root,
        actual_sigma_normal_not_constant_wall_velocity=True,
        sigma_foliation_normal_not_assigned_a_Gaussian_geodesic=True,
        radial_trial_normalization_not_claimed_as_sigma_flow_mode_normalization=True,
        sigma_flow_density_normalization_and_retarded_tail_not_evaluated=True)


def principal_normal_point_trace(right_normal_value,left_normal_value,
        right_normal_first,left_normal_first,material_normal_velocity,
        material_normal_velocity_first, *, sheet_orientation,full_representation):
    """Bind the stable PLUS boost helper to this action's signed principal.

    The original derivative/Green coefficient gives
      GammaT=(Gamma0-eps U Gamma4)/sqrt(1-U²),
      GammaN=(eps Gamma4-U Gamma0)/sqrt(1-U²).
    Consequently the helper's argument is -eps U. This versioned adapter
    exports the actual principal matrices and checks their Spin pullback.
    It does not change the stable representation/trace source or choose an
    eta-normal mode, retarded domain, asymptotic trace or physical residue.
    """
    from .muon_full_d5_localized_lepton_trace import normalized_d5_dirac_bar_trace,moving_d5_material_trace_frame
    eps=int(sheet_orientation)
    if eps not in(-1,1):raise ValueError('original eta sheet orientation required')
    U=complex(material_normal_velocity);dU=np.asarray(material_normal_velocity_first,complex)
    tr=normalized_d5_dirac_bar_trace(right_normal_value,left_normal_value,
        right_normal_first,left_normal_first,-eps*U,-eps*dU,full_representation=full_representation)
    b=moving_d5_material_trace_frame(-eps*U,0,full_representation=full_representation)
    G=full_representation['gamma5D_self_dual128'];root=np.sqrt(1-U*U)
    GT=(G[0]-eps*U*G[4])/root;GN=(eps*G[4]-U*G[0])/root
    return dict(tr,original_principal_time_Clifford128=GT,
        original_principal_normal_Clifford128=GN,
        original_principal_time_spin_rows=b['spin_boost_inverse128']@GT@b['spin_boost128']-G[0],
        original_principal_normal_spin_rows=b['spin_boost_inverse128']@GN@b['spin_boost128']-eps*G[4],
        actual_material_velocity=np.array(U),representation_helper_velocity=np.array(-eps*U),
        original_eta_sheet_orientation=np.array(eps))


def d5_sigma_normal_flow_germ(coefficients, normal, *, coordinate_time_first_slot):
    """Actual characteristic/density first germ, with no history extrapolation.

    In the original fixed-rho chart X_s=(n0/N,n4/Crho-zeta*n0/N).
    d_s log J=div_mu X_s follows from the SAME mu=N Crho R³. Time
    derivatives are the declared original canonical coordinate-time
    direction, not an affine held-lapse inference. This evaluates the
    normalization equation needed along the sigma-normal collar. It does
    not assign its nonlocal integral or physical outer return to zero.
    """
    c=coefficients;a=normal;k=int(coordinate_time_first_slot)
    if k!=coordinate_time_first_slot or k<0 or k>=c['lapse_first'].shape[0]:
        raise ValueError('explicit supplied canonical coordinate-time first slot required')
    N,C,z=(c[v]for v in('lapse','radial_coframe','coordinate_shift'))
    Nt,Ct,zt=(c[v+'_first'][k]for v in('lapse','radial_coframe','coordinate_shift'))
    Nr=N*c['lapse_log_radial'];Cr=C*c['radial_coframe_log_radial'];zr=c['coordinate_shift_radial']
    st,sr,srr=(c[v]for v in('sigma_coordinate_time','sigma_radial','sigma_radial_second'))
    str_=c['sigma_radial_first'][k]
    s0=(st-z*sr)/N;s4=sr/C;root=np.sqrt(s4*s4-s0*s0)
    s0r=(str_-zr*sr-z*srr)/N-s0*Nr/N;s4r=srr/C-s4*Cr/C
    rootr=(s4*s4r-s0*s0r)/root
    n0,n4=(a[v]for v in('sigma_normal_timelike_component','sigma_normal_radial_component'))
    n0r=-s0r/root-n0*rootr/root;n4r=s4r/root-n4*rootr/root
    n0t,n4t=(a[v+'_first'][k]for v in('sigma_normal_timelike_component','sigma_normal_radial_component'))
    nt=n0/N;nr=n4/C-z*nt
    ntt=n0t/N-nt*Nt/N;ntr=n0r/N-nt*Nr/N
    nrt=n4t/C-n4*Ct/C**2-zt*nt-z*ntt
    nrr=n4r/C-n4*Cr/C**2-zr*nt-z*ntr
    mu=c['volume_density'];mut=c['volume_density_first'][k]
    mur=mu*(c['lapse_log_radial']+c['radial_coframe_log_radial']+3*c['radius_log_radial'])
    divergence=(mut*nt+mur*nr)/mu+ntt+nrr
    return dict(sigma_flow_coordinate_velocity=np.c_[nt,nr],
        sigma_flow_coordinate_velocity_time=np.c_[ntt,nrt],
        sigma_flow_coordinate_velocity_radial=np.c_[ntr,nrr],
        sigma_flow_coordinate_acceleration=np.c_[ntt*nt+ntr*nr,nrt*nt+nrr*nr],
        sigma_flow_log_density_normal_first=divergence,
        sigma_flow_normal_velocity_parameter=-s0/s4,
        sigma_flow_normal_velocity_time=(n0t*n4-n0*n4t)/(n4*n4),
        sigma_flow_normal_velocity_radial=(n0r*n4-n0*n4r)/(n4*n4),
        sigma_flow_density_derivative_from_original_volume=True,
        sigma_flow_history_normalization_or_retarded_completion_not_evaluated=True)


def normalized_two_sheet_point_action(canonical_point_actions,
        canonical_point_actions_energy, normalized_trace, intrinsic_Higgs_mass,
        surface_density, full_time_Clifford, *, left_trace_count=12):
    """Consume the two eta-sheet weak actions and once-only SH bridge.

    The input weak Kcan already contains Gamma0 in its left trial pairing.
    Convert it once to the ambient Dirac-bar operator Gamma0 Kcan.
    The normalized point trace supplies the explicit independent right
    and left maps. SH is off-diagonal between eta sheets, not between
    temporal parent/child history arms. A full-field border retains every
    complementary row before returning its 18x18 source equation Gamma.
    No retarded exterior, physical normal mode or pole is selected here.
    """
    from .muon_coupled_phase_trace_projection import _solve
    K,KE,M,G0=(np.asarray(a,complex)for a in(canonical_point_actions,
        canonical_point_actions_energy,intrinsic_Higgs_mass,full_time_Clifford))
    if K.ndim!=3 or K.shape[0]!=2 or K.shape[1]!=K.shape[2]or KE.shape!=K.shape:
        raise ValueError('both complete eta-sheet point actions and energy derivatives required')
    d=K.shape[1];n=len(M);nl=int(left_trace_count)
    if M.ndim!=2 or M.shape!=(n,n)or nl!=left_trace_count or not 0<nl<n:
        raise ValueError('original LR trace partition and full intrinsic mass required')
    if not isinstance(normalized_trace,(tuple,list))or len(normalized_trace)!=2:
        raise ValueError('independent original PLUS/MINUS eta-sheet normalized point traces required')
    def maps(tr):
        BR,BL,ER,EL=(np.asarray(tr[k],complex)for k in('normalized_right_Gamma0',
            'normalized_Dirac_bar_left_Gamma0','normal_mode_right_point_lift','normal_mode_Dirac_bar_left_point_lift'))
        if BR.shape!=(n,d)or BL.shape!=(d,n)or ER.shape!=(d,n)or EL.shape!=(n,d):
            raise ValueError('same full-carrier normalized Dirac-bar point incidence required')
        return BR,BL,ER,EL
    rp,lp,erp,elp=maps(normalized_trace[0]);rm,lm,erm,elm=maps(normalized_trace[1])
    if G0.shape!=(d,d):raise ValueError('same intrinsic mass and full time Clifford required')
    PL=np.diag(np.r_[np.ones(nl),np.zeros(n-nl)]);PR=np.eye(n)-PL
    if np.max(abs(PL@M@PL))+np.max(abs(PR@M@PR))>1e-12*max(1.,float(np.max(abs(M)))):
        raise ValueError('SH must be the original off-diagonal fixed-Y LR bridge')
    B=np.c_[PL@rp,PR@rm];C=np.r_[lp@PL,lm@PR]
    mode_right=np.r_[erp@PL,erm@PR];mode_left=np.c_[PL@elp,PR@elm]
    zeros=np.zeros((d,d),complex)
    bulk=np.block([[G0@K[0],zeros],[zeros,G0@K[1]]])
    bulkE=np.block([[G0@KE[0],zeros],[zeros,G0@KE[1]]])
    seam=-complex(surface_density)*C@M@B
    action=bulk+seam
    border=np.block([[action,C],[B,np.zeros((n,n),complex)]])
    rhs=np.r_[np.zeros((2*d,n),complex),np.eye(n)]
    sol,rs,cs=_solve(border,rhs)
    energy_rhs=np.r_[-bulkE@sol[:2*d],np.zeros((n,n),complex)]
    energy_sol,_,_=_solve(border,energy_rhs)
    original=border@sol-rhs;energy_rows=border@energy_sol-energy_rhs
    Gamma=-sol[2*d:];GammaE=-energy_sol[2*d:]
    return dict(eta_two_sheet_Dirac_bar_bulk_action=bulk,
        eta_two_sheet_Dirac_bar_Higgs_seam_action=seam,
        eta_two_sheet_Dirac_bar_action=action,eta_two_sheet_Dirac_bar_action_energy=bulkE,
        normalized_two_sheet_right_trace=B,normalized_two_sheet_Dirac_bar_left_trace=C,
        normalized_two_sheet_right_mode_test=mode_right,normalized_two_sheet_left_mode_test=mode_left,
        full_complementary_field_Poisson=sol[:2*d],full_complementary_field_Poisson_energy=energy_sol[:2*d],
        finite_normalized_field_Gamma=Gamma,finite_normalized_field_Gamma_energy=GammaE,
        original_full_field_and_trace_rows=original,original_full_field_and_trace_energy_rows=energy_rows,
        direct_boundary_equation_rows=mode_left@action@sol[:2*d]-Gamma,
        direct_boundary_equation_energy_rows=mode_left@(bulkE@sol[:2*d]+action@energy_sol[:2*d])-GammaE,
        normalized_right_trace_recovery_rows=B@mode_right-np.eye(n),
        normalized_left_trace_recovery_rows=mode_left@C-np.eye(n),
        original_off_diagonal_Higgs_seam_pullback_rows=mode_left@seam@mode_right+surface_density*M,
        original_border_row_scale=rs,original_border_column_scale=cs,
        original_complementary_field_rows_not_deleted=2*d-n,
        eta_sheet_not_temporal_parent_child_reset=True,once_only_Higgs_seam_no_second_kinetic=True,
        finite_point_field_Gamma_not_physical_retarded_Gamma2=True,
        intrinsic_charge_pole_residue_or_clock_not_selected=True)


def d5_wall_material_eta(coefficients, *, gamma, carrier_count, angular_count,
        sheet_orientation):
    """Evaluate the material-normal eta contact AT the actual wall only.

    Gamma_N=(eps Gamma_rho-U Gamma0)/sqrt(1-U²),
    m_eta=−cot(f)[U(f_t−shift f_rho)/N+f_rho/Crho]/sqrt(1-U²).
    This proves and quantifies the extra temporal contact at a moving wall.
    It is not extended along a guessed radial/Gaussian collar: that needs
    the same history's actual normal-curve pullback and moving inclusion.
    """
    c=coefficients;G=np.asarray(gamma,complex);eps=int(sheet_orientation)
    nc,nh=int(carrier_count),int(angular_count)
    if (G.shape[0]!=5 or G.ndim!=3 or G.shape[1]!=G.shape[2] or nc<1 or nh<1
            or eps not in(-1,1) or abs(c['radial_points'][-1]-WALL)>1e-14):
        raise ValueError('the actual material wall and full five Clifford/carrier/angular maps required')
    U=c['material_wall_velocity'][-1];root=np.sqrt(1-U*U)
    f=c['eta_profile'][-1];fr=c['eta_profile_radial'][-1];ft=c['eta_profile_coordinate_time'][-1]
    N,C,z=(c[k][-1]for k in('lapse','radial_coframe','coordinate_shift'))
    normal_f=(U*(ft-z*fr)/N+fr/C)/root
    mass=-normal_f/np.tan(f)
    g0,gr=(np.kron(G[j],np.eye(nc*nh))for j in(0,4))
    GN=(eps*gr-U*g0)/root
    actual=1j*GN*mass
    radial=1j*eps*gr*c['eta_radial_contact'][-1]
    reduced=1j*(eps*gr-U*g0)*c['eta_radial_contact'][-1]
    return dict(actual_wall_normal_Clifford=GN,actual_wall_normal_eta_mass=np.array(mass),
        actual_wall_material_eta_contact=actual,coordinate_radial_eta_contact=radial,
        omitted_moving_wall_eta_contact=actual-radial,
        anchored_material_wall_eta_identity=actual-reduced,
        material_eta_bulk_Gaussian_curve_extension_evaluated=False,
        physical_retarded_tail_or_normal_mode_admission=False)


def d5_current_normal_inclusion(coefficients, radial_weights, *, wall_coefficients):
    """Actual u=sin(f)/sqrt(I*(N/Nw)*(R/Rw)^3), with its first jets.

    I is integrated from the current Crho and material f, not copied from a
    historical background. The analytic normal derivative is independently
    reconstructed from f_rho, N_rho and R_rho, then checked against the
    ORIGINAL geometric+eta Dirac contact. No u_wall^-2 coefficient is fitted.
    The represented quadrature normalization is not a continuum enclosure.
    """
    c, wc = coefficients, wall_coefficients
    w = np.asarray(radial_weights, float)
    f, df = c['eta_profile'], c['eta_profile_first']
    C, dC = c['radial_coframe'], c['radial_coframe_first']
    N, dN, R, dR = (c[k] for k in ('lapse','lapse_first','radius','radius_first'))
    if w.shape != f.shape or not np.isfinite(w).all():
        raise ValueError('same current original radial quadrature required')
    I = np.dot(w, C*np.sin(f)**2)
    dI = np.einsum('q,kq->k',w,dC*np.sin(f)**2+2*C*np.sin(f)*np.cos(f)*df)
    nw,rw,fw = (wc[k][-1] for k in ('lapse','radius','eta_profile'))
    dnw,drw,dfw = (wc[k+'_first'][:,-1] for k in ('lapse','radius','eta_profile'))
    root = np.sqrt(complex(I))
    if root.real <= 0 or not root or not np.isfinite(root):
        raise ValueError('current normal integral must remain on its inherited analytic square-root chart')
    J = (N/nw)*(R/rw)**3
    roots = np.sqrt(I*J)
    if np.any(roots.real <= 0) or not np.isfinite(roots).all():
        raise ValueError('current normal inclusion left its inherited analytic density chart')
    u = np.sin(f)/roots
    du = np.cos(f)*df/roots-u[None]/2*(dI[:,None]/I+dN/N-dnw[:,None]/nw+3*dR/R-3*drw[:,None]/rw)
    log_rho = c['eta_profile_radial']/np.tan(f)-c['lapse_log_radial']/2-3*c['radius_log_radial']/2
    ur = u*log_rho
    normal_rows = ur/c['radial_coframe']+(c['geometric_radial_contact']+c['eta_radial_contact'])*u
    wall = np.sin(fw)/root
    dwall = np.cos(fw)*dfw/root-wall*dI/(2*I)
    target_density = nw*rw**3
    actual_density = np.dot(w,c['volume_density']*u*u)
    return dict(normal_integral=np.array(I),normal_integral_first=dI,
        original_normal_inclusion=u,original_normal_inclusion_first=du,
        original_normal_inclusion_radial=ur,original_first_order_normal_rows=normal_rows,
        actual_normalized_Gamma0_multiplier=np.array(wall),actual_normalized_Gamma0_multiplier_first=dwall,
        current_normal_density_pullback=np.array(actual_density),original_wall_volume_density=np.array(target_density),
        normal_density_identity=np.array(actual_density-target_density),
        current_normal_field_not_fitted=True,normal_radial_identity_not_an_exterior_pole_admission=True,
        continuum_and_off_mode_trace_complement_not_enclosed=True)


def d5_unsquared_weak_trace(coefficients, radial_weights, *, gamma,
        carrier_generators, angular_derivatives, right_values, right_radial,
        right_coordinate_time, literal_left_values, energy, sheet_orientation,
        eta_clifford_contact):
    """Apply the original unsquared D5(E) to explicit full trace test maps.

    Trial maps carry all radial/angular/spin/carrier fibers. The fixed
    Clifford and harmonic dual is supplied, while source coefficients are
    never conjugated. The declared surface-proper phase obeys
    d_t exp(-i E tau_Sigma)=-i E*ell_Sigma exp(-i E tau_Sigma), so energy
    enters gamma0*ell_Sigma*E/N, not an E-squared pencil or an assumed unit
    boundary lapse. This is a represented off-shell frequency chart; it
    does not prove global time-translation invariance of a moving history.
    The actual coordinate-time trial derivative is mandatory, including
    a moving normal inclusion/frame where used. The eta matrix is also
    mandatory: the coordinate-radial Gamma4*eta candidate does not by
    itself supply the moving Gaussian-normal/material eta coupling.
    This first-order form does not select an exterior at the material wall;
    that surface is internal and requires the action-owned joined trace.
    """
    c = coefficients;w = np.asarray(radial_weights, float)
    G = np.asarray(gamma, complex);T = np.asarray(carrier_generators, complex)
    Es = np.asarray(angular_derivatives, complex)
    V, Vr, Vt, L, Eta = map(lambda x: np.asarray(x, complex), (right_values, right_radial,
        right_coordinate_time, literal_left_values, eta_clifford_contact))
    E = complex(energy);eps = int(sheet_orientation)
    q = len(w)
    if (G.ndim != 3 or G.shape[0] != 5 or G.shape[1] != G.shape[2]
            or T.ndim != 3 or T.shape[0] != 4 or T.shape[1] != T.shape[2]
            or Es.ndim != 3 or Es.shape[0] != 3 or Es.shape[1] != Es.shape[2]
            or eps not in (-1, 1) or not np.isfinite(E)):
        raise ValueError("all five Clifford/complete carrier/three angular maps and owned sheet orientation required")
    ds, dc, na = G.shape[1], T.shape[1], Es.shape[1]
    d = ds*dc*na
    if (V.ndim != 3 or V.shape[:2] != (q, d) or Vr.shape != V.shape or Vt.shape != V.shape
            or Eta.shape != (q,d,d)
            or L.ndim != 3 or L.shape[0] != q or L.shape[2] != d
            or any(not np.isfinite(a).all() for a in (w, G, T, Es, V, Vr, Vt, L, Eta))):
        raise ValueError("every original radial trace/dual row and complete spin/carrier/angular trial column required")
    I = np.eye(dc*na);g = np.array([np.kron(item, I) for item in G])
    spin = np.kron(-1.5j*G[1]@G[2]@G[3], I)
    angular = sum(np.kron(np.kron(1j*G[a+1], np.eye(dc)), Es[a]) for a in range(3))
    gauge_matrices = np.array([np.kron(np.eye(ds), np.kron(t, np.eye(na))) for t in T])
    K = np.zeros((L.shape[1], V.shape[2]), complex);KE = np.zeros_like(K)
    action = [];energy_action = []
    for r in range(q):
        N, C, R, shift, h0, h4, eta = (c[k][r] for k in ("lapse", "radial_coframe", "radius",
            "coordinate_shift", "geometric_time_contact", "geometric_radial_contact", "eta_radial_contact"))
        A = np.einsum('fc,cij->fij', c["gauge_connection_material"][r], gauge_matrices)
        D0 = 1j*g[0]*h0+1j*eps*g[4]*h4+Eta[r]+(spin+angular)/R
        D0 += 1j*g[0]@(A[0]-shift*A[1])/N+1j*eps*g[4]@A[1]/C
        D0 += sum(1j*g[a+1]@A[a+2]/R for a in range(3))
        clock = c['surface_proper_clock_rate'][r]
        D = g[0]*E*clock/N+D0
        Dr = -1j*g[0]*shift/N+1j*eps*g[4]/C
        acted = D@V[r]+Dr@Vr[r]+1j*g[0]@Vt[r]/N
        actedE = clock*g[0]@V[r]/N
        density = w[r]*c["volume_density"][r]
        K += density*L[r]@acted;KE += density*L[r]@actedE
        action.append(acted);energy_action.append(actedE)
    return dict(unsquared_trace_action=K, unsquared_trace_action_energy_first=KE,
        original_D5_on_trial=np.array(action), original_D5_energy_on_trial=np.array(energy_action),
        full_field_exterior_domain_or_pole_selected=False,
        intrinsic_Higgs_seam_contact_not_included_by_bulk_form=True,
        original_radial_and_angular_trace_complement_must_be_retained=True,
        supplied_trial_coordinate_time_and_eta_contacts_not_assigned_zero=True,
        external_variable="unsquared surface-proper phase frequency E in original D5 coefficient",
        global_stationary_frequency_or_pole_not_inferred=True)


def d5_material_green_trace(coefficients, *, gamma, carrier_count,
        angular_count, sheet_orientation, point_index):
    """Return the actual first-order value/Green trace and its source jets.

    In the fixed material rho chart the derivative coefficient is
    i eps gamma_rho/C_rho-i gamma0*shift/N. Multiplying by the SAME
    N C_rho R^3 action density gives the outward Green matrix
    i R^3(eps N gamma_rho-C_rho shift gamma0). This is a first-order
    Green trace, not the weak squared Gamma1, Dirichlet flux or boundary law.
    The Dirac-bar left pairing additionally multiplies by gamma0.
    """
    c = coefficients;G = np.asarray(gamma, complex);i = int(point_index)
    nc, nh, eps = int(carrier_count), int(angular_count), int(sheet_orientation)
    if (G.ndim != 3 or G.shape[0] != 5 or G.shape[1] != G.shape[2]
            or nc < 1 or nh < 1 or eps not in (-1, 1)
            or i != point_index or i < 0 or i >= len(c['lapse'])):
        raise ValueError("actual full spin/carrier/angular material trace and original orientation required")
    N, C, R, shift = (c[k][i] for k in ('lapse','radial_coframe','radius','coordinate_shift'))
    dN, dC, dR, ds = (c[k+'_first'][:,i] for k in ('lapse','radial_coframe','radius','coordinate_shift'))
    g0, gr = (np.kron(G[j], np.eye(nc*nh)) for j in (0,4))
    trace = 1j*R**3*(eps*N*gr-C*shift*g0)
    dtrace = 1j*(eps*(dN*R**3+3*N*R**2*dR)[:,None,None]*gr
        -(dC*shift*R**3+C*ds*R**3+3*C*shift*R**2*dR)[:,None,None]*g0)
    return dict(original_Gamma0_value_matrix=np.eye(len(trace),dtype=complex),
        original_first_order_Green_trace_matrix=trace,
        original_first_order_Green_trace_matrix_first=dtrace,
        original_Dirac_bar_Green_matrix=g0@trace,
        original_Dirac_bar_Green_matrix_first=g0@dtrace,
        material_internal_interface_not_outer_selector=True,
        squared_domain_or_retarded_tail_not_inferred=True,
        lapse_used_in_action_flux_not_as_free_spinor_field_rescaling=True)
