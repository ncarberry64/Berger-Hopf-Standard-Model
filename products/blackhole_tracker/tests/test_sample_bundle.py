"""A downloadable example must preserve the supported full-C import contract."""
from copy import deepcopy
import hashlib
from io import BytesIO, StringIO
import json
import zipfile

import numpy as np
import pytest

from bhtracker.data import load_dataset
from bhtracker.examples import make_example
from bhtracker.importers import import_measurement_csv
from bhtracker.sample_bundle import build_sample_bundle


def test_example_bundle_csv_round_trip_preserves_native_input_and_full_covariance():
    raw, _ = make_example("nearby_motion")
    # A deliberate block permutation verifies that neither export nor import
    # time-sorts repeated source rows or drops cross-epoch covariance.
    order = [7, 1, 4, 0, 8, 2, 6, 3, 5]
    indices = np.concatenate([np.arange(6 * i, 6 * i + 6) for i in order])
    raw["epochs_yr"] = np.asarray(raw["epochs_yr"])[order].tolist()
    raw["observations"] = np.asarray(raw["observations"])[order].tolist()
    raw["covariance"] = np.asarray(raw["covariance"])[np.ix_(indices, indices)].tolist()
    original = deepcopy(raw)
    bundle = build_sample_bundle(raw)
    with zipfile.ZipFile(BytesIO(bundle)) as archive:
        assert set(archive.namelist()) == {"dataset.json", "metadata.json", "measurements.csv",
                                          "full_covariance.csv", "README.md", "manifest.json"}
        native = json.loads(archive.read("dataset.json"))
        metadata = json.loads(archive.read("metadata.json"))
        assert not {"epochs_yr", "observations", "covariance"} & metadata.keys()
        imported = import_measurement_csv(StringIO(archive.read("measurements.csv").decode()), metadata,
                                          StringIO(archive.read("full_covariance.csv").decode()))
        assert imported == load_dataset(native).raw == load_dataset(raw).raw
        assert np.count_nonzero(np.asarray(imported["covariance"]) - np.diag(np.diag(imported["covariance"]))) > 0
        manifest = json.loads(archive.read("manifest.json"))
        for name, expected in manifest["files"].items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == expected
        assert manifest["dataset_sha256"] == load_dataset(raw).sha256
        assert manifest["provenance_kind"] == "synthetic"
    assert raw == original
    assert build_sample_bundle(raw) == bundle


def test_bundle_rejects_invalid_input_instead_of_packaging_plausible_values():
    raw, _ = make_example("nearby_motion")
    raw["covariance"] = [[1.]]
    with pytest.raises(ValueError, match="covariance"):
        build_sample_bundle(raw)
