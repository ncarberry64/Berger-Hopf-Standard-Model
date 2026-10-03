"""Replay the scoped forcing derivation and inspect preserved operand identities.

No producer, native heat operator, physical response or old test is executed.
This is a resumable blocked-step record, not a numerical muon calculation.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path

import numpy as np
import sympy as s

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def lifting_identities():
    """Exact residual identities for arbitrary non-Hermitian retarded blocks.

Dimensions remain symbolic. The eight source columns are the supplied photon
labels, not a claim that the trace or zero-trace space is eight dimensional.
"""
    n, m = s.symbols('n m', integer=True, positive=True)
    K = s.MatrixSymbol('K_ZZ', n, n)
    C = s.MatrixSymbol('K_gammaZ', m, n)
    F = s.MatrixSymbol('f_Z', n, 8)
    G = s.MatrixSymbol('f_gamma', m, 8)
    z = s.MatrixSymbol('z', n, 8)
    r = s.MatrixSymbol('r', n, 8)
    T = s.MatrixSymbol('T', n, m)
    p = s.MatrixSymbol('p', m, 1)
    w = s.MatrixSymbol('w', n, 1)
    residual = F - K*z
    adjoint_residual = s.Adjoint(K)*w - s.Adjoint(C)*p
    relations = {
        'trial_lifting_solve_residual': (F+K*r)-K*(z+r)-residual,
        'trial_lifting_return': (G+C*r)-C*(z+r)-(G-C*z),
        'test_lifting_return_minus_solver_residual':
            G+s.Adjoint(T)*F-(C+s.Adjoint(T)*K)*z-(G-C*z)-s.Adjoint(T)*residual,
        'output_adjoint_return_minus_residuals':
            s.Adjoint(p)*G-s.Adjoint(w)*F-s.Adjoint(p)*(G-C*z)
            +s.Adjoint(adjoint_residual)*z+s.Adjoint(w)*residual,
    }
    zeros = {}
    for name, expression in relations.items():
        value = s.expand(expression).doit()
        zeros[name] = bool(value == s.ZeroMatrix(*value.shape))
        if not zeros[name]:
            raise AssertionError((name, value))
    return dict(exact_residual_identities=zeros,
        assumptions='Compatible same-domain weak blocks; Z_trial/Z_test represent ker B5. No symmetry, positivity, inverse or physical-state selection.',
        distinct_test_trial='Use Z_test^dagger K^R Z_trial for Petrov spaces; equal-coordinate notation is only presentation.',
        singular_case='f_Z in ran K_ZZ; return unique iff K_gammaZ ker K_ZZ=0; otherwise retain its affine Calderon relation.',
        adjoint='(K_ZZ)^dagger w_p=(K_gammaZ)^dagger p; p^dagger j=p^dagger f_gamma-w_p^dagger f_Z. This is a mathematical dual, not an advanced physical propagator.',
        differentiated_lifting='Retain derivatives of lifts, source, pairing, trace/basis and coupled domain. Identities do not set their jets to zero.')


def run(manifest, output):
    refs = json.loads(manifest.read_text())
    root = HERE.parent if (HERE.parent/'src').is_dir() else Path(refs['repository'])
    if output.exists():
        raise FileExistsError('Use a new output directory')
    equations = []
    arrays = []
    for row in refs['inputs']:
        path = root/row['repository_path'] if 'repository_path' in row else Path(row['local_path'])
        if sha(path) != row['sha256']:
            raise ValueError('Changed recorded input: ' + str(path))
        if row.get('functions'):
            text = path.read_text(encoding='utf-8-sig')
            lines = text.splitlines()
            nodes = {node.name:node for node in ast.walk(ast.parse(text)) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
            for name in row['functions']:
                node = nodes[name]
                equations.append(dict(path=str(path),function=name,line=node.lineno,end_line=node.end_lineno,
                    sha256=row['sha256'],source='\n'.join(lines[node.lineno-1:node.end_lineno])))
        if path.suffix == '.npz':
            with np.load(path) as cache:
                arrays.append(dict(path=str(path),sha256=row['sha256'],arrays={k:list(cache[k].shape) for k in cache.files}))
    algebra = lifting_identities()
    output.mkdir(parents=True)
    save(output/'source_equations.json', equations)
    save(output/'supplied_array_inventory.json', arrays)
    save(output/'lifting_and_adjoint_identities.json', algebra)
    missing = dict(name='owned stratified Dirac heat action restricted to the connected parent source image',
        first_contact_coefficient='c_D,ZA_contact=-Tr(Q_strat A_ZA), Q_strat=(1/2) A_strat^-1 exp(-ell_star^2 A_strat), A_strat=M_strat^-1 K_strat on the owned quotient',
        paired_coefficient='c_D,ZA_pair=-Tr(DQ_strat[A_A] A_Z)',
        generalized_mixed_jet='A_ZA=M_strat^-1(K_ZA-M_ZA A_strat-M_Z A_A-M_A A_Z)',
        compressed_action_warning='Pi5 Q(A_strat) iota5 is not Q(Pi5 A_strat iota5); retain cross-stratum/interface and connected tails. A supplied condensed pencil requires its matching remainder.',
        input_space='Common-domain parent spin/internal/family source-connected space, on the inherited prefix and interfaces; full weak/angular outputs retained.',
        output_space='Only the contact/pair scalar for an owned zero-trace test or the necessary output-adjoint direction; a complete kernel or matrix is unnecessary.',
        producer='M5 common-A Dirac weak pencil and its source jets, with reset/domain/quotient/connected-complement and native ell_star binding; equivalently its certified contracted heat/shifted-resolvent actions.',
        consumer='f_Z,A=q5_AE4(v_Z,a_L,A), then K_ZZ^R z_A=f_Z,A and the source-corrected affine traction return.',
        value=None,classification='uncomputed prescribed operator action; common-A and effective family attachment are resolved',
        no_circular_extension_prerequisite=True,
        source_lifting='An inherited-admissible computational lifting a_L is sufficient for forming f_Z; the response correction is lifting-independent as shown.',
        missing_graph_representation='No numerical B5, zero-trace directions or parent output adjoint are supplied by solve_retarded_event_kkt; it consumes blocks. The old 16 child columns and 7x73 geometric directions are not those spaces.',
        inspected_scope='The named saved arrays and evaluator/solver producers, not an exhaustive absence claim over the scientific record.')
    save(output/'missing_action.json', missing)
    ledger = dict(primitive_mechanical='evaluated rows retained, not rerun; a subset of the AE4 functional',
        conditional_Higgs='evaluated conditional row retained, not a complete saddle/return',
        induced_Dirac_heat=None,gauge_constraint_and_BRST_completion=None,
        induced_contact=None,pairing_and_domain_jets=None,native_length_jets=None,
        relative_zeta_eta_completion=None,causal_zero_trace_response=None,
        strong_within_native=None,
        no_zero_substitution=True,no_local_double_counting=True)
    save(output/'contribution_ledger.json',ledger)
    result = dict(checkpoint='BHSM_MUON_FORCING_LIFTING_ADJOINT_AND_PARENT_HEAT_ACTION_20261002',
        start_HEAD=refs['start_HEAD'],scientific_reference=refs['scientific_reference'],
        scientific_result='Source/lifting correction and output-adjoint reduction established for compatible nonsymmetric causal weak blocks; concrete parent heat action remains uncomputed.',
        target_reached=False,new_physical_native_contractions=0,f_Z_A=None,z_A=None,j_ext_A=None,
        physical_a_mu=None,physical_g_mu=None,one_next_missing_action=missing,
        exact_algebra=algebra,ledger=ledger,
        executed=dict(input_hashes=len(refs['inputs']),new_exact_symbolic_residuals=4,old_production_calculations=0,
            preserved_four_checks_rerun=False,new_operator_numerical_evaluations=0,native_E1_evaluations=0,physical_transfer_directions=0),
        error_scope='Exact algebra conditional on the stated common-domain/solvability hypotheses. No new numerical operator, continuum error enclosure or native uncertainty.',
        frozen_local=json.loads((root/'artifacts/muon_connection_attachment_20261002/frozen_local.json').read_text()),
        native_ledger=json.loads((root/'artifacts/muon_connection_attachment_20261002/native_ledger.json').read_text()))
    save(output/'result.json',result)
    save(output/'checkpoint.json',dict(checkpoint_id=result['checkpoint'],start_HEAD=refs['start_HEAD'],
        result='result.json',one_next_operand=missing,actual_native_contractions=0,target_reached=False))
    save(output/'replay_receipt.json',dict(script_sha256=sha(Path(__file__)),manifest_sha256=sha(manifest),
        executed=result['executed'],files=[dict(path=p.name,sha256=sha(p)) for p in sorted(output.iterdir())]))
    print(json.dumps(dict(output=str(output),target_reached=False,exact_symbolic_residuals=4,induced_contractions=0)))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    default=HERE/'input_refs.json'
    if not default.exists():default=HERE.parent/'artifacts/muon_zero_trace_forcing_20261002/input_refs.json'
    parser.add_argument('--inputs',type=Path,default=default)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    run(args.inputs,args.output)
