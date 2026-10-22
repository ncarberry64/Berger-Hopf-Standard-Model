"""Materialize a browser forward-view fixture from the pinned research product.

Run from any directory with numpy/scipy installed. This does not run inference,
change a product file, or regenerate statistical calibration.
"""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
REVISION = "33f26a5113392c0d2c323d7e4a36c7e81bd3ee29"
PRODUCT = "products/blackhole_tracker"


def pinned(path):
    raw = subprocess.check_output(["git", "show", f"{REVISION}:{path}"], cwd=ROOT)
    # Working-tree CRLF conversion is immaterial to the JSON values, but a
    # changed scientific input must never be silently picked up by this tool.
    local = (ROOT / path).read_bytes().replace(b"\r\n", b"\n")
    if local != raw.replace(b"\r\n", b"\n"):
        raise ValueError(f"Working source differs from the pinned product: {path}")
    return raw


data_path = f"{PRODUCT}/bhtracker/examples/nearby_motion.json"
truth_path = f"{PRODUCT}/bhtracker/examples/nearby_motion.truth.json"
forward_path = f"{PRODUCT}/bhtracker/forward.py"
raws = {path: pinned(path) for path in [data_path, truth_path, forward_path]}
dataset = json.loads(raws[data_path])
truth = json.loads(raws[truth_path])
sys.path.insert(0, str(ROOT / PRODUCT))
from bhtracker.forward import LensEngine  # noqa: E402

engine = LensEngine(dataset)
forward, _ = engine.calculate(truth)
out = {
    "schema": "bhsm-museum-tracker-forward-example/v1",
    "source_revision": REVISION,
    "classification": "SYNTHETIC_NOISE_FREE_FORWARD_VIEW_NOT_A_FIT",
    "source_records": [
        {
            "path": path,
            "git_blob_sha256": sha256(raw).hexdigest(),
            "normalized_source_sha256": sha256(raw.replace(b"\r\n", b"\n")).hexdigest(),
        }
        for path, raw in raws.items()
    ],
    "geometry": dataset["geometry"],
    "reference_epoch_yr": dataset["reference_epoch_yr"],
    "epochs_yr": dataset["epochs_yr"],
    "truth": truth,
    "theta_reference_mas": engine.theta,
    "forward_reference": forward.tolist(),
    "scope": "Declared synthetic truth and noise-free ordinary monopole forward values. No optimizer, observation, fit, R1 response or microscopic/horizon inference.",
}
target = ROOT / "museum/lib/blackhole-tracker-example.json"
target.write_bytes((json.dumps(out, indent=2, ensure_ascii=False) + "\n").encode())
print(f"Wrote {target.name}; 9 independent source/epoch rows, no fitting.")
