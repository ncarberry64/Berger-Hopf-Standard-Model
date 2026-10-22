"""CSV fidelity includes off-diagonal, cross-epoch covariance and row order."""
from copy import deepcopy
import csv
from io import StringIO
import json

import numpy as np
import pytest

from bhtracker.data import FIELDS, load_dataset
from bhtracker.importers import import_measurement_csv


@pytest.fixture
def csv_parts():
    # Deliberately unsorted and repeated epochs must not be collapsed or sorted.
    epochs = [2026.25, 2025.5, 2026.25]
    observations = np.asarray([
        [2.125, 1.25, -1.5, -0.25, 0.75, 4.125e-6],
        [3.25, 0.5, -0.75, 0.125, 1.25, 7.5e-6],
        [1.75, 2.5, -0.5, -1.25, 0.625, 3.25e-6],
    ])
    # Dense SPD C with distinct row scales and signed cross-epoch terms.
    scales = np.tile([.02, .03, .04, .05, .01, 2e-7], 3)
    correlated = np.linspace(-.17, .23, 18)
    covariance = (np.eye(18) + np.outer(correlated, correlated)) * np.outer(scales, scales)
    metadata = {
        "schema_version": 1,
        "geometry": {"D_l_pc": 1000., "D_s_pc": 8000., "D_ls_pc": 7000., "z_l": 0., "z_s": 0.},
        "reference_epoch_yr": 2026.,
        "provenance": {"kind": "synthetic", "label": "CSV round-trip control"},
        "analysis": {"lens_parallax_factors": [[.2, -.1], [-.3, .4], [.5, .6]]},
    }
    rows = [[epoch, *obs] for epoch, obs in zip(epochs, observations)]
    return metadata, ["epoch_yr", *FIELDS], rows, covariance


def csv_stream(rows, bom=False):
    output = StringIO(newline="")
    if bom:
        output.write("\ufeff")
    csv.writer(output).writerows(rows)
    output.seek(0)
    return output


def ingest(parts, header=None, rows=None, covariance=None, metadata=None):
    meta, names, measurements, matrix = parts
    return import_measurement_csv(
        csv_stream([names if header is None else header, *(measurements if rows is None else rows)]),
        deepcopy(meta) if metadata is None else metadata,
        csv_stream(matrix if covariance is None else covariance),
    )


def test_bom_path_round_trip_preserves_full_covariance_and_unsorted_rows(csv_parts, tmp_path):
    metadata, header, rows, covariance = csv_parts
    measurement_path = tmp_path / "measurements.csv"
    metadata_path = tmp_path / "metadata.json"
    covariance_path = tmp_path / "covariance.csv"
    measurement_path.write_text(csv_stream([header, *rows]).getvalue(), encoding="utf-8-sig", newline="")
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8-sig")
    covariance_path.write_text(csv_stream(covariance).getvalue(), encoding="utf-8-sig", newline="")
    raw = import_measurement_csv(measurement_path, metadata_path, covariance_path)
    assert raw["epochs_yr"] == [row[0] for row in rows]
    np.testing.assert_array_equal(raw["observations"], np.asarray(rows)[:, 1:])
    np.testing.assert_array_equal(raw["covariance"], covariance)
    assert raw["covariance"][1][15] != 0  # An actual cross-epoch term survived.
    assert raw["analysis"] == metadata["analysis"]
    assert "observations" not in metadata
    restored = load_dataset(json.loads(json.dumps(raw, allow_nan=False)))
    np.testing.assert_array_equal(restored.raw["covariance"], covariance)
    np.testing.assert_array_equal(restored.whiten(np.arange(18.)),
                                  load_dataset(raw).whiten(np.arange(18.)))


def test_named_columns_can_be_reordered_without_reordering_covariance(csv_parts):
    metadata, header, rows, covariance = csv_parts
    order = [4, 0, 6, 2, 5, 1, 3]
    expected = ingest(csv_parts)
    actual = import_measurement_csv(
        csv_stream([[header[i] for i in order], *[[row[i] for i in order] for row in rows]], bom=True),
        StringIO("\ufeff" + json.dumps(metadata)), csv_stream(covariance, bom=True))
    assert actual == expected


@pytest.mark.parametrize("kind", ["duplicate", "missing", "extra"])
def test_rejects_ambiguous_or_unrecognized_columns(csv_parts, kind):
    _, header, rows, _ = csv_parts
    if kind == "duplicate":
        header = [*header[:-1], header[-2]]
    elif kind == "missing":
        header = header[:-1]
        rows = [row[:-1] for row in rows]
    else:
        header = [*header, "delay_error"]
        rows = [[*row, .1] for row in rows]
    with pytest.raises(ValueError, match="columns"):
        ingest(csv_parts, header=header, rows=rows)


@pytest.mark.parametrize("bad", ["", "not-a-number", "NaN", "inf", "-Infinity", "1e999"])
def test_rejects_bad_or_nonfinite_measurements(csv_parts, bad):
    rows = deepcopy(csv_parts[2])
    rows[1][3] = bad
    with pytest.raises(ValueError, match="numeric|finite"):
        ingest(csv_parts, rows=rows)


@pytest.mark.parametrize("count", [0, 2, 81])
def test_rejects_measurement_row_counts(csv_parts, count):
    rows = [deepcopy(csv_parts[2][0]) for _ in range(count)]
    with pytest.raises(ValueError, match="3 to 80"):
        ingest(csv_parts, rows=rows)


def test_rejects_ragged_measurement_row(csv_parts):
    rows = deepcopy(csv_parts[2])
    rows[0].pop()
    with pytest.raises(ValueError, match="row 2.*columns"):
        ingest(csv_parts, rows=rows)


def test_requires_full_dense_covariance(csv_parts):
    metadata, header, rows, _ = csv_parts
    with pytest.raises(ValueError, match="full dense covariance"):
        import_measurement_csv(csv_stream([header, *rows]), metadata, None)


@pytest.mark.parametrize("kind", ["few_rows", "extra_rows", "diagonal_only", "extra_column", "nonfinite", "nonnumeric", "asymmetric", "not_spd"])
def test_rejects_invalid_covariance(csv_parts, kind):
    matrix = csv_parts[3].tolist()
    if kind == "few_rows":
        matrix.pop()
    elif kind == "extra_rows":
        matrix.append(matrix[0][:])
    elif kind == "diagonal_only":
        matrix = [[matrix[i][i]] for i in range(18)]
    elif kind == "extra_column":
        matrix[4].append(0)
    elif kind == "nonfinite":
        matrix[0][2] = "NaN"
    elif kind == "nonnumeric":
        matrix[0][2] = "x"
    elif kind == "asymmetric":
        matrix[0][7] += .001
    else:
        matrix[0][1] = matrix[1][0] = 1.
    with pytest.raises(ValueError):
        ingest(csv_parts, covariance=matrix)


@pytest.mark.parametrize("key", ["epochs_yr", "observations", "covariance"])
def test_rejects_metadata_measurement_payloads(csv_parts, key):
    metadata = deepcopy(csv_parts[0])
    metadata[key] = []
    with pytest.raises(ValueError, match=f"must not contain {key}"):
        ingest(csv_parts, metadata=metadata)


def test_rejects_bad_metadata_and_does_not_close_streams(csv_parts):
    metadata, header, rows, covariance = csv_parts
    for body in ['{"schema_version":1,"schema_version":1}', '{"bad":NaN}', '[]', '{']:
        with pytest.raises(ValueError):
            import_measurement_csv(csv_stream([header, *rows]), StringIO(body), csv_stream(covariance))
    measurement_stream = csv_stream([header, *rows])
    covariance_stream = csv_stream(covariance)
    import_measurement_csv(measurement_stream, metadata, covariance_stream)
    assert not measurement_stream.closed
    assert not covariance_stream.closed


def test_dataset_validator_still_enforces_physical_contract(csv_parts):
    metadata = deepcopy(csv_parts[0])
    metadata["geometry"]["D_l_pc"] = -1.
    with pytest.raises(ValueError, match="D_l_pc"):
        ingest(csv_parts, metadata=metadata)
