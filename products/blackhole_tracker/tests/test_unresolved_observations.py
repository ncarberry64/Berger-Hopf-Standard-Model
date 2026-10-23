"""Independent native-observable, likelihood and angular-convention regressions."""
from copy import deepcopy
import hashlib
import json

import numpy as np
import pytest
from scipy.optimize._numdiff import approx_derivative

from bhtracker.astrometry import (PrecisionMetadataError, dark_centroid_shift,
    geocentric_sun_displacement, parallax_trajectory, predict_astrometric_centroid,
    predict_parallax_photometry, precision_metadata_status)
from bhtracker.observations import (SOURCE_WARNING, UnresolvedPhotometry,
    parse_ogle_photometry, parse_benchmark_photometry, load_ogle_catalog)
from bhtracker.photometry import (FIT_PROTOCOL_SHA256, _Model, fit_photometry,
    predict_photometry, profile_timescale, pspl_magnification)


def synthetic_dataset(noise=False, seed=18, fraction=.65):
    # Uneven seasons, complete baseline and an independently calculated native
    # magnitude PSPL injection; no implementation predictor generates this truth.
    t = np.r_[np.linspace(1000, 1150, 45), np.linspace(1300, 1450, 75), np.linspace(1650, 1900, 60)]
    q = (t - 1375) / 72
    u2 = .28 ** 2 + q * q
    magnification = (u2 + 2) / np.sqrt(u2 * (u2 + 4))
    sigma = .008 * np.ones(len(t))
    mag = 18 - 2.5 * np.log10(1 + fraction * (magnification - 1))
    if noise:
        mag += np.random.default_rng(seed).normal(size=len(t)) * sigma
    content = "\n".join(f"{time:.9f} {m:.12f} {s:.12f}" for time, m, s in zip(t, mag, sigma)).encode("ascii")
    return parse_ogle_photometry(content, source_name="SYNTHETIC.dat", metadata={"synthetic": True})


def verified_context():
    return {"metadata": {"time_numeric_origin_jd": 2400000.5,
        "verified_time_transform_provenance": "SYNTHETIC analytic test only",
        "ra_cosdec_convention_verified": True, "frame_and_filter_alignment_verified": True,
        "noise_and_frame_model": "SYNTHETIC independent tangent-plane test",
        "verified_observer_ephemeris_provenance": "SYNTHETIC polynomial trajectory only"}}


def test_parser_exact_annotation_rows_sha_and_native_order():
    raw = f"3 18 .1\n1 19 .2\n1 20 .3\n{SOURCE_WARNING}\n".encode("ascii")
    dataset = parse_ogle_photometry(raw, source_name="original.dat")
    assert dataset.times.tolist() == [3, 1, 1]
    assert dataset.errors.tolist() == [.1, .2, .3]
    source = dataset.document["sources"][0]
    assert source["sha256"] == hashlib.sha256(raw).hexdigest()
    assert source["numeric_rows"] == 3 and source["duplicate_times"] == [1]
    assert source["native_order_strictly_increasing"] is False
    assert source["annotations"][0]["line"] == 4
    assert [r["source_line"] for r in dataset.rows] == [1, 2, 3]
    assert UnresolvedPhotometry.from_dict(dataset.to_dict()).sha256 == dataset.sha256


@pytest.mark.parametrize("row", ["ERROR: data not sorted!", "1 18 0", "1 nan .1", "1 18 -.1", "1 18 .1 extra", "1 bright .1"])
def test_malformed_native_rows_fail_actionably(row):
    with pytest.raises(ValueError, match="original.dat:1"):
        parse_ogle_photometry((row + "\n").encode("ascii"), source_name="original.dat")


def test_catalog_26_columns_sentinels_and_overlap_are_preserved(tmp_path):
    path = tmp_path / "catalog.table"
    path.write_text("0337 17:00:00.00 -30:00:00.0 BLG100.1 12345 3000 -.1 .1 180 -10 10 .2 -.02 .02 .5 -.1 .1 18 -.1 .1 100 95 99.999 9.999 2004-BLG-123,2005-BLG-456 BLG101.2.23456\n")
    record = load_ogle_catalog(path)["OGLE3-ULENS-0337"]
    assert record["published_tE_days"] == 180
    assert record["published_u0"] == .2 and record["published_baseline_I_magnitude"] == 18
    assert record["V_magnitude"] is None and record["V_error"] is None
    assert record["ews_aliases"] == ["2004-BLG-123", "2005-BLG-456"]
    assert record["overlap_alias"] == "BLG101.2.23456"


def test_benchmark_headers_origin_only_and_separate_instruments():
    contents = {"OGLE": {"content": b"hjd mag mag_err\n2456000.5 18 .1\n", "source_name": "ogle.dat"},
                "MOA": {"content": b"hjd mag mag_err\n2456001.5 19 .2\n", "source_name": "moa.dat"}}
    dataset = parse_benchmark_photometry(contents)
    assert dataset.times.tolist() == [6000.5, 6001.5]
    assert dataset.rows[0]["native_time"] == 2456000.5
    assert dataset.rows[0]["source_line"] == 2
    assert len(dataset.instruments) == 2
    assert "not verified clock equivalence" in dataset.document["metadata"]["relative_time_combination_assumption"]
    document = dataset.to_dict(); del document["metadata"]["relative_time_combination_assumption"]
    with pytest.raises(ValueError, match="explicit limited"):
        UnresolvedPhotometry(document)


@pytest.mark.parametrize("mutation", ["row_bool", "origin_bool", "common_inf"])
def test_schema_rejects_bool_and_invalid_origin(mutation):
    document = synthetic_dataset().to_dict()
    if mutation == "row_bool":
        document["rows"][0]["native_time"] = True
    elif mutation == "origin_bool":
        document["instruments"]["OGLE-III"]["time"]["numeric_origin_jd"] = True
    else:
        document["common_numeric_origin_jd"] = float("inf")
    with pytest.raises(ValueError):
        UnresolvedPhotometry(document)


def test_magnification_against_independent_two_image_jacobians():
    u = np.asarray([.01, .1, .3, 1, 3, 10, 100])
    theta_p = (u + np.sqrt(u * u + 4)) / 2
    theta_m = (u - np.sqrt(u * u + 4)) / 2
    # Signed radial/tangential Jacobian determinant = 1 - 1/theta^4.
    magnification = np.abs(1 / (1 - theta_p ** -4)) + np.abs(1 / (1 - theta_m ** -4))
    np.testing.assert_allclose(pspl_magnification(u), magnification, rtol=2e-13)
    assert pspl_magnification(1) == pytest.approx(3 / np.sqrt(5))


def test_analytic_magnitude_jacobian_matches_independent_finite_difference():
    data = synthetic_dataset()
    model = _Model(data, 1, False, False)
    x = model.encode({"t0": 1360, "tE_days": 80, "u0": .4,
        "instruments": {"OGLE-III": {"source_fraction": .6, "baseline_magnitude": 18}}})
    numerical = approx_derivative(model.evaluate, x, method="3-point")
    np.testing.assert_allclose(model.evaluate(x, jac=True), numerical, rtol=2e-6, atol=1e-6)


def test_noiseless_trajectory_recovery_native_likelihood_and_mass_null():
    data = synthetic_dataset()
    result = fit_photometry(data, starts=3, initial={"t0": 1360, "tE_days": 100, "u0": .5})
    assert result["parameters"]["tE_days"] == pytest.approx(72, rel=1e-7)
    assert result["parameters"]["u0"] == pytest.approx(.28, rel=1e-7)
    assert result["diagnostics"]["chi_square_native_noise"] < 1e-14
    assert result["status"] == "PHOTOMETRIC_FIT" and result["point_count"] == 180
    assert result["mass_status"] == "MASS_UNRESOLVED"
    assert result["unresolved_quantities"]["mass_msun"] is None
    assert result["bhsm_interpretation"]["interpretation_schema_version"] == 2
    assert result["bhsm_interpretation"]["spherical_boundary"]["status"] == "NOT_REPORTED_FOR_UNRESOLVED_MASS"
    np.testing.assert_array_equal(predict_photometry(data, result["parameters"]), result["predictions_magnitude"])
    assert result["input_sha256"] == UnresolvedPhotometry(result["dataset_input"]).sha256
    assert result["protocol_sha256"] == FIT_PROTOCOL_SHA256
    json.dumps(result, allow_nan=False)


def test_magnitude_objective_uses_native_errors_and_noise_sensitivity():
    data = synthetic_dataset(noise=True)
    fit = fit_photometry(data, starts=2)
    prediction = np.asarray(fit["predictions_magnitude"])
    manual_chi_square = np.sum(((data.magnitudes - prediction) / data.errors) ** 2)
    assert fit["diagnostics"]["chi_square_native_noise"] == pytest.approx(manual_chi_square)
    # Uniform explicit noise rescaling changes information, not the optimum.
    scaled = fit_photometry(data, starts=2, noise_scale=2)
    assert scaled["parameters"]["tE_days"] == pytest.approx(fit["parameters"]["tE_days"], rel=1e-6)
    assert scaled["uncertainty"]["standard_errors"]["tE_days"] == pytest.approx(2 * fit["uncertainty"]["standard_errors"]["tE_days"], rel=1e-5)


def test_negative_blend_is_explicit_sensitivity_and_does_not_infer_mass():
    data = synthetic_dataset(fraction=1.5)
    ordinary = fit_photometry(data, starts=2)
    sensitivity = fit_photometry(data, starts=3, allow_negative_blend=True)
    assert ordinary["parameters"]["instruments"]["OGLE-III"]["source_fraction"] <= 1
    assert sensitivity["parameters"]["instruments"]["OGLE-III"]["source_fraction"] == pytest.approx(1.5, rel=1e-6)
    assert "SIGNED_BLEND_CALIBRATION_SENSITIVITY" in sensitivity["flags"]
    assert sensitivity["unresolved_quantities"]["mass_msun"] is None
    parameters = deepcopy(sensitivity["parameters"]); parameters["allow_negative_blend"] = False
    with pytest.raises(ValueError, match="explicit"):
        predict_photometry(data, parameters)


def test_fixed_timescale_profile_reoptimizes_blend_nuisance():
    data = synthetic_dataset(noise=True)
    result = fit_photometry(data, starts=3)
    te = result["parameters"]["tE_days"]
    profile = profile_timescale(data, result, [te * .8, te, te * 1.2])
    assert profile["coverage_claim"] is False
    middle = profile["rows"][1]
    assert middle["delta_chi_square"] < 1e-6
    assert all(row["status"].startswith("ADMITTED_") for row in profile["rows"])
    assert profile["rows"][0]["parameters"]["instruments"]["OGLE-III"]["source_fraction"] != pytest.approx(result["parameters"]["instruments"]["OGLE-III"]["source_fraction"])


def test_dark_centroid_against_flux_weighted_two_image_positions():
    u_ne = np.asarray([[.1, .3], [1, 0], [3, 4]])
    u = np.linalg.norm(u_ne, axis=1)
    positive = (u + np.sqrt(u * u + 4)) / 2
    negative = (u - np.sqrt(u * u + 4)) / 2
    ap = np.abs(1 / (1 - positive ** -4)); am = np.abs(1 / (1 - negative ** -4))
    centroid = ((ap * positive + am * negative) / (ap + am))[:, None] * u_ne / u[:, None]
    expected = (centroid - u_ne) * 2.3
    np.testing.assert_allclose(dark_centroid_shift(u_ne, 2.3), expected, rtol=1e-13)


def test_parallax_reference_subtraction_and_ne_signs():
    times = np.asarray([-1.0, 0, 1.0]) + 2450000
    pos = np.column_stack([np.zeros(3), np.asarray([-2, 0, 2]) + .1, np.asarray([.5, 0, .5])])
    ds = geocentric_sun_displacement(times, pos, 2450000, [0, .1, 0], [0, 2, 0], 0, 0)
    np.testing.assert_allclose(ds, [[-.5, 0], [0, 0], [-.5, 0]], atol=1e-15)
    trajectory = parallax_trajectory([0, 1], t0=0, tE_days=2, u0=.3,
        pi_E_north=.1, pi_E_east=.2, sun_displacement_ne=[[2, 3], [4, 5]])
    np.testing.assert_allclose(trajectory, [[.8, .2], [1.9, 0]])


def test_angular_source_motion_parallax_blend_and_frame_are_explicit():
    t = np.asarray([2450000., 2450365.25])
    u = np.asarray([[1., 0], [0, 2.]])
    source = np.asarray([[3., 4], [4, 6]])  # position+[1,2] mas/year
    shift = dark_centroid_shift(u, 2)
    context = verified_context()
    dark = predict_astrometric_centroid(t, reference_jd=t[0], source_position_ne_mas=[3, 4],
        source_proper_motion_ne_mas_yr=[1, 2], source_parallax_mas=.5,
        parallax_factors_ne=[[0, 0], [0, 0]], u_ne=u, theta_E_mas=2,
        frame_offset_ne_mas=[.1, -.2], precision_context=context)
    np.testing.assert_allclose(dark, source + shift + [.1, -.2])
    lens = source - 2 * u
    luminous = predict_astrometric_centroid(t, reference_jd=t[0], source_position_ne_mas=[3, 4],
        source_proper_motion_ne_mas_yr=[1, 2], source_parallax_mas=0,
        parallax_factors_ne=[[0, 0], [0, 0]], u_ne=u, theta_E_mas=2,
        blend_to_source_flux_ratio=.5, blend_position_ne_mas=lens, precision_context=context)
    a = pspl_magnification(np.linalg.norm(u, axis=1))
    np.testing.assert_allclose(luminous, (a[:, None] * (source + shift) + .5 * lens) / (a + .5)[:, None])
    with pytest.raises(PrecisionMetadataError):
        predict_astrometric_centroid(t, reference_jd=t[0], source_position_ne_mas=[3, 4],
            source_proper_motion_ne_mas_yr=[1, 2], source_parallax_mas=0,
            parallax_factors_ne=[[0, 0], [0, 0]], u_ne=u, theta_E_mas=2)


def test_parallax_route_fails_closed_on_actual_missing_metadata():
    data = synthetic_dataset()
    status = precision_metadata_status({"time_scale": "UTC"})
    assert status["status"] == "BLOCKED_MISSING_VERIFIED_METADATA"
    assert any("numeric epoch origin" in gap for gap in status["missing"])
    with pytest.raises(PrecisionMetadataError, match="clock scale"):
        predict_parallax_photometry(data, {}, {"metadata": {"time_scale": "UTC"}})


def test_bool_start_count_is_not_an_integer_configuration():
    with pytest.raises(ValueError, match="positive integers"):
        fit_photometry(synthetic_dataset(), starts=True)


def test_repeated_epoch_photometry_exposes_unidentified_covariance():
    data = parse_ogle_photometry(b"1000 18 .01\n" * 20, metadata={"synthetic": True})
    result = fit_photometry(data, starts=2)
    assert result["uncertainty"]["rank"] < result["uncertainty"]["parameter_count"]
    assert result["uncertainty"]["standard_errors"]["tE_days"] is None
    index = result["uncertainty"]["parameter_order"].index("tE_days")
    assert result["uncertainty"]["covariance"][index][index] is None
    assert result["uncertainty"]["physical_null_directions"]
    json.dumps(result, allow_nan=False)


def test_profile_does_not_certify_a_failed_reference_solution():
    data = synthetic_dataset()
    result = fit_photometry(data, starts=2)
    result["numerical_convergence"]["multistart_confirmed"] = False
    profile = profile_timescale(data, result, [result["parameters"]["tE_days"]])
    assert profile["rows"][0]["status"] == "REFERENCE_MINIMUM_UNRESOLVED"
    assert profile["rows"][0]["delta_chi_square"] is None


@pytest.mark.parametrize("origin", [float("nan"), float("inf"), True, "2400000.5"])
def test_precision_origin_is_a_finite_actual_number(origin):
    metadata = verified_context()["metadata"]
    metadata["time_numeric_origin_jd"] = origin
    assert precision_metadata_status(metadata)["status"] == "BLOCKED_MISSING_VERIFIED_METADATA"


def test_precision_verification_flags_require_actual_booleans():
    metadata = verified_context()["metadata"]
    metadata["frame_and_filter_alignment_verified"] = "yes"
    assert precision_metadata_status(metadata)["status"] == "BLOCKED_MISSING_VERIFIED_METADATA"


@pytest.mark.parametrize("field", ["source_fraction", "baseline_magnitude"])
def test_parallax_prediction_rejects_nonfinite_photometric_parameters(field):
    data = synthetic_dataset()
    context = verified_context()
    context.update(row_ids=[r["source_row_id"] for r in data.rows], times_relative_days=data.times.tolist(),
        sun_displacement_ne_au=np.zeros((len(data.rows), 2)).tolist())
    parameters = {"t0": 1375, "tE_days": 72, "u0": .3, "pi_E_north": .1, "pi_E_east": 0,
        "instruments": {"OGLE-III": {"source_fraction": .5, "baseline_magnitude": 18}}}
    parameters["instruments"]["OGLE-III"][field] = float("nan")
    with pytest.raises(ValueError, match="invalid parallax"):
        predict_parallax_photometry(data, parameters, context)
