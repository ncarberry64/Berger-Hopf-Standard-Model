"""Prospectively declared non-BH simulation at unchanged2023 observation support.

No authentic values enter the generator. This is not a native-data fit. The CLI
requires a separate exact source/input freeze and root generation admission.
"""
import argparse
import base64
import hashlib
import json
import math
from pathlib import Path
import sys

NATIVE_SHA = 'd2409db410e113872781494ca4d73db57d2a44fd65146c4e7ec2f40828448428'
SEED = 2026102402

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def checked_generation_configuration(freeze, runtime):
    if freeze.get('purpose') != 'ACTUAL_CADENCE_GENERATION' or type(freeze.get('random_seed')) is not int or freeze['random_seed'] != SEED:
        raise ValueError('Exact frozen generation purpose and declared integer seed required')
    if runtime != freeze.get('runtime'):
        raise ValueError('Generation runtime differs from exact reviewed environment')
    return {'runtime': dict(runtime), 'purpose': freeze['purpose'], 'random_seed': SEED}

def chronological_cholesky_apply(times, innovations, fraction, tau):
    """Apply exact OU-plus-white Cholesky law in O(N), without drawing Gaussian noise.

    Kalman innovations factor the covariance; only the *factor* is borrowed
    from the Gaussian covariance identity. The supplied innovations are Student.
    This does not turn the resulting law into Gaussian or elliptical Student.
    """
    import numpy as np
    t, z = np.asarray(times, dtype=float), np.asarray(innovations, dtype=float)
    if t.ndim != 1 or z.shape != t.shape or not np.isfinite(t).all() or not np.isfinite(z).all() or np.any(np.diff(t) < 0):
        raise ValueError('Finite chronological one-dimensional times/innovations required')
    if isinstance(fraction, bool) or isinstance(tau, bool) or not 0 <= fraction < 1 or not math.isfinite(tau) or tau <= 0:
        raise ValueError('Finite fraction in[0,1) and positive tau required')
    root = math.sqrt(fraction)
    state, variance = 0., 1.
    result = np.empty(len(t))
    for i in range(len(t)):
        if i:
            rho = math.exp(-(t[i] - t[i-1]) / tau)
            state *= rho
            variance = -math.expm1(-2 * (t[i] - t[i-1]) / tau) + rho * rho * variance
        innovation_variance = fraction * variance + 1 - fraction
        innovation = math.sqrt(innovation_variance) * z[i]
        result[i] = root * state + innovation
        gain = root * variance / innovation_variance
        state += gain * innovation
        variance *= (1 - fraction) / innovation_variance
    if not np.isfinite(result).all():
        raise FloatingPointError('Unrepresentable generated observation')
    return result

def generate(parent_raw, core_path):
    """One admitted call; original bytes embedded intact, values in new namespace."""
    import numpy as np
    from known2023_student_model_v1 import load_source, CORE_SHA, KAPPA, MAG, YEAR
    if sha(parent_raw) != NATIVE_SHA:
        raise ValueError('Only the frozen2023 parent is supported')
    parent = json.loads(parent_raw.decode('utf-8'))
    core = load_source(core_path, CORE_SHA, '_bhsm_cadence_generation_core_' + CORE_SHA[:12])
    rng = np.random.default_rng(SEED)
    photo, angular = parent['photometry'], parent['astrometry']
    p = {'t0_jd_tdb': 2455765., 'tE_days': 140., 'u0_heliocentric': .23,
         'angle_source_minus_lens_rad': .8, 'pi_E': .17}
    reference, theta = 2456000., 2.4
    instruments = {'OGLE': (18.1, .35), 'HST_F606W': (20.1, .92), 'HST_F814W': (18.6, .9)}
    times = np.array([r['time_jd_tdb'] for r in photo], dtype=float)
    errors = np.array([r['magnitude_error'] for r in photo], dtype=float)
    if not np.isfinite(errors).all() or np.any(errors <= 0):
        raise ValueError('Positive supplied error support required')
    earth = core.earth_heliocentric_ne(times, parent['ra_deg'], parent['dec_deg'])
    amplitude = core.amplification(core.trajectory(times, p, earth))
    means = np.empty(len(photo))
    for i, row in enumerate(photo):
        baseline, fraction = instruments[row['instrument']]
        means[i] = baseline - MAG * np.log1p(fraction * (amplitude[i] - 1))
    ogle = np.array([i for i, r in enumerate(photo) if r['instrument'] == 'OGLE'], dtype=int)
    order = ogle[np.argsort(times[ogle], kind='stable')]
    years = np.floor((times[order] - 2451545.) / YEAR).astype(int) + 2000
    seasons = sorted(set(map(int, years)))
    alpha = [.05 * math.sin(j + .5) for j in range(len(seasons))]
    seeing = np.array([photo[i]['seeing_pixels'] for i in order], dtype=float)
    zs = np.clip((seeing - 5) / 2, -1, 1)
    scale = errors[order] * np.exp(np.array([alpha[seasons.index(int(y))] for y in years]) + .04 * np.clip((means[order]-16.5)/2, -1, 1) - .03*zs)
    innovations = rng.standard_t(6, len(order)) * math.sqrt(4/6)
    observed = np.empty(len(photo))
    observed[order] = means[order] + .007*zs + scale*chronological_cholesky_apply(times[order], innovations, .2, 2.7)
    others = np.array([i for i, r in enumerate(photo) if r['instrument'] != 'OGLE'], dtype=int)
    observed[others] = means[others] + errors[others]*rng.normal(size=len(others))
    eref = core.earth_heliocentric_ne([reference], parent['ra_deg'], parent['dec_deg'])[0]
    generated_angular = []
    for row in angular:
        ts = np.array(row['exposure_midpoints_jd_tdb'], dtype=float)
        e = core.earth_heliocentric_ne(ts, parent['ra_deg'], parent['dec_deg'])
        unit = core.centroid_unit(core.trajectory(ts, p, e)).mean(axis=0)
        mu = theta*unit + np.array([8.,-4.]) + np.array([.7,-.4])*(ts.mean()-reference)/YEAR - .05*(e-eref).mean(axis=0)
        if row['filter'] == 'F814W':
            mu += np.array([.1,-.08])
        sigma = np.array([row['north_error_mas'], row['east_error_mas']], dtype=float)
        if not np.isfinite(sigma).all() or np.any(sigma <= 0):
            raise ValueError('Positive genuine angular error support required')
        value = mu + sigma*rng.normal(size=2)
        generated_angular.append({'parent_source_row_id': row['source_row_id'], 'generated_north_mas': float(value[0]), 'generated_east_mas': float(value[1])})
    daughter = {'schema': 'bhsm.known2023.generated_control.v1', 'simulation_only': True,
        'scope': 'CONDITIONAL_SIMULATION_AT_AUTHENTIC_CADENCE', 'parent_native_sha256': NATIVE_SHA,
        'parent_native_bytes_base64': base64.b64encode(parent_raw).decode('ascii'),
        'generated_photometry': [{'parent_source_row_id': r['source_row_id'], 'generated_magnitude': float(y)} for r,y in zip(photo,observed)],
        'generated_astrometry': generated_angular}
    truth = {'purpose': 'GENERIC_NON_BH_CONTROL_NOT_LITERATURE_BH_TRUTH', 'random_seed': SEED,
        'geometry': p, 'theta_E_mas': theta, 'generating_mass_msun': theta/(KAPPA*p['pi_E']),
        'instruments': instruments, 'source_position_NE_mas_at_reference': [8.,-4.],
        'relative_source_motion_NE_mas_per_year': [.7,-.4], 'relative_source_parallax_mas': .05,
        'F814W_offset_NE_mas': [.1,-.08], 'reference_jd_tdb': reference, 'seasons': seasons,
        'season_logscale': alpha, 'brightness_scale_slope': .04, 'seeing_scale_slope': -.03,
        'OGLE_fraction': .2, 'OGLE_tau_days': 2.7, 'seeing_mean_slope_mag': .007,
        'original_observed_values_used_for_generation': False,
        'parent_support_and_errors_used': True, 'equal_exposure_weights_are_assumed': True}
    return daughter, truth

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', type=Path, required=True)
    parser.add_argument('--freeze-sha256', required=True)
    parser.add_argument('--admission', type=Path, required=True)
    parser.add_argument('--admission-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.freeze.read_bytes()
    if sha(raw) != args.freeze_sha256:
        raise ValueError('Generation freeze differs')
    freeze = json.loads(raw.decode('utf-8'))
    admission_raw = args.admission.read_bytes()
    admission = json.loads(admission_raw.decode('utf-8'))
    if sha(admission_raw) != args.admission_sha256 or admission.get('schema') != 'bhsm.known2023.cadence_generation_admission.v1' or admission.get('execution_admitted') is not True or admission.get('prospective_freeze_sha256') != args.freeze_sha256:
        raise ValueError('Separate root admission required for exact generation')
    for pin in freeze['source_files']:
        data = Path(pin['path']).read_bytes()
        if len(data) != pin['bytes'] or sha(data) != pin['sha256']:
            raise ValueError('Source pin differs')
    import numpy
    import scipy
    import astropy
    actual_runtime = {'python':sys.version.split()[0], 'numpy':numpy.__version__, 'scipy':scipy.__version__, 'astropy':astropy.__version__}
    checked_generation_configuration(freeze, actual_runtime)  # Before every forward call or random draw.
    parent_raw = Path(freeze['input']['path']).read_bytes()
    if sha(parent_raw) != NATIVE_SHA or sha(parent_raw) != freeze['input']['sha256']:
        raise ValueError('Frozen parent changed')
    args.output.mkdir(exist_ok=False)
    daughter, truth = generate(parent_raw, freeze['core_path'])
    daughter_raw = (json.dumps(daughter, indent=2, allow_nan=False)+'\n').encode('utf-8')
    outputs = {'GENERATED_DATASET_v1.json': daughter_raw,
        'GENERATING_TRUTH_v1.json': (json.dumps(truth,indent=2,allow_nan=False)+'\n').encode(),
        'CONTROL_REGISTRY_v1.json': (json.dumps({'actual_cadence_sha256':[sha(daughter_raw)]},indent=2)+'\n').encode()}
    for name, data in outputs.items():
        with (args.output/name).open('xb') as stream:
            stream.write(data)
    after = []
    for pin in freeze['source_files'] + [freeze['input']]:
        data = Path(pin['path']).read_bytes()
        after.append({'path':pin['path'],'unchanged':len(data)==pin['bytes'] and sha(data)==pin['sha256']})
    receipt = {'schema':'bhsm.known2023.cadence_generation_receipt.v1', 'prospective_freeze_sha256':args.freeze_sha256,
        'actual_runtime': actual_runtime, 'declared_random_seed': SEED, 'purpose': freeze['purpose'],
        'output_files': {name:{'bytes':len(data),'sha256':sha(data)} for name,data in outputs.items()},
        'generated_photometric_rows':len(daughter['generated_photometry']),
        'generated_angular_rows':len(daughter['generated_astrometry']), 'source_integrity':after,
        'passed':all(p['unchanged'] for p in after), 'native_likelihood_or_fitter_calls':0,
        'native_observations_modified':False, 'accepted_known_bh_recovery':False}
    (args.output/'GENERATION_RECEIPT_v1.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt))
    return 0 if receipt['passed'] else 1

if __name__ == '__main__':
    sys.exit(main())
