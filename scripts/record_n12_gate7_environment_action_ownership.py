"""Read-only action provenance ledger. No scientific producer is imported/run."""
import argparse
import ast
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'artifacts/flagship_integration'
ACTION='scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py'
FUNCTIONS={
    ACTION:['_integrand','_boundary','_arb_action_jets','_contracted_action'],
    'scripts/derive_n12_gate7_parent_sector_jets.py':['local_sectors','calculate'],
    'scripts/bind_n12_gate7_recentered_launch_response.py':['conormal','calculate'],
    'src/bhsm/interface/aether_m4_standard_model_zeta_backreaction_v15_51.py':['standard_model_zeta_contract','standard_model_casimir_coefficient'],
    'src/bhsm/interface/aether_forward_channel_transfer.py':['restrict_two_boundary_weyl_to_dirichlet_birth_jets'],
    'src/bhsm/interface/ae2_covariant_seam_response.py':['covariant_effective_event_load','covariant_effective_event_load_jet','covariant_seam_response'],
    'src/bhsm/interface/aether_forward_common_source_incidence.py':['forward_weyl_squared_operator_and_vertices','forward_hs_scalar_operator_and_gauge_vertices','forward_oneform_ghost_matrices'],
    'src/bhsm/interface/forward_finite_endpoint_heat_force.py':['heat_regulator_value_and_force','replacement_heat_minus_zeta_force'],
    'src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py':['event_to_child_on_shell_calderon_interface'],
    'src/bhsm/interface/owner_authorized_encapsulation_interface_action.py':['owner_authorization'],
}
NOTES=[
    'src/bhsm/interface/current_semantic_normalization.py',
    'theory/n12_compact_history_endpoint_role_provenance.md',
    'theory/n12_c2_projected_adjoint_cauchy_criterion.md',
    'theory/n12_finite_history_gluing_force_provenance.md',
    'theory/n12_finite_endpoint_zero_source_force_functional.md',
    'theory/n12_c2_fixed_seed_upstream_force_owner.md',
    'theory/n12_forward_common_source_incidence.md',
    'theory/n12_ae2_covariant_seam_enclosure_z_minus_1.md',
]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest().upper()
def encoded(x):return (json.dumps(x,sort_keys=True,indent=2)+'\n').encode()


def provenance(path,names):
    text=path.read_text(encoding='utf-8');lines=text.splitlines();found={}
    for f in ast.parse(text).body:
        if isinstance(f,ast.FunctionDef) and f.name in names:
            found[f.name]=dict(start=f.lineno,end=f.end_lineno,
                text='\n'.join(lines[f.lineno-1:f.end_lineno]),
                calls=sorted({ast.unparse(n.func) for n in ast.walk(f) if isinstance(n,ast.Call)}))
    if set(found)!=set(names):raise ValueError('source function missing: '+str(path))
    return dict(SHA256=sha(path),functions=found)


def calculate():
    sources={p:provenance(ROOT/p,names) for p,names in FUNCTIONS.items()}
    sectors=json.loads((BASE/'gate7_parent_sectors_20260927/report.json').read_bytes())
    native=json.loads((BASE/'gate7_launch_response_20260927/report.json').read_bytes())
    frozen={}
    for directory in ('gate7_parent_sectors_20260927','gate7_event_conormal_20260927','gate7_launch_response_20260927'):
        folder=BASE/directory;report=json.loads((folder/'report.json').read_bytes())
        if sha(folder/'arrays.npz')!=report['arrays_SHA256']:raise ValueError('frozen array changed')
        for name in ('arrays.npz','report.json','reproduction.json'):
            p=folder/name;frozen[p.relative_to(ROOT).as_posix()]=sha(p)
    terms=[]
    for n in sectors['sector_names']:
        vacuum=n.startswith('boundary_')
        terms.append(dict(name=n,
            classification='shared/common term' if vacuum else 'parent/event geometry',
            evaluation_side='native event functional; same action law used separately on the child',
            sector=('fixed-species static conformal vacuum' if vacuum else
                    'topographic scalar/geometry' if n.startswith('eta_') else
                    'global retained Hopf inertia' if n=='hopf_inertia' else 'cap geometry'),
            independent_external_environment_action=False,
            included_in_frozen_local_derivative=True,
            active_closed_history_operator_response_evaluated_by_this_term=False))
    blocks=[]
    for name,owner,role in (
        ('M_f','aether_forward_channel_transfer.py::restrict_two_boundary_weyl_to_dirichlet_birth_jets','nonzero upstream formation response M11'),
        ('M_C2','ae2_covariant_seam_response.py::covariant_effective_event_load','transported child Calderon response'),
        ('U_R','ae2_covariant_seam_response.py::covariant_effective_event_load_jet','bundle transition, covariantly parallel, not a free source'),
        ('W_phys','ae2_covariant_seam_response.py::covariant_seam_response','retained contact block; fermion block exactly zero, other sectors not globally zero'),
        ('gauge_transverse_contact','aether_forward_common_source_incidence.py::forward_oneform_ghost_matrices','one-form/ghost pair and contact vertices'),
        ('scalar_topographic_contact','aether_forward_common_source_incidence.py::forward_hs_scalar_operator_and_gauge_vertices','HS scalar pair/contact; local eta action separately retained'),
        ('AE2_pair_contact','aether_forward_common_source_incidence.py::forward_weyl_squared_operator_and_vertices','retained Weyl pair/contact vertices and joint seam assembly')):
        blocks.append(dict(name=name,owner=owner,role=role,retained_in_declared_closed_model=True,
                           explicitly_assembled_in_native_7x73_derivative=False,zeroed_by_this_audit=False))
    return dict(status='N12_EXTERNAL_BIRTH_ARM_ABSENT_NATIVE_LOCAL_RESPONSE_NOT_FULL_JOINT_RESPONSE',
        base_commit='b3fc521e80618bf49301fa10e78f4e5b66316cdd',
        external_birth_cauchy_forcing=0,
        N12_ADDITIONAL_ENVIRONMENT_BOUNDARY_ACTION='ABSENT_BY_DECLARED_MODEL',
        absence_scope='Independent additional external/pre-E0 birth-response arm in the declared first N12 model. Not a claim that all environment/internal response vanishes.',
        separate_instantiated_N12_W_E_found=False,
        abstract_interface_action_class='owner_authorized_encapsulation_interface_action declares an unselected density class, not an instantiated N12 W_E; excluded from this frozen action',
        local_ten_term_ledger=terms,local_action_exhausted_by_ten_terms=True,
        full_outside_closed_operator_response_exhausted_by_ten_terms=False,
        retained_internal_blocks=blocks,
        distinctions=dict(native='D[Tq,P,Lq^T radial] evaluated on a local state/chart',
            on_shell='Lambda_event/child from complete variational history boundary reaction',
            quantum='D Gamma_closed[P_joint;j_birth] at fixed source, then source=0',
            replacement='D Gamma_heat[P_joint] - D Gamma_SM_zeta; static zeta already in local action'),
        promotion_conditions=dict(all_active_fixed_environment_blocks_inside_native_packet=False,
            external_birth_forcing_zero=True,no_separate_instantiated_N12_W_E=True),
        promoted_to_N12_FIXED_ENVIRONMENT_MATERIAL_RESPONSE_7x73=False,
        no_internal_response_relabelled_as_extra_Lambda_E=True,
        exact_first_remaining_identity='Bind the complete fixed-source joint history boundary reaction and its material derivative to the seven native rows on the declared launch chart, or prove its reduction to those rows. Local action exhaustiveness alone is not that identity.',
        native_packet_status=native['status'],frozen_artifact_SHA256=frozen,
        function_provenance=sources,source_SHA256={p:sha(ROOT/p) for p in NOTES}|{str(Path(__file__).relative_to(ROOT).as_posix()):sha(Path(__file__))},
        search_scope='Current N12 local action, producer call paths, zero-source semantics, complete-child reaction owner, joint AE2/Weyl and contact builders; abstract environment/interface notation inspected but not instantiated.',
        scientific_producers_run=False,derivative_7x73_recomputed=False,
        extra_environment_law_added=False,internal_response_blocks_zeroed=False,
        boundary_solve_run=False,Layer_C_rebound=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False,
        frozen_tolerances_changed=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False);report=calculate()
    (a.out/'report.json').write_bytes(encoded(report));print(report['status'])
