"""Prospectively frozen, invented-only BHSM claim algebra controls.

No observations, product imports, fit, likelihood, optimizer or network.
The helper is imported only after freeze/admission checks and durable log.
"""
import argparse
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import platform
import sys
import unittest
from fractions import Fraction

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
HELPER = None
CONTRACT = None
EVENTS = []
WITNESSES = []
OUTCOMES = []
EVENT_FILE = None
CURRENT = None


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tagged(value):
    """Closed builtin/Fraction evidence set; no silent NaN JSON or coercion."""
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is float:
        if math.isnan(value):
            return {'typed_float': 'NaN'}
        if math.isinf(value):
            return {'typed_float': '+Infinity' if value > 0 else '-Infinity'}
        return value
    if type(value) is Fraction:
        return {'rational_numerator': value.numerator,
                'rational_denominator': value.denominator}
    if type(value) in (tuple, list):
        return [tagged(item) for item in value]
    if type(value) is dict and all(type(key) is str for key in value):
        return {key: tagged(item) for key, item in value.items()}
    raise TypeError('Unsupported evidence type: ' + type(value).__name__)


def event(value):
    encoded = tagged(value)
    line = json.dumps(encoded, allow_nan=False, sort_keys=True) + '\n'
    EVENT_FILE.write(line)
    EVENT_FILE.flush()
    os.fsync(EVENT_FILE.fileno())
    EVENTS.append(encoded)


def call(name, *args):
    record = {'kind': 'HELPER_INVOCATION', 'control': CURRENT,
              'name': name, 'args': args}
    event({**record, 'stage': 'STARTED'})
    try:
        value = getattr(HELPER, name)(*args)
    except Exception as error:
        event({**record, 'stage': 'RAISED', 'error_type': type(error).__name__,
               'error': str(error)})
        raise
    event({**record, 'stage': 'RETURNED', 'output': value})
    return value


def witness(value):
    record = {'kind': 'INDEPENDENT_IDEAL_WITNESS', 'control': CURRENT,
              'payload': value}
    event(record)
    WITNESSES.append(tagged(record))


class ClaimControls(unittest.TestCase):
    def setUp(self):
        global CURRENT
        CURRENT = self._testMethodName
        event({'kind': 'CONTROL_STARTED', 'control': CURRENT})

    def near(self, actual, expected, tolerance=2e-12):
        self.assertLessEqual(abs(actual-expected),
                             tolerance*max(1.0, abs(expected)))

    def test_01_monopole(self):
        for r1, r2 in ((1.0, 3.0), (1.25, 7.5), (2.0, 11.0)):
            result = call('annular_contrast', r1, r2, 6/r1, 6/r2)
            self.near(result['contrast'], 0)

    def test_02_disk_interior(self):
        # Mtot=16,Rsupport=4 -> M(<R)=R^2, alpha=M(<R)/R=R.
        result = call('annular_contrast', 1, 2, 1, 2)
        witness({'independent_enclosed_masses': [1, 4],
                 'enclosed_ratio': Fraction(4), 'contrast_expected': 3})
        self.assertEqual(result['contrast'], 3)

    def test_03_finite_support_counterexample(self):
        r1, r2, total, support = 5, 8, 16, 4
        self.assertGreater(r1, support)
        disk = [total/r1, total/r2]
        point = [total/r1, total/r2]
        witness({'ordinary_disk_support': support, 'radii': [r1, r2],
                 'disk_bending': disk, 'point_bending': point,
                 'unique_BH_identity': False})
        self.assertEqual(disk, point)
        self.assertEqual(call('annular_contrast', r1, r2, *disk)['contrast'], 0)

    def test_04_central_mass_cancels(self):
        for central in (0, 3, 15):
            # Inside the same normalized disk: M(<R)=central+R^2.
            a1, a2 = (central+1), (central+4)/2
            result = call('annular_contrast', 1, 2, a1, a2)
            witness({'central_mass': central, 'annular_mass_expected': 3})
            self.assertEqual(result['contrast'], 3)

    def test_05_negative_retained(self):
        result = call('annular_contrast', 1, 2, 3, 1)
        self.assertEqual(result['contrast'], -1)
        self.assertIsNone(result['classification'])
        self.assertIsNone(result['uncertainty'])

    def test_06_gradient(self):
        values = [1.5, 4.0, .7, .4]
        result = call('annular_contrast', *values)
        differences = []
        step = 1e-5
        # Reference differences use the raw product expression, not helper.
        for index in range(4):
            plus, minus = list(values), list(values)
            plus[index] += step
            minus[index] -= step
            fp = plus[1]*plus[3]-plus[0]*plus[2]
            fm = minus[1]*minus[3]-minus[0]*minus[2]
            differences.append((fp-fm)/(2*step))
        witness({'raw_expression_central_difference': differences,
                 'helper_gradient': result['gradient'], 'step': step})
        for actual, reference in zip(result['gradient'], differences):
            self.assertLessEqual(abs(actual-reference), 1e-9)

    def test_07_boundary_inverse(self):
        for radius in (3, 10, 100):
            deficit = call('principal_reference_deficit', 1, radius)
            inverse = radius**2*deficit-radius**3*deficit**2/2
            witness({'m': 1, 'radius': radius, 'deficit': deficit,
                     'independent_inverse': inverse})
            self.assertGreater(deficit, 0)
            self.near(inverse, 1, 1e-12)

    def test_08_radius_and_intrinsic_curvature(self):
        deficits = [call('principal_reference_deficit', 1, radius)
                    for radius in (10, 20)]
        witness({'radii': [10, 20], 'same_m': 1, 'deficits': deficits,
                 'intrinsic_curvatures': [1/100, 1/400]})
        self.assertNotEqual(*deficits)
        for radius, deficit in zip((10, 20), deficits):
            self.assertGreater(abs(deficit-1/radius**2), 1e-8)
            self.near(radius**2*deficit-radius**3*deficit**2/2, 1)

    def test_09_mass_sheet(self):
        for u in (.4, 1.3, 2.0):
            xplus = (u+math.sqrt(u*u+4))/2
            images = [xplus, -1/xplus]
            for lam in (.6, .8):
                old_dets, new_dets, old_phi, new_phi = [], [], [], []
                residuals = []
                for x in images:
                    # psi0=ln|x|; full 2D radial/tangential Hessian eigenvalues.
                    radius = abs(x)
                    old = (1+1/radius**2)*(1-1/radius**2)
                    new = (1-(-lam/radius**2+1-lam))*(
                        1-(lam/radius**2+1-lam))
                    old_dets.append(old)
                    new_dets.append(new)
                    transformed_gradient = lam/x+(1-lam)*x
                    residuals.append(x-transformed_gradient-lam*u)
                    old_phi.append(.5*(x-u)**2-math.log(radius))
                    new_phi.append(.5*(x-lam*u)**2-
                                   lam*math.log(radius)-(1-lam)*x*x/2)
                old_ratio = abs(old_dets[1]/old_dets[0])
                new_ratio = abs(new_dets[1]/new_dets[0])
                old_delay = old_phi[1]-old_phi[0]
                new_delay = new_phi[1]-new_phi[0]
                witness({'u': u, 'lambda': lam, 'same_images': images,
                         'transformed_lens_residuals': residuals,
                         'old_determinants': old_dets,
                         'new_determinants': new_dets,
                         'flux_ratios': [old_ratio, new_ratio],
                         'fermat_differences': [old_delay, new_delay]})
                for residual in residuals:
                    self.near(residual, 0)
                self.near(old_ratio, new_ratio)
                self.near(new_delay, lam*old_delay)
                self.assertGreater(abs(new_delay-old_delay), 1e-3)

    def test_10_stf_oddness(self):
        for transverse in ((Fraction(1), Fraction(2)),
                           (Fraction(3, 2), Fraction(-1, 2))):
            x, y = transverse
            for z in (Fraction(1, 4), Fraction(2), Fraction(7)):
                r2 = x*x+y*y+z*z
                row = [2*x*z/r2**2, 2*y*z/r2**2]
                opposite = [-2*x*z/r2**2, -2*y*z/r2**2]
                sums = [a+b for a, b in zip(row, opposite)]
                witness({'x_y_z': [x, y, z], 'radial_factor': 1/r2**2,
                         'cross_terms': row, 'opposite': opposite,
                         'paired_projection': sums})
                self.assertEqual(sums, [0, 0])

    def test_11_radial_rank(self):
        xs = [Fraction(1), Fraction(4), Fraction(9)]
        matrix = [[Fraction(1), 1/x, x] for x in xs]
        a, b, c = matrix
        determinant = (a[0]*(b[1]*c[2]-b[2]*c[1])-
                       a[1]*(b[0]*c[2]-b[2]*c[0])+
                       a[2]*(b[0]*c[1]-b[1]*c[0]))
        closed = -((xs[1]-xs[0])*(xs[2]-xs[0])*(xs[2]-xs[1]))/(
            xs[0]*xs[1]*xs[2])
        null_vector = [Fraction(-5), Fraction(4), Fraction(1)]
        values = [sum(entry*coef for entry, coef in zip(row, null_vector))
                  for row in matrix]
        witness({'squared_radii': xs, 'matrix': matrix,
                 'independent_determinant': determinant,
                 'closed_determinant': closed, 'two_radius_null': null_vector,
                 'values': values})
        self.assertEqual(determinant, Fraction(-10, 3))
        self.assertEqual(determinant, closed)
        self.assertEqual(values, [0, 0, Fraction(40, 9)])

    def test_12_ideal_slip(self):
        for slip in (0, .5, 1):
            alpha = (1+slip)*math.pi*.01**2
            residual = call('ideal_slip_residual', alpha, .01, 1, slip)
            rescaled = call('ideal_slip_residual', alpha, 3, 300, slip)
            self.near(residual, 0, 1e-12)
            self.near(rescaled, residual, 1e-12)
        mismatched = call('ideal_slip_residual', 2*math.pi*.01**2, .01, 1, 0)
        self.near(mismatched, 1)

    def test_13_duration_nonidentification(self):
        theta, motion, mass, relative_parallax = map(Fraction, (3, 2, 9, 1))
        for scale in (Fraction(1, 2), Fraction(2), Fraction(3)):
            scaled_theta, scaled_motion, scaled_mass = (
                scale*theta, scale*motion, scale**2*mass)
            witness({'scale': scale, 'theta': scaled_theta,
                     'relative_motion': scaled_motion, 'mass': scaled_mass,
                     'relative_parallax': relative_parallax,
                     'same_tE': scaled_theta/scaled_motion})
            self.assertEqual(scaled_theta/scaled_motion, theta/motion)
            self.assertEqual(scaled_theta**2/scaled_mass, theta**2/mass)

    def test_14_refusals(self):
        cases = [
            ('annular_contrast', (True, 2, 1, 1)),
            ('annular_contrast', (float('nan'), 2, 1, 1)),
            ('annular_contrast', (1, float('inf'), 1, 1)),
            ('annular_contrast', (0, 2, 1, 1)),
            ('annular_contrast', (2, 1, 1, 1)),
            ('annular_contrast', (1, 1, 1, 1)),
            ('annular_contrast', (1, 2, -1, 1)),
            ('annular_contrast', (1, 2, 0, 1)),
            ('annular_contrast', (1e308, 1.1e308, 1e308, 1e308)),
            ('annular_contrast', (1e-300, 2e-300, 1e-300, 1e-300)),
            ('principal_reference_deficit', (1, 2)),
            ('principal_reference_deficit', (1, 1)),
            ('principal_reference_deficit', (True, 10)),
            ('principal_reference_deficit', (-1, 10)),
            ('principal_reference_deficit', (1e-300, 1e300)),
            ('ideal_slip_residual', (1, 1e-300, 1e300, 1)),
            ('ideal_slip_residual', (1, 1, 0, 1)),
            ('ideal_slip_residual', (1, 1, 2, float('inf'))),
        ]
        for name, args in cases:
            with self.assertRaises(ValueError):
                call(name, *args)

    def test_15_eight_branches(self):
        literal = [
            ('GO-', 'StellarIMF', 'Near', '0.47', '7.2'),
            ('GO-', 'StellarIMF', 'Far', '0.53', '0.94'),
            ('GO-', 'DarkIMF', 'Near', '0.96', '11.1'),
            ('GO-', 'DarkIMF', 'Far', '0.04', '1.11'),
            ('GO+', 'StellarIMF', 'Near', '0.94', '2.8'),
            ('GO+', 'StellarIMF', 'Far', '0.06', '0.4'),
            ('GO+', 'DarkIMF', 'Near', '0.999', '4.9'),
            ('GO+', 'DarkIMF', 'Far', '0.001', '0.59'),
        ]
        rows = CONTRACT['candidate_context']['all_eight_literature_branches']
        self.assertEqual(len(rows), 8)
        pairs = {}
        for row, expected in zip(rows, literal):
            mode, prior, branch, weight, mass = expected
            self.assertEqual((row['photometric_mode'], row['mass_prior'],
                              row['branch']), (mode, prior, branch))
            self.assertEqual(Fraction(str(row['published_branch_weight'])),
                             Fraction(weight))
            self.assertEqual(Fraction(str(row['published_mass_posterior_median_msun'])),
                             Fraction(mass))
            pairs[mode, prior] = pairs.get((mode, prior), Fraction(0))+Fraction(weight)
        witness({'literal_primary_table_references': literal,
                 'all_contract_branches': rows,
                 'within_pair_weight_sums': [list(key)+[value]
                                             for key, value in pairs.items()]})
        self.assertEqual(list(pairs.values()), [1, 1, 1, 1])

    def test_16_status_contract(self):
        claims = CONTRACT['claims']
        self.assertEqual([row['claim_id'] for row in claims],
                         ['C'+str(i) for i in range(7)])
        for claim in claims:
            for key in ('statement', 'domain', 'nuisance', 'falsifier',
                        'minimum_extra_evidence', 'does_not_identify'):
                self.assertTrue(claim[key])
        candidate = CONTRACT['candidate_context']
        self.assertEqual(candidate['novelty_status'],
                         'PREVIOUSLY_PUBLISHED_CANDIDATE_NOT_A_NEW_ENGINE_DISCOVERY')
        self.assertTrue(all(value is None for value in candidate['engine_measurements'].values()))
        self.assertFalse(CONTRACT['known_positive_reference']['independent_engine_recovery_accepted'])
        self.assertFalse(CONTRACT['non_BH_comparison']['independently_recovered_by_this_engine'])
        self.assertFalse(CONTRACT['publication_ready'])
        self.assertFalse(CONTRACT['new_boundary_law_derived'])
        witness({'claim_count': len(claims), 'candidate_context': candidate,
                 'positive_reference': CONTRACT['known_positive_reference'],
                 'non_BH_comparison': CONTRACT['non_BH_comparison'],
                 'new_boundary_law_derived': False, 'publication_ready': False})


class RecordingResult(unittest.TextTestResult):
    def _outcome(self, test, status, error=None):
        row = {'control': test._testMethodName, 'status': status, 'error': error}
        OUTCOMES.append(row)
        event({'kind': 'CONTROL_TERMINAL', **row})

    def addSuccess(self, test):
        super().addSuccess(test)
        self._outcome(test, 'PASS')

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._outcome(test, 'FAIL', self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        self._outcome(test, 'ERROR', self._exc_info_to_string(err, test))


def main():
    global HELPER, CONTRACT, EVENT_FILE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--freeze', required=True)
    parser.add_argument('--freeze-sha256', required=True)
    parser.add_argument('--admission-file', required=True)
    parser.add_argument('--admission-sha256', required=True)
    parser.add_argument('--root-execution-admitted', action='store_true')
    args = parser.parse_args()
    if not args.root_execution_admitted:
        raise ValueError('Exact source-reviewed root execution admission required')
    if sha(args.freeze) != args.freeze_sha256:
        raise ValueError('Freeze mismatch')
    if sha(args.admission_file) != args.admission_sha256:
        raise ValueError('Admission evidence mismatch')
    admission = json.loads(Path(args.admission_file).read_text(encoding='utf-8'))
    if admission.get('execution_admitted') is not True:
        raise ValueError('Admission must explicitly record execution_admitted=true')
    freeze = json.loads(Path(args.freeze).read_text(encoding='utf-8'))
    if admission.get('freeze_sha256') != args.freeze_sha256:
        raise ValueError('Admission must bind this exact prospective freeze')
    before = {}
    for record in freeze['files']:
        path = record['path']
        digest = sha(path)
        if digest != record['sha256'] or Path(path).stat().st_size != record['bytes']:
            raise ValueError('Frozen file mismatch: '+path)
        before[path] = digest
    if str(Path(__file__).resolve()) not in before:
        raise ValueError('Driver itself must be frozen')
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    log_path = out/'FULL_IDEAL_CONTROL_EVENTS_v1.jsonl'
    with log_path.open('x', encoding='utf-8', newline='\n') as log:
        EVENT_FILE = log
        event({'kind': 'ADMISSION_AND_PREFLIGHT', 'admission': admission,
               'freeze_sha256': args.freeze_sha256, 'source_hashes_before': before,
               'python': sys.version, 'executable': sys.executable})
        helper_path = HERE/'ideal_claim_diagnostics_v1.py'
        spec = importlib.util.spec_from_file_location('ideal_claim_diagnostics_v1', helper_path)
        HELPER = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(HELPER)
        CONTRACT = json.loads((HERE/'CLAIM_CONTRACT_v1.json').read_text(encoding='utf-8'))
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(ClaimControls)
        stream = io.StringIO()
        result = unittest.TextTestRunner(stream=stream, verbosity=2,
                                        resultclass=RecordingResult).run(suite)
        text_log = stream.getvalue()
        with (out/'IDEAL_CONTROL_OUTCOMES_v1.log').open('x', encoding='utf-8') as handle:
            handle.write(text_log)
            handle.flush()
            os.fsync(handle.fileno())
        after = {path: sha(path) for path in before}
        status = ('PASS_INVENTED_ALGEBRA_ONLY' if result.wasSuccessful() and
                  result.testsRun == 16 and before == after else 'FAILED_OR_INCOMPLETE')
        event({'kind': 'CAMPAIGN_TERMINAL', 'status': status,
               'tests_run': result.testsRun, 'source_hashes_after': after})
    receipt = {'schema': 'bhsm.claim_dossier.ideal_controls.v1', 'status': status,
               'python': platform.python_version(), 'executable': sys.executable,
               'freeze_sha256': args.freeze_sha256,
               'admission_sha256': args.admission_sha256,
               'source_hashes_before': before, 'source_hashes_after': after,
               'controls': OUTCOMES, 'witnesses': WITNESSES, 'events': EVENTS,
               'test_count': result.testsRun, 'failures': len(result.failures),
               'errors': len(result.errors), 'event_log_sha256': sha(log_path),
               'outcome_log_sha256': sha(out/'IDEAL_CONTROL_OUTCOMES_v1.log'),
               'native_calls': 0, 'likelihood_calls': 0, 'fit_calls': 0,
               'probability_calls': 0, 'downloads': 0,
               'accepted_BH_or_new_native_result': False,
               'publication_hold_cleared': False}
    encoded = json.dumps(tagged(receipt), allow_nan=False, indent=2)+'\n'
    with (out/'COMPLETE_IDEAL_CLAIM_CONTROLS_v1.json').open('x', encoding='utf-8') as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    print(json.dumps({'status': status, 'controls': result.testsRun,
                      'failures': len(result.failures), 'errors': len(result.errors),
                      'output': str(out)}))
    return 0 if status == 'PASS_INVENTED_ALGEBRA_ONLY' else 1


if __name__ == '__main__':
    raise SystemExit(main())
