"""True-Lyy normal kinetic applications on the retained phase action.

All geometry, gauge, Higgs and algebraic responses are solved together.
The two analytic central gauge generators are framed by named coefficient
conditions, not numerical eigenvectors.  The evaluated response is a
conditional trial form; it is not a selected formation mode or cutoff.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_birth_chronological_boundary_action import retained_chronological_boundary_application
from .muon_birth_finite_geometric_trace_endpoint import moving_geometric_trace_jet
from .muon_birth_trace_enriched_action import generic_coordinate_lift
from .muon_trace_enriched_charged_current_response import enriched_central_profiles
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_moving_geometric_action import moving_cap_action_jet
from .muon_parent_mean_causal_action import VOLUME
from .muon_birth_phase_continuation import _compressed_npz


def true_legendre_normal_trial(action_hessian, raw, representation, *, frame='temporal', normal_trace='proper'):
    """Solve the full kinetic/algebraic saddle for two attachments and n.

    K=((Lvv,Lvy,B^T),(Lyv,Lyy,0),(B,0,0)).  In particular Lyy is
    retained.  Gauge framing retains each original equation and exposes
    its reaction.  This is not the earlier zero-Lyy kinetic projection.
    """
    H=np.asarray(action_hessian,float); raw=np.asarray(raw,float); rep=representation
    c=generic_coordinate_lift(rep['gauge_labels']); n=c['x_count']; m=c['y_count']; P=c['lift']
    if H.shape!=(2*n+m,)*2 or raw.shape!=(len(P),) or not np.isfinite(H).all() or not np.isfinite(raw).all():
        raise ValueError('same complete retained action/state/frame required')
    if frame not in ('temporal','radial'):raise ValueError('named central temporal or radial frame required')
    if normal_trace not in ('proper','chart'):raise ValueError('proper wall-normal or coordinate chart trace required')
    intrinsic=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
    # T=(e0+U e1)/sqrt(1-U^2), n_out=(U e0+e1)/sqrt(1-U^2).
    # At fixed coordinate t, -g(n_out,delta X)=C delta chi/sqrt(1-U^2).
    # The wall chi(q,n) also moves under q; retaining this covector avoids
    # equating the finite-n chart coordinate with unit proper displacement.
    normal_projection=intrinsic['fields']['C'].value/np.sqrt(1-intrinsic['U'].value**2)
    proper_trace=normal_projection*intrinsic['wall'].gradient@P[:100,:n]
    geometry=moving_geometric_trace_jet(raw); B=np.zeros((3,n))
    B[:2]=geometry['attachment_first']@P[:100,:n]
    if normal_trace=='proper':B[2]=proper_trace
    else:B[2,37]=1.
    A=H[n:,n:]; K=np.block([[A,np.vstack((B.T,np.zeros((m,3))))],
        [np.c_[B,np.zeros((3,m))],np.zeros((3,3))]])
    profiles=enriched_central_profiles(rep); theta=profiles['theta_coefficients']; derivative=profiles['radial_derivative_coefficients']
    labels=rep['gauge_labels']; At=[j for j,i in enumerate(c['At_indices']) if labels[i]['internal']==3]
    Ar=[j for j,i in enumerate(c['dynamic_gauge_indices']) if labels[i]['field']=='A_rho' and labels[i]['internal']==3]
    if len(At)!=4 or len(Ar)!=4:raise ValueError('complete enriched central radial profiles required')
    Z=np.zeros((len(K),2)); Z[38+np.array(Ar)]=derivative
    Z[n+24+np.array(At)]=theta
    generator=higgs_u2_real_representation()['real_generators'][3]
    Hreal=raw[100+2*rep['gauge_count']:104+2*rep['gauge_count']]
    wall=rep['wall_trace_map'][0,3,c['At_indices'][np.array(At)]]@theta
    Z[n-4:n]=-np.outer(generator@Hreal,wall)
    C=np.zeros((2,len(K)))
    if frame=='temporal':C[:,n+24+np.array(At)]=theta.T
    else:C[:,38+np.array(Ar)]=derivative.T
    bordered=np.block([[K,C.T],[C,np.zeros((2,2))]])
    rhs=np.zeros((len(bordered),3)); rhs[n+m:n+m+3]=np.eye(3)
    row=np.max(abs(bordered),axis=1)
    if np.any(row==0):raise np.linalg.LinAlgError('literal framed saddle has an unbound row')
    s=1/np.sqrt(row); balance=s[:,None]*bordered*s[None,:]
    solution=s[:,None]*np.linalg.solve(balance,s[:,None]*rhs)
    response=solution[:n+m].T@A@solution[:n+m]
    lapse=intrinsic['induced_lapse'].value if 'induced_lapse' in intrinsic else intrinsic['lapse'].value
    # d tau=l dt, hence I_proper=l I_coordinate for the same normal amplitude.
    return dict(response=response,normal_coordinate_time_inertia=float(response[2,2]),
        normal_proper_clock_inertia=float(lapse*response[2,2]),induced_lapse=float(lapse),
        proper_normal_trace=proper_trace,normal_trace_kind=normal_trace,
        normal_embedding_projection_factor=float(normal_projection),
        normal_chart_projection_factor=float(proper_trace[37]),
        normal_projection_rule='-g(n_out,delta_X)=C_wall*delta_chi/sqrt(1-U^2); delta_chi=D_x( pi/4+n/Cstar(q) ) delta_x',
        velocity_algebraic_lift=solution[:n+m],velocity_lift=solution[:n],algebraic_lift=solution[n:n+m],
        trial_trace=B,legendre_saddle=K,framed_saddle=bordered,solution=solution,
        reaction=solution[n+m:n+m+3],frame_reactions=solution[-2:],
        literal_gauge_generators=Z,gauge_Ward_image=K@Z,gauge_source_pairing=Z.T@rhs[:-2],
        full_algebraic_residual=H[2*n:,n:]@solution[:n+m],
        solve_residual=bordered@solution-rhs,unframed_equation_reaction=K@solution[:-2]-rhs[:-2],
        frame_condition=C@solution[:-2],trial_residual=B@solution[:n]-np.eye(3),
        balanced_condition_number=float(np.linalg.cond(balance)),frame=frame,
        full_true_Lyy_retained=True,zero_Lyy_projection_used=False,spectral_directions_removed=0,
        physical_unit_inertia_normalization=False,physical_mode_selected=False,
        clock_rule='d_tau=induced_lapse*d_t; I_proper=induced_lapse*I_coordinate for the frozen supplied proper wall-normal trace; no global clock matching selected')


def surface_weak_area_application(raw, representation, *, stratum):
    """Return the literal area two-jet, including off-shell path contacts.

    No raw area Hessian is relabelled J=-Delta-(|A|^2+Ric).  Its
    nonminimal traction/path and temporal contacts remain explicit.
    M8 and M5 quotient actions have different densities and dimensions.
    """
    raw=np.asarray(raw,float); rep=representation
    w=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
    if stratum=='M8':
        area=moving_cap_action_jet(12,raw[:37],raw[37:74],raw[74:98],points=rep['cap_points'],
            source_value=raw[98],source_rate=raw[99])['surface_per_gamma'];dimension=7
        normalization='M8 orbit integral V^2 divided by common V^2'
    elif stratum=='M5':
        area=-w['wV']/VOLUME;dimension=4
        normalization='M5 quotient orbit integral V divided by common V^2'
    else:raise ValueError('explicit owned M8 wall or M5 quotient stratum required')
    d=np.zeros((100,2)); d[98,0]=1.;d[99,1]=1.
    return dict(area_value_per_gamma=float(area.value),area_gradient_per_gamma=area.gradient,
        area_hessian_per_gamma=area.hessian,normal_value_rate_first_per_gamma=d.T@area.gradient,
        normal_value_rate_second_per_gamma=d.T@area.hessian@d,worldvolume_dimension=dimension,
        gamma_equation=f'gamma=alpha_FSC*c^(-{dimension}/2)',normalization=normalization,
        raw_area_Hessian_equals_Jacobi_not_claimed=True,nonminimal_path_and_temporal_contacts_retained=True,
        stratum_sum_not_selected=True,physical_gamma_or_c_selected=False)


def materialize_normal_inertia(phase_directory, output, *, repository=ROOT):
    root=Path(repository);out=Path(output);out=out if out.is_absolute() else root/out
    if out.exists():raise FileExistsError('preserve earlier applications')
    a=retained_chronological_boundary_application(phase_directory,repository=root);rep=a['representation'];r=a['receipt']
    rows=[];arrays={}; k=len(a['action_hessians'])-1 if r['side']=='incoming' else 0
    H=a['action_hessians'][k];raw=a['raw_chronological_midpoints'][k]
    for frame in ('temporal','radial'):
        b=true_legendre_normal_trial(H,raw,rep,frame=frame)
        for key,value in b.items():
            if isinstance(value,np.ndarray):arrays[frame+'_'+key]=value
        rows.append({key:value for key,value in b.items() if not isinstance(value,np.ndarray)})
        rows[-1].update(solve_residual_max=float(np.max(abs(b['solve_residual']))),
            gauge_Ward_image_max=float(np.max(abs(b['gauge_Ward_image']))),
            gauge_source_pairing_max=float(np.max(abs(b['gauge_source_pairing']))),
            full_algebraic_residual_max=float(np.max(abs(b['full_algebraic_residual']))),
            frame_reaction_max=float(np.max(abs(b['frame_reactions']))))
    areas={}
    for stratum in ('M8','M5'):
        b=surface_weak_area_application(raw,rep,stratum=stratum)
        for key,value in b.items():
            if isinstance(value,np.ndarray):arrays[stratum+'_'+key]=value
        areas[stratum]={key:value for key,value in b.items() if not isinstance(value,np.ndarray)}
        areas[stratum]['normal_value_rate_first_per_gamma']=b['normal_value_rate_first_per_gamma'].tolist()
        areas[stratum]['normal_value_rate_second_per_gamma']=b['normal_value_rate_second_per_gamma'].tolist()
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    refs=dict(r['input_hashes']);refs.update({p.relative_to(root).as_posix():d for p,d in a['input_refs'].items()})
    for name in ('muon_birth_chronological_normal_inertia','muon_birth_chronological_boundary_action',
        'muon_birth_finite_geometric_trace_endpoint','muon_trace_enriched_charged_current_response','muon_intrinsic_higgs_gauge_action'):
        path='src/bhsm/interface/'+name+'.py';refs[path]=sha256((root/path).read_bytes()).hexdigest()
    md=dict(scope='EVALUATED_TRUE_LEGENDRE_NORMAL_TRIAL_AND_SIGNED_AREA_WEAK_APPLICATION',side=r['side'],steps=r['steps'],
        chronological_birth_adjacent_cell=k,input_hashes=refs,numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        action_parameters=r['action_parameters'],normal_kinetic_applications=rows,separate_surface_strata=areas,
        clock_matching='each arm transformed with its actual induced_lapse; no equality of coordinate clocks assumed',
        area_Jacobi_readout='literal area weak Hessian retained; J_Sigma requires off-shell traction/path correction and the same boundary/domain pairing',
        physical_scalar_invariant_sector_not_disproved_by_internal_image=True,full_internal_image_retained=True,
        scalar_gamma_c_root_selected=False,event_drive_not_equated_to_resistance=True,
        physical_formation_cutoff_or_Pauli_closed=False,
        error_scope='binary64 complete saved action Hessian and literal named gauge frame solve; no continuum/action-rounding certificate')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase-directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();print(json.dumps(materialize_normal_inertia(args.phase_directory,args.output),sort_keys=True))
