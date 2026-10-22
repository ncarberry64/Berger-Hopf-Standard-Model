"""Read-only reproduction of a likelihood-profile physical-admission gap.

Uses the installed wheel. The solver wrapper records
the returned nuisance optimum; it changes neither the objective nor the solve.
The deliberately tight, declared weak-field budget probes a domain boundary.
No repository source is modified and no observational claim is made.
"""
from pathlib import Path
import argparse
import json

import bhtracker
import numpy as np
from bhtracker import fit, inference
from bhtracker.examples import make_example
from bhtracker.forward import C, GM_SUN, PC, LensEngine
from bhtracker.physics_admission import assess_physics
from bhtracker.provenance import VERSION


def run():
    raw, truth = make_example("nearby_motion", noise=False)
    control = LensEngine(raw)
    _, branch = control.calculate(truth, admit=False)
    weak_ratio = GM_SUN * truth["mass_msun"] / (C * C * PC) / np.min(branch["impact_pc"])
    raw["analysis"]["weak_metric_cap"] = float(weak_ratio * 1.00001)
    fitted = fit(raw, starts=1, nuisance="none")
    assert fitted["status"] == "TRACKED"
    assert fitted["physics_admission"]["allowed_physics_models"]["baseline_point_mass"]

    engine = LensEngine(raw, reference_mass=fitted["model"]["reference_mass_msun"])
    mapping = inference.ParameterMap(engine, "none")
    x0 = np.asarray(fitted["_internal"]["x"])
    width = max(3 * np.sqrt(fitted["_internal"]["covariance"][0][0]), .001)
    grid = np.unique(np.r_[np.linspace(max(mapping.lower[0], x0[0] - width),
                                      min(mapping.upper[0], x0[0] + width), 7), x0[0]])
    original_solver = inference.least_squares
    checks = []

    def record_optimum(*args, **kwargs):
        solved = original_solver(*args, **kwargs)
        x = x0.copy()
        x[0] = grid[len(checks)]
        x[1:] = solved.x
        parameters = mapping.decode(x)
        _, image_branch = engine.calculate(parameters, admit=False)
        admission = assess_physics(engine.physics_config, parameters, image_branch["impact_pc"])
        try:
            engine.calculate(parameters, admit=True)
            public_prediction = "ACCEPTED"
        except ValueError as error:
            public_prediction = str(error)
        checks.append({
            "baseline_point_mass_admitted": admission["allowed_physics_models"]["baseline_point_mass"],
            "actual_weak_ratio": float(GM_SUN * parameters["mass_msun"] / (C * C * PC)
                                       / np.min(image_branch["impact_pc"])),
            "public_prediction": public_prediction,
        })
        return solved

    inference.least_squares = record_optimum
    try:
        curve = inference.profile(raw, fitted, points=7)
    finally:
        inference.least_squares = original_solver

    assert len(curve["points"]) == len(checks)
    assert all(point["converged"] for point in curve["points"])
    rows = [{**point, **check} for point, check in zip(curve["points"], checks)]
    assert any(.9 < row["delta_chi2"] < 1.1 and not row["baseline_point_mass_admitted"]
               and row["public_prediction"] != "ACCEPTED" for row in rows)
    return {
        "product_version": VERSION,
        "source": str(Path(bhtracker.__file__).resolve().parent),
        "scope": "Synthetic regression probe; no physical data or repository mutation.",
        "fixture": "make_example('nearby_motion', noise=False)",
        "fit_controls": {"starts": 1, "nuisance": "none"},
        "budget_construction": "true minimum-impact GM/(c^2 b) times 1.00001",
        "weak_metric_cap": raw["analysis"]["weak_metric_cap"],
        "baseline_status": fitted["status"],
        "baseline_admitted": True,
        "profile_interpretation": curve["interpretation"],
        "profile_row_keys_before_instrumentation": list(curve["points"][0]),
        "profile_points_with_independent_admission_check": rows,
        "finding": "Converged profile points near delta_chi2=1 and 4 are outside the declared physical domain, but public profile rows do not report or exclude them.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("profile_admission_rerun.json"),
                        help="Output JSON path; recorded review evidence is not overwritten by default")
    args = parser.parse_args()
    result = run()
    destination = args.output
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf8")
    print(json.dumps({"result": str(destination), "finding": result["finding"]}))
