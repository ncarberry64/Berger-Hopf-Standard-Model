"""Actual retained cap-area inertia contact, with no coefficient assignment.

Read the previous parameter-contact packet; do not replay its source or
profile calculations. Independently differentiate the literal rate density.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys


def evaluate(repository, output):
    import numpy as np
    import mpmath as mp
    root,out=Path(repository).resolve(),Path(output).resolve()
    if out.exists(): raise FileExistsError('Preserve earlier scientific outputs')
    sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
    source='artifacts/muon_real_action_inputs_20261015/parameter_contacts_run_1'
    result_rel=source+'/result.json'
    arrays_rel=source+'/actual_real_phase_parameter_contacts.npz'
    receipt=json.loads((root/result_rel).read_bytes())
    if sha256((root/arrays_rel).read_bytes()).hexdigest()!=receipt['array_archive_sha256']:
        raise ValueError('Original parameter contact archive changed')
    with np.load(root/arrays_rel,allow_pickle=False) as data:
        states=data['actual_initial_and_stage_raw'].copy()
        area_hessians=data['coefficient_polynomial_hessians'][:,3,:100,:100].copy()
    if not np.isrealobj(states): raise ValueError('Do not project complex states')
    records=[]
    mp.mp.dps=80
    for index,(raw,Hessian) in enumerate(zip(states,area_hessians)):
        w=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],
                                source_value=raw[98],source_rate=raw[99])
        A,B,C,N=[w['fields'][k].value for k in ('A','B','C','N')]
        cstar,U,lapse=[w[k].value for k in ('Cstar','U','induced_lapse')]
        rho=(A*B)**3
        a=C/(N*cstar)
        explicit=rho*C*C/(N*cstar*cstar*(1-U*U)**1.5)
        # Every constant here is the actual same-state scalar value. Vary
        # only the declared normal-rate coordinate; no new background.
        n,r,u,slope=map(mp.mpf,(N,rho,U,a))
        literal=lambda delta_rate: -n*r*mp.sqrt(1-(u+slope*delta_rate)**2)
        independent=mp.diff(literal,mp.mpf(0),2)
        original=float(Hessian[99,99])
        records.append(dict(
            state=('initial','stage_0000')[index],
            coordinate_normal_rate_inertia_per_gamma=original,
            independent_closed_formula=explicit,
            independent_MP80_literal_second_derivative=str(independent),
            closed_formula_vs_saved_Hessian_absolute=abs(explicit-original),
            MP80_literal_vs_saved_Hessian_absolute=float(abs(independent-mp.mpf(original))),
            induced_proper_clock=lapse,
            proper_clock_normal_rate_inertia_per_gamma=lapse*explicit,
            normal_rate_geometry_mixed_row_norm=float(np.linalg.norm(Hessian[99])),
            retained_H_norm=float(np.linalg.norm(raw[260:264])),
            retained_gauge_coefficient_norm=float(np.linalg.norm(raw[100:180])),
            area_value=-N*rho*np.sqrt(1-U*U),
            actual_physical_mode_inertia_contraction=None,
        ))
    source_files=[
        'src/bhsm/interface/muon_moving_geometric_action.py',
        'src/bhsm/interface/muon_intrinsic_m4_normal_pullback.py',
        'src/bhsm/interface/muon_complex_endpoint_area_action.py',
        'src/bhsm/interface/covariant_bubble_interface_mechanics.py',
        'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
        'src/bhsm/interface/muon_native_impedance_energy_response.py',
    ]
    pins={p:sha256((root/p).read_bytes()).hexdigest() for p in (result_rel,arrays_rel,*source_files)}
    result=dict(
        classification='ACTUAL_ORIGINAL_AREA_LEGENDRE_INERTIA_CONTACT',
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_hashes=pins,records=records,
        area_rate_second_derivative='rho*C^2/[N*Cstar^2*(1-U^2)^(3/2)]',
        original_unquotiented_orbit_density='rho=A^3 B^3; no M5 or intrinsic-R4 replacement',
        scope='Positive local coordinate inertia per held gamma on historical real initial/stage germs. Not the physical mode-projected total inertia.',
        native_I_can_be_held_fixed_while_varying_gamma_at_fixed_fields=False,
        normalized_mode_scope='A moving I-normalization can cancel this contact only together with its mode/pairing jets; it cannot freeze i,j,h simultaneously.',
        ell_s_equals_native_ell_star_assumed=False,
        surface_gamma_derived_or_assigned=False,
        alpha_FSC_assigned=False,
        spin_or_temporal_connection_erased=False,
        physical_real_fields_or_outgoing_solution_constructed=False,
        physical_full_derivative_passed_2e_minus_10=False,
        physical_two_spin_normalization=None,physical_muon_magnetic_moment=None,
        coupled_matching_corrections_applied=0,
        completed_source_or_profile_campaign_replayed=False,
    )
    out.mkdir(parents=True)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(records=records,result_sha256=sha256((out/'result.json').read_bytes()).hexdigest()),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository',required=True)
    p.add_argument('--output',required=True)
    a=p.parse_args()
    evaluate(a.repository,a.output)
