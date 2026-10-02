"""Evaluate the inherited attachment and event-weighted local electric block."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import numpy as np
from flint import arb,ctx

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'src'))
try:
    from muon_connection_weight import rank16_connection_attachment,matched_local_electric_density
except ModuleNotFoundError:
    from bhsm.interface.muon_connection_weight import rank16_connection_attachment,matched_local_electric_density

def save(p,obj):
    p.write_bytes((json.dumps(obj,indent=2,sort_keys=True)+'\n').encode('utf-8'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def exact_input_ball(state,log_R4,rho_fraction):
    """Certify new arithmetic, using the already-derived current geometry.

    No error for the current history, stratified source/domain matching or
    theory completion is inferred from these fixed-input balls.
    """
    with ctx.workprec(192):
        q=[arb(float(z)) for z in state[:37]]
        m=[arb(float(z)) for z in state[74:98]]
        rho=arb.pi()*arb(rho_fraction);chi=rho/2
        u=sum((q[k]*(4*k*chi).cos() for k in range(1,13)),arb(0))
        window=(2*chi).sin()**2
        w=window*sum((q[13+j]*(4*j*chi).cos() for j in range(12)),arb(0))
        v=window*sum((q[25+j]*(4*j*chi).cos() for j in range(12)),arb(0))
        ub=sum((q[k]*(-1)**k for k in range(1,13)),arb(0))
        vb=sum((q[25+j]*(-1)**j for j in range(12)),arb(0))
        rb=arb(float(log_R4)).exp()
        scale=2*rb*(-ub).exp()*(2*vb).cosh().sqrt()
        ap=scale*(u+v).exp();bm=scale*(u-v).exp()
        A=ap*chi.cos();B=bm*chi.sin()
        C=scale*(u+w).exp()/2
        LF=(A*A+B*B).sqrt();r=A*B/LF
        logN=sum((m[k-1]*(4*k*chi).cos() for k in range(1,13)),arb(0))
        logNb=sum((m[k-1]*(-1)**k for k in range(1,13)),arb(0))
        nu=(logN-logNb).exp()
        beta=(4*chi).sin()*sum((m[12+j]*(4*j*chi).cos() for j in range(12)),arb(0))
        f_normal=-beta/ logN.exp()
        X=1/(4*C*C)+3/(ap*ap)+3/(bm*bm)-f_normal*f_normal
        L=1+X**3
        sig=-arb(1)/2+rho/arb.pi()-(2*rho).sin()/(2*arb.pi())
        lam=1-4*sig*sig
        matched=(arb(2)/3)*arb.pi()**2*LF**5*lam*C*r/(nu*rb)
        weighted=matched*L
        return dict(rho='pi*'+rho_fraction,X_eta=X.str(45),L_eta=L.str(45),
            E_Lambda_only_per_kappa1=matched.str(45),
            E_event_weighted_per_kappa1=weighted.str(45),
            arithmetic_relative_accuracy_bits=int(weighted.rel_accuracy_bits()),
            classification='CERTIFIED_FIXED_INPUT_ARITHMETIC__FULL_AE4_MATCHING_UNEVALUATED')

def run(rep,cache,states,out):
    if out.exists():
        raise FileExistsError('new output directory required')
    out.mkdir(parents=True)
    representation=json.loads(rep.read_text())
    attachment=rank16_connection_attachment(representation['bundle']['multiplets'])
    with np.load(cache,allow_pickle=False) as z:
        fields={k:np.array(z[k]) for k in z.files}
    with np.load(states,allow_pickle=False) as z:
        data={k:np.array(z[k]) for k in z.files}
    weighted=matched_local_electric_density(fields,attachment)
    source_coord=weighted.pop('source_coordinate')
    np.savez(out/'attachment_and_weighted_density.npz',
        **weighted,T=attachment['T'],Y=attachment['Y'],Q=attachment['Q'],
        jmath=attachment['jmath'],rho=fields['rho'],proper_times=fields['proper_times'])
    balls=[dict(history_node=i,**exact_input_ball(data['states'][i],data['log_R4'][i],fraction))
           for i in (0,47) for fraction in ('1/4','1/2')]
    e=weighted['E_b_event_weighted_per_kappa1'];plain=weighted['E_b_Lambda_only_per_kappa1']
    result=dict(
        classification='EXECUTED_INHERITED_PREDECESSOR_CONNECTION_AND_POINTWISE_LOCAL_ELECTRIC_COEFFICIENT__NOT_COMPLETE_AE4_OR_MUON_ANOMALY',
        source_revision='524ed90689bd5923c249bba2e699abf627e703cd',
        exact_trace_data=attachment['exact_traces'],
        K_Q_over_K_component_exact=str(attachment['K_Q_over_K_component']),
        generator_equation='jmath(e_a)=-2i T_a; W_hat=2 omega; [e_a,e_b]=2 eps_abc e_c',
        normalization_equation='K_trace=K_component/8; K_Q=(16/3)*K_trace=(2/3)*K_component',
        source_coordinate=source_coord,
        representation_labels=attachment['labels'],exact_Q_diagonal=attachment['exact_Q_diagonal'],
        previously_unresolved_predecessor_index_resolved=True,
        current_native_source_domain_lift_materialized=False,
        weight_equation='W=Lambda*(1+X_eta^3); actual X_eta from retained f=chi cap fields, not minimum or frozen radius',
        sampled_L_eta_range=[float(weighted['L_eta'].min()),float(weighted['L_eta'].max())],
        sampled_L_eta_range_is_continuum_certificate=False,
        E_Lambda_only_boundary_first_last=[float(plain[0,-1]),float(plain[-1,-1])],
        E_event_weighted_boundary_first_last=[float(e[0,-1]),float(e[-1,-1])],
        fixed_input_Arb_values=balls,history_nodes=e.shape[0],radial_nodes=e.shape[1],
        full_AE4_induced_matching_remainder=None,
        new_kappa1_or_Wilson_value_chosen=False,
        source_inputs=dict(representation_sha256=sha(rep),cache_sha256=sha(cache),state_bundle_sha256=sha(states)),
        native_shifted_resolvent_actions=0,physical_soft_transfer_directions=0,
        physical_a_mu=None,physical_g_mu=None,
        previous_local_contributions_refitted=False,native_added_to_selected_local=False)
    save(out/'result.json',result)
    next_operand=dict(
        name='current_domain_photon_source_jet_of_P_strat',
        needed_projection='only the eight retained Q sources and their generated profiles, with the connected complement; not entire vertex reconstruction',
        equation='Xi_A=delta_beta_A D_strat; P_A=D0^dagger Xi_A+Xi_A^dagger D0 plus owned adjoint/domain jets; P_AB=Xi_A^dagger Xi_B+Xi_B^dagger Xi_A plus owned second-source/domain jets',
        known_local_fiber_factor='Q=T3+Y and the same-action predecessor index8 are now explicitly materialized',
        local_source_equation='Xi_A|M4=c(a_A) Q, a_A=T_b Y_A times the given profile; positive-parent/source/domain lift must be inherited from the actual D_strat realization',
        missing_implementation='The inspected AE4 owner and event-flux assembler accept or define source/sector operands; they do not supply the current nonzero stratified photon lift and its source-domain jet. The geometry Hessian and scalar domain templates are not those operands.',
        classification='UNMATERIALIZED_SAME_OWNER_SOURCE_AND_DOMAIN_REALIZATION__NOT_AN_ADJUSTABLE_EMBEDDING_INDEX',
        no_new_state_boundary_Wick_or_normalization_choice_allowed=True,
        next_calculation='materialize this source jet from the existing operator/domain, evaluate its same-owner induced matching projection, and use the completed K+sM on the supplied source with complement control')
    save(out/'next_operand.json',next_operand)
    save(out/'checkpoint.json',dict(
        checkpoint_id='BHSM_MUON_PREDECESSOR_INDEX8_POINTWISE_WEIGHT_524ED906_20261001',
        result=result,one_next_operand=next_operand,
        full_native_ledger=dict(native_bulk_heat=None,state_variation=None,contact=None,
            domain_boundary=None,completion_counterterm=None,strong_within_native=None),
        earlier_evidence_preserved=True,complete_AE4_E_Q=None,
        native_anomaly=None,physical_g_mu=None))
    save(out/'packet_hashes.json',dict(files=[dict(path=p.name,sha256=sha(p)) for p in sorted(out.iterdir())]))
    print(json.dumps({k:result[k] for k in ['K_Q_over_K_component_exact',
        'E_Lambda_only_boundary_first_last','E_event_weighted_boundary_first_last',
        'native_shifted_resolvent_actions']}))

if __name__=='__main__':
    local=HERE.parent/'BHSM_muon_parent_geometry_524ed906_20261001'
    artifact=HERE.parent/'artifacts'
    rep=HERE/'representation_input.json'
    if not rep.exists():
        rep=artifact/'muon_connection_weight_20261001/representation_input.json'
    cache=local/'run_2/local_parent_velocity_density.npz'
    states=local/'inputs.npz'
    if not cache.exists():
        cache=artifact/'muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz'
        states=artifact/'muon_parent_geometry_20261001/inputs.npz'
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--representation',type=Path,default=rep)
    p.add_argument('--parent-cache',type=Path,default=cache)
    p.add_argument('--states',type=Path,default=states)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    run(a.representation,a.parent_cache,a.states,a.output)
