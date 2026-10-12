"""Evaluate the exact explicit inherited-clock contact at actual terminal1150."""
from pathlib import Path
from hashlib import sha256
import argparse, json, sys
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
sys.path.insert(0, str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_child_clock_application import holomorphic_child_explicit_clock_application
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(output):
    out = ROOT/output
    if out.exists():
        raise FileExistsError('preserve previous applications')
    refs = {}
    phase, _ = retained_input('outgoing', refs)
    base = ROOT/'artifacts/muon_holomorphic_child_terminal_20261011/run_2'
    md = json.loads((base/'result.json').read_bytes())
    path = base/'actual_complex_terminal_full_action.npz'
    expected = md['archives'][path.name]['sha256']
    if sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError('same complete terminal changed')
    with np.load(path, allow_pickle=False) as data:
        raw = data['raw_fields'].copy()
        time = complex(data['coordinate_time'].item())
    args = (phase['arrays']['initial_pair'], phase['arrays']['reference_pair'], phase['representation'])
    params = phase['receipt']['action_parameters']
    applied = holomorphic_child_explicit_clock_application(raw, time, *args, **params)
    controls = []
    for h in (2e-5, 1e-5):
        plus = holomorphic_inherited_child_action(raw, time+h, *args, **params)
        minus = holomorphic_inherited_child_action(raw, time-h, *args, **params)
        fd = (plus['gradient']-minus['gradient'])/(2*h)
        fv = (plus['value']-minus['value'])/(2*h)
        controls.append(dict(step=h, gradient_relative_max=float(np.max(abs(fd-applied['gradient_clock_first']))/
            max(1., np.max(abs(applied['gradient_clock_first'])))), value_relative_error=float(abs(fv-applied['value_clock_first'])/
            max(1., abs(applied['value_clock_first'])))))
    if max(max(c['gradient_relative_max'], c['value_relative_error']) for c in controls) > 3e-6:
        raise ArithmeticError('explicit-clock action derivative control failed')
    out.mkdir(parents=True)
    archive = out/'explicit_clock_action_application.npz'
    _compressed_npz(archive, dict(raw_fields=raw, coordinate_time=np.array(time),
        value_clock_first=np.array(applied['value_clock_first']),
        raw_gradient_clock_first=applied['raw_gradient_clock_first'],
        gradient_clock_first=applied['gradient_clock_first'],
        effective_connection_clock_first=applied['effective_connection_clock_first'],
        effective_wall_connection_clock_first=applied['effective_wall_connection_clock_first'],
        canonical_tangent_rhs=applied['canonical_tangent_rhs'],
        canonical_tangent_operator=applied['canonical_tangent_operator']))
    for name, module in sorted(sys.modules.items()):
        file = getattr(module, '__file__', None)
        if name.startswith('bhsm.') and file:
            try:
                rel = Path(file).relative_to(ROOT).as_posix()
            except ValueError:
                continue
            refs[rel] = sha256((ROOT/rel).read_bytes()).hexdigest()
    for file in (path, base/'result.json', Path(__file__), ROOT/'tests/test_muon_holomorphic_child_clock_application.py'):
        refs[file.relative_to(ROOT).as_posix()] = sha256(file.read_bytes()).hexdigest()
    action = applied['action']
    n = action['coordinates']['x_count']
    result = dict(classification='EVALUATED_EXACT_EXPLICIT_INHERITED_CLOCK_CONTACT_AT_FULL_COMPLEX_CHILD252',
        archives={archive.name: dict(bytes=archive.stat().st_size, sha256=sha256(archive.read_bytes()).hexdigest())},
        input_hashes=refs, original_terminal_node=1150, independent_clock_controls=controls,
        gradient_clock_first_norm=float(np.linalg.norm(applied['gradient_clock_first'])),
        canonical_tangent_rhs_norm=float(np.linalg.norm(applied['canonical_tangent_rhs'])),
        actual_geometry_multiplier_residual_max=float(np.max(abs(action['gradient'][2*n:2*n+24]))),
        cap_and_child_baseline_explicit_clock_first=0,
        zero_provenance=applied['zero_provenance'],
        canonical_tangent_solved=False, canonical_compatibility_established=False,
        physical_pole_or_Pauli_normalization_evaluated=False,
        remaining_action_application='same-action Gv=Pi and Gy=0 before solving the framed canonical tangent and selected first-hit descriptor',
        error_scope='binary64 exact connection polarizations with independent finite-clock checks; no exterior, continuum, matching or anomaly enclosure')
    receipt = out/'result.json'
    receipt.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False)+'\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(result_sha256=sha256(receipt.read_bytes()).hexdigest(),
        gradient_clock_first_norm=result['gradient_clock_first_norm'],
        canonical_tangent_rhs_norm=result['canonical_tangent_rhs_norm'], controls=controls)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    materialize(parser.parse_args().output)
