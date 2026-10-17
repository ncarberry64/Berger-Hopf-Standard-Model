"""Bounded residual corrections of a fixed stored canonical/frame saddle.

The Acb bounds concern exact stored binary coefficients only. Neither a
bordered solve nor its frame reaction establishes the unbordered action rows.
"""
from __future__ import annotations
import numpy as np
from flint import acb, acb_mat, ctx


def _matrix(values):
    a = np.asarray(values, complex)
    if a.ndim == 1:
        a = a[:, None]
    return acb_mat([[acb(float(v.real), float(v.imag)) for v in row] for row in a])


def _mid(values):
    return np.array([[complex(float(values[i, j].real.mid()),
                              float(values[i, j].imag.mid()))
                      for j in range(values.ncols())]
                     for i in range(values.nrows())])


def _upper(values):
    return max(float(abs(values[i, j]).upper())
               for i in range(values.nrows()) for j in range(values.ncols()))


def bounded_stored_admission_correction(K, rhs, initial, original_count, *,
        action_rows=None, fixed_x=None, source_rows=None, target_rows=None,
        precision_bits=192, correction_count=3, tolerance=2e-10):
    """Correct Kz=rhs with all original/frame rows and unchanged coefficients.

    Optional ``action_rows`` is the independently stored original H[phase,:].
    It rechecks H[phase,:] (fixed_x, phase_solution)+source-target. This keeps
    binary rhs assembly error distinct from phase residual and F.T*rho.
    The corrected high/low pair is a matrix-solution representation; the
    rounded solution is checked separately and is the ordinary consumer state.
    """
    K = np.asarray(K, complex); rhs = np.asarray(rhs, complex)
    initial = np.asarray(initial, complex); n = int(original_count)
    if (K.shape != (len(rhs), len(rhs)) or initial.shape != rhs.shape
            or not 0 < n < len(rhs) or not np.isfinite(K).all()
            or not np.isfinite(rhs).all() or not np.isfinite(initial).all()
            or np.any(K[n:, n:] != 0)):
        raise ValueError('finite original saddle, named frame border and same state required')
    if correction_count not in (1, 2, 3) or precision_bits < 128 or tolerance != 2e-10:
        raise ValueError('one bounded 1..3 correction application, precision>=128 and original guard required')
    supplied = (action_rows, fixed_x, source_rows, target_rows)
    if any(v is not None for v in supplied) and not all(v is not None for v in supplied):
        raise ValueError('all independent original action operands must be supplied')
    if action_rows is not None:
        H = np.asarray(action_rows, complex); x = np.asarray(fixed_x, complex)
        g = np.asarray(source_rows, complex); p = np.asarray(target_rows, complex)
        if (H.shape != (n, len(x)+n) or g.shape != (n,) or p.shape != (n,)
                or not np.array_equal(H[:, len(x):], K[:n, :n])):
            raise ValueError('same original action phase block and unchanged x/source/target required')
    old = ctx.prec; ctx.prec = precision_bits
    try:
        KK, rr, zz = _matrix(K), _matrix(rhs), _matrix(initial)
        A, F = _matrix(K[:n, :n]), _matrix(K[:n, n:])
        C, rframe = _matrix(K[n:, :n]), _matrix(rhs[n:])
        rphase = _matrix(rhs[:n])
        if action_rows is not None:
            HH, xx, gg, pp = _matrix(H), _matrix(x), _matrix(g), _matrix(p)
            exact_rhs = pp - _matrix(H[:, :len(x)])*xx - gg
            assembly = rphase-exact_rhs
        histories = []; rounded_states = []; rounded_original = []
        def evaluate(z):
            phase = acb_mat([[z[i, 0]] for i in range(n)])
            rho = acb_mat([[z[i, 0]] for i in range(n, len(rhs))])
            original = A*phase-rphase
            reaction = F*rho
            bordered = KK*z-rr
            frame = C*phase-rframe
            result = dict(bordered_residual_upper=_upper(bordered),
                unbordered_phase_residual_upper=_upper(original),
                frame_equation_residual_upper=_upper(frame),
                frame_reaction_phase_rows_upper=_upper(reaction))
            full = None
            if action_rows is not None:
                direction = acb_mat([[xx[i, 0]] for i in range(len(x))]
                    + [[phase[i, 0]] for i in range(n)])
                full = HH*direction+gg-pp
                result['original_action_rows_residual_upper'] = _upper(full)
                result['decomposition_residual_upper'] = _upper(full-(original+assembly))
            return result, original, reaction, bordered, frame, full
        for iteration in range(correction_count+1):
            metric, _, _, _, _, full = evaluate(zz)
            rounded = _mid(zz)[:, 0]; rz = _matrix(rounded)
            rmetric, _, _, _, _, rfull = evaluate(rz)
            metric.update(iteration=iteration, rounded_state=rmetric)
            histories.append(metric); rounded_states.append(rounded)
            if rfull is not None: rounded_original.append(_mid(rfull)[:, 0])
            if iteration < correction_count:
                residual = rr-KK*zz
                correction = KK.solve(residual)
                metric['correction_norm'] = float(np.linalg.norm(_mid(correction)))
                zz = zz+correction
        final, unbordered, reaction, bordered, frame, full = evaluate(zz)
        hi = _mid(zz)[:, 0]; lo = _mid(zz-_matrix(hi))[:, 0]
        pair = _matrix(hi)+_matrix(lo)
        pair_metric, _, _, _, _, pair_full = evaluate(pair)
        rounded_metric, _, _, _, _, rounded_full = evaluate(_matrix(hi))
        strings = np.array([[str(zz[i, 0].real), str(zz[i, 0].imag)]
                            for i in range(len(rhs))])
        arrays = dict(stored_saddle=K, stored_rhs=rhs, initial_solution=initial,
            correction_solution_high=hi, correction_solution_low=lo,
            correction_solution_ball_strings=strings,
            rounded_states=np.asarray(rounded_states),
            exact_stored_unbordered_phase_rows=_mid(unbordered)[:, 0],
            exact_stored_frame_reaction_phase_rows=_mid(reaction)[:, 0],
            exact_stored_bordered_rows=_mid(bordered)[:, 0],
            exact_stored_frame_rows=_mid(frame)[:, 0])
        if action_rows is not None:
            arrays.update(original_action_row_matrix=H, fixed_delta_x=x,
                unchanged_source_rows=g, unchanged_target_rows=p,
                stored_rhs_assembly_difference=_mid(assembly)[:, 0],
                exact_stored_original_action_rows=_mid(full)[:, 0],
                rounded_original_action_rows=_mid(rounded_full)[:, 0],
                high_low_original_action_rows=_mid(pair_full)[:, 0],
                rounded_original_action_rows_history=np.asarray(rounded_original))
        return dict(arrays=arrays, histories=histories, exact_stored=final,
            rounded_state=rounded_metric, high_low_state=pair_metric,
            stored_rhs_assembly_difference_upper=None if action_rows is None else _upper(assembly),
            rounded_original_rows_guard_passed=bool(action_rows is not None and
                rounded_metric['original_action_rows_residual_upper'] <= tolerance and
                rounded_metric['frame_equation_residual_upper'] <= tolerance),
            high_low_original_rows_guard_passed=bool(action_rows is not None and
                pair_metric['original_action_rows_residual_upper'] <= tolerance and
                pair_metric['frame_equation_residual_upper'] <= tolerance),
            tolerance=tolerance, correction_count=correction_count,
            precision_bits=precision_bits, fixed_coefficients_target_source_preserved=True)
    finally:
        ctx.prec = old
