"""Exact finite zero-flux harmonic degeneracy: formal operator control only.

Large coefficients make the algebra observable in floating point. They are
not admitted scalar states and are never interpreted as physical signals.
Public prediction must reject the inflated state separately.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

PRODUCT = Path(__file__).resolve().parents[1]
ROOT = PRODUCT.parent
sys.path.insert(0, str(PRODUCT))
from bhtracker import load_dataset, predict  # noqa: E402
from bhtracker.examples import make_example  # noqa: E402
from bhtracker.forward import LensEngine  # noqa: E402


def flattened(values):
    return np.concatenate([np.asarray(value).ravel() for value in values])


def main():
    source_paths = ["product/tests/check_finite_harmonic_degeneracy.py", "product/bhtracker/data.py",
                    "product/bhtracker/forward.py", "product/bhtracker/r1_runtime.py",
                    "product/bhtracker/physics_admission.py", "product/bhtracker/theory/radial_response.py"]
    source_hashes = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in source_paths}
    raw, truth = make_example("nearby_motion", noise=False)
    raw["analysis"].update({"flux_ratio": 0.0, "flux_provenance": "supplied_worldtube_flux"})
    truth["flux_ratio"] = 0.0
    data = load_dataset(raw)
    r1 = LensEngine(data, "r1")
    gr = LensEngine(data, "gr")
    # Independently form the dimensionless phase coefficient from SI units.
    gm = 1.3271244e20
    c = 299792458.0
    pc = 3.085677581491367e16
    geometry = raw["geometry"]
    mref_pc = gm * raw["analysis"]["reference_mass_msun"] / c**2 / pc
    rE_pc_squared = 4.0 * mref_pc * geometry["D_l_pc"] * geometry["D_ls_pc"] / geometry["D_s_pc"]
    n2 = np.sqrt(15.0 / (16.0 * np.pi))
    beta_hat = r1._r1.ref.beta_hat  # Pinned action background datum, not an inferred coupling.
    coefficient = -beta_hat * n2 * raw["analysis"]["r0_pc"]**3 / (3.0 * mref_pc * rE_pc_squared)
    radii = np.asarray([0.55, 0.8, 1.05, 1.5, 2.3])
    angles = np.asarray([0.2, 0.7, 1.1, 2.2, -0.8])
    x = radii[:, None] * np.column_stack([np.cos(angles), np.sin(angles)])
    shear = [0.02, -0.012]
    compact_base = np.asarray([0.0002, 0.0001])
    records = []
    for compact_effect in [np.asarray([1e-4, -2e-4]), np.asarray([-3e-4, 1e-4]), np.asarray([5e-4, 4e-4])]:
        boundary = np.r_[compact_effect / coefficient, 0.5 * np.max(abs(compact_effect / coefficient))]
        actual = r1.potential(x, 1.0, shear, compact_base, 0.01, flux=0.0, boundary=boundary)
        expected = gr.potential(x, 1.0, shear, compact_base + compact_effect, 0.01, flux=0.0)
        scale = max(float(np.max(abs(flattened(expected)))), 1.0)
        error = float(np.max(abs(flattened(actual) - flattened(expected))))
        np.testing.assert_allclose(flattened(actual), flattened(expected), rtol=5e-12, atol=5e-12)
        # A finite compensating change is an exact potential identity, not
        # merely a tangent cancellation or an estimator-only first-order null.
        shift = np.asarray([-0.00013, 0.00009])
        shifted_boundary = boundary.copy()
        shifted_boundary[:2] += shift / coefficient
        compensated = r1.potential(x, 1.0, shear, compact_base - shift, 0.01,
                                   flux=0.0, boundary=shifted_boundary)
        np.testing.assert_allclose(flattened(actual), flattened(compensated), rtol=5e-12, atol=5e-12)
        records.append({"compact_effect": compact_effect.tolist(), "formal_boundary_coefficients": boundary.tolist(),
                        "maximum_absolute_operator_difference": error,
                        "maximum_operator_difference_over_scale": error / scale})
    baseline = flattened(gr.potential(x, 1.0, shear, [0.0, 0.0], 0.01, flux=0.0))
    columns = []
    for index in range(2):
        unit = np.eye(2)[index]
        columns.append(flattened(gr.potential(x, 1.0, shear, unit, 0.01, flux=0.0)) - baseline)
    for index in range(2):
        unit = np.eye(2)[index] / coefficient
        columns.append(flattened(r1.potential(x, 1.0, shear, [0.0, 0.0], 0.01,
                                             flux=0.0, boundary=np.r_[unit, 0.0])) - baseline)
    singular_values = np.linalg.svd(np.column_stack(columns), compute_uv=False)
    rank = int(np.sum(singular_values > singular_values[0] * 1e-10))
    assert rank == 2, "The four equivalent compact/harmonic coordinates must have two exact nulls."
    inflated = deepcopy(truth)
    inflated["boundary_amplitudes"] = records[0]["formal_boundary_coefficients"]
    rejected = False
    rejection = None
    try:
        predict(data, inflated, family="r1")
    except ValueError as error:
        rejected = True
        rejection = str(error)
    report = {"schema_version": 1, "control": "C9 formal finite harmonic/compact potential identity",
              "pass": bool(rank == 2 and rejected),
              "scope": "Nonadmitted large-coefficient operator test; no physical state is enlarged and no detectability result is calculated.",
              "mapping": "compact_effect = boundary[:2] * (-beta_hat*N2*r0_pc^3/(3*mref_pc*rE_pc^2))",
              "mapping_coefficient": float(coefficient), "operator_tolerance": {"rtol": 5e-12, "atol": 5e-12},
              "records": records, "combined_operator_singular_values": singular_values.tolist(),
              "rank_at_relative_1e_minus_10": rank,
              "individual_coordinate_identifiability": "Four coordinates have only two independent operator directions; separate finite likelihood-only uncertainties are not licensed.",
              "public_inflated_state_rejected": rejected, "public_rejection_message": rejection,
              "inference_scope": "The current nonlinear fit does not expose a joint free compact-plus-boundary fit; this verifies the exact finite cause ambiguity and admission, not joint interval calibration.",
              "dataset_sha256": data.sha256,
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "source_sha256": source_hashes,
              "source_unchanged_during_run": all(source_hashes[path] == hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                                                 for path in source_paths)}
    output = PRODUCT / "validation/product_finite_degeneracy_receipt.json"
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
