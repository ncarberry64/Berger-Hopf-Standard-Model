"""Evaluate new cutoff/source mixed contacts on saved multiprecision C2 jets.

No eigenproblem or completed source/history calculation is rerun. The
coordinate u=ell_witness*H remains fixed while s=log(c/c_witness) varies.
Neither this conditioning witness nor its finite Galerkin domain is physical.
"""
from hashlib import sha256
from pathlib import Path
import argparse
import json


def evaluate(repository, output):
    import mpmath as mp
    root, out = Path(repository).resolve(), Path(output).resolve()
    if out.exists():
        raise FileExistsError(out)
    relative = 'artifacts/muon_scalar_surface_derivation_20261015/quartic_run_1/result.json'
    source = json.loads((root / relative).read_bytes())
    records = {}
    with mp.workdps(80):
        fmt = lambda x: mp.nstr(x, 65)
        for name, channel in source['channels'].items():
            data = channel['precision105']
            eigenvalues = list(map(mp.mpf, data['base_low_eigenvalues_dimensionless']))
            jets = [list(map(mp.mpf, row)) for row in data['simple_eigenline_Taylor_coefficients']]

            def source_derivative(order, s):
                scale = mp.exp(s)
                terms = []
                for lam, (a, b, c, d) in zip(eigenvalues, jets):
                    exponential = mp.exp(-scale * lam)
                    r0 = exponential / lam
                    r1 = -exponential * (scale / lam + 1 / lam**2)
                    r2 = exponential * (scale**2 / lam + 2 * scale / lam**2 + 2 / lam**3)
                    r3 = -exponential * (scale**3 / lam + 3 * scale**2 / lam**2
                                         + 6 * scale / lam**3 + 6 / lam**4)
                    values = [mp.e1(scale * lam) / 2,
                              -r0 * a / 2,
                              -(2 * r0 * b + r1 * a**2) / 2,
                              -(6 * r0 * c + 6 * r1 * a * b + r2 * a**3) / 2,
                              -(24 * r0 * d + r1 * (24 * a * c + 12 * b**2)
                                + 12 * r2 * a**2 * b + r3 * a**4) / 2]
                    terms.append(values[order])
                return mp.fsum(terms)

            def eigen_taylor(u, lam, jet):
                return lam + mp.fsum(value * u**k for k, value in enumerate(jet, 1))

            def cutoff_kernel(u, order):
                # Exact s derivatives of the microscopic E1 functional for
                # w=-1: Gamma_s=-Tr(exp(-P))/2; Gamma_ss=Tr(P exp(-P))/2.
                values = [eigen_taylor(u, lam, jet) for lam, jet in zip(eigenvalues, jets)]
                if order == 1:
                    return -mp.fsum(mp.exp(-value) for value in values) / 2
                return mp.fsum(value * mp.exp(-value) for value in values) / 2

            rows = []
            for order in range(5):
                base = source_derivative(order, mp.mpf(0))
                first = mp.diff(lambda s: source_derivative(order, s), 0, 1)
                second = mp.diff(lambda s: source_derivative(order, s), 0, 2)
                direct_first = mp.diff(lambda u: cutoff_kernel(u, 1), 0, order)
                direct_second = mp.diff(lambda u: cutoff_kernel(u, 2), 0, order)
                coarse, fine = [
                    (source_derivative(order, step) - source_derivative(order, -step)) / (2 * step)
                    for step in (mp.mpf('0.00002'), mp.mpf('0.00001'))]
                rows.append(dict(
                    source_order=order, Gamma_u=fmt(base), Gamma_u_logc=fmt(first),
                    Gamma_u_logc_logc=fmt(second), relative_first_cutoff_slope=fmt(first / base),
                    partial_log_native_energy_contribution=fmt(-2 * first),
                    direct_heat_first_absolute_error=fmt(abs(first - direct_first)),
                    direct_heat_second_absolute_error=fmt(abs(second - direct_second)),
                    centered_logc_FD_relative_error=fmt(abs((fine - first) / first)),
                    centered_logc_FD_error_step_improvement=fmt(abs((coarse - first) / (fine - first))),
                ))
            # The old outer-cluster bound was Cauchy-derived for E1. For the
            # new first s derivative use |exp(-z)|, not |E1(z)|.
            rho = mp.mpf('.025')
            b, q = map(mp.mpf, data['source_operator_norm_upper_bounds'])
            delta = rho * b + rho**2 * q / 2
            tail = mp.factorial(4) * 123 * mp.exp(-(100 - delta)) / (2 * rho**4)
            records[name] = dict(rows=rows, omitted_outer_trace_Gamma_u4_logc_bound=fmt(tail))
    result = dict(
        classification='SAVED_CURRENT_C2_FINITE_SCALAR_MIXED_CUTOFF_CONTACTS',
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_hashes={relative: sha256((root / relative).read_bytes()).hexdigest()},
        actual_saved_source_jets_reused=True,
        completed_eigen_source_D5_profile_history_campaigns_restarted=False,
        coordinate='u=ell_witness*H held fixed; s=log(c/c_witness)',
        cutoff_first_identity='Gamma_s=(w/2) Tr exp(-cP); w=-1 in each declared core block',
        total_native_energy_rule='d_logE Gamma=-2*Gamma_s PLUS the actual P, domain, field and quotient variations',
        first_tail_scope='analytic omitted-outer-trace bound on the prior isolated cluster; not an outward input/continuum certificate',
        physical_lambda_H=None, physical_surface_gamma=None,
        physical_outgoing_fields=None, physical_full_derivative_passed_2e_minus_10=False,
        coupled_matching_corrections_applied=0, physical_two_spin_normalization=None,
        physical_muon_magnetic_moment=None, channels=records,
    )
    out.mkdir(parents=True)
    (out / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n',
                                     encoding='utf-8', newline='\n')
    print(json.dumps(dict(output=str(out), fourth_logc=records['plus']['rows'][4]['Gamma_u_logc'])))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    evaluate(args.repository, args.output)
