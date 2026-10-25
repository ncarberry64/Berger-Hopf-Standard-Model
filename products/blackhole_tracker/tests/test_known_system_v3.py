"""Portable invented-only engine/loader/replay tests; never native recovery."""
import ast
import base64
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bhtracker import known_system_v3 as api

REFERENCE = Path(__file__).resolve().parent / 'known_system_v3_reference'


def functions(path):
    result = {}
    def visit(nodes, prefix=''):
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                result[prefix + node.name] = ast.dump(node, include_attributes=False)
            elif isinstance(node, ast.ClassDef): visit(node.body, prefix + node.name + '.')
    visit(ast.parse(path.read_bytes()).body)
    return result


class SourceAndMetadata(unittest.TestCase):
    def test_numerical_function_asts_equal_exact_prototypes_except_declared_loader(self):
        manifest = api.verify_sources(); private = Path(api.__file__).parent / '_joint_v3'
        count = 0
        for row in manifest['files']:
            if 'prototype_sha256' not in row: continue
            relative = ('providers/' if row['filename'] in ('student_ou.py', 'student_ou_banded.py') else '') + row['filename'] + '.txt'
            original = REFERENCE / relative
            self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(), row['prototype_sha256'])
            before, after = functions(original), functions(private / row['filename'])
            changed = [name for name in before if before[name] != after.get(name)]
            self.assertEqual(changed, ['load_source'] if row['filename'] == 'known2023_student_model_v2.py' else [])
            count += len(before) - len(changed)
        self.assertGreater(count, 70)

    def test_inspection_does_not_import_optional_scientific_engine(self):
        with patch.object(api, '_model', side_effect=AssertionError('No model during inspection')):
            result = api.availability()
        self.assertEqual(result['engine'], api.ENGINE); self.assertEqual(result['publication_hold'], 'HOLD')
        self.assertFalse(result['scientific_acceptance'])

    def test_manifest_tamper_and_nonlocal_provider_paths_refuse(self):
        with patch.object(api, 'SOURCE_MANIFEST_SHA256', '0' * 64), self.assertRaises(ValueError): api.verify_sources()
        from bhtracker._joint_v3._bindings import load_provider
        with self.assertRaises(ValueError): load_provider(REFERENCE / 'core_snapshot_v2.py.txt', '0' * 64)

    def test_equal_loaded_code_is_not_rejected_by_marshal_reference_layout(self):
        from bhtracker._joint_v3._bindings import check_live_source
        from bhtracker._joint_v3 import core_snapshot_v2
        self.assertIsNone(check_live_source(core_snapshot_v2))

    def test_physical_source_alias_passes_but_foreign_filename_or_constants_refuse(self):
        from bhtracker._joint_v3._bindings import check_live_source
        from bhtracker._joint_v3 import core_snapshot_v2 as core
        source = Path(core.__file__).resolve(strict=True)
        original = core.project_ne
        aliases = [str(source.parent) + '/./' + source.name]
        if sys.platform == 'win32':
            import ctypes
            buffer = ctypes.create_unicode_buffer(32768)
            if ctypes.windll.kernel32.GetShortPathNameW(str(source), buffer, len(buffer)):
                aliases.append(buffer.value)
        def function(code):
            return types.FunctionType(code, original.__globals__, original.__name__,
                                      original.__defaults__, original.__closure__)
        for alias in aliases:
            self.assertEqual(Path(alias).resolve(strict=True), source)
            with patch.object(core, 'project_ne', function(original.__code__.replace(co_filename=alias))):
                self.assertIsNone(check_live_source(core))
        with patch.object(core, 'project_ne', function(original.__code__.replace(co_filename=str(Path(api.__file__).resolve())))):
            with self.assertRaises(ValueError): check_live_source(core)
        changed = original.__code__.replace(co_consts=original.__code__.co_consts + ('INVENTED_CONSTANT_DRIFT',))
        with patch.object(core, 'project_ne', function(changed)):
            with self.assertRaises(ValueError): check_live_source(core)
        self.assertIsNone(check_live_source(core))

    def test_duplicate_keys_general_input_and_native_relabel_refuse(self):
        for raw, purpose in [(b'{"x":1,"x":2}', 'WHOLLY_INVENTED'),
                             (b'{}', 'GENERAL_USER'), (b'{}', 'AUTHENTIC2023')]:
            with self.assertRaises(ValueError): api.validate_benchmark(raw, purpose=purpose)

    def test_optional_dependency_unavailable_is_explicit_not_old_solver_fallback(self):
        original = api.importlib.metadata.version
        def version(name):
            if name == 'celerite2': raise api.importlib.metadata.PackageNotFoundError(name)
            return original(name)
        with patch.object(api.importlib.metadata, 'version', version):
            state = api.availability()
            self.assertFalse(state['available']); self.assertIn('celerite2', state['missing_dependencies'])


@unittest.skipUnless(api.availability()['available'], 'Optional joint-research dependencies are required')
class PortableEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (REFERENCE / 'invented_fixture_v1/INVENTED_DATASET_v1.json').read_bytes()
        cls.registry = json.loads((REFERENCE / 'invented_fixture_v1/CONTROL_REGISTRY_v1.json').read_bytes())
        cls.truth = json.loads((REFERENCE / 'invented_fixture_v1/INVENTED_TRUTH_v1.json').read_bytes())
        cls.settings = {'purpose': 'WHOLLY_INVENTED', 'control_registry': cls.registry,
                        'numerical_time_origin': 2455765., 'angular_reference': 2456000.}

    def state(self, model=None):
        import numpy as np
        names = model.names if model is not None else api.validate_benchmark(self.raw, **{k: self.settings[k] for k in ('purpose', 'control_registry')})['instruments']
        p = self.truth['p']; origin = model.data.time_origin if model is not None else 2455765.
        return [p['t0_jd_tdb'] - origin, float(np.log(p['tE_days'])), p['u0_heliocentric'],
                p['angle_source_minus_lens_rad'], p['pi_E']] + [self.truth['instruments'][n][1] for n in names] + list(map(float, np.log([.007, 20., .004, .2])))

    def child(self, mode):
        process = subprocess.run([sys.executable, '-I', '-B', str(REFERENCE / 'run_reference_checks.py'), mode,
            '--package-root', str(Path(api.__file__).resolve().parent.parent)], capture_output=True, text=True, timeout=120)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        return json.loads(process.stdout)

    def test_72_preserved_invented_leaf_assertions(self):
        result = self.child('leaves'); self.assertTrue(result['passed']); self.assertEqual(result['tests'], 72)

    def test_exact_package_vs_prototype_all_four_faces(self):
        reference = self.child('reference')
        for case in reference['results']:
            result = api.evaluate_saved_state(self.raw, reference['state'], zero_components=case['zero_components'], **self.settings)
            self.assertEqual(result['result'], case['result'])
            self.assertFalse(result['known_black_hole_recovery_accepted']); self.assertIsNone(result['accepted_mass_interval'])

    def test_large_jd_origin_reference_and_exact_small_offset_retained(self):
        import numpy as np
        a = api._model(self.raw, self.settings)
        other = {**self.settings, 'numerical_time_origin': 2455710., 'angular_reference': 2456500.}
        b = api._model(self.raw, other); x, y = self.state(a), self.state(b)
        first, second = a.evaluate(x, details=True), b.evaluate(y, details=True)
        self.assertAlmostEqual(first['negative_two_log_likelihood'], second['negative_two_log_likelihood'], places=8)
        self.assertAlmostEqual(first['parameters']['theta_E_mas'], second['parameters']['theta_E_mas'], places=9)
        from bhtracker._joint_v3.centered_geometry_v1 import centered_geometry
        args = dict(numerical_time_origin=2455765., tE_days=128., u0_heliocentric=.25,
                    angle_source_minus_lens_rad=.7, pi_E=.125, earth=np.array([[.125, -.25]]))
        near = centered_geometry(np.array([2455765.]), t0_offset_days=1e-10, **args)
        exact = centered_geometry(np.array([2455765.]), t0_offset_days=0., **args)
        self.assertTrue(any(np.any(left != right) for left, right in zip(near, exact)))

    def test_instrument_order_and_explicit_simulation_registration(self):
        document = json.loads(self.raw); document['photometry'] = document['photometry'][-1:] + document['photometry'][:-1]
        raw = api._encode(document); registry = {'wholly_invented_sha256': [api._sha(raw)]}
        summary = api.validate_benchmark(raw, purpose='WHOLLY_INVENTED', control_registry=registry)
        expected = list(dict.fromkeys(r['instrument'] for r in document['photometry']))
        self.assertEqual(summary['instruments'], expected)
        model = api._model(raw, {**self.settings, 'control_registry': registry})
        self.assertEqual(list(model.names), expected)
        with self.assertRaises(ValueError): api.validate_benchmark(raw, purpose='WHOLLY_INVENTED', control_registry=self.registry)

    def test_wrong_clock_missing_uncertainty_and_provider_mutation_refuse(self):
        for field in ('clock', 'error'):
            document = json.loads(self.raw)
            if field == 'clock': document['time_coordinate'] = 'UNSPECIFIED'
            else: document['astrometry'][0]['north_error_mas'] = None
            raw = api._encode(document)
            with self.assertRaises(ValueError):
                api.validate_benchmark(raw, purpose='WHOLLY_INVENTED', control_registry={'wholly_invented_sha256': [api._sha(raw)]})
        from bhtracker._joint_v3 import gaussian_joint_model_v4 as module
        with patch.object(module.GaussianJointModel, '_photo', lambda *a, **k: None), self.assertRaises(ValueError):
            api._model(self.raw, self.settings)

    def test_unrelated_bare_provider_does_not_replace_qualified_engine(self):
        alien = types.ModuleType('student_ou'); alien.__file__ = 'UNTRUSTED_UNUSED.py'
        with patch.dict(sys.modules, {'student_ou': alien}):
            model = api._model(self.raw, self.settings)
            self.assertNotEqual(model.data.student.__name__, 'student_ou')
            self.assertTrue(model.verify_snapshot()['verified'])

    def test_replay_integrity_numerical_and_tampered_statistic(self):
        saved = api.evaluate_saved_state(self.raw, self.state(), zero_components=['matern', 'sho'], **self.settings)
        self.assertEqual(api.verify_replay(saved, mode='integrity')['verification']['mode'], 'INTEGRITY_ONLY')
        self.assertTrue(api.verify_replay(saved, mode='numerical')['verification']['passed'])
        bad = deepcopy(saved); bad['result']['negative_two_log_likelihood'] += 1.
        with self.assertRaises(ValueError): api.verify_replay(bad)
        bad.pop('integrity_sha256'); bad = api._envelope(bad.pop('schema'), {k: v for k, v in bad.items() if k != 'engine'})
        self.assertFalse(api.verify_replay(bad, mode='numerical')['verification']['passed'])

    def test_replay_lineage_and_runtime_refusal(self):
        saved = api.evaluate_saved_state(self.raw, self.state(), zero_components=['matern', 'sho'], **self.settings)
        for key in ('runtime', 'result'):
            bad = deepcopy(saved)
            if key == 'runtime': bad['runtime']['python'] = '0.0.0'
            else: bad['result']['complete_evaluated_state']['parameter_names'].reverse()
            bad.pop('integrity_sha256'); schema = bad.pop('schema'); bad.pop('engine')
            bad = api._envelope(schema, bad)
            with self.assertRaises(ValueError): api.verify_replay(bad, mode='numerical')

    def test_plan_is_model_free_explicit_bounded_and_no_root_permission_gate(self):
        with patch.object(api, '_model', side_effect=AssertionError('Planning must not construct a forward model')):
            plan = api.plan_run(self.raw, [{'state': self.state(), 'zero_components': ['matern', 'sho']}], **self.settings)
        self.assertEqual(api._validated_plan(plan), self.raw)
        self.assertFalse(any('admission' in key or 'root' in key for key in plan))
        for resources in ({'full_calls_per_case': 3}, {'max_iterations': 65}, {'wall_seconds': True}, {'unknown': 1}):
            with self.assertRaises(ValueError): api.plan_run(self.raw, [{'state': self.state(), 'zero_components': []}], resources=resources, **self.settings)

    def test_real_invented_worker_retains_budget_status_and_full_prefix(self):
        from bhtracker._joint_v3._run import worker
        plan = api.plan_run(self.raw, [{'state': self.state(), 'zero_components': ['matern', 'sho']}],
            resources={'max_iterations': 1, 'full_calls_per_case': 4, 'full_calls_total': 4,
                       'covariance_calls_total': 4, 'case_seconds': 10, 'wall_seconds': 15}, **self.settings)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'workspace'; path.mkdir(); api._write_new(path / 'PLAN.json', plan)
            self.assertEqual(worker(path), 0)
            events = [json.loads(line) for line in (path / 'ALL_OBJECTIVE_STAGES.jsonl').read_bytes().splitlines()]
            summary = json.loads((path / 'WORKER.json').read_bytes())
            self.assertLessEqual(summary['full_calls'], 4); self.assertLessEqual(summary['covariance_calls'], 4)
            self.assertTrue(any(e['stage'] == 'FULL_PLANNED' for e in events))
            self.assertTrue(any(e['stage'] == 'FULL_RETURNED' for e in events))
            case = json.loads((path / 'case_0000.json').read_bytes())
            self.assertFalse(case['known_black_hole_recovery_accepted'])
            self.assertTrue(case['solver']['status'].endswith('UNRESOLVED'))
            api._write_new(path / 'RUN.json', {'schema': 'bhtracker.known_system_v3.run.v1', 'engine': api.ENGINE,
                'plan_sha256': api._sha(api._encode(plan)), 'source_identity': api.source_identity(), **api.FLAGS})
            archive = Path(temp) / 'audit.zip'
            api.export_workspace(path, archive)
            self.assertTrue(api.replay_export(archive, mode='integrity')['verification']['passed'])
            partial = api.replay_export(archive, mode='numerical', max_saved_states=1)
            self.assertFalse(partial['verification']['passed'])
            self.assertTrue(any(r['status'] == 'UNKNOWN_REPLAY_BUDGET' for r in partial['outcomes']))
            with zipfile.ZipFile(archive, 'a') as bundle: bundle.writestr('../UNEXPECTED.json', '{}')
            with self.assertRaises(ValueError): api.replay_export(archive)

    def prepared_workspace(self, directory, *, raw=None, registry=None, saved=None):
        raw = self.raw if raw is None else raw
        registry = self.registry if registry is None else registry
        settings = {**self.settings, 'control_registry': registry}
        zero = ['matern', 'sho']
        plan = api.plan_run(raw, [{'state': self.state(), 'zero_components': zero}], **settings)
        if saved is None: saved = api.evaluate_saved_state(raw, self.state(), zero_components=zero, **settings)
        path = Path(directory) / 'workspace'; path.mkdir()
        api._write_new(path / 'PLAN.json', plan)
        api._write_new(path / 'RUN.json', {'schema': 'bhtracker.known_system_v3.run.v1', 'engine': api.ENGINE,
            'plan_sha256': api._sha(api._encode(plan)), 'source_identity': api.source_identity(), **api.FLAGS})
        api._write_new(path / 'case_0000.json', {**plan['cases'][0], 'status': 'RETURNED',
            'replayed_states': [{'role': 'terminal', 'saved_state': saved}], **api.FLAGS})
        return path, plan

    def test_keyboard_interrupt_stops_child_and_retains_cancelled_unknown_terminal(self):
        plan = api.plan_run(self.raw, [{'state': self.state(), 'zero_components': []}], **self.settings)
        class Child:
            def __init__(self): self.waits = 0; self.terminated = False; self.killed = False
            def wait(self, timeout=None):
                self.waits += 1
                if self.waits == 1: raise KeyboardInterrupt()
                return -15
            def terminate(self): self.terminated = True
            def kill(self): self.killed = True
        child = Child()
        with tempfile.TemporaryDirectory() as temp, patch.object(api.subprocess, 'Popen', return_value=child) as start:
            path = Path(temp) / 'cancelled'
            result = api.run_plan(plan, path)
            self.assertTrue(child.terminated); self.assertFalse(child.killed); self.assertEqual(start.call_count, 1)
            self.assertEqual(child.waits, 2); self.assertTrue(result['cancelled'])
            self.assertEqual(result['status'], 'CANCELLED_PARTIAL')
            self.assertEqual(result['cases'][0]['status'], 'UNKNOWN_CANCELLED')
            self.assertTrue((path / 'PLAN.json').exists()); self.assertTrue((path / 'RUN.json').exists())
            self.assertFalse(result['known_black_hole_recovery_accepted'])

    def test_worker_vetoes_last_full_or_final_metadata_deadline_with_saved_prefix(self):
        import numpy as np
        from bhtracker._joint_v3 import _run, bounded_negative_curvature_trust_v6 as solver
        for crossing in ('full', 'final'):
            class Clock:
                now = 0.
                def monotonic(self): return self.now
            clock = Clock()
            class Model:
                lower = np.full(12, -100.); upper = np.full(12, 100.); scales = np.ones(12)
                parameter_names = tuple('x' + str(i) for i in range(12))
                data = types.SimpleNamespace(ep=np.zeros(1), ea=np.zeros(1), eref=np.zeros(1))
                verifications = 0
                def active_optimizer_indices(self, zero): return tuple(range(12))
                def verify_snapshot(self):
                    self.verifications += 1
                    if crossing == 'final' and self.verifications == 2: clock.now = 11.
                def evaluate(self, state, **options):
                    context = {'kind': 'CENTRAL', 'state': state.tolist(), 'zero_components': [], 'fixed_mass': None}
                    options['objective_audit']({**context, 'stage': 'PLANNED'})
                    options['objective_audit']({**context, 'stage': 'RETURNED', 'negative_two_log_likelihood': 0.})
                    if crossing == 'full': clock.now = 11.
                    return {'gradient': np.zeros(12), 'negative_two_log_likelihood': 0.}
            plan = api.plan_run(self.raw, [{'state': self.state(), 'zero_components': []}],
                resources={'case_seconds': 10, 'wall_seconds': 15}, **self.settings)
            with tempfile.TemporaryDirectory() as temp:
                path = Path(temp); api._write_new(path / 'PLAN.json', plan)
                with patch.object(api, '_model', return_value=Model()), patch.object(_run.time, 'monotonic', clock.monotonic), \
                        patch.object(solver, 'minimize', return_value={'terminal': None, 'lowest_observed': None}):
                    _run.worker(path)
                row = json.loads((path / 'case_0000.json').read_bytes())
                self.assertEqual(row['status'], 'FAILED_OR_UNRESOLVED'); self.assertEqual(row['error_type'], 'TimeoutError')
                events = [json.loads(x) for x in (path / 'ALL_OBJECTIVE_STAGES.jsonl').read_bytes().splitlines()]
                self.assertTrue(any(x['stage'] == 'RETURNED' for x in events))
                if crossing == 'full': self.assertTrue(any(x['stage'] == 'FULL_RESULT_AFTER_DEADLINE' for x in events))

    def test_final_replay_deadline_retains_computed_result_but_cannot_pass(self):
        class Clock:
            now = 0.
            def monotonic(self): return self.now
        clock = Clock()
        with tempfile.TemporaryDirectory() as temp:
            path, _ = self.prepared_workspace(temp); archive = Path(temp) / 'audit.zip'; api.export_workspace(path, archive)
            def late(*args, **kwargs):
                clock.now = 121.
                return {'verification': {'passed': True, 'scope': 'MOCK computed result'}}
            with patch.object(api.time, 'monotonic', clock.monotonic), patch.object(api, 'verify_replay', late):
                result = api.replay_export(archive, mode='numerical')
            self.assertFalse(result['verification']['passed']); self.assertTrue(result['verification']['deadline_exceeded'])
            self.assertEqual(result['outcomes'][0]['status'], 'UNKNOWN_REPLAY_DEADLINE')
            self.assertTrue(result['outcomes'][0]['verification']['verification']['passed'])

    def test_valid_foreign_registered_input_cannot_be_attached_to_another_plan(self):
        document = json.loads(self.raw); document['photometry'][0]['magnitude'] += .125
        other_raw = api._encode(document)
        registry = {'wholly_invented_sha256': [api._sha(self.raw), api._sha(other_raw)]}
        other = api.evaluate_saved_state(other_raw, self.state(), zero_components=['matern', 'sho'],
                                        **{**self.settings, 'control_registry': registry})
        self.assertTrue(api.verify_replay(other, mode='integrity')['verification']['passed'])
        with tempfile.TemporaryDirectory() as temp:
            path, _ = self.prepared_workspace(temp, registry=registry, saved=other)
            archive = Path(temp) / 'wrong-parent.zip'; api.export_workspace(path, archive)
            with self.assertRaisesRegex(ValueError, 'enclosing plan'): api.replay_export(archive)

    def test_export_refuses_verifier_expansion_or_structured_limits_before_writing(self):
        with tempfile.TemporaryDirectory() as temp:
            path, _ = self.prepared_workspace(temp)
            (path / 'ALL_OBJECTIVE_STAGES.jsonl').write_text('MOCK\n', encoding='utf-8')
            original = api._file_record
            for large in ('expanded', 'json'):
                def oversized(p):
                    record = original(p)
                    if large == 'expanded' and Path(p).name == 'ALL_OBJECTIVE_STAGES.jsonl': record['bytes'] = api.EXPANDED_LIMIT
                    if large == 'json' and Path(p).name == 'case_0000.json': record['bytes'] = api.STRUCTURE_LIMIT + 1
                    return record
                destination = Path(temp) / (large + '.zip')
                with patch.object(api, '_file_record', oversized), self.assertRaisesRegex(ValueError, 'verifier'):
                    api.export_workspace(path, destination)
                self.assertFalse(destination.exists()); self.assertTrue((path / 'PLAN.json').exists())


if __name__ == '__main__': unittest.main(verbosity=2)
