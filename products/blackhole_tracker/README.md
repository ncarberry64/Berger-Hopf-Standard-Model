# BHSM Blackhole Tracker 0.2.0rc5

BHSM Blackhole Tracker reconstructs the effective gravitational mass, location and motion of a BHSM-described compact configuration from resolved image pairs, their magnification ratio and their delay. The ordinary lens response and the BHSM boundary/envelope interpretation use the **same optical potential, counted once**. Agreement with ordinary gravity is an allowed result; a non-GR deviation is not required to use this interpretation.

The product provides a local browser app, command-line tools, a Python API, notebooks, reproducible synthetic validation, and a separately versioned native unresolved-photometry route. The latter has processed the frozen 100-event OGLE-III pilot and the corresponding 2022 historical benchmark. It leaves mass unavailable when angular and parallax information are absent. It also reports a spherical boundary representation of an ordinary fitted monopole at a fixed declared radius. The optional conditional R1 response evaluates a specific adopted scalar–tensor exterior and its normalized state-admission bound.

The formal source and reviewer record are in the [BHSM GitHub repository](https://github.com/ncarberry64/Berger-Hopf-Standard-Model), under `products/blackhole_tracker/`; the paper is under `papers/bhsm_blackhole_tracker_20261021/`. App/package metadata and exported `project_citation` records cite that repository. Immutable historical provider/source citations retain their original locations.

The fitted object is a **compact exterior**. Its BHSM interpretation does not uniquely identify the microscopic theory, establish a horizon or select an R1 deformation state. Bundled resolved measurement examples are explicitly synthetic. Actual downloaded observations remain in the external data handoff; the paper includes the complete derived 100-event results, residual plots and protocol without redistributing those raw files.

## Candidate atlas: useful targets with mass unresolved

Open **Candidate sky atlas**, run `blackhole-tracker serve --open --page atlas`, or use `Start_Blackhole_Tracker_Atlas.cmd`. The offline inventory contains all 100 pilot events and all 59 published parallax events, with four verified overlaps counted once: **155 unique source/event directions**. A separate published black-hole benchmark has an explicitly unresolved tracker recovery. No catalog coordinate is presented as a current lens position.

Three records warrant investigation for different reasons: the two existing photometric followups and disputed, population-dependent PAR-13. Later literature revisions and alternatives remain visible. These are search targets; no new black-hole identification or independently measured lens mass is claimed. Failed fits, unavailable observations and unknown physical fields stay in the inventory. Filter, inspect the sky map, export CSV or a full JSON replay, and reopen the replay without fitting. [CANDIDATE_ATLAS.md](CANDIDATE_ATLAS.md) describes the evidence stages, source versions, Python/CLI use and offline metadata rebuild.

## Joint angular observations and annual parallax

The joint workflow introduced in rc4 provides `/joint`, `blackhole-tracker joint`, a versioned Python API and `04_joint_astrometry_and_parallax.ipynb`. The GUI imports the reviewed 2023 known-system source ZIP directly, or calibrated joint JSON, and verifies/reopens saved results. Use the explicit Joint launcher or install the wheel's `[astrometry]` extra. [JOINT_RESEARCH.md](JOINT_RESEARCH.md) explains inputs, formulas, complete likelihood choices, interpretation, export and replay.

The new source version uses actual corrected author OGLE data and 21 HST centroid rows across 11 visits, with 82 mapped exposure headers. It preserves unknown clock and averaging conventions as explicit assumptions. This route is separate from the original 2022 benchmark. All three declared v2 benchmark noise models fail an adequacy check; their conditional masses are not reliable black-hole measurements. The software retains those failures, profile degeneracies and the required additional calibration evidence. Successful state replay does not change that scientific outcome. It has not validated general recognition of known black holes or identified a new one.

## Native unresolved observations: app, CLI, Python and notebook

Use **Unresolved photometry** in the app, or open `http://127.0.0.1:8765/photometry`. Import an optimized OGLE-III `.dat` file, the corresponding benchmark OGLE/MOA files, or a saved `bhsm_unresolved_observations/1` JSON. The import preserves byte hashes, source-line identities, native magnitude/errors/time, filter/instrument calibration, literal source warnings and transformation history. Original files remain unchanged. The separate native page supports a 32 MB versioned input; the resolved page retains its 8 MB limit. The local server has a 40 MB total request limit.

Validate, fit and inspect the observations and residuals before exporting the replay ZIP. The default is the reviewed 12-start native-magnitude PSPL likelihood with published errors, nonnegative source/blend flux and no clipping or thinning. A signed calibration blend or changed weights/noise is an explicitly labelled sensitivity. Numerical convergence, photometric flux admission, observational adequacy and parameter identification are separate decisions. The public `PHOTOMETRIC_FIT` status does not imply a measured lens mass; this route always retains `MASS_UNRESOLVED`.

```text
python -m bhtracker import-ogle3 /path/to/photBLG122.6.I.83113.dat --output observations.json
python -m bhtracker validate observations.json
python -m bhtracker fit-photometry observations.json --output native_fit
python -m bhtracker replay native_fit --output native_replayed
python -m bhtracker profile-photometry observations.json native_fit/result.json --timescales 150 200 250 300 350 --output timescale_profile.json
```

For the historical 2022 reduction, use `import-benchmark --ogle OGLE_file --moa MOA_file --output observations.json`. The native HJD origin arithmetic is recorded; an origin shift is not a clock-scale or heliocentric conversion. The additional limited relative-time assumption for combining the two instruments remains explicit. Their baseline, blend and residual diagnostics remain separate.

```python
from bhtracker.observations import load_ogle_photometry
from bhtracker.photometry import fit_photometry
from bhtracker.report import export_result, replay_analysis
observations = load_ogle_photometry('/path/to/photBLG122.6.I.83113.dat')
result = fit_photometry(observations, starts=12)
assert result['mass_status'] == 'MASS_UNRESOLVED'
export_result(result, 'native_fit')
replay_analysis('native_fit', 'native_replayed')
```

The notebook `03_native_unresolved_photometry.ipynb` uses the actual external observations when `BHSM_DATA_ROOT` points to the handoff's `data` directory; its portable fallback is explicitly synthetic. The frozen measured pilot lives in the paper's `real_data_pilot_20261022/` directory. It processed **all 100 events / 76,344 rows**: 89 simple-model inadequate and 11 photometric fits. Two predeclared archival follow-up targets pass stricter checks, with no mass-supported black-hole candidate or new black-hole interpretation. Neither ranking nor duration is a black-hole probability. The original 2022 benchmark remains photometric-model inadequate; its released HST timing/frame conventions prevent a validated joint mass inference. The separate 2023 joint route above uses independently versioned observations and retains its own failed noise checks.

The native model identifies only supported model-conditional photometric combinations. Since `tE = thetaE / mu_rel` and `thetaE^2 = kappa M pi_rel`, mass, distance, absolute angular proper motion, horizon and core state remain `null`. One effective optical potential has the explicit BHSM interpretation and is counted once. No inferred surface deformation or core dynamics are added to an inadequate light curve. See [UNRESOLVED_OBSERVATIONS.md](UNRESOLVED_OBSERVATIONS.md) for the likelihood and optional astrometric metadata gates.

## Reviewed fitting corrections in rc3

Resolved fits use a stable data-derived optimization epoch and scaling, then transform parameters, the full covariance and null directions to the supplied reporting epoch. Numerical reference mass and epoch impose no hidden positional box. `model.parameter_basis` and `physical_parameter_uncertainty` version this representation; unidentified public covariance is unavailable rather than a tiny pseudoinverse block. Low-significance identifiable motion retains finite covariance. [FITTING_CONTRACT_V2.md](FITTING_CONTRACT_V2.md) documents compact-quadrupole normalization, physical bounds and migration.

Resolved profiles genuinely search physically admissible nuisance states and distinguish interior, boundary, numerical failure and unresolved physical-domain outcomes. Unresolved rows cannot supply interval crossings. Legacy internal profile coordinates require refitting the preserved raw input. Replay records raw-input refitting and rejects a silently changed historical default worldtube. The radial membrane source now explicitly states its fixed-background, constant-tension assumptions and pressure source, with both handoff versions and original documents reconciled in the BHSM source record.

## What the fitted quantities mean in BHSM

The recovered BHSM source records admit an Einstein/GHY gravitational sector and a boundary representation of its mass. The ordinary response reconstructs that effective exterior; the boundary description is an interpretation of its gravitational response, rather than a second force added to it.

| Optical fit quantity | BHSM interpretation |
|---|---|
| Ordinary `mass_msun` | Effective gravitational monopole of the represented configuration, conditional on the supplied geometry and lens model. It does not separately measure a microscopic constituent mass or a topological charge. |
| `center_mas` | Location of that same optical configuration in the supplied tangent-plane frame. |
| `proper_motion_mas_yr` | Translation of that configuration per observer year; internal deformation dynamics are separate. |
| `compact_quad` | Projected compact structure, which may represent an envelope when it produces that potential. The coefficient does not uniquely select a physical surface mode. |
| `shear` / `convergence` | Admitted tidal/focusing response of the surrounding environment; not automatically intrinsic structure of the tracked object. |

An equivalent envelope quadrupole already represented by `compact_quad` is not added again under another name. A separate R1 term is included only as a distinct response of the adopted common action and its supplied matching data. The tracker uses `W_full = Phi + Psi`; a BHSM convention `W_topo = (Phi_topo + Psi_topo)/2` contributes `2*W_topo` to that same full Weyl potential. This notation conversion creates no additional physical contribution.

The result's `bhsm_interpretation` dictionary records these meanings and the one-potential rule. Its `source_provenance` points to packaged, hash-checked BHSM source records. This is a traceable interpretation within the declared sector, not an exclusive test distinguishing every theory that produces the same exterior. No microscopic or horizon identification is required to retain the ordinary mass/motion fit.

## Start on Windows

Install Python **3.11 or newer**, with the `python` command available on PATH. Unpack the complete product folder and double-click **`Start_Blackhole_Tracker.cmd`**.

On first launch the script creates `.venv`, installs the package and runtime dependencies, and opens the local app. It also checks an existing environment and repairs missing dependencies. Dependency installation needs access to your configured package index; fitting uses no remote service or API key. Keep the console open while using the app. Press **Ctrl+C** there to stop it. The launcher also accepts the Windows `py -3` launcher when `python` is unavailable.

The default address is **http://127.0.0.1:8765/**. If the browser does not open, enter that address manually. If the port is occupied, run `Start_Blackhole_Tracker.cmd --port 8766`. `--no-open` suppresses browser opening; `--check-install` installs/checks dependencies and exits. A missing or old Python produces an installation message and a nonzero exit code. Paths containing spaces are supported.

### Enable joint astrometry explicitly

The standard launcher installs the resolved-image and native-photometry routes. Joint parallax and angular-centroid research also needs **Astropy**. To choose that extra, double-click **`Start_Blackhole_Tracker_Joint.cmd`**, or run `Start_Blackhole_Tracker.cmd --astrometry`. This explicitly installs/checks the same package with its `astrometry` extra, then starts the same local app. Initial dependency installation needs network access. The ordinary launcher never adds optional dependencies merely because the joint page is opened.

For an existing source installation, close the app and run these PowerShell commands from the unpacked product directory:

```powershell
.\.venv\Scripts\python.exe -m pip install ".[astrometry]"
.\.venv\Scripts\python.exe -m bhtracker serve --open
```

If the environment does not exist yet, use the explicit joint launcher or the environment-creation commands below first. A wheel installation uses its actual local path: `python -m pip install "./bhsm_blackhole_tracker-0.2.0rc5-py3-none-any.whl[astrometry]"`. Quoting keeps the path and extra together, including paths containing spaces. On Linux/macOS, use the interpreter in your chosen virtual environment with the same wheel-extra command.

Open **Joint astrometry research** and follow [JOINT_RESEARCH.md](JOINT_RESEARCH.md) for the reviewed source-pack import, explicit clock/frame assumptions, fitting, export and replay. Enabling the dependency does not validate a noise model or establish a black-hole mass. The original 2022 ambiguous HST export and the separately versioned 2023 benchmark remain distinct.

For an explicit PowerShell installation, start in this `product` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\python.exe -m bhtracker serve --open
```

This does not require activating the environment or changing PowerShell's execution policy. If an existing `.venv` is missing dependencies, rerun the installation command. After changing source dependencies, rerun it before restarting the app.

### Other installation options

Use the interpreter/environment in which you want the package installed:

```text
python -m pip install .
python -m bhtracker serve --port 8766 --open
```

For development and notebook replay, use `python -m pip install -e ".[dev]"`. To run the optional joint tests and notebooks, explicitly use `python -m pip install -e ".[dev,astrometry]"`. To install a supplied wheel, replace the path below with its actual location:

```text
python -m pip install path/to/bhsm_blackhole_tracker-0.2.0rc5-py3-none-any.whl
python -m bhtracker serve --open
```

The wheel contains the browser assets, example JSON files and pinned R1 provider inputs. The source distribution also supplies the launcher, notebooks, tests and validation scripts. To build a wheel from source with the development dependencies installed, run `python -m build --wheel`; output goes to `dist/`.

The commands below use `python` to mean the interpreter with this package installed. With the Windows environment above, substitute `.\.venv\Scripts\python.exe`. The installed `blackhole-tracker` executable is equivalent to `python -m bhtracker`.

On Linux, create a fresh environment with `python3 -m venv tracker-env`, install the wheel with `tracker-env/bin/python -m pip install /path/to/the.whl`, then run `tracker-env/bin/python -m bhtracker serve --open`. The source installation uses the same `pip install .` command from the unpacked product directory. Distribution-provided Python installations may require their `python3-venv` package first.

## Use the local app

1. Choose a built-in example and **Load**, or **Import your dataset** from a JSON file.
2. Select **Validate dataset**. Inspect the dataset summary and the input JSON under **Inspect dataset & configuration**.
3. Keep the recommended **Ordinary lens response** and select **Run fit**. It defaults to smooth tidal shear and two optimization starts. Its API/CLI family name remains `gr`; R1, environment and starts are inside **Advanced model options**.
4. Read the fit status, BHSM interpretation, uncertainties, residuals and diagnostics. The spherical boundary cards describe the same fitted monopole at the displayed fixed radius. **Conditional R1 response** additionally requires declared scalar-flux provenance and an admitted physical domain.
5. Select **Download replay bundle**. It includes the original input, full covariance and calibrations, exact fit controls, result, HTML, prediction CSV, two plots, software/source hashes and a reproduction guide. JSON and HTML remain separately available.
6. Install the same wheel in another working directory and run `python -m bhtracker replay bhsm-analysis-replay.zip --output replayed`. Read `replayed/replay_check.json`; no original private input path is needed.

The server binds only to `127.0.0.1`. Inputs and jobs remain in that local process until you export them; it uses no remote fitting service. Closing the process clears its in-memory jobs. Dataset imports are limited to 8 MB; JSON requests are limited to 40 MB to accommodate result exports. At most 64 jobs are retained per session; restart to clear a full session. One worker runs fits sequentially: **pending** means queued, **running** means inference is executing, **complete** means a scientific result is available (which may be rejected or unresolved), and **failed** means computation raised an error. Duplicate pending/running submissions of the same dataset/configuration reuse the existing job. Cancellation is unavailable. This is a local research tool, not an authenticated network deployment.

### Bundled examples

| Example ID | Purpose |
|---|---|
| `nearby_motion` | A synthetic, identifiable compact-mass track from three source positions sampled over ten years. |
| `cosmological_short_track` | A mass measurement with deliberately weak ten-year proper-motion information. An unresolved motion is a useful result. |
| `ordinary_shear` | Conventional external shear; compare fits that omit and admit shear. |
| `stellar_benchmark` | A synthetic stellar-lens variation inspired by the Lu et al. arXiv:2512.03364 Table 2 parameters, with explicitly synthetic observer factors. It is neither observed data nor BAGLE output. |

The example `seed` controls generated Gaussian noise. Example uncertainties are declared test inputs, not an instrument forecast. The synthetic truth is used for validation and is not supplied to the ordinary example fit.

Choose **Download example files · ZIP** in the app, or use `examples/nearby_motion/` in the source package. The complete bundle supplies `measurements.csv`, `metadata.json`, `full_covariance.csv`, `dataset.json`, a short units/ordering guide and file hashes. Import the native JSON in the app; the CLI conversion below supports the three CSV/metadata files.

## Command-line workflow

Run these commands in a working directory where you want `user_runs` created:

```text
python -m bhtracker example nearby_motion --output user_runs/nearby_motion.json
python -m bhtracker validate user_runs/nearby_motion.json
python -m bhtracker fit user_runs/nearby_motion.json --family gr --nuisance shear --starts 3 --output user_runs/nearby_fit
python -m bhtracker replay user_runs/nearby_fit --output user_runs/replayed_fit
python -m bhtracker profile user_runs/nearby_motion.json user_runs/nearby_fit/result.json --parameter mass_msun --output user_runs/mass_profile.json
```

`validate` checks the versioned measurement schema and covariance. A valid measurement file can still fail the physical model or contain insufficient information; those checks occur during prediction/inference.

### Import CSV measurements with their full covariance

```text
python -m bhtracker import-csv measurements.csv --metadata metadata.json --covariance covariance.csv --output user_runs/imported.json
python -m bhtracker validate user_runs/imported.json
```

The measurement CSV has one header with exactly these seven names, each once. Their column order may differ; extra or missing columns are rejected:

```csv
epoch_yr,x_plus_mas,y_plus_mas,x_minus_mas,y_minus_mas,ln_flux_ratio,delay_seconds
```

Supply 3–80 finite numeric rows. `metadata.json` is the version-1 JSON skeleton containing `schema_version`, `geometry`, `reference_epoch_yr`, `analysis` and `provenance`, with optional `title` and `fields`. It must **not** contain `epochs_yr`, `observations` or `covariance`; the importer obtains them from the CSV files. For example, a local synthetic metadata file is:

```json
{
  "schema_version": 1,
  "geometry": {"D_l_pc": 1000, "D_s_pc": 8000, "D_ls_pc": 7000, "z_l": 0, "z_s": 0},
  "reference_epoch_yr": 2026,
  "analysis": {"source_policy": "free_per_epoch", "r0_pc": 0.00000001},
  "provenance": {"kind": "synthetic", "description": "Replace with the actual origin of these measurements"}
}
```

`covariance.csv` is a required **headerless, dense `6N × 6N` numeric matrix**. It uses the canonical six-observable order within each measurement row, regardless of the order of columns in `measurements.csv`; it never includes an epoch covariance column. Keep cross-row correlations. The importer preserves measurement row order and does not infer errors, sort epochs or diagonalize the covariance. UTF-8 with an optional BOM is accepted. Set observed provenance accurately when importing real data.

`fit --output` takes a **directory**, not a JSON filename. It writes:

| File | Contents |
|---|---|
| `result.json` | Estimates, local uncertainty, BHSM interpretation and derived boundary dictionary, model/bounds, source positions, measurements, full covariance, predictions, admission and diagnostics. |
| `report.html` | Portable research report, including the BHSM same-response interpretation. |
| `predictions.csv` | Observer epoch and the six predicted observables, with a header. |
| `track_and_residuals.png` | Fitted center track and full-covariance whitened residuals. |
| `manifest.json` | Dataset hash and SHA-256 hashes of exported files. |

Use a fresh output directory for each analysis. Available nuisance options are `none`, `shear` (default) and `full`. Every option still fits two independent source coordinates per row. `full` adds two ordinary compact-quadrupole coefficients and convergence to shear. The number of starts must be 1–8.

For the conditional family:

```text
python -m bhtracker fit user_runs/nearby_motion.json --family r1 --nuisance shear --starts 2 --output user_runs/nearby_r1
```

Profile parameters are `mass_msun`, `motion_x` and `motion_y`. A profile reoptimizes the other parameters; its reference levels Δχ² = 1 and 3.84146 are not automatically calibrated confidence limits at a bound or other nonregular point. Inspect convergence and truncation. Use the same original dataset and full, unstripped `result.json`; profiles require its saved internal fit state. The CLI checks the original dataset hash and creates the output file's parent directory when needed.

Run `python -m bhtracker --help` or append `--help` to a subcommand for the installed interface.

## Measurement JSON: schema version 1

JSON numbers must be finite. There are **3–80 epoch/source rows**. Repeated epoch values are allowed, for example several sources observed at one epoch; 3 rows do not imply 3 distinct times or an identifiable proper motion. Row order is preserved.

| Field | Type and meaning |
|---|---|
| `schema_version` | Required integer `1`. |
| `title` | Optional descriptive string. |
| `fields` | Optional exact array shown below. If present, its order must match exactly. |
| `geometry` | Required object with the five distance/redshift fields below. |
| `geometry.D_l_pc` | Positive angular-diameter lens distance, pc. |
| `geometry.D_s_pc` | Positive angular-diameter source distance, pc. |
| `geometry.D_ls_pc` | Positive lens-to-source angular-diameter distance, pc. |
| `geometry.z_l`, `geometry.z_s` | Finite nonnegative redshifts, with `z_s > z_l`; equal zero values are also allowed for a supplied local geometry. |
| `reference_epoch_yr` | Required finite observer-year reference epoch. |
| `epochs_yr` | Required length-`N` array of finite observer-year epochs. |
| `observations` | Required `N × 6` numeric array in the exact order below. |
| `covariance` | Required `6N × 6N` full covariance in the flattened order below; finite, symmetric, positive definite, with positive variances. |
| `analysis` | Optional object; scientific choices should be supplied explicitly. See the next table. |
| `provenance` | Required object containing `kind: "synthetic"` or `kind: "observed"`. Other provenance metadata is preserved. |

The exact column-name array is:

```json
["x_plus_mas", "y_plus_mas", "x_minus_mas", "y_minus_mas", "ln_flux_ratio", "delay_seconds"]
```

The `+` image is the continued positive-parity point-lens branch and `−` the continued negative-parity branch. **These labels do not mean bright and faint.**

```text
ln_flux_ratio = ln(|mu_plus| / |mu_minus|)
delay_seconds = arrival_time_minus - arrival_time_plus
```

`ln_flux_ratio` may be negative when the positive-parity image is fainter. Model predictions retain positive delay on the admitted time-ordered primary branches. The fluxes must correspond to the same source emission; an observed flux ratio with extinction, microlensing, source variability or calibration effects needs a justified treatment of those effects and its uncertainty. The input loader does not establish those physical conditions.

Both image coordinates use **mas in the same absolute tangent-plane frame**. Center/source coordinates use that same frame. No automatic RA/Dec conversion, reference-frame fit or epoch-timescale conversion is performed.

### Full covariance order and units

Flatten observations **row first**, exactly as `numpy.asarray(observations).ravel(order="C")`:

```text
[x+_0, y+_0, x-_0, y-_0, lnR_0, delay_0,
 x+_1, y+_1, x-_1, y-_1, lnR_1, delay_1, ...]
```

`covariance[6*i+j][6*k+l]` is the covariance of column `j` in row `i` with column `l` in row `k`. Supply **variances**, not standard deviations, on its diagonal. Off-diagonal units are products of the corresponding observable units: mas², mas·seconds, seconds², and so on. Image, cross-observable and cross-epoch correlations are supported. If you reorder rows, permute both covariance axes in the same six-element blocks. The product does not silently sort epochs or discard off-diagonal covariance.

A safe starting file is a generated example rather than a manually shortened covariance matrix:

```python
import json
from pathlib import Path
from bhtracker.examples import make_example

raw, truth = make_example("nearby_motion", noise=False)
Path("dataset.json").write_text(json.dumps(raw, indent=2), encoding="utf-8")
```

### Analysis options

| Key in `analysis` | Meaning/default |
|---|---|
| `source_policy` | Only `"free_per_epoch"` is supported; this is the default. Two source coordinates are fitted independently per row. |
| `r0_pc` | Positive unresolved-worldtube radius in pc. Supply this for a physically fixed worldtube. If omitted, the engine uses `0.001` times its computational reference Einstein radius; the result records `model.r0_pc` and its `worldtube_policy`. This default is not a selected physical surface. |
| `reference_mass_msun` | Optional positive numerical normalization. Fit initialization supplies one if omitted; it is not a physical mass prior. Compact-quadrupole coefficients are expressed in this reference lens basis. |
| `mass_bounds_msun` | Two increasing positive finite physical masses; default `[0.001, 1000000000000]`. Active bounds are diagnosed. |
| `lens_parallax_factors` | Optional `N × 2` finite, dimensionless supplied observer factors; defaults to zero. Their angular contribution is `(1000 / D_l_pc) * factors` mas. |
| `flux_ratio` | R1 scalar-source flux relative to the declared regular-body normalization; default `1`. **This is not the image flux ratio.** It has no effect on the GR family. |
| `flux_provenance` | R1 provenance and fixed/fitted policy, described below. |
| `H0` | R1 scale in km/s/Mpc; default `67.4`. An explicitly supplied `geometry.H0` takes precedence. |
| `eta_cap` | Retained-action boundary admission budget, default `0.001`. This bounds possible states; it does not select one. |
| `weak_metric_cap`, `hessian_fraction_cap`, `principal_fraction_cap` | Positive approximation budgets, each default `0.01`; the principal fraction must be below 1. |
| `quasistatic_speed_ratio_cap`, `background_drift_cap`, `spatial_gradient_ratio_cap` | Positive approximation budgets, each default `0.01`. They define model scope, not measurement precision. |
| `intrinsic_timescale_observer_yr` | Optional supplied positive intrinsic boundary-evolution timescale for its additional quasistatic check. Without it, fixed boundary coefficients are assumed; no relaxation time is derived. |

Supplied cosmological distances need not satisfy the Euclidean identity `D_ls = D_s - D_l`. The code does not infer distances or redshifts and does not propagate their uncertainty. The supplied parallax factors must match your observer, time convention and tangent-plane frame; the tool does not calculate an Earth ephemeris or a fitted parallax. The center track is

```text
center(t_i) = center_mas + (t_i - reference_epoch_yr) * proper_motion_mas_yr
              + (1000 / D_l_pc) * lens_parallax_factors[i]
```

Thus `center_mas` is the linear-track reference center before the supplied parallax offset. Proper motion is **mas per observer year**. A physical transverse velocity requires the corresponding distance/redshift conversion. A drifting or uncertain astrometric frame affects the inferred motion and is not estimated implicitly.

### Observed versus synthetic provenance

For real measurements set `provenance.kind` to `"observed"` and retain their origin, citation/data release, instrument, reduction, coordinate/time conventions, image identification, flux treatment and covariance construction in that object. These extra keys are metadata, not a substitute for validated reduction. Setting the label does not verify an observation or establish a detection. Keep simulated modifications labeled synthetic, with a seed and an explanation of what was simulated. None of the bundled examples is an observed object.

## Python API

```python
from bhtracker import load_dataset, predict, fit
from bhtracker.examples import make_example
from bhtracker.inference import profile
from bhtracker.report import export_result

raw, _ = make_example("nearby_motion")
data = load_dataset(raw)                         # also accepts a JSON path
result = fit(data, family="gr", nuisance="shear", starts=3)
parameters = result["_internal"]["parameters"]   # includes fitted source rows and reference basis
predicted = predict(data, parameters, family=result["model"]["family"])
interpretation = result["bhsm_interpretation"]
spherical_boundary = interpretation["spherical_boundary"]
curve = profile(data, result, parameter="mass_msun", points=11)
export_result(result, "user_runs/python_fit")
```

`predict` returns an `N × 6` NumPy array in the documented physical-unit order. Its parameters include positive `mass_msun`, `center_mas[2]`, `proper_motion_mas_yr[2]`, and `source_mas[N,2]`. Optional fields are `shear[2]`, `compact_quad[2]`, scalar `convergence`, R1 `flux_ratio`, and R1 `boundary_amplitudes[2 or 3]` in the plus/cross/axial harmonic basis. Alternatively supply `conormal_coefficients[2 or 3]`; the exact impedance maps them to amplitudes. If both are supplied they must agree. `reference_mass_msun` preserves the numerical basis when replaying fitted parameters; the saved `_internal.parameters` carries it. Public prediction checks physical admission. A formal potential-operator test with nonadmitted coefficients is not a public physical prediction.

Shear uses the potential `0.5*gamma_plus*(x*x-y*y) + gamma_cross*x*y`; `compact_quad` multiplies the two ordinary `r^-2` harmonics in the reference lens coordinates. `fit` always fits mass, center, proper motion and all source positions. It fits the requested finite nuisance family, not arbitrary environmental structure. Inspect `model.fitted_parameters`, `model.bounds_internal`, the numerical reference scales and diagnostics for the actual fit domain.

Result schema version 1 includes `status`, `estimates`, `uncertainty`, `chi2`, `dof`, `diagnostics`, `model`, `predictions`, `physics_admission`, `bhsm_interpretation` and `conditional_envelope`. Local coordinate uncertainties are 1σ; the mass interval named `mass_68pct_interval_msun` is a local log-Gaussian interval. Null directions return JSON `null`, not zero uncertainty. The parameter covariance uses the supplied known measurement covariance without reduced-χ² rescaling. The full result also retains measurements, source positions, covariance, branch checks, singular values, runtime and dataset hash.

### Core/surface interpretation revision and discovery use

Version **0.2.0rc2** fixes trajectory endpoint year labels without rounding supplied integer or fractional epochs. It adds interpretation schema **2** inside the existing result schema 1; the separate measurement-input schema stays unchanged. Existing interpretation fields remain present. The additive `core_surface` dictionary is read from one hash-checked `theory/BHSM_CORE_SURFACE_CONTRACT.json` adapter and shared by fit/API/CLI, the app, notebooks and JSON/HTML/replay exports. Its dated source amendment is packaged in `theory/bhsm_sources/` and pinned to an exact BHSM repository revision in `BHSM_INTERPRETATION_MANIFEST.json`.

Norman P. Carberry's 22 October 2026 proposal distinguishes abstract core harmonic relationships from spacetime-side fields and interfaces. The core has no ordinary internal metric, clock, trajectory or propagation speed. Surface Berger–Hopf harmonics retain their declared geometry. The inherited differential, formation, boundary dominance and terminal transition are distinct questions. Existing regular carrier/attachment/response constructions are retained; they are not silently a terminal core-transfer law. The expandable theory section carries the attributed ontology, matching scope and claim ledger. The main result remains the mass/motion fit and its declared boundary representation.

Machine status `PROPOSED_NOT_INFERRED` is interpretation provenance, not a new observed class. `core_parameters_fitted` and `new_optical_term_added` are false. Underived core modes, interface strength, daughter channels, conversion rate, horizon and neutron-star endpoint remain `NOT_INFERRED` with JSON `null` and a reason. They are not rendered as an empty control grid. Old result dictionaries without the additive metadata retain their original report view. Replaying an older complete analysis evaluates the current interpretation and reports original/current interpretation schemas and whether it changed; it does not rewrite the saved original bundle.

The engine is intended to help identify previously uncatalogued compact lenses and black-hole candidates from supplied observations. For an observational candidate, supply actual associated primary pairs, full covariance and justified geometry/frame/flux/delay calibration, then inspect identifiability, residuals, branch/domain admission and alternative source/environment models. Catalogue novelty and additional observations distinguishing unresolved stellar systems, multiple lenses and other compact interiors must be evaluated separately. This specialist engine does not acquire raw sky images or infer a horizon from a track. No non-GR residual is required for its BHSM interpretation.

### BHSM interpretation and fixed-radius boundary output

Version 0.2.0rc1 also retains `dataset_input` (the full original input and calibrations), `analysis_configuration` (family, nuisance, starts, evaluation budget and explicit initial values) and `software_provenance` (runtime versions and installed file hashes). `export_result` writes a replay directory; `export_analysis_bundle` returns its ZIP bytes. `replay_analysis(path, output)` checks all manifest hashes before fitting `dataset.json` with `analysis_config.json`. Replay requires the same scientific status and predicted observable differences at most 0.001 of the supplied marginal standard deviation. This numerical comparison never alters the covariance; `replay_check.json` reports version/content changes and the measured difference.

`bhsm_interpretation` contains `framework`, `model_role`, `one_potential_rule`, a `parameter_meanings` list, `inference_scope`, `conditional_extension`, `weyl_convention`, `source_provenance` and `spherical_boundary`. Each parameter entry gives its `parameter`, `interpretation` and `qualification`. These metadata explain the fitted physical configuration without changing the likelihood, adding a second mass or requiring a non-GR residual.

For an admitted ordinary fit with supported mass, `spherical_boundary.status` is `AVAILABLE`. It is the **static spherical Schwarzschild equivalent of the ordinary monopole**, with flat Euclidean reference subtraction on a static spatial slice, evaluated at `model.r0_pc`. It is not the boundary energy of the complete nonspherical lens/environment. At fixed radius `R`, write `m = G*M_opt/c²` and `f = 1 - 2m/R > 0`. The principal extrinsic-curvature deficit of the enclosing sphere is `delta_k = (1 - sqrt(f))/R`, and Brown–York energy satisfies `E_BY/c² = (c²*R/G)*(1 - sqrt(f))`. Its inverse gives the same optical mass: `M_opt = E_BY/c² - G*E_BY²/(2*c^6*R)`.

| `spherical_boundary` field | Units / meaning |
|---|---|
| `radius_pc` | Fixed enclosing radius `R` in pc; not inferred from the lens fit. |
| `curvature_deficit_pc_inverse` | Principal extrinsic-curvature deficit of the enclosing sphere `delta_k`, pc⁻¹. |
| `curvature_deficit_sigma_pc_inverse` | Local propagated 1σ error on `delta_k`, conditional on fixed `R`, or `null`. |
| `boundary_energy_over_Msun_c2` | `E_BY/(M_sun*c²)`, equivalently `E_BY/c²` in solar masses. |
| `boundary_energy_sigma_over_Msun_c2` | Local propagated 1σ error on that mass-equivalent boundary energy, conditional on fixed `R`, or `null`. |
| `mixed_curvature_velocity2_km2_s2` | Same spherical monopole's `G*M_opt/R`, in km²/s². |
| `reconstructed_monopole_msun` | Optical monopole recovered from the inverse boundary-energy identity, in solar masses. |
| `geometry`, `qualification` | Reference subtraction, spherical-equivalent interpretation and its limitations. |

For the seeded noisy `nearby_motion` example with the supplied `R = 0.0001 pc`, an ordinary shear fit gives approximately `M_opt = 99947.20 ± 38.70 M_sun`, `delta_k = 0.478300 ± 0.000185 pc⁻¹`, and `E_BY/c² = 99949.59 ± 38.70 M_sun`. These are one synthetic realization's outputs. The boundary energy is radius dependent; its small difference from the conserved monopole is the standard gravitational boundary relation, not a new source of mass.

The propagated errors use `sigma(E_BY/c²) = sigma(M_opt)/sqrt(f)` and `sigma(delta_k) = G*sigma(M_opt)/(c²*R²*sqrt(f))`. They add no independent information and do not include uncertainty in `R`. Set `analysis.r0_pc` for an explicitly declared physical representation radius. If it is omitted, the computational radius policy in `model.worldtube_policy` remains explicit; it is not a measured surface. Changing the enclosing radius is not physical mass drift.

Rejected fits and unresolved masses suppress this numeric representation. R1 returns `NOT_ASSUMED_FOR_R1_METRIC` with its reason: the Schwarzschild identity is not inserted into a modified metric. Its boundary energy would require the appropriate R1 metric and reference subtraction.

### Interpret statuses before using estimates

| Status | Interpretation |
|---|---|
| `TRACKED` | The fit converged, passed the declared goodness-of-fit/domain checks, has sufficiently identified mass and a two-component motion SNR of at least 5, and is not downgraded by an active global bound. It remains conditional on the supplied model/calibration. |
| `PARTIALLY_IDENTIFIED` | Motion is weak or unresolved, or a global modeling bound qualifies the result. A mass can still be informative. Inspect diagnostics and profiles. |
| `INSUFFICIENT_INFORMATION` | Mass is unidentified or its local log uncertainty exceeds the product's 0.5 threshold. Do not force a track from this input. |
| `FIT_REJECTED` | Optimizer, physical-domain or goodness-of-fit checks failed; the predeclared goodness-of-fit rejection threshold is `p < 0.001`. Treat the parameter estimates as a failed model fit. |

The motion threshold concerns the **joint two-component** Mahalanobis SNR, not a requirement that each component separately exceeds five standard deviations. An optimizer success flag alone is not a scientific acceptance. Rank truncation, active bounds, approximation budgets and residual mismatch can qualify the result. Local errors and profile reference levels have a finite tested domain; they are not universal interval-coverage guarantees.

## Conditional R1 policy

The exterior-wide bound is **sufficient**, not necessary. Exceeding its cap is outside the proved guarantee and the product's admitted domain; it does not prove physical impossibility. Retained principal-sign control is separate from full-system stability, a nonlinear solution-error bound, horizon regularity and ultraviolet completion.

R1 is an adopted weak-metric, frozen-background, quasistatic scalar–tensor exterior outside a supplied worldtube. Its pinned background covers lens redshifts `0 <= z_l <= 2.1`. The code computes admission information, the normalized boundary/conormal pairing and a sufficient state-norm cap; it does not derive a black-hole horizon charge or a preferred deformation amplitude.

In an R1 fit, `mass_msun` is the adopted action's **metric/source mass parameter**. The optical response also includes the action-derived scalar term. Its relation to the ordinary model's effective point-exterior monopole must therefore be evaluated through that total response; the two mass labels are not interchangeable by relabeling. The R1 term supplements the reference configuration only once, with its fixed scalar-to-metric normalization and stated matching assumptions.

| `analysis.flux_provenance` | Fit policy |
|---|---|
| `"regular_body_proxy"` | Hold `analysis.flux_ratio` fixed (normally 1); report `fixed_regular_body_proxy`. This is an explicitly adopted proxy, not a horizon matching result. |
| `"supplied_conditional_flux"` or `"supplied_worldtube_flux"` | Fit the scalar flux as a conditional matching nuisance over the declared ratio interval `[0.05, 20]`; report `fitted_conditional_flux`. |
| Missing/other value | Conditional R1 inference is not admitted. Baseline GR does not require scalar provenance. |

`flux_ratio` in parameters or analysis always means **scalar-source normalization**, whereas the measurement `ln_flux_ratio` means image magnification ratio. Changing the R1 policy changes the statistical model; retain it in a comparison.

The nonlinear R1 fit estimates its spherical exterior and ordinary nuisances. The boundary envelope is then a **local GLS information assessment** after source/lens and axial profiling, with an admitted amplitude cap. It is not an unconstrained nonlinear measurement of a surface deformation. Read `physics_admission.reasons`, `allowed_physics_models`, `model.flux_policy` and `conditional_envelope` together.

Envelope status `UNRESOLVED` means the admitted design has weak or rank-deficient information. `NOT_EVALUATED` means the baseline fit was rejected; no envelope sensitivity is interpreted. `NOT_ADMITTED` means the domain checks disallow that inference; `NOT_REQUESTED` is the GR default. `INFORMATION_AVAILABLE` describes local information under the declared model and cap; it is not a detection claim. An unconstrained amplitude estimate outside the admitted ball is not a physical R1 state measurement. The exact zero-flux harmonic/ordinary-compact degeneracy remains a cause ambiguity.

## Executed notebooks and validation

The notebooks are saved with executed outputs; their cell counts and SHA-256 hashes are recorded in `validation/notebook_receipt.json`:

| Notebook | Walkthrough |
|---|---|
| `notebooks/01_compact_mass_and_motion.ipynb` | Full-covariance ordinary fit, BHSM interpretation and fixed-radius spherical boundary output, center track, reoptimized mass profile, weak-motion control and portable exports. Six code cells. |
| `notebooks/02_conditional_boundary_response.ipynb` | Same-potential BHSM reporting contract, conditional R1 fit, physical admission, Dirichlet/conormal cap, unresolved envelope and rejection of an inadmissible state. Five code cells. |
| `notebooks/03_native_unresolved_photometry.ipynb` | Native OGLE import, all-row fit/residuals and export/refit replay. Four code cells; actual external observations when configured. |
| `notebooks/04_joint_astrometry_and_parallax.ipynb` | Verified 2023 source import, recorded conditional joint fit/profile audit, all-row plots and forward-state replay. Five code cells; no automatic measured fit or accepted mass claim. |
| `notebooks/05_candidate_atlas.ipynb` | All 155 source/events, three differently qualified targets, separate literature benchmark, explicit unavailable lens quantities and exact UTF-8 inventory replay. Six code cells; no physical fit. |

Open them in an editor with Jupyter support and select the environment in which this product is installed. With development dependencies installed, replay them and the product checks from this source directory:

```text
python scripts/execute_notebooks.py
python scripts/validate_product.py
```

Notebook replay uses the `python3` kernel through `nbclient`, updates the notebooks and writes its receipt. Ensure that kernel can import this installation. Validation runs pytest, the frozen 64-draw calibration and the exact finite harmonic/compact operator control, and writes stage logs, full calibration/operator receipts and code hashes under `validation/`. The companion paper's `review` directory contains the detailed preregistered protocol and a delivery snapshot of these receipts.

The fixed ordinary-lens calibration retains all 64 draws and failures, uses known full covariance and local 95% intervals, and applies exact binomial gross-miscalibration tests at α = 0.01. Its observed coverage is 61/64 for mass and both motion components, 59/64 for center x and 61/64 for center y; no fit failures were excluded. The receipts report bias, scatter, small-sample uncertainty and negative controls. Passing this bounded test does not prove universal coverage or observational performance.

## Attribution and limits

The BHSM/R1 research and companion manuscript are by **Norman P. Carberry**. `bhtracker/theory/BHSM_INTERPRETATION_MANIFEST.json` identifies the packaged, hash-checked BHSM boundary/source records used for the ordinary interpretation. The Brown–York construction is established gravitational theory: [Brown and York, Physical Review D 47, 1407–1419 (1993)](https://arxiv.org/abs/gr-qc/9209012); its use here represents the same ordinary gravitational monopole.

The adopted R1 provider is pinned to Manuscript-Generation commit `06cf7c1b85d6605bfee0cc0d07fb2af86a66cae9`. `bhtracker/theory/provider/SOURCE_MANIFEST.json` gives original paths, source URLs and hashes; `bhtracker/theory/ADAPTATION.json` records the product adaptation and consistent nominal solar gravitational parameter. Runtime-used provider inputs are checked on loading; release checks verify all six pinned provider files. NumPy, SciPy and Matplotlib supply the numerical and plotting libraries; the development tools include pytest, nbformat, nbclient and ipykernel.

Ordinary point-lens inference, astrometric tracking and Galileon multipoles have established predecessors. The package does not claim that a software tracker is itself a new physical discovery. The companion paper separates its conditional boundary-to-lensing transfer and blind-direction results from the practical inference product and from earlier information experiments.

The primary-pair model continues two noncritical point-lens image branches, checks stationarity/parity/time ordering and keeps rays outside the worldtube. It does not enumerate every image of a general lens, solve full caustic-crossing events, model arbitrary macro lenses, propagate unknown calibration, provide an Earth ephemeris, derive causal horizon/surface evolution, or select a microscopic BHSM-to-action map. Source variability, extinction, small-scale microlensing and other causes of a changed flux/delay pattern require their own measurement/model treatment. Equivalent exterior potentials remain indistinguishable by these observables alone.

Use the estimates, uncertainty, physical-admission result, residual diagnostics, provenance and declared bounds as one research result. A valid outcome can be an identifiable compact-mass track, a rejected model, an unresolved motion, or a conditional envelope limit.
