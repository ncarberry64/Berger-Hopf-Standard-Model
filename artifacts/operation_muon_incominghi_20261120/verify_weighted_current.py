"""Test the action-owned weighted Higgs row in the saved finite force space.

Run with Python -I -S and an explicit inspected global --site-packages.
This is an adjoint diagnostic, not an exterior source or physical moment.
"""
import sys
from pathlib import Path
assert sys.flags.isolated and sys.flags.no_site and sys.flags.no_user_site
import argparse, hashlib, json, os

ap = argparse.ArgumentParser()
ap.add_argument('--site-packages', required=True)
ap.add_argument('--output', required=True)
args = ap.parse_args()
runtime = Path(sys.base_prefix).resolve()
site = Path(args.site_packages).resolve()
assert site.is_relative_to(runtime) and site.name == 'site-packages'
assert all(Path(p).resolve().is_relative_to(runtime) for p in sys.path)
for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
sys.dont_write_bytecode = True
sys.path.insert(0, str(site))
def no_external(event, details):
    if event in ('subprocess.Popen', 'os.system', 'socket.connect', 'socket.getaddrinfo'):
        raise RuntimeError(event)
sys.addaudithook(no_external)
import numpy as np

root = Path(__file__).resolve().parent
ev = root / 'evidence'
manifest = {}
for line in (ev / 'SHA256SUMS').read_text(encoding='utf-8').splitlines():
    digest, name = line.split('  ', 1)
    path = (ev / name).resolve()
    assert path.is_relative_to(ev.resolve())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    manifest[name] = digest
sub = ev / 'native_patch_first_jet'
with np.load(sub / 'formed_n0_wall_spin_transfer.npz', allow_pickle=False) as z:
    A, g = z['action_A'], z['spin_gap_covector']
with np.load(sub / 'formed_n0_equal_local_field_test.npz', allow_pickle=False) as z:
    C = z['field_covector']
    states = {k: z[k] for k in ('central_wall_response', 'H_aligned_wall_response', 'field_null_difference')}
with np.load(sub / 'formed_higgs_invariant_companion.npz', allow_pickle=False) as z:
    companion = z['invariant_companion']
    six = z['six_force_state_lift']
with np.load(ev / 'native_n0_coupled_static.npz', allow_pickle=False) as z:
    KH, K, lift, interior = z['KH20'], z['K84'], z['lift84x20'], z['interior64']
# KH20 order H4,[At,A1,A2,A3]x4; A order [A1,A2,A3]x4,H4.
# The central axial row is kappa*d(|H|^2 J3), including d|H|^2.
weighted = KH[19, np.r_[np.arange(8, 20), np.arange(4)]]
t = np.linalg.solve(A.T, g)
F = np.linalg.solve(A.T, C.T).T
def project(rows, target):
    coeff, _, rank, singular = np.linalg.lstsq(rows.T, target, rcond=None)
    residual = target - coeff @ rows
    return coeff, residual, int(rank), singular

cases = {}
rowsets = {'field_only': C, 'field_and_phase_current': np.vstack([C, companion]),
           'field_and_weighted_sheet_current': np.vstack([C, weighted]),
           'field_and_both_currents': np.vstack([C, companion, weighted])}
identity_error = 0.0
for name, rows in rowsets.items():
    force_rows = np.linalg.solve(A.T, rows.T).T
    c, r, rank, sv = project(force_rows, t)
    cs, rs, ranks, svs = project(rows, g)
    c6, r6, rank6, sv6 = project(rows @ six, g @ six)
    contractions = {}
    for key, u in states.items():
        f = A @ u
        gap = float(g @ u)
        known, remainder = float(c @ rows @ u), float(r @ f)
        identity_error = max(identity_error, abs(known + remainder - gap))
        contractions[key] = dict(gap=gap, reconstructed_from_readouts=known,
            remaining_force_projection=remainder, readouts=(rows @ u).tolist(),
            rhs_norm=float(np.linalg.norm(f)),
            independent_interior_residual=float(np.linalg.norm((K @ lift @ np.r_[np.zeros(4), u])[interior])))
    orth = float(np.linalg.norm(force_rows @ r))
    cases[name] = dict(rank=rank, singular_values=sv.tolist(), coefficients=c.tolist(),
        force_residual_norm=float(np.linalg.norm(r)),
        force_relative_residual=float(np.linalg.norm(r)/np.linalg.norm(t)),
        state_relative_residual=float(np.linalg.norm(rs)/np.linalg.norm(g)),
        six_force_relative_residual=float(np.linalg.norm(r6)/np.linalg.norm(g @ six)),
        orthogonality_error=orth, remaining_force_covector=r.tolist(),
        contractions=contractions)
    assert orth < 1e-9
assert identity_error < 2e-12
assert cases['field_only']['force_residual_norm'] > .3
assert cases['field_and_phase_current']['state_relative_residual'] > 1e-8
assert cases['field_and_phase_current']['six_force_relative_residual'] < 1e-10
assert np.linalg.norm(A.T @ t - g) < 1e-12
for module in tuple(sys.modules.values()):
    loc = getattr(module, '__file__', None)
    if loc:
        path = Path(loc).resolve()
        assert path.is_relative_to(runtime) or path == Path(__file__).resolve()
result = dict(classification='FINITE_CONDITIONAL_FORCE_SPACE_DIAGNOSTIC',
    baseline='archived incoming-hi; n=0; fixed geometry; temporal trace held',
    physical_guard='2e-10', physical_moment=None, physical_uncertainty=None,
    coordinate_norm_is_physical_norm=False, actual_exterior_force_supplied=False,
    matrix_condition_2=float(np.linalg.cond(A)),
    weighted_sheet_current_row=weighted.tolist(),
    adjoint_identity_max_error=identity_error, cases=cases,
    assumptions=['Use archived calibrated Higgs potential unchanged.',
      'No assertion that arbitrary finite forces are admissible physical loads.',
      'Weighted Higgs current is intrinsic action work, not an added exterior traction.'],
    exact_remaining_quantity='r.T f_ext for the same-background held-incident retarded exterior; coefficients above are in fixed archived coordinate norm',
    conditional_bound='abs(r.T f_ext) <= norm(r) * norm(project_kernel(force_rows, f_ext)); no physical force norm is supplied',
    source_sha256={k: manifest[k] for k in manifest if k.endswith(('formed_n0_wall_spin_transfer.npz', 'formed_n0_equal_local_field_test.npz', 'formed_higgs_invariant_companion.npz', 'native_n0_coupled_static.npz'))})
Path(args.output).write_bytes((json.dumps(result, indent=2, sort_keys=True)+'\n').encode('utf-8'))
print(json.dumps({'passed': True, 'identity_error': identity_error,
                 'cases': {k: {n:v[n] for n in ('rank','force_residual_norm','force_relative_residual','state_relative_residual')} for k,v in cases.items()}}))
