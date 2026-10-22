"""Author the portable walkthroughs; execute with execute_notebooks.py."""
from pathlib import Path
import nbformat as nbf
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'notebooks';out.mkdir(exist_ok=True)
def save(name,cells):
    book=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3 (BHSM Blackhole Tracker environment)','language':'python','name':'python3'},'language_info':{'name':'python'},'bhsm_interpretation':{'framework':'BHSM','product_version':__import__('tomllib').loads((ROOT/'pyproject.toml').read_text(encoding='utf8'))['project']['version'],'one_optical_potential':True,'requires_non_GR_deviation':False,'scope':'Ordinary and boundary descriptions represent the same fitted response, counted once; microscopic and horizon inference remain separate.'}})
    nbf.write(book,out/name)
md=nbf.v4.new_markdown_cell;code=nbf.v4.new_code_cell
save('01_compact_mass_and_motion.ipynb',[
md('''# BHSM Blackhole Tracker: mass and motion

This executable walkthrough imports a versioned measurement set and its **full covariance**, fits the two continued primary images, and exports a portable analysis. Source positions are free at every epoch/source row. Distances, redshift and the tangent-plane frame are supplied calibrations.

The ordinary mass is the effective gravitational monopole of the BHSM-described configuration; its center and proper motion locate and translate that same optical response. Equivalent gravity and envelope descriptions contribute through **one potential, counted once**. No non-GR deviation is required. A fixed-radius spherical boundary representation is a derived interpretation of that monopole, not a second mass or an independent measurement.

The input is synthetic. Its uncertainties are declared experimental inputs, not an instrument forecast or evidence for a black-hole horizon. Run from the installed project environment; no external service or API key is used.'''),
code('''import json
import numpy as np
import matplotlib.pyplot as plt
from bhtracker import fit, load_dataset
from bhtracker.examples import make_example
from bhtracker.inference import profile
from bhtracker.report import export_result
dataset, truth = make_example('nearby_motion')
load_dataset(dataset).summary()'''),
md('## Fit and interpret the same optical configuration\nThe optimizer uses data-based initial estimates and the declared nuisance family. The truth is retained only for validation. The boundary dictionary reports the principal curvature deficit and flat-reference Brown–York energy of the spherical ordinary monopole at `model.r0_pc`. Its errors condition on that fixed radius. The fit does not measure the radius or the full nonspherical/environmental boundary energy.'),
code('''result = fit(dataset, family='gr', nuisance='shear', starts=3)
summary = {key: result[key] for key in ['status', 'estimates', 'uncertainty', 'chi2', 'dof', 'motion_snr']}
summary['spherical_boundary'] = result['bhsm_interpretation']['spherical_boundary']
summary['radius_policy'] = result['model']['worldtube_policy']
summary'''),
code('''epochs = np.asarray(result['epochs_yr'])
track = np.asarray(result['center_track_mas'])
errors = np.asarray(result['center_track_sigma_mas'])
fig, axes = plt.subplots(1, 2, figsize=(10, 3.5), layout='constrained')
for j, label in enumerate(['x', 'y']):
    axes[0].errorbar(epochs, track[:,j], yerr=errors[:,j], fmt='o', label=label)
axes[0].set(xlabel='Observer epoch (yr)', ylabel='Lens center (mas)')
axes[0].legend()
axes[1].plot(result['whitened_residuals'], 'o', ms=3)
axes[1].axhline(0, color='.6')
axes[1].set(xlabel='Full-covariance whitened component', ylabel='Residual / noise')
plt.show()'''),
md('## Reoptimized likelihood\nLocal Gaussian errors are qualified by rank and active bounds. This curve refits the other parameters at each mass; its reference levels are not a universal boundary-coverage theorem.'),
code('''curve = profile(dataset, result, parameter='mass_msun', points=11)
plt.plot([p['value'] for p in curve['points']], [p['delta_chi2'] for p in curve['points']], '-o')
plt.axhline(1, color='.5', ls=':')
plt.xlabel('Lens mass (solar masses)'); plt.ylabel('Profile delta chi-squared'); plt.show()'''),
md('## A required negative control\nThe same workflow must not declare a well-measured motion merely because a mass can be measured.'),
code('''short_data, _ = make_example('cosmological_short_track')
short_result = fit(short_data, starts=2)
assert short_result['status'] != 'TRACKED'
{key: short_result[key] for key in ['status', 'motion_snr', 'uncertainty', 'diagnostics']}'''),
code("export_result(result, 'user_runs/notebook_baseline')\nprint('Exported JSON, HTML, predictions CSV, figure and file-hash manifest.')"),
md('The fixed 64-draw calibration and independent physical-unit/covariance tests are replayed by `python scripts/validate_product.py`. This notebook demonstrates inference and the BHSM interpretation of the same response; it does not replace the calibration protocol or uniquely identify a microscopic theory.')])
save('02_conditional_boundary_response.ipynb',[
md('''# BHSM Blackhole Tracker: conditional R1 response

The R1 extension uses one adopted scalar–tensor action and its metric response. Scalar flux provenance, worldtube radius and approximation budgets are explicit. The uniform bound restricts the admitted boundary-state norm. It does not select an astrophysical amplitude or a horizon solution.

This extends the same-potential BHSM interpretation. An ordinary envelope contribution already represented by a metric multipole is not added again. R1 `mass_msun` labels the action's metric/source mass; its total optical response includes the scalar term, so it is not automatically the ordinary point-exterior monopole. The Schwarzschild boundary conversion is not assumed for the modified metric. The metadata/reporting checks below do not test exclusive physical identification.

This notebook keeps the same declared synthetic measurement errors; it does not enlarge the physical state to manufacture detectability.'''),
code('''import json
import numpy as np
from bhtracker import fit
from bhtracker.examples import make_example
from bhtracker.physics_admission import assess_physics
dataset, truth = make_example('nearby_motion')
result = fit(dataset, family='r1', nuisance='shear', starts=2)
interpretation = result['bhsm_interpretation']
assert interpretation['framework'] == 'BHSM'
assert 'counted once' in interpretation['one_potential_rule']  # reporting contract
summary = {key: result[key] for key in ['status', 'estimates', 'conditional_envelope']}
summary['BHSM_same_response_interpretation'] = {key: interpretation[key] for key in ['model_role', 'one_potential_rule', 'conditional_extension', 'spherical_boundary']}
summary'''),
md('## Physical admission and canonical source pairing'),
code('''admission = result['physics_admission']
{key: admission[key] for key in ['allowed_physics_models', 'boundary_state', 'source_pairing', 'approximation_budgets']}'''),
code('''boundary = admission['boundary_state']
a_max = boundary['amplitude_norm_max']
q_max = boundary['impedance_l2'] * a_max
assert np.isclose(q_max, boundary['conormal_norm_max'], rtol=1e-12, atol=0)
{'Dirichlet_norm_cap': a_max, 'conormal_norm_cap': q_max,
 'horizon_matched': admission['horizon_matched_r1']}'''),
md('## Honest unresolved output\nAn unconstrained local coefficient that lies outside the admitted state ball is not a physical deformation measurement. The largest local SNR in the admitted ball tests whether even the most favorable admitted orientation could be resolved in this data design.'),
code('''envelope = result['conditional_envelope']
assert envelope['status'] == 'UNRESOLVED'
assert envelope['all_admitted_states_below_unit_snr']
{key: envelope[key] for key in ['status', 'boundary_amplitude_cap',
 'maximum_admitted_local_snr', 'unconstrained_estimate_inside_admitted_ball']}'''),
md('## Reject an inadmissible state instead of converting noise into a discovery'),
code('''bad_state = dict(result['_internal']['parameters'])
bad_state['boundary_amplitudes'] = [100 * a_max, 0, 0]
rejected = assess_physics(dataset, bad_state, result['branch_admission']['impact_pc'])
assert not rejected['allowed_physics_models']['r1_boundary_conditional']
rejected['reasons']'''),
md('An unresolved conditional surface family does not remove the BHSM interpretation of the ordinary mass, location and translation. The product uses one optical response within its declared domain. Separate microscopic, horizon-charge or deformation-dynamics inference requires the corresponding source/matching relations; these are not conditions for retaining the ordinary track.')])
print('Two portable research notebooks authored.')

# Keep the separate native route in a complete tutorial rebuild.
import runpy
runpy.run_path(str(ROOT/'scripts/make_unresolved_notebook.py'))
