from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATION = ROOT / "artifacts" / "BHSM_live_feynrules_validation_attempt_v1_5.json"
RUN_DIR = ROOT / "runs" / "feynrules_validation"
LOG = RUN_DIR / "ufo_export.log"
EXPORT_SCRIPT = ROOT / "scripts" / "feynrules" / "export_bhsm_minimal_to_ufo.m"


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    if not VALIDATION.exists():
        LOG.write_text("Missing validation artifact; UFO export refused.\n", encoding="utf-8")
        return 2
    payload = json.loads(VALIDATION.read_text(encoding="utf-8"))
    if not (payload.get("feynrules_syntax_validated") and payload.get("feynrules_model_load_validated")):
        LOG.write_text("FeynRules validation gates did not pass; UFO export refused.\n", encoding="utf-8")
        return 2
    wolframscript = shutil.which("wolframscript")
    if wolframscript is None:
        LOG.write_text("wolframscript not found; UFO export not run.\n", encoding="utf-8")
        return 2
    result = subprocess.run(
        [wolframscript, "-file", str(EXPORT_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    LOG.write_text(result.stdout + "\n" + result.stderr, encoding="utf-8")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

