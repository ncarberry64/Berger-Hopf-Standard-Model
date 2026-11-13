"""Reached scalar/interface parameter contacts on the saved real phase.

No physical trajectory or coefficient is selected. Read the original real
initial/stage268 values, differentiate the owned scalar potential polynomial
and retained ambient-cap area density per gamma, and check those jets by literal
finite differences on the same recorded germ. Do not replay a source solve.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys


def evaluate(repository, output):
    import numpy as np
    root, out = Path(repository).resolve(), Path(output).resolve()
    if out.exists():
        raise FileExistsError('Preserve earlier applications.')
    sys.path.insert(0,str(root/'src'))
    from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import Jet
    from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
    from bhsm.interface.muon_literal_euclidean_wall_action import VOLUME
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz

    folder='artifacts/muon_inherited_finite_normal_phase_20261011/run_1'
    receipt_rel=folder+'/result.json'
    data_rel=folder+'/application.npz'
    md=json.loads((root/receipt_rel).read_bytes())
    if sha256((root/data_rel).read_bytes()).hexdigest()!=md['numerical_sha256']:
        raise ValueError('Recorded original phase changed.')
    if md['completed_steps']!=md['steps'] or md['classification']!='EVALUATED_INHERITED_PROFILE_CHILD_CANONICAL_ACTION':
        raise ValueError('Completed original finite phase required.')
    with np.load(root/data_rel,allow_pickle=False) as archive:
        initial=archive['initial_independent_raw'].copy()
        stages=archive['stage_independent_raw'].copy()
        times=archive['stage_coordinate_time'].copy()
    raw=np.concatenate((initial[None],stages))
    if raw.shape[1]!=268 or not np.isrealobj(raw) or not np.isfinite(raw).all():
        raise ValueError('Actual real initial/stage268 coordinates required; no complex projection.')
    nu2=float(md['action_parameters']['nu_squared_action'])
    names=['initial']+[f'stage_{i:04d}' for i in range(len(stages))]
    eye=np.eye(104)

    def application(x):
        if x.shape!=(104,) or not np.isrealobj(x):
            raise ValueError('Original real geometry100 plus H4 required.')
        w=intrinsic_m4_weight_jet(12,x[:37],x[37:74],x[74:98],
            source_value=x[98],source_rate=x[99])
        def lift(j):
            g=np.r_[j.gradient,np.zeros(4)]
            h=np.zeros((104,104));h[:100,:100]=j.hessian
            return Jet(j.value,g,h)
        hv=[Jet.affine(x[100+j],eye[100+j]) for j in range(4)]
        q=sum((h*h for h in hv),Jet.constant(0.,104))
        pv=lift(w['wV'])/VOLUME
        # Original normalized n0 intrinsic action is S4/VOLUME^2;
        # its Haar-constant potential density is -wV*(H.H-nu2)^2/VOLUME.
        poly=[-pv*q*q,2*pv*q,-pv]
        # Original ambient-cap angular area, NOT the intrinsic M4 quotient
        # volume. A^3 B^3 retains both S3 orbit factors; no M5 relabelling.
        area=lift(-w['induced_lapse']*(w['fields']['A']*w['fields']['B'])**3)
        return poly+[area], w

    all_values,all_gradients,all_hessians,all_force=[],[],[],[]
    records=[]
    d=np.sin(np.arange(104)+.37);d/=np.linalg.norm(d)
    e=np.zeros(104);e[[0,25,74,98,99,100,101,102,103]]=[.2,-.1,.15,.3,-.2,.2,-.4,.1,.25];e/=np.linalg.norm(e)
    directions=np.array([d,e])
    h=1e-4
    for name,rr in zip(names,raw):
        x=np.r_[rr[:100],rr[260:264]]
        jets,w=application(x)
        vals=np.array([j.value for j in jets])
        grad=np.array([j.gradient for j in jets])
        hess=np.array([j.hessian for j in jets])
        all_values.append(vals);all_gradients.append(grad);all_hessians.append(hess)
        scalar=jets[0]+nu2*jets[1]+nu2*nu2*jets[2]
        force_action_H=scalar.gradient[100:]
        all_force.append(force_action_H)
        expected=-4*w['wV'].value*(x[100:]@x[100:]-nu2)*x[100:]/VOLUME
        checks=[]
        for direction in directions:
            nearby={k:application(x+k*h*direction)[0] for k in (-2,-1,1,2)}
            f={k:np.array([j.value for j in nearby[k]]) for k in nearby}
            g={k:np.array([j.gradient for j in nearby[k]]) for k in nearby}
            fd1=(f[-2]-8*f[-1]+8*f[1]-f[2])/(12*h)
            fd2=(g[-2]-8*g[-1]+8*g[1]-g[2])/(12*h)
            a1=grad@direction
            a2=np.einsum('kij,j->ki',hess,direction)
            checks.append(dict(
                value_to_gradient_max_scaled_error=float(np.max(abs(fd1-a1)/np.maximum(1.,abs(a1)))),
                gradient_to_Hessian_vector_max_scaled_error=float(np.max(abs(fd2-a2)/np.maximum(1.,abs(a2)))),
                value_to_gradient_errors=(fd1-a1).tolist(),
                gradient_to_Hessian_vector_norm_errors=np.linalg.norm(fd2-a2,axis=1).tolist(),
            ))
        records.append(dict(
            state=name,
            scalar_H_norm=float(np.linalg.norm(x[100:])),
            assigned_historical_nu_squared_action=nu2,
            wV=float(w['wV'].value),
            intrinsic_R4=float(w['R4'].value),
            real_induced_lapse=float(w['induced_lapse'].value),
            original_cap_area_density_per_gamma=float(jets[3].value),
            original_cap_area_vs_intrinsic_volume_ratio=float(-jets[3].value/w['wV'].value),
            geometry_gradient_per_gamma_norm=float(np.linalg.norm(jets[3].gradient[:100])),
            geometry_Hessian_per_gamma_norm=float(np.linalg.norm(jets[3].hessian[:100,:100])),
            partial_lambda_H_action_cotangent_norm=float(np.linalg.norm(force_action_H)),
            partial_lambda_H_action_cotangent=force_action_H.tolist(),
            same_scalar_cotangent_literal_formula_error=float(np.max(abs(force_action_H-expected))),
            finite_difference_checks=checks,
            source_amplitude=float(rr[98]),source_rate=float(rr[99]),
        ))
    arrays=dict(actual_initial_and_stage_raw=raw,actual_stage_coordinate_times=times,
        coefficient_polynomial_values=np.array(all_values),
        coefficient_polynomial_gradients=np.array(all_gradients),
        coefficient_polynomial_hessians=np.array(all_hessians),
        assigned_nu2_partial_lambda_H_action_cotangent=np.array(all_force),
        actual_germ_test_directions=directions)
    source_files=[
        'src/bhsm/interface/muon_intrinsic_m4_normal_pullback.py',
        'src/bhsm/interface/muon_moving_geometric_action.py',
        'src/bhsm/interface/muon_birth_finite_normal_trace_graph.py',
        'src/bhsm/interface/muon_material_higgs_gauge_action.py',
        'src/bhsm/interface/muon_literal_euclidean_wall_action.py',
        'src/bhsm/interface/aether_exact_radial_schur_lift_v15_83.py',
        'src/bhsm/interface/aether_n3_exact_full_local_action_jet_v17_60.py',
        'src/bhsm/interface/aether_unified_m5_m4_pushforward_v15_69.py',
        'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
    ]
    pins={p:sha256((root/p).read_bytes()).hexdigest() for p in [data_rel,receipt_rel,*source_files]}
    result=dict(
        classification='ACTUAL_SAVED_REAL_PHASE_SCALAR_POTENTIAL_AND_ORIGINAL_CAP_AREA_PARAMETER_CONTACTS',
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_hashes=pins,records=records,
        scalar_polynomial_coefficient_order=['lambda_H','lambda_H_times_nu_squared','lambda_H_times_nu_fourth'],
        fourth_array_coefficient='surface_gamma',
        coordinate_order='geometry q37,v37,m24,s,sdot then real intrinsic H4; total104',
        scalar_action_polynomial='-wV/VOLUME * [lambda_H*(H.H)^2-2*(lambda_H*nu2)*(H.H)+lambda_H*nu2^2]',
        actual_original_cap_area_coefficient='-induced_lapse*(A*B)^3, in original ambient angular action measure with both S3 orbit factors retained',
        surface_coefficient_scope='Geometry jets of the coefficient multiplying gamma, with gamma held fixed. Full physical gamma=alpha_FSC*ell_s^(-m) variation also requires gamma_a*area and gamma_ab*area+gamma_a*area_b+gamma_b*area_a; those scale contacts are not evaluated here.',
        scalar_angular_action_normalization='Constant scalar action S4/VOLUME^2; normalized n0 scalar integrand divided by VOLUME=2pi^2 once.',
        scalar_H_force_sign_and_pairing='Exported H4 cotangent is partial_H of signed potential L, per lambda at recorded nu2; canonical momentum-equation force is its negative half in the complex2Re pairing.',
        assigned_nu2_provenance='Read unchanged4.0 from historical finite phase action_parameters; not a new physical scalar scale or unit matching.',
        numeric_lambda_H_assigned=False,numeric_surface_gamma_assigned=False,
        empirical_scalar_or_lepton_input_consumed=False,
        literal_fd_scheme='Five-point first derivative of value and gradient with one fixed h=1e-4; two declared coefficient directions. Finite-germ diagnostics, not rigorous continuum or physical derivative enclosures.',
        first_jet_scope='Actual coefficient sensitivities of original scalar potential and original ambient-cap area at saved real initial/stage values; no stratum transfer or Gamma_boundary quartic extraction performed.',
        real_timelike_local_germ_confirmed=True,real_physical_stationary_history_constructed=False,
        field_dependent_outgoing_domain_or_E_B_derivative_evaluated=False,
        scalar_interface_coefficients_cannot_be_removed_as_uniform_action_units=True,
        nonzero_action_contact_proves_nonzero_Pauli_parameter_dependence=False,
        completed_source_campaign_replayed=False,coupled_matching_corrections_applied=0,
        physical_muon_moment=None,
    )
    out.mkdir(parents=True)
    _compressed_npz(out/'actual_real_phase_parameter_contacts.npz',arrays)
    result['array_archive_sha256']=sha256((out/'actual_real_phase_parameter_contacts.npz').read_bytes()).hexdigest()
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(records=records,result_sha256=sha256((out/'result.json').read_bytes()).hexdigest()),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();evaluate(a.repository,a.output)
