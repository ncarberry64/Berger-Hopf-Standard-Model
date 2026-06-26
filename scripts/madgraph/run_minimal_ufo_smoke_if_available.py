from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
UFO = ROOT / "artifacts" / "BHSM_ufo_export_live_attempt_v1_5.json"
RUN_DIR = ROOT / "runs" / "madgraph_smoke"
LOG = RUN_DIR / "minimal_ufo_smoke.log"
MG5_SCRIPT = ROOT / "scripts" / "madgraph" / "import_bhsm_minimal_ufo_smoke.mg5"


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    if not UFO.exists():
        LOG.write_text("Missing UFO artifact; MadGraph smoke test refused.\n", encoding="utf-8")
        return 2
    payload = json.loads(UFO.read_text(encoding="utf-8"))
    if not (payload.get("ufo_export_passed") and payload.get("ufo_loadability_passed")):
        LOG.write_text("UFO export/loadability gates did not pass; MadGraph smoke test refused.\n", encoding="utf-8")
        return 2
    mg5 = shutil.which("mg5_aMC") or shutil.which("mg5")
    if mg5 is None:
        LOG.write_text("MadGraph executable not found; smoke test not run.\n", encoding="utf-8")
        return 2
    result = subprocess.run(
        [mg5, str(MG5_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    LOG.write_text(result.stdout + "\n" + result.stderr, encoding="utf-8")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

