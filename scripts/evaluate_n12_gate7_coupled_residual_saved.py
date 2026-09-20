"""Bound the recoverable coupled normalization residuals from saved jets.

The complete projected action residual fails closed when its common-parameter
action/normalization/HS remainder is missing. No action graph is evaluated.
"""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from bhsm.interface import shared_parameter_residual as shared


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2)+'\n').encode()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def bound(value):
    return dict(upper_exact=str(value.upper().fmpq()), upper=float(value.upper()))


def read_matrix(saved, name, *, center=False):
    mid = saved[name+'_mid_q']
    rad = saved[name+'_rad_q']
    values = [arb(str(m))+arb(0, arb(str(r))) for m, r in zip(mid.flat, rad.flat, strict=True)]
    # A predictor is an arbitrary exact polynomial, not an enclosure. Choosing
    # its exact centers does not assume the point uncertainty is zero: the
    # full equation residual must enclose the error relative to this predictor.
    if center:
        values = [v.mid() for v in values]
    shape = mid.shape if mid.ndim == 2 else (mid.size, 1)
    return arb_mat(*shape, values)


def model(constant, derivatives, rows=61):
    if constant.nrows() < rows or constant.ncols() != 1 or derivatives.nrows() < rows:
        raise ValueError('complete affine predictor operands required')
    return arb_mat(rows, derivatives.ncols()+1,
                   [constant[i, 0] if j == 0 else derivatives[i, j-1]
                    for i in range(rows) for j in range(derivatives.ncols()+1)])


def normalization_residuals(psi, hard, psi_u, hard_u, groups):
    dot = shared.affine_dot_polynomial
    norm = dot(psi, psi)/2
    norm[0, 0] -= arb('0.5')
    coefficients = dict(eigenline_normalization=norm,
        response_normalization=dot(psi, hard),
        axis_line_normalization=dot(psi, psi_u),
        axis_response_normalization=dot(psi, hard_u)+dot(psi_u, hard))
    result = {}
    for name, polynomial in coefficients.items():
        result[name] = dict(
            complete_polynomial_support=bound(shared.quadratic_support(polynomial, groups)),
            constant_absolute=bound(abs(polynomial[0, 0])),
            linear_support=bound(shared.linear_support(
                [polynomial[0, i]+polynomial[i, 0] for i in range(1, polynomial.nrows())], groups)),
            coefficient_SHA256=hashlib.sha256(encoded([
                [str(v.mid().fmpq()), str(v.rad().fmpq())] for v in polynomial.entries()])).hexdigest().upper())
    return result


def evaluate(root):
    prior_path = ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_JOINT_INPUT_COLUMN_SUFFICIENCY_20260913.json'
    prior = json.loads(prior_path.read_bytes())
    if sha(prior_path) != 'F9BBF59B0E695DC96228C4ADAE2CB0CEFA2FB93D8B05B033703B3FF8B5075CA8':
        raise ValueError('reviewed baseline changed')
    sys.path[:0] = [str(root/'scripts'), str(root/'src')]
    import diagnose_n12_gate7_directed_trial_hs_column as base
    p = base.p
    residual = p.geometry.residual
    targets = [(p.values, 'sha'), (residual.center, '_sha'),
               (residual.foundation.coordinate.center, '_sha')]
    results, sources = {}, {}
    with base.cache.cache_hashes(targets):
        for name, pair, eigenpath, dimension in (
            ('midpoint', 'bhsm_midpoint_center_mean_value_right_pair_20260913',
             '.coupled_midpoint_eigenpair_pilot_work/interval_013', 249),
            ('endpoint', 'bhsm_endpoint_trial_mean_value_bootstrap_right_pair_20260913',
             '.affine_eigenpair_pilot_work/endpoint_014', 75)):
            directory = root/'tmp'/pair/'value'
            record_path, data = directory/'first/record.json', directory/'first/column.npz'
            receipt_path = directory/'reproduction.json'
            record = json.loads(record_path.read_bytes())
            receipt = json.loads(receipt_path.read_bytes())
            for filename in ('record.json', 'column.npz'):
                first = directory/'first'/filename
                digest = sha(first)
                if (digest != prior['paired_source_hashes'][first.relative_to(root).as_posix()]
                        or digest != sha(directory/'repeat'/filename)
                        or digest != receipt['files_SHA256'][filename]):
                    raise ValueError('paired baseline evidence changed')
                sources[first.relative_to(root).as_posix()] = digest
            if not all(receipt.get(k) is True for k in ('fresh_process', 'independent_recomputation', 'byte_identical')):
                raise ValueError('independent physical source pair required')
            if sha(receipt_path) != prior['paired_source_hashes'][receipt_path.relative_to(root).as_posix()]:
                raise ValueError('source receipt changed')
            sources[receipt_path.relative_to(root).as_posix()] = sha(receipt_path)
            p.verify_sources(record['binding'])
            eigendata = root/'artifacts/flagship_integration'/eigenpath/'eigenpair.npz'
            if record['binding']['files'].get(eigendata.relative_to(root).as_posix()) != sha(eigendata):
                raise ValueError('eigenpair predictor outside original binding')
            sources[eigendata.relative_to(root).as_posix()] = sha(eigendata)
            groups = ([(g['start'], g['stop'], g['norm']) for g in prior['groups']]
                      if name == 'midpoint' else [(0, 1, 'interval'), (1, 75, 'euclidean')])
            shared.validate_groups(groups, dimension)
            with np.load(data, allow_pickle=False) as saved, np.load(eigendata, allow_pickle=False) as eigen:
                # The eigenpair center may differ slightly from the point-jet
                # solve center. It is only a proposal; no tangent residual is
                # set to zero or inferred from numerical smallness.
                centers = [read_matrix(saved, f'point_center_{i}', center=True) for i in range(7)]
                if [x.ncols() for x in centers] != [1, 1, 1, dimension, dimension, dimension, dimension]:
                    raise ValueError('complete original seven-solve point model required')
                psi = model(read_matrix(eigen, 'eigenpair_center', center=True), centers[3])
                hard = model(centers[0], centers[4])
                psi_u = model(centers[1], centers[5])
                hard_u = model(centers[2], centers[6])
                norms = normalization_residuals(psi, hard, psi_u, hard_u, groups)
                array_names = sorted(k[:-6] for k in saved.files if k.endswith('_mid_q'))
            proofs = [item for batch in record['report']['solve_proofs'] for item in batch]
            q = max(Fraction(item['weighted_contraction_upper_rational']) for item in proofs)
            if not 0 <= q < 1:
                raise ValueError('original same-family bordered contraction required')
            results[name] = dict(parameters=dimension, groups=groups,
                all_seven_saved_point_solves_reused=True,
                exact_predictor_not_claimed_as_solution=True,
                shared_parameters_retained_in_normalization_products=True,
                normalization_residuals=norms,
                original_bordered_contraction_upper_exact=str(q),
                original_bordered_contraction_upper=float(q),
                original_bordered_inverse_amplification_upper=bound(1/(1-arb(str(q)))),
                stacked_graph_contraction_established=False,
                saved_arrays=array_names,
                saved_residuals_are_coordinate_balls=True,
                common_parameter_action_residual_available=False)
            p.verify_sources(record['binding'])
    # Retain the baseline's entire conservative vector budget. Do not subtract
    # unprojected normalization residuals with incompatible units from it.
    retained = sum((Fraction(prior[k]['upper_exact']) for k in (
        'signed_point_linearization_norm_upper',
        'endpoint_signed_point_linearization_norm_upper',
        'anchor_and_center_shift_norm_upper')), Fraction(0))
    budget = Fraction(1)-retained
    return dict(algorithm='SAVED_COUPLED_NORMALIZATION_RESIDUAL_AND_OPERATOR_CONTRACT_ARB512_V1',
        claim='PARTIAL_COUPLED_RESIDUAL_EVALUATED_FULL_ACTION_PULLBACK_MISSING',
        interval=13, trial_column=14, first_affected_output_node=14,
        source_result_SHA256=sha(prior_path), paired_source_hashes=sources,
        families=results, original_physical_domain_shrunk=False,
        predictor_coefficients_exact=True, predictor_is_solution_enclosure=False,
        complete_physical_coupled_residual_evaluated=False,
        implicit_polynomial_solver_implemented=True, physical_implicit_solver_instantiated=False,
        known_relaxation_gain_lower=prior['relaxation_gain_lower'],
        known_relaxation_contraction_margin_upper=prior['relaxation_contraction_margin_upper'],
        conservative_complete_local_remainder_budget_exact=str(budget),
        conservative_complete_local_remainder_budget=float(budget),
        missing_ingredient=dict(
            action='Shared-parameter enclosures of H, H_u, physical source f and f_u, including their signed remainders, evaluated on the same affine solve predictors and correction domain.',
            output='A verified common-parameter lifted normalization and endpoint-to-HS-midpoint graph, with complete right-column output pullback and its nonlinear remainder.',
            inverse='A full stacked secant-defect/inclusion bound or rigorously weighted triangular block transport; the separate bordered q bounds are insufficient.',
            target='A pulled-back residual plus correction support below the complete local vector remainder budget; a scalar screen alone cannot close Gate 7.'),
        measured_certification_gap_reduction=None, physical_global_margin=None,
        physical_noncontraction_proved=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False,
        new_action_derivative_evaluations=0, new_workers_launched=0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    ctx.prec = 512
    result = evaluate(args.evidence_root.resolve())
    result['implementation_SHA256'] = {Path(__file__).name: sha(Path(__file__)),
                                      Path(shared.__file__).name: sha(Path(shared.__file__))}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('xb') as output:
        output.write(encoded(result))
    print(json.dumps(dict(claim=result['claim'],
        normalization={key: {name: value['complete_polynomial_support']['upper']
                            for name, value in family['normalization_residuals'].items()}
                       for key, family in result['families'].items()},
        local_remainder_budget=result['conservative_complete_local_remainder_budget'],
        physical_global_margin=None)), flush=True)


if __name__ == '__main__':
    main()
