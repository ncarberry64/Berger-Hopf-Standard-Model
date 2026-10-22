"""Lossless measurement examples in native JSON and the supported CSV contract."""
import csv
import hashlib
from io import BytesIO, StringIO
import json
import zipfile

from .data import FIELDS, load_dataset


def _csv(rows):
    stream = StringIO(newline="")
    csv.writer(stream, lineterminator="\n").writerows(rows)
    return stream.getvalue().encode("utf-8")


def build_sample_bundle(dataset, title="BHSM Blackhole Tracker example"):
    """Validate once and return a ZIP containing one dataset in both formats.

    Rows and every full-covariance entry are preserved. The input is copied by
    load_dataset; this helper adds no noise, independent-error approximation,
    fitted result or synthetic truth. ZIP member names never depend on input.
    """
    data = load_dataset(dataset)
    raw = data.raw
    metadata = {key: value for key, value in raw.items()
                if key not in {"epochs_yr", "observations", "covariance"}}
    kind = raw["provenance"]["kind"]
    size = 6 * data.n
    guide = f"""# {title}

This bundle contains one {kind} dataset, represented losslessly in two formats.
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
- full_covariance.csv: headerless dense {size} by {size} matrix for {data.n} rows.
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
"""
    files = {
        "dataset.json": (json.dumps(raw, indent=2, allow_nan=False) + "\n").encode("utf-8"),
        "measurements.csv": _csv([["epoch_yr", *FIELDS],
                                  *[[epoch, *row] for epoch, row in zip(raw["epochs_yr"], raw["observations"])]]),
        "metadata.json": (json.dumps(metadata, indent=2, allow_nan=False) + "\n").encode("utf-8"),
        "full_covariance.csv": _csv(raw["covariance"]),
        "README.md": guide.encode("utf-8"),
    }
    manifest = {"schema": "bhtracker.example_bundle.v1", "dataset_sha256": data.sha256,
                "provenance_kind": kind, "rows": data.n,
                "files": {name: hashlib.sha256(payload).hexdigest() for name, payload in files.items()}}
    files["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    stream = BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, payload in files.items():
            member = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            member.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(member, payload)
    return stream.getvalue()
