"""Independent literal original84 daughter-frequency finite differences.

All coefficient/map/vertex entries are the exact stored binary64 values.
No BHSM derivative helper, state, history or physical outgoing selector is run.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import io
import json
from pathlib import Path
import zipfile

import numpy as np
from flint import acb, acb_mat, arb, ctx

REPO = Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
WORK = Path('C:/Users/carbe/OneDrive/Documents/CODEX')
INITIAL = WORK/'outputs/muon_daughter_source_20261016/initial_electron_only'
FIELD = REPO/'artifacts/muon_coupled_lorentz_field_symbol_20261011/run_1'
INITIAL_ARRAY_SHA = 'b4b98bcbe79a29b96edaa7712a0319d80be64356d049144848876a994caeaae5'
STEPS = (1e-4, 1e-6, 1e-8)
PRECISIONS = (192, 256)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def point(value):
    z = complex(value)
    a, b = arb(z.real), arb(z.imag)
    if not a.is_exact() or not b.is_exact():
        raise ArithmeticError('binary64-to-Arb conversion must be exact')
    return acb(a, b)


def matrix(value):
    a = np.asarray(value)
    if a.ndim != 2 or not np.isfinite(a).all():
        raise ValueError('finite stored matrix required')
    return acb_mat([[point(z) for z in row] for row in a])


def upper(value):
    if value.is_zero():
        return 0.0
    return float(np.nextafter(float(value.upper()), np.inf))


def maximum(a):
    return max(upper(abs(a[i, j])) for i in range(a.nrows()) for j in range(a.ncols()))


def center_error(a):
    c = np.array([[complex(float(a[i,j].real.mid()), float(a[i,j].imag.mid()))
                   for j in range(a.ncols())] for i in range(a.nrows())])
    e = np.array([[upper(abs(a[i,j]-point(c[i,j])))
                   for j in range(a.ncols())] for i in range(a.nrows())])
    return c, e


def overlap(a, b):
    return all(a[i,j].overlaps(b[i,j]) for i in range(a.nrows()) for j in range(a.ncols()))


def npz_write(path, arrays):
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, value in sorted(arrays.items()):
            data = io.BytesIO()
            np.lib.format.write_array(data, np.asarray(value), allow_pickle=False)
            info = zipfile.ZipInfo(name+'.npy', (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data.getvalue(), compresslevel=9)


def evaluate_side(coeff, Q, T, right, left, saved_first, bits):
    ctx.prec = bits
    ks = [matrix(k) for k in coeff]
    q, t = matrix(Q), matrix(T)
    r, l = matrix(right.reshape(24, 8)), matrix(left.reshape(24, 8))
    p = t*q
    exact_first = matrix(saved_first.reshape(8, 8))

    def literal(w):
        # Form the original full84 polynomial before its fixed Q/T maps.
        k = ks[0] + ks[1]*w + ks[2]*(w*w)
        a = q.transpose()*k*q
        u = a.solve(p.transpose())
        green = p*u
        tensor = r.transpose()*green*l
        return tensor, a*u-p.transpose()

    c0, rows0 = literal(acb(0))
    a0 = q.transpose()*ks[0]*q
    a1 = q.transpose()*ks[1]*q
    u0 = a0.solve(p.transpose())
    du = a0.solve(-a1*u0)
    derivative = r.transpose()*(p*du)*l
    derivative_rows = a0*du+a1*u0
    direct_error = maximum(derivative-exact_first)
    samples = []
    results = {}
    for step in STEPS:
        h = point(step)
        values = []
        equation_rows = []
        for mult in (2, 1, -1, -2):
            c, rows = literal(h*mult)
            values.append(c)
            equation_rows.append(maximum(rows))
        fd = (-values[0]+values[1]*8-values[2]*8+values[3])/(h*12)
        norm2 = sum(abs(exact_first[i,j])**2 for i in range(8) for j in range(8)).sqrt()
        difference2 = sum(abs((fd-exact_first)[i,j])**2 for i in range(8) for j in range(8)).sqrt()
        if not norm2 > 0:
            raise ArithmeticError('the complete supplied first tensor must be nonzero')
        results[step] = fd
        samples.append(dict(step=step, step_exact_binary64_ratio=list(float(step).as_integer_ratio()),
            maximum_absolute_difference_from_saved_binary64_jet=maximum(fd-exact_first),
            relative_Frobenius_difference_upper=upper(difference2/norm2),
            finite_difference_truncation_vs_independent_mp_derivative_upper=maximum(fd-derivative),
            maximum_literal_80x24_equation_residual_upper=max(equation_rows)))
    return dict(value=c0, derivative=derivative, finite_differences=results,
        record=dict(precision_bits=bits, literal_value_equation_residual_upper=maximum(rows0),
            independent_mp_derivative_equation_residual_upper=maximum(derivative_rows),
            independent_mp_derivative_vs_saved_binary64_jet_upper=direct_error,
            samples=samples))


def binary_literal(coeff, Q, T, right, left, w):
    k = coeff[0]+w*coeff[1]+w*w*coeff[2]
    p = T@Q
    return right.reshape(24,8).T @ (p@np.linalg.solve(Q.T@k@Q, p.T)) @ left.reshape(24,8)


def run(output):
    out = Path(output).resolve()
    if out.exists():
        raise FileExistsError('preserve previous independent controls')
    saved = json.loads((INITIAL/'result.json').read_text())
    if digest(INITIAL/'application.npz') != INITIAL_ARRAY_SHA or saved['numerical_sha256'] != INITIAL_ARRAY_SHA:
        raise ValueError('the exact parent daughter-frequency epoch changed')
    pins = dict(saved['input_sha256'])
    for name, expected in pins.items():
        if digest(REPO/name) != expected:
            raise ValueError('same original source changed: '+name)
    for path in (INITIAL/'result.json', INITIAL/'application.npz', FIELD/'result.json', FIELD/'application.npz'):
        pins[str(path)] = digest(path)
    md = json.loads((FIELD/'result.json').read_text())
    if digest(FIELD/'application.npz') != md['archive']['sha256']:
        raise ValueError('the original field coefficient archive changed')
    arrays = {}
    records = []
    with np.load(FIELD/'application.npz', allow_pickle=False) as field, np.load(INITIAL/'application.npz', allow_pickle=False) as daughter:
        for side in ('incoming', 'outgoing'):
            coeff, Q, T = [field[side+'_'+key].copy() for key in
                ('proper_frequency_coefficients', 'field_quotient_lift', 'joint_trace_map')]
            right = daughter[side+'_owned_charged_current_right_vertices'].copy()
            left = daughter[side+'_owned_charged_current_left_vertices'].copy()
            first = daughter[side+'_tensor_frequency_first'].copy()
            if coeff.shape != (3,84,84) or Q.shape != (84,80) or T.shape != (24,84):
                raise ValueError('the complete original84 fixed domain is required')
            if right.shape != (24,2,4) or left.shape != (24,4,2) or first.shape != (2,4,4,2):
                raise ValueError('all24 original legs and64 tensor entries are required')
            applications = [evaluate_side(coeff,Q,T,right,left,first,bits) for bits in PRECISIONS]
            a, b = applications
            if not overlap(a['value'],b['value']) or not overlap(a['derivative'],b['derivative']):
                raise ArithmeticError('independent precision enclosures do not overlap')
            precision_rows = []
            for step in STEPS:
                if not overlap(a['finite_differences'][step],b['finite_differences'][step]):
                    raise ArithmeticError('finite-difference precision enclosures do not overlap')
                key = f'{side}_h_{step:.0e}'
                c, e = center_error(b['finite_differences'][step])
                arrays[key+'_mp_fd'] = c.reshape(2,4,4,2)
                arrays[key+'_mp_export_absolute_error_upper'] = e.reshape(2,4,4,2)
                precision_rows.append(dict(step=step,
                    lower_precision_minus_higher_precision_absolute_upper=maximum(a['finite_differences'][step]-b['finite_differences'][step]),
                    enclosures_overlap=True))
            c, e = center_error(b['derivative'])
            arrays[side+'_independent_mp_derivative'] = c.reshape(2,4,4,2)
            arrays[side+'_independent_mp_derivative_export_error_upper'] = e.reshape(2,4,4,2)
            arrays[side+'_saved_binary64_analytic_first'] = first
            binary_rows = []
            for step in STEPS:
                values = [binary_literal(coeff,Q,T,right,left,mult*step) for mult in (2,1,-1,-2)]
                fd = (-values[0]+8*values[1]-8*values[2]+values[3])/(12*step)
                mp = b['finite_differences'][step]
                binary_rows.append(dict(step=step,
                    max_absolute_vs_saved_binary64_analytic=float(np.max(abs(fd-first.reshape(8,8)))),
                    max_absolute_vs_exact_stored_mp_fd_upper=maximum(matrix(fd)-mp)))
                arrays[f'{side}_h_{step:.0e}_binary64_fd'] = fd.reshape(2,4,4,2)
            records.append(dict(side=side, multiprecision=[x['record'] for x in applications],
                precision_comparison=precision_rows, independent_binary64_literal_sweep=binary_rows,
                parent_legacy_binary64_sweep=next(x['source_frequency_jet_comparisons'] for x in saved['records'] if x['side']==side)))
            print(json.dumps(dict(side=side, high_precision=b['record'], binary64=binary_rows),sort_keys=True),flush=True)
    ctx.prec = 256
    pins[str(Path(__file__).resolve())] = digest(Path(__file__))
    out.mkdir(parents=True)
    npz_write(out/'frequency_control.npz', arrays)
    result = dict(classification='INDEPENDENT_LITERAL_ORIGINAL84_DAUGHTER_FREQUENCY_CONTROL',
        records=records, precision_bits=list(PRECISIONS), input_sha256=pins,
        numerical_sha256=digest(out/'frequency_control.npz'), producer_sha256=digest(Path(__file__)),
        exact_stored_entry_scope=True, binary64_entries_imported_as_exact_dyadic_points=True,
        literal_equation='K(w)=K0+w K1+w^2 K2; A=Q^T K Q; P=T Q; G=P solve(A,P^T); C=R_flat^T G L_flat',
        frequency_variable='original proper-frequency w, centered at0; fixed Q/T/H/R/N and all24 original vertices',
        finite_difference='[-C(2h)+8C(h)-8C(-h)+C(-2h)]/(12h); every requested step retained',
        derivative_helper_called=False, original_full84_and_all64_coefficients_retained=True,
        analytic_left_conjugated=False, physical_state_or_domain_selected=False,
        physical_outgoing_derivative_admitted=False, original_Maxwell_or226_after_pass=False,
        original_coupled_corrections=0, measured_parameters_or_VA_fit_used=False,
        error_scope='certified Acb arithmetic enclosures for exact stored coefficient/map/vertex data; finite-step truncation measured against independent MP inverse derivative; source formation, continuum, physical outgoing/domain and state errors not enclosed')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    (out/'executed_producer.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(output=str(out),result_sha256=digest(out/'result.json'),numerical_sha256=result['numerical_sha256']),sort_keys=True),flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
