"""Isolated invented-only reference harness; never a production provider loader.

Only this test child uses legacy bare-name aliases and temporary source copies.
The installed engine itself uses qualified imports and fixed local roles.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def load(name, path):
    module = types.ModuleType(name); module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def check_references():
    manifest = json.loads((HERE / 'REFERENCE_MANIFEST_v1.json').read_bytes())
    for r in manifest['files']:
        if hashlib.sha256((HERE / r['path']).read_bytes()).hexdigest() != r['sha256']:
            raise ValueError('Reference source or invented fixture changed')


def leaves():
    import bhtracker._joint_v3 as package
    from bhtracker._joint_v3 import centered_geometry_v1, gaussian_mean_profile_v1
    from bhtracker._joint_v3 import spectral_trust_step_v1, bounded_negative_curvature_trust_v6
    from bhtracker._joint_v3 import known2023_student_model_v2, gaussian_joint_model_v4, published_gp_leaf_v2
    root = Path(package.__file__).resolve().parent
    for name, module in {'centered_geometry_v1': centered_geometry_v1,
                         'gaussian_mean_profile_v1': gaussian_mean_profile_v1,
                         'spectral_trust_step_v1': spectral_trust_step_v1,
                         'bounded_negative_curvature_trust_v6': bounded_negative_curvature_trust_v6,
                         'bounded_negative_curvature_trust_v5': bounded_negative_curvature_trust_v6,
                         'published_gp_leaf_v2': published_gp_leaf_v2,
                         'gaussian_joint_model_v4': gaussian_joint_model_v4}.items():
        sys.modules[name] = module
    # The original assertions keep their source. Only their explicit provider
    # fixture boundary is redirected to the reviewed installed role loader.
    adapter = types.ModuleType('known2023_student_model_v2')
    def factory(raw, *, core_path, student_directory, **options):
        return known2023_student_model_v2.Known2023StudentModel(raw,
            core_path=root / 'core_snapshot_v2.py', student_directory=root, **options)
    adapter.Known2023StudentModel = factory
    adapter.sha = known2023_student_model_v2.sha; adapter.KAPPA = known2023_student_model_v2.KAPPA
    sys.modules[adapter.__name__] = adapter
    load('gaussian_joint_model_v2', HERE / 'gaussian_joint_model_v2.py.txt')
    modules = []
    for name in ('test_numerical_leaves_v5', 'test_centered_model_v2', 'test_spectral_trust_v6',
                 'test_gaussian_joint_model_v4', 'test_audited_gaussian_model_v4'):
        module = load(name, HERE / (name + '.py.txt'))
        if name == 'test_gaussian_joint_model_v4': module.NUMERICAL = HERE
        modules.append(module)
    # The audited class inherits the unchanged eight Gaussian assertions.
    chosen = [modules[0], modules[1], modules[2], modules[4]]
    suites = [unittest.defaultTestLoader.loadTestsFromModule(m) for m in chosen]
    counts = [s.countTestCases() for s in suites]
    if counts != [25, 8, 22, 17]: raise ValueError('Reference assertion roster differs: ' + repr(counts))
    log = io.StringIO(); result = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.TestSuite(suites))
    return {'passed': result.wasSuccessful() and not result.skipped, 'tests': result.testsRun,
            'counts': counts, 'failures': [(str(t), s) for t, s in result.failures],
            'errors': [(str(t), s) for t, s in result.errors], 'log': log.getvalue(),
            'scope': '72 unchanged invented leaf/model assertions via explicit test-only provider facade',
            'native_model_calls': 0}


def reference_evaluate():
    import numpy as np
    with tempfile.TemporaryDirectory(prefix='bhsm-reference-') as directory:
        root = Path(directory)
        for path in HERE.rglob('*.py.txt'):
            if path.name.startswith('test_'): continue
            target = root / str(path.relative_to(HERE))[:-4]
            target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(path, target)
        sys.path[:0] = [str(root), str(root / 'providers')]
        from known2023_student_model_v2 import Known2023StudentModel, sha
        from gaussian_joint_model_v4 import GaussianJointModel
        raw = (HERE / 'invented_fixture_v1/INVENTED_DATASET_v1.json').read_bytes()
        truth = json.loads((HERE / 'invented_fixture_v1/INVENTED_TRUTH_v1.json').read_bytes())
        registry = json.loads((HERE / 'invented_fixture_v1/CONTROL_REGISTRY_v1.json').read_bytes())
        data = Known2023StudentModel(raw, purpose='WHOLLY_INVENTED', expected_sha256=sha(raw),
            core_path=root / 'core_snapshot_v2.py', student_directory=root / 'providers', control_registry=registry)
        model = GaussianJointModel(data); p = truth['p']
        state = np.r_[p['t0_jd_tdb'] - data.time_origin, np.log(p['tE_days']), p['u0_heliocentric'],
                      p['angle_source_minus_lens_rad'], p['pi_E'],
                      [truth['instruments'][n][1] for n in model.names], np.log([.007, 20., .004, .2])]
        def native(v):
            if hasattr(v, 'tolist'): return native(v.tolist())
            if isinstance(v, dict): return {str(k): native(x) for k, x in v.items()}
            if isinstance(v, (tuple, list)): return [native(x) for x in v]
            return v
        values = []
        for zero in ([], ['matern'], ['sho'], ['matern', 'sho']):
            values.append({'zero_components': zero, 'result': native(model.evaluate(state, details=True, zero_components=zero))})
        return {'state': state.tolist(), 'results': values, 'scope': 'Only frozen wholly invented measurements'}


def main():
    p = argparse.ArgumentParser(); p.add_argument('mode', choices=['leaves', 'reference'])
    p.add_argument('--package-root', type=Path, required=True); args = p.parse_args()
    check_references()
    # Source-checkout tests pass their explicit package parent; clean installed
    # tests pass site-packages. This is test-only and never resolves OUT/F.
    sys.path.insert(0, str(args.package_root.resolve()))
    value = leaves() if args.mode == 'leaves' else reference_evaluate()
    print(json.dumps(value, allow_nan=False))
    return 0 if value.get('passed', True) else 1


if __name__ == '__main__': raise SystemExit(main())
