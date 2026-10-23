# Blackhole Tracker: research paper and usable product

The current manuscript is **Blackhole Tracker: BHSM Boundary Interpretation of Compact-Lens Mass, Motion, and Conditional Response**. It accompanies a runnable specialist product for inference from resolved image pairs, flux ratios and delays. The ordinary fit reconstructs an effective BHSM-described exterior in the adopted Einstein/GHY sector; an observable departure from GR is not required. The earlier boundary-transfer and broad information experiment remain in the paper as distinct theoretical results; the preserved angular and Hopf papers remain supporting research.

The formal reviewer source is [BHSM draft PR #470](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/pull/470), branch `codex/norman-core-surface-amendment-20261022`. Its canonical paths are `products/blackhole_tracker/` for the product and `papers/bhsm_blackhole_tracker_20261021/` for this paper. [Manuscript-Generation PR #24](https://github.com/ncarberry64/Manuscript-Generation/pull/24) is the workspace/history record. The immutable formal code snapshot is `33f26a5113392c0d2c323d7e4a36c7e81bd3ee29`; the external delivery receipt binds the final paper revision and artifact hashes.

The package establishes three connected results:

- A local GUI, CLI, Python API and two executed notebooks reconstruct the mass, center and observer proper motion of the BHSM-described compact exterior, retaining the full supplied covariance and free source positions. The same monopole can have the conventional point-lens potential. Negative or unresolved results are explicit outputs.
- A uniform sufficient bound controls all five normalized quadrupole coordinates throughout the retained R1 exterior, preserving its scalar principal signs within declared budgets. The exact Dirichlet/conormal pairing gives the corresponding source bound. This is a conditional local-action result, not full-system or horizon stability.
- The normalized boundary-to-metric-to-lensing transfer has explicit information losses: two line-of-sight modes vanish; the leading screened primary-pair delay response vanishes; and its first-order apparent-mass response is degenerate with external shear. The old joint-response experiment retains information discarded by the scalar statistic within its declared finite nuisance family.

## BHSM boundary interpretation: one mass, one potential

The recovered BHSM sources explicitly adopt Einstein gravity with GHY-completed boundary variation. They derive the spherical curvature deficit and normalize a mixed surface scalar; the v14.25 record evaluates a conditional Brown–York interface charge and prohibits adding the same gravitational energy twice. The [new manuscript section](manuscript/bhsm_interpretation.tex), [source-grounded dictionary](provenance/bhsm_boundary_mass_interpretation.md) and [hashed source ledger](provenance/bhsm_boundary_mass_interpretation_sources.json) give the exact provenance and assumptions.

For the static Schwarzschild member, put `m=GM/c²`, `f=1-2m/r` and choose an areal worldtube radius `r>2m`. With a flat reference:

```text
delta k_g = (1-sqrt(f))/r
M = (c²/G)[r² delta k_g - r³ delta k_g²/2]
E_BY = (c^4 r/G)(1-sqrt(f))
M = E_BY/c² - G E_BY²/(2c^6 r)
Q_Sigma = (c²/8pi) integral H kappa_acc dA = GM/r
```

Thus the fitted monopole is equivalently encoded by boundary curvature/charge. It supplies the same Weyl potential and is counted once; no second “BHSM mass” is added. Brown–York energy depends on the enclosing radius and reference, while M is the conserved mass of this spherical solution. Changing the chosen radius is not physical mass drift. A computational default radius is not an observed surface. These identities are a BHSM gravitational-sector interpretation, not a microscopic state-selection or horizon derivation. With a distinct non-Schwarzschild R1 contribution, the complete metric/source matching must replace a blind application of the Schwarzschild dictionary.

Interpretation schema 2 records Norman P. Carberry's 22 October 2026 amendment: abstract harmonic core data have no ordinary internal spacetime, while spacetime-side dynamics and enclosing-surface quantities retain their declared geometry. The app separates fitted, derived and proposed statements, with detailed theory and exact source provenance expandable. Existing regular-side reconstruction/attachment/response results are retained; their extension to terminal core transfer requires a selected admissible matching map and charge/flux accounting. This update supplies no new optical term, measured core parameter, horizon classification or terminal rate.

## Use the product

Read `products/blackhole_tracker/README.md` in the formal BHSM checkout for the Windows double-click launcher, installation, local app, CSV/JSON import, exact covariance order, CLI fitting/profiles, Python API and notebooks. The standalone product source ZIP retains its self-contained `product/README.md` layout; the historical Manuscript-Generation workspace also uses top-level `product/`. These are packaging/development layouts, not competing reviewer authorities. The installed product needs no private research archive, remote fitting service or API key.

The ordinary compact-lens mode is usable within its validated synthetic domain as inference of that BHSM-described optical configuration. It can identify a supported mass/motion track, reject an inadequate model or report unresolved motion. The optional R1 extension tests a distinct conditional response; it is not a condition for ordinary BHSM utility. It does not establish that a compact dark source has a horizon. All bundled data are synthetic, including the published-parameter stellar variation.

The frozen 64-draw full-covariance calibration completes without excluded fit failures. Nominal local 95% coverage is 61/64 for mass and both motion components, 59/64 for center x and 61/64 for center y. Exact binomial tests at the fixed alpha=0.01 reject none; finite-sample uncertainty and bias remain reported. The short cosmological control stays motion unresolved, and omitting conventional shear rejects the fit. The optional R1 envelope stays far below the nearby example's supplied noise at its admitted state cap.

## Completed rc2 integration checks

The installed `0.2.0rc2` wheel and browser assets carry the shared schema-2 interpretation and hashed amendment sources. API/CLI/report consistency, ordinary/rejected/unresolved/R1 output handling, legacy report rendering and exact source bytes passed the [independent installed review](review/RC2_INSTALLED_USABILITY_REVIEW.md). Actual browser downloads, installed CLI replay and both executed notebooks are recorded in the release receipts. The GUI/API/CLI/notebook comparison has identical supplied values/configuration/interpretation and zero predicted-observable differences. The rc1-to-rc2 replay records changed interpretation/provenance, rather than claiming historical metadata is identical. The endpoint labels now retain the actual years 2015 and 2025.

The amendment adds interpretation metadata and source material, not a changed likelihood or new fitted physics. The prior fixed calibration and historical receipts remain preserved; that campaign was not restarted for this update. Final-head CI and artifact/code hashes are reported against their actual formal delivery commits in the external receipt.

The subsequent full reviewer audit corrected uploaded duplicate-key handling, nonnumeric JSON coercion and lost-job recovery, and clarified independent-source plots. The rebuilt installed wheel has SHA256 `323bcf675f6fe1c1262e85be49644d3736c2777788ecf2f92568f1cc6ba92ae3`; unchanged valid predictions, likelihood and uncertainties remain exactly equal. The complete product suite passed 133 tests, including 17 new typed-input cases. The [review addendum](review/RC2_INSTALLED_USABILITY_REVIEW.md) distinguishes this final wheel and full-review receipt from the earlier rc2 bytes and records installed rejection/recovery, canonical BHSM citations and exact export/replay. No runtime usability blocker remains in those reviewed flows; this does not imply journal acceptance or a new physical detection.

## Reproduce the separate calculations

From `products/blackhole_tracker/` in the formal checkout (or the self-contained source product directory), install its development dependencies and run:

```text
python -m pip install -e ".[dev]"
python scripts/validate_product.py
python scripts/execute_notebooks.py --kernel-python /absolute/path/to/installed/python --work-directory /path/to/fresh/notebook-output
```

Replace the two notebook paths with your installed interpreter and an output directory. For the Windows environment in the product guide, the interpreter is `.venv/Scripts/python.exe`; on Linux it is `.venv/bin/python`. This selects the intended installation explicitly rather than relying on whichever interpreter a previously registered `python3` Jupyter kernel uses. Notebook execution updates the notebook files and writes its receipt; preserve the supplied executed versions if you want an unchanged reference copy.

Product stage logs, hashes and machine receipts are under the product's `validation/` directory; the paper's `review/` contains the protocol and delivery snapshots. The notebooks replay the workflow rather than replace calibration. `validate_product.py` includes the historical 64-draw calibration, so it is a full reproduction command rather than a requirement for a first app run. These full validation commands were not all rerun solely for the rc2 metadata update.

The original theory replay remains independent. Keep the sibling `bhsm_angular_lensing_20261021` directory containing its exact archived provider. From this paper directory, with `requirements.txt` installed, run:

```text
python scripts/reproduce.py
```

Its nine stages check pinned inputs, the source/radial/projection equations, estimator nulls, nonlinear image derivatives, nuisance projection and figures. Logs are under `results/` and `review/`. The old 54-component, 30-nuisance scan uses equal dimensionless errors, not a telescope covariance; its broad trajectory would require millions of years for the cosmological example. It is not the product's ten-year calibration fixture.

From `manuscript/`, compile with:

```text
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Read `RESULT_STATEMENT.md`, `LAY_REPORT.md`, `VALIDATION.md`, `CHAIN_AND_FREEDOMS.md`, the provenance map and internal reviews for scope and evidence. This is an author-review draft for *Galaxies*, not a submitted or accepted article. No journal submission or external contact has occurred.
