"""Identical-epoch data cannot identify proper motion.

Run against the installed wheel from any directory with python -B.
This checks an exact invariance, not an implementation-specific string.
"""
import argparse
import copy
import json
from pathlib import Path
import numpy as np
from bhtracker import fit, predict
from bhtracker.examples import make_example

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, default=Path("null_motion_covariance_rerun.json"),
                    help="Output JSON path; recorded review evidence is not overwritten by default")
args = parser.parse_args()

raw, truth = make_example("nearby_motion", noise=False)
raw["epochs_yr"] = [raw["reference_epoch_yr"]] * len(raw["epochs_yr"])
raw["observations"] = predict(raw, truth).tolist()
alternative = copy.deepcopy(truth)
alternative["proper_motion_mas_yr"] = [-0.125, 0.075]
invariance_error = float(np.max(np.abs(predict(raw, alternative) - predict(raw, truth))))
result = fit(raw, starts=1, nuisance="none")
record = {
    "all_rows_at_reference_epoch": True,
    "distinct_motion_values": [truth["proper_motion_mas_yr"], alternative["proper_motion_mas_yr"]],
    "maximum_prediction_change_for_distinct_admitted_motions": invariance_error,
    "status": result["status"],
    "reported_motion_standard_errors": result["uncertainty"]["proper_motion_mas_yr"],
    "reported_motion_covariance": result["proper_motion_covariance"],
    "motion_snr": result["motion_snr"],
    "unidentified_motion_mask": result["_internal"]["unidentified"][3:5],
    "diagnostics": [item["code"] for item in result["diagnostics"]],
}
print(json.dumps(record, indent=2))
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf8")
