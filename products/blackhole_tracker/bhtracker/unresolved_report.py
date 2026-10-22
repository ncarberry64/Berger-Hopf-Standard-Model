"""Native-observation exports; no resolved observables or mass are invented."""
from pathlib import Path
import csv
import hashlib
import html
import json
import numpy as np

from .provenance import REPOSITORY_URL, project_citation

BUNDLE_SCHEMA = 'bhtracker.unresolved_analysis_bundle.v1'


def is_unresolved_result(result):
    return result.get('schema') == 'bhsm_unresolved_photometry_result/1'


def report_html(result):
    """A standalone report that separates model fit, adequacy and identification."""
    escape = lambda value: html.escape(str(value))
    def fmt(value):
        if value is None:
            return 'unavailable / unresolved'
        if isinstance(value, (float, int)):
            return f'{value:.8g}'
        return escape(value)
    parameters = result['parameters']
    errors = result['uncertainty']['standard_errors']
    quantities = [('Peak time (native relative HJD days)', parameters['t0'], errors.get('t0')),
                  ('Einstein crossing timescale (days)', parameters['tE_days'], errors.get('tE_days')),
                  ('Dimensionless impact parameter', parameters['u0'], errors.get('u0')),
                  ('Lens mass', None, None), ('Lens distance', None, None),
                  ('Absolute angular proper motion', None, None)]
    table = ''.join(f'<tr><th>{label}</th><td>{fmt(value)}</td><td>{fmt(error)}</td></tr>'
                    for label, value, error in quantities)
    meaning = result['bhsm_interpretation']
    diagnostic = escape(json.dumps(result['diagnostics'], indent=2, allow_nan=False))
    timing = escape(json.dumps(result['dataset_input']['instruments'], indent=2, allow_nan=False))
    return f'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width"><title>BHSM unresolved photometry report</title>
<style>body{{font:16px/1.55 system-ui;max-width:1050px;margin:2rem auto;padding:0 1rem;color:#172b40}}table{{border-collapse:collapse;width:100%}}th,td{{padding:.6rem;border-bottom:1px solid #ccd6df;text-align:left}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#f0f4f7;padding:1rem}}.status{{padding:1rem;border-left:4px solid #137c94;background:#eef7fa}}</style>
<h1>BHSM Blackhole Tracker · unresolved photometry</h1>
<p class="status">{escape(result['status'])} · MASS_UNRESOLVED</p>
<p>Project and reviewer record: <a href="{REPOSITORY_URL}">BHSM GitHub repository</a>.</p>
<p>All {result['point_count']} native magnitude observations were used; {result['excluded_point_count']} numeric observations excluded. The separate source annotations remain in the input provenance.</p>
<table><tr><th>Quantity</th><th>Estimate</th><th>Conditional local 1σ</th></tr>{table}</table>
<p>Time is represented relative to the explicitly recorded numeric origin {fmt(parameters['time_numeric_origin_jd'])}. An origin shift is not a clock-scale or heliocentric conversion. Native times and row identities remain in the observation file.</p>
<h2>What is and is not identified</h2><p>tE = θE / μrel and θE² = κ M πrel. This light-curve route does not measure θE or microlens parallax, so duration does not supply a mass. It does not identify a black hole or horizon.</p>
<p>{escape(result['uncertainty']['qualification'])}</p>
<pre>{escape(json.dumps(result['timescale_uncertainty'], indent=2))}</pre>
<h2>BHSM interpretation</h2><p>{escape(meaning['one_potential_rule'])}</p>
<p>The unresolved brightness is the sum of the images of one effective optical configuration. Its BHSM interpretation counts that optical response once. This fit does not select a core state, boundary deformation, membrane radius, transition rate or conditional R1 state.</p>
<h2>Fit and residual checks</h2><pre>{diagnostic}</pre>
<h2>Timing, calibration and noise assumptions</h2><pre>{timing}</pre>
<p>Published magnitude errors are retained. Independent diagonal Gaussian noise is an analysis assumption, not a supplied full covariance. Correlated/seasonal residuals and active bounds qualify uncertainty and model adequacy. Equal-instrument weights or a signed calibration blend, when requested, are sensitivities rather than recovered physical lens properties.</p>
<h2>Reproduction</h2><pre>{escape(json.dumps(result['analysis_configuration'], indent=2))}</pre>
<p>Product {escape(result['product_version'])}; protocol {escape(result['protocol_sha256'])}; input {escape(result['input_sha256'])}.</p></html>'''


def export_result(result, directory):
    from .observations import UnresolvedPhotometry
    from .photometry import predict_photometry
    if not is_unresolved_result(result):
        raise ValueError('not a versioned unresolved photometry result')
    data = UnresolvedPhotometry.from_dict(result['dataset_input'])
    if data.sha256 != result['input_sha256']:
        raise ValueError('native observation input differs from fitted hash')
    identities = [row['source_row_id'] for row in data.rows]
    if identities != result['row_ids'] or len(identities) != len(result['predictions_magnitude']):
        raise ValueError('prediction rows differ from native source identities/order')
    check = predict_photometry(data, result['parameters'])
    if np.max(np.abs(check - result['predictions_magnitude']) / data.errors) > .001:
        raise ValueError('public physical parameters do not reconstruct saved predictions')
    dest = Path(directory)
    dest.mkdir(parents=True, exist_ok=True)
    for name, value in [('dataset.json', data.to_dict()), ('result.json', result),
                        ('analysis_config.json', result['analysis_configuration']),
                        ('software_provenance.json', result['software_provenance'])]:
        (dest / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf8')
    (dest / 'report.html').write_text(report_html(result), encoding='utf8')
    fields = ['source_row_id', 'source_file', 'source_sha256', 'source_line', 'instrument',
              'native_time', 'magnitude', 'magnitude_error', 'quality_flags']
    with (dest / 'native_observations.csv').open('w', newline='', encoding='utf8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in data.rows:
            writer.writerow({key: json.dumps(row[key]) if key == 'quality_flags' else row[key] for key in fields})
    with (dest / 'predictions.csv').open('w', newline='', encoding='utf8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['source_row_id', 'instrument', 'native_time', 'magnitude', 'magnitude_error',
                         'prediction_magnitude', 'residual_magnitude', 'standardized_residual'])
        for index, row in enumerate(data.rows):
            writer.writerow([row['source_row_id'], row['instrument'], row['native_time'],
                row['magnitude'], row['magnitude_error'], result['predictions_magnitude'][index],
                result['residuals_magnitude'][index], result['standardized_residuals'][index]])
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2 * len(data.instruments), 1, figsize=(10, 5 * len(data.instruments)),
                             squeeze=False, layout='constrained')
    for index, name in enumerate(data.instruments):
        chosen = data.instrument_indices == index
        order = np.argsort(data.times[chosen], kind='stable')
        times = data.times[chosen][order]
        pred = np.asarray(result['predictions_magnitude'])[chosen][order]
        ax, residual = axes[2 * index, 0], axes[2 * index + 1, 0]
        ax.errorbar(times, data.magnitudes[chosen][order], yerr=data.errors[chosen][order],
                    fmt='.', ms=2, alpha=.55, label='Native observations ± published σ')
        ax.plot(times, pred, color='#be4c24', lw=1.2, label='Fitted PSPL trajectory')
        ax.invert_yaxis()
        ax.set(title=name, ylabel='Apparent magnitude')
        ax.legend(fontsize=8)
        residual.plot(times, np.asarray(result['standardized_residuals'])[chosen][order], '.', ms=2)
        residual.axhline(0, color='.4', lw=.8)
        residual.set(xlabel=f'HJD − {data.common_origin_jd:g} days (clock as recorded)',
                     ylabel='Residual / declared σ')
    fig.suptitle(result['status'] + ' · mass unavailable')
    fig.savefig(dest / 'photometry_and_residuals.png', dpi=150)
    plt.close(fig)
    (dest / 'REPRODUCE.md').write_text('''# Replay native unresolved photometry

Install the matching Blackhole Tracker wheel and run outside the source checkout:

    python -m bhtracker replay . --output replayed

dataset.json preserves native time values, measurement errors, instrument/filter,
source row identities, raw source hashes, annotations, calibration and transformation
history. It contains no fabricated resolved positions, image ratios, delays,
distances or supplied full covariance. Source rows are not thinned or reordered.
The source byte hashes identify the separately retained original downloaded files;
the CSV is a processed representation and is not described as the original bytes.

The fit assumes independent native magnitude errors. The replay records exact fit
controls and checks predictions/status/identification with a 0.001 supplied-sigma
numerical tolerance. It does not rescale the original errors. Changed likelihood
protocols are rejected rather than silently interpreted as the saved analysis.
MASS_UNRESOLVED is distinct from the resolved-input TRACKED status.
''', encoding='utf8')
    names = ['dataset.json', 'result.json', 'analysis_config.json', 'software_provenance.json',
             'report.html', 'native_observations.csv', 'predictions.csv',
             'photometry_and_residuals.png', 'REPRODUCE.md']
    manifest = {'schema': BUNDLE_SCHEMA, 'dataset_sha256': data.sha256,
                'protocol_sha256': result['protocol_sha256'], 'project_citation': project_citation(),
                'files': {name: hashlib.sha256((dest / name).read_bytes()).hexdigest() for name in names}}
    (dest / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf8')
    return str(dest.resolve())


def replay_analysis(read, manifest, output):
    from .data import read_json
    from .observations import UnresolvedPhotometry
    from .photometry import FIT_PROTOCOL_SHA256, fit_photometry
    required = {'dataset.json', 'result.json', 'analysis_config.json', 'software_provenance.json'}
    if not required.issubset(manifest.get('files', {})):
        raise ValueError('unresolved replay manifest omits required inputs')
    for name, digest in manifest['files'].items():
        if Path(name).name != name or hashlib.sha256(read(name)).hexdigest() != digest:
            raise ValueError('unresolved replay member/path/hash mismatch: ' + name)
    if manifest.get('protocol_sha256') != FIT_PROTOCOL_SHA256:
        raise ValueError('saved likelihood protocol differs; retain the matching wheel or make a separately versioned reanalysis')
    data = UnresolvedPhotometry.from_dict(read_json(read('dataset.json')))
    if data.sha256 != manifest['dataset_sha256']:
        raise ValueError('unresolved replay native input hash differs')
    old = read_json(read('result.json'))
    config = read_json(read('analysis_config.json'))
    controls = {'initial', 'starts', 'max_nfev', 'noise_scale', 'equal_instrument_weight', 'allow_negative_blend'}
    if set(config) != controls:
        raise ValueError('unresolved replay controls differ from the versioned fit contract')
    result = fit_photometry(data, **config)
    difference = np.abs(np.asarray(old['predictions_magnitude']) - result['predictions_magnitude']) / data.errors
    maximum = float(np.max(difference))
    same_status = old['status'] == result['status']
    same_rows = old['row_ids'] == result['row_ids']
    same_identification = old['unresolved_quantities'] == result['unresolved_quantities']
    check = {'passed': bool(maximum <= .001 and same_status and same_rows and same_identification),
             'maximum_prediction_difference_in_supplied_sigma': maximum,
             'tolerance_in_supplied_sigma': .001, 'same_status': same_status,
             'same_native_row_identities_and_order': same_rows,
             'same_unresolved_quantities': same_identification,
             'original_version': old['product_version'], 'current_version': result['product_version'],
             'same_package_content': old['software_provenance']['package_files_sha256'] == result['software_provenance']['package_files_sha256'],
             'same_interpretation': old['bhsm_interpretation'] == result['bhsm_interpretation']}
    export_result(result, output)
    (Path(output) / 'replay_check.json').write_text(json.dumps(check, indent=2, allow_nan=False) + '\n', encoding='utf8')
    if not check['passed']:
        raise ValueError('native photometry replay differs; inspect replay_check.json')
    return check
