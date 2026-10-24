"""Wholly invented small-cadence control; never reads authentic observations."""
import argparse
import json
from pathlib import Path
import numpy as np
from known2023_student_model_v1 import load_source, CORE_SHA, KAPPA, YEAR, MAG, packed, sha

def build(core_path, output):
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    core = load_source(core_path, CORE_SHA, '_bhsm_fixture_core_' + CORE_SHA[:12])
    rng = np.random.default_rng(2026102401)
    t0, reference = 2455765., 2456000.
    p = {'t0_jd_tdb': t0, 'tE_days': 140., 'u0_heliocentric': .23, 'angle_source_minus_lens_rad': .8, 'pi_E': .17}
    ra, dec = 39., -20.
    tp = t0 + np.linspace(-600., 700., 144)
    seeing = 5. + 1.3 * np.sin(np.arange(len(tp)) * .43)
    zseeing = np.clip((seeing - 5.) / 2., -1., 1.)
    ep = core.earth_heliocentric_ne(tp, ra, dec)
    amp = core.amplification(core.trajectory(tp, p, ep))
    mean = 18.1 - MAG * np.log1p(.35 * (amp - 1))
    years = np.floor((tp - 2451545.) / YEAR).astype(int) + 2000
    seasons = sorted(set(map(int, years)))
    alpha = [.05 * np.sin(j + .5) for j in range(len(seasons))]
    idx = np.array([seasons.index(int(y)) for y in years])
    marginal = .03 * np.exp(np.asarray(alpha)[idx] + .04 * np.clip((mean - 16.5) / 2., -1., 1.) - .03 * zseeing)
    corr = .2 * np.exp(-np.abs(tp[:, None] - tp[None, :]) / 2.7) + .8 * np.eye(len(tp))
    unit_student = rng.standard_t(6, len(tp)) * np.sqrt(4 / 6)
    observed = mean + .007 * zseeing + marginal * (np.linalg.cholesky(corr) @ unit_student)
    photo = [{'source_row_id': f'INVENTED:OGLE:{i:04d}', 'time_jd_tdb': float(t), 'magnitude': float(y), 'magnitude_error': .03, 'seeing_pixels': float(s), 'instrument': 'OGLE'} for i, (t, y, s) in enumerate(zip(tp, observed, seeing))]
    for filt, baseline, fraction in [('F606W', 20.1, .92), ('F814W', 18.6, .9)]:
        for j, time in enumerate(t0 + np.array([-10., 80., 300., 900.])):
            earth = core.earth_heliocentric_ne([time], ra, dec)
            a = core.amplification(core.trajectory([time], p, earth))[0]
            y = baseline - MAG * np.log1p(fraction * (a - 1)) + .04 * rng.normal()
            photo.append({'source_row_id': f'INVENTED:HST_PHOT:{filt}:{j:02d}', 'time_jd_tdb': float(time), 'magnitude': float(y), 'magnitude_error': .04, 'instrument': 'HST_' + filt})
    astro = []
    eref = core.earth_heliocentric_ne([reference], ra, dec)[0]
    for j, time in enumerate(t0 + np.linspace(-90., 1400., 12)):
        for filt in ('F606W', 'F814W'):
            ts = np.array([time - .001, time + .001])
            e = core.earth_heliocentric_ne(ts, ra, dec)
            unit = core.centroid_unit(core.trajectory(ts, p, e)).mean(axis=0)
            mu = 2.4 * unit + np.array([8., -4.]) + np.array([.7, -.4]) * (time - reference) / YEAR - .05 * (e - eref).mean(axis=0)
            if filt == 'F814W':
                mu += np.array([.1, -.08])
            y = mu + rng.normal(size=2) * np.array([.05, .06])
            astro.append({'source_row_id': f'INVENTED:ASTRO:{j:02d}:{filt}', 'visit_id': f'INVENTED_VISIT_{j:02d}', 'filter': filt, 'exposure_midpoints_jd_tdb': ts.tolist(), 'north_mas': float(y[0]), 'east_mas': float(y[1]), 'north_error_mas': .05, 'east_error_mas': .06})
    document = {'schema': 'bhtracker.native_joint_mass.v1', 'data_version': 'SYNTHETIC_KNOWN2023_ST6_CONTROL_v1', 'simulation_only': True, 'target': 'WHOLLY_INVENTED_NO_AUTHENTIC_DATA_OR_CADENCE', 'time_coordinate': 'JD_TDB', 'reference_jd_tdb': reference, 'ra_deg': ra, 'dec_deg': dec, 'native_files': {}, 'photometry': photo, 'astrometry': astro}
    truth = {'p': p, 'theta_E_mas': 2.4, 'conditional_generating_mass_msun': 2.4 / (KAPPA * .17), 'season_logscales': alpha, 'seasons': seasons, 'OGLE_scale_brightness_slope': .04, 'OGLE_scale_seeing_slope': -.03, 'OGLE_fraction': .2, 'OGLE_tau_days': 2.7, 'OGLE_seeing_mean_slope_mag': .007, 'instruments': {'OGLE': [18.1, .35], 'HST_F606W': [20.1, .92], 'HST_F814W': [18.6, .9]}, 'reference_jd_tdb': reference, 'native_observations_or_cadence_loaded': False, 'seed': 2026102401}
    output.mkdir()
    raw = (json.dumps(document, indent=2, allow_nan=False) + '\n').encode()
    (output / 'INVENTED_DATASET_v1.json').write_bytes(raw)
    (output / 'INVENTED_TRUTH_v1.json').write_text(json.dumps(truth, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    (output / 'CONTROL_REGISTRY_v1.json').write_text(json.dumps({'wholly_invented_sha256': [sha(raw)]}, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'dataset_sha256': sha(raw), 'rows': [len(photo), len(astro)], 'authentic_data_or_cadence_loaded': False}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core-path', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.core_path, args.output)
