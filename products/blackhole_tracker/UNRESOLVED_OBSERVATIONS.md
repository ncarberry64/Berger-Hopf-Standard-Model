# Native unresolved observations, schema 1

This route fits published apparent magnitudes directly. It preserves the
resolved-image tracker and does not construct image positions, an image flux
ratio, an interimage delay, distances or a measured covariance from a light
curve. Its result schema is `bhsm_unresolved_photometry_result/1`; the BHSM
interpretation remains schema 2.

```python
from bhtracker.observations import load_ogle_photometry
from bhtracker.photometry import fit_photometry, predict_photometry, profile_timescale

data = load_ogle_photometry("photBLG100.3.I.144687.dat", metadata={
    "event_id": "OGLE3-ULENS-0033", "ra_j2000": "17:52:01.31",
    "dec_j2000": "-29:53:56.2", "ews_alias": "2004-BLG-281"})
result = fit_photometry(data)  # all rows, 12 deterministic starts
prediction = predict_photometry(data, result["parameters"])
profile = profile_timescale(data, result, [150, 200, 300, 500])
```

`parse_ogle_photometry(content: bytes, source_name=..., metadata=...)` is the
equivalent upload API. `load_benchmark_photometry({"OGLE": path, "MOA": path})`
and `parse_benchmark_photometry({name: {"content": bytes, "source_name": str}})`
read the 2022 Zenodo benchmark with distinct instrument calibration terms.

## Observation identity, timing and calibration

`UnresolvedPhotometry.to_dict()` returns `bhsm_unresolved_observations/1`.
The document contains the observable `apparent_magnitude`, instruments,
source-file records, native rows, contextual metadata and an explicit
transformation history. `from_dict()` validates the schema. Its canonical
JSON SHA-256 is distinct from each immutable raw-file SHA-256.

Every row retains `native_time`, `magnitude`, `magnitude_error`, instrument,
source filename, raw SHA-256, one-based source line and the identity
`<raw SHA-256>:<source line>`. Quality flags are retained. There is no complete
resolved-row limit, silent thinning, outlier clipping, averaging or duplicate
deletion. Times remain in source-row order; diagnostics sort a separate index.
Duplicate times and nonmonotonic order are reported. The exact OGLE annotation
`ERROR: data not sorted in HJD!` is retained as provenance. Other malformed rows
fail with filename and line. The exact plain-text Zenodo column header is
recognized only before measurements and also retained as provenance.

OGLE-III optimized times are HJD minus 2450000 in days. Zenodo OGLE/MOA times
are full HJD. `.times` uses declared numeric-origin arithmetic to a common
2450000 origin; native values remain unchanged. HJD's underlying clock scale
is explicitly `UNSPECIFIED`. Subtracting an origin is neither a clock conversion
nor a heliocentric/barycentric transformation. The combined benchmark records
the limited assumption that published HJD days share an adequate relative axis
for a rectilinear screen. It does not certify clock equivalence for parallax.

Each instrument records filter, magnitude convention, time metadata, calibration
and error treatment. OGLE optimized errors already include the publisher's
correction, which is not reapplied. Per-point errors are not a supplied full
covariance. The analysis explicitly assumes independent Gaussian errors in
native magnitudes. No approximate Gaussian flux errors are constructed.

`load_ogle_catalog()` parses the actual 26 physical fields. It preserves EWS
and overlap aliases and all deduplicated primary events, including 0337.
V=99.999 and V-error=9.999 become unavailable. Catalog fitted values remain
selection/initialization metadata, not additional likelihood measurements.
`reproduce_pilot_selection(catalog, manifest)` verifies parent bytes, counts,
hash-selected controls, all 100 identities and the canonical selection SHA-256.

## Likelihood, search and identification

The trajectory has `u²=u0²+((t-t0)/tE)²` and image-summed
`A=(u²+2)/(u sqrt(u²+4))`. For instrument j,
`Fj=Fs,j*A+Fb,j`, evaluated as
`mj=mbase,j-2.5 log10(1+fj*(A-1))`, with `fj=Fs,j/(Fs,j+Fb,j)`.
The baseline bounds enforce positive source light and nonnegative blended
stellar light. Source and blend relative fluxes have an arbitrary per-instrument
zero point and must not be interpreted as independently calibrated luminosities.

The exact versioned defaults and their SHA-256 are available as
`FIT_PROTOCOL` and `FIT_PROTOCOL_SHA256` in `bhtracker.photometry`. The baseline
uses 12 deterministic starts, an analytic Jacobian, linear least squares in
native magnitude residuals and unchanged published sigma. Bounds are tE
0.1–10000 days, u0 0.0001–10, source fraction 0.000001–1, t0 one data span
outside either end of the measured span, and instrument baseline median ±10
magnitudes. These are declared model/search restrictions, not inferred limits.
Optimization uses a median-relative epoch internally and returns `t0` relative
to the dataset's declared common numeric origin. The log tE/u0 coordinates and
full local covariance are transformed back to the public parameter basis.

`allow_negative_blend=True` is a separate phenomenological calibration-offset
sensitivity, allowing source fraction up to 10 while predicted total flux
remains positive. It does not assign negative luminosity to a physical star.
`noise_scale` is a declared uniform error sensitivity. With multiple instruments,
`equal_instrument_weight=True` equalizes their total residual weight; this is
an alternative objective, not the original independent-noise likelihood or an
exact reproduction of any historical publication's equal-weight procedure.

The result separately reports optimizer convergence, multistart confirmation,
photometric admission, observational adequacy, local information rank and active
bounds. Native chi-square and instrument residual diagnostics remain available
even when a sensitivity uses a different objective. Reports include constant
and linear-trend comparisons, sorted residual runs/correlations, seasonal
offsets and counts above 3 sigma. These screens have no calibrated search-wide
false-discovery interpretation. A failed PSPL screen can reflect outliers,
correlated calibration, intrinsic variability, parallax or binary structure;
it does not support a black-hole or BHSM-specific claim by itself.

Local inverse-information errors condition on the adopted noise model. Public
null-affected covariance entries and errors are unavailable, and the associated
null directions/projector are supplied separately. Low significance and
non-identifiability differ. Active boundaries, modes, near-degeneracies and
failed residual screens qualify local errors. `profile_timescale` genuinely
reoptimizes admissible nuisance states at each declared timescale from four
seeds; failure or an insufficiently solved reference is unresolved. A search
failure does not prove infeasibility. No automatic profile-interval coverage is
claimed. The calling analysis must define and preserve its interval policy.

Bare API results contain input data, analysis configuration, product and
dependency provenance, every original row identity, all predictions/residuals,
run diagnostics and a strict finite-or-null JSON representation for replay.

The photometric route may identify t0, tE, u0 and instrument flux parameters
under its model; blending and sampling can weaken even those constraints.
It leaves mass, distances, angular Einstein radius, microlens parallax, absolute
proper motion, horizon, core state and physical boundary radius unavailable.
`tE=thetaE/mu_rel` and `thetaE²=kappa*M*pi_rel` leave a mass/geometry/motion
degeneracy. Its statuses therefore use `PHOTOMETRIC_*` and `MASS_UNRESOLVED`.
The single potential keeps its BHSM Einstein/GHY interpretation without being
counted again. An ordinary light curve does not test the proposed core,
encapsulation or galaxy dark-matter mechanisms.

## Optional angular/parallax forward route and current gate

`bhtracker.astrometry` implements the independently tested point-lens centroid,
source position/proper motion/parallax, luminous blending and frame offsets.
Coordinates are explicitly north/east tangent-plane mas; u points from lens
to unlensed source. The dark centroid shift is `thetaE*u/(u²+2)`, derived
independently by summing the two image positions with their magnifications.
Luminous blending uses the actual weighted centroid of the lensed source and
the supplied blend position, not an extra lens displacement.

The geocentric parallax helper requires observer **heliocentric** positions and
velocities in ICRS Cartesian axes, subtracts their reference position/velocity,
projects minus that residual into NE and uses Gould's signed dot/cross convention.
Barycentric ephemerides require subtracting the Sun's barycentric vectors first;
the coordinate origins cannot be silently mixed. Callers must supply a verified
observer ephemeris, native-to-ephemeris time transformation, reference position
and velocity, and sky coordinates. This release performs no guessed UTC/HJD
conversion or ephemeris interpolation. These are optional validated forward
building blocks, not a certified joint angular mass-recovery fitter.

Gould's returned `(tau,beta)` is the **lens relative to source** in a trajectory
basis; it is not the centroid's source-minus-lens NE vector. With lens-motion
angle alpha east of north, set `n=(cos(alpha),sin(alpha))` and
`b=(-sin(alpha),cos(alpha))`, then `u_NE=-tau*n-beta*b`. Nonzero vector piE fixes
`n=(piN,piE)/|piE|`; zero piE requires a separately declared motion direction.
Do not directly feed the two returned trajectory components into the centroid.
Their norm alone suffices for unresolved photometric magnification. The supplied
observations do not pass the precision gate, so no composed joint fit is claimed.

`load_hst_astrometry` preserves all 16 native rows at eight shared epochs in
the two 2022 filters. It assigns no guessed MJD origin, RA*cos(Dec) convention,
cross-filter correction, frame covariance or independent-visit count.
`precision_metadata_status`/`require_precision_metadata` enumerate and enforce
the required time, frame, calibration, noise and ephemeris provenance before
precision parallax or centroid predictions. Actual supplied HST metadata fail
this gate. Ingestion is useful; a precision joint fit or lens mass from these
bytes remains unresolved until their actual export-time mapping and frame
calibration are established. Already applied offsets must not be applied again.

## Validation and primary references

`tests/test_unresolved_observations.py` checks the summed-image Jacobian,
analytic likelihood derivatives, synthetic recovery/noise scaling, nuisance
profiles, strict parsers and angular/parallax conventions. Run
`scripts/validate_unresolved_observations.py --data-root <data> --output <json>`
to verify actual observation counts/selection and controlled synthetic
injections at authentic cadence/error sampling. It does not fit observed
magnitudes. Synthetic validation, historical benchmark and candidate pilot
must have separate output identities. Sixteen noise trials do not calibrate
coverage or a discovery false-positive rate.

Sources consulted 22 October 2026:

- [Paczynski (1986), ApJ 304, 1](https://articles.adsabs.harvard.edu/pdf/1986ApJ...304....1P): image-summed PSPL magnification.
- [Wyrzykowski et al. (2015), ApJS 216, 12](https://arxiv.org/html/1405.3134v4): published OGLE-III standard-event catalog and limitations; DOI 10.1088/0067-0049/216/1/12.
- [Gould (2004), ApJ 606, 319](https://arxiv.org/abs/astro-ph/0311548): geocentric parallax and degeneracies; DOI 10.1086/382782.
- [Dominik & Sahu (2000), ApJ 534, 213](https://arxiv.org/abs/astro-ph/9805360): unresolved astrometric centroid and luminous blending; DOI 10.1086/308716.
- [Gould (2000), ApJ 542, 785](https://arxiv.org/abs/astro-ph/0001421): observable mass/geometry relations.
- [Lam et al. (2022), Zenodo version 1.0.0](https://doi.org/10.5281/zenodo.6607578): the actual historical benchmark reduction, not later changed data.

Retain the source-specific attribution/rights statements with analyses. Raw
download accessibility does not imply a blanket software redistribution license.
