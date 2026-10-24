"""Independent-generator physics/lineage checks; no prospective study seeds used."""
from copy import deepcopy
import importlib.util
from pathlib import Path

import numpy as np
import pytest

from bhtracker import load_dataset, predict
from bhtracker.observations import UnresolvedPhotometry
from bhtracker.photometry import predict_photometry

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rc7_study_development", ROOT / "research/validation_20261024/calibration_study.py")
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)


@pytest.mark.parametrize("mass,epoch,ref,worldtube", [(10., 2026., 7., 1e-8), (10., 2000., .001, 1e-8),
                                                     (.05, 2026., 7., 1e-8), (1e5, 2026., 7., 1e-5)])
def test_independent_physical_generator_matches_public_exterior(mass, epoch, ref, worldtube):
    raw, truth = study.resolved_design({"mass_msun": mass, "reporting_epoch_yr": epoch,
        "reference_mass_msun": ref, "r0_pc": worldtube})
    actual = predict(load_dataset(raw), truth)
    np.testing.assert_allclose(actual, raw["observations"], rtol=3e-10, atol=2e-10)
    lower = np.linalg.cholesky(raw["covariance"])
    np.testing.assert_allclose(lower @ lower.T, raw["covariance"], rtol=1e-12, atol=1e-25)


def test_independent_shear_jacobian_and_fermat_match_full_model():
    raw, truth = study.resolved_design({"mass_msun": 10., "shear": [.03, -.018]})
    actual = predict(load_dataset(raw), truth)
    np.testing.assert_allclose(actual, raw["observations"], rtol=3e-10, atol=2e-10)
    plain = deepcopy(truth)
    plain["shear"] = [0., 0.]
    assert np.max(np.abs(actual - predict(load_dataset(raw), plain))) > .01


def test_reporting_epoch_is_only_a_physical_basis_change():
    first, truth1 = study.resolved_design({"mass_msun": 10.})
    second, truth2 = study.resolved_design({"mass_msun": 10., "reporting_epoch_yr": 2000., "reference_mass_msun": .001})
    np.testing.assert_allclose(first["observations"], second["observations"], rtol=2e-13, atol=2e-13)
    np.testing.assert_allclose(np.asarray(truth2["center_mas"])+26*np.asarray(truth2["proper_motion_mas_yr"]), truth1["center_mas"])


def invented_parent():
    return {"schema": "bhsm_unresolved_observations/1", "observable": "apparent_magnitude",
        "common_numeric_origin_jd": 2450000., "metadata": {"synthetic": True}, "sources": [], "transformations": [],
        "instruments": {"INVENTED": {"filter": "I", "time": {"reference": "HJD", "unit": "day",
            "numeric_origin_jd": 2450000., "clock_scale": "UNSPECIFIED"}, "calibration": "Wholly invented test"}},
        "rows": [{"source_row_id": f"INVENTED:{i}", "source_file": "invented.dat", "source_line": i+1,
                  "source_sha256": "invented-parent-only", "instrument": "INVENTED", "native_time": float(t),
                  "magnitude": 20.+i, "magnitude_error": .02, "quality_flags": []}
                 for i, t in enumerate([2999., 2900., 3000., 3000., 3001., 3020., 3100.])]}


def test_native_mean_matches_independent_flux_sum_without_observed_brightness():
    parent = invented_parent()
    data = UnresolvedPhotometry(parent)
    truth = {"t0": 3000., "tE_days": 30., "u0": .3, "baseline_magnitude": 18., "source_fraction": .65}
    parameters = {**truth, "instruments": {"INVENTED": {"baseline_magnitude": 18., "source_fraction": .65}}}
    np.testing.assert_allclose(study.photometry_mean(data.times, truth, "pspl"), predict_photometry(data, parameters), atol=1e-13)
    altered = deepcopy(parent)
    for row in altered["rows"]:
        row["magnitude"] = -999.
    first = study.photometry_draw(parent, truth, "pspl", 999999, 1)
    second = study.photometry_draw(altered, truth, "pspl", 999999, 1)
    np.testing.assert_array_equal([r["magnitude"] for r in first[0]["rows"]], [r["magnitude"] for r in second[0]["rows"]])


@pytest.mark.parametrize("family", ["pspl", "constant", "periodic_variable", "binary_source", "correlated_pspl"])
def test_generated_lineage_time_error_ties_order_and_parent_immutability(family):
    parent, original = invented_parent(), invented_parent()
    truth = {"t0": 3000., "tE_days": 30., "u0": .3, "baseline_magnitude": 18., "source_fraction": .65}
    first = study.photometry_draw(parent, truth, family, 999999, 2)
    second = study.photometry_draw(parent, truth, family, 999999, 2)
    assert study.canonical(first) == study.canonical(second)
    assert parent == original
    generated = UnresolvedPhotometry(first[0])
    assert len(generated.rows) == len(parent["rows"])
    for before, after in zip(parent["rows"], generated.rows):
        assert after["native_time"] == before["native_time"]
        assert after["magnitude_error"] == before["magnitude_error"]
        assert after["cadence_parent_source_row_id"] == before["source_row_id"]
        assert after["cadence_parent_source_sha256"] == before["source_sha256"]
        assert after["source_row_id"].startswith("SYNTHETIC:")
        assert "SYNTHETIC_MAGNITUDE" in after["quality_flags"]
    assert "synthetic_truth" not in generated.document["metadata"]


def test_incomplete_campaign_has_completion_bounds_not_binomial_certificate():
    incomplete = study.binomial_summary(8, 10, 20)
    assert incomplete["exact95_binomial_interval_complete_campaign_only"] is None
    assert incomplete["completion_bounds"] == [.4, .9]
    complete = study.binomial_summary(0, 300, 300)
    assert complete["one_sided95_upper_if_zero_and_complete"] < .01
