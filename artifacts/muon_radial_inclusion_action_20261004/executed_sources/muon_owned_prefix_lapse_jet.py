"""Extract one retained action-owned prefix lapse jet, without a new solve."""
from __future__ import annotations
import numpy as np
from flint import arb,ctx
from bhsm.interface.muon_cut_inverse_coverage import encoded
from bhsm.interface.muon_radial_inclusion_action import affine_sin_squared_integral
from bhsm.interface.muon_parent_maxwell_velocity import current_parent_fields
from bhsm.interface.aether_forward_boundary_radius import boundary_log_radius


def evaluate_owned_center(snapshot,report,geometry,pairing,contact,corrected):
    """Physical tau conversion of the supplied weighted descriptor field.

    sigma is the signed descriptor, NOT radial distance or a resolvent
    variable. This is the saved proof center, NOT the step1222 endpoint.
    """
    ctx.prec=192;y=snapshot['center_state'];weights=snapshot['state_weights'];F=snapshot['exact_center_field_action']
    m=y[74:];sign=(-1.)**np.arange(1,13)
    Nb=sum((arb(float(m[k]))*int(sign[k]) for k in range(12)),arb(0)).exp()
    sigma=arb(report['center_field']['signed_descriptor_decimal']);Delta=arb(float(report['center_field']['Delta']))
    factor=Delta/(Nb*sigma)
    rates=[factor*arb(float(f))/arb(float(w)) for f,w in zip(F,weights)]
    rate_float=np.array([float(a.mid()) for a in rates]);mtau=rate_float[74:98]
    grid=geometry['rho'];logR=boundary_log_radius(12,y[:37])
    fields={k:v[0] if np.ndim(v)>1 else v for k,v in current_parent_fields(y[None],np.array([logR]),grid).items()}
    I=affine_sin_squared_integral(grid,fields['C_rho'])
    cells=pairing['gauss_cells'];rho=pairing['gauss_rho'];x=(rho-grid[cells])/np.diff(grid)[cells]
    interp=lambda a:a[cells]*(1-x)+a[cells+1]*x
    ck=np.cos(2*np.outer(grid,np.arange(1,13)))
    ck[-1]=sign  # exact owned proper-boundary lapse, not a tiny trig defect
    lograte_nodes=(ck-sign)@mtau[:12]
    nu=interp(fields['proper_lapse']);C=interp(fields['C_rho']);r=interp(fields['base_radius'])
    nu_tau=interp(fields['proper_lapse']*lograte_nodes);Lused=nu_tau/nu
    direct=[]
    for z in rho:
        value=sum((rates[74+k]*((2*(k+1)*arb(float(z))).cos()-int(sign[k])) for k in range(12)),arb(0))
        direct.append(value)
    nb=float(fields['proper_lapse'][-1]);Rb=float(fields['base_radius'][-1]);u=np.sin(rho/2)/np.sqrt(float(I.mid())*(nu/nb)*(r/Rb)**3)
    G0=np.kron(corrected['parent_gamma'][0],np.eye(16))
    kernel=(-.5*u*Lused/nu)[:,None,None]*(1j*G0)
    arrays=dict(center_state=y,physical_tau_state_rate=rate_float,lapse_rates_tau=mtau[:12],shift_rates_tau=mtau[12:],
        gauss_rho=rho,owned_log_nu_tau_fourier=np.array([float(a.mid()) for a in direct]),
        owned_nu_tau_nodal=nu_tau,owned_log_nu_tau_used_nodal=Lused,
        owned_center_u_vol=u,owned_center_nu=nu,owned_lapse_time_D5W_coefficient=kernel,
        source_spatial_interpolation_difference=Lused-np.array([float(a.mid()) for a in direct]))
    for n in (1,3):
        xi=contact[f'Xi_A_unit_n{n}'][:,:,corrected['source_image_probe_columns']]
        arrays[f'owned_lapse_time_action_on_source_directions_n{n}']=np.einsum('goi,Aicmk->gAocmk',kernel,xi,optimize=True)
    result=dict(proof_center='C2 LoHner fixed-s center1221, reused by step1222 center_state',
        physical_endpoint=False,descriptor_name='sigma, signed descriptor; distinct from proper radial distance',
        equation='Y_tau=Delta/(N_b sigma) * exact_center_field_action/state_weights',
        log_lapse_equation='partial_tau log nu=sum_k m_tau,k [cos(2k rho)-(-1)^k]',
        contribution_equation='(D5W)_lapse,time=-(i Gamma0 u/(2 nu)) partial_tau log nu',
        clock_factor=encoded(factor),normalization_center=encoded(I),
        owned_lapse_rates=[encoded(a) for a in rates[74:86]],
        direct_source_log_nu_tau_range=[min(encoded(a)['interval'][0] for a in direct),max(encoded(a)['interval'][1] for a in direct)],
        nodal_source_log_nu_tau_range=[float(min(Lused)),float(max(Lused))],
        source_spatial_interpolation_max_difference=float(max(abs(arrays['source_spatial_interpolation_difference']))),
        q_tau_consistency_with_v_over_Nb=float(max(abs(rate_float[:37]-y[37:74]/float(Nb.mid())))),
        not_substituted_for_endpoint=True,complete_center_D5W_evaluated=False,
        meaning='evaluated action-owned lapse-time summand at its supplied center; independent point provenance and no inferred endpoint jet',
        error_scope='Arb clock/coefficient contractions at fixed saved binary64 field operands; original field-action/continuum uncertainty not upgraded; nodal/direct spatial difference recorded',
        endpoint_next_equation='partial_tau log nu_cut = Delta_cut/(N_b_cut sigma_cut) sum_k [F_sigma(endpoint)_74+k/weight_74+k] [cos(2k rho)-(-1)^k]',
        next_producer='audit_n12_c2_exact_center_fixed_s_field_matrix.build_payload and the same cancellation-preserving action field at the endpoint or on its certified tube',
        next_consumer='radial half-density temporal action, full coupled inherited exterior K/M; keep trace complement')
    return arrays,result
