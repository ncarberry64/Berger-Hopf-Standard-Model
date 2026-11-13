"""Actual REAL birth-side FP flux/density constituents, with the base reset active.

This applies the retained one-cell source germs at their shared t=0 face.
It does not prescribe F_B, its differential, pulled ghost data or a total J.
The displayed common gauge representative follows AE2; it is not F_B=Id.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
sys.path.insert(0, str(ROOT/'scripts'))
from bhsm_real_full_d5_combined_eta_open_form_20261016 import (
    PHASES, radial_representation, sample_coefficients)
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_exact_material_response import exact_geometric_connection_coefficient_jets
from bhsm.interface.muon_holomorphic_normal_geometry import (
    _geometry_variables, _fields, _sqrt, _response, anchored_holomorphic_chart)
from bhsm.interface.muon_parent_maxwell_corrected_retarded import _ad
from bhsm.interface.gauge_connection_reset_bundle_lift_adjudication import common_reset_gauge_vertical_one_jet
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from bhsm.interface.muon_regular_reset_brst_domain import REGULAR_OWNER, AFFINE_OWNER
from bhsm.interface.muon_parent_retarded_hypercharge import WALL


def real(a, name):
    a = np.asarray(a)
    if not np.isfinite(a).all() or (np.iscomplexobj(a) and np.any(a.imag != 0)):
        raise ValueError('Actual real source chart required: '+name)
    return np.asarray(a.real, float)


def product(a, b):
    return np.array([a[0]*b[0], a[1]*b[0]+a[0]*b[1]])


def reciprocal(a):
    return np.array([1/a[0], -a[1]/a[0]**2])


def power(a, p):
    return np.array([a[0]**p, p*a[0]**(p-1)*a[1]])


def error(a, b):
    return dict(absolute=float(np.max(abs(a-b))),
        relative=float(np.max(abs(a-b)/np.maximum(np.maximum(abs(a), abs(b)), 1e-300))))


def coefficients(phase):
    original = phase['representation']
    rho = np.r_[original['rho'], WALL]
    rep = radial_representation(original, rho)
    c, sample = sample_coefficients(phase, 0., rep)
    c = {k: real(v, k) for k,v in c.items() if isinstance(v,np.ndarray)}
    raw, rate = sample['raw_fields'], sample['raw_coordinate_time_derivative']
    geo = exact_geometric_connection_coefficient_jets(12, raw[:37], raw[37:74], raw[74:98], rho,
        source_value=raw[98], source_rate=raw[99])
    fromc = lambda name: np.array([c[name], c[name+'_first'][0]])
    fromgeo = lambda name: np.array([[row[name].value for row in geo['rows']],
        [row[name].gradient@rate[:100] for row in geo['rows']]])
    N,C,R,z = (fromc(k) for k in ('lapse','radial_coframe','radius','coordinate_shift'))
    e,r,d = (fromgeo(k) for k in ('electric','radial','angular'))
    gt,gr,gs = (product(a,power(R,2)) for a in (e,r,d))
    mu = product(d,power(R,4))
    btime = product(mu,reciprocal(N))
    bare = product(C,power(R,3))
    common = product(btime,reciprocal(bare))
    q,v,m,delta,wallrate,wall,_ = _geometry_variables(raw[:100])
    LF=[];stable_common=[]
    chart=anchored_holomorphic_chart(delta.value)
    for rr in rho:
        f=_fields(12,q,v,m,(rr/WALL)*wall)
        L=_sqrt(f['A']**2+f['B']**2)
        LF.append((L.value,L.gradient@rate[:100]))
        response=_response((rr/WALL)*wall,delta,wallrate,chart)
        w=2*np.pi**4*L**5*response['localization_weight']
        stable_common.append((w.value,w.gradient@rate[:100]))
    LF=real(np.array(LF).T,'LF one jet')
    sigma=fromc('sigma'); weight=np.array([1-4*sigma[0]**2,-8*sigma[0]*sigma[1]])
    common_direct=2*np.pi**4*product(power(LF,5),weight)
    stable_common=real(np.array(stable_common).T,'stable direct common one jet')
    # Flux density = a_t D_t c + a_r D_rho c, with material At/Ar once.
    time_t=gt;time_r=-product(gt,z)
    wall_t=time_r
    wall_r=gr+product(gt,power(z,2))
    A=np.array([c['gauge_connection_material'],c['gauge_connection_material_first'][0]])
    comm=np.array([[[_ad(a) for a in point] for point in axis] for axis in A])
    body = lambda a,b: np.array([
        a[0,:,None,None]*comm[0,:,0]+b[0,:,None,None]*comm[0,:,1],
        a[1,:,None,None]*comm[0,:,0]+a[0,:,None,None]*comm[1,:,0]
        +b[1,:,None,None]*comm[0,:,1]+b[0,:,None,None]*comm[1,:,1]])
    # Positive-reference induced wall measure; not the Lorentz wall measure.
    wallnorm=power(power(N,2)+product(power(C,2),power(z,2)),.5)
    bwall=product(product(common,power(R,3)),wallnorm)
    blorentz=product(product(common,power(R,3)),fromc('surface_proper_clock_rate'))
    identity_rows=dict(
        full_Maxwell_weight_vs_direct_stable_cumulative=error(common,stable_common),
        naive_LF_sigma_subtraction_roundoff_diagnostic=error(common,common_direct),
        metric_volume_vs_common_N_C_R3=error(mu,product(common,product(N,bare))),
        temporal_flux_vs_boundary_measure_over_lapse=error(gt,product(btime,reciprocal(N))),
        source_shift_vs_geometry=error(z,fromgeo('shift')),
        density_two_form_identity=error(fromgeo('electric_radial'),product(product(e,r),reciprocal(d))))
    out=dict(rho=rho,raw=raw,raw_coordinate_time=rate,
        common_Maxwell_weight=common,direct_stable_Maxwell_weight=stable_common,
        naive_subtracted_Maxwell_weight=common_direct,LF=LF,sigma=sigma,lapse=N,radial_coframe=C,radius=R,shift=z,
        ghost_volume_density=mu,temporal_boundary_density=btime,
        positive_reference_material_wall_boundary_density=bwall,
        Lorentz_material_wall_boundary_density=blorentz,
        angular_S3_weighted_density=product(common,power(R,3)),
        temporal_unoriented_density_Dt_coefficient=time_t,
        temporal_unoriented_density_Drho_coefficient=time_r,
        temporal_unoriented_density_covariant_body=body(time_t,time_r),
        material_wall_unoriented_density_Dt_coefficient=wall_t,
        material_wall_unoriented_density_Drho_coefficient=wall_r,
        material_wall_unoriented_density_covariant_body=body(wall_t,wall_r),
        angular_FP_density_coefficient=gs,gauge_connection_material=A,
        adjoint_connection_material=comm,original_radial_quadrature=original['radial_quadrature'])
    out['birth_outward_temporal_density_Dt_coefficient']=time_t*(1 if phase['receipt']['side']=='incoming' else -1)
    out['birth_outward_temporal_density_Drho_coefficient']=time_r*(1 if phase['receipt']['side']=='incoming' else -1)
    out['birth_outward_temporal_density_covariant_body']=body(time_t,time_r)*(1 if phase['receipt']['side']=='incoming' else -1)
    return out,identity_rows,sample


def execute(output):
    out=Path(output).resolve()
    if out.exists():raise FileExistsError('Preserve independent numerical applications')
    arrays={};records=[];pins={};sides={}
    for side,path in PHASES.items():
        phase=load_profile_preserving_phase(path,repository=ROOT)
        if phase['receipt']['steps']!=1:raise ValueError('Original complete one-cell sources required')
        a,rows,sample=coefficients(phase);sides[side]=a;pins.update(phase['input_hashes'])
        arrays.update({side+'_'+k:v for k,v in a.items()})
        records.append(dict(side=side,coordinate_time=0.,source_slot='inside-cell future coordinate time, frozen v/y',
            signed_phase_span=float(phase['receipt']['span']),radial_interior_count=len(a['rho'])-1,
            actual_wall_separate=True,original_radial_nodes_retained=True,
            density_and_source_identity_rows=rows,
            common_weight_min=float(np.min(a['common_Maxwell_weight'][0])),
            common_weight_source_norm=float(np.linalg.norm(a['common_Maxwell_weight'][1])),
            temporal_boundary_density_source_norm=float(np.linalg.norm(a['temporal_boundary_density'][1])),
            gauge_value_norm=float(np.linalg.norm(a['gauge_connection_material'][0])),
            gauge_source_norm=float(np.linalg.norm(a['gauge_connection_material'][1])),
            all_three_spatial_connection_norms=np.linalg.norm(a['gauge_connection_material'][0,:,2:],axis=(0,2)).tolist(),
            temporal_covariant_flux_body_norm=float(np.linalg.norm(a['temporal_unoriented_density_covariant_body'][0])),
            wall_covariant_flux_body_norm=float(np.linalg.norm(a['material_wall_unoriented_density_covariant_body'][0]))))
    if not np.array_equal(sides['incoming']['rho'],sides['outgoing']['rho']):raise ValueError('Same source reference chart required')
    # This is an evaluated coefficient in a common chart, NEVER total F*mu_c/mu_p.
    for name in ('temporal_boundary_density','positive_reference_material_wall_boundary_density',
            'Lorentz_material_wall_boundary_density','angular_S3_weighted_density'):
        arrays['same_coordinate_child_over_parent_'+name]=product(sides['outgoing'][name],reciprocal(sides['incoming'][name]))
    vertical=common_reset_gauge_vertical_one_jet(4,2)
    arrays['AE2_common_gauge_vertical_G_R']=vertical['G_R']
    arrays['AE2_common_gauge_vertical_dG_R']=vertical['dG_R']
    arrays['AE2_common_gauge_adjoint_representative4']=np.eye(4)
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':
            pp=Path(p);pins[pp.relative_to(ROOT).as_posix()]=sha256(pp.read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    result=dict(classification='ACTUAL_REAL_BIRTH_FP_WEIGHTED_CONORMAL_AND_GAUGE_VERTICAL_CONSTITUENTS',
        jet_order=['value','supplied_source_first'],records=records,
        weight='common=2*pi**4*LF**5*(1-4*sigma**2); mu_FP=common*N*C_rho*R**3',
        temporal_density_flux='outward_sign*common*C_rho*R**3/N*(D_t-z*D_rho)',
        material_wall_density_flux='-gt*z*D_t+(gr+gt*z**2)*D_rho, gt=common*C_rho*R**3/N, gr=common*N*R**3/C_rho',
        boundary_measure_conventions=dict(temporal='common*C_rho*R**3 drho dOmega3',
            positive_reference_wall='common*R**3*sqrt(N**2+C_rho**2*z**2) dt dOmega3',
            Lorentz_wall='common*R**3*surface_proper_clock_rate dt dOmega3'),
        ghost_and_independent_antighost_share_the_derived_adjoint_graph=True,
        supplied_ghost_or_antighost_solutions=False,ghost_trace_or_conormal_loads=None,
        common_gauge_vertical_owner=vertical['status'],common_gauge_choice_does_not_select_base_map=True,
        full_spin_lift_derivative_claimed_zero=False,regular_domain_owner=REGULAR_OWNER,affine_connection_owner=AFFINE_OWNER,
        physical_base_reset_F_B=None,physical_base_reset_DF_B=None,total_boundary_density_ratio_J=None,
        base_reset_scope='F_B and its total jets remain coupled field unknowns selected by worldvolume/first-crossing equations, not a new external preparation choice',
        same_coordinate_ratios_are_not_total_reset_J=True,
        total_J_formula='F_B^*(displayed child boundary density)/displayed parent boundary density; includes det DF_B and all measure/clock/base motion contacts',
        regular_reset_fp_domain_jets_called=False,
        reason_graph_not_evaluated='No supplied solved F_B/DF_B and pulled ghost/antighost conormal fields; no identity, zero load, or frozen missing jets inserted',
        finite_positive_reference_not_proved_physical_FP_domain=True,
        no_pure_connection_pullback_equation_imposed_on_off_shell_trial=True,
        all_internal_four_Lie_components_retained=True,source_profile_composed_once=True,
        polar_weight_evaluation='Stable owned 4*p*(1-p); naive 1-4*sigma**2 comparison retained separately and is not a physical derivative test',
        angular_truncation_for_local_coefficient_maps=None,radial_integration_performed=False,
        new_history_source_or_profile_integrations=0,coupled_corrections=0,
        physical_derivative_at_2e_minus10_passed=False,physical_outgoing_domain_evaluated=False,
        normalized_physical_spins=None,physical_muon_magnetic_moment=None,
        input_and_source_sha256=dict(sorted(pins.items())))
    out.mkdir(parents=True)
    _compressed_npz(out/'application.npz',arrays)
    result['numerical_sha256']=sha256((out/'application.npz').read_bytes()).hexdigest()
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();r=execute(a.output)
    print(json.dumps(dict(classification=r['classification'],numerical_sha256=r['numerical_sha256']),sort_keys=True))
