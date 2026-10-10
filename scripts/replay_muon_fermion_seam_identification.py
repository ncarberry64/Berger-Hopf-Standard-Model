"""Exact field-specific variational certificate, without old producer execution.

This reads the retained action expressions and incidence types. It does not
construct D_strat, evaluate heat, choose a boundary law, or replay node3.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import subprocess

import sympy as sp


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, payload):
    path.write_text(json.dumps(payload, indent=2, sort_keys=True,
                               allow_nan=False) + '\n', encoding='utf-8')


def function_record(path, name):
    """Read a concrete producer, without invoking its embedded calculations."""
    source = path.read_text(encoding='utf-8-sig')
    node = next(n for n in ast.parse(source).body
                if isinstance(n, ast.FunctionDef) and n.name == name)
    return dict(path=str(path), function=name, line=node.lineno,
                end_line=node.end_lineno, sha256=sha(path),
                execution='AST read only; not imported or executed',
                source=ast.get_source_segment(source, node)), node


def literals(node):
    """Literal return dictionary entries; no interpretation of status labels."""
    result = []
    for item in ast.walk(node):
        if isinstance(item, ast.Dict):
            row = {}
            for key, value in zip(item.keys, item.values):
                try:
                    k = ast.literal_eval(key)
                    row[k] = ast.literal_eval(value)
                except (ValueError, TypeError, SyntaxError):
                    continue
            result.append(row)
    return result


def exact_compatibility_derivatives():
    """Tensor components are independent bosonic coordinates in this proof.

    Each expression is the coefficient of the actual retained nondegenerate
    tensor/scalar dual pairing. Componentwise zero derivatives imply zero
    distributional/weak derivatives in every fermionic test direction. No
    bosonic field is eliminated, and no total induced response is inferred.
    """
    g5, QH, sigma5, P0sigma8, h, trgp, trgm = sp.symbols(
        'g5 QH sigma5 P0sigma8 h trgp trgm')
    upsilon = sp.Symbol('upsilon', positive=True)
    barw, w, barPsi, Psi, b = sp.symbols('barw w barPsi Psi b')
    multipliers = sp.symbols('Lambda85 lambda_sigma Lambda54p Lambda54m')
    inherited = [g5-QH, sigma5-P0sigma8, h-trgp, h-trgm]
    dressed = [g5/sp.sqrt(upsilon)-sp.sqrt(upsilon)*QH,
               *inherited[1:]]
    variables = [barPsi, Psi, barw, w]
    action = sum(m*c for m, c in zip(multipliers, dressed))
    jacobian = sp.Matrix(dressed).jacobian(variables)
    return dict(
        coordinates=[str(x) for x in variables],
        constraints=['C85_metric', 'C_sigma', 'C54_plus_metric',
                     'C54_minus_metric'],
        inherited=[str(x) for x in inherited],
        dressed=[str(x) for x in dressed],
        fermionic_constraint_Jacobian=[[str(x) for x in jacobian.row(i)]
                                       for i in range(jacobian.rows)],
        fermionic_constraint_rank=int(jacobian.rank()),
        D_bar_w_D_Psi_Scompat=str(sp.diff(action, barw, Psi)),
        D_b_D_bar_w_D_Psi_Scompat=str(sp.diff(action, barw, Psi, b)),
        normal_spinor_momentum_from_Scompat='0 (algebraic bosonic term)',
        scope='explicit metric/scalar compatibility density at fixed owned bosonic inputs; not complete native c45')


def retained_action_inventory(root):
    base = root/'src/bhsm/interface'
    specifications = [
        ('master_action/reduction.py', 'authoritative_action'),
        ('master_action/reduction.py', 'field_transport'),
        ('master_action/reduction.py', 'domain_and_hessian'),
        ('completion/attachment_incidence_ledger_v11_3.py', 'incidence_rows'),
        ('completion/reciprocal_attachment_action_v11_3.py', 'action_payload'),
        ('completion/attachment_boundary_core_domain_v11_3.py', 'boundary_payload'),
        ('completion/foundational_dirac_spin_glue_v14_45.py', 'foundational_action_payload'),
        ('completion/foundational_dirac_spin_glue_v14_45.py', 'zero_mode_pullback_payload'),
        ('completion/foundational_dirac_spin_glue_v14_45.py', 'global_spin_glue_payload'),
        ('aether_hybrid_yukawa_mass_semantics_v15_56.py', 'yukawa_operator_factorization'),
        ('ae31_c2_intrinsic_m4_lepton_action.py', 'action_composition_contract'),
        ('ae31_c2_intrinsic_m4_lepton_action.py', 'first_variation_and_pole_gate'),
        ('ae31_c2_chiral_green_domain.py', 'domain_provenance_reconciliation'),
        ('action_extension_global_spin_reset_ae2.py', 'action_definition'),
        ('aether_unified_m5_m4_pushforward_v15_69.py', 'unified_parent_boundary_functional'),
        ('ae4_stratified_dirac_zeta_induced_owner.py', 'microscopic_owner_contract')]
    records = []; dictionaries = {}
    for path, function in specifications:
        record, node = function_record(base/path, function)
        records.append(record)
        dictionaries[function] = literals(node)
    incidence = [x for x in dictionaries['incidence_rows'] if 'object' in x]
    expected = ['I_C=Q_H(G8)', 'I_W=id_5(g5)', 'Lambda85',
                'lambda_sigma', 'Lambda54,epsilon']
    if [x['object'] for x in incidence] != expected:
        raise ValueError('changed incidence inventory: review derivation before reuse')
    types = [x['tensor_type'] for x in incidence]
    if types != ['symmetric covariant two-tensor', 'symmetric covariant two-tensor',
                 'dual symmetric tensor/density', 'scalar multiplier',
                 'contravariant multiplier density']:
        raise ValueError('changed tensor types: no fermionic-zero certificate licensed')
    action = next(x['compatibility_action'] for x in dictionaries['authoritative_action']
                  if 'compatibility_action' in x)
    expected_action = ('int_M5 <Lambda85,g5-Q_H(G8)>'
                       '+<lambda_sigma,sigma5-P0 sigma8> '
                       '+sum_epsilon int_M4 '
                       'Lambda54,epsilon^{ab}(h_ab-iota_epsilon^*g_epsilon,ab)')
    if action != expected_action:
        raise ValueError('changed compatibility action: redo component transcription')
    reciprocal = next(x['exact_action'] for x in dictionaries['action_payload']
                      if 'exact_action' in x)
    if reciprocal != ('S_attach=int_M5 dmu5 <Lambda85,'
                       'upsilon^(-1/2) I_W-upsilon^(1/2) I_C>'):
        raise ValueError('changed reciprocal action: redo component transcription')
    return records, dict(compatibility_action=action,
                         reciprocal_action=reciprocal, incidence=incidence,
                         extracted=dictionaries)


def run(root, out, local_root):
    if out.exists():
        raise FileExistsError('use a new output directory')
    out.mkdir(parents=True)
    records, inventory = retained_action_inventory(root)
    proof = exact_compatibility_derivatives()
    previous = root/'artifacts/muon_joint_variational_attachment_20261005/run_2'
    prior = json.loads((previous/'result.json').read_text())
    # Inspect existing evidence only: no old calculations or old checks rerun.
    local_refs = [
        local_root/'Downloads/BHSM_muon_owned_connection_0b02a8dd_20261002/report.md',
        local_root/'Downloads/BHSM_muon_radial_inclusion_action_20261004/run_3/result.json',
        local_root/'Downloads/BHSM_muon_daughter_collar_delivery_final_20261003/report.md',
        local_root/'Downloads/BHSM_muon_daughter_collar_delivery_final_20261003/run_1/retained_equations.json',
        local_root/'Downloads/BHSM_muon_attachment_reconciliation_0b02a8dd_20261002/verification.json',
        local_root/'Downloads/BHSM_muon_connection_attachment_524ed906_20261002/report.md',
        local_root/'OneDrive/Documents/CODEX/outputs/bhsm_muon_20260930/action_source/report.md',
        local_root/'OneDrive/Documents/CODEX/outputs/bhsm_muon_20260930/fermion_body_20261001/report.md']
    missing_local = [str(p) for p in local_refs if not p.is_file()]
    if missing_local:
        raise FileNotFoundError(missing_local)
    refs = set(Path(r['path']) for r in records)
    refs.update(local_refs)
    refs.update([previous/'result.json', previous/'node3_joint_known_variations.npz',
                 root/'artifacts/muon_wall_input_attachment_20261005/run_1/result.json',
                 Path(__file__)])
    save(out/'retained_equations.json', records)
    save(out/'field_inventory.json', inventory)
    save(out/'exact_derivatives.json', proof)
    result = dict(
        classification='exact restricted-action variational insufficiency result; not a native operator evaluation',
        new_result='the actual metric/scalar matcher fermionic incidence Jacobian has rank0; its mixed wall/bulk derivative and same-photon derivative vanish identically. Neither it nor cap/reset transmission supplies an independent-H4 attachment.',
        known_term_c45=proof['D_bar_w_D_Psi_Scompat'],
        known_term_c45_source_jet=proof['D_b_D_bar_w_D_Psi_Scompat'],
        action_owned_native_c45=None,
        source_columns=prior['source_columns'], reused_node=prior['node'],
        reused_action_arc=prior['action_arc'], reused_branch=prior['branch'],
        Green_columns_and_time_jet='preserved without recomputation; zero compatibility derivative applies in every actual reached direction as an exact field identity',
        missing_equation='(g_plus,g_minus)=F_b(gamma5_plus Psi5_plus,gamma5_minus Psi5_minus,L_L,e_R), together with the owned joint allowed-variation/normal-output relation; its required mixed/source jets on the reached response directions suffice (first jets alone only for a justified fermion-linear identification)',
        missing_classification='not determined by the explicit examined action/compatibility equations; not recovered from the specified local handoffs. This is not an exhaustive absence theorem.',
        producer='pre-localized-mode fermionic seam identification and joint domain, compatible with AE31 independent fields and AE4 canonical direct-sum architecture',
        consumer='wall Euler mixed row E45 and reverse bulk normal output, then same-source Xi_strat and joint q=<D V,D U>',
        native_R4=None, updated_stationary_solution=None, native_heat_contact=None,
        physical_a_mu=None, physical_g_mu=None, native_uncertainty=None,
        new_parent_point_actions=0, old_checks_rerun=0, new_stationary_solves=0,
        new_native_physical_transfer_directions=0,
        error_scope='exact algebra for the explicitly transcribed compatibility density; inherited numerical arrays not recalculated or certified anew; no continuum/heat/Pauli error bound',
        frozen_local=dict(a_mu_QED_local=0.00116550200495813,
                          calibration_only_uncertainty=1.79e-13,
                          delta_a_mu_h_local_1_open=[0,3.500331e-9],
                          selected_local_open=[0.0011655039493,0.0011655109506]))
    save(out/'result.json', result)
    save(out/'input_hashes.json', [{ 'path':str(p), 'sha256':sha(p)}
                                  for p in sorted(refs)])
    head=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    branch=subprocess.check_output(['git','-C',str(root),'branch','--show-current'],text=True).strip()
    save(out/'workspace.json', dict(head=head,branch=branch,
         scientific_reference='524ed90689bd5923c249bba2e699abf627e703cd',
         worktree_status=subprocess.check_output(['git','-C',str(root),'status','--porcelain=v1'],text=True),
         intentional_change='new focused derivation/replay/tests; old operator and caches unchanged'))
    save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps({k:result[k] for k in ['classification','known_term_c45',
          'known_term_c45_source_jet','action_owned_native_c45','old_checks_rerun']},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--local-root',type=Path,default=Path('C:/Users/carbe'))
    args=parser.parse_args()
    run(args.repository.resolve(),args.output.resolve(),args.local_root.resolve())
