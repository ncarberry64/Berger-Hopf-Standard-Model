"""Evaluate the recovered parent density; require explicit physical matching."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,ctx

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'src'))
try:
    from muon_parent_maxwell_velocity import (current_parent_fields,
        local_velocity_density,electromagnetic_trace_coefficient,
        MissingConnectionAttachment)
except ModuleNotFoundError:
    from bhsm.interface.muon_parent_maxwell_velocity import (current_parent_fields,
        local_velocity_density,electromagnetic_trace_coefficient,
        MissingConnectionAttachment)
DEFAULT_INPUT=HERE/'inputs.npz'
if not DEFAULT_INPUT.exists():
    DEFAULT_INPUT=HERE.parent/'artifacts/muon_parent_geometry_20261001/inputs.npz'

def save_json(path,value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n',encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def ball_density(state,log_R4, *, rho_pi_fraction):
    """Outward Arb evaluation for exact supplied binary64 inputs at fixed rho.

    These enclosures do not include parent-history/domain/matching error.
    Coefficients remain factored by kappa1 and c_Q.
    """
    with ctx.workprec(192):
        q=[arb(float(z)) for z in state[:37]]
        m=[arb(float(z)) for z in state[74:98]]
        rho=arb.pi()*arb(rho_pi_fraction)
        chi=rho/2
        u=sum((q[k]*(4*k*chi).cos() for k in range(1,13)),arb(0))
        w=(2*chi).sin()**2*sum((q[13+j]*(4*j*chi).cos() for j in range(12)),arb(0))
        v=(2*chi).sin()**2*sum((q[25+j]*(4*j*chi).cos() for j in range(12)),arb(0))
        ub=sum((q[k]*(-1)**k for k in range(1,13)),arb(0))
        vb=sum((q[25+j]*(-1)**j for j in range(12)),arb(0))
        rb=arb(float(log_R4)).exp()
        scale=2*rb*(-ub).exp()*(2*vb).cosh().sqrt()
        A=scale*(u+v).exp()*chi.cos()
        B=scale*(u-v).exp()*chi.sin()
        C=scale*(u+w).exp()/2
        LF=(A*A+B*B).sqrt(); r=A*B/LF
        logN=sum((m[k-1]*(4*k*chi).cos() for k in range(1,13)),arb(0))
        logNb=sum((m[k-1]*(-1)**k for k in range(1,13)),arb(0))
        nu=(logN-logNb).exp()
        sig=-arb(1)/2+rho/arb.pi()-(2*rho).sin()/(2*arb.pi())
        lam=1-4*sig*sig
        kcomp=arb.pi()**2*LF**5
        density=kcomp*lam*C*r/(nu*rb)
        return dict(rho='pi*'+str(rho_pi_fraction),
            K_component_per_kappa1=kcomp.str(45),
            E_b_local_per_kappa1_cQ=density.str(45),
            relative_accuracy_bits=int(density.rel_accuracy_bits()),
            classification='CERTIFIED_ARITHMETIC_FOR_EXACT_CACHED_INPUTS__MATCHING_AND_HISTORY_ERRORS_NOT_INCLUDED')

def run(input_path,out):
    if out.exists():
        raise FileExistsError('new dedicated output directory required')
    out.mkdir(parents=True)
    with np.load(input_path,allow_pickle=False) as a:
        inputs={k:np.array(a[k]) for k in a.files}
    # A fixed radial collocation inventory, not a parameter sweep or a new
    # radial/temporal solve. No quadrature or continuum bound is inferred.
    rho=np.linspace(0,np.pi/2,65)
    f=current_parent_fields(inputs['states'],inputs['log_R4'],rho)
    d=local_velocity_density(f,angular_haar_Gram=inputs['angular_Haar_Gram'])
    np.savez(out/'local_parent_velocity_density.npz',**f,**d,
        proper_times=inputs['proper_times'],boundary_H=inputs['boundary_H'])
    balls=[dict(history_node=i,**ball_density(inputs['states'][i],inputs['log_R4'][i],rho_pi_fraction=frac))
           for i in (0,47) for frac in ('1/4','1/2')]
    try:
        electromagnetic_trace_coefficient(f['connection_component_coefficient_per_kappa1'])
    except MissingConnectionAttachment as exc:
        preflight=str(exc)
    eb=d['b_velocity_density_per_kappa1_cQ']
    receipt=dict(
        classification='EXECUTED_CURRENT_C2_GEOMETRIC_PREDECESSOR_MAXWELL_VELOCITY_DENSITY__FACTORED_NOT_COMPLETE_AE4_ELECTRIC_HESSIAN',
        source_parent_revision='524ed90689bd5923c249bba2e699abf627e703cd',
        input_sha256=sha(input_path),history_nodes=len(inputs['states']),radial_sample_points=len(rho),
        density_frame='b; beta=b/sqrt(2*pi^2*R4), Haar-normalized eight photon angular modes',
        density_factor='E_b=(kappa1*c_Q)*recorded_density; c_Q=Tr16(Q^2)/I_jmath',
        EM_attachment_index_selected=False,component_coefficient='K_comp=kappa1*pi^2*L_F^5',
        electric_angular_scalarity_reason='cohomogeneity-one round quotient orbit, radial-only lapse/weight and supplied orthonormal mode lifts',
        electric_scalarity_inferred_from_curl=False,curl_squared_restriction='9 I8; full covariant magnetic operator not inferred from it',
        raw_reference_RADIUS0_normalization_copied=False,
        boundary_density_per_kappa1_cQ_first=float(eb[0,-1]),
        boundary_density_per_kappa1_cQ_last=float(eb[-1,-1]),
        sample_grid_min=float(eb.min()),sample_grid_max=float(eb.max()),
        samples_are_integrated_profile_contraction=False,certified_fixed_input_values=balls,
        full_AE4_matching_remainder=None,complete_common_domain_residual=None,
        positivity_of_sampled_predecessor_density=bool(np.all(eb>=0)),
        native_shifted_resolvent_actions=0,physical_soft_transfer_directions=0,
        physical_a_mu=None,physical_g_mu=None,preflight=preflight)
    save_json(out/'result.json',receipt)
    first=dict(
        map='jmath_EH_to_Q',
        definition='connection embedding of the SAME mechanical Sp(1) component amplitude and its retained neutral extension into the rank16 gauge connection used by D_strat[beta]',
        normalization_equation='Tr16(jmath(L_a)^dagger*jmath(L_b))=I_jmath*delta_ab; K_trace=K_comp/I_jmath; K_Q=K_comp*(16/3)/I_jmath',
        source_equation='D_strat[beta]=D_strat[0]+sum_A beta_A*Xi_Q,A+... on the common domain, with Xi_Q,A from this same embedding',
        known_geometry='A,B,C,lapse,radial shift and quotient scale are supplied and now evaluated',
        unresolved_classification='the same-action mechanical-to-neutral/positive-source realization is unspecified in the inspected matching route; not an unfinished Maxwell geometry solve',
        primitive_E8_geometric_density_computed=True,
        positive_functional_owner_selected=True,
        new_Wick_or_domain_or_Wilson_choice_allowed=False,
        next_step='materialize the existing action-owned connection attachment jmath_EH_to_Q and its normalization/source map; then evaluate the retained induced matching remainder rather than set it zero')
    save_json(out/'missing_map.json',first)
    save_json(out/'checkpoint.json',dict(result=receipt,first_missing_map=first,
        source_parent_revision=receipt['source_parent_revision'],
        checkpoint_id='BHSM_MUON_CURRENT_PARENT_LOCAL_VELOCITY_524ED906_20261001',
        earlier_evidence_preserved=True,earlier_derivations_or_tests_repeated=False,
        local_contributions_frozen=True,native_terms_added_to_local=False,
        full_native_bulk=None,state=None,contact=None,domain_boundary=None,
        completion_counterterm=None,strong_within_native=None,
        github_scope='reviewable predecessor velocity-density milestone; no physical muon anomaly',
        replay='python replay.py --input inputs.npz --output <new-directory>'))
    save_json(out/'packet_hashes.json',dict(files=[dict(path=p.name,sha256=sha(p)) for p in sorted(out.iterdir())]))
    print(json.dumps({k:receipt[k] for k in (
        'classification','boundary_density_per_kappa1_cQ_first','boundary_density_per_kappa1_cQ_last',
        'native_shifted_resolvent_actions')},sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,default=DEFAULT_INPUT)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    run(args.input.resolve(),args.output.resolve())
