"""Evaluate actual local b-source/form actions, retaining the n2 complement."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys
import numpy as np
from flint import arb,ctx
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'src'))
try:
    import muon_local_source_jet as implementation
except ModuleNotFoundError:
    from bhsm.interface import muon_local_source_jet as implementation

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,value):p.write_bytes((json.dumps(value,indent=2,sort_keys=True)+'\n').encode())
def arrays(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}

def integrated_certificates(frame):
    with ctx.workprec(192):
        x=[arb(float(v)) for v in frame['log_radius']]
        h=[arb(float(v)) for v in frame['proper_durations']]
        c=1/(2*arb.pi()**2).sqrt()
        sums=[]
        for power in (2,4):
            k=arb(3)*power/2
            result=arb(0)
            for lo,hi,dt in zip(x[:-1],x[1:],h):
                dx=hi-lo
                exprel=arb(1) if dx.is_zero() else (-k*dx).expm1()/(-k*dx)
                result+=dt*c**power*(-k*lo).exp()*exprel
            sums.append(result)
        return dict(I_f2=sums[0].str(45),I_f4=sums[1].str(45),
            E0_contact_sum_trace=(64*sums[0]).str(45),
            generated_contact_sum_trace=(512*sums[1]).str(45),
            generated_n2_complement_contact_sum_trace=(arb(1024)/3*sums[1]).str(45),
            classification='CERTIFIED_FIXED_INPUT_ARITHMETIC_FOR_THE_DECLARED_AFFINE_LOGR_CHILD_TEST_PROFILES; not physical input/interpolation or native-theory error')

def run(inp,out,reuse=None,validated_module=None):
    if out.exists():raise FileExistsError('Use a new output directory; preserved stages are resumable evidence.')
    out.mkdir(parents=True)
    data=arrays(inp)
    parts={p:{k.split('__',1)[1]:v for k,v in data.items() if k.startswith(p+'__')}
           for p in ('angular','body','frame','mixed')}
    save(out/'stage_receipt.json',dict(input_sha256=sha(inp),
        code_sha256=sha(Path(implementation.__file__)),stage='inputs_loaded'))
    if reuse:
        if validated_module is None:raise ValueError('Cached code identity required.')
        old= json.loads((reuse/'result.json').read_text())
        assert old['source_inputs_sha256']==sha(inp)
        assert old['module_sha256']==sha(validated_module)
        def scope(p):
            return p.read_text().split('\ndef missing_native_lift():',1)[0]
        assert scope(validated_module)==scope(Path(implementation.__file__)), 'Actual source/form implementation changed.'
        hashes=json.loads((reuse/'output_hashes.json').read_text())
        identities={f['path']:f['sha256'] for f in hashes['files']}
        for name in ['local_source_actions.npz','local_contact_forms.npz','evaluated_child_forms.npz']:
            assert sha(reuse/name)==identities[name]
            shutil.copyfile(reuse/name,out/name)
        s=arrays(out/'local_source_actions.npz');contact=arrays(out/'local_contact_forms.npz');f=arrays(out/'evaluated_child_forms.npz')
        certificates=old['fixed_input_Arb']
    else:
        s=implementation.full_local_source(parts['angular'],data['gamma'])
        np.savez_compressed(out/'local_source_actions.npz',**s)
        contact=implementation.contact_forms(s)
        np.savez_compressed(out/'local_contact_forms.npz',**contact)
        f=implementation.evaluated_child_forms(s,contact,parts['body'],parts['frame'],parts['mixed'])
        np.savez_compressed(out/'evaluated_child_forms.npz',**f)
        certificates=integrated_certificates(parts['frame'])
    P=parts['mixed']['current_generated_projector_canonical20']
    n0=np.zeros((20,20));n0[[0,1,10,11],[0,1,10,11]]=1
    n1plus=P-n0
    total=np.einsum('aaij->ij',contact['contact_full'])
    tail=np.einsum('aaij->ij',contact['contact_connected_complement'])
    generated=s['Xi_complete']@P
    ret=s['retained_output_indices']
    complement=generated.copy();complement[:,ret]=0
    b_source_match=float(np.linalg.norm(s['V_retained']-parts['mixed']['canonical_B_H_photon_source_unit']))
    checks=dict(saved_B_H_source_match_residual=b_source_match,
        source_gamma0_identification_residual=float(np.linalg.norm(s['gamma0_output']@s['Xi_complete']-s['V_complete'])),
        charge_conjugation_residual=float(s['charge_conjugation_residual']),
        full_contact_addition_theorem_residual=float(np.linalg.norm(total-16*np.eye(20))),
        n2_contact_sumrule_residual=float(np.linalg.norm(P@tail@P-(32/3)*n1plus)),
        current_generated_n2_action_frobenius_norm=float(np.linalg.norm(complement)),
        integrated_first_form_Hermitian_residual=float(np.linalg.norm(f['child_q_A_integrated']-f['child_q_A_integrated'].conj().transpose(0,2,1))),
        mass_first_jet_coefficient_residual=float(np.linalg.norm(f['local_mass_first_jet_coefficient'])),
        child_mesh_source_trace_max_abs=float(np.abs(f['child_mesh_source_trace_residual']).max()),
        first_form_max_abs=float(np.abs(f['child_q_A_integrated']).max()),
        generated_contact_sum_trace=float(np.trace(np.einsum('aaij->ij',f['child_q_AB_integrated'])[-32:,-32:]).real),
        generated_n2_contact_sum_trace=float(np.trace(np.einsum('aaij->ij',f['child_q_AB_connected_complement'])[-32:,-32:]).real))
    result=dict(classification='ACTUAL_M4_b_SOURCE_AND_COMMON_CHILD_FORM_ACTIONS_WITH_CONNECTED_n2_CONTACT; NOT_COMPLETE_NATIVE_OPERATOR_OR_PHYSICAL_MUON_STATE',
        coordinate='b',coordinate_equations=['beta=T_b*b','A_Q=sqrt(2)*beta','f_R=T_b/R4=(2*pi^2*R4^3)^(-1/2)'],
        action_index_2_over_3_inserted_in_vertex=False,
        source_equation='Xi_b^(4)=f_R*c_src(Y_A)Q; gamma0_LR Xi_b=f_R Q diag(-J_A,+J_A)',
        physical_muon_charge=-1,conjugate_charge=1,
        input_spatial_levels=[0,1],one_source_output_spatial_levels=[0,1,2],
        n_ge_3_one_action_tail='exactly absent by Wigner product triangle; no claim for heat/resolvent or repeated source actions',
        test_columns='[E0,f_R V_0 E0,...,f_R V_7 E0]; E0 is the saved canonical n0 frame, not a physical muon LSZ state',
        history_interpolation='existing affine logR on 47 saved proper-clock segments; not a refined history or continuum-error certificate',
        local_Xi_AB=0,local_Xi_AB_zero_provenance='affine direct connection coordinates at fixed background and fixed source lifts, not a claim about eliminated native/source-domain contacts',
        common_first_order_child_domain=True,
        parent_common_domain_established=False,parent_strong_domain_motion_assumed=False,
        local_pairing_M_source_jets='zero for fixed geometric child pairing/test columns under direct b differentiation only; native M jets remain unevaluated',
        checks=checks,fixed_input_Arb=certificates,
        evaluated_arrays_reused=bool(reuse),
        reuse_reason='Only reset-equation metadata changed; identical source/form implementation scope and original output hashes verified.' if reuse else None,
        native_parent_interface_residual=None,native_reset_source_residual=None,
        full_AE4_induced_matching_remainder=None,native_E1_evaluations=0,native_shifted_resolvent_applications=0,
        physical_soft_transfer_directions=0,physical_a_mu=None,physical_g_mu=None,
        frozen_local_values_changed=False,native_added_to_selected_local=False,
        source_inputs_sha256=sha(inp),module_sha256=sha(Path(implementation.__file__)))
    save(out/'result.json',result)
    missing=implementation.missing_native_lift()
    save(out/'missing_lift.json',missing)
    save(out/'checkpoint.json',dict(checkpoint_id='BHSM_MUON_LOCAL_SOURCE_COMPLETE_CONTACT_524ED906_20261002',
        result=result,one_next_operand=missing,
        native_ledger={k:None for k in ['native_bulk_heat','state_variation','contact','domain_boundary','completion_counterterm','strong_within_native']},
        primitive_and_induced_same_owner_not_added_twice=True))
    save(out/'stage_receipt.json',dict(input_sha256=sha(inp),code_sha256=sha(Path(implementation.__file__)),
        stage='local_source_contact_and_child_form_actions_saved; native_E1_not_invoked_without_the_parent_lift'))
    save(out/'output_hashes.json',dict(files=[dict(path=p.name,sha256=sha(p)) for p in sorted(out.iterdir())]))
    print(json.dumps(checks))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    default=HERE/'source_inputs.npz'
    if not default.exists():default=HERE.parent/'artifacts/muon_source_jet_20261002/source_inputs.npz'
    p.add_argument('--inputs',type=Path,default=default)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--reuse-actions-from',type=Path)
    p.add_argument('--validated-module',type=Path)
    a=p.parse_args();run(a.inputs,a.output,a.reuse_actions_from,a.validated_module)
