"""Actual finite scalar Cauchy direction; not a full solution multiplicity proof.

The intrinsic pole problem does not require collider preparation after a
complete background/operator is fixed. This separate local calculation asks
what the future retarded prescription alone says about that nonlinear
background. No quartic, external moment or new boundary value is selected.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import numpy as np

REPO=Path(r'C:\Users\carbe\Downloads\BHSM_muon_parent_maxwell_worktree_20261001')
sys.path.insert(0,str(REPO/'src'))
from bhsm.interface.muon_profile_preserving_phase_sample import (
    load_profile_preserving_phase, profile_preserving_lepton_sample,
)
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from bhsm.interface.muon_nonlinear_n0_field_action import analytic_intrinsic_n0_jet
from bhsm.interface.muon_literal_euclidean_wall_action import VOLUME


def evaluate(output):
    folder='artifacts/muon_inherited_finite_normal_phase_20261011/run_1'
    phase=load_profile_preserving_phase(folder,repository=REPO)
    sample=profile_preserving_lepton_sample(phase,0.)
    raw=sample['sample']['raw_fields']
    if not np.isrealobj(raw):
        raise ValueError('real retained historical phase required without projection')
    h=raw[-8:-4];hd=raw[-4:]
    weight=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],
        source_value=raw[98],source_rate=raw[99])
    wt,ws,wv=[float(weight[x].value) for x in ('wT','wS','wV')]
    a=wt/VOLUME
    if a<=0 or np.linalg.norm(h)==0:
        raise ValueError('nonzero scalar and positive real wall Legendre block required')
    generators=higgs_u2_real_representation()['real_generators']
    connection=np.einsum('fc,cij->fij',sample['operator']['total_wall_connection'],generators)
    # Exact canonical real4 momentum for the same 1/V local wall action.
    pi=2*a*(hd+connection[0]@h)
    direction=h/np.linalg.norm(h)  # unit coordinate direction, not a spin state
    gauge_orbit=np.stack([g@h for g in generators],axis=1)
    gauss_direction=gauge_orbit.T@direction
    projection=gauge_orbit@np.linalg.lstsq(gauge_orbit,direction,rcond=None)[0]
    # For L=a|Hdot+O_t H|^2-... and pi->pi+eps direction,
    # H_can(eps)-H_can(0)=c1 eps+c2 eps^2. The O_t term
    # is retained, and vanishes in this direction by antisymmetry alone.
    c1=float(pi@direction/(2*a)-direction@connection[0]@h)
    c2=float(direction@direction/(4*a))
    q=float(h@h)
    # Potential Hessian per unit lambda_H remains a polynomial in the
    # unselected numerical nu_squared, rather than choosing either value.
    lambda_hessian_constant=(-4*wv/VOLUME)*(q*np.eye(4)+2*np.outer(h,h))
    lambda_hessian_nu_squared=(4*wv/VOLUME)*np.eye(4)
    # On a scalar radial stationary saddle q=nu_squared, its three
    # tangent eigenvalues vanish but its radial lambda derivative does not.
    saddle_radial_lambda_eigenvalue=float(-8*wv*q/VOLUME)
    result=dict(
        classification='ACTUAL_REAL_FINITE_LOCAL_CANONICAL_RADIAL_DIRECTION_NOT_FULL_COUPLED_FAMILY',
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        consumed_history=folder,input_hashes=phase['input_hashes'],
        scalar_norm=float(np.linalg.norm(h)),
        temporal_connection_real4_norm=float(np.linalg.norm(connection[0])),
        canonical_scalar_legendre_eigenvalue=2*a,
        all_four_scalar_Gauss_moment_map_direction_max=float(np.max(abs(gauss_direction))),
        gauge_generator_antisymmetry_max=float(np.max(abs(generators+generators.transpose(0,2,1)))),
        radial_direction_gauge_orbit_projection_norm=float(np.linalg.norm(projection)),
        radial_canonical_energy_polynomial=dict(linear=c1,quadratic=c2),
        nonzero_radial_energy_variation=c2>0,
        scalar_potential_Hessian_lambda_derivative_constant=lambda_hessian_constant.tolist(),
        scalar_potential_Hessian_lambda_derivative_nu_squared_coefficient=lambda_hessian_nu_squared.tolist(),
        radial_saddle_lambda_derivative=saddle_radial_lambda_eigenvalue,
        scalar_potential_radial_saddle_scope='q=nu_squared is the isolated scalar potential saddle only, not a full kinetic/gauge/geometric stationary solution',
        numerical_lambda_H_or_nu_squared_consumed=False,
        local_canonical_momentum_readout_scope='same intrinsic_n0 1/V action on stored fields; no nonlinear phase solve',
        scalar_Gauss_identity='delta J_alpha=direction^T T_alpha h=0 since direction is parallel to h and T_alpha is antisymmetric; holds for all eps at held h',
        full_gravity_or_Maxwell_constraint_family_established=False,
        actual_new_Cauchy_data_or_quiet_surroundings_selected=False,
        intrinsic_pole_requires_collider_history=False,
        full_nonlinear_background_selected=False,
        physical_two_spin_normalization=None,muon_magnetic_moment=None,
        physical_full_outgoing_derivative_passed=False,coupled_corrections=0)
    # Literal derivative formula independent of the gauge part of the
    # canonical Legendre transform; no numerical quartic is assigned here.
    result['analytic_owner']='muon_nonlinear_n0_field_action.analytic_intrinsic_n0_jet'
    paths=['src/bhsm/interface/'+name+'.py' for name in (
        'muon_nonlinear_n0_field_action','muon_intrinsic_higgs_gauge_action',
        'muon_literal_euclidean_wall_action','muon_intrinsic_m4_normal_pullback',
        'muon_profile_preserving_phase_sample')]
    result['owner_hashes']={p:sha256((REPO/p).read_bytes()).hexdigest() for p in paths}
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:result[k] for k in ('scalar_norm','temporal_connection_real4_norm',
        'all_four_scalar_Gauss_moment_map_direction_max','radial_direction_gauge_orbit_projection_norm',
        'radial_canonical_energy_polynomial','radial_saddle_lambda_derivative')},sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    evaluate(p.parse_args().output)
