"""Offline replay of the new angular-light-transfer paper and its audits."""
from pathlib import Path
import hashlib
import json
import os
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
STAGES = [
    "theory/verify_exact_identities.py",
    "scripts/check_angular_geometry.py",
    "code/angular_optical_response.py",
    "code/audit_nodal_angular_geodesic.py",
    "code/strong_lensing_prediction.py",
    "code/shared_state_relations.py",
    "review/check_geometry_identities.py",
    "review/audit_sis_prediction.py",
    "scripts/make_figures_and_tables.py",
]


def main():
    vendor = ROOT / "code/vendor_original"
    source = json.loads((vendor / "SOURCE_MANIFEST.json").read_text())
    verified = []
    for item in source["files"]:
        content = (vendor / item["path"]).read_bytes()
        sha = hashlib.sha256(content).hexdigest()
        assert sha == item["sha256"], item["path"]
        assert len(content) == item["bytes"], item["path"]
        verified.append(item["path"])
    env = os.environ.copy()
    env["OPENBLAS_NUM_THREADS"] = "1"
    env["OMP_NUM_THREADS"] = "1"
    env.setdefault("MPLCONFIGDIR", str(ROOT / "artifacts/replay/matplotlib_cache"))
    os.environ.setdefault("MPLCONFIGDIR", env["MPLCONFIGDIR"])
    out = ROOT / "artifacts/replay"
    out.mkdir(parents=True, exist_ok=True)
    stages = []
    for stage in STAGES:
        print("Running", stage, flush=True)
        start = time.monotonic()
        result = subprocess.run([sys.executable, str(ROOT / stage)],
                                cwd=ROOT, env=env, capture_output=True, text=True)
        log = result.stdout + result.stderr
        (out / (Path(stage).stem + ".log")).write_text(log)
        stages.append({"script": stage, "returncode": result.returncode,
                       "elapsed_seconds": round(time.monotonic()-start, 3)})
        if result.returncode:
            print(log[-6000:])
            raise SystemExit(result.returncode)
    import numpy
    import scipy
    import matplotlib
    receipt = {"schema": "BHSM-ANGULAR-REPLAY-V1",
               "status": "ALL_STAGES_EXECUTED",
               "python": platform.python_version(),
               "numpy": numpy.__version__, "scipy": scipy.__version__,
               "matplotlib": matplotlib.__version__,
               "verified_inherited_inputs": verified,
               "source_commit": source["source_commit"],
               "observations_used": False, "stages": stages}
    (out / "replay_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
