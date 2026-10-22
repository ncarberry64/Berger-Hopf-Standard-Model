"""Independent physical-unit and known-covariance public API contracts.

These tests use an independently evaluated ordinary point lens, not the
package's lens helpers/constants. They do not establish R1 detectability or
nonlinear interval calibration. Protocol: paper review/product_validation_protocol.md.
"""
from copy import deepcopy
import json
from math import asinh, pi, sqrt

import numpy as np
import pytest

from bhtracker import fit, load_dataset, predict


# Independent SI construction from nominal GM_sun and exact c/parsec units.
SOLAR_GM_SI = 1.3271244e20
LIGHT_SPEED_SI = 299792458.0
PARSEC_SI = 3.085677581491367e16
MAS_PER_RADIAN = 180.0 * 3600.0 * 1000.0 / pi


def independent_point_lens(raw, parameters):
    g = raw["geometry"]
    mass = parameters["mass_msun"]
    mass_length_pc = SOLAR_GM_SI * mass / LIGHT_SPEED_SI**2 / PARSEC_SI
    theta_e = sqrt(
        4.0 * mass_length_pc * g["D_ls_pc"] / (g["D_l_pc"] * g["D_s_pc"])
    ) * MAS_PER_RADIAN
    time_scale = 4.0 * SOLAR_GM_SI * mass / LIGHT_SPEED_SI**3 * (1.0 + g["z_l"])
    rows = []
    for epoch, source in zip(raw["epochs_yr"], parameters["source_mas"]):
        center = np.asarray(parameters["center_mas"]) + (
            epoch - raw["reference_epoch_yr"]
        ) * np.asarray(parameters["proper_motion_mas_yr"])
        y = (np.asarray(source) - center) / theta_e
        u = float(np.linalg.norm(y))
        direction = y / u
        separation = sqrt(u * u + 4.0)
        xp = (u + separation) / 2.0
        xm = -1.0 / xp
        plus = center + theta_e * xp * direction
        minus = center + theta_e * xm * direction
        log_ratio = 4.0 * asinh(u / 2.0)
        delay = time_scale * (u * separation / 2.0 + 2.0 * asinh(u / 2.0))
        rows.append([*plus, *minus, log_ratio, delay])
    return np.asarray(rows), theta_e


@pytest.fixture
def point_fixture():
    # A synthetic Galactic point mass, not an object or observing forecast.
    epochs = np.asarray([2025.55, 2025.69, 2025.88, 2026.03, 2026.21, 2026.39, 2026.58])
    raw = {
        "schema_version": 1,
        "geometry": {"D_l_pc": 1000.0, "D_s_pc": 8000.0, "D_ls_pc": 7000.0,
                     "z_l": 0.0, "z_s": 0.0},
        "reference_epoch_yr": 2026.0,
        "epochs_yr": epochs.tolist(),
        "analysis": {"r0_pc": 1e-8, "reference_mass_msun": 7.0,
                     "flux_ratio": 0.0, "source_policy": "free_per_epoch"},
        "provenance": {"kind": "synthetic", "fixture": "independent-point-contract-v1",
                       "seed": 20261021, "observations_used": False},
    }
    mass_length_pc = SOLAR_GM_SI * 10.0 / LIGHT_SPEED_SI**2 / PARSEC_SI
    theta_e = sqrt(4.0 * mass_length_pc * 7000.0 / (1000.0 * 8000.0)) * MAS_PER_RADIAN
    parameters = {
        "mass_msun": 10.0,
        "center_mas": [12.3, -4.2],
        "proper_motion_mas_yr": [7.5, -2.5],
        "source_mas": [
            [12.3 + theta_e * (0.65 + 0.12 * np.sin(i)),
             -4.2 + theta_e * (0.55 + 0.07 * np.cos(0.7 * i))]
            for i in range(len(epochs))
        ],
        "shear": [0.0, 0.0], "compact_quad": [0.0, 0.0], "convergence": 0.0,
    }
    observations, _ = independent_point_lens(raw, parameters)
    # Dense SPD covariance: mixed units, image correlations and epoch correlation.
    sigma = np.asarray([0.02, 0.02, 0.02, 0.02, 0.015, 1.5e-6])
    within = np.eye(6)
    within[0, 2] = within[2, 0] = 0.25
    within[1, 3] = within[3, 1] = 0.25
    within[4, 5] = within[5, 4] = 0.20
    epoch_corr = 0.2 ** np.abs(np.arange(len(epochs))[:, None] - np.arange(len(epochs)))
    covariance = np.kron(epoch_corr, sigma[:, None] * within * sigma[None, :])
    raw["observations"] = observations.tolist()
    raw["covariance"] = covariance.tolist()
    return raw, parameters


def permute_fixture(raw, parameters, order):
    raw = deepcopy(raw)
    parameters = deepcopy(parameters)
    indices = np.concatenate([np.arange(6 * i, 6 * i + 6) for i in order])
    raw["epochs_yr"] = np.asarray(raw["epochs_yr"])[order].tolist()
    raw["observations"] = np.asarray(raw["observations"])[order].tolist()
    raw["covariance"] = np.asarray(raw["covariance"])[np.ix_(indices, indices)].tolist()
    parameters["source_mas"] = np.asarray(parameters["source_mas"])[order].tolist()
    return raw, parameters, indices


def test_independent_point_lens_physical_units(point_fixture):
    raw, parameters = point_fixture
    expected, theta_e = independent_point_lens(raw, parameters)
    actual = predict(load_dataset(raw), parameters, family="gr")
    assert actual.shape == (len(raw["epochs_yr"]), 6)
    assert np.all(np.isfinite(actual))
    np.testing.assert_allclose(actual[:, :4], expected[:, :4], rtol=2e-11, atol=2e-10)
    np.testing.assert_allclose(actual[:, 4:], expected[:, 4:], rtol=2e-10, atol=2e-13)
    assert np.all(actual[:, 4] > 0.0)
    assert np.all(actual[:, 5] > 0.0)
    # Independently recover center and mass from the baseline outputs.
    sqrt_ratio = np.exp(actual[:, 4] / 2.0)
    recovered_centers = (actual[:, :2] + sqrt_ratio[:, None] * actual[:, 2:4]) / (1.0 + sqrt_ratio[:, None])
    centers = np.asarray(parameters["center_mas"]) + (
        np.asarray(raw["epochs_yr"]) - raw["reference_epoch_yr"]
    )[:, None] * np.asarray(parameters["proper_motion_mas_yr"])
    np.testing.assert_allclose(recovered_centers, centers, rtol=2e-11, atol=2e-10)
    inferred_u = 2.0 * np.sinh(actual[:, 4] / 4.0)
    h = inferred_u * np.sqrt(inferred_u**2 + 4.0) / 2.0 + 2.0 * np.arcsinh(inferred_u / 2.0)
    recovered_mass = actual[:, 5] * LIGHT_SPEED_SI**3 / (4.0 * SOLAR_GM_SI * (1.0 + raw["geometry"]["z_l"]) * h)
    np.testing.assert_allclose(recovered_mass, parameters["mass_msun"], rtol=3e-10)
    assert theta_e > 0.0


def test_absolute_frame_translation_and_reference_epoch(point_fixture):
    raw, parameters = point_fixture
    baseline = predict(load_dataset(raw), parameters)
    shift = np.asarray([-17.0, 9.0])
    translated = deepcopy(raw)
    translated_parameters = deepcopy(parameters)
    translated_parameters["center_mas"] = (np.asarray(parameters["center_mas"]) + shift).tolist()
    translated_parameters["source_mas"] = (np.asarray(parameters["source_mas"]) + shift).tolist()
    translated_observations = np.asarray(translated["observations"])
    translated_observations[:, :2] += shift
    translated_observations[:, 2:4] += shift
    translated["observations"] = translated_observations.tolist()
    moved = predict(load_dataset(translated), translated_parameters)
    np.testing.assert_allclose(moved[:, :4], baseline[:, :4] + np.tile(shift, 2), atol=3e-10, rtol=2e-11)
    np.testing.assert_allclose(moved[:, 4:], baseline[:, 4:], atol=2e-13, rtol=2e-10)
    changed_epoch = deepcopy(raw)
    changed_parameters = deepcopy(parameters)
    dt = 0.37
    changed_epoch["reference_epoch_yr"] += dt
    changed_parameters["center_mas"] = (np.asarray(parameters["center_mas"]) + dt * np.asarray(parameters["proper_motion_mas_yr"])).tolist()
    np.testing.assert_allclose(predict(load_dataset(changed_epoch), changed_parameters), baseline, atol=3e-10, rtol=2e-10)


def test_epoch_and_dense_covariance_block_permutation(point_fixture):
    raw, parameters = point_fixture
    order = np.asarray([4, 1, 6, 0, 3, 5, 2])
    permuted, permuted_parameters, indices = permute_fixture(raw, parameters, order)
    data = load_dataset(raw)
    other = load_dataset(permuted)
    np.testing.assert_array_equal(other.epochs, np.asarray(raw["epochs_yr"])[order])
    np.testing.assert_allclose(predict(other, permuted_parameters), predict(data, parameters)[order], atol=3e-10, rtol=2e-10)
    # Whitened components need not permute individually; their squared norm must.
    residual = np.tile(np.asarray([0.02, 0.02, 0.02, 0.02, 0.015, 1.5e-6]), data.n)
    q0 = float(data.whiten(residual) @ data.whiten(residual))
    q1 = float(other.whiten(residual[indices]) @ other.whiten(residual[indices]))
    direct = float(residual @ np.linalg.solve(data.covariance, residual))
    np.testing.assert_allclose([q0, q1], direct, rtol=2e-12, atol=2e-12)
    diagonal_only = float(np.sum(residual**2 / np.diag(data.covariance)))
    assert abs(diagonal_only / direct - 1.0) > 0.05


def test_loader_file_dict_equivalence_and_input_immutability(point_fixture, tmp_path):
    raw, parameters = point_fixture
    before = deepcopy(raw)
    path = tmp_path / "independent_point.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    from_dict = load_dataset(raw)
    from_file = load_dataset(path)
    assert from_dict.sha256 == from_file.sha256
    np.testing.assert_array_equal(from_dict.covariance, from_file.covariance)
    predict(from_dict, parameters)
    assert raw == before


@pytest.mark.parametrize("case", [
    "schema", "geometry_zero", "geometry_nonfinite", "negative_redshift", "short_rows",
    "observation_shape", "nonfinite_observation", "covariance_shape", "asymmetric_covariance",
    "indefinite_covariance", "zero_variance", "nonfinite_covariance", "unknown_source_policy",
    "unknown_provenance", "wrong_fields", "invalid_worldtube",
])
def test_invalid_dataset_admission(point_fixture, case):
    raw, _ = point_fixture
    # Prove this control is valid before introducing one invalid feature; an
    # unrelated baseline rejection must not make every negative control pass.
    load_dataset(raw)
    bad = deepcopy(raw)
    cov = np.asarray(bad["covariance"])
    if case == "schema": bad["schema_version"] = 2
    elif case == "geometry_zero": bad["geometry"]["D_l_pc"] = 0.0
    elif case == "geometry_nonfinite": bad["geometry"]["D_s_pc"] = float("inf")
    elif case == "negative_redshift": bad["geometry"]["z_l"] = -0.1
    elif case == "short_rows":
        bad["epochs_yr"] = bad["epochs_yr"][:2]
        bad["observations"] = bad["observations"][:2]
        bad["covariance"] = cov[:12, :12].tolist()
    elif case == "observation_shape": bad["observations"] = np.asarray(bad["observations"])[:, :5].tolist()
    elif case == "nonfinite_observation": bad["observations"][0][0] = float("nan")
    elif case == "covariance_shape": bad["covariance"] = cov[:-1, :-1].tolist()
    elif case == "asymmetric_covariance":
        cov[0, 1] += 0.03 * sqrt(cov[0, 0] * cov[1, 1])
        bad["covariance"] = cov.tolist()
    elif case == "indefinite_covariance":
        cov[0, 6] = cov[6, 0] = 2.0 * sqrt(cov[0, 0] * cov[6, 6])
        bad["covariance"] = cov.tolist()
    elif case == "zero_variance":
        cov[0, 0] = 0.0
        bad["covariance"] = cov.tolist()
    elif case == "nonfinite_covariance":
        cov[1, 1] = float("nan")
        bad["covariance"] = cov.tolist()
    elif case == "unknown_source_policy": bad["analysis"]["source_policy"] = "secret_known_track"
    elif case == "unknown_provenance": bad["provenance"]["kind"] = "unknown"
    elif case == "wrong_fields": bad["fields"] = ["delay_seconds"] * 6
    elif case == "invalid_worldtube": bad["analysis"]["r0_pc"] = -1.0
    with pytest.raises(ValueError):
        load_dataset(bad)


@pytest.mark.parametrize("case", ["zero_mass", "negative_mass", "nonfinite_mass", "center_shape",
                                  "motion_nonfinite", "source_shape", "shear_shape", "compact_shape",
                                  "convergence_nonfinite", "aligned_source", "enters_worldtube"])
def test_invalid_forward_parameters(point_fixture, case):
    raw, parameters = point_fixture
    predict(load_dataset(raw), parameters)
    bad = deepcopy(parameters)
    if case == "zero_mass": bad["mass_msun"] = 0.0
    elif case == "negative_mass": bad["mass_msun"] = -1.0
    elif case == "nonfinite_mass": bad["mass_msun"] = float("nan")
    elif case == "center_shape": bad["center_mas"] = [0.0]
    elif case == "motion_nonfinite": bad["proper_motion_mas_yr"] = [float("inf"), 0.0]
    elif case == "source_shape": bad["source_mas"] = bad["source_mas"][:-1]
    elif case == "shear_shape": bad["shear"] = [0.0]
    elif case == "compact_shape": bad["compact_quad"] = [0.0, 0.0, 0.0]
    elif case == "convergence_nonfinite": bad["convergence"] = float("nan")
    elif case == "aligned_source":
        bad["source_mas"][0] = (np.asarray(bad["center_mas"]) +
                                   (raw["epochs_yr"][0] - raw["reference_epoch_yr"]) *
                                   np.asarray(bad["proper_motion_mas_yr"])).tolist()
    elif case == "enters_worldtube":
        raw = deepcopy(raw)
        raw["analysis"]["r0_pc"] = 1.0
    with pytest.raises(ValueError):
        predict(load_dataset(raw), bad)


def test_unknown_family_rejected(point_fixture):
    raw, parameters = point_fixture
    with pytest.raises(ValueError):
        predict(load_dataset(raw), parameters, family="unknown_theory")


def test_fit_reports_full_supplied_covariance_objective(point_fixture):
    """Check the fit's statistical contract, not a new recovery benchmark."""
    raw, _ = point_fixture
    raw = deepcopy(raw)
    rng = np.random.default_rng(20261021)
    covariance = np.asarray(raw["covariance"])
    noise = np.linalg.cholesky(covariance) @ rng.standard_normal(covariance.shape[0])
    raw["observations"] = (np.asarray(raw["observations"]) + noise.reshape(-1, 6)).tolist()
    data = load_dataset(raw)
    result = fit(data, family="gr", starts=1, nuisance="shear")
    required = {"status", "estimates", "uncertainty", "chi2", "dof", "diagnostics", "model", "predictions"}
    assert required.issubset(result)
    assert {"mass_msun", "center_mas", "proper_motion_mas_yr"}.issubset(result["estimates"])
    prediction = np.asarray(result["predictions"])
    assert prediction.shape == data.observations.shape and np.all(np.isfinite(prediction))
    residual = (prediction - data.observations).ravel()
    expected = float(residual @ np.linalg.solve(data.covariance, residual))
    np.testing.assert_allclose(result["chi2"], expected, rtol=2e-9, atol=2e-8)


@pytest.mark.parametrize("reference_mass", [None, 1e5])
def test_stellar_mass_fit_does_not_inherit_normalization_prior(point_fixture, reference_mass):
    """A numerical reference mass must not silently bound physical mass.

    Regression thresholds are fixed before the normalization correction is
    evaluated. This is an exact ordinary-lens recovery check, not coverage.
    """
    raw, parameters = point_fixture
    raw = deepcopy(raw)
    if reference_mass is None:
        raw["analysis"].pop("reference_mass_msun")
    else:
        raw["analysis"]["reference_mass_msun"] = reference_mass
    result = fit(load_dataset(raw), starts=1, nuisance="shear")
    np.testing.assert_allclose(result["estimates"]["mass_msun"], parameters["mass_msun"],
                               rtol=1e-5, atol=0.0)
    assert result["chi2"] < 1e-6
    assert result["status"] != "FIT_REJECTED"


def test_active_physical_bound_does_not_claim_unqualified_tracking(point_fixture):
    raw, parameters = point_fixture
    raw = deepcopy(raw)
    raw["analysis"]["mass_bounds_msun"] = [parameters["mass_msun"], 100.0]
    result = fit(load_dataset(raw), starts=1, nuisance="shear")
    assert any(item["code"] == "BOUND_ACTIVE" for item in result["diagnostics"])
    assert result["status"] != "TRACKED"
