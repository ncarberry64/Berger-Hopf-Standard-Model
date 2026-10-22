"""Independent point-lens fixture; vary only computational coordinates.

Run against the installed wheel from any directory. Supply --product-source
or BHSM_PRODUCT_SOURCE for the source directory containing the independent
fixture. No source files are changed. The fixture uses SI point-lens equations.
"""
import argparse
import ast
import copy
import json
import os
from pathlib import Path
import numpy as np
from bhtracker import fit
from bhtracker.forward import LensEngine

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--product-source", type=Path, default=os.environ.get("BHSM_PRODUCT_SOURCE"),
                    help="Product source directory containing tests/test_inference_contract.py")
parser.add_argument("--output", type=Path, default=Path("coordinate_domain_rerun.json"),
                    help="Output JSON path; recorded review evidence is not overwritten by default")
args = parser.parse_args()
if args.product_source is None:
    parser.error("Supply --product-source or set BHSM_PRODUCT_SOURCE")
fixture_path = args.product_source / "tests" / "test_inference_contract.py"
if not fixture_path.is_file():
    parser.error(f"Independent fixture not found: {fixture_path}")
tree = ast.parse(fixture_path.read_text(encoding="utf8"))
nodes = []
for node in tree.body:
    if isinstance(node, ast.ImportFrom) and node.module == "math":
        nodes.append(node)
    elif isinstance(node, ast.Import) and node.names[0].name == "numpy":
        nodes.append(node)
    elif isinstance(node, ast.Assign):
        nodes.append(node)
    elif isinstance(node, ast.FunctionDef) and node.name in ("independent_point_lens", "point_fixture"):
        node.decorator_list = []
        nodes.append(node)
namespace = {}
exec(compile(ast.Module(body=nodes, type_ignores=[]), "<independent fixture>", "exec"), namespace)
original, truth = namespace["point_fixture"]()

results = []
for label, change in (
    ("control", {}),
    ("reference_epoch_2000", {"reference_epoch_yr": 2000.0}),
    ("reference_mass_0.001", {"reference_mass_msun": 0.001}),
    ("reference_mass_100000", {"reference_mass_msun": 100000.0}),
):
    raw = copy.deepcopy(original)
    if "reference_epoch_yr" in change:
        raw["reference_epoch_yr"] = change["reference_epoch_yr"]
    if "reference_mass_msun" in change:
        raw["analysis"]["reference_mass_msun"] = change["reference_mass_msun"]
    engine = LensEngine(raw, reference_mass=raw["analysis"]["reference_mass_msun"])
    parameters = copy.deepcopy(truth)
    parameters["center_mas"] = (
        np.asarray(truth["center_mas"])
        + (raw["reference_epoch_yr"] - original["reference_epoch_yr"])
        * np.asarray(truth["proper_motion_mas_yr"])
    ).tolist()
    exact_prediction, _ = engine.calculate(parameters)
    forward_max_error = float(np.max(np.abs(exact_prediction - np.asarray(raw["observations"]))))
    result = fit(raw, starts=1, nuisance="none")
    row = {
        "case": label,
        "same_measurements": raw["observations"] == original["observations"],
        "same_covariance": raw["covariance"] == original["covariance"],
        "same_physical_worldtube": raw["analysis"]["r0_pc"] == original["analysis"]["r0_pc"],
        "exact_truth_forward_max_error": forward_max_error,
        "status": result["status"],
        "mass_msun": result["estimates"]["mass_msun"],
        "chi2": result["chi2"],
        "diagnostics": [item["code"] for item in result["diagnostics"]],
    }
    results.append(row)
    print(json.dumps(row), flush=True)

if __name__ == "__main__":
    target = args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(results, indent=2) + "\n", encoding="utf8")
