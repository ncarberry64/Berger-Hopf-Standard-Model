"""Portable, self-contained research exports with traceable assumptions."""
from pathlib import Path
import csv
import hashlib
import html
import json
from io import BytesIO
import tempfile
import zipfile
import numpy as np
from .provenance import REPOSITORY_URL, project_citation

def report_html(result):
    r=result;e=r['estimates'];u=r['uncertainty']
    escape=lambda value:html.escape(str(value))
    def fmt(v):
        if v is None:return 'unresolved'
        if isinstance(v,list):return ', '.join(fmt(x) for x in v)
        if isinstance(v,(float,int)):return f'{v:.7g}'
        return escape(v)
    items=[('Mass (solar masses)',e['mass_msun'],u['mass_msun']),
           ('Center at reference epoch (mas)',e['center_mas'],u['center_mas']),
           ('Proper motion (mas / observer year)',e['proper_motion_mas_yr'],u['proper_motion_mas_yr'])]
    rows=''.join(f'<tr><th>{label}</th><td>{fmt(value)}</td><td>{fmt(err)}</td></tr>' for label,value,err in items)
    diagnostics=''.join(f"<li><strong>{escape(item['code'])}</strong>: {escape(item['message'])}</li>" for item in r['diagnostics'])
    from .interpretation import bhsm_interpretation
    interpretation=r.get('bhsm_interpretation') or bhsm_interpretation(r['model']['family'],e,u,r['model'],r['status'])
    meanings=''.join(f"<tr><th>{escape(item['parameter'])}</th><td>{escape(item['interpretation'])}<br><small>{escape(item['qualification'])}</small></td></tr>" for item in interpretation['parameter_meanings'])
    boundary=interpretation.get('spherical_boundary',{})
    boundary_html=''
    if boundary.get('status')=='AVAILABLE':
        boundary_html=f"<h3>Spherical boundary representation of the same monopole</h3><p>Declared radius {fmt(boundary['radius_pc'])} pc. Principal extrinsic-curvature deficit of the enclosing sphere {fmt(boundary['curvature_deficit_pc_inverse'])} ± {fmt(boundary['curvature_deficit_sigma_pc_inverse'])} pc⁻¹; Brown–York E/c² {fmt(boundary['boundary_energy_over_Msun_c2'])} ± {fmt(boundary['boundary_energy_sigma_over_Msun_c2'])} solar masses (local 1σ, fixed radius).</p><p><small>{escape(boundary['geometry'])} {escape(boundary['qualification'])} Radius policy: {escape(r['model'].get('worldtube_policy','not recorded'))}.</small></p>"
    elif boundary.get('reason'):
        boundary_html=f"<p>{escape(boundary['reason'])}</p>"
    core_surface=interpretation.get('core_surface')
    core_html=''
    if core_surface:
        ledger=''.join(f"<tr><th>{escape(item['label'])}<br><small>{escape(item['status'])}</small></th><td>{escape(item['statement'])}</td></tr>" for item in core_surface.get('claim_ledger',[]))
        core_html=f"<h3>Spacetime-side fit and proposed core interpretation</h3><p>{escape(core_surface['surface_summary'])}</p><p>{escape(core_surface['core_summary'])}</p><p><small>Interpretation status: {escape(core_surface['status'])}; this does not change the scientific fit status.</small></p><details><summary>Core, surface and matching theory</summary><p>{escape(core_surface['attribution'])}</p><p>{escape(core_surface['matching_summary'])}</p><p>{escape(core_surface['inference_scope'])}</p><table>{ledger}</table><h4>Versioned theory/source provenance</h4><pre>{escape(json.dumps(interpretation.get('source_provenance',{}),indent=2))}</pre></details>"
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Blackhole Tracker research report</title><style>body{{font:16px/1.55 system-ui;max-width:1050px;margin:3rem auto;padding:0 1.5rem;color:#172b40}}h1{{font-size:2.2rem}}table{{border-collapse:collapse;width:100%}}th,td{{padding:.7rem;border-bottom:1px solid #dce3e9;text-align:left}}pre{{background:#f1f5f8;padding:1rem;overflow:auto;white-space:pre-wrap}}small{{color:#4f657a}}.status{{padding:1rem;background:#edf6fa;border-left:4px solid #167e9b}}</style>
<h1>BHSM Blackhole Tracker</h1><p class="status">{escape(r['status'])} · {escape(r['data_summary']['provenance']['kind'])} measurements</p>
<p>Project source and reviewer record: <a href="{REPOSITORY_URL}">BHSM GitHub repository</a>.</p>
<p>Reference epoch {fmt(r['reference_epoch_yr'])}; family {escape(r['model']['family'])}; nuisance {escape(r['model']['nuisance'])}.</p>
<table><tr><th>Quantity</th><th>Estimate</th><th>Local 1σ</th></tr>{rows}</table>
<p>χ² {fmt(r['chi2'])} for {r['dof']} degrees of freedom; goodness-of-fit p={fmt(r['goodness_of_fit_p'])}. Uncertainties are local known-covariance approximations; active bounds and nulls require the stated qualification.</p>
<h2>BHSM interpretation</h2><p>{escape(interpretation['model_role'])}</p><p>{escape(interpretation['one_potential_rule'])}</p><p>{escape(interpretation['inference_scope'])}</p>{core_html}{boundary_html}<details><summary>Parameter interpretation</summary><table>{meanings}</table><p>{escape(interpretation['conditional_extension'])}</p></details>
<h2>Fit diagnostics</h2><ul>{diagnostics}</ul><h2>Conditional envelope</h2><pre>{escape(json.dumps(r['conditional_envelope'],indent=2))}</pre>
<h2>Model and domain</h2><pre>{escape(json.dumps(r['model'],indent=2))}</pre><pre>{escape(json.dumps(r.get('physics_admission'),indent=2))}</pre>
<h2>Reproduction</h2><pre>{escape(json.dumps(r['data_summary'],indent=2))}</pre><pre>{escape(json.dumps(r['runtime'],indent=2))}</pre>
<p><small>Product {escape(r['product_version'])}. A compact exterior fit does not identify a horizon. Synthetic examples and supplied uncertainties are not empirical detections or instrument forecasts. Full measurements, covariance, predictions and parameter covariance accompany the JSON export.</small></p></html>'''

def export_result(result,directory):
    dest=Path(directory);dest.mkdir(parents=True,exist_ok=True)
    from .data import load_dataset
    if 'dataset_input' not in result or 'analysis_configuration' not in result:
        raise ValueError('This older result lacks replay inputs; refit the original dataset with version 0.2.0rc1 or later before exporting a replay analysis')
    data=load_dataset(result['dataset_input'])
    if data.sha256!=result['data_summary']['sha256']:
        raise ValueError('result.dataset_input does not match data_summary.sha256; export the unmodified fitted result')
    for name,value in [('dataset.json',result['dataset_input']),('analysis_config.json',result['analysis_configuration']),
                       ('software_provenance.json',result['software_provenance'])]:
        (dest/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf8')
    (dest/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf8')
    (dest/'report.html').write_text(report_html(result),encoding='utf8')
    with (dest/'predictions.csv').open('w',newline='',encoding='utf8') as stream:
        writer=csv.writer(stream)
        from .data import FIELDS
        writer.writerow(['epoch_yr',*FIELDS])
        for epoch,row in zip(result['epochs_yr'],result['predictions']):writer.writerow([epoch,*row])
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    times=np.array(result['epochs_yr']);track=np.array(result['center_track_mas'])
    err=np.array([[np.nan if v is None else v for v in row] for row in result['center_track_sigma_mas']])
    axes[0].errorbar(times,track[:,0],yerr=err[:,0],fmt='o',label='x center')
    axes[0].errorbar(times,track[:,1],yerr=err[:,1],fmt='s',label='y center')
    axes[0].set(xlabel='Observer epoch (year)',ylabel='Lens center (mas)');axes[0].legend(frameon=False)
    axes[1].plot(result['whitened_residuals'],'o',ms=3);axes[1].axhline(0,color='.6',lw=.8)
    axes[1].set(xlabel='Whitened component (full covariance)',ylabel='Residual / supplied noise')
    fig.suptitle('Blackhole Tracker · '+result['status'])
    fig.savefig(dest/'track_and_residuals.png',dpi=170);plt.close(fig)
    obs=np.asarray(result['observations']);pred=np.asarray(result['predictions'])
    marginal=np.sqrt(np.diag(np.asarray(result['covariance']))).reshape(-1,6)
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for a,b,label,marker in [(0,1,'positive parity','o'),(2,3,'negative parity','s')]:
        axes[0].errorbar(obs[:,a],obs[:,b],xerr=marginal[:,a],yerr=marginal[:,b],fmt=marker,
                         ms=3,capsize=2,label=label+' data (marginal 1σ)')
        axes[0].plot(pred[:,a],pred[:,b],'x',label=label+' model')
    axes[0].set(xlabel='Tangent-plane x (mas)',ylabel='Tangent-plane y (mas)');axes[0].legend(fontsize=7)
    axes[1].errorbar(times,obs[:,5],yerr=marginal[:,5],fmt='o',ms=3,label='supplied delay ± marginal 1σ')
    axes[1].plot(times,pred[:,5],'x',label='fitted model')
    axes[1].set(xlabel='Observer epoch (Julian year)',ylabel='Minus − plus arrival delay (seconds)');axes[1].legend(fontsize=7)
    fig.suptitle(result['data_summary']['provenance']['kind']+' input · full covariance used in inference')
    fig.savefig(dest/'measurements_and_model.png',dpi=170);plt.close(fig)
    (dest/'REPRODUCE.md').write_text('''# Replay this analysis

Install the accompanying bhsm-blackhole-tracker wheel (pip resolves NumPy,
SciPy and Matplotlib on first installation). Work in this extracted directory.

    python -m bhtracker validate dataset.json
    python -m bhtracker replay . --output replayed

Or pass this ZIP directly to replay. For the Python API:

    import json
    from bhtracker import fit
    data = json.load(open("dataset.json", encoding="utf8"))
    config = json.load(open("analysis_config.json", encoding="utf8"))
    result = fit(data, **config)

dataset.json preserves the original full input, including its full covariance,
calibrations, provenance and analysis assumptions. analysis_config.json records
all public fit controls, including explicit starting values if supplied.
software_provenance.json hashes the installed code/assets and pinned theory.
manifest.json verifies every exported file. result.json retains parameters,
predictions, covariance, diagnostics and BHSM interpretation/domain information.
The original input covariance is retained even if symmetry within the declared
1e-9 correlation-unit tolerance was averaged for numerical Cholesky evaluation.

Replay uses the current installed version and reports version/content changes.
It requires the same scientific status and prediction differences no greater
than 0.001 of each supplied marginal standard deviation. This numerical
tolerance is not a change to observational errors or a statistical acceptance
threshold. It never rescales covariance. Different platforms/versions can give
different optimizer rounding; inspect replay_check.json and pin the recorded
dependencies when reproducing archived results.

Plots show marginal 1σ bars; the fit and whitened residuals use the entire
supplied covariance. TRACKED is a supported compact exterior under the adopted
BHSM Einstein/GHY sector, not a horizon detection. Boundary energy/curvature
are derived from the same mass at a declared radius, counted once. Conditional
R1 information is an optional extension and does not select a black-hole charge.
''',encoding='utf8')
    files=[dest/name for name in ('dataset.json','analysis_config.json','software_provenance.json',
        'result.json','report.html','predictions.csv','track_and_residuals.png','measurements_and_model.png','REPRODUCE.md')]
    (dest/'manifest.json').write_text(json.dumps({'schema':'bhtracker.analysis_bundle.v1','dataset_sha256':result['data_summary']['sha256'],
        'project_citation':project_citation(),
        'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}},indent=2)+'\n')
    return str(dest.resolve())

def export_analysis_bundle(result):
    """Return a self-contained replay ZIP; never use user-controlled filenames."""
    with tempfile.TemporaryDirectory(prefix='bhtracker export ') as directory:
        export_result(result,directory)
        stream=BytesIO()
        with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(Path(directory).iterdir()):archive.writestr(path.name,path.read_bytes())
        return stream.getvalue()

def replay_analysis(source,output):
    """Verify hashes, re-fit the saved input/config and compare predictions."""
    from .data import read_json
    from .inference import fit
    source=Path(source)
    if source.is_dir() and source.resolve()==Path(output).resolve():
        raise ValueError('replay output must be a different directory, so the saved original analysis is preserved')
    if source.is_dir():
        def read(name):
            if Path(name).name!=name:raise ValueError('manifest filenames must be single path components')
            return (source/name).read_bytes()
        manifest=read_json(read('manifest.json'))
    else:
        try:
            with zipfile.ZipFile(source) as archive:
                infos=archive.infolist()
                if sum(i.file_size for i in infos)>100_000_000:raise ValueError('replay ZIP exceeds 100 MB uncompressed limit')
                if len({i.filename for i in infos})!=len(infos):raise ValueError('replay ZIP contains duplicate filenames')
                content={i.filename:archive.read(i) for i in infos}
        except zipfile.BadZipFile as error:raise ValueError('replay requires an exported analysis directory or valid ZIP') from error
        def read(name):
            if name not in content:raise ValueError(f'replay ZIP is missing {name}')
            return content[name]
        manifest=read_json(read('manifest.json'))
    if manifest.get('schema')!='bhtracker.analysis_bundle.v1':raise ValueError('manifest is not a version-1 analysis replay bundle')
    for required in ('dataset.json','analysis_config.json','result.json','software_provenance.json'):
        if required not in manifest.get('files',{}):raise ValueError(f'manifest must include {required}')
    for name,digest in manifest['files'].items():
        if hashlib.sha256(read(name)).hexdigest()!=digest:raise ValueError(f'replay hash mismatch for {name}; use the unmodified exported bundle')
    raw=read_json(read('dataset.json'));config=read_json(read('analysis_config.json'));old=read_json(read('result.json'))
    if set(config)!={'family','nuisance','starts','max_nfev','initial'}:raise ValueError('analysis_config.json has missing or unsupported fit controls')
    from .data import load_dataset
    if load_dataset(raw).sha256!=manifest['dataset_sha256']:raise ValueError('dataset hash differs from replay manifest')
    result=fit(raw,**config)
    difference=np.abs(np.asarray(result['predictions'])-np.asarray(old['predictions']))
    sigma=np.sqrt(np.diag(np.asarray(result['covariance']))).reshape(-1,6)
    maximum=float(np.max(difference/sigma))
    check={'passed':bool(maximum<=.001 and result['status']==old['status']),
           'maximum_prediction_difference_in_supplied_sigma':maximum,'tolerance_in_supplied_sigma':.001,
           'same_status':result['status']==old['status'],'original_version':old['product_version'],
           'current_version':result['product_version'],
           'same_package_content':old.get('software_provenance',{}).get('package_files_sha256')==result['software_provenance']['package_files_sha256'],
           'original_interpretation_schema_version':old.get('bhsm_interpretation',{}).get('interpretation_schema_version',1),
           'current_interpretation_schema_version':result['bhsm_interpretation']['interpretation_schema_version'],
           'same_interpretation':old.get('bhsm_interpretation')==result['bhsm_interpretation']}
    export_result(result,output)
    (Path(output)/'replay_check.json').write_text(json.dumps(check,indent=2)+'\n',encoding='utf8')
    if not check['passed']:raise ValueError(f'replay differs from saved result: inspect {Path(output)/"replay_check.json"}')
    return check
