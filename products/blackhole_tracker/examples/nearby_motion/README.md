# BHSM Blackhole Tracker: nearby synthetic example

This bundle contains one synthetic dataset, represented losslessly in two formats.
It contains measurements and supplied covariance, not precomputed fit results.
The provenance in dataset.json remains the authority for the input's origin.

## First run in the local app

1. Import dataset.json, then choose Validate dataset.
2. Keep Ordinary lens response selected and run the fit.
3. Read the supported/unresolved/rejected outcome, local uncertainties and
   synthetic/observed provenance. Inspect residuals and supplied calibrations.
4. Download a replay bundle to retain input, configuration and the result.

## Recreate the native input from CSV

With the package installed, run in this directory:

    python -m bhtracker import-csv measurements.csv --metadata metadata.json --covariance full_covariance.csv --output imported.json
    python -m bhtracker validate imported.json

Import imported.json in the app. Do not import a CSV as native JSON.

## Files, units and order

- dataset.json: the native version-1 input, including all supplied metadata.
- measurements.csv: epoch_yr followed by the six named observable columns.
- metadata.json: the same native metadata without the three numeric arrays.
- full_covariance.csv: headerless dense 54 by 54 matrix for 9 rows.
- manifest.json: SHA-256 hashes of the other bundle files.

The six observable columns, in canonical covariance order, are:
  x_plus_mas, y_plus_mas, x_minus_mas, y_minus_mas,
  ln_flux_ratio, delay_seconds

Positions are mas in one supplied tangent-plane frame. Plus/minus mean positive
and negative parity, not bright/faint. Log flux ratio is ln(|mu_plus|/|mu_minus|).
Delay is arrival_time_minus - arrival_time_plus in seconds. Epochs and proper
motions use observer years. Distances in geometry are angular-diameter pc.
Distances, redshifts, clock/frame and optional observer factors are supplied
calibrations; this model does not fit their uncertainty.

The covariance flattens each row's six observables before the next row. Its
diagonal contains variances; mixed/cross-row entries retain their product units.
It has no epoch-error row/column. Preserve row order or permute both covariance
axes in six-element blocks. Never replace this matrix with independent errors.

The BHSM interpretation describes the same optical mass, location and motion;
equivalent gravity and envelope descriptions are counted once. A boundary
radius is a declared representation choice, not a measured horizon. R1 is an
advanced conditional model and is not required for the ordinary interpretation.
