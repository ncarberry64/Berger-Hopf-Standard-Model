"""Actual adopted preparation weak-Gauss moment and same-background test jets."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import os
import sys

os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
ROOT = Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
WORK = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'src'), str(ROOT)]
import numpy as np
from bhsm.interface.muon_prepared_weak_gauss_dressing import (
    prepared_charge_moments, charge_test_twojet,
    physical_unit_moment_twojet, required_dressing_contractions,
)
from bhsm.interface.retained_response.finite_time_response import write_npz


def pin(path):
    return sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n', encoding='utf8')


def main(out):
    out = Path(out).resolve();out.mkdir(exist_ok=False)
    prep = ROOT/'artifacts/muon_ideal_collider_preparation_20261016/BHSM_IDEAL_COLLIDER_PREPARATION_V1.json'
    pair = ROOT/'artifacts/muon_collider_common_state_constraint_family_20261014/retained_preparation/actual_frozen_family_and_exact_pair_spin_CAR_preparation.npz'
    receipt = pair.parent/'result.json'
    native = ROOT/'artifacts/muon_stationary_native_reference_load_20261019/run_5/native_reference_load.npz'
    exact = {
        prep: 'dcc4ad850ea38dcd405637d24b306efe8789ab08e144f559d7cc294cd72e8f0f',
        pair: '20db0b3b1a5cb09be1979b0fb24027bbb70f713d4001bd8c50e9807137a136d3',
        receipt: '4eb26ad104914e6d78cd686157aecbad83e8bb376e642eb514430377d35fe369',
        native: '1663a7d19350412cae236345974e9c48f07ace8f54b29752bd5e2956a8221753',
    }
    for path, expected in exact.items():
        if pin(path) != expected:
            raise ValueError('immutable actual input identity differs: '+str(path))
    owners = [ROOT/'src/bhsm/interface'/name for name in (
        'muon_prepared_weak_gauss_dressing.py',
        'muon_primal_electromagnetic_source.py',
        'muon_native_dirac_hamiltonian.py',
        'muon_native_product_factor_graph.py',
        'muon_parent_maxwell_full_weak.py',
        'muon_stationary_native_reference_load.py',
    )]
    paths = list(exact)+owners+[ROOT/'audits/bhsm_collider_incoming_field_current.py',
        ROOT/'AGENTS.md', Path(__file__)]
    input_hashes = {str(p): pin(p) for p in paths}
    (out/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
    (out/'executed_owner.py').write_bytes(owners[0].read_bytes())
    dump(out/'BEFORE.json', dict(input_sha256=input_hashes,
        equation='D_i Pi^i+j_pair+j_other=0, tested against lambda=X3*s(H)',
        NEXT_OPERAND='Evaluate charge/dipole target and its same-background gauge-covariant test coefficients; no physical packet/flux choice'))
    preparation = json.loads(prep.read_text(encoding='utf8'))
    with np.load(pair, allow_pickle=False) as data:
        rho = data['pair_Fock_density16'].copy()
    with np.load(native, allow_pickle=False) as data:
        x, theta, first, second = (data[k].copy() for k in (
            'input_iterate151', 'actual_theta', 'actual_theta_gradient', 'actual_theta_hessian'))
    moments = prepared_charge_moments(preparation, rho)
    test = charge_test_twojet(theta, first, second)
    units = physical_unit_moment_twojet(moments, x[150])
    consumed = required_dressing_contractions(moments)
    arrays = dict(input_iterate151=x, actual_theta22=theta,
        actual_theta_gradient22x151=first, actual_theta_hessian22x151x151=second)
    for name, value in moments.items():
        if isinstance(value, np.ndarray):
            arrays[name] = value
    for name, value in test.items():
        if isinstance(value, dict):
            arrays.update({name+'_'+key: val for key, val in value.items()})
        elif isinstance(value, np.ndarray):
            arrays[name] = value
    for name, value in units.items():
        if isinstance(value, dict):
            arrays.update({name+'_'+key: val for key, val in value.items()})
    arrays['physical_required_K0_K1_fm'] = np.array([consumed['required_K0'], consumed['required_K1_fm']])
    arrays['provisional_chart_required_K1'] = units['required_dipole_chart']['value'].copy()
    # Substitution checks the newly evaluated mandatory source contribution
    # in its contracted Gauss equation, not the unevaluated physical lhs.
    arrays['contracted_mean_Gauss_source_substitution_row'] = np.array([consumed['exact_mean_reconstructed_Gauss_row_fm']])
    write_npz(out/'application.npz', arrays)
    scalar_moments = {k: v for k, v in moments.items() if not isinstance(v, np.ndarray)}
    coefficient_report = {k: v for k, v in test.items() if not isinstance(v, (dict, np.ndarray))}
    coefficient_report.update(charge_test4=test['charge_test']['value'].tolist(),
        proper_covariant_charge_derivative3x4=test['proper_spatial_covariant_charge_derivative']['value'].reshape(3, 4).tolist(),
        proper_covariant_charge_derivative_max=float(np.max(abs(test['proper_spatial_covariant_charge_derivative']['value']))),
        Ds151_max=float(np.max(abs(test['charge_test']['gradient']))),
        D2s151_max=float(np.max(abs(test['charge_test']['hessian']))),
        D_covariant_test151_max=float(np.max(abs(test['proper_spatial_covariant_charge_derivative']['gradient']))),
        D2_covariant_test151_max=float(np.max(abs(test['proper_spatial_covariant_charge_derivative']['hessian']))),
        induced_lapse=float(theta[1]), radius=float(theta[0]))
    report = dict(classification='EXECUTED_ADOPTED_NONZERO_WEAK_GAUSS_DRESSING_MOMENT_AND_SAME_BACKGROUND_COVARIANT_TEST_TWOJET',
        moment_evaluation=scalar_moments, original_coefficient_checks=coefficient_report,
        consumed_Gauss_contraction=consumed,
        physical_unit_scope=dict(log_unit_initializer=float(x[150]),
            unit_initializer_GeV=float(np.exp(x[150])),
            required_dipole_chart_at_initializer=float(units['required_dipole_chart']['value'][0]),
            exact_total_derivative=units['exact_total_derivative'],
            physical_scale_equation_solved=False,initializer_promoted=False),
        derivative_scope='Saved same151 field/Higgs/geometry/unit pullback two-jet; ordinary rate, physical incidence, endpoint, state and domain variations outside this finite chart remain explicit.',
        missing_coordinate_terms='D_i(X3*s)=(e_i X3)*s+X3*(E_i s+[A_i,s])/R. X3, its frame gradients and normal extension on the actual collider/Cauchy incidence remain to be evaluated; only E_i s=0 on this saved homogeneous angular component.',
        inherited_state_scope='All inherited/reference/other source and boundary contractions remain in J_other, Flux and Bulk. Their individual values and connected correlations are not assigned zero or reconstructed from this mandatory moment.',
        local_native_accounting='No local Maxwell/Higgs functional removed or added; no saved partial classical flux is promoted to the complete interacting flux.',
        original_equation_residual_scope='Charge reconstruction and lapse cancellation are finite operator coefficient identities. Contracted source substitution is algebraic only; complete physical Gauss residual and achieved packet moments are unevaluated.',
        continuum_or_dressing_error_bound=False,physical_admission=False,physical_guard=2e-10,
        physical_parent_d_in40_selected=False,physical_collider_pair_conversion_computed=False,
        NEXT_OPERAND='Apply the actual collider-to-Cauchy X3/frame/normal incidence to these covariant tests; solve the nonzero required flux-minus-bulk/other-source contraction with the same dressed packet constraints and inherited reference, then supply operator/mode-amplitude data to parentSigma/incoming40.')
    dump(out/'result.json', dict(input_sha256=input_hashes,
        arrays=dict(path='application.npz', sha256=pin(out/'application.npz')), report=report))
    print(json.dumps(report, sort_keys=True, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    arguments = parser.parse_args();main(arguments.output)
