"""Integrate paired all-direction first variations to tighten primal values."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import certify_n12_gate7_affine_basis_mean_value_column as parent
import numpy as np


def evaluate(pilot):
    arrays, binding, report = original_evaluate(pilot)
    p = parent.producer.engine.p
    record = parent.json.loads((pilot/'record.json').read_bytes())
    witness = record['report']['point_eigenpair_checks'][0]
    if not p.proof_valid(witness) or witness.get('normalized_eigenpair_enclosed') is not True:
        raise ValueError('verified normalized point eigenvector enclosure required')
    point = p.hs.restore_balls(np.array(witness['target_midpoints_rational']),
                               np.array(witness['target_radii_rational']))
    if point.shape != (62,):
        raise ValueError('complete point eigenpair witness required')
    with np.load(pilot/'hessian.npz', allow_pickle=False) as a:
        def read(name):
            return p.hs.restore_balls(a[name+'_mid_q'], a[name+'_rad_q'])
        # The line solve's border is an auxiliary projected-RHS variable,
        # not the eigenvalue derivative. Only its first 61 rows are used.
        dpsi = read('uniform_solve_3')[:61]
        dresponse = read('uniform_solve_4')
        response = read('point_solve_0')
    if dpsi.shape != (61, 75) or dresponse.shape != (62, 75) or response.shape != (62, 1):
        raise ValueError('complete scaled tube derivatives and point response required')
    for name, derivative, anchor in (('psi_value', dpsi, point[:61, None]),
                                      ('response_value', dresponse, response)):
        bound = parent.producer.support(derivative)
        arrays[name+'_support'] = bound
        arrays[name] = anchor+np.array([parent.arb(0, v) for v in bound], dtype=object)[:, None]
    if not all(v.is_finite() for a in arrays.values() for v in a.flat):
        raise ArithmeticError('finite primal mean-value enclosures required')
    for file in (Path(__file__), ROOT/'theory/n12_gate7_affine_mean_value_primal_bootstrap.md'):
        p.geometry.residual.merge(binding['files'], {p.df.file_key(file): p.values.sha(file)})
    p.verify_sources(binding)
    report.update(uniform_primal_psi_and_response_enclosed=True,
                  eigenvalue_refined=False, auxiliary_line_border_used_as_eigenvalue_derivative=False,
                  maximum_psi_value_radius=float(max(v.rad() for v in arrays['psi_value'].flat)),
                  maximum_response_value_radius=float(max(v.rad() for v in arrays['response_value'].flat)))
    return arrays, binding, report


original_evaluate = parent.evaluate

if __name__ == '__main__':
    try:
        parent.evaluate = evaluate
        parent.main()
    finally:
        parent.evaluate = original_evaluate
